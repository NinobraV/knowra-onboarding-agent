"""
Core configuration and settings for the Knowledge Chatbot backend.
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Application
    APP_NAME: str = "Knowledge Chatbot API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "RAG-powered chatbot with streaming responses"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000"
    ]
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_TEMPERATURE: float = 0.7
    
    # RAG Configuration
    DATA_DIR: str = "./backend/data/raw"
    VECTOR_STORE_DIR: str = "./backend/chroma_db"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    RETRIEVER_K: int = 5
    MEMORY_WINDOW: int = 10
    
    # SSE Streaming
    SSE_DELAY: float = 0.01
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Get the global settings instance.
    
    Returns:
        Settings: Application settings
    """
    return settings
