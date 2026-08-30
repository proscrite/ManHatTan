import os
from typing import Dict, Any
from langchain_litellm import ChatLiteLLMRouter
from langchain_litellm import ChatLiteLLM
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers.openai_tools import PydanticToolsParser
import litellm
from app.schemas import GraderOutput, ExerciseGenerationOutput
from app.services.llm_service import llm_service
from app.services.vector_service import vector_service

# GLOBAL CONFIG: Strips LangChain-incompatible kwargs during multi-provider fallbacks
litellm.drop_params = True

agent_llm = ChatLiteLLM(
    model="gemini/gemini-3.1-flash-lite",
    api_key=os.getenv("GEMINI_API_KEY"),
    timeout=45,
)

async def retrieve_context_node(state: dict) -> Dict[str, Any]:
    """
    Deterministic entry point for the Tier-1 RAG pipeline.
    Queries Zilliz Cloud for context before passing it to the Evaluator.
    """
    target_word = state.get("target_word", "")
    target_lang = state.get("target_lang", "")
    
    # Execute the asynchronous vector search against Zilliz Cloud
    hits = await vector_service.search_context(
        target_word=target_word, 
        language=target_lang, 
        limit=3
    )
    
    # Updates the AgentState with the retrieved contexts
    return {"retrieved_contexts": hits}

async def evaluate_context_node(state: dict) -> Dict[str, Any]:
    """
    Evaluates retrieved Milvus context quality against the target lexeme.
    """
    contexts = state.get("retrieved_contexts", [])
    
    if not contexts:
        return {"is_context_valid": False, "relevance_score": 0.0}
        
    context_str = "\n".join([
        f"- Target Lang: {c.get('sentence_ll', '')} | Native Lang: {c.get('sentence_ul', '')} (Sim: {c.get('similarity', 0.0):.2f})"
        for c in contexts
    ])

    system_prompt = (
        "You are an expert linguistic grader. Evaluate if the retrieved context sentences "
        "naturally and accurately demonstrate the usage of the target word in the target language.\n"
        "CRITICAL FLUENCY GUARDRAIL:\n"
        f"The user's level is {state.get('cefr_level', 'A1')}. You MUST evaluate if the sentence complies with these rules: {state.get('grammar_rules')}\n"
        "If the sentence violates these grammar rules (e.g., it uses passive voice when forbidden), you MUST return is_valid=False, regardless of semantic relevance.\n"
        "Return is_valid=True ONLY if the semantic alignment is >= 0.7 AND it strictly obeys the grammar rules."
    )
    
    user_prompt = (
        f"Target Word: {state.get('target_word')}\n"
        f"Target Language: {state.get('target_lang')}\n"
        f"Context Candidates:\n{context_str}"
    )
    
    # 1. Bind tools and explicitly enforce a provider-compliant tool_choice
    llm_with_tools = agent_llm.bind_tools(
        [GraderOutput],
        tool_choice="auto"  # Supported by Gemini, Groq (Llama 3), and OpenAI
    )

    # 2. Attach the LangChain parser to extract the Pydantic object from the tool call
    parser = PydanticToolsParser(tools=[GraderOutput])
    
    # 3. Create the execution chain
    structured_grader = llm_with_tools | parser
    
    result_list = await structured_grader.ainvoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    
    # PydanticToolsParser returns a list of matched tool calls; extract the first one
    result: GraderOutput = result_list[0]
    
    return {
        "is_context_valid": result.is_valid,
        "relevance_score": result.relevance_score
    }

