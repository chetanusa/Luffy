import json
import sys
from pathlib import Path
from typing import List, Dict
from openai import OpenAI

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from AI.config.settings import settings
from AI.prompts.entity_extraction import get_entity_extraction_prompt

class EntityExtractor:
    """Extract entities from text using GPT-4o-mini"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"
        self.total_cost = 0.0
    
    def extract_entities(self, text: str) -> List[Dict]:
        """Extract entities from text"""
        try:
            # Get prompt
            prompt = get_entity_extraction_prompt(text)
            
            # Call OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert knowledge extraction AI. You ONLY respond with valid JSON, no other text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # Calculate cost (GPT-4o-mini: $0.15 per 1M input tokens, $0.60 per 1M output tokens)
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            cost = (input_tokens * 0.15 / 1_000_000) + (output_tokens * 0.60 / 1_000_000)
            self.total_cost += cost
            
            print(f"💰 API Cost: ${cost:.4f} (Total: ${self.total_cost:.4f})")
            
            # Parse response
            content = response.choices[0].message.content.strip()
            
            # Debug: print first 100 chars
            print(f"📥 Response preview: {content[:100]}...")
            
            # Clean up the response
            # Remove markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1]
            if "```" in content:
                content = content.split("```")[0]
            
            # Remove any leading/trailing whitespace
            content = content.strip()
            
            # Try to find JSON object
            if not content.startswith("{"):
                # Try to find the first { and last }
                start = content.find("{")
                end = content.rfind("}") + 1
                if start != -1 and end > start:
                    content = content[start:end]
            
            print(f"🔧 Cleaned content: {content[:100]}...")
            
            # Parse JSON
            result = json.loads(content)
            entities = result.get("entities", [])
            
            print(f"✅ Extracted {len(entities)} entities")
            return entities
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse Error: {e}")
            print(f"📄 Full response: {content}")
            return []
        except Exception as e:
            print(f"❌ Error extracting entities: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return []
    
    def batch_extract(self, chunks: List[str]) -> List[Dict]:
        """Extract entities from multiple text chunks"""
        all_entities = []
        
        for idx, chunk in enumerate(chunks):
            print(f"\n📄 Processing chunk {idx + 1}/{len(chunks)}...")
            entities = self.extract_entities(chunk)
            all_entities.extend(entities)
        
        # Deduplicate entities by name (keep highest confidence)
        unique_entities = {}
        for entity in all_entities:
            name = entity['name'].lower()
            if name not in unique_entities or entity['confidence'] > unique_entities[name]['confidence']:
                unique_entities[name] = entity
        
        return list(unique_entities.values())
    
    def get_total_cost(self) -> float:
        """Get total API cost"""
        return self.total_cost