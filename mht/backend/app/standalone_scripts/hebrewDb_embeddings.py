import os
import asyncio
import pandas as pd
from litellm import aembedding
from dotenv import load_dotenv, find_dotenv

# Force load environment variables for standalone execution
load_dotenv(find_dotenv())

# Configuration
CSV_PATH = "/Users/pabloherrero/Documents/ManHatTan/mht/backend/app/services/hebrew_db.csv"
OUTPUT_PATH = "/Users/pabloherrero/Documents/ManHatTan/mht/backend/app/services/hebrew_db_embedded.parquet"
MODEL_NAME = "gemini/gemini-embedding-001"  
BATCH_SIZE = 100  # Adjust based on your API rate limits

async def fetch_embeddings(text_batch: list[str]) -> list[list[float]]:
    """Fetch embeddings concurrently using LiteLLM."""
    try:
        response = await aembedding(
            model=MODEL_NAME,
            input=text_batch,
            api_key=os.getenv("GEMINI_API_KEY")
        )
        return [item["embedding"] for item in response.data]
    except Exception as e:
        print(f"Error fetching embeddings: {e}")
        return [[] for _ in text_batch]

async def main():
    print(f"Loading data from {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    print(f"Df head:\n{df.head()}\nColumns: {df.columns.tolist()}")
    df_embeddings = pd.read_parquet(OUTPUT_PATH) if os.path.exists(OUTPUT_PATH) else None
    if df_embeddings is not None:
        df = df.merge(df_embeddings, on="word_ll", how="left")

    text_column = "word_ll" 
    
    if text_column not in df.columns:
        print(f"Error: Column '{text_column}' not found. Available columns: {df.columns.tolist()}")
        return
    

    texts = df[text_column].dropna().astype(str).tolist()
    all_embeddings = []

    print(f"Generating embeddings for {len(texts)} lexemes using {MODEL_NAME}...")
    
    # Process in chunks to prevent payload overflows and handle rate limits
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        print(f"Processing batch {i // BATCH_SIZE + 1}...")
        
        batch_embeddings = await fetch_embeddings(batch)
        all_embeddings.extend(batch_embeddings)
        
        # Optional: Add a slight delay if hitting Gemini Free Tier RPM limits
        await asyncio.sleep(1)

    # Attach vectors back to the dataframe
    df["embedding"] = all_embeddings
    
    # Save to Parquet for highly efficient binary storage
    df.to_parquet(OUTPUT_PATH, index=False)
    print(f"Successfully saved {len(all_embeddings)} embeddings to {OUTPUT_PATH}")

if __name__ == "__main__":
    asyncio.run(main())