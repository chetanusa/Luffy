import json
import sys
from pathlib import Path
from typing import List, Dict
from openai import OpenAI

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from AI.config.settings import settings
from AI.prompts.relationships import get_relationship_extraction_prompt

class RelationshipMapper:
    """Extract relationships between entities using GPT-4o-mini"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"
        self.total_cost = 0.0
    
    def extract_relationships(self, text: str, entities: List[Dict]) -> List[Dict]:
        """Extract relationships between entities"""
        if len(entities) < 2:
            print("⚠️ Need at least 2 entities to find relationships")
            return []
        
        try:
            # Get prompt
            prompt = get_relationship_extraction_prompt(text, entities)
            
            # Call OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at discovering relationships between concepts. You ONLY respond with valid JSON, no other text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # Calculate cost
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            cost = (input_tokens * 0.15 / 1_000_000) + (output_tokens * 0.60 / 1_000_000)
            self.total_cost += cost
            
            print(f"💰 API Cost: ${cost:.4f} (Total: ${self.total_cost:.4f})")
            
            # Parse response
            content = response.choices[0].message.content.strip()
            
            # Clean up response
            if "```json" in content:
                content = content.split("```json")[1]
            if "```" in content:
                content = content.split("```")[0]
            content = content.strip()
            
            if not content.startswith("{"):
                start = content.find("{")
                end = content.rfind("}") + 1
                if start != -1 and end > start:
                    content = content[start:end]
            
            # Parse JSON
            result = json.loads(content)
            relationships = result.get("relationships", [])
            
            print(f"✅ Found {len(relationships)} relationships")
            return relationships
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse Error: {e}")
            print(f"📄 Response: {content[:200]}")
            return []
        except Exception as e:
            print(f"❌ Error extracting relationships: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return []
    
    def batch_extract(self, chunks: List[str], entities: List[Dict]) -> List[Dict]:
        """Extract relationships from multiple chunks"""
        all_relationships = []
        
        for idx, chunk in enumerate(chunks):
            print(f"\n📄 Processing chunk {idx + 1}/{len(chunks)} for relationships...")
            relationships = self.extract_relationships(chunk, entities)
            all_relationships.extend(relationships)
        
        # Deduplicate relationships
        unique_rels = {}
        for rel in all_relationships:
            key = f"{rel['source']}_{rel['type']}_{rel['target']}".lower()
            if key not in unique_rels or rel['confidence'] > unique_rels[key]['confidence']:
                unique_rels[key] = rel
        
        return list(unique_rels.values())
    
    def get_total_cost(self) -> float:
        """Get total API cost"""
        return self.total_cost