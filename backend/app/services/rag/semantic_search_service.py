"""
Semantic Search Service - Coordinates search operations.

Responsibilities:
- Execute semantic searches using vector store
- Provide high-level search interface
- Handle query processing and result formatting
"""
from typing import List

from langchain_core.documents import Document

from .vector_store_service import VectorStoreService


class SemanticSearchService:
    """
    Service for coordinating semantic search operations.
    
    Provides a high-level interface for searching the knowledge base
    using the vector store's similarity search capabilities.
    """
    
    def __init__(self, vector_store_service: VectorStoreService):
        """
        Initialize the semantic search service.
        
        Args:
            vector_store_service: Vector store service instance
        """
        self.vector_store_service = vector_store_service
    
    def semantic_search(
        self,
        query: str,
        k: int = 5,
        score_threshold: float = 0.0
    ) -> List[Document]:
        """
        Perform semantic search on the knowledge base.
        
        Args:
            query: Search query text
            k: Number of documents to retrieve
            score_threshold: Minimum similarity score (0.0 to 1.0)
            
        Returns:
            List[Document]: Most relevant documents
        """
        results = self.vector_store_service.similarity_search(query, k=k)
        
        # TODO: Implement score filtering when score_threshold > 0.0
        # Note: Pinecone similarity_search returns top-k most similar documents
        # For score-based filtering, use similarity_search_with_score
        
        return results
    
    def search_with_scores(self, query: str, k: int = 5) -> List[tuple]:
        """
        Perform semantic search with relevance scores.
        
        Args:
            query: Search query text
            k: Number of documents to retrieve
            
        Returns:
            List[tuple]: List of (document, score) tuples
        """
        if not self.vector_store_service.vectorstore:
            raise ValueError("Vector store not initialized")
        
        return self.vector_store_service.vectorstore.similarity_search_with_score(
            query, k=k
        )
    
    def get_retriever(self, k: int = 5, search_type: str = "similarity"):
        """
        Get a retriever for use in LangChain agents/chains.
        
        Args:
            k: Number of documents to retrieve
            search_type: Type of search ("similarity" or "mmr")
            
        Returns:
            Retriever: LangChain retriever instance
        """
        return self.vector_store_service.get_retriever(k=k, search_type=search_type)
    
    def get_stats(self) -> dict:
        """
        Get search service statistics.
        
        Returns:
            dict: Service statistics
        """
        return {
            "search_backend": "Pinecone",
            "search_algorithm": "cosine_similarity"
        }
