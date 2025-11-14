"""
Pydantic models and schemas for request/response validation.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


# ============================================================================
# Chat Message Schemas (for MongoDB persistence)
# ============================================================================

class MessageSource(BaseModel):
    """Source document reference for a message."""
    
    id: str = Field(..., description="Document ID in vector store")
    score: float = Field(..., description="Relevance score")
    text: str = Field(..., description="Excerpt or full text")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "doc_123",
                "score": 0.89,
                "text": "The onboarding process includes...",
                "metadata": {"source": "01_ONBOARDING_GUIDE.md", "section": "Overview"}
            }
        }


class ChatMessageCreate(BaseModel):
    """Schema for creating a new chat message."""
    
    session_id: str = Field(..., description="Session this message belongs to")
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    sources: Optional[List[MessageSource]] = Field(None, description="Retrieved sources for this message")
    routing_info: Optional[Dict[str, Any]] = Field(None, description="RAG routing decision metadata")
    safety_info: Optional[Dict[str, Any]] = Field(None, description="Safety analysis metadata")
    tokens: Optional[int] = Field(None, description="Token count for this message")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session-abc-123",
                "role": "assistant",
                "content": "The onboarding process consists of...",
                "sources": [
                    {
                        "id": "doc_123",
                        "score": 0.89,
                        "text": "The onboarding process includes...",
                        "metadata": {"source": "01_ONBOARDING_GUIDE.md"}
                    }
                ],
                "routing_info": {"decision": "kb_and_memory", "confidence": 0.85},
                "safety_info": {"level": "safe"},
                "tokens": 150
            }
        }


class ChatMessage(BaseModel):
    """Schema for a chat message stored in MongoDB."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id", description="Message ID")
    session_id: str = Field(..., description="Session this message belongs to")
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    sources: Optional[List[MessageSource]] = Field(None, description="Retrieved sources")
    routing_info: Optional[Dict[str, Any]] = Field(None, description="RAG routing metadata")
    safety_info: Optional[Dict[str, Any]] = Field(None, description="Safety analysis metadata")
    tokens: Optional[int] = Field(None, description="Token count")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "msg-abc-123",
                "session_id": "session-abc-123",
                "role": "assistant",
                "content": "The onboarding process consists of...",
                "sources": [],
                "routing_info": {"decision": "kb_and_memory"},
                "safety_info": {"level": "safe"},
                "tokens": 150,
                "created_at": "2025-11-14T12:00:00Z"
            }
        }


class ChatMessageResponse(BaseModel):
    """Response model for chat messages."""
    
    id: str = Field(..., description="Message ID")
    session_id: str = Field(..., description="Session ID")
    role: str = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    sources: Optional[List[MessageSource]] = Field(None, description="Sources")
    routing_info: Optional[Dict[str, Any]] = Field(None, description="Routing info")
    safety_info: Optional[Dict[str, Any]] = Field(None, description="Safety info")
    tokens: Optional[int] = Field(None, description="Tokens")
    created_at: datetime = Field(..., description="Timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "msg-abc-123",
                "session_id": "session-abc-123",
                "role": "assistant",
                "content": "The onboarding process...",
                "sources": [],
                "created_at": "2025-11-14T12:00:00Z"
            }
        }


class MessageListResponse(BaseModel):
    """Response model for paginated message list."""
    
    messages: List[ChatMessageResponse] = Field(..., description="List of messages")
    total_count: int = Field(..., description="Total number of messages in session")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of messages per page")
    has_more: bool = Field(..., description="Whether there are more messages")
    
    class Config:
        json_schema_extra = {
            "example": {
                "messages": [],
                "total_count": 25,
                "page": 1,
                "page_size": 20,
                "has_more": True
            }
        }


# ============================================================================
# Chat Session Schemas (for MongoDB persistence)
# ============================================================================

class ChatSessionCreate(BaseModel):
    """Schema for creating a new chat session."""
    
    user_id: Optional[str] = Field(None, description="User identifier")
    project_id: Optional[str] = Field("default", description="Project identifier")
    title: Optional[str] = Field(None, description="Auto-generated session title")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user-123",
                "project_id": "project-onboarding",
                "title": "Questions about onboarding",
                "metadata": {}
            }
        }


class ChatSession(BaseModel):
    """Schema for a chat session stored in MongoDB."""
    
    id: str = Field(default_factory=lambda: f"session-{uuid.uuid4()}", alias="_id", description="Session ID")
    user_id: Optional[str] = Field(None, description="User identifier")
    project_id: str = Field(default="default", description="Project identifier")
    title: str = Field(default="New Conversation", description="Session title")
    message_count: int = Field(default=0, description="Number of messages in session")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "session-abc-123",
                "user_id": "user-123",
                "project_id": "project-onboarding",
                "title": "Onboarding Questions",
                "message_count": 10,
                "created_at": "2025-11-14T12:00:00Z",
                "updated_at": "2025-11-14T13:30:00Z"
            }
        }


