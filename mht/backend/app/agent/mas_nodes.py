# app/agent/mas_nodes.py
import os
from typing import Dict, Any
from langchain_litellm import ChatLiteLLM
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.output_parsers.openai_tools import PydanticToolsParser

from app.services.vector_service import vector_service
from app.schemas import ConversationalistResponse, TutorDecision
from app.agent.mas_state import MASState

# Dedicated LLM instance for MAS Agent execution
agent_llm = ChatLiteLLM(
    # model="gemini/gemini-3.5-flash",
    model="gemini/gemini-3.1-flash-lite",
    api_key=os.getenv("GEMINI_API_KEY"),
    timeout=30,
)


async def tutor_evaluation_node(state: MASState) -> Dict[str, Any]:
    """
    The Critic: Analyzes the user's latest message for grammatical accuracy.
    Does not respond directly to the user.
    """
    last_user_message = state["messages"][-1].content
    
    system_prompt = (
        "You are a strict linguistic evaluator.\n"
        f"Target Language (LL): {state.get('target_lang', 'Spanish')}\n"
        f"User Native Language (UL): {state.get('native_lang', 'English')}\n"
        "Check the user's message for errors. If an error exists, provide a correction and explanation in both LL and UL."
        "EVALUATION DIRECTIVES:\n"
        "1. Check the user message for tense mismatches, incorrect verb conjugations, gender/number disagreements, or unnatural phrasing.\n"
        "3. If grammatically sound, set intervention_type='none' and tutor_critique_ll=None and tutor_critique_ul=None.\n"
        "4. Strict brevity: 'tutor_critique_ll' and 'tutor_critique_ul' must never exceed 25 words."
    )
    
    # Using tool_choice="auto" to ensure compatibility
    llm_with_tools = agent_llm.bind_tools([TutorDecision], tool_choice="auto")
    parser = PydanticToolsParser(tools=[TutorDecision])
    structured_tutor = llm_with_tools | parser
    
    result_list = await structured_tutor.ainvoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=last_user_message)
    ])

    if not result_list:
        return {"intervention_type": "none", "tutor_critique_ll": None, "tutor_critique_ul": None}

    decision: TutorDecision = result_list[0]
    
    # Trigger Vector Ingestion if a critique was generated
    if decision.intervention_type == "correction" and decision.tutor_critique_ul:
        try:
            # We pass the user's native language since the critique_ul is written in it
            await vector_service.insert_conversation_history(
                critique_ul=decision.tutor_critique_ul,
                language=state.get("native_lang", "English")
            )
        except Exception as e:
            print(f"[Warning] Failed to cache MAS critique to Zilliz: {e}")

    return {
        "intervention_type": decision.intervention_type,
        "tutor_critique_ll": decision.tutor_critique_ll,
        "tutor_critique_ul": decision.tutor_critique_ul
    }

async def conversationalist_node(state: MASState) -> Dict[str, Any]:
    """
    The Actor: Maintains natural dialogue in the target language.
    If the Tutor flagged a correction, integrates the critique seamlessly.
    """
    system_prompt = (
        f"You are a friendly conversation partner speaking {state.get('target_lang', 'Spanish')}.\n"
        f"Adapt your vocabulary and grammar to suit a {state.get('cefr_level', 'A1')} learner.\n"
        f"Generate a 2-3 sentence reply and exactly 1 open question in both LL and UL.\n"
    )
    
    if state.get("intervention_type") == "correction" and state.get("tutor_critique_ll"):
        system_prompt += (
            "\n[INTERNAL SUPERVISOR NOTE]\n"
            f"The user made a mistake: {state['tutor_critique_ll']}\n"
            "Do NOT mention this correction in your reply. Simply steer the conversation naturally using the correct grammar."
        )

    history = list(state["messages"][-6:])
    messages_to_pass = [SystemMessage(content=system_prompt)] + history
    
    llm_with_tools = agent_llm.bind_tools([ConversationalistResponse], tool_choice="auto")
    parser = PydanticToolsParser(tools=[ConversationalistResponse])
    structured_actor = llm_with_tools | parser
    
    result_list = await structured_actor.ainvoke(messages_to_pass)
    response_data: ConversationalistResponse = result_list[0]
    
    # We only append the target language reply to the ongoing conversation history
    return {
        "messages": [AIMessage(content=response_data.message_ll)],
        "conversationalist_message_ll": response_data.message_ll,
        "conversationalist_message_ul": response_data.message_ul,
        "intervention_type": "none" # Reset state for the next turn
    }