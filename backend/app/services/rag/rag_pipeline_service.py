"""
RAG Pipeline Service - Orchestrates the complete RAG workflow.

Responsibilities:
- Coordinate all sub-services (chunking, embedding, vector store, search, ranking, LLM)
- Provide unified interface for RAG operations
- Manage initialization and rebuild workflows
- Handle agent-based conversational interactions
"""
from pathlib import Path
from typing import AsyncGenerator, Dict, Any, Optional

from langgraph.prebuilt import create_react_agent
from langchain_core.tools import Tool

from .chunking_service import ChunkingService
from .embedding_service import EmbeddingService
from .vector_store_service import VectorStoreService
from .semantic_search_service import SemanticSearchService
from .ranking_service import RankingService
from .llm_service import LLMService


class RAGPipelineService:
    """
    Orchestrator for the complete RAG (Retrieval-Augmented Generation) pipeline.
    
    Coordinates all sub-services to provide:
    - Document loading and chunking
    - Vector store management with auto-rebuild
    - Semantic search and ranking
    - Conversational agent with memory
    - Streaming and non-streaming responses
    """
    
    def __init__(
        self,
        data_dir: str,
        persist_dir: str,
        openai_base_url: str,
        openai_api_key: str,
        embedding_api_key: str,
        pinecone_api_key: str,
        pinecone_environment: str,
        pinecone_index_name: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        embedding_model: str = "text-embedding-3-small",
        pca_components: int = None,  # New parameter for PCA
        llm_model: str = "gpt-4o-mini",
        llm_temperature: float = 0.7,
        retriever_k: int = 5,
        memory_window: int = 10,
        auto_rebuild: bool = False,
        chunk_add_section_headers: bool = True,
        chunk_extract_metadata: bool = True
    ):
        """
        Initialize the RAG pipeline service with Pinecone.
        
        Args:
            data_dir: Directory containing markdown knowledge base files
            persist_dir: Directory for hash storage (legacy)
            openai_api_key: OpenAI API key for LLM
            embedding_api_key: API key for embedding service
            pinecone_api_key: Pinecone API key
            pinecone_environment: Pinecone environment/region
            pinecone_index_name: Pinecone index name
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            embedding_model: Embedding model to use (default: text-embedding-3-small)
            llm_model: OpenAI LLM model
            llm_temperature: LLM temperature
            retriever_k: Number of documents to retrieve
            memory_window: Conversation memory window size
            auto_rebuild: Enable automatic rebuild on startup and chat (default: False)
            chunk_add_section_headers: Add section context to chunks (default: True)
            chunk_extract_metadata: Extract rich metadata from documents (default: True)
        """
        self.data_dir = Path(data_dir)
        self.persist_dir = Path(persist_dir)
        self.openai_api_key = openai_api_key
        self.embedding_api_key = embedding_api_key
        self.retriever_k = retriever_k
        self.auto_rebuild = auto_rebuild
        
        # Initialize sub-services
        self.chunking_service = ChunkingService(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            add_section_headers=chunk_add_section_headers,
            extract_metadata=chunk_extract_metadata
        )
        
        self.embedding_service = EmbeddingService(
            openai_api_key=embedding_api_key,
            model=embedding_model,
            pca_components=pca_components  # Pass to EmbeddingService
        )
        
        self.vector_store_service = VectorStoreService(
            embeddings=self.embedding_service.get_embeddings_instance(),
            pinecone_api_key=pinecone_api_key,
            pinecone_environment=pinecone_environment,
            pinecone_index_name=pinecone_index_name,
            data_dir=self.data_dir,
            persist_dir=self.persist_dir
        )
        
        self.search_service = SemanticSearchService(
            vector_store_service=self.vector_store_service
        )
        
        self.ranking_service = RankingService(
            score_threshold=0.0
        )
        
        self.llm_service = LLMService(
            open_ai_base_url=openai_base_url,
            openai_api_key=openai_api_key,
            model=llm_model,
            temperature=llm_temperature,
            memory_window=memory_window,
            streaming=True
        )
        
        # Agent executor (initialized after vector store)
        self.agent_executor = None
        
        # Initialize the pipeline
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize or rebuild vector store and agent."""
        if self.auto_rebuild and self.vector_store_service.should_rebuild():
            print("🔨 Auto-rebuild ENABLED - Rebuilding vector store (files changed or missing)...")
            self._build_vectorstore()
        else:
            if not self.auto_rebuild:
                print("⚙️  Auto-rebuild DISABLED - Loading existing vector store from Pinecone...")
            else:
                print("✨ Vector store is up to date - Loading from Pinecone...")
            self.vector_store_service.load_vectorstore()
        
        self._create_agent()
    
    def _build_vectorstore(self) -> None:
        """Build or rebuild the vector store from markdown files."""
        print("🔄 Building vector store...")
        
        # Load and chunk documents
        chunks = self.chunking_service.process(self.data_dir)
        
        # Create vector store
        self.vector_store_service.create_vectorstore(chunks)
    
    def _create_agent(self) -> None:
        """Create the conversational agent with retriever tool using LangGraph."""
        # Get retriever from search service
        retriever = self.search_service.get_retriever(
            k=self.retriever_k,
            search_type="similarity"
        )
        
        # Create retriever tool with improved function
        def retrieve_context(query: str) -> str:
            """Retrieve relevant context from the knowledge base."""
            try:
                docs = self.search_service.semantic_search(query, k=self.retriever_k)
                if not docs:
                    return "No relevant information found in the knowledge base."
                return "\n\n".join([doc.page_content for doc in docs])
            except Exception as e:
                return f"Error retrieving information: {str(e)}"
        
        retriever_tool = Tool(
            name="knowledge_base_search",
            description=(
                "Search the knowledge base for information about onboarding, "
                "business overview, system architecture, API references, "
                "requirements, deployment, and security compliance. "
                "Use this tool to answer questions about the company's documentation. "
                "Input should be a search query string."
            ),
            func=retrieve_context
        )
        
        # Get LLM instance
        llm = self.llm_service.get_llm_instance()
        
        # Create react agent with LangGraph
        self.agent_executor = create_react_agent(
            llm,
            tools=[retriever_tool]
        )
    
    def rebuild_if_needed(self) -> bool:
        """
        Check and rebuild vector store if files changed (only if auto_rebuild is enabled).
        
        Returns:
            bool: True if rebuild occurred
        """
        if not self.auto_rebuild:
            print("⚙️  Auto-rebuild DISABLED - Skipping rebuild check")
            return False
            
        if self.vector_store_service.should_rebuild():
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
        if not self.agent_executor:
            raise ValueError("Agent executor not initialized")
        
        # Configure recursion limit to prevent infinite loops
        config = {"recursion_limit": 50}
        
        async for chunk in self.agent_executor.astream(
            {"messages": [("user", query)]},
            config=config
        ):
            if "agent" in chunk:
                if "messages" in chunk["agent"]:
                    for message in chunk["agent"]["messages"]:
                        if hasattr(message, "content") and message.content.strip():
                            yield message.content
    
    def chat(self, query: str) -> str:
        """
        Non-streaming chat response.
        
        Args:
            query: User query
            
        Returns:
            str: Complete response
        """
        if not self.agent_executor:
            raise ValueError("Agent executor not initialized")
        
        # Configure recursion limit to prevent infinite loops
        config = {"recursion_limit": 50}
        
        response = self.agent_executor.invoke(
            {"messages": [("user", query)]},
            config=config
        )
        # Extract the last message from agent
        if "messages" in response:
            for message in reversed(response["messages"]):
                if hasattr(message, "content") and message.content:
                    return message.content
        return ""
    
    def clear_memory(self) -> None:
        """Clear conversation memory."""
        self.llm_service.clear_memory()
        print("🧹 Memory cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the RAG system.
        
        Returns:
            Dict[str, Any]: System statistics from all services
        """
        doc_count = len(list(self.data_dir.glob("*.md")))
        
        return {
            "documents_loaded": doc_count,
            "chunking": self.chunking_service.get_stats(),
            "embedding": self.embedding_service.get_stats(),
            "vector_store": self.vector_store_service.get_stats(),
            "search": self.search_service.get_stats(),
            "ranking": self.ranking_service.get_stats(),
            "llm": self.llm_service.get_stats()
        }
