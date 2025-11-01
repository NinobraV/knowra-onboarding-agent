"""
RAG (Retrieval-Augmented Generation) Package

Modular RAG implementation with separate services for:
- Document chunking
- Embedding generation
- Vector store management
- Semantic search
- Result ranking
- LLM interactions
- Pipeline orchestration

Main entry point: RAGPipelineService
"""

from .rag_pipeline_service import RAGPipelineService
from .chunking_service import ChunkingService
from .embedding_service import EmbeddingService
from .vector_store_service import VectorStoreService
from .semantic_search_service import SemanticSearchService
from .ranking_service import RankingService
from .llm_service import LLMService

__all__ = [
    "RAGPipelineService",
    "ChunkingService",
    "EmbeddingService",
    "VectorStoreService",
    "SemanticSearchService",
    "RankingService",
    "LLMService",
]

__version__ = "1.0.0"
