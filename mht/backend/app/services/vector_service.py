# app/services/vector_service.py
import os
import json
from typing import List, Dict, Any
from pymilvus import MilvusClient
from pathlib import Path
from app.services.embedding_service import embedding_service
from dotenv import load_dotenv, find_dotenv

# Ensure environment variables are loaded for local script execution
load_dotenv(find_dotenv())

BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_MILVUS_DB = str(BACKEND_ROOT / "milvus_local.db")

class VectorService:
    def __init__(self):
        # 1. Attempt Zilliz Cloud Connection First
        zilliz_uri = os.getenv("ZILLIZ_CLUSTER_URL")
        zilliz_token = os.getenv("ZILLIZ_API_KEY")

        if zilliz_uri and zilliz_token:
            try:
                self.client = MilvusClient(
                    uri=zilliz_uri,
                    token=zilliz_token
                )
                # Execute a lightweight metadata request to verify the handshake
                self.client.list_collections()
                print("[VectorService] Successfully connected to Zilliz Cloud.")
                return
            except Exception as e:
                print(f"[VectorService] Zilliz Cloud connection failed: {e}. Initiating local fallback...")

        # 2. Fallback to Local Milvus Lite
        print("[VectorService] Mounting local Milvus database.")
        self.db_path = os.path.abspath(DEFAULT_MILVUS_DB)
        
        try:
            self.client = MilvusClient(uri=self.db_path)
        except Exception as e:
            # Fallback for strict PyMilvus versions that reject absolute paths
            print(f"[VectorService] Absolute path mount failed, trying relative path: {e}")
            self.client = MilvusClient(uri="./milvus_local.db")

    async def search_context(self, target_word: str, language: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Asynchronously searches the 'sentence_contexts' collection using 
        cosine similarity and scalar filtering by language.
        """
        if not self.client.has_collection("sentence_contexts"):
            return []

        # Embed the query word asynchronously
        query_vector = await embedding_service.embed_text(target_word)
        filter_expr = f"language == '{language}'"

        # Vector search against 'embedding' field
        results = self.client.search(
            collection_name="sentence_contexts",
            data=[query_vector],
            anns_field="embedding",
            filter=filter_expr,
            limit=limit,
            output_fields=["text", "word_ll", "metadata"]
        )

        formatted_hits = []
        if results and len(results) > 0:
            for hit in results[0]:
                entity = hit.get("entity", {})
                metadata = entity.get("metadata", {})
                
                # Handle dictionary parsing if metadata is returned as JSON/dict
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except Exception:
                        metadata = {}

                formatted_hits.append({
                    "sentence_ll": entity.get("text", ""),
                    "sentence_ul": metadata.get("sentence_translated", ""),
                    "target_word": entity.get("word_ll", ""),
                    "similarity": hit.get("distance", 0.0)
                })
        return formatted_hits

    async def insert_context(self, text: str, language: str, word_ll: str, 
                             translated_text: str, source: str = "AI_Generated", difficulty: float = 1.0) -> bool:
        """
        Embeds a sentence and inserts it into the 'sentence_contexts' collection.
        """
        if not self.client.has_collection("sentence_contexts"):
            return False

        # 1. Generate embedding vector
        embedding = await embedding_service.embed_text(text)

        # 2. Construct payload matching the Zilliz schema
        data = [{
            "text": text,
            "language": language,
            "word_ll": word_ll,
            "embedding": embedding,
            "metadata": {
                "sentence_translated": translated_text,
                "source": source,
                "difficulty": difficulty
            }
        }]

        # 3. Insert into Zilliz Cloud
        insert_result = self.client.insert(
            collection_name="sentence_contexts",
            data=data
        )
        return insert_result.get("insert_count", 0) > 0

    async def insert_conversation_history(self, critique_ul: str, language: str) -> bool:
        """
        Embeds and stores the Tutor's native-language critique for future MAS retrieval.
        """
        # Failsafe if you haven't created the collection in Zilliz yet
        if not self.client.has_collection("conversation_history"):
            print("[VectorService] Warning: 'conversation_history' collection not found.")
            return False

        # 1. Generate embedding vector
        embedding = await embedding_service.embed_text(critique_ul)

        # 2. Construct payload matching the conversation_history schema
        data = [{
            "text": critique_ul,
            "language": language,
            "embedding": embedding,
            "metadata": {
                "source": "TierPro_Critic"
            }
        }]

        # 3. Insert into Zilliz Cloud / Local Milvus
        insert_result = self.client.insert(
            collection_name="conversation_history",
            data=data
        )
        return insert_result.get("insert_count", 0) > 0

vector_service = VectorService()