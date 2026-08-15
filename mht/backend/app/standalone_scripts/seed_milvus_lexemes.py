import os
import pandas as pd
import numpy as np
from pymilvus import MilvusClient

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARQUET_PATH = os.path.join(BASE_DIR, "hebrew_db_embedded.parquet")
MILVUS_URI = os.path.abspath("milvus_local.db")
COLLECTION_NAME = "lexemes"

def seed_milvus():
    if not os.path.exists(PARQUET_PATH):
        raise FileNotFoundError(f"Parquet file not found at {PARQUET_PATH}")

    print(f"Connecting to Milvus at {MILVUS_URI}...")
    client = MilvusClient(uri=MILVUS_URI)

    print(f"Loading Parquet dataset from {PARQUET_PATH}...")
    df = pd.read_parquet(PARQUET_PATH)

    # print(f"Dataset loaded:\n {df['embedding'].apply(lambda v: isinstance(v, (list, tuple, np.ndarray)) and len(v) > 0) }")

    # Filter rows with valid embeddings
    df = df[df["embedding"].apply(lambda v: isinstance(v, (list, tuple, np.ndarray)) and len(v) > 0)]
    print(f"Filtered dataset to {len(df)} valid records with embeddings.")
    entities = []

    for _, row in df.iterrows():
        entity = {
            "word_ll": str(row["word_ll"]),
            "language": "Hebrew",
            "embedding": list(row["embedding"]),
            "metadata": {
                "p_recall": float(row.get("p_recall", 0.0)),
                "history_seen": int(row.get("history_seen", 0)),
                "user_id": str(row.get("user_id", "default_user"))
            }
        }
        entities.append(entity)

    print(f"Inserting {len(entities)} records into '{COLLECTION_NAME}'...")
    res = client.insert(collection_name=COLLECTION_NAME, data=entities)
    print(f"Ingestion complete. Insert count: {res['insert_count']}")

if __name__ == "__main__":
    seed_milvus()