"""
RAG (Retrieval-Augmented Generation) service implementation.
Handles vector store management, document processing, and agent interactions.
"""
import os
import hashlib
from pathlib import Path
from typing import List, Dict, Any, AsyncGenerator
from datetime import datetime

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools.retriever import create_retriever_tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.documents import Document

from app.core.config import settings


class RAGService:
    """
    RAG Service with ChromaDB, OpenAI embeddings, and conversational memory.
    
    Provides:
    - Document loading and chunking
    - Vector store management with auto-rebuild
    - Conversational agent with memory
    - Streaming and non-streaming responses
    """
    
    def __init__(
        self,
        data_dir: str = None,
        persist_dir: str = None,
        openai_api_key: str = None
    ):
        """
        Initialize the RAG service.
        
        Args:
            data_dir: Directory containing markdown knowledge base files
            persist_dir: Directory for vector store persistence
            openai_api_key: OpenAI API key
        """
        self.data_dir = Path(data_dir or settings.DATA_DIR)
        self.persist_dir = Path(persist_dir or settings.VECTOR_STORE_DIR)
        self.openai_api_key = openai_api_key or settings.OPENAI_API_KEY
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
            openai_api_key=self.openai_api_key
        )
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            streaming=True,
            openai_api_key=self.openai_api_key
        )
        
        # Initialize memory
        self.memory = ConversationBufferWindowMemory(
            k=settings.MEMORY_WINDOW,
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )
        
        # Initialize vector store and agent
        self.vectorstore = None
        self.agent_executor = None
        self._initialize()
    
    def _calculate_files_hash(self) -> str:
        """
        Calculate SHA-256 hash of all markdown files to detect changes.
        
        Returns:
            str: Hexadecimal hash digest
        """
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
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        hash_file = self.persist_dir / ".content_hash"
        hash_file.write_text(content_hash)
    
    def _should_rebuild(self) -> bool:
        """
        Check if vector store needs to be rebuilt.
        
        Returns:
            bool: True if rebuild is needed
        """
        current_hash = self._calculate_files_hash()
        stored_hash = self._get_stored_hash()
        
        # Check if database exists
        if not (self.persist_dir / "chroma.sqlite3").exists():
            return True
        
        return current_hash != stored_hash
    
    def _load_documents(self) -> List[Document]:
        """
        Load all markdown files from the data directory.
        
        Returns:
            List[Document]: List of loaded documents with metadata
        """
        documents = []
        md_files = sorted(self.data_dir.glob("*.md"))
        
        for file_path in md_files:
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
        
        return documents
    
    def _build_vectorstore(self) -> None:
        """Build or rebuild the vector store from markdown files."""
        print("🔄 Building vector store...")
        
        # Load documents
        documents = self._load_documents()
        print(f"📄 Loaded {len(documents)} documents")
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""]
        )
        
        splits = text_splitter.split_documents(documents)
        print(f"✂️  Created {len(splits)} chunks")
        
        # Create vector store
        self.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=str(self.persist_dir)
        )
        
        # Save hash
        content_hash = self._calculate_files_hash()
        self._save_hash(content_hash)
        
        print("✅ Vector store built successfully")
    
    def _load_vectorstore(self) -> None:
        """Load existing vector store from disk."""
        print("📂 Loading existing vector store...")
        self.vectorstore = Chroma(
            persist_directory=str(self.persist_dir),
            embedding_function=self.embeddings
        )
        print("✅ Vector store loaded")
    
    def _create_agent(self) -> None:
        """Create the conversational agent with retriever tool."""
        # Create retriever
        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": settings.RETRIEVER_K}
        )
        
        # Create retriever tool
        retriever_tool = create_retriever_tool(
            retriever,
            name="knowledge_base_search",
            description=(
                "Search the knowledge base for information about onboarding, "
                "business overview, system architecture, API references, "
                "requirements, deployment, and security compliance. "
                "Use this tool to answer questions about the company's documentation."
            )
        )
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI assistant with access to a comprehensive knowledge base.
            
Your role is to:
- Answer questions based on the knowledge base using the search tool
- Provide accurate, detailed, and well-structured responses
- Cite sources when possible
- Be conversational and helpful
- If you don't find relevant information, say so honestly

Always use the knowledge_base_search tool to find relevant information before answering."""),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create agent
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=[retriever_tool],
            prompt=prompt
        )
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=[retriever_tool],
            memory=self.memory,
            verbose=True,
            return_intermediate_steps=False,
            handle_parsing_errors=True
        )
    
    def _initialize(self) -> None:
        """Initialize or rebuild vector store and agent."""
        if self._should_rebuild():
            print("🔨 Rebuilding vector store (files changed or missing)...")
            self._build_vectorstore()
        else:
            print("✨ Vector store is up to date")
            self._load_vectorstore()
        
        self._create_agent()
    
    def rebuild_if_needed(self) -> bool:
        """
        Check and rebuild vector store if files changed.
        
        Returns:
            bool: True if rebuild occurred
        """
        if self._should_rebuild():
            print("🔄 Files changed, rebuilding vector store...")
            self._build_vectorstore()
            self._create_agent()
            return True
        return False
    
    async def stream_response(self, query: str) -> AsyncGenerator[str, None]:
        """
        Stream response from agent.
        
        Args:
            query: User query
            
        Yields:
            str: Response chunks
        """
        async for chunk in self.agent_executor.astream({"input": query}):
            if "output" in chunk:
                yield chunk["output"]
    
    def chat(self, query: str) -> str:
        """
        Non-streaming chat response.
        
        Args:
            query: User query
            
        Returns:
            str: Complete response
        """
        response = self.agent_executor.invoke({"input": query})
        return response.get("output", "")
    
    def clear_memory(self) -> None:
        """Clear conversation memory."""
        self.memory.clear()
        print("🧹 Memory cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG system.
        
        Returns:
            Dict[str, Any]: System statistics
        """
        doc_count = len(list(self.data_dir.glob("*.md")))
        
        return {
            "documents_loaded": doc_count,
            "vector_store_path": str(self.persist_dir),
            "embedding_model": settings.OPENAI_EMBEDDING_MODEL,
            "llm_model": settings.OPENAI_MODEL,
            "memory_window": settings.MEMORY_WINDOW,
            "last_hash": self._get_stored_hash()[:8]
        }