async def synthesize_exercise_node(state: dict) -> Dict[str, Any]:
    """
    Transforms a highly-rated retrieved Milvus context sentence into a strict CLOZE payload,
    ensuring translations and distractors respect the user's CEFR level.
    """
    best_context = state["retrieved_contexts"][0]
    sentence_ll = best_context.get("sentence_ll", "")
    sentence_ul = best_context.get("sentence_ul", "")
    
    system_prompt = (
        "You are an expert language teacher creating a fill-in-the-blank CLOZE exercise.\n"
        "1. Replace the Target Word in 'sentence_target' with underscores (___).\n"
        "2. Provide the exact Native Language translation.\n"
        "3. Generate 3 plausible distractors that match the grammatical gender, number, and part-of-speech of the Target Word.\n\n"
        "CRITICAL FLUENCY RULES:\n"
        f"The user is currently at a {state.get('cefr_level', 'A1')} level. Ensure your distractors are common words appropriate for this level. "
        "Do not use highly obscure literary words for distractors."
    )
    
    user_prompt = (
        f"Target Word: {state['target_word']}\n"
        f"Target Sentence: {sentence_ll}\n"
        f"Native Translation: {sentence_ul}"
    )
    
    llm_with_tools = agent_llm.bind_tools([ExerciseGenerationOutput], tool_choice="auto")
    parser = PydanticToolsParser(tools=[ExerciseGenerationOutput])
    structured_synthesizer = llm_with_tools | parser
    
    result_list = await structured_synthesizer.ainvoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    result_payload = result_list[0]

    # Asynchronously store generated sentence into Zilliz memory
    try:
        # Reconstruct the full sentence by replacing blanks with the target word
        full_sentence = result_payload.sentence_target.replace("___", state["target_word"])
        
        await vector_service.insert_context(
            text=full_sentence,
            language=state["target_lang"],
            word_ll=state["target_word"],
            translated_text=result_payload.sentence_translated,
            source="Tier1_Fallback_Generator",
            difficulty=state.get("fsrs_difficulty", 1.0)
        )
    except Exception as e:
        print(f"[Warning] Failed to cache generated context to Zilliz: {e}")

    
    return {"generated_payload": result_payload.model_dump()}

async def generate_from_scratch_node(state: dict) -> Dict[str, Any]:
    """
    Fallback node: Generates a brand new context sentence from scratch when Milvus retrieval fails.
    Strictly applies the user's CEFR level and grammar rules to prevent cognitive overload.
    """
    system_prompt = (
        "You are an expert language teacher. Generate a fill-in-the-blank CLOZE exercise from scratch.\n"
        "1. Replace the Target Word in 'sentence_target' with underscores (___).\n"
        "2. Provide the exact Native Language translation.\n"
        "3. Generate 3 plausible distractors that match the grammatical part-of-speech.\n\n"
        "CRITICAL LINGUISTIC GUARDRAILS:\n"
        f"- Target CEFR Level: {state.get('cefr_level', 'A1')}\n"
        f"- Grammar Rules: {state.get('grammar_rules', 'Use simple, active voice sentences only.')}\n"
        "Under NO circumstances should you violate the Grammar Rules."
        "- Corpus Frequency: This rule applies if the target CEFR level is below C1. With the exception of the Target Word, every single word in your generated sentence MUST belong to the top 1,000 most frequent conversational words.\n"
    )
    
    user_prompt = (
        f"Target Word: {state['target_word']}\n"
        f"Target Language: {state['target_lang']}\n"
        f"Native Language: {state['native_lang']}"
    )
    
    llm_with_tools = agent_llm.bind_tools([ExerciseGenerationOutput], tool_choice="auto")
    parser = PydanticToolsParser(tools=[ExerciseGenerationOutput])
    structured_generator = llm_with_tools | parser
    
    result_list = await structured_generator.ainvoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    result_payload = result_list[0]

    # Asynchronously store generated sentence into Zilliz memory
    try:
        # Reconstruct the full sentence by replacing blanks with the target word
        full_sentence = result_payload.sentence_target.replace("___", state["target_word"])
        
        await vector_service.insert_context(
            text=full_sentence,
            language=state["target_lang"],
            word_ll=state["target_word"],
            translated_text=result_payload.sentence_translated,
            source="Tier1_Fallback_Generator",
            difficulty=state.get("fsrs_difficulty", 1.0)
        )
    except Exception as e:
        print(f"[Warning] Failed to cache generated context to Zilliz: {e}")

    
    return {"generated_payload": result_payload.model_dump()}