class ChatSessionResponse(BaseModel):
    """Response model for chat sessions."""
    
    session_id: str = Field(..., description="Session ID")
    user_id: Optional[str] = Field(None, description="User ID")
    project_id: str = Field(..., description="Project ID")
    title: str = Field(..., description="Session title")
    message_count: int = Field(..., description="Message count")
    created_at: datetime = Field(..., description="Created timestamp")
    updated_at: datetime = Field(..., description="Updated timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "session-abc-123",
                "user_id": "user-123",
                "project_id": "project-onboarding",
                "title": "Onboarding Questions",
                "message_count": 10,
                "created_at": "2025-11-14T12:00:00Z",
                "updated_at": "2025-11-14T13:30:00Z"
            }
        }


class ChatSessionListResponse(BaseModel):
    """Response model for paginated session list."""
    
    sessions: List[ChatSessionResponse] = Field(..., description="List of sessions")
    total_count: int = Field(..., description="Total number of sessions")
    page: int = Field(default=1, description="Current page")
    page_size: int = Field(default=50, description="Page size")
    has_more: bool = Field(default=False, description="More sessions available")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sessions": [],
                "total_count": 5,
                "page": 1,
                "page_size": 50,
                "has_more": False
            }
        }


# ============================================================================
# Existing Schemas (preserved for backward compatibility)
# ============================================================================

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    
    message: str = Field(..., description="User message to send to the chatbot")
    stream: bool = Field(True, description="Whether to stream the response via SSE")
    session_id: Optional[str] = Field(None, description="Session identifier for conversation continuity")
    project_id: Optional[str] = Field(None, description="Project identifier for scoped conversations")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "message": "What is the onboarding process?",
                "stream": True,
                "session_id": "user-123-session-456",
                "project_id": "project-onboarding"
            }
        }


class ChatResponse(BaseModel):
    """Response model for non-streaming chat."""
    
    response: str = Field(..., description="Chatbot response")
    sources: Optional[List[str]] = Field(None, description="Source documents used")
    session_id: Optional[str] = Field(None, description="Session identifier")
    project_id: Optional[str] = Field(None, description="Project identifier")
    routing_info: Optional[Dict[str, Any]] = Field(None, description="Routing decision information")
    safety_info: Optional[Dict[str, Any]] = Field(None, description="Safety analysis information")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "response": "The onboarding process consists of...",
                "sources": ["01_ONBOARDING_GUIDE.md"],
                "session_id": "user-123-session-456",
                "project_id": "project-onboarding",
                "routing_info": {
                    "decision": "kb_and_memory",
                    "confidence": 0.85
                },
                "safety_info": {
                    "level": "safe"
                }
            }
        }


class ClearResponse(BaseModel):
    """Response model for clear and rebuild endpoints."""
    
    message: str = Field(..., description="Status message")
    session_id: Optional[str] = Field(None, description="Session that was affected")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "message": "Conversation history cleared successfully",
                "session_id": "user-123-session-456"
            }
        }


class SessionRequest(BaseModel):
    """Request model for session management."""
    
    user_id: Optional[str] = Field(None, description="User identifier")
    project_id: Optional[str] = Field(None, description="Project identifier")
    session_name: Optional[str] = Field(None, description="Human-readable session name")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "user_id": "user-123",
                "project_id": "project-onboarding",
                "session_name": "Onboarding Questions"
            }
        }


class SessionResponse(BaseModel):
    """Response model for session creation/management."""
    
    session_id: str = Field(..., description="Created session identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    project_id: Optional[str] = Field(None, description="Project identifier")
    session_name: Optional[str] = Field(None, description="Session name")
    created_at: str = Field(..., description="Session creation timestamp")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "session_id": "session-789-abc-def",
                "user_id": "user-123",
                "project_id": "project-onboarding",
                "session_name": "Onboarding Questions",
                "created_at": "2025-11-10T12:00:00Z"
            }
        }


class SessionListResponse(BaseModel):
    """Response model for session listing."""
    
    sessions: List[SessionResponse] = Field(..., description="List of sessions")
    total_count: int = Field(..., description="Total number of sessions")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "sessions": [
                    {
                        "session_id": "session-789-abc-def",
                        "user_id": "user-123",
                        "project_id": "project-onboarding",
                        "session_name": "Onboarding Questions",
                        "created_at": "2025-11-10T12:00:00Z"
                    }
                ],
                "total_count": 1
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    
    status: str = Field(..., description="Health status")
    stats: Dict[str, Any] = Field(..., description="System statistics")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "stats": {
                    "documents_loaded": 9,
                    "vector_store_type": "Pinecone",
                    "embedding_model": "llama-text-embed-v2",
                    "llm_model": "gpt-4o-mini",
                    "memory_window": 10,
                    "active_sessions": 5,
                    "total_facts_stored": 150
                }
            }
        }


class RootResponse(BaseModel):
    """Response model for root endpoint."""
    
    message: str = Field(..., description="Welcome message")
    docs: str = Field(..., description="API documentation URL")
    health: str = Field(..., description="Health check URL")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "message": "Knowledge Chatbot API",
                "docs": "/docs",
                "health": "/api/health"
            }
        }
