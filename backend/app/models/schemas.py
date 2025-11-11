"""
Pydantic models and schemas for request/response validation.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import uuid


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
