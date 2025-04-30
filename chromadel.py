from chromadb import PersistentClient

chroma_client = PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("notesai")

# Debug function to list all documents
def list_all_notes():
    results = collection.get()
    for doc_id, doc in zip(results['ids'], results['documents']):
        print(f"ID: {doc_id}\nDocument: {doc}\n{'-'*40}")
        
collection.delete(where={})  # deletes all documents






