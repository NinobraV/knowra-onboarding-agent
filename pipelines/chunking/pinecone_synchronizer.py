"""
Pinecone Synchronizer - Manage vector updates with change detection

This module handles Pinecone index synchronization, including deletion
of outdated vectors and insertion of new embeddings.
"""

from typing import List, Dict, Optional, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PineconeSynchronizer:
    """
    Synchronize document chunks with Pinecone vector database.
    
    Handles insertion, deletion, and updates with namespace organization.
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        environment: Optional[str] = None,
        index_name: str = "knowledge-base",
        namespace: str = "knowledge_base",
        dry_run: bool = False
    ):
        """
        Initialize Pinecone synchronizer.
        
        Args:
            api_key: Pinecone API key (optional, can use env var)
            environment: Pinecone environment (optional, can use env var)
            index_name: Name of Pinecone index
            namespace: Namespace for organization
            dry_run: If True, simulate operations without actual API calls
        """
        self.index_name = index_name
        self.namespace = namespace
        self.dry_run = dry_run
        self.index = None
        
        if not dry_run:
            try:
                import pinecone
                
                # Initialize Pinecone
                if api_key and environment:
                    pinecone.init(api_key=api_key, environment=environment)
                else:
                    # Try to use environment variables
                    pinecone.init()
                
                self.index = pinecone.Index(index_name)
                logger.info(f"✅ Connected to Pinecone index: {index_name}")
            except ImportError:
                logger.warning("⚠️  Pinecone library not installed. Running in dry-run mode.")
                self.dry_run = True
            except Exception as e:
                logger.error(f"❌ Failed to connect to Pinecone: {e}")
                self.dry_run = True
    
    def delete_document_vectors(self, doc_id: str) -> int:
        """
        Delete all vectors associated with a document ID.
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            Number of vectors deleted (or 0 in dry-run)
        """
        if self.dry_run:
            logger.info(f"🔵 [DRY RUN] Would delete vectors for doc_id: {doc_id}")
            return 0
        
        try:
            # Query to find all chunk IDs for this document
            # Pinecone filter: metadata.doc_id == doc_id
            filter_dict = {"doc_id": doc_id}
            
            # Delete by filter
            self.index.delete(
                filter=filter_dict,
                namespace=self.namespace
            )
            
            logger.info(f"🗑️  Deleted vectors for doc_id: {doc_id}")
            return 1  # Return success
            
        except Exception as e:
            logger.error(f"❌ Failed to delete vectors for {doc_id}: {e}")
            return 0
    
    def upsert_chunks(
        self, 
        chunks: List[Dict[str, Any]], 
        embeddings: List[List[float]]
    ) -> int:
        """
        Upsert chunk vectors to Pinecone.
        
        Args:
            chunks: List of chunk dictionaries with metadata
            embeddings: List of embedding vectors
            
        Returns:
            Number of vectors upserted
        """
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"Chunks ({len(chunks)}) and embeddings ({len(embeddings)}) "
                "must have the same length"
            )
        
        if self.dry_run:
            logger.info(
                f"🔵 [DRY RUN] Would upsert {len(chunks)} vectors "
                f"to namespace '{self.namespace}'"
            )
            return len(chunks)
        
        try:
            # Prepare vectors for upsert
            vectors = []
            for chunk, embedding in zip(chunks, embeddings):
                vector = {
                    "id": chunk["chunk_id"],
                    "values": embedding,
                    "metadata": chunk.get("metadata", {})
                }
                vectors.append(vector)
            
            # Upsert in batches of 100
            batch_size = 100
            total_upserted = 0
            
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(
                    vectors=batch,
                    namespace=self.namespace
                )
                total_upserted += len(batch)
                logger.info(
                    f"📤 Upserted batch {i//batch_size + 1}: "
                    f"{len(batch)} vectors"
                )
            
            logger.info(
                f"✅ Successfully upserted {total_upserted} vectors "
                f"to namespace '{self.namespace}'"
            )
            return total_upserted
            
        except Exception as e:
            logger.error(f"❌ Failed to upsert vectors: {e}")
            return 0
    
    def sync_document(
        self,
        doc_id: str,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]],
        is_update: bool = False
    ) -> bool:
        """
        Synchronize a document with Pinecone.
        
        If document is being updated, delete old vectors first.
        
        Args:
            doc_id: Document ID
            chunks: List of chunk dictionaries
            embeddings: List of embedding vectors
            is_update: If True, delete existing vectors first
            
        Returns:
            True if successful
        """
        try:
            # Delete old vectors if this is an update
            if is_update:
                logger.info(f"🔄 Updating document: {doc_id}")
                self.delete_document_vectors(doc_id)
            else:
                logger.info(f"➕ Adding new document: {doc_id}")
            
            # Upsert new vectors
            upserted = self.upsert_chunks(chunks, embeddings)
            
            if upserted > 0 or self.dry_run:
                logger.info(
                    f"✅ Synchronized document {doc_id}: "
                    f"{len(chunks)} chunks"
                )
                return True
            else:
                logger.error(f"❌ Failed to sync document {doc_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error syncing document {doc_id}: {e}")
            return False
    
    def query_similar(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Query similar vectors from Pinecone.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            filter_dict: Optional metadata filter
            
        Returns:
            List of matching results with metadata
        """
        if self.dry_run:
            logger.info(
                f"🔵 [DRY RUN] Would query {top_k} similar vectors"
            )
            return []
        
        try:
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                namespace=self.namespace,
                filter=filter_dict
            )
            
            return results.get("matches", [])
            
        except Exception as e:
            logger.error(f"❌ Query failed: {e}")
            return []
    
    def get_index_stats(self) -> Dict:
        """
        Get statistics about the Pinecone index.
        
        Returns:
            Dictionary with index statistics
        """
        if self.dry_run:
            return {
                "mode": "dry_run",
                "namespace": self.namespace,
                "index_name": self.index_name
            }
        
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vectors": stats.get("total_vector_count", 0),
                "namespace": self.namespace,
                "index_name": self.index_name,
                "dimension": stats.get("dimension", 0),
                "namespaces": stats.get("namespaces", {})
            }
        except Exception as e:
            logger.error(f"❌ Failed to get index stats: {e}")
            return {}
