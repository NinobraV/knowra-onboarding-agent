"""
Legacy compatibility wrapper for RAG functionality.
This file maintains backward compatibility with existing imports.
All logic has been moved to app.services.rag_service.

DEPRECATED: Import from app.services.rag_service or app.core.dependencies instead.
"""
import warnings

from app.services.rag_service import RAGService
from app.core.dependencies import get_rag_service, rebuild_rag_service


# Deprecated: Use RAGService from app.services.rag_service
RAGAgent = RAGService


def get_rag_agent() -> RAGService:
    """
    DEPRECATED: Use get_rag_service from app.core.dependencies instead.
    
    Returns:
        RAGService: RAG service instance
    """
    warnings.warn(
        "get_rag_agent() is deprecated. Use get_rag_service() from app.core.dependencies",
        DeprecationWarning,
        stacklevel=2
    )
    return get_rag_service()


def rebuild_rag_agent() -> RAGService:
    """
    DEPRECATED: Use rebuild_rag_service from app.core.dependencies instead.
    
    Returns:
        RAGService: New RAG service instance
    """
    warnings.warn(
        "rebuild_rag_agent() is deprecated. Use rebuild_rag_service() from app.core.dependencies",
        DeprecationWarning,
        stacklevel=2
    )
    return rebuild_rag_service()


# For backward compatibility
__all__ = [
    "RAGAgent",
    "RAGService",
    "get_rag_agent",
    "rebuild_rag_agent"
]

