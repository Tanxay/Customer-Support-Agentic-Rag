from pymilvus import connections, utility

print("Attempting to connect to Milvus...")
try:
    connections.connect("default", host="localhost", port="19530")
    print("Successfully connected to Milvus!")
    
    # Check health by listing collections (should be empty initially)
    collections = utility.list_collections()
    print(f"Collections: {collections}")
    
except Exception as e:
    print(f"Failed to connect: {e}")
