"""
RAG (Retrieval-Augmented Generation) service implementation.
Handles vector store management, document processing, and agent interactions.

DEPRECATED: This module provides backward compatibility.
New code should use: from app.services.rag import RAGPipelineService

This class is now a thin wrapper around the modular RAG pipeline.
"""
from typing import Dict, Any, AsyncGenerator

from app.core.config import settings
from app.services.rag import RAGPipelineService


class RAGService:
    """
    RAG Service - Backward compatibility wrapper.
    
    DEPRECATED: This is a thin wrapper around RAGPipelineService.
    New code should import RAGPipelineService directly.
    
    Provides:
    - Document loading and chunking
    - Vector store management with auto-rebuild
    - Conversational agent with memory
    - Streaming and non-streaming responses
    """
    
    def __init__(
        self,
        data_dir: str = None,
        persist_dir: str = None,
        openai_api_key: str = None
    ):
        """
        Initialize the RAG service.
        
        Args:
            data_dir: Directory containing markdown knowledge base files
            persist_dir: Directory for vector store persistence (legacy)
            openai_api_key: OpenAI API key
        """
        # Initialize the modular pipeline service with Pinecone
        self._pipeline = RAGPipelineService(
            data_dir=data_dir or settings.DATA_DIR,
            persist_dir=persist_dir or settings.VECTOR_STORE_DIR,
            openai_base_url=settings.OPENAI_BASE_URL,
            openai_api_key=openai_api_key or settings.OPENAI_API_KEY,
            embedding_api_key=settings.OPENAI_EMBEDDING_API_KEY or settings.OPENAI_API_KEY,
            pinecone_api_key=settings.PINECONE_API_KEY,
            pinecone_environment=settings.PINECONE_ENVIRONMENT,
            pinecone_index_name=settings.PINECONE_INDEX_NAME,
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            embedding_model=settings.OPENAI_EMBEDDING_MODEL,
            llm_model=settings.OPENAI_MODEL,
            llm_temperature=settings.OPENAI_TEMPERATURE,
            retriever_k=settings.RETRIEVER_K,
            memory_window=settings.MEMORY_WINDOW,
            auto_rebuild=settings.AUTO_REBUILD_ENABLED,
            chunk_add_section_headers=settings.CHUNK_ADD_SECTION_HEADERS,
            chunk_extract_metadata=settings.CHUNK_EXTRACT_METADATA
        )
    
    def rebuild_if_needed(self) -> bool:
        """
        Check and rebuild vector store if files changed.
        
        Returns:
            bool: True if rebuild occurred
        """
        return self._pipeline.rebuild_if_needed()
    
    async def stream_response(self, query: str) -> AsyncGenerator[str, None]:
        """
        Stream response from agent.
        
        Args:
            query: User query
            
        Yields:
            str: Response chunks
        """
        async for chunk in self._pipeline.stream_response(query):
            yield chunk
    
    def chat(self, query: str) -> str:
        """
        Non-streaming chat response.
        
        Args:
            query: User query
            
        Returns:
            str: Complete response
        """
        return self._pipeline.chat(query)
    
    def clear_memory(self) -> None:
        """Clear conversation memory."""
        self._pipeline.clear_memory()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG system.
        
        Returns:
            Dict[str, Any]: System statistics
        """
        return self._pipeline.get_stats()
