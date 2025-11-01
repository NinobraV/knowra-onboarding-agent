"""
Ranking Service - Ranks and filters search results.

Responsibilities:
- Rank documents by relevance score
- Apply filtering and re-ranking strategies
- Provide sorted results for LLM context
"""
from typing import List, Tuple

from langchain_core.documents import Document


class RankingService:
    """
    Service for ranking and filtering search results.
    
    Applies relevance-based ranking and filtering to ensure
    the most relevant documents are provided to the LLM.
    """
    
    def __init__(self, score_threshold: float = 0.0):
        """
        Initialize the ranking service.
        
        Args:
            score_threshold: Minimum relevance score (0.0 to 1.0)
        """
        self.score_threshold = score_threshold
    
    def rank_by_score(
        self,
        results: List[Tuple[Document, float]],
        reverse: bool = False
    ) -> List[Tuple[Document, float]]:
        """
        Rank documents by their similarity scores.
        
        Args:
            results: List of (document, score) tuples
            reverse: If True, sort ascending; if False, sort descending
            
        Returns:
            List[Tuple[Document, float]]: Sorted results
        """
        return sorted(results, key=lambda x: x[1], reverse=not reverse)
    
    def filter_by_threshold(
        self,
        results: List[Tuple[Document, float]]
    ) -> List[Tuple[Document, float]]:
        """
        Filter results by minimum score threshold.
        
        Args:
            results: List of (document, score) tuples
            
        Returns:
            List[Tuple[Document, float]]: Filtered results
        """
        return [
            (doc, score) for doc, score in results
            if score >= self.score_threshold
        ]
    
    def rank_results(
        self,
        results: List[Tuple[Document, float]],
        apply_threshold: bool = True
    ) -> List[Document]:
        """
        Complete ranking pipeline: filter and sort results.
        
        Args:
            results: List of (document, score) tuples
            apply_threshold: Whether to apply score threshold
            
        Returns:
            List[Document]: Ranked documents (without scores)
        """
        # Filter by threshold if enabled
        if apply_threshold and self.score_threshold > 0.0:
            results = self.filter_by_threshold(results)
        
        # Sort by score (highest first)
        ranked = self.rank_by_score(results, reverse=False)
        
        # Extract documents only
        return [doc for doc, score in ranked]
    
    def deduplicate_by_source(
        self,
        documents: List[Document]
    ) -> List[Document]:
        """
        Remove duplicate documents from the same source.
        
        Args:
            documents: List of documents
            
        Returns:
            List[Document]: Deduplicated documents
        """
        seen_sources = set()
        unique_docs = []
        
        for doc in documents:
            source = doc.metadata.get("source", "")
            if source not in seen_sources:
                seen_sources.add(source)
                unique_docs.append(doc)
        
        return unique_docs
    
    def limit_results(
        self,
        documents: List[Document],
        max_results: int
    ) -> List[Document]:
        """
        Limit the number of results.
        
        Args:
            documents: List of documents
            max_results: Maximum number of results to return
            
        Returns:
            List[Document]: Limited results
        """
        return documents[:max_results]
    
    def get_stats(self) -> dict:
        """
        Get ranking service statistics.
        
        Returns:
            dict: Service statistics
        """
        return {
            "score_threshold": self.score_threshold,
            "ranking_strategy": "similarity_score"
        }
