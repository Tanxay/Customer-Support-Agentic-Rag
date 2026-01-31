import os
import pickle
from langchain_community.vectorstores import Milvus
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from app.core.config import config

class RetrievalAgent:
    def __init__(self):
        print("Initializing Retrieval Agent...")
        self.embeddings = OllamaEmbeddings(
            model=config.EMBEDDING_MODEL,
            base_url=config.OLLAMA_BASE_URL
        )
        self.vector_store = Milvus(
            embedding_function=self.embeddings,
            collection_name=config.COLLECTION_NAME,
            connection_args={"host": config.MILVUS_HOST, "port": config.MILVUS_PORT}
        )
        self.milvus_retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
        
        # Load chunks for BM25
        self.ensemble_retriever = None
        data_path = "data/chunks.pkl"
        if os.path.exists(data_path):
            print("Loading chunks for Hybrid Search (BM25)...")
            try:
                with open(data_path, "rb") as f:
                    chunks = pickle.load(f)
                
                if chunks:
                    print(f"Loaded {len(chunks)} chunks for BM25.")
                    self.bm25_retriever = BM25Retriever.from_documents(chunks)
                    self.bm25_retriever.k = 5
                    
                    # Create Ensemble (Hybrid)
                    # Weights: 0.5 Dense (Milvus) + 0.5 Sparse (BM25)
                    self.ensemble_retriever = EnsembleRetriever(
                        retrievers=[self.milvus_retriever, self.bm25_retriever],
                        weights=[0.5, 0.5]
                    )
                    print("Hybrid Search Enabled.")
                else:
                    print("Chunks file is empty.")
            except Exception as e:
                print(f"Error loading BM25: {e}")
        else:
            print("No chunks.pkl found. Hybrid search disabled (Milvus only).")

    def retrieve(self, query: str):
        print(f"Retrieving for: {query}")
        try:
            if self.ensemble_retriever:
                docs = self.ensemble_retriever.invoke(query)
                print(f"Hybrid Search found {len(docs)} documents.")
            else:
                docs = self.milvus_retriever.invoke(query)
                print(f"Vector Search found {len(docs)} documents.")
            return docs
        except Exception as e:
            print(f"CRITICAL RETRIEVAL ERROR: {e}")
            # Do not crash, return empty list so AnswerAgent can try (or fail gracefully with 'no context')
            return []

if __name__ == "__main__":
    agent = RetrievalAgent()
    results = agent.retrieve("refund policy")
    for doc in results:
        print(f"Content: {doc.page_content[:100]}...")
        print(f"Source: {doc.metadata.get('source')}")
