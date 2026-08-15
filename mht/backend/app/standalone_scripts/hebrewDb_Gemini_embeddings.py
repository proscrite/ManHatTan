import os
import time 
import pandas as pd
from google import genai
from google.genai import types
from dotenv import load_dotenv, find_dotenv

# Force load environment variables for standalone execution
load_dotenv(find_dotenv())

# Configuration
CSV_PATH = "/Users/pabloherrero/Documents/ManHatTan/mht/backend/app/services/hebrew_db.csv"
OUTPUT_PATH = "/Users/pabloherrero/Documents/ManHatTan/mht/backend/app/services/hebrew_db_embedded.parquet"
MODEL_NAME = "gemini-embedding-001"
BATCH_SIZE = 100 

def fetch_embeddings_batch(client: genai.Client, text_batch: list[str]) -> list[list[float]]:
    """Fetch embeddings using the native SDK batch capabilities."""
    try:
        response = client.models.embed_content(
            model=MODEL_NAME,
            contents=text_batch, # Pass the entire list natively
        )
        return [emb.values for emb in response.embeddings]
    except Exception as e:
        print(f"Error fetching embeddings: {e}")
        return [[] for _ in text_batch]
    
def run_embeddings_pipeline():
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(f"API key not found. Ensure GEMINI_API_KEY is set in {dotenv_path}")

    print(f"Loading data from {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    text_column = "word_ll"

    if text_column not in df.columns:
        raise KeyError(f"Column '{text_column}' not found. Available columns: {df.columns.tolist()}")

    # 1. Incremental Cache Check: Read existing parquet if available
    existing_embeddings = {}
    if os.path.exists(OUTPUT_PATH):
        print(f"Found existing parquet at {OUTPUT_PATH}. Loading cached vectors...")
        df_existing = pd.read_parquet(OUTPUT_PATH)
        if text_column in df_existing.columns and "embedding" in df_existing.columns:
            for _, row in df_existing.iterrows():
                if isinstance(row["embedding"], (list, pd.Series)) and len(row["embedding"]) > 0:
                    existing_embeddings[row[text_column]] = list(row["embedding"])

    # 2. Filter words needing API calls
    all_words = df[text_column].dropna().astype(str).unique().tolist()
    words_to_fetch = [w for w in all_words if w not in existing_embeddings]

    print(f"Total lexemes: {len(df)} | Cached: {len(existing_embeddings)} | Pending API fetch: {len(words_to_fetch)}")

    # 3. Batch API calls for missing words
    if words_to_fetch:
        client = genai.Client(api_key=api_key)
        
        for i in range(0, len(words_to_fetch), BATCH_SIZE):
            batch = words_to_fetch[i:i + BATCH_SIZE]
            print(f"Processing batch {(i // BATCH_SIZE) + 1} of {(len(words_to_fetch) // BATCH_SIZE) + 1} ({len(batch)} words)...")

            batch_vectors = fetch_embeddings_batch(client, batch)
            for word, vec in zip(batch, batch_vectors):
                if vec:
                    existing_embeddings[word] = vec

            # Respect 100 RPM rolling window
            if i + BATCH_SIZE < len(words_to_fetch):
                print("Free Tier quota limit reached (100 RPM). Sleeping for 65 seconds...")
                time.sleep(65)

    # 4. Map vectors back to DataFrame ensuring 1:1 row alignment
    df["embedding"] = df[text_column].map(existing_embeddings)

    # Save to Parquet
    df.to_parquet(OUTPUT_PATH, index=False)
    print(f"Successfully saved {len(df)} rows to {OUTPUT_PATH}")
    return df

if __name__ == "__main__":
    run_embeddings_pipeline()
