"""
Chunking Service - Handles document loading and text segmentation.

Responsibilities:
- Load markdown documents from data directory
- Split documents into optimally-sized chunks
- Preserve metadata during chunking
"""
from pathlib import Path
from typing import List
from datetime import datetime

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class ChunkingService:
    """
    Service for loading and chunking documents.
    
    Uses RecursiveCharacterTextSplitter to create semantically meaningful chunks
    with proper overlap for context preservation.
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        Initialize the chunking service.
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of overlapping characters between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize text splitter with markdown-aware separators
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""]
        )
    
    def load_documents(self, data_dir: Path) -> List[Document]:
        """
        Load all markdown files from the specified directory.
        
        Args:
            data_dir: Path to directory containing markdown files
            
        Returns:
            List[Document]: List of loaded documents with metadata
            
        Raises:
            FileNotFoundError: If data directory doesn't exist
            ValueError: If no markdown files are found
        """
        if not data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {data_dir}")
        
        documents = []
        md_files = sorted(data_dir.glob("*.md"))
        
        if not md_files:
            raise ValueError(f"No markdown files found in {data_dir}")
        
        for file_path in md_files:
            try:
                content = file_path.read_text(encoding="utf-8")
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": file_path.name,
                        "file_path": str(file_path),
                        "last_modified": datetime.fromtimestamp(
                            file_path.stat().st_mtime
                        ).isoformat()
                    }
                )
                documents.append(doc)
            except Exception as e:
                print(f"⚠️  Warning: Failed to load {file_path.name}: {e}")
                continue
        
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks using the configured text splitter.
        
        Args:
            documents: List of documents to split
            
        Returns:
            List[Document]: List of document chunks with preserved metadata
        """
        if not documents:
            return []
        
        chunks = self.text_splitter.split_documents(documents)
        return chunks
    
    def process(self, data_dir: Path) -> List[Document]:
        """
        Complete pipeline: load documents and split into chunks.
        
        Args:
            data_dir: Path to directory containing markdown files
            
        Returns:
            List[Document]: List of document chunks ready for embedding
        """
        print(f"📂 Loading documents from {data_dir}...")
        documents = self.load_documents(data_dir)
        print(f"📄 Loaded {len(documents)} documents")
        
        print("✂️  Splitting documents into chunks...")
        chunks = self.split_documents(documents)
        print(f"✅ Created {len(chunks)} chunks")
        
        return chunks
    
    def get_stats(self) -> dict:
        """
        Get chunking service statistics.
        
        Returns:
            dict: Service configuration statistics
        """
        return {
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "splitter_type": "RecursiveCharacterTextSplitter"
        }
