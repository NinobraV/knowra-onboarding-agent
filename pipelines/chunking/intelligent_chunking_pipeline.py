"""
Intelligent Chunking Pipeline with Change Detection

This pipeline implements:
1. Document change detection via content hashing
2. Efficient re-chunking (only changed documents)
3. Sentence window overlap
4. JSONL export for embedding pipelines
5. Pinecone synchronization with namespace organization
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from hybrid_recursive_splitter import HybridRecursiveSplitter
from document_tracker import DocumentTracker
from pinecone_synchronizer import PineconeSynchronizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntelligentChunkingPipeline:
    """
    Smart document processing pipeline with change detection.
    
    Only re-processes documents that have changed since last run.
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_chunk_size: int = 50,
        index_file: str = "metadata_index.json",
        output_dir: str = "../../data/processed",
        namespace: str = "knowledge_base",
        is_markdown: bool = True,
        dry_run: bool = False
    ):
        """
        Initialize the intelligent chunking pipeline.
        
        Args:
            chunk_size: Maximum chunk size in characters
            chunk_overlap: Overlap between chunks (sentence window)
            min_chunk_size: Minimum chunk size
            index_file: Path to metadata index file
            output_dir: Directory for JSONL output files (default: ../../data/processed)
            namespace: Pinecone namespace
            is_markdown: Enable markdown-aware splitting
            dry_run: Simulate without actual Pinecone operations
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.namespace = namespace
        self.output_dir = output_dir
        self.dry_run = dry_run
        
        # Initialize components
        self.splitter = HybridRecursiveSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            min_chunk_size=min_chunk_size,
            is_markdown=is_markdown
        )
        
        self.tracker = DocumentTracker(index_file=index_file)
        
        self.synchronizer = PineconeSynchronizer(
            namespace=namespace,
            dry_run=dry_run
        )
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Statistics
        self.stats = {
            "processed": 0,
            "skipped": 0,
            "updated": 0,
            "new": 0,
            "total_chunks": 0,
            "errors": 0
        }
    
    def load_document(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Load document from file.
        
        Args:
            file_path: Path to document file
            
        Returns:
            Dictionary with content and metadata
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_name = os.path.basename(file_path)
            
            # Extract title from first heading (markdown)
            title = None
            for line in content.split('\n'):
                if line.startswith('# '):
                    title = line.replace('# ', '').strip()
                    break
            
            return {
                "content": content,
                "source": file_path,
                "file_name": file_name,
                "title": title,
                "file_size": len(content)
            }
        except Exception as e:
            logger.error(f"❌ Failed to load {file_path}: {e}")
            return None
    
    def chunk_document(
        self,
        doc_id: str,
        content: str,
        source: str,
        page: Optional[int] = None,
        additional_metadata: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Chunk document and prepare for embedding.
        
        Args:
            doc_id: Document ID
            content: Document content
            source: Document source path
            page: Optional page number
            additional_metadata: Additional metadata to include
            
        Returns:
            List of chunk dictionaries ready for JSONL export
        """
        # Split text into chunks
        chunks_text = self.splitter.split_text(content)
        
        # Prepare chunk records
        chunks = []
        timestamp = datetime.now().isoformat()
        
        for i, chunk_text in enumerate(chunks_text):
            chunk_id = f"{doc_id}_chunk_{i:04d}"
            
            # Prepare metadata
            metadata = {
                "doc_id": doc_id,
                "source": source,
                "page": page,
                "timestamp": timestamp,
                "chunk_index": i,
                "total_chunks": len(chunks_text),
                "char_count": len(chunk_text),
                "word_count": len(chunk_text.split()),
            }
            
            # Add additional metadata
            if additional_metadata:
                metadata.update(additional_metadata)
            
            # Create chunk record
            chunk_record = {
                "chunk_id": chunk_id,
                "doc_id": doc_id,
                "content": chunk_text,
                "metadata": metadata
            }
            
            chunks.append(chunk_record)
        
        return chunks
    
    def save_chunks_jsonl(
        self, 
        chunks: List[Dict[str, Any]], 
        output_file: str
    ):
        """
        Save chunks to JSONL file (one chunk per line).
        
        Args:
            chunks: List of chunk dictionaries
            output_file: Output file path
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for chunk in chunks:
                    json_line = json.dumps(chunk, ensure_ascii=False)
                    f.write(json_line + '\n')
            
            logger.info(f"💾 Saved {len(chunks)} chunks to {output_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save chunks: {e}")
    
    def process_document(
        self,
        file_path: str,
        page: Optional[int] = None,
        sync_to_pinecone: bool = False,
        embeddings: Optional[List[List[float]]] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Process a single document with change detection.
        
        Args:
            file_path: Path to document file
            page: Optional page number
            sync_to_pinecone: Whether to sync with Pinecone
            embeddings: Pre-computed embeddings (if syncing to Pinecone)
            
        Returns:
            List of chunks if processed, None if skipped
        """
        # Load document
        doc = self.load_document(file_path)
        if not doc:
            self.stats["errors"] += 1
            return None
        
        content = doc["content"]
        source = doc["source"]
        
        # Check if document changed
        doc_id, needs_processing, old_metadata = self.tracker.check_document(
            source=source,
            content=content,
            page=page
        )
        
        # Determine action
        if not needs_processing:
            logger.info(f"⏭️  SKIPPED (unchanged): {doc['file_name']}")
            self.stats["skipped"] += 1
            return None
        
        is_new = old_metadata is None
        is_update = not is_new
        
        if is_new:
            logger.info(f"➕ NEW document: {doc['file_name']}")
            self.stats["new"] += 1
        else:
            logger.info(f"🔄 UPDATED document: {doc['file_name']}")
            self.stats["updated"] += 1
        
        # Chunk the document
        chunks = self.chunk_document(
            doc_id=doc_id,
            content=content,
            source=source,
            page=page,
            additional_metadata={
                "title": doc.get("title"),
                "file_name": doc["file_name"]
            }
        )
        
        logger.info(f"   ✂️  Split into {len(chunks)} chunks")
        
        # Save chunks to JSONL
        output_file = os.path.join(
            self.output_dir,
            f"{doc_id}_chunks.jsonl"
        )
        self.save_chunks_jsonl(chunks, output_file)
        
        # Update tracker
        self.tracker.update_document(
            doc_id=doc_id,
            source=source,
            content=content,
            page=page,
            chunk_count=len(chunks),
            additional_metadata={
                "title": doc.get("title"),
                "file_name": doc["file_name"]
            }
        )
        
        # Sync to Pinecone if requested
        if sync_to_pinecone:
            if embeddings and len(embeddings) == len(chunks):
                success = self.synchronizer.sync_document(
                    doc_id=doc_id,
                    chunks=chunks,
                    embeddings=embeddings,
                    is_update=is_update
                )
                if success:
                    logger.info(f"   ✅ Synced to Pinecone: {doc_id}")
                else:
                    logger.error(f"   ❌ Failed to sync: {doc_id}")
            else:
                logger.warning(
                    f"   ⚠️  Cannot sync to Pinecone: "
                    f"Embeddings not provided or count mismatch"
                )
        
        self.stats["processed"] += 1
        self.stats["total_chunks"] += len(chunks)
        
        return chunks
    
    def process_directory(
        self,
        docs_dir: str,
        pattern: str = "*.md",
        sync_to_pinecone: bool = False
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Process all documents in a directory.
        
        Args:
            docs_dir: Directory containing documents
            pattern: File pattern to match (e.g., '*.md', '*.txt')
            sync_to_pinecone: Whether to sync with Pinecone
            
        Returns:
            Dictionary mapping file paths to chunks
        """
        docs_path = Path(docs_dir)
        files = sorted(docs_path.glob(pattern))
        
        logger.info("=" * 70)
        logger.info("🚀 INTELLIGENT CHUNKING PIPELINE")
        logger.info("=" * 70)
        logger.info(f"📁 Processing directory: {docs_dir}")
        logger.info(f"🔍 Pattern: {pattern}")
        logger.info(f"📄 Found {len(files)} files")
        logger.info(f"⚙️  Chunk size: {self.chunk_size}, Overlap: {self.chunk_overlap}")
        logger.info(f"🎯 Pinecone namespace: {self.namespace}")
        if self.dry_run:
            logger.info("🔵 DRY RUN MODE: Pinecone operations will be simulated")
        logger.info("=" * 70)
        
        results = {}
        
        for file_path in files:
            chunks = self.process_document(
                file_path=str(file_path),
                sync_to_pinecone=sync_to_pinecone
            )
            if chunks:
                results[str(file_path)] = chunks
        
        return results
    
    def print_statistics(self):
        """Print processing statistics."""
        logger.info("\n" + "=" * 70)
        logger.info("📊 PROCESSING STATISTICS")
        logger.info("=" * 70)
        logger.info(f"✅ Processed:     {self.stats['processed']} documents")
        logger.info(f"   ➕ New:        {self.stats['new']}")
        logger.info(f"   🔄 Updated:    {self.stats['updated']}")
        logger.info(f"⏭️  Skipped:      {self.stats['skipped']} (unchanged)")
        logger.info(f"❌ Errors:        {self.stats['errors']}")
        logger.info(f"📝 Total chunks:  {self.stats['total_chunks']}")
        
        # Tracker statistics
        tracker_stats = self.tracker.get_statistics()
        logger.info(f"\n📚 Document Index:")
        logger.info(f"   Total tracked: {tracker_stats['total_documents']}")
        logger.info(f"   Total chunks:  {tracker_stats['total_chunks']}")
        logger.info(f"   Index file:    {tracker_stats['index_file']}")
        
        # Pinecone statistics
        if not self.dry_run:
            pinecone_stats = self.synchronizer.get_index_stats()
            logger.info(f"\n🌲 Pinecone Index:")
            logger.info(f"   Index name:    {pinecone_stats.get('index_name')}")
            logger.info(f"   Namespace:     {pinecone_stats.get('namespace')}")
            logger.info(f"   Total vectors: {pinecone_stats.get('total_vectors', 0)}")
        
        logger.info("=" * 70)
    
    def get_embeddings_placeholder(
        self, 
        chunks: List[Dict[str, Any]]
    ) -> List[List[float]]:
        """
        Placeholder for embedding generation.
        
        In production, this would call OpenAI or another embedding service.
        
        Args:
            chunks: List of chunks to embed
            
        Returns:
            List of embedding vectors (placeholder zeros)
        """
        # Placeholder: return zero vectors
        # In production, use:
        # import openai
        # embeddings = []
        # for chunk in chunks:
        #     response = openai.Embedding.create(
        #         model="text-embedding-ada-002",
        #         input=chunk["content"]
        #     )
        #     embeddings.append(response['data'][0]['embedding'])
        
        logger.warning(
            "⚠️  Using placeholder embeddings. "
            "Integrate with OpenAI or another embedding service."
        )
        
        dimension = 1536  # OpenAI ada-002 dimension
        return [[0.0] * dimension for _ in chunks]


def main():
    """Example usage of the intelligent chunking pipeline."""
    
    # Initialize pipeline
    pipeline = IntelligentChunkingPipeline(
        chunk_size=1000,
        chunk_overlap=200,
        min_chunk_size=50,
        index_file="../../data/metadata/metadata_index.json",
        output_dir="../../data/processed",
        namespace="knowledge_base",
        is_markdown=True,
        dry_run=True  # Set to False when Pinecone is configured
    )
    
    # Process all markdown files in docs directory
    results = pipeline.process_directory(
        docs_dir="../../data/docs",
        pattern="*.md",
        sync_to_pinecone=False  # Set to True to sync with Pinecone
    )
    
    # Print statistics
    pipeline.print_statistics()
    
    # Show sample output
    if results:
        first_file = list(results.keys())[0]
        first_chunks = results[first_file]
        
        logger.info("\n" + "=" * 70)
        logger.info("📋 SAMPLE OUTPUT (First chunk)")
        logger.info("=" * 70)
        print(json.dumps(first_chunks[0], indent=2, ensure_ascii=False))
        logger.info("=" * 70)


if __name__ == "__main__":
    main()
