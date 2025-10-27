import re
from typing import Any, List, Optional

from langchain_text_splitters import TextSplitter, MarkdownHeaderTextSplitter
from langchain_core.documents import Document


class HybridRecursiveSplitter(TextSplitter):
    """
    LangChain-compatible text splitter with hybrid recursive and sentence window chunking.
    
    Combines recursive text segmentation with sliding sentence windowing to maintain
    context and semantic coherence across chunks. Optimized for markdown files with
    header-aware splitting.
    
    Example:
        >>> splitter = HybridRecursiveSplitter(chunk_size=1000, chunk_overlap=200)
        >>> chunks = splitter.split_text("Your text here...")
        >>> 
        >>> # For markdown files
        >>> splitter = HybridRecursiveSplitter(chunk_size=1000, chunk_overlap=200, 
        ...                                    is_markdown=True)
        >>> chunks = splitter.split_text(markdown_content)
        >>> 
        >>> # With LangChain Documents
        >>> docs = [Document(page_content="Text", metadata={"source": "file.txt"})]
        >>> split_docs = splitter.split_documents(docs)
    """
    
    # Standard separators for general text
    SEPARATORS = [
        "\n\n\n",
        "\n\n",
        "\n",
        ". ",
        "! ",
        "? ",
        "; ",
        ", ",
        " ",
    ]
    
    # Markdown-specific separators (prioritize markdown structure)
    MARKDOWN_SEPARATORS = [
        "\n## ",      # H2 headers
        "\n### ",     # H3 headers
        "\n#### ",    # H4 headers
        "\n\n\n",     # Multiple blank lines
        "\n\n",       # Paragraph breaks
        "\n",         # Line breaks
        ". ",         # Sentence boundaries
        "! ",
        "? ",
        "; ",
        ", ",
        " ",
    ]
    
    def __init__(
        self, 
        chunk_size: int = 1000, 
        chunk_overlap: int = 200,
        min_chunk_size: int = 50,
        separators: Optional[List[str]] = None,
        length_function: callable = len,
        is_markdown: bool = False,
        **kwargs: Any
    ):
        """
        Initialize the hybrid splitter.
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
            min_chunk_size: Minimum chunk size to avoid tiny fragments
            separators: Custom separator hierarchy (uses default if None)
            length_function: Function to measure text length (default: len)
            is_markdown: If True, use markdown-aware separators (default: False)
            **kwargs: Additional arguments passed to TextSplitter base class
            
        Raises:
            ValueError: If parameters are invalid
        """
        if chunk_size <= 0:
            raise ValueError(f"chunk_size must be positive, got {chunk_size}")
        if chunk_overlap < 0:
            raise ValueError(f"chunk_overlap cannot be negative, got {chunk_overlap}")
        if chunk_overlap >= chunk_size:
            raise ValueError(
                f"chunk_overlap ({chunk_overlap}) must be less than chunk_size ({chunk_size})"
            )
        if min_chunk_size < 0 or min_chunk_size >= chunk_size:
            raise ValueError(
                f"min_chunk_size ({min_chunk_size}) must be between 0 and chunk_size ({chunk_size})"
            )
        
        super().__init__(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=length_function,
            **kwargs
        )
        
        self.min_chunk_size = min_chunk_size
        self.is_markdown = is_markdown
        
        # Choose separators based on content type
        if separators:
            self.separators = separators
        elif is_markdown:
            self.separators = self.MARKDOWN_SEPARATORS
        else:
            self.separators = self.SEPARATORS

    def split_text(self, text: str) -> List[str]:
        """Split text into chunks using hybrid recursive + sentence window strategy."""
        text = self._normalize_text(text)
        if not text:
            return []
        
        if self._length_function(text) <= self._chunk_size:
            return [text]
        
        segments = self._recursive_split(text, self.separators)
        chunks = self._apply_sentence_window(segments)
        chunks = self._post_process_chunks(chunks)
        
        return chunks

    def _normalize_text(self, text: str) -> str:
        """Normalize text by removing excessive whitespace while preserving structure."""
        if not text or not isinstance(text, str):
            return ""
        
        text = text.strip()
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{4,}", "\n\n\n", text)
        
        return text

    def _recursive_split(
        self, 
        text: str, 
        separators: List[str],
        depth: int = 0
    ) -> List[str]:
        """Recursively split text by trying separators in hierarchical order."""
        if self._length_function(text) <= self._chunk_size:
            return [text] if text.strip() else []
        
        if depth > 10:
            return self._force_split(text)
        
        if not separators:
            return self._force_split(text)
        
        separator = separators[0]
        remaining_separators = separators[1:]
        
        parts = text.split(separator)
        
        if len(parts) == 1:
            return self._recursive_split(text, remaining_separators, depth + 1)
        
        chunks = []
        current_chunk = ""
        
        for i, part in enumerate(parts):
            piece = part + (separator if i < len(parts) - 1 else "")
            
            if current_chunk and self._length_function(current_chunk + piece) > self._chunk_size:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = piece
            else:
                current_chunk += piece
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        result = []
        for chunk in chunks:
            if self._length_function(chunk) > self._chunk_size:
                result.extend(
                    self._recursive_split(chunk, remaining_separators, depth + 1)
                )
            else:
                result.append(chunk)
        
        return result

    def _force_split(self, text: str) -> List[str]:
        """Force split text at chunk_size boundaries with overlap (fallback)."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self._chunk_size
            chunk = text[start:end].strip()
            
            if chunk:
                chunks.append(chunk)
            
            start = end - self._chunk_overlap if self._chunk_overlap > 0 else end
        
        return chunks

    def _apply_sentence_window(self, segments: List[str]) -> List[str]:
        """Merge segments with overlapping window to maintain context."""
        if not segments:
            return []
        
        chunks = []
        current_chunk = ""
        
        for segment in segments:
            segment = segment.strip()
            if not segment:
                continue
            
            space = " " if current_chunk else ""
            needed_length = self._length_function(current_chunk + space + segment)
            
            if needed_length <= self._chunk_size:
                current_chunk += space + segment
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                
                if self._chunk_overlap > 0 and current_chunk:
                    overlap = self._extract_overlap(current_chunk)
                    current_chunk = overlap + " " + segment
                else:
                    current_chunk = segment
                
                while self._length_function(current_chunk) > self._chunk_size:
                    split_point = self._chunk_size - self._chunk_overlap
                    chunks.append(current_chunk[:split_point].strip())
                    current_chunk = current_chunk[split_point:].strip()
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks

    def _extract_overlap(self, text: str) -> str:
        """Extract overlap text from end of chunk, preferring sentence boundaries."""
        if self._length_function(text) <= self._chunk_overlap:
            return text
        
        overlap_start = len(text) - self._chunk_overlap
        overlap_text = text[overlap_start:]
        
        sentence_ends = [". ", "! ", "? ", "\n"]
        best_pos = 0
        
        for sep in sentence_ends:
            pos = overlap_text.find(sep)
            if pos != -1 and pos > best_pos:
                best_pos = pos + len(sep)
        
        if best_pos > 0:
            return overlap_text[best_pos:].strip()
        
        return overlap_text.strip()

    def _post_process_chunks(self, chunks: List[str]) -> List[str]:
        """Clean up chunks by removing too-small fragments and normalizing."""
        result = []
        
        for chunk in chunks:
            chunk = chunk.strip()
            
            if not chunk:
                continue
            
            if self._length_function(chunk) < self.min_chunk_size and result:
                if self._length_function(result[-1] + " " + chunk) <= self._chunk_size:
                    result[-1] = result[-1] + " " + chunk
                    continue
            
            result.append(chunk)
        
        return result

    def get_chunk_metadata(self, chunks: List[str]) -> List[dict]:
        """Generate metadata for each chunk (useful for debugging/analytics)."""
        metadata = []
        
        for i, chunk in enumerate(chunks):
            metadata.append({
                "chunk_id": i,
                "length": len(chunk),
                "word_count": len(chunk.split()),
                "starts_with": chunk[:50] + "..." if len(chunk) > 50 else chunk,
                "ends_with": "..." + chunk[-50:] if len(chunk) > 50 else chunk,
            })
        
        return metadata
