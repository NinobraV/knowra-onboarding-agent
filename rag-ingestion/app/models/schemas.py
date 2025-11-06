"""
Pydantic models for API request/response validation.
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


# Root endpoint response
class RootResponse(BaseModel):
    """Root endpoint response."""
    message: str = Field(..., description="Welcome message")
    docs: str = Field(..., description="Documentation URL")
    health: str = Field(..., description="Health check URL")


# Health check response
class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    stats: Dict[str, Any] = Field(default_factory=dict, description="Service statistics")


# Ingestion request
class IngestionRequest(BaseModel):
    """Document ingestion request."""
    force_rebuild: bool = Field(
        default=False,
        description="Force rebuild even if no changes detected"
    )


# Ingestion response
class IngestionResponse(BaseModel):
    """Document ingestion response."""
    success: bool = Field(..., description="Whether ingestion was successful")
    message: str = Field(..., description="Status message")
    stats: Dict[str, Any] = Field(default_factory=dict, description="Ingestion statistics")


# Status check response
class StatusResponse(BaseModel):
    """Vector store status response."""
    initialized: bool = Field(..., description="Whether vector store is initialized")
    documents_count: int = Field(..., description="Number of documents in vector store")
    last_updated: Optional[str] = Field(None, description="Last update timestamp")
    data_hash: Optional[str] = Field(None, description="Current data hash")


# Error response
class ErrorResponse(BaseModel):
    """Error response."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
