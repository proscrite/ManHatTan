import os
import json
import random
import time
from litellm import completion
from pymilvus import MilvusClient
from google import genai

from dotenv import load_dotenv, find_dotenv

# Force load environment variables for standalone execution
load_dotenv(find_dotenv())

# ==========================================
# CONFIGURATION
# ==========================================
MILVUS_URI = "milvus_local.db"
COLLECTION_NAME = "conversation_history"
MODEL_NAME = "gemini-embedding-001" # Google's recommended stable version

MILVUS_URI = os.path.abspath("./milvus_local.db")
EMBEDDING_MODEL = "gemini-embedding-001"

def get_random_lexeme(client: MilvusClient) -> str:
    """Fetch a sample of lexemes from Milvus and select one at random."""
    results = client.query(
        collection_name="lexemes",
        filter="id >= 0",
        output_fields=["word_ll"],
        limit=100
    )
    if not results:
        raise ValueError("No lexemes found in the 'lexemes' collection! Run seed_milvus_lexemes.py first.")
    
    selected_record = random.choice(results)
    return selected_record["word_ll"]

def run_tutor_pipeline():
    # ---------------------------------------------------------
    # STEP 1: The Multi-Turn Conversation (LiteLLM + Ollama)
    # ---------------------------------------------------------
    
    client_milvus = MilvusClient(uri=MILVUS_URI)
    target_word = get_random_lexeme(client_milvus)
    print("--- STARTING TUTOR SESSION ---")
    
    # We must manually manage memory by passing the whole array back every time!
    conversation = [
        {"role": "system", "content": "You are a Hebrew tutor. Be brief."}
    ]
    
    prompts = [
        f"How do you say '{target_word}' in Hebrew?",
        f"Can you put '{target_word}' in a sentence (mid level)?",
        f"Do you remember what specific word we are learning?",
        f"Can you give me a mnemonic for '{target_word}'?" # Testing the memory!
    ]
    
    for prompt in prompts:
        print(f"\nUser: {prompt}")
        conversation.append({"role": "user", "content": prompt})
        
        # Route directly to your Mac's Ollama server using the ollama_chat/ prefix
        response = completion(
            model="ollama_chat/aya",
            messages=conversation,
            api_base="http://localhost:11434"
        )
        
        reply = response.choices[0].message.content
        print(f"Aya:  {reply}")
        
        # Append the assistant's reply to the history so it remembers next turn
        conversation.append({"role": "assistant", "content": reply})


    # ---------------------------------------------------------
    # STEP 2: Embed the History (Google GenAI)
    # ---------------------------------------------------------
    print("\n--- GENERATING EMBEDDINGS ---")

    history_text = json.dumps(conversation, ensure_ascii=False)

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    client_genai = genai.Client(api_key=api_key)
    
    emb_res = client_genai.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=history_text
    )
    vector = emb_res.embeddings[0].values
    print(f"Generated embedding vector with {len(vector)} dimensions.")

    # ---------------------------------------------------------
    # STEP 3: Store and Retrieve (Milvus)
    # ---------------------------------------------------------
    print("\n--- STORING IN MILVUS ---")

    session_id = f"session_{int(time.time())}"
    insert_data = [{
        "user_id": "test_user_001",
        "session_id": session_id,
        "language": "Hebrew",
        "embedding": vector,
        "metadata": {
            "history": history_text,
            "target_word": target_word
        }
    }]

    res = client_milvus.insert(
        collection_name="conversation_history",
        data=insert_data
    )
    print("\n--- RETRIEVING FROM MILVUS ---")

    search_res = client_milvus.search(
        collection_name="conversation_history",
        data=[vector],
        output_fields=["user_id", "session_id", "metadata"],
        limit=1
    )

    match = search_res[0][0]["entity"]
    print(f"Retrieved Session ID: {match['session_id']}")
    print(f"Target Word (from Metadata): {match['metadata']['target_word']}")
    print("\nDecoded Conversation Payload from Milvus:")
    print(json.dumps(json.loads(match["metadata"]["history"]), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run_tutor_pipeline()