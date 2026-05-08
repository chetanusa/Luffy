ENTITY_EXTRACTION_PROMPT = """You are an expert knowledge extraction AI. Extract entities and concepts from the following text.

Extract these entity types:
- PERSON: People, authors, researchers
- CONCEPT: Ideas, theories, methodologies, frameworks
- TECHNOLOGY: Tools, software, programming languages, platforms
- ORGANIZATION: Companies, institutions, projects
- TOPIC: Subject areas, domains, fields of study

For each entity, provide:
- name: The entity name
- type: Entity type (PERSON, CONCEPT, TECHNOLOGY, ORGANIZATION, TOPIC)
- confidence: 0.0-1.0 (how confident you are)
- context: Brief explanation of why this entity is important in the text

Return ONLY valid JSON in this format:
{{
  "entities": [
    {{
      "name": "Machine Learning",
      "type": "CONCEPT",
      "confidence": 0.95,
      "context": "Core methodology discussed throughout the document"
    }}
  ]
}}

Text to analyze:
{text}

Remember: Return ONLY the JSON, no other text."""


def get_entity_extraction_prompt(text: str, max_length: int = 3000) -> str:
    """Get entity extraction prompt with text"""
    # Truncate text if too long
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    return ENTITY_EXTRACTION_PROMPT.format(text=text)