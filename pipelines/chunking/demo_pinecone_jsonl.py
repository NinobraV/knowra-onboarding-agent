"""
Demo: Split Documentation and Generate JSONL for Pinecone Embedding

This script demonstrates how to:
1. Load documents from the data/docs folder
2. Split them using HybridRecursiveSplitter
3. Generate JSONL output ready for Pinecone embedding and indexing

Output format is optimized for:
- Pinecone vector database ingestion
- OpenAI embedding generation
- Metadata preservation for filtering and retrieval
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from hybrid_recursive_splitter import HybridRecursiveSplitter


def load_document(file_path: str) -> Dict[str, Any]:
    """
    Load a markdown document and extract metadata.
    
    Args:
        file_path: Path to the markdown file
        
    Returns:
        Dictionary with content and metadata
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    file_name = os.path.basename(file_path)
    
    # Extract basic metadata from filename
    metadata = {
        "source": file_name,
        "file_path": file_path,
        "file_size": len(content),
        "doc_type": "markdown",
    }
    
    # Try to extract title from first heading
    lines = content.split('\n')
    for line in lines:
        if line.startswith('# '):
            metadata["title"] = line.replace('# ', '').strip()
            break
    
    return {
        "content": content,
        "metadata": metadata
    }


def chunk_to_pinecone_format(
    chunk_text: str,
    chunk_id: int,
    doc_metadata: Dict[str, Any],
    total_chunks: int
) -> Dict[str, Any]:
    """
    Convert a text chunk to Pinecone-ready JSONL format.
    
    Args:
        chunk_text: The chunked text content
        chunk_id: Sequential chunk identifier
        doc_metadata: Original document metadata
        total_chunks: Total number of chunks in document
        
    Returns:
        Dictionary ready for JSONL serialization
    """
    # Generate unique ID for this chunk
    source_name = doc_metadata.get("source", "unknown")
    unique_id = f"{source_name}_chunk_{chunk_id}"
    
    # Prepare metadata for Pinecone (will be stored alongside vectors)
    pinecone_metadata = {
        "text": chunk_text,  # Store the actual text
        "source": doc_metadata.get("source", ""),
        "title": doc_metadata.get("title", ""),
        "doc_type": doc_metadata.get("doc_type", ""),
        "chunk_id": chunk_id,
        "total_chunks": total_chunks,
        "char_count": len(chunk_text),
        "word_count": len(chunk_text.split()),
        "created_at": datetime.now().isoformat(),
    }
    
    return {
        "id": unique_id,
        "text": chunk_text,  # Text to be embedded
        "metadata": pinecone_metadata
    }


def process_docs_folder(
    docs_folder: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[Dict[str, Any]]:
    """
    Process all markdown files in the docs folder.
    
    Args:
        docs_folder: Path to documentation folder
        chunk_size: Maximum chunk size in characters
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of chunk records ready for JSONL output
    """
    # Initialize the splitter with markdown-aware mode
    splitter = HybridRecursiveSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        min_chunk_size=50,
        is_markdown=True  # Enable markdown-aware splitting
    )
    
    all_chunks = []
    docs_path = Path(docs_folder)
    
    # Get all markdown files
    md_files = sorted(docs_path.glob("*.md"))
    
    print(f"📁 Found {len(md_files)} markdown documents to process")
    print(f"⚙️  Chunk settings: size={chunk_size}, overlap={chunk_overlap}")
    print(f"📝 Markdown mode: ENABLED (header-aware splitting)")
    print("=" * 70)
    
    for md_file in md_files:
        print(f"\n📄 Processing: {md_file.name}")
        
        # Load document
        doc = load_document(str(md_file))
        content = doc["content"]
        metadata = doc["metadata"]
        
        # Split into chunks
        chunks = splitter.split_text(content)
        total_chunks = len(chunks)
        
        print(f"   ✂️  Split into {total_chunks} chunks")
        
        # Convert each chunk to Pinecone format
        for i, chunk_text in enumerate(chunks):
            chunk_record = chunk_to_pinecone_format(
                chunk_text=chunk_text,
                chunk_id=i,
                doc_metadata=metadata,
                total_chunks=total_chunks
            )
            all_chunks.append(chunk_record)
        
        # Show sample
        if chunks:
            sample = chunks[0][:100] + "..." if len(chunks[0]) > 100 else chunks[0]
            print(f"   📝 Sample chunk: {sample}")
    
    print("\n" + "=" * 70)
    print(f"✅ Total chunks generated: {len(all_chunks)}")
    
    return all_chunks


