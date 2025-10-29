"""
Pydantic models and schemas for request/response validation.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    
    message: str = Field(..., description="User message to send to the chatbot")
    stream: bool = Field(True, description="Whether to stream the response via SSE")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "message": "What is the onboarding process?",
                "stream": True
            }
        }


class ChatResponse(BaseModel):
    """Response model for non-streaming chat."""
    
    response: str = Field(..., description="Chatbot response")
    sources: Optional[List[str]] = Field(None, description="Source documents used")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "response": "The onboarding process consists of...",
                "sources": ["01_ONBOARDING_GUIDE.md"]
            }
        }


class ClearResponse(BaseModel):
    """Response model for clear and rebuild endpoints."""
    
    message: str = Field(..., description="Status message")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "message": "Conversation history cleared successfully"
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
                    "vector_store_path": "./backend/chroma_db",
                    "embedding_model": "text-embedding-3-small",
                    "llm_model": "gpt-4o-mini",
                    "memory_window": 10
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
