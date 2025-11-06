"""
Ingestion Service - Orchestrates the document ingestion pipeline.

Responsibilities:
- Coordinate chunking, embedding, and vector store services
- Manage ingestion workflow
- Handle rebuild operations
- Provide status information
"""
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import VectorStoreService
from app.utils.logger import app_logger


class IngestionService:
    """
    Orchestrator for the document ingestion pipeline.
    
    Coordinates all sub-services to provide:
    - Document loading and chunking
    - Vector store management
    - Hash-based change detection
    """
    
    def __init__(
        self,
        data_dir: str,
        persist_dir: str,
        embedding_api_key: str,
        pinecone_api_key: str,
        pinecone_environment: str,
        pinecone_index_name: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        embedding_model: str = "text-embedding-3-small"
    ):
        """
        Initialize the ingestion service.
        
        Args:
            data_dir: Directory containing markdown knowledge base files
            persist_dir: Directory for hash storage
            embedding_api_key: API key for embedding service
            pinecone_api_key: Pinecone API key
            pinecone_environment: Pinecone environment/region
            pinecone_index_name: Pinecone index name
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            embedding_model: Embedding model to use
        """
        self.data_dir = Path(data_dir)
        self.persist_dir = Path(persist_dir)
        
        # Initialize sub-services
        self.chunking_service = ChunkingService(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        self.embedding_service = EmbeddingService(
            openai_api_key=embedding_api_key,
            model=embedding_model
        )
        
        self.vector_store_service = VectorStoreService(
            embeddings=self.embedding_service.get_embeddings_instance(),
            pinecone_api_key=pinecone_api_key,
            pinecone_environment=pinecone_environment,
            pinecone_index_name=pinecone_index_name,
            data_dir=self.data_dir,
            persist_dir=self.persist_dir
        )
        
        self._initialized = False
        self._last_ingestion = None
        
        # Initialize on startup if needed
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize the vector store if needed."""
        try:
            if self.vector_store_service.should_rebuild():
                app_logger.info("🔄 Initializing vector store...")
                self.ingest_documents(force=False)
            else:
                app_logger.info("✅ Vector store already up to date")
                self.vector_store_service.load_vectorstore()
            
            self._initialized = True
        except Exception as e:
            app_logger.error(f"❌ Failed to initialize: {e}")
            raise
    
    def ingest_documents(self, force: bool = False) -> Dict[str, Any]:
        """
        Ingest documents into the vector store.
        
        Args:
            force: Force rebuild even if no changes detected
            
        Returns:
            dict: Ingestion statistics and results
        """
        try:
            start_time = datetime.now()
            
            # Check if rebuild is needed
            if not force and not self.vector_store_service.should_rebuild():
                app_logger.info("✅ Vector store is up to date, no rebuild needed")
                return {
                    "rebuilt": False,
                    "message": "Vector store is already up to date",
                    "stats": self.get_stats()
                }
            
            app_logger.info("🚀 Starting document ingestion...")
            
            # Step 1: Load and chunk documents
            chunks = self.chunking_service.process(self.data_dir)
            
            if not chunks:
                raise ValueError("No documents were chunked")
            
            # Step 2: Create vector store with chunks
            self.vector_store_service.create_vectorstore(chunks)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self._last_ingestion = end_time.isoformat()
            
            result = {
                "rebuilt": True,
                "message": "Document ingestion completed successfully",
                "stats": {
                    "chunks_created": len(chunks),
                    "duration_seconds": round(duration, 2),
                    "timestamp": self._last_ingestion,
                    **self.get_stats()
                }
            }
            
            app_logger.info(f"✅ Ingestion completed in {duration:.2f}s")
            return result
            
        except Exception as e:
            app_logger.error(f"❌ Ingestion failed: {e}")
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current ingestion service status.
        
        Returns:
            dict: Service status information
        """
        stats = self.vector_store_service.get_stats()
        
        return {
            "initialized": self._initialized,
            "documents_count": stats.get("vector_count", 0),
            "last_updated": self._last_ingestion,
            "data_hash": stats.get("last_hash", "N/A"),
            "needs_rebuild": self.vector_store_service.should_rebuild()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get detailed service statistics.
        
        Returns:
            dict: Service statistics
        """
        return {
            "chunking": self.chunking_service.get_stats(),
            "embedding": self.embedding_service.get_stats(),
            "vector_store": self.vector_store_service.get_stats()
        }
