from pymilvus import MilvusClient, DataType
import os
# Configuration
# MILVUS_URI = "http://localhost:19530" # Default Milvus Lite / Standalone port
MILVUS_URI = os.path.abspath("./milvus_local.db")
VECTOR_DIMENSION = 3072 # MUST match gemini-embedding-001 output exactly

def init_database():
    print(f"Connecting to Milvus at {MILVUS_URI}...")
    client = MilvusClient(uri=MILVUS_URI)

    # ---------------------------------------------------------
    # Schema 1: Lexemes (Wordbank)
    # ---------------------------------------------------------
    print("Designing 'lexemes' schema...")
    lexeme_schema = client.create_schema(auto_id=True, enable_dynamic_field=True)
    
    lexeme_schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
    lexeme_schema.add_field(field_name="word_ll", datatype=DataType.VARCHAR, max_length=255)
    lexeme_schema.add_field(field_name="language", datatype=DataType.VARCHAR, max_length=50)
    lexeme_schema.add_field(field_name="embedding", datatype=DataType.FLOAT_VECTOR, dim=VECTOR_DIMENSION)
    # JSON field for flexible attributes (translation, POS, frequency)
    lexeme_schema.add_field(field_name="metadata", datatype=DataType.JSON) 

    # ---------------------------------------------------------
    # Schema 2: Sentence Contexts (Content Engine)
    # ---------------------------------------------------------
    print("Designing 'sentence_contexts' schema...")
    context_schema = client.create_schema(auto_id=True, enable_dynamic_field=True)
    
    context_schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
    context_schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=2048)
    context_schema.add_field(field_name="language", datatype=DataType.VARCHAR, max_length=50)
    context_schema.add_field(field_name="embedding", datatype=DataType.FLOAT_VECTOR, dim=VECTOR_DIMENSION)
    # Link back to the specific word it teaches
    context_schema.add_field(field_name="word_ll", datatype=DataType.VARCHAR, max_length=255)
    # JSON field for source (e.g., "Google Play Books"), difficulty, translated text
    context_schema.add_field(field_name="metadata", datatype=DataType.JSON)

    # ---------------------------------------------------------
    # Schema 3: Conversation History (Stateful AI Tutor Memory)
    # ---------------------------------------------------------
    print("Designing 'conversation_history' schema...")
    history_schema = client.create_schema(auto_id=True, enable_dynamic_field=True)
    history_schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
    history_schema.add_field(field_name="language", datatype=DataType.VARCHAR, max_length=50)
    history_schema.add_field(field_name="user_id", datatype=DataType.VARCHAR, max_length=255)
    history_schema.add_field(field_name="session_id", datatype=DataType.VARCHAR, max_length=255)
    history_schema.add_field(field_name="embedding", datatype=DataType.FLOAT_VECTOR, dim=VECTOR_DIMENSION)
    # JSON field stores the full raw messages array: [{"role": "user", "content": ...}]
    history_schema.add_field(field_name="metadata", datatype=DataType.JSON)

    # Index Configuration (Required for fast vector similarity)

    index_params = client.prepare_index_params()
    index_params.add_index(
        field_name="embedding",
        index_type="AUTOINDEX", 
        metric_type="COSINE" # Cosine similarity is standard for LLM embeddings
    )

    index_params.add_index(
        field_name="language"
    )

    # ---------------------------------------------------------
    # Collection Instantiation
    # ---------------------------------------------------------
    collections = [
        ("lexemes", lexeme_schema), 
        ("sentence_contexts", context_schema),
        ("conversation_history", history_schema)
    ]

    for coll_name, schema in collections:
        if client.has_collection(coll_name):
            print(f"Collection '{coll_name}' already exists. Dropping for clean slate...")
            client.drop_collection(coll_name)
            
        print(f"Creating collection: {coll_name}")
        client.create_collection(
            collection_name=coll_name,
            schema=schema,
            index_params=index_params
        )

    print("\nDatabase instantiation complete. Ready for ingestion.")

if __name__ == "__main__":
    init_database()