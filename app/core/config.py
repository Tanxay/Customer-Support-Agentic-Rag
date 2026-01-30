
class Config:
    # Milvus
    MILVUS_HOST = "localhost"
    MILVUS_PORT = "19530"
    COLLECTION_NAME = "agentic_rag_docs"
    
    # LLM
    OLLAMA_BASE_URL = "http://localhost:11434"
    LLM_MODEL = "llama3.2:1b"
    EMBEDDING_MODEL = "nomic-embed-text" # or "all-minilm"
    
config = Config()
