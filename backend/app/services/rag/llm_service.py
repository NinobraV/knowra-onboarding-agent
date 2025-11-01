"""
LLM Service - Handles language model interactions.

Responsibilities:
- Initialize and manage OpenAI ChatGPT instance
- Build prompts from context and queries
- Generate responses (streaming and non-streaming)
- Manage conversation history
"""
from typing import List, Optional, AsyncGenerator

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


class LLMService:
    """
    Service for managing LLM interactions.
    
    Handles prompt generation, response generation (streaming and non-streaming),
    and conversation memory management.
    """
    
    def __init__(
        self,
        open_ai_base_url: str,
        openai_api_key: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        memory_window: int = 10,
        streaming: bool = True
    ):
        """
        Initialize the LLM service.
        
        Args:
            openai_api_key: OpenAI API key
            model: OpenAI model name
            temperature: Sampling temperature (0.0 to 1.0)
            memory_window: Number of messages to keep in memory
            streaming: Enable streaming responses
        """
        self.model = model
        self.temperature = temperature
        self.memory_window = memory_window
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            base_url=open_ai_base_url,
            model=self.model,
            temperature=self.temperature,
            streaming=streaming,
            openai_api_key=openai_api_key
        )
        
        # Initialize simple message history for memory
        self.chat_history: List = []
    
    def build_prompt(
        self,
        system_message: Optional[str] = None
    ) -> ChatPromptTemplate:
        """
        Build a chat prompt template with system message and memory.
        
        Args:
            system_message: Optional custom system message
            
        Returns:
            ChatPromptTemplate: Configured prompt template
        """
        default_system = """You are a helpful AI assistant with access to a comprehensive knowledge base.

Your role is to:
- Answer questions based on the knowledge base using the search tool
- Provide accurate, detailed, and well-structured responses
- Cite sources when possible
- Be conversational and helpful
- If you don't find relevant information, say so honestly

Always use the knowledge_base_search tool to find relevant information before answering."""
        
        system = system_message or default_system
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        return prompt
    
    def build_context_prompt(
        self,
        query: str,
        context_docs: List[Document]
    ) -> str:
        """
        Build a prompt with retrieved context for non-agent workflows.
        
        Args:
            query: User query
            context_docs: Retrieved documents for context
            
        Returns:
            str: Formatted prompt with context
        """
        context = "\n\n".join([
            f"Source: {doc.metadata.get('source', 'Unknown')}\n{doc.page_content}"
            for doc in context_docs
        ])
        
        prompt = f"""Based on the following context, answer the question.

Context:
{context}

Question: {query}

Answer:"""
        
        return prompt
    
    def generate_answer(
        self,
        query: str,
        context_docs: Optional[List[Document]] = None
    ) -> str:
        """
        Generate a non-streaming answer.
        
        Args:
            query: User query
            context_docs: Optional context documents
            
        Returns:
            str: Generated answer
        """
        if context_docs:
            prompt = self.build_context_prompt(query, context_docs)
        else:
            prompt = query
        
        response = self.llm.invoke(prompt)
        return response.content
    
    async def generate_answer_stream(
        self,
        query: str,
        context_docs: Optional[List[Document]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming answer.
        
        Args:
            query: User query
            context_docs: Optional context documents
            
        Yields:
            str: Response chunks
        """
        if context_docs:
            prompt = self.build_context_prompt(query, context_docs)
        else:
            prompt = query
        
        async for chunk in self.llm.astream(prompt):
            if chunk.content:
                yield chunk.content
    
    def get_llm_instance(self) -> ChatOpenAI:
        """
        Get the underlying LangChain LLM instance.
        
        Useful for integration with LangChain agents/chains.
        
        Returns:
            ChatOpenAI: LangChain LLM instance
        """
        return self.llm
    
    def get_memory_instance(self) -> List:
        """
        Get the conversation memory instance.
        
        Returns:
            List: Chat history messages
        """
        return self.chat_history
    
    def clear_memory(self) -> None:
        """Clear conversation memory."""
        self.chat_history.clear()
    
    def get_stats(self) -> dict:
        """
        Get LLM service statistics.
        
        Returns:
            dict: Service statistics
        """
        return {
            "model": self.model,
            "temperature": self.temperature,
            "memory_window": self.memory_window,
            "provider": "OpenAI"
        }