def save_jsonl(data: List[Dict[str, Any]], output_file: str):
    """
    Save data in JSONL format (one JSON object per line).
    
    Args:
        data: List of dictionaries to save
        output_file: Output file path
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for record in data:
            json_line = json.dumps(record, ensure_ascii=False)
            f.write(json_line + '\n')
    
    print(f"\n💾 Saved to: {output_file}")
    print(f"   File size: {os.path.getsize(output_file):,} bytes")


def display_statistics(chunks: List[Dict[str, Any]]):
    """Display statistics about the chunked data."""
    print("\n" + "=" * 70)
    print("📊 STATISTICS")
    print("=" * 70)
    
    total_chunks = len(chunks)
    total_chars = sum(c["metadata"]["char_count"] for c in chunks)
    total_words = sum(c["metadata"]["word_count"] for c in chunks)
    avg_chunk_size = total_chars / total_chunks if total_chunks > 0 else 0
    
    # Group by source
    by_source = {}
    for chunk in chunks:
        source = chunk["metadata"]["source"]
        if source not in by_source:
            by_source[source] = 0
        by_source[source] += 1
    
    print(f"Total Chunks:        {total_chunks}")
    print(f"Total Characters:    {total_chars:,}")
    print(f"Total Words:         {total_words:,}")
    print(f"Avg Chunk Size:      {avg_chunk_size:.0f} chars")
    print(f"\nChunks per Document:")
    for source, count in sorted(by_source.items()):
        print(f"  • {source:40s} {count:4d} chunks")


def display_sample_output(chunks: List[Dict[str, Any]], num_samples: int = 2):
    """Display sample JSONL records."""
    print("\n" + "=" * 70)
    print("📋 SAMPLE JSONL OUTPUT (First 2 chunks)")
    print("=" * 70)
    
    for i, chunk in enumerate(chunks[:num_samples]):
        print(f"\n--- Chunk {i+1} ---")
        print(json.dumps(chunk, indent=2, ensure_ascii=False))


def main():
    """Main execution function."""
    print("\n" + "=" * 70)
    print("🚀 HYBRID RECURSIVE SPLITTER - PINECONE JSONL DEMO")
    print("=" * 70)
    
    # Configuration
    DOCS_FOLDER = "../../data/docs"
    OUTPUT_FILE = "output_pinecone_chunks.jsonl"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Check if docs folder exists
    if not os.path.exists(DOCS_FOLDER):
        print(f"❌ Error: Documentation folder not found: {DOCS_FOLDER}")
        print("   Please run this script from pipelines/chunking/ directory")
        return
    
    # Process all documents
    chunks = process_docs_folder(
        docs_folder=DOCS_FOLDER,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    
    # Save to JSONL
    save_jsonl(chunks, OUTPUT_FILE)
    
    # Display statistics
    display_statistics(chunks)
    
    # Display sample output
    display_sample_output(chunks, num_samples=2)
    
    # Instructions for next steps
    print("\n" + "=" * 70)
    print("📝 NEXT STEPS FOR PINECONE EMBEDDING")
    print("=" * 70)
    print("""
1. Load the JSONL file:
   with open('output_pinecone_chunks.jsonl', 'r') as f:
       chunks = [json.loads(line) for line in f]

2. Generate embeddings using OpenAI:
   import openai
   embeddings = []
   for chunk in chunks:
       response = openai.Embedding.create(
           model="text-embedding-ada-002",
           input=chunk["text"]
       )
       embeddings.append(response['data'][0]['embedding'])

3. Upsert to Pinecone:
   import pinecone
   index = pinecone.Index("your-index-name")
   
   vectors = []
   for chunk, embedding in zip(chunks, embeddings):
       vectors.append({
           "id": chunk["id"],
           "values": embedding,
           "metadata": chunk["metadata"]
       })
   
   index.upsert(vectors=vectors)

4. Query example:
   query_embedding = openai.Embedding.create(
       model="text-embedding-ada-002",
       input="How do I set up the development environment?"
   )['data'][0]['embedding']
   
   results = index.query(
       vector=query_embedding,
       top_k=5,
       include_metadata=True
   )
   
   for match in results['matches']:
       print(f"Score: {match['score']:.4f}")
       print(f"Text: {match['metadata']['text'][:200]}...")
       print(f"Source: {match['metadata']['source']}")
       print()
""")
    
    print("=" * 70)
    print("✅ Demo completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
