"""
Chunking Service - Handles document loading and text segmentation.

Responsibilities:
- Load markdown documents from data directory
- Split documents into optimally-sized chunks with semantic awareness
- Preserve and enrich metadata during chunking
- Provide chunk quality metrics
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class ChunkingService:
    """
    Advanced service for loading and chunking documents with semantic awareness.
    
    Features:
    - Markdown-aware hierarchical splitting
    - Rich metadata preservation and extraction
    - Section header tracking for context
    - Chunk quality metrics
    - Smart separator ordering for optimal segmentation
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        add_section_headers: bool = True,
        extract_metadata: bool = True
    ):
        """
        Initialize the chunking service with advanced options.
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of overlapping characters between chunks
            add_section_headers: Whether to prepend section headers to chunks for context
            extract_metadata: Whether to extract rich metadata (tags, categories, etc.)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.add_section_headers = add_section_headers
        self.extract_metadata = extract_metadata
        
        # Enhanced markdown-aware separators with better hierarchy
        # Order matters: try larger semantic units first
        self.separators = [
            "\n\n---\n\n",  # Document sections
            "\n## ",         # H2 headers
            "\n### ",        # H3 headers
            "\n#### ",       # H4 headers
            "\n\n",          # Paragraphs
            "\n",            # Lines
            ". ",            # Sentences
            " ",             # Words
            ""               # Characters
        ]
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=self.separators,
            is_separator_regex=False
        )
        
        # Statistics tracking
        self.stats = {
            "total_documents": 0,
            "total_chunks": 0,
            "avg_chunk_size": 0,
            "files_processed": []
        }
    
    def _extract_frontmatter_metadata(self, content: str) -> Dict[str, Any]:
        """
        Extract YAML frontmatter metadata from markdown content.
        
        Args:
            content: Raw markdown content
            
        Returns:
            Dict[str, Any]: Extracted metadata or empty dict
        """
        metadata = {}
        
        # Match YAML frontmatter (between --- markers)
        frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(frontmatter_pattern, content, re.DOTALL)
        
        if match:
            frontmatter = match.group(1)
            # Parse simple key: value pairs
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Handle comma-separated tags
                    if key.lower() in ['tags', 'categories']:
                        metadata[key] = [tag.strip() for tag in value.split(',')]
                    else:
                        metadata[key] = value
        
        return metadata
    
    def _extract_section_hierarchy(self, content: str) -> List[str]:
        """
        Extract hierarchical section headers from content.
        
        Args:
            content: Text content
            
        Returns:
            List[str]: List of section headers in order
        """
        headers = []
        # Find all markdown headers (## to ####)
        header_pattern = r'^(#{1,4})\s+(.+)$'
        
        for line in content.split('\n'):
            match = re.match(header_pattern, line.strip())
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                headers.append(f"{'  ' * (level-1)}{title}")
        
        return headers
    
    def _find_current_section(self, text: str, full_content: str) -> Optional[str]:
        """
        Find the current section header for a given text chunk.
        
        Args:
            text: Chunk text
            full_content: Full document content
            
        Returns:
            Optional[str]: Section header or None
        """
        # Find position of chunk in full content
        try:
            chunk_pos = full_content.index(text)
        except ValueError:
            return None
        
        # Look backwards for the nearest header
        content_before = full_content[:chunk_pos]
        header_pattern = r'^(#{1,4})\s+(.+)$'
        
        headers = []
        for line in content_before.split('\n'):
            match = re.match(header_pattern, line.strip())
            if match:
                headers.append(match.group(2).strip())
        
        return headers[-1] if headers else None
    
    def load_documents(self, data_dir: Path) -> List[Document]:
        """
        Load all markdown files from the specified directory with rich metadata.
        
        Args:
            data_dir: Path to directory containing markdown files
            
        Returns:
            List[Document]: List of loaded documents with enhanced metadata
            
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
                
                # Base metadata
                metadata = {
                    "source": file_path.name,
                    "file_path": str(file_path),
                    "last_modified": datetime.fromtimestamp(
                        file_path.stat().st_mtime
                    ).isoformat(),
                    "file_size": file_path.stat().st_size
                }
                
                # Extract frontmatter metadata if enabled
                if self.extract_metadata:
                    frontmatter_meta = self._extract_frontmatter_metadata(content)
                    metadata.update(frontmatter_meta)
                    
                    # Extract section structure
                    sections = self._extract_section_hierarchy(content)
                    if sections:
                        metadata["sections"] = sections
                        metadata["section_count"] = len(sections)
                
                doc = Document(
                    page_content=content,
                    metadata=metadata
                )
                documents.append(doc)
                
                self.stats["files_processed"].append(file_path.name)
                
            except Exception as e:
                print(f"⚠️  Warning: Failed to load {file_path.name}: {e}")
                continue
        
        self.stats["total_documents"] = len(documents)
        return documents
    
    def _is_pure_separator(self, content: str) -> bool:
        """
        Check if chunk is just a separator with no meaningful content.
        
        Args:
            content: Chunk content
            
        Returns:
            bool: True if chunk is pure separator
        """
        stripped = content.strip()
        # Check for common separators
        if stripped in ['---', '___', '***', '===']:
            return True
        # Check for only whitespace/newlines and separators
        if re.match(r'^[\s\-_*=]+$', stripped):
            return True
        return False
    
    def _should_merge_chunks(self, chunk1: Document, chunk2: Document) -> bool:
        """
        Determine if two chunks should be merged.
        
        Args:
            chunk1: First chunk
            chunk2: Second chunk
            
        Returns:
            bool: True if chunks should be merged
        """
        min_size = self.chunk_size * 0.15  # Very small threshold (15%)
        
        # Merge if first chunk is very short and not a complete section
        if len(chunk1.page_content) < min_size:
            # Don't merge if chunk1 ends with complete section marker
            if not chunk1.page_content.strip().endswith(('\n\n', '---')):
                # Only merge if combined size is reasonable
                combined_size = len(chunk1.page_content) + len(chunk2.page_content)
                if combined_size <= self.chunk_size * 1.2:  # Allow 20% overflow
                    return True
        
        return False
    
    def _post_process_chunks(self, chunks: List[Document]) -> List[Document]:
        """
        Post-process chunks to improve quality.
        
        Improvements:
        1. Filter out pure separator chunks
        2. Merge very short chunks with neighbors
        3. Reindex chunks after changes
        
        Args:
            chunks: Initial chunks
            
        Returns:
            List[Document]: Processed chunks
        """
        if not chunks:
            return []
        
        # Step 1: Filter out pure separators
        filtered_chunks = []
        filtered_count = 0
        
        for chunk in chunks:
            if not self._is_pure_separator(chunk.page_content):
                filtered_chunks.append(chunk)
            else:
                filtered_count += 1
        
        if filtered_count > 0:
            print(f"   🧹 Filtered {filtered_count} pure separator chunks")
        
        # Step 2: Merge very short chunks
        merged_chunks = []
        merged_count = 0
        i = 0
        
        while i < len(filtered_chunks):
            current_chunk = filtered_chunks[i]
            
            # Check if we should merge with next chunk
            if i < len(filtered_chunks) - 1:
                next_chunk = filtered_chunks[i + 1]
                
                if self._should_merge_chunks(current_chunk, next_chunk):
                    # Merge chunks
                    merged_content = current_chunk.page_content + "\n\n" + next_chunk.page_content
                    merged_metadata = current_chunk.metadata.copy()
                    merged_metadata["chunk_size"] = len(merged_content)
                    merged_metadata["merged"] = True
                    
                    merged_chunk = Document(
                        page_content=merged_content,
                        metadata=merged_metadata
                    )
                    merged_chunks.append(merged_chunk)
                    merged_count += 1
                    i += 2  # Skip next chunk since we merged it
                    continue
            
            merged_chunks.append(current_chunk)
            i += 1
        
        if merged_count > 0:
            print(f"   🔗 Merged {merged_count} small chunks with neighbors")
        
        # Step 3: Reindex chunks
        for i, chunk in enumerate(merged_chunks):
            chunk.metadata["chunk_index"] = i
            chunk.metadata["total_chunks"] = len(merged_chunks)
        
        return merged_chunks
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks with enhanced context preservation.
        
        Args:
            documents: List of documents to split
            
        Returns:
            List[Document]: List of document chunks with enriched metadata
        """
        if not documents:
            return []
        
        all_chunks = []
        chunk_sizes = []
        
        for doc in documents:
            # Split the document
            chunks = self.text_splitter.split_documents([doc])
            
            # Enrich each chunk with additional context
            for i, chunk in enumerate(chunks):
                # Add chunk-specific metadata
                chunk.metadata["chunk_index"] = i
                chunk.metadata["total_chunks"] = len(chunks)
                chunk.metadata["chunk_size"] = len(chunk.page_content)
                
                # Track chunk size for statistics
                chunk_sizes.append(len(chunk.page_content))
                
                # Add section context if enabled
                if self.add_section_headers:
                    section = self._find_current_section(
                        chunk.page_content, 
                        doc.page_content
                    )
                    if section:
                        chunk.metadata["section"] = section
                        # Optionally prepend section header to chunk content for better context
                        # This helps the LLM understand the chunk's context better
                        if not chunk.page_content.strip().startswith('#'):
                            chunk.page_content = f"[Section: {section}]\n\n{chunk.page_content}"
                
                all_chunks.append(chunk)
        
        # Post-process chunks to improve quality
        all_chunks = self._post_process_chunks(all_chunks)
        
        # Update statistics after post-processing
        chunk_sizes = [len(c.page_content) for c in all_chunks]
        self.stats["total_chunks"] = len(all_chunks)
        if chunk_sizes:
            self.stats["avg_chunk_size"] = sum(chunk_sizes) / len(chunk_sizes)
            self.stats["min_chunk_size"] = min(chunk_sizes)
            self.stats["max_chunk_size"] = max(chunk_sizes)
        
        return all_chunks
    
    def _calculate_chunk_quality_score(self, chunk: Document) -> float:
        """
        Calculate a quality score for a chunk based on various metrics.
        
        Args:
            chunk: Document chunk to score
            
        Returns:
            float: Quality score between 0 and 1
        """
        score = 1.0
        content = chunk.page_content
        
        # Penalize very short chunks (less than 20% of target size)
        min_size = self.chunk_size * 0.2
        if len(content) < min_size:
            score *= 0.7
        
        # Penalize chunks that don't end with sentence boundaries
        if not content.strip().endswith(('.', '!', '?', '\n')):
            score *= 0.9
        
        # Bonus for chunks with headers (structural information)
        if re.search(r'^#{1,4}\s+', content, re.MULTILINE):
            score *= 1.1
        
        # Bonus for complete code blocks
        code_blocks = re.findall(r'```[\s\S]*?```', content)
        incomplete_code = re.findall(r'```(?![\s\S]*?```)', content)
        if code_blocks and not incomplete_code:
            score *= 1.05
        elif incomplete_code:
            score *= 0.8
        
        return min(1.0, score)
    
    def analyze_chunk_quality(self, chunks: List[Document]) -> Dict[str, Any]:
        """
        Analyze the quality of generated chunks.
        
        Args:
            chunks: List of document chunks
            
        Returns:
            Dict[str, Any]: Quality metrics
        """
        if not chunks:
            return {}
        
        quality_scores = [self._calculate_chunk_quality_score(chunk) for chunk in chunks]
        
        return {
            "total_chunks": len(chunks),
            "avg_quality_score": sum(quality_scores) / len(quality_scores),
            "min_quality_score": min(quality_scores),
            "max_quality_score": max(quality_scores),
            "high_quality_chunks": sum(1 for s in quality_scores if s >= 0.9),
            "low_quality_chunks": sum(1 for s in quality_scores if s < 0.7)
        }
    
    def process(self, data_dir: Path) -> List[Document]:
        """
        Complete pipeline: load documents, split into chunks, and analyze quality.
        
        Args:
            data_dir: Path to directory containing markdown files
            
        Returns:
            List[Document]: List of document chunks ready for embedding
        """
        print(f"📂 Loading documents from {data_dir}...")
        documents = self.load_documents(data_dir)
        print(f"📄 Loaded {len(documents)} documents")
        
        print("✂️  Splitting documents into chunks with semantic awareness...")
        chunks = self.split_documents(documents)
        print(f"✅ Created {len(chunks)} chunks")
        
        # Analyze chunk quality
        if chunks:
            quality_metrics = self.analyze_chunk_quality(chunks)
            print(f"📊 Chunk Quality Metrics:")
            print(f"   - Average Quality Score: {quality_metrics.get('avg_quality_score', 0):.2f}")
            print(f"   - High Quality Chunks: {quality_metrics.get('high_quality_chunks', 0)}")
            print(f"   - Low Quality Chunks: {quality_metrics.get('low_quality_chunks', 0)}")
            
            # Store quality metrics in stats
            self.stats["quality_metrics"] = quality_metrics
        
        return chunks
    
    def get_stats(self) -> dict:
        """
        Get comprehensive chunking service statistics.
        
        Returns:
            dict: Service configuration and processing statistics
        """
        return {
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "splitter_type": "RecursiveCharacterTextSplitter",
            "add_section_headers": self.add_section_headers,
            "extract_metadata": self.extract_metadata,
            "separator_count": len(self.separators),
            **self.stats
        }
