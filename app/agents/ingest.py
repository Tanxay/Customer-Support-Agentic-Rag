import os
import pandas as pd
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Milvus
from langchain_core.documents import Document
from app.core.config import config

def ingest_documents():
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    all_documents = []
    
    # scan directory
    for filename in os.listdir(data_dir):
        file_path = os.path.join(data_dir, filename)
        
        # Process PDF
        if filename.endswith(".pdf"):
            print(f"Loading PDF: {filename}")
            try:
                loader = PyPDFLoader(file_path)
                docs = loader.load()
                # Initial split
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
                splits = text_splitter.split_documents(docs)
                for split in splits:
                    split.metadata["source"] = filename
                    split.metadata["type"] = "pdf"
                all_documents.extend(splits)
            except Exception as e:
                print(f"Error loading PDF {filename}: {e}")

        # Process Excel
        elif filename.endswith(".xlsx") or filename.endswith(".xls"):
            print(f"Loading Excel: {filename}")
            try:
                df = pd.read_excel(file_path)
                # Convert rows to documents
                for index, row in df.iterrows():
                    # Create a text representation of the row
                    row_text = ", ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                    doc = Document(
                        page_content=row_text,
                        metadata={
                            "source": filename,
                            "row": index,
                            "type": "excel"
                        }
                    )
                    all_documents.append(doc)
            except Exception as e:
                print(f"Error loading Excel {filename}: {e}")

    if not all_documents:
        print("No documents found to ingest!")
        return

    print(f"Total documents to ingest: {len(all_documents)}")
    
    print("Initializing Embeddings (nomic-embed-text)...")
    embeddings = OllamaEmbeddings(
        model=config.EMBEDDING_MODEL,
        base_url=config.OLLAMA_BASE_URL
    )
    
    print(f"Indexing to Milvus collection '{config.COLLECTION_NAME}'...")
    try:
        Milvus.from_documents(
            all_documents,
            embeddings,
            collection_name=config.COLLECTION_NAME,
            connection_args={"host": config.MILVUS_HOST, "port": config.MILVUS_PORT},
            drop_old=True # Reset collection for fresh start
        )
        print("Indexing to Milvus Complete!")
        
        # Save chunks for BM25 (Hybrid Search)
        import pickle
        with open(os.path.join(data_dir, "chunks.pkl"), "wb") as f:
            pickle.dump(all_documents, f)
        print("Saved chunks for Hybrid Search.")
        
    except Exception as e:
        print(f"Failed to ingest to Milvus: {e}")

if __name__ == "__main__":
    ingest_documents()
