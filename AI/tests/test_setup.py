import pytest
from config.settings import settings


def test_settings_loaded():
    """Test that settings are loaded"""
    assert settings.OPENAI_API_KEY
    assert settings.NEO4J_URI
    print("✅ Settings loaded successfully")

def test_openai_connection():
    """Test OpenAI API connection"""
    from openai import OpenAI
    
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    # Test with a minimal call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say 'test'"}],
        max_tokens=5
    )
    
    assert response.choices[0].message.content
    print(f"✅ OpenAI connected: {response.choices[0].message.content}")

def test_neo4j_connection():
    """Test Neo4j connection"""
    from neo4j import GraphDatabase
    
    driver = GraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
    )
    
    with driver.session() as session:
        result = session.run("RETURN 1 AS num")
        assert result.single()["num"] == 1
    
    driver.close()
    print("✅ Neo4j connected")

def test_postgres_connection():
    """Test PostgreSQL connection"""
    from sqlalchemy import create_engine, text
    
    db_url = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1
    
    print("✅ PostgreSQL connected")

if __name__ == "__main__":
    test_settings_loaded()
    test_openai_connection()
    test_neo4j_connection()
    test_postgres_connection()
    print("\n🎉 All connections successful!")