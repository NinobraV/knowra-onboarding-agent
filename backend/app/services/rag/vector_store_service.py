"""
Vector Store Service - Manages vector database operations.

Responsibilities:
- Initialize and manage Pinecone vector store
- Handle document insertion and updates
- Provide retriever interface for semantic search
- Manage hash-based change detection
"""
import hashlib
from pathlib import Path
from typing import List, Optional, Dict, Any

from pinecone import Pinecone, ServerlessSpec
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings


class VectorStoreService:
    """
    Service for managing Pinecone vector store operations.
    
    Handles change detection via SHA-256 hashing and provides
    retriever interface for semantic search.
    """
    
    def __init__(
        self,
        embeddings: Embeddings,
        pinecone_api_key: str,
        pinecone_environment: str,
        pinecone_index_name: str,
        data_dir: Optional[Path] = None,
        persist_dir: Optional[Path] = None  # Kept for hash storage only
    ):
        """
        Initialize the vector store service with Pinecone.
        
        Args:
            embeddings: Embeddings instance for vectorization
            pinecone_api_key: Pinecone API key
            pinecone_environment: Pinecone environment/region
            pinecone_index_name: Name of the Pinecone index
            data_dir: Optional data directory for hash calculation
            persist_dir: Optional directory for hash storage (legacy)
        """
        self.embeddings = embeddings
        self.pinecone_api_key = pinecone_api_key
        self.pinecone_environment = pinecone_environment
        self.pinecone_index_name = pinecone_index_name
        self.data_dir = Path(data_dir) if data_dir else None
        self.persist_dir = Path(persist_dir) if persist_dir else Path("./backend/.vectorstore")
        self.index = None
        
        # Ensure persist directory exists (for hash storage)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Pinecone client
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        self._ensure_index_exists()
        self.index = self.pc.Index(self.pinecone_index_name)
    
    def _ensure_index_exists(self) -> None:
        """
        Ensure the Pinecone index exists, create if it doesn't.
        """
        existing_indexes = [index.name for index in self.pc.list_indexes()]
        
        if self.pinecone_index_name not in existing_indexes:
            print(f"📝 Creating Pinecone index: {self.pinecone_index_name}")
            self.pc.create_index(
                name=self.pinecone_index_name,
                dimension=1536,  # text-embedding-3-small dimension
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region=self.pinecone_environment
                )
            )
            print(f"✅ Pinecone index created: {self.pinecone_index_name}")
        else:
            print(f"✅ Pinecone index exists: {self.pinecone_index_name}")
    
    def _calculate_files_hash(self) -> str:
        """
        Calculate SHA-256 hash of all markdown files to detect changes.
        
        Returns:
            str: Hexadecimal hash digest
            
        Raises:
            ValueError: If data_dir is not set
        """
        if not self.data_dir:
            raise ValueError("data_dir must be set to calculate hash")
        
        hasher = hashlib.sha256()
        md_files = sorted(self.data_dir.glob("*.md"))
        
        for file_path in md_files:
            hasher.update(file_path.name.encode())
            hasher.update(file_path.read_bytes())
        
        return hasher.hexdigest()
    
    def _get_stored_hash(self) -> str:
        """
        Get the stored hash from previous vector store build.
        
        Returns:
            str: Stored hash or empty string if not found
        """
        hash_file = self.persist_dir / ".content_hash"
        if hash_file.exists():
            return hash_file.read_text().strip()
        return ""
    
    def _save_hash(self, content_hash: str) -> None:
        """
        Save the current hash to disk.
        
        Args:
            content_hash: Hash to save
        """
        hash_file = self.persist_dir / ".content_hash"
        hash_file.write_text(content_hash)
    
    def should_rebuild(self) -> bool:
        """
        Check if vector store needs to be rebuilt.
        
        Returns:
            bool: True if rebuild is needed
        """
        # Check if index is empty
        try:
            index = self.pc.Index(self.pinecone_index_name)
            stats = index.describe_index_stats()
            if stats.total_vector_count == 0:
                return True
        except Exception as e:
            print(f"⚠️  Could not check index stats: {e}")
            return True
        
        # Check if data directory is set for hash comparison
        if not self.data_dir:
            return False
        
        current_hash = self._calculate_files_hash()
        stored_hash = self._get_stored_hash()
        
        return current_hash != stored_hash
    
    def create_vectorstore(self, documents: List[Document]) -> None:
        """
        Create a new vector store from documents using Pinecone.
        
        Args:
            documents: List of document chunks to vectorize
        """
        print(f"🔄 Creating Pinecone vector store in index: {self.pinecone_index_name}")
        
        # Prepare vectors for upsert
        vectors_to_upsert = []
        for i, doc in enumerate(documents):
            # Generate embedding
            embedding = self.embeddings.embed_query(doc.page_content)
            
            # Prepare vector with metadata
            vector_id = f"doc_{i}"
            metadata = {
                "text": doc.page_content,
                **doc.metadata
            }
            
            vectors_to_upsert.append((vector_id, embedding, metadata))
        
        # Upsert in batches
        batch_size = 100
        for i in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[i:i + batch_size]
            self.index.upsert(vectors=batch)
        
        # Save hash if data_dir is set
        if self.data_dir:
            content_hash = self._calculate_files_hash()
            self._save_hash(content_hash)
        
        print(f"✅ Vector store created successfully ({len(documents)} documents)")
    
    def load_vectorstore(self) -> None:
        """Load existing vector store from Pinecone."""
        print(f"📂 Loading existing Pinecone vector store: {self.pinecone_index_name}")
        print("✅ Vector store loaded")
    
    def upsert_documents(self, documents: List[Document]) -> None:
        """
        Add or update documents in the vector store.
        
        Args:
            documents: List of documents to upsert
        """
        if not self.index:
            raise ValueError("Vector store not initialized.")
        
        vectors_to_upsert = []
        for i, doc in enumerate(documents):
            embedding = self.embeddings.embed_query(doc.page_content)
            vector_id = f"doc_upsert_{i}"
            metadata = {
                "text": doc.page_content,
                **doc.metadata
            }
            vectors_to_upsert.append((vector_id, embedding, metadata))
        
        # Upsert in batches
        batch_size = 100
        for i in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[i:i + batch_size]
            self.index.upsert(vectors=batch)
    
    def get_retriever(self, k: int = 5, search_type: str = "similarity"):
        """
        Get a retriever interface for semantic search.
        
        Args:
            k: Number of documents to retrieve
            search_type: Type of search ("similarity" or "mmr")
            
        Returns:
            dict: Retriever configuration
            
        Raises:
            ValueError: If vector store is not initialized
        """
        if not self.index:
            raise ValueError("Vector store not initialized.")
        
        return {
            "index": self.index,
            "embeddings": self.embeddings,
            "k": k,
            "search_type": search_type
        }
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """
        Perform similarity search directly.
        
        Args:
            query: Query text
            k: Number of results to return
            
        Returns:
            List[Document]: Most similar documents
            
        Raises:
            ValueError: If vector store is not initialized
        """
        if not self.index:
            raise ValueError("Vector store not initialized.")
        
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)
        
        # Query Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=k,
            include_metadata=True
        )
        
        # Convert results to Documents
        documents = []
        for match in results.matches:
            metadata = match.metadata.copy()
            text = metadata.pop("text", "")
            doc = Document(page_content=text, metadata=metadata)
            documents.append(doc)
        
        return documents
    
    def get_stats(self) -> dict:
        """
        Get vector store statistics.
        
        Returns:
            dict: Service statistics
        """
        # Get index stats from Pinecone
        vector_count = 0
        try:
            index = self.pc.Index(self.pinecone_index_name)
            stats = index.describe_index_stats()
            vector_count = stats.total_vector_count
        except Exception as e:
            print(f"⚠️  Could not retrieve index stats: {e}")
        
        return {
            "index_name": self.pinecone_index_name,
            "vector_store_type": "Pinecone",
            "environment": self.pinecone_environment,
            "vector_count": vector_count,
            "last_hash": self._get_stored_hash()[:8] if self.data_dir else "N/A"
        }
