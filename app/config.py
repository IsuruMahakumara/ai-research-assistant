from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    app_name: str = "AI Research Assistant"
    debug: bool = False
    
    # HuggingFace Configuration
    hf_api_token: str = ""
    hf_model_id: str = "mistralai/Mistral-7B-Instruct-v0.2"
    
    # Vector Store Configuration
    vector_store_path: str = "./data/vector_store"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Chunking Configuration
    chunk_size: int = 512
    chunk_overlap: int = 50
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

