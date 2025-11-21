# backend/app/database/vector_db.py
import chromadb
from chromadb.config import Settings
from typing import List, Dict
import os
from pathlib import Path

class VectorDB:
    def __init__(self):
        # Get the persist directory from environment or use default
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
        
        # Create directory if it doesn't exist
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="notes_collection",
            metadata={"description": "College notes and documents"}
        )
    
    def add_documents(self, documents: List[str], metadatas: List[Dict], ids: List[str]):
        """Add documents to the vector database"""
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            return True
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False
    
    def search(self, query: str, n_results: int = 5) -> Dict:
        """Search for similar documents"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Format results consistently
            return {
                'documents': results['documents'][0] if results.get('documents') and results['documents'] else [],
                'metadatas': results['metadatas'][0] if results.get('metadatas') and results['metadatas'] else [],
                'distances': results['distances'][0] if results.get('distances') and results['distances'] else []
            }
        except Exception as e:
            print(f"Error searching: {e}")
            return {'documents': [], 'metadatas': [], 'distances': []}
    
    def get_collection_count(self) -> int:
        """Get number of documents in collection"""
        try:
            return self.collection.count()
        except Exception as e:
            print(f"Error getting count: {e}")
            return 0
    
    def delete_by_file_id(self, file_id: str):
        """Delete all chunks associated with a file_id"""
        try:
            # Get all items with this file_id
            results = self.collection.get(
                where={"file_id": file_id}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                print(f"Deleted {len(results['ids'])} chunks for file {file_id}")
                return True
            return False
        except Exception as e:
            print(f"Error deleting from ChromaDB: {str(e)}")
            return False
    
    def reset_collection(self):
        """Reset the collection (delete all documents)"""
        try:
            self.client.delete_collection("notes_collection")
            self.collection = self.client.get_or_create_collection(
                name="notes_collection",
                metadata={"hnsw:space": "cosine"}
            )
            return True
        except Exception as e:
            print(f"Error resetting collection: {e}")
            return False

# Create a singleton instance
vector_db = VectorDB()