import os
import asyncio
from dotenv import load_dotenv, find_dotenv
from pymilvus import MilvusClient

load_dotenv(find_dotenv())

async def ping_cloud_db():
    print("Initiating Zilliz Cloud handshake...")
    try:
        # Ensure your vector_service uses both URI and TOKEN
        client = MilvusClient(
            uri=os.getenv("ZILLIZ_CLUSTER_URL"),
            token=os.getenv("ZILLIZ_API_KEY")
        )
        
        # A lightweight metadata request to verify authentication and latency
        collections = client.list_collections()
        print(f"Success! Connected to Zilliz. Active Collections: {collections}")
        
    except Exception as e:
        print(f"Network or Authentication Failure: {e}")

if __name__ == "__main__":
    asyncio.run(ping_cloud_db())