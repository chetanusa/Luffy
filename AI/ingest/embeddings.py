import sys
from pathlib import Path
from typing import List, Dict
from openai import OpenAI
import numpy as np

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from AI.config.settings import settings

class EmbeddingGenerator:
    """Generate embeddings for text using OpenAI"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "text-embedding-3-small"  # Cheaper and faster
        self.total_cost = 0.0
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            # Truncate if too long (max 8191 tokens)
            if len(text) > 30000:
                text = text[:30000]
            
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            
            # Calculate cost ($0.02 per 1M tokens)
            tokens = response.usage.total_tokens
            cost = tokens * 0.02 / 1_000_000
            self.total_cost += cost
            
            embedding = response.data[0].embedding
            return embedding
            
        except Exception as e:
            print(f"❌ Error generating embedding: {str(e)}")
            return []
    
    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        embeddings = []
        
        for idx, text in enumerate(texts):
            print(f"📊 Generating embedding {idx + 1}/{len(texts)}...")
            embedding = self.generate_embedding(text)
            if embedding:
                embeddings.append(embedding)
        
        print(f"✅ Generated {len(embeddings)} embeddings")
        print(f"💰 Total cost: ${self.total_cost:.4f}")
        
        return embeddings
    
    def get_total_cost(self) -> float:
        """Get total API cost"""
        return self.total_cost
    
    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)