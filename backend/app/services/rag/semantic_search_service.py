# semantic_search_service.py
"""
Semantic Search Service - Coordinates search operations.

Responsibilities:
- Execute semantic searches using vector store
- Provide high-level search interface
- Handle query processing, score filtering and result formatting
"""

import logging
from typing import List, Tuple, Optional, Dict, Any

from langchain_core.documents import Document

from .vector_store_service import VectorStoreService

logger = logging.getLogger("semantic_search_service")
if not logger.handlers:
    import sys
    ch = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    ch.setFormatter(fmt)
    logger.addHandler(ch)
logger.setLevel("INFO")


class SemanticSearchService:
    """
    Service for coordinating semantic search operations.

    Wraps a VectorStoreService (Pinecone/FAISS/etc.) and exposes:
    - semantic_search(query, k, score_threshold, namespace) -> List[Document]
    - semantic_search_with_scores(query, k, namespace) -> List[(Document, score)]
    - get_retriever(k, search_type) to return lightweight retriever metadata
    """

    def __init__(self, vector_store_service: VectorStoreService):
        self.vector_store_service = vector_store_service

    def semantic_search(
        self,
        query: str,
        k: int = 5,
        score_threshold: float = 0.0,
        namespace: Optional[str] = None
    ) -> List[Document]:
        """
        Perform semantic search and return Documents passing score_threshold.

        Args:
            query: Query text
            k: number of results to return
            score_threshold: minimum score (lower = less similar for cosine depending on store)
            namespace: optional Pinecone namespace (e.g., "memory" for long-term memory)

        Returns:
            List[Document]: matching Documents ordered by score descending
        """
        try:
            # Use vector_store_service.semantic_search which returns Documents without scores
            # For score filtering we use search_by_vector to get scores.
            emb_fn = getattr(self.vector_store_service.embeddings, "embed_query", None) or getattr(self.vector_store_service.embeddings, "embed_text", None)
            if not emb_fn:
                # fallback to vector_store_service.semantic_search if embedding not available
                docs = self.vector_store_service.semantic_search(query, k=k, namespace=namespace)
                # No scores available; return as-is
                return docs

            query_vec = emb_fn(query)
            results = self.vector_store_service.search_by_vector(query_vec, k=k, namespace=namespace)

            docs: List[Document] = []
            for r in results:
                score = r.get("score", None)
                # If score is present and below threshold, skip it
                if score is not None and score < score_threshold:
                    continue
                text = r.get("text", "") or ""
                metadata = r.get("metadata", {}) or {}
                # Reattach score into metadata for downstream usage
                if score is not None:
                    metadata = dict(metadata)
                    metadata["_score"] = score
                docs.append(Document(page_content=text, metadata=metadata))
            return docs
        except Exception as e:
            logger.exception("semantic_search failed: %s", e)
            return []

    def semantic_search_with_scores(
        self,
        query: str,
        k: int = 5,
        namespace: Optional[str] = None
    ) -> List[Tuple[Document, float]]:
        """
        Return list of (Document, score) tuples for a query.

        Args:
            query: Query text
            k: number of results
            namespace: optional namespace to search (e.g., "memory")

        Returns:
            List[Tuple[Document, float]]
        """
        try:
            emb_fn = getattr(self.vector_store_service.embeddings, "embed_query", None) or getattr(self.vector_store_service.embeddings, "embed_text", None)
            if not emb_fn:
                # If embeddings not available, try semantic_search (no scores)
                docs = self.vector_store_service.semantic_search(query, k=k, namespace=namespace)
                return [(d, 0.0) for d in docs]

            query_vec = emb_fn(query)
            results = self.vector_store_service.search_by_vector(query_vec, k=k, namespace=namespace)
            out: List[Tuple[Document, float]] = []
            for r in results:
                score = r.get("score", 0.0)
                text = r.get("text", "") or ""
                metadata = r.get("metadata", {}) or {}
                doc = Document(page_content=text, metadata=metadata)
                out.append((doc, score))
            return out
        except Exception as e:
            logger.exception("semantic_search_with_scores failed: %s", e)
            return []

    def get_retriever(self, k: int = 5, search_type: str = "similarity") -> Dict[str, Any]:
        """
        Return a lightweight retriever configuration that can be passed to an agent.

        This does not return a full LangChain Retriever object but provides the necessary
        configuration; adapt as needed for LangChain integration.

        Returns:
            dict: {"index_name": ..., "k": k, "search_type": search_type}
        """
        try:
            return self.vector_store_service.get_retriever(k=k, search_type=search_type)
        except Exception as e:
            logger.exception("get_retriever failed: %s", e)
            return {"index_name": getattr(self.vector_store_service, "pinecone_index_name", None), "k": k, "search_type": search_type}

    def get_stats(self) -> Dict[str, Any]:
        try:
            stats = self.vector_store_service.get_stats()
            return {"backend": "pinecone", "vector_store_stats": stats}
        except Exception:
            return {"backend": "pinecone", "vector_store_stats": {}}
