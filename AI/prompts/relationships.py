RELATIONSHIP_EXTRACTION_PROMPT = """You are an expert at discovering relationships between entities in text.

Given this text and these entities, find relationships between them.

Entities:
{entities}

Relationship types to identify:
- WORKS_WITH: Person works with a technology/organization
- RELATES_TO: Concepts that are related or connected
- PART_OF: Entity is part of another entity
- USES: Entity uses another entity
- REQUIRES: Entity requires another entity
- IMPLEMENTS: Entity implements another entity
- MANAGES: Person/entity manages another entity

For each relationship, provide:
- source: Name of source entity (must be from the list above)
- target: Name of target entity (must be from the list above)
- type: Relationship type
- confidence: 0.0-1.0 (how confident you are)
- context: Brief explanation from the text

Return ONLY valid JSON in this format:
{{{{
  "relationships": [
    {{{{
      "source": "Machine Learning",
      "target": "Artificial Intelligence",
      "type": "PART_OF",
      "confidence": 0.95,
      "context": "Machine Learning is described as a subset of AI"
    }}}}
  ]
}}}}

Text:
{text}

Remember: Return ONLY the JSON, no other text. Only create relationships between entities in the list above."""


def get_relationship_extraction_prompt(text: str, entities: list, max_length: int = 3000) -> str:
    """Get relationship extraction prompt with text and entities"""
    # Truncate text if too long
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    # Format entities list
    entity_list = "\n".join([f"- {e['name']} ({e['type']})" for e in entities])
    
    return RELATIONSHIP_EXTRACTION_PROMPT.format(
        entities=entity_list,
        text=text
    )