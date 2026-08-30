import pprint
from pymilvus import MilvusClient

LOCAL_DB_PATH = "/Users/pabloherrero/Documents/ManHatTan/mht/backend/milvus_local.db"

def run_diagnostics_truncated():
    print(f"Connecting to local Milvus Lite at: {LOCAL_DB_PATH}\n")
    client = MilvusClient(LOCAL_DB_PATH)
    
    target_collections = ['lexemes', 'sentence_contexts', 'conversation_history']
    
    for coll in target_collections:
        print("=" * 60)
        print(f"COLLECTION: {coll.upper()}")
        print("=" * 60)
        
        if not client.has_collection(coll):
            print("Status: Not found locally.\n")
            continue
            
        # 1. Dump Exact Schema
        print("--- RAW SCHEMA ---")
        schema = client.describe_collection(coll)
        fields = schema.get("fields", []) if isinstance(schema, dict) else getattr(schema, "fields", [])
        
        for f in fields:
            name = f.get('name') if isinstance(f, dict) else getattr(f, 'name')
            print(f" - Field: {name} | Details: {f}")
        
        # Extract Primary Key dynamically for the safe filter
        pk_field = "id"
        pk_type = 5 # Default INT64
        for f in fields:
            is_pk = f.get("is_primary") if isinstance(f, dict) else getattr(f, "is_primary", False)
            if is_pk:
                pk_field = f.get("name") if isinstance(f, dict) else getattr(f, "name")
                pk_type = f.get("type") if isinstance(f, dict) else getattr(f, "dtype")

        # 2. Dump Exact Payload (Limit 1) - TRUNCATED
        print("\n--- RAW DATA PAYLOAD (LIMIT 1) ---")
        safe_filter = f"{pk_field} >= 0" if pk_type in [2, 3, 4, 5] else f"{pk_field} != ''"
        
        try:
            res = client.query(
                collection_name=coll,
                filter=safe_filter,
                output_fields=["*"],
                limit=1
            )
            
            if res:
                row = res[0]
                
                # TRUNCATE LOGIC: Hide massive vectors to protect terminal buffers
                for key, val in row.items():
                    if isinstance(val, list) and len(val) > 10:
                        row[key] = f"<Vector Truncated. Length: {len(val)}>"
                        
                pprint.pprint(row, indent=2)
                print(f"\nDetected Keys in Payload ({len(row.keys())} total): {list(row.keys())}")
            else:
                print("Status: Collection is empty.")
                
        except Exception as e:
            print(f"Query Failed: {e}")
            
        print("\n")

if __name__ == "__main__":
    run_diagnostics_truncated()