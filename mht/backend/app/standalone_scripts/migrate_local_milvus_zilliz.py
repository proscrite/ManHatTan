import os
from dotenv import load_dotenv, find_dotenv
from pymilvus import MilvusClient

# 1. Environment Setup
load_dotenv(find_dotenv())
LOCAL_DB_PATH = "/Users/pabloherrero/Documents/ManHatTan/mht/backend/milvus_local.db"
ZILLIZ_ENDPOINT = os.getenv("ZILLIZ_CLUSTER_URL")
ZILLIZ_TOKEN = os.getenv("ZILLIZ_API_KEY")

# 2. Clients Initialization
print("Initializing clients...")
local_client = MilvusClient(LOCAL_DB_PATH)
cloud_client = MilvusClient(uri=ZILLIZ_ENDPOINT, token=ZILLIZ_TOKEN)

target_collections = ['lexemes', 'sentence_contexts', 'conversation_history']


for collection_name in target_collections:
    if not local_client.has_collection(collection_name):
        print(f"[{collection_name}] Not found locally. Skipping.")
        continue

    print(f"\n--- Migrating: {collection_name} ---")

    # 3. Exact Schema Extraction
    info = local_client.describe_collection(collection_name)
    schema_info = info.get("schema", info)
    fields = schema_info.get("fields", [])
    
    field_names = []
    schema = MilvusClient.create_schema(
        enable_dynamic_field=schema_info.get("enable_dynamic_field", True)
    )
    
    vector_field = "vector"
    pk_field = "id"
    pk_type = 5
    
    for f in fields:
        f_name = f.get("name")
        field_names.append(f_name)
        
        f_type = f.get("type")
        is_primary = f.get("is_primary", False)
        
        params = f.get("params", {})
        dim = params.get("dim") or f.get("dim")
        max_length = params.get("max_length") or f.get("max_length")
        
        if is_primary:
            pk_field = f_name
            pk_type = f_type
            
        if f_type in [101, 102]: 
            vector_field = f_name
            
        # THE FIX: Strict Kwargs Filtering
        field_kwargs = {
            "field_name": f_name,
            "datatype": f_type,
            "is_primary": is_primary,
            "auto_id": f.get("auto_id", False)
        }
        
        # Only attach max_length if it's a VARCHAR (Type 21)
        if f_type == 21 and max_length is not None:
            field_kwargs["max_length"] = int(max_length)
            
        # Only attach dim if it's a VECTOR (Type 101, 102)
        if f_type in [101, 102] and dim is not None:
            field_kwargs["dim"] = int(dim)
            
        schema.add_field(**field_kwargs)

    # 4. Collection Creation in Zilliz
    if not cloud_client.has_collection(collection_name):
        print(f"[{collection_name}] Mirroring sanitized schema to Zilliz Cloud...")
        
        index_params = cloud_client.prepare_index_params()
        index_params.add_index(
            field_name=vector_field,
            index_type="AUTOINDEX",
            metric_type="COSINE" 
        )
        
        cloud_client.create_collection(
            collection_name=collection_name,
            schema=schema,
            index_params=index_params
        )

    # 5. Formulate Safe Bounded Filter
    safe_filter = f"{pk_field} >= 0" if pk_type in [2, 3, 4, 5] else f"{pk_field} != ''"
    
    print(f"[{collection_name}] Extracting data via offset pagination...")
   
    batch_size = 500
    current_offset = 0
    total_inserted = 0
    
    while True:
        batch = local_client.query(
            collection_name=collection_name,
            filter=safe_filter,
            output_fields=field_names, 
            offset=current_offset,
            limit=batch_size
        )
        
        if not batch:
            break
            
        # THE FIX: Strict Payload Sanitization
        sanitized_batch = []
        for row in batch:
            clean_row = dict(row) # Create a mutable copy
            
            # Strip the Primary Key so Zilliz can auto-generate it securely
            if pk_field in clean_row:
                del clean_row[pk_field]
                
            # Strip any PyMilvus internal dynamic wrappers (safety measure)
            clean_row.pop("$meta", None)
            
            sanitized_batch.append(clean_row)
            
        # Insert the sanitized payload
        res = cloud_client.insert(collection_name=collection_name, data=sanitized_batch)
        
        inserted_this_batch = res.get("insert_count", len(batch)) if isinstance(res, dict) else len(batch)
        total_inserted += inserted_this_batch
        current_offset += batch_size
        
        print(f"[{collection_name}] Uploaded batch of {len(batch)} records... (Total: {total_inserted})")
print("\nAll collections successfully migrated to Zilliz Cloud!")