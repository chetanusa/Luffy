import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from AI.extraction.entity_extractor import EntityExtractor
from AI.graph.builder import GraphBuilder

def test_entity_extraction():
    """Test entity extraction"""
    text = """
    Machine Learning is a subset of Artificial Intelligence that enables computers to learn from data.
    Python is the most popular programming language for ML development.
    TensorFlow and PyTorch are leading frameworks created by Google and Meta respectively.
    """
    
    extractor = EntityExtractor()
    entities = extractor.extract_entities(text)
    
    print(f"\n✅ Extracted {len(entities)} entities:")
    for entity in entities:
        print(f"  - {entity['name']} ({entity['type']}) - Confidence: {entity['confidence']:.2f}")
    
    assert len(entities) > 0
    print(f"\n💰 Total cost: ${extractor.get_total_cost():.4f}")

def test_graph_builder():
    """Test Neo4j graph building"""
    graph = GraphBuilder()
    
    # Test entity
    test_entity = {
        'name': 'Test Concept',
        'type': 'CONCEPT',
        'confidence': 0.95,
        'context': 'Testing the graph builder'
    }
    
    graph.create_entity_node(test_entity, doc_id=999)
    
    count = graph.get_entity_count()
    print(f"✅ Total entities in graph: {count}")
    
    graph.close()

if __name__ == "__main__":
    test_entity_extraction()
    test_graph_builder()
    print("\n🎉 All extraction tests passed!")