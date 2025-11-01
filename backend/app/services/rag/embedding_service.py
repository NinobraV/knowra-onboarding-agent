"""
Embedding Service - Handles vector representation generation.

Responsibilities:
- Generate embeddings for text using OpenAI models
- Provide consistent embedding interface
- Handle batch embedding operations
"""
from typing import List

from langchain_openai import OpenAIEmbeddings


class EmbeddingService:
    """
    Service for generating text embeddings using OpenAI models.
    
    Wraps OpenAIEmbeddings to provide a consistent interface for
    generating vector representations of text.
    """
    
    def __init__(
        self,
        openai_api_key: str,
        model: str = "text-embedding-3-small"
    ):
        """
        Initialize the embedding service.
        
        Args:
            openai_api_key: OpenAI API key
            model: OpenAI embedding model to use
        """
        self.model = model
        self.embeddings = OpenAIEmbeddings(
            model=self.model,
            openai_api_key=openai_api_key
        )
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        if not texts:
            return []
        
        return self.embeddings.embed_documents(texts)
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a single query.
        
        Args:
            query: Query text to embed
            
        Returns:
            List[float]: Query embedding vector
        """
        return self.embeddings.embed_query(query)
    
    def get_embeddings_instance(self) -> OpenAIEmbeddings:
        """
        Get the underlying LangChain embeddings instance.
        
        Useful for integration with LangChain vector stores.
        
        Returns:
            OpenAIEmbeddings: LangChain embeddings instance
        """
        return self.embeddings
    
    def get_stats(self) -> dict:
        """
        Get embedding service statistics.
        
        Returns:
            dict: Service configuration statistics
        """
        return {
            "model": self.model,
            "provider": "OpenAI"
        }
