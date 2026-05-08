from pydantic_settings import BaseSettings
from pathlib import Path
import os

class Settings(BaseSettings):
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    
    # Neo4j
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "mindweave123"
    
    # PostgreSQL
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "mindweave"
    POSTGRES_USER: str = "mindweave_user"
    POSTGRES_PASSWORD: str = "mindweave123"
    
    # ChromaDB
    CHROMA_PATH: str = "./data/chroma"
    
    # Cost Limits
    COST_LIMIT: float = 5.0
    WARN_AT_COST: float = 4.0
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "data" / "uploads"
    
    class Config:
        env_file = str(Path(__file__).parent.parent.parent / ".env")
        case_sensitive = True

settings = Settings()

# Create directories
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
Path(settings.CHROMA_PATH).mkdir(parents=True, exist_ok=True)