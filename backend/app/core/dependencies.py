"""
Dependency injection and shared dependencies for the application.
"""
from typing import Generator
from functools import lru_cache

from app.core.config import Settings, get_settings
from app.services.rag_service import RAGService


# Global RAG service instance
_rag_service: RAGService = None


@lru_cache()
def get_settings_cached() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings: Cached application settings
    """
    return get_settings()


def get_rag_service() -> RAGService:
    """
    Get or create the global RAG service instance.
    
    Returns:
        RAGService: RAG service instance
    """
    global _rag_service
    if _rag_service is None:
        settings = get_settings_cached()
        _rag_service = RAGService(
            data_dir=settings.DATA_DIR,
            persist_dir=settings.VECTOR_STORE_DIR,
            openai_api_key=settings.OPENAI_API_KEY
        )
    return _rag_service


def rebuild_rag_service() -> RAGService:
    """
    Force rebuild of the RAG service.
    
    Returns:
        RAGService: New RAG service instance
    """
    global _rag_service
    settings = get_settings_cached()
    _rag_service = RAGService(
        data_dir=settings.DATA_DIR,
        persist_dir=settings.VECTOR_STORE_DIR,
        openai_api_key=settings.OPENAI_API_KEY
    )
    return _rag_service
