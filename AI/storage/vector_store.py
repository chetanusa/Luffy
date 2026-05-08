import sys
from pathlib import Path
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from AI.config.settings import settings as app_settings

class VectorStore:
    """ChromaDB vector store for document embeddings"""
    
    def __init__(self):
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=app_settings.CHROMA_PATH
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"description": "Document embeddings for semantic search"}
        )
    
    def add_document(self, doc_id: int, title: str, text: str, embedding: List[float]):
        """Add document embedding to vector store"""
        try:
            self.collection.add(
                ids=[f"doc_{doc_id}"],
                embeddings=[embedding],
                documents=[text],
                metadatas=[{
                    "doc_id": doc_id,
                    "title": title,
                    "text_length": len(text)
                }]
            )
            print(f"✅ Added document {doc_id} to vector store")
        except Exception as e:
            print(f"❌ Error adding document to vector store: {str(e)}")
    
    def search(self, query_embedding: List[float], n_results: int = 5) -> List[Dict]:
        """Search for similar documents"""
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        'doc_id': results['metadatas'][0][i]['doc_id'],
                        'title': results['metadatas'][0][i]['title'],
                        'distance': results['distances'][0][i] if 'distances' in results else 0,
                        'similarity': 1 - results['distances'][0][i] if 'distances' in results else 1
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Error searching vector store: {str(e)}")
            return []
    
    def get_document_count(self) -> int:
        """Get total number of documents in vector store"""
        try:
            return self.collection.count()
        except:
            return 0
    
    def delete_document(self, doc_id: int):
        """Delete document from vector store"""
        try:
            self.collection.delete(ids=[f"doc_{doc_id}"])
            print(f"✅ Deleted document {doc_id} from vector store")
        except Exception as e:
            print(f"❌ Error deleting document: {str(e)}")
    
    def clear_all(self):
        """Clear all documents from vector store"""
        try:
            self.client.delete_collection("documents")
            self.collection = self.client.create_collection("documents")
            print("✅ Cleared vector store")
        except Exception as e:
            print(f"❌ Error clearing vector store: {str(e)}")