"""
Embedding Service - Handles vector representation generation.

Responsibilities:
- Generate embeddings for text using OpenAI models
- Provide consistent embedding interface
- Handle batch embedding operations
"""
from typing import List

import numpy as np
from langchain_openai import OpenAIEmbeddings
from sklearn.decomposition import PCA


class EmbeddingService:
    """
    Service for generating text embeddings using OpenAI models.
    
    Wraps OpenAIEmbeddings to provide a consistent interface for
    generating vector representations of text.
    """
    
    def __init__(
        self,
        openai_api_key: str,
        model: str = "text-embedding-3-small",
        pca_components: int = None
    ):
        """
        Initialize the embedding service.
        
        Args:
            openai_api_key: OpenAI API key
            model: OpenAI embedding model to use
            pca_components: Number of dimensions to reduce to using PCA
        """
        self.model = model
        self.embeddings = OpenAIEmbeddings(
            model=self.model,
            openai_api_key=openai_api_key
        )
        self.pca_components = pca_components
        self.pca = PCA(n_components=self.pca_components) if self.pca_components else None

    def _apply_pca(self, embeddings: List[List[float]]) -> List[List[float]]:
        """
        Apply PCA to reduce the dimensionality of embeddings.
        """
        if not self.pca:
            return embeddings
        
        embedding_array = np.array(embeddings)
        
        if not hasattr(self.pca, "components_"):
             self.pca.fit(embedding_array)

        reduced_embeddings = self.pca.transform(embedding_array)
        return reduced_embeddings.tolist()

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
        
        raw_embeddings = self.embeddings.embed_documents(texts)
        return self._apply_pca(raw_embeddings)
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a single query.
        
        Args:
            query: Query text to embed
            
        Returns:
            List[float]: Query embedding vector
        """
        raw_embedding = self.embeddings.embed_query(query)
        if not self.pca:
            return raw_embedding
        
        embedding_array = np.array(raw_embedding).reshape(1, -1)
        reduced_embedding = self.pca.transform(embedding_array)
        return reduced_embedding.flatten().tolist()
    
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
            "provider": "OpenAI",
            "pca_components": self.pca_components
        }
