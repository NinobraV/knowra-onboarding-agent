"""
Dependency injection for ingestion services.
"""
from functools import lru_cache

from app.services.ingestion_service import IngestionService
from app.core.config import settings


_ingestion_service: IngestionService = None


def get_ingestion_service() -> IngestionService:
    """
    Get or create the singleton ingestion service instance.
    
    Returns:
        IngestionService: The ingestion service instance
    """
    global _ingestion_service
    
    if _ingestion_service is None:
        _ingestion_service = IngestionService(
            data_dir=settings.DATA_DIR,
            persist_dir=settings.VECTOR_STORE_DIR,
            embedding_api_key=settings.OPENAI_EMBEDDING_API_KEY or settings.OPENAI_API_KEY,
            pinecone_api_key=settings.PINECONE_API_KEY,
            pinecone_environment=settings.PINECONE_ENVIRONMENT,
            pinecone_index_name=settings.PINECONE_INDEX_NAME,
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            embedding_model=settings.OPENAI_EMBEDDING_MODEL
        )
    
    return _ingestion_service


def rebuild_ingestion_service() -> IngestionService:
    """
    Rebuild the ingestion service (force recreate).
    
    Returns:
        IngestionService: New ingestion service instance
    """
    global _ingestion_service
    
    _ingestion_service = IngestionService(
        data_dir=settings.DATA_DIR,
        persist_dir=settings.VECTOR_STORE_DIR,
        embedding_api_key=settings.OPENAI_EMBEDDING_API_KEY or settings.OPENAI_API_KEY,
        pinecone_api_key=settings.PINECONE_API_KEY,
        pinecone_environment=settings.PINECONE_ENVIRONMENT,
        pinecone_index_name=settings.PINECONE_INDEX_NAME,
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        embedding_model=settings.OPENAI_EMBEDDING_MODEL
    )
    
    return _ingestion_service
