import sys
from pathlib import Path
from typing import List, Dict, Optional
from collections import deque

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from AI.graph.builder import GraphBuilder

class GraphQueryEngine:
    """Query and traverse the knowledge graph"""
    
    def __init__(self):
        self.graph = GraphBuilder()
    
    def find_path(self, start_entity: str, end_entity: str, max_hops: int = 5) -> Optional[List[Dict]]:
        """Find shortest path between two entities using BFS"""
        with self.graph.driver.session() as session:
            query = """
            MATCH path = shortestPath(
                (start:Entity {name: $start})-[*..%d]-(end:Entity {name: $end})
            )
            RETURN [node in nodes(path) | node.name] as nodes,
                   [rel in relationships(path) | type(rel)] as relationships
            LIMIT 1
            """ % max_hops
            
            result = session.run(query, start=start_entity, end=end_entity)
            record = result.single()
            
            if not record:
                return None
            
            nodes = record['nodes']
            rels = record['relationships']
            
            # Format path
            path = []
            for i in range(len(nodes) - 1):
                path.append({
                    'from': nodes[i],
                    'relationship': rels[i],
                    'to': nodes[i + 1]
                })
            
            return path
    
    def find_related_entities(self, entity_name: str, max_depth: int = 2) -> List[Dict]:
        """Find all entities related to a given entity within max_depth hops"""
        with self.graph.driver.session() as session:
            query = """
            MATCH (start:Entity {name: $entity_name})-[r*1..%d]-(related:Entity)
            RETURN DISTINCT related.name as name, 
                   related.type as type,
                   length([rel in r]) as distance
            ORDER BY distance, name
            LIMIT 50
            """ % max_depth
            
            result = session.run(query, entity_name=entity_name)
            return [dict(record) for record in result]
    
    def find_common_connections(self, entity1: str, entity2: str) -> List[Dict]:
        """Find entities that connect two entities"""
        with self.graph.driver.session() as session:
            query = """
            MATCH (e1:Entity {name: $entity1})-[r1]-(bridge:Entity)-[r2]-(e2:Entity {name: $entity2})
            RETURN DISTINCT bridge.name as bridge_entity,
                   bridge.type as entity_type,
                   type(r1) as relationship1,
                   type(r2) as relationship2
            LIMIT 10
            """
            
            result = session.run(query, entity1=entity1, entity2=entity2)
            return [dict(record) for record in result]
    
    def get_entity_neighbors(self, entity_name: str) -> Dict:
        """Get all directly connected entities"""
        with self.graph.driver.session() as session:
            query = """
            MATCH (e:Entity {name: $entity_name})-[r]->(target:Entity)
            RETURN e.name as entity,
                   collect({
                       name: target.name,
                       type: target.type,
                       relationship: type(r)
                   }) as outgoing
            
            UNION
            
            MATCH (source:Entity)-[r]->(e:Entity {name: $entity_name})
            RETURN e.name as entity,
                   collect({
                       name: source.name,
                       type: source.type,
                       relationship: type(r)
                   }) as incoming
            """
            
            result = session.run(query, entity_name=entity_name)
            records = list(result)
            
            if not records:
                return {'entity': entity_name, 'outgoing': [], 'incoming': []}
            
            outgoing = []
            incoming = []
            
            for record in records:
                if 'outgoing' in record and record['outgoing'][0].get('name'):
                    outgoing.extend(record['outgoing'])
                if 'incoming' in record and record['incoming'][0].get('name'):
                    incoming.extend(record['incoming'])
            
            return {
                'entity': entity_name,
                'outgoing': outgoing,
                'incoming': incoming
            }
    
    def search_entities_by_type(self, entity_type: str) -> List[str]:
        """Get all entities of a specific type"""
        with self.graph.driver.session() as session:
            query = """
            MATCH (e:Entity {type: $entity_type})
            RETURN e.name as name
            ORDER BY name
            """
            result = session.run(query, entity_type=entity_type)
            return [record['name'] for record in result]
    
    def close(self):
        """Close database connection"""
        self.graph.close()