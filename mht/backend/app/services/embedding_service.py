import os
import asyncio
from typing import List
from google import genai
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class EmbeddingService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured in the environment.")
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-embedding-001"
        self.dimension = 3072

    async def embed_text(self, text: str) -> List[float]:
        """
        Asynchronously embeds a single text string.
        """
        try:
            response = await self.client.aio.models.embed_content(
                model=self.model_name,
                contents=text,
            )
            return response.embeddings[0].values
        except Exception as e:
            print(f"[EmbeddingService] Async single embed error: {e}")
            return [0.0] * self.dimension

    async def embed_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        Asynchronously batch-embeds a list of strings in chunks of `batch_size` 
        per API call, respecting the 100 RPM safety window.
        """
        all_embeddings: List[List[float]] = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                # 1 API request for all strings in `batch`
                response = await self.client.aio.models.embed_content(
                    model=self.model_name,
                    contents=batch,
                )
                all_embeddings.extend([emb.values for emb in response.embeddings])
            except Exception as e:
                print(f"[EmbeddingService] Async batch embed error: {e}")
                all_embeddings.extend([[0.0] * self.dimension for _ in batch])
                
            if i + batch_size < len(texts):
                # Non-blocking async sleep
                await asyncio.sleep(65)
                
        return all_embeddings

embedding_service = EmbeddingService()