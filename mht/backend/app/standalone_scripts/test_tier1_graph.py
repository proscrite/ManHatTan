import asyncio
import os
import litellm
import mlflow
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from app.agent.graph import tier1_agent, AgentState
from app.services.fluency_service import resolve_course_cefr

# --- MLflow Local Telemetry Setup ---
os.environ["MLFLOW_TRACKING_URI"] = "file:./mlruns"
litellm.success_callback = ["mlflow"]
mlflow.set_experiment("Manhattan_Local_Telemetry")
mlflow.langchain.autolog()

async def test_full_graph_execution():
    print("\n--- Initializing Tier-1 Agent Graph Test ---")
    
    target_word = "שוחד" # Bribe
    
    # 1. Mock the user's DB state (Assume FSRS difficulty is high, but user is A2)
    mock_db_cefr_int = 2 
    cefr_label, grammar_rules = resolve_course_cefr(mock_db_cefr_int)
    
    print(f"User Profile Loaded -> Level: {cefr_label}")
    print(f"Active Guardrails: {grammar_rules}")
    
    # 2. Mock a Milvus Retrieval (Testing a poor context sentence in passive voice)
    mock_retrieved_contexts = [
        {
            "sentence_ll": "הואשם בקבלת שוחד מהחברה",
            "sentence_ul": "He was accused of receiving a bribe from the company",
            "similarity": 0.81
        }
    ]
    
    # 3. Hydrate the Graph State
    initial_state: AgentState = {
        "vocab_id": "mock_uuid_1234",
        "target_word": target_word,
        "target_lang": "Hebrew",
        "native_lang": "English",
        "fsrs_difficulty": 5.32,
        "cefr_level": cefr_label,
        "grammar_rules": grammar_rules,
        "retrieved_contexts": mock_retrieved_contexts,
        "is_context_valid": False, # Will be overwritten by Evaluator
        "relevance_score": 0.0,    # Will be overwritten by Evaluator
        "generated_payload": None
    }
    
    print("\n--- Executing Graph ---")
    # 4. Invoke the state machine
    with mlflow.start_run(run_name="Tier1_Evaluation_RAG"):
        final_state = await tier1_agent.ainvoke(initial_state)
    # final_state = await tier1_agent.ainvoke(initial_state)
    
    print("\n--- Execution Complete ---")
    print(f"Evaluator Graded Context As Valid: {final_state.get('is_context_valid')}")
    print(f"Evaluator Relevance Score: {final_state.get('relevance_score')}")
    
    print("\n--- Final Synthesized Payload ---")
    payload = final_state.get("generated_payload")
    if payload:
        import json
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print("Error: No payload generated.")

    # TEARDOWN FIX: Allow background aiohttp client sessions in LiteLLM to close gracefully
    await asyncio.sleep(0.25)
    

if __name__ == "__main__":
    asyncio.run(test_full_graph_execution())