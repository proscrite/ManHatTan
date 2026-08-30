import os
import asyncio

from pymilvus import MilvusClient
from app.services.embedding_service import embedding_service
from app.services.vector_service import vector_service
from app.agent.nodes import evaluate_context_node

from pathlib import Path
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

BACKEND_ROOT = Path(__file__).resolve().parent if "backend" in Path(__file__).resolve().name else Path(__file__).resolve().parents[1]
DEFAULT_MILVUS_DB = str(BACKEND_ROOT / "milvus_local.db")
MILVUS_URI = os.getenv("MILVUS_URI", DEFAULT_MILVUS_DB)

async def seed_sample_contexts(client: MilvusClient):
    """
    Seeds 2 sample Hebrew sentences for the word 'תפוח' into sentence_contexts.
    """
    print("\n--- Step 1: Seeding Sample Context Sentences ---")
    
    sample_data = [
        {
            "text": "אני אוהב לאכול תפוח אדום בבוקר",
            "language": "Hebrew",
            "word_ll": "תפוח",
            "metadata": {
                "sentence_translated": "I like to eat a red apple in the morning",
                "source": "Sample Seed",
                "difficulty": 1.0
            }
        },
        {
            "text": "קניתי קילו תפוחים בשוק",
            "language": "Hebrew",
            "word_ll": "תפוח",
            "metadata": {
                "sentence_translated": "I bought a kilo of apples at the market",
                "source": "Sample Seed",
                "difficulty": 1.5
            }
        }
    ]

    # Batch embed the sentence texts in a single call to save quota
    texts_to_embed = [item["text"] for item in sample_data]
    print(f"Generating embeddings for {len(texts_to_embed)} sentences...")
    embeddings = await embedding_service.embed_batch(texts_to_embed, batch_size=100)

    rows_to_insert = []
    for item, emb in zip(sample_data, embeddings):
        rows_to_insert.append({
            "text": item["text"],
            "language": item["language"],
            "word_ll": item["word_ll"],
            "embedding": emb,
            "metadata": item["metadata"]
        })

    insert_result = client.insert(
        collection_name="sentence_contexts",
        data=rows_to_insert
    )
    print(f"Successfully inserted {insert_result['insert_count']} records into 'sentence_contexts'.")


async def main():
    client = MilvusClient(uri=MILVUS_URI)
    
    if not client.has_collection("sentence_contexts"):
        print("Error: Collection 'sentence_contexts' not found. Run init_milvus_schema.py first.")
        return

    # 1. Seed data
    # await seed_sample_contexts(client)

    # 2. Test Vector Search
    print("\n--- Step 2: Testing Vector Retrieval ---")
    target_word = "תפוח"
    language = "Hebrew"
    
    print(f"Searching nearest context sentences for word: '{target_word}' (Language: {language})...")
    hits = await vector_service.search_context(target_word=target_word, language=language, limit=2)
    
    for idx, hit in enumerate(hits, 1):
        print(f"Hit {idx}: {hit['sentence_ll']} | Translation: {hit['sentence_ul']} | Cosine Similarity: {hit['similarity']:.4f}")

    # 3. Test Evaluative Grader Node
    print("\n--- Step 3: Testing Evaluator Node (LangGraph Node) ---")
    test_state = {
        "target_word": target_word,
        "target_lang": language,
        "native_lang": "English",
        "retrieved_contexts": hits
    }

    eval_result = await evaluate_context_node(test_state)
    print(f"Evaluator Node Output: {eval_result}")
    print(f"Is Context Valid: {eval_result['is_context_valid']} (Score: {eval_result['relevance_score']})")

if __name__ == "__main__":
    asyncio.run(main())