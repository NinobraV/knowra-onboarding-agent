"""
API route definitions for the Knowledge Chatbot.
"""
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    ClearResponse,
    HealthResponse,
    RootResponse
)
from app.core.dependencies import get_rag_service, rebuild_rag_service
from app.core.config import settings


# Create API router
router = APIRouter()


@router.get("/", response_model=RootResponse)
async def root():
    """
    Root endpoint providing API information.
    
    Returns:
        RootResponse: API information and links
    """
    return RootResponse(
        message="Knowledge Chatbot API",
        docs="/docs",
        health="/api/health"
    )


@router.get("/api/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint with system statistics.
    
    Returns:
        HealthResponse: System health and statistics
        
    Raises:
        HTTPException: If service is unavailable
    """
    try:
        service = get_rag_service()
        stats = service.get_stats()
        
        return HealthResponse(
            status="healthy",
            stats=stats
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Service unavailable: {str(e)}"
        )


@router.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Chat endpoint with optional Server-Sent Events streaming.
    
    Args:
        request: Chat request with message and stream flag
        
    Returns:
        StreamingResponse: If stream=True (SSE format)
        ChatResponse: If stream=False (JSON format)
        
    Raises:
        HTTPException: If chat processing fails
    """
    try:
        service = get_rag_service()
        
        # Note: Auto-rebuild is controlled by AUTO_REBUILD_ENABLED in config
        # Manual rebuild available via POST /rebuild endpoint
        
        if request.stream:
            # Streaming response using SSE
            async def event_generator():
                """Generate Server-Sent Events."""
                try:
                    async for chunk in service.stream_response(request.message):
                        if chunk:
                            # SSE format: data: <content>\n\n
                            yield f"data: {chunk}\n\n"
                            await asyncio.sleep(settings.SSE_DELAY)
                    
                    # Send end signal
                    yield "data: [DONE]\n\n"
                    
                except Exception as e:
                    error_msg = f"Error during streaming: {str(e)}"
                    yield f"data: {error_msg}\n\n"
                    yield "data: [DONE]\n\n"
            
            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"  # Disable buffering in nginx
                }
            )
        else:
            # Non-streaming JSON response
            response = service.chat(request.message)
            return ChatResponse(response=response)
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}"
        )


@router.post("/api/clear", response_model=ClearResponse)
async def clear_history():
    """
    Clear conversation history (memory).
    
    Returns:
        ClearResponse: Confirmation message
        
    Raises:
        HTTPException: If clear operation fails
    """
    try:
        service = get_rag_service()
        service.clear_memory()
        
        return ClearResponse(
            message="Conversation history cleared successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear history: {str(e)}"
        )


@router.post("/api/rebuild", response_model=ClearResponse)
async def rebuild_vectorstore():
    """
    Force rebuild of the vector store.
    
    Returns:
        ClearResponse: Confirmation message
        
    Raises:
        HTTPException: If rebuild fails
    """
    try:
        rebuild_rag_service()
        return ClearResponse(
            message="Vector store rebuilt successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to rebuild vector store: {str(e)}"
        )
