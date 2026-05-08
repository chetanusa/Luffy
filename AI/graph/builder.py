import sys
from pathlib import Path
from typing import List, Dict
from neo4j import GraphDatabase

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from AI.config.settings import settings

class GraphBuilder:
    """Build knowledge graph in Neo4j"""
    
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
    
    def close(self):
        """Close Neo4j connection"""
        self.driver.close()
    
    def create_entity_node(self, entity: Dict, doc_id: int):
        """Create entity node in Neo4j"""
        with self.driver.session() as session:
            query = """
            MERGE (e:Entity {name: $name, type: $type})
            ON CREATE SET 
                e.confidence = $confidence,
                e.context = $context,
                e.created_at = datetime()
            ON MATCH SET
                e.confidence = CASE 
                    WHEN $confidence > e.confidence THEN $confidence 
                    ELSE e.confidence 
                END
            
            MERGE (d:Document {id: $doc_id})
            MERGE (e)-[r:MENTIONED_IN]->(d)
            ON CREATE SET r.context = $context
            
            RETURN e.name as name
            """
            
            result = session.run(
                query,
                name=entity['name'],
                type=entity['type'],
                confidence=entity['confidence'],
                context=entity.get('context', ''),
                doc_id=doc_id
            )
            return result.single()
    
    def create_entities_batch(self, entities: List[Dict], doc_id: int):
        """Create multiple entity nodes"""
        created_count = 0
        
        for entity in entities:
            try:
                self.create_entity_node(entity, doc_id)
                created_count += 1
            except Exception as e:
                print(f"❌ Error creating entity {entity['name']}: {str(e)}")
        
        print(f"✅ Created {created_count} entity nodes in Neo4j")
        return created_count
    
    def get_entity_count(self) -> int:
        """Get total number of entities"""
        with self.driver.session() as session:
            result = session.run("MATCH (e:Entity) RETURN count(e) as count")
            return result.single()["count"]
    
    def get_document_entities(self, doc_id: int) -> List[Dict]:
        """Get all entities for a document"""
        with self.driver.session() as session:
            query = """
            MATCH (e:Entity)-[:MENTIONED_IN]->(d:Document {id: $doc_id})
            RETURN e.name as name, e.type as type, e.confidence as confidence
            ORDER BY e.confidence DESC
            """
            result = session.run(query, doc_id=doc_id)
            return [dict(record) for record in result]
    
    def clear_all(self):
        """Clear all nodes and relationships (for testing)"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("🗑️ Cleared all Neo4j data")
    def create_relationship(self, relationship: Dict):
        """Create relationship between entities"""
        with self.driver.session() as session:
            # Create relationship with dynamic type
            query = f"""
            MATCH (source:Entity {{name: $source_name}})
            MATCH (target:Entity {{name: $target_name}})
            MERGE (source)-[r:{relationship['type']}]->(target)
            ON CREATE SET 
                r.confidence = $confidence,
                r.context = $context,
                r.created_at = datetime()
            ON MATCH SET
                r.confidence = CASE 
                    WHEN $confidence > r.confidence THEN $confidence 
                    ELSE r.confidence 
                END
            RETURN r
            """
            
            try:
                result = session.run(
                    query,
                    source_name=relationship['source'],
                    target_name=relationship['target'],
                    confidence=relationship['confidence'],
                    context=relationship.get('context', '')
                )
                return result.single()
            except Exception as e:
                print(f"❌ Error creating relationship: {str(e)}")
                return None
    
    def create_relationships_batch(self, relationships: List[Dict]) -> int:
        """Create multiple relationships"""
        created_count = 0
        
        for rel in relationships:
            try:
                result = self.create_relationship(rel)
                if result:
                    created_count += 1
            except Exception as e:
                print(f"❌ Error creating relationship {rel['source']} -> {rel['target']}: {str(e)}")
        
        print(f"✅ Created {created_count} relationships in Neo4j")
        return created_count
    
    def get_relationship_count(self) -> int:
        """Get total number of relationships"""
        with self.driver.session() as session:
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            return result.single()["count"]
    
    def get_document_graph(self, doc_id: int) -> Dict:
        """Get full graph for a document (entities + relationships)"""
        with self.driver.session() as session:
            query = """
            MATCH (e:Entity)-[:MENTIONED_IN]->(d:Document {id: $doc_id})
            OPTIONAL MATCH (e)-[r]->(e2:Entity)-[:MENTIONED_IN]->(d)
            RETURN 
                collect(DISTINCT {name: e.name, type: e.type}) as entities,
                collect(DISTINCT {
                    source: e.name, 
                    target: e2.name, 
                    type: type(r),
                    confidence: r.confidence
                }) as relationships
            """
            result = session.run(query, doc_id=doc_id)
            data = result.single()
            
            return {
                'entities': data['entities'] if data else [],
                'relationships': [r for r in data['relationships'] if r['target']] if data else []
            }