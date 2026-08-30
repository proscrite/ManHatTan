import os
import litellm
import mlflow
import asyncio
from dotenv import load_dotenv, find_dotenv
from langchain_core.messages import HumanMessage

load_dotenv(find_dotenv())

from app.agent.mas_graph import mas_agent
from app.agent.mas_state import MASState


# --- MLflow Local Telemetry Setup ---
os.environ["MLFLOW_TRACKING_URI"] = "file:./mlruns"
litellm.success_callback = ["mlflow"]
mlflow.set_experiment("Manhattan_Local_Telemetry")

# Enable native LangChain/LangGraph tracing
mlflow.langchain.autolog()

async def test_mas_actor_critic_turn():
    print("\n--- Initializing Tier-Pro MAS Agent Test ---")
    
    # Intentional grammatical error: incorrect gender/tense
    broken_user_msg = "אני הולכת אתמול לחנות וקנה תפוח" 
    
    # Initialize the expanded Phase 5 state
    initial_state: MASState = {
        "messages": [HumanMessage(content=broken_user_msg)],
        "fluency_index": 0.45,
        "cefr_level": "A2",
        "target_lang": "Hebrew",
        "native_lang": "English",
        "due_vocab_id": None,
        "intervention_type": None,
        "tutor_critique_ll": None,
        "tutor_critique_ul": None,
        "conversationalist_message_ll": None,
        "conversationalist_message_ul": None
    }
    
    print(f"User Utterance: '{broken_user_msg}'")
    print("Executing Actor-Critic loop...\n")

    # --- 2. Explicit MLflow Run Context ---
    with mlflow.start_run(run_name="MAS_Actor_Critic_Turn"):
        final_state = await mas_agent.ainvoke(initial_state)
    # final_state = await mas_agent.ainvoke(initial_state)
    
    print("=== EXECUTION COMPLETED ===")
    print(f"Intervention Type: {final_state.get('intervention_type')}")
    
    print("\n--- 🕵️ THE TUTOR (Critic) ---")
    print(f"Critique (LL): {final_state.get('tutor_critique_ll')}")
    print(f"Critique (UL): {final_state.get('tutor_critique_ul')}")
    
    print("\n--- 🗣️ THE CONVERSATIONALIST (Actor) ---")
    print(f"Message (LL): {final_state.get('conversationalist_message_ll')}")
    print(f"Message (UL): {final_state.get('conversationalist_message_ul')}")
    
    # Drain the asyncio SSL transport pool to prevent the closing fd warning
    await asyncio.sleep(0.25)

if __name__ == "__main__":
    asyncio.run(test_mas_actor_critic_turn())