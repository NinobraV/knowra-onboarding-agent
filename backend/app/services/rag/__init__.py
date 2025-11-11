"""
RAG (Retrieval-Augmented Generation) Package

Enhanced modular RAG implementation with:
- Intelligent routing (heuristic + semantic)
- Safety analysis and content moderation  
- Advanced memory management with fact extraction
- Session and project scoping
- Automated memory cleanup
- Document chunking and embedding generation
- Vector store management and semantic search
- Result ranking and LLM interactions
- Pipeline orchestration

Main entry points: 
- RAGPipelineService (basic pipeline)
- EnhancedRAGPipelineService (optimized pipeline with all enhancements)
"""

# Base RAG components
from .rag_pipeline_service import RAGPipelineService
from .chunking_service import ChunkingService
from .embedding_service import EmbeddingService
from .vector_store_service import VectorStoreService
from .semantic_search_service import SemanticSearchService
from .ranking_service import RankingService
from .llm_service import LLMService

# Enhanced components (may not be available if dependencies missing)
try:
    from .enhanced_rag_pipeline_service import EnhancedRAGPipelineService
    from .router_service import RouterService, RouteDecision, RoutingResult
    from .safety_service import SafetyService, SafetyLevel, SafetyResult
    from .fact_extractor_service import FactExtractorService, FactType, ImportanceLevel
    from .enhanced_memory_service import EnhancedMemoryService
    from .memory_cleanup_service import MemoryCleanupService
    
    ENHANCED_COMPONENTS_AVAILABLE = True
    
    __all__ = [
        # Base components
        "RAGPipelineService",
        "ChunkingService", 
        "EmbeddingService",
        "VectorStoreService",
        "SemanticSearchService",
        "RankingService",
        "LLMService",
        # Enhanced components
        "EnhancedRAGPipelineService",
        "RouterService",
        "RouteDecision", 
        "RoutingResult",
        "SafetyService",
        "SafetyLevel",
        "SafetyResult", 
        "FactExtractorService",
        "FactType",
        "ImportanceLevel",
        "EnhancedMemoryService",
        "MemoryCleanupService"
    ]
    
except ImportError as e:
    # Enhanced components not available, only export base components
    ENHANCED_COMPONENTS_AVAILABLE = False
    
    __all__ = [
        "RAGPipelineService",
        "ChunkingService",
        "EmbeddingService", 
        "VectorStoreService",
        "SemanticSearchService",
        "RankingService",
        "LLMService",
    ]

__version__ = "2.0.0"
