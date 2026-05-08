import sys
from pathlib import Path
from typing import List, Dict
from openai import OpenAI

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from AI.config.settings import settings
from AI.reasoning.query_engine import GraphQueryEngine

class AIReasoner:
    """Use GPT to answer complex questions using graph traversal"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"
        self.query_engine = GraphQueryEngine()
        self.total_cost = 0.0
    
    def answer_question(self, question: str) -> Dict:
        """Answer a question by first gathering graph context, then reasoning"""
        try:
            # Step 1: Extract entities from question
            entities_in_question = self._extract_entities_from_question(question)
            
            # Step 2: Gather graph context for those entities
            context = self._gather_graph_context(entities_in_question)
            
            # Step 3: Answer using the context
            answer = self._generate_answer(question, context)
            
            return answer
            
        except Exception as e:
            print(f"❌ Error in AI reasoning: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'answer': f"Error: {str(e)}",
                'cost': 0,
                'context_used': {}
            }
    
    def _extract_entities_from_question(self, question: str) -> List[str]:
        """Extract potential entity names from the question"""
        # Get all entities from graph
        with self.query_engine.graph.driver.session() as session:
            result = session.run("MATCH (e:Entity) RETURN e.name as name")
            all_entities = [r['name'] for r in result]
        
        # Find which entities are mentioned in the question
        question_lower = question.lower()
        found_entities = []
        
        for entity in all_entities:
            if entity.lower() in question_lower:
                found_entities.append(entity)
        
        return found_entities
    
    def _gather_graph_context(self, entities: List[str]) -> Dict:
        """Gather comprehensive context for entities"""
        context = {
            'entities_found': entities,
            'entity_details': []
        }
        
        for entity in entities:
            # Get neighbors
            neighbors = self.query_engine.get_entity_neighbors(entity)
            
            # Get related entities
            related = self.query_engine.find_related_entities(entity, max_depth=2)
            
            context['entity_details'].append({
                'entity': entity,
                'neighbors': neighbors,
                'related': related[:10]
            })
        
        return context
    
    def _generate_answer(self, question: str, context: Dict) -> Dict:
        """Generate answer using GPT with graph context"""
        # Format context
        context_text = self._format_context(context)
        
        prompt = f"""You are a knowledge graph reasoning AI. Answer the question using ONLY the provided graph context.

Graph Context:
{context_text}

Question: {question}

Instructions:
- If the answer exists in the graph context, provide a clear answer
- If you need to make connections between entities, explain the reasoning
- If the information is NOT in the graph context, clearly state: "The information needed to answer this question is not in the knowledge graph."
- Be specific and cite the entities and relationships you're using

Answer:"""
        
        # Call OpenAI
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful AI that answers questions using knowledge graph data. Be honest when information is not available."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        # Calculate cost
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cost = (input_tokens * 0.15 / 1_000_000) + (output_tokens * 0.60 / 1_000_000)
        self.total_cost += cost
        
        answer = response.choices[0].message.content.strip()
        
        return {
            'answer': answer,
            'cost': cost,
            'context_used': context
        }
    
    def _format_context(self, context: Dict) -> str:
        """Format graph context for the prompt"""
        if not context.get('entities_found'):
            return "No relevant entities found in the knowledge graph for this question."
        
        lines = [f"Found {len(context['entities_found'])} relevant entities: {', '.join(context['entities_found'])}\n"]
        
        for detail in context.get('entity_details', []):
            entity = detail['entity']
            lines.append(f"\n=== {entity} ===")
            
            neighbors = detail.get('neighbors', {})
            
            if neighbors.get('outgoing'):
                lines.append("\nDirect relationships (outgoing):")
                for conn in neighbors['outgoing'][:10]:
                    lines.append(f"  - {entity} --[{conn['relationship']}]--> {conn['name']} ({conn['type']})")
            
            if neighbors.get('incoming'):
                lines.append("\nDirect relationships (incoming):")
                for conn in neighbors['incoming'][:10]:
                    lines.append(f"  - {conn['name']} ({conn['type']}) --[{conn['relationship']}]--> {entity}")
            
            related = detail.get('related', [])
            if related:
                lines.append("\nExtended network:")
                for rel in related[:5]:
                    lines.append(f"  - {rel['name']} ({rel['type']}) - {rel['distance']} hops away")
        
        return "\n".join(lines)
    
    def get_total_cost(self) -> float:
        """Get total reasoning cost"""
        return self.total_cost
    
    def close(self):
        """Close connections"""
        self.query_engine.close()
