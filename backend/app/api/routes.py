"""
API route definitions for the Knowledge Chatbot.
"""
import asyncio
import uuid
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Optional

from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    ClearResponse,
    HealthResponse,
    RootResponse,
    SessionRequest,
    SessionResponse,
    SessionListResponse
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
        request: Chat request with message, stream flag, and session info
        
    Returns:
        StreamingResponse: If stream=True (SSE format)
        ChatResponse: If stream=False (JSON format)
        
    Raises:
        HTTPException: If chat processing fails
    """
    try:
        service = get_rag_service()
        
        # Get or create session if session_id provided
        session_id = request.session_id
        if not session_id:
            # Generate a new session ID if none provided
            session_id = f"session-{uuid.uuid4()}"
        
        # Note: Auto-rebuild is controlled by AUTO_REBUILD_ENABLED in config
        # Manual rebuild available via POST /rebuild endpoint
        
        if request.stream:
            # Streaming response using SSE
            async def event_generator():
                """Generate Server-Sent Events."""
                try:
                    async for chunk in service.stream_response(
                        request.message, 
                        session_id=session_id,
                        project_id=request.project_id
                    ):
                        if chunk:
                            # SSE format: data: <content>\n\n
                            yield f"data: {chunk}\n\n"
                            await asyncio.sleep(settings.SSE_DELAY)
                    
                    # Send end signal with metadata
                    metadata = {
                        "session_id": session_id,
                        "project_id": request.project_id
                    }
                    yield f"data: [DONE]\n\n"
                    yield f"data: [METADATA]{metadata}\n\n"
                    
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
                    "X-Accel-Buffering": "no",  # Disable buffering in nginx
                    "X-Session-ID": session_id
                }
            )
        else:
            # Non-streaming JSON response
            response_text, metadata = service.chat_with_metadata(
                request.message,
                session_id=session_id,
                project_id=request.project_id
            )
            
            return ChatResponse(
                response=response_text,
                sources=metadata.get('sources', []),
                session_id=session_id,
                project_id=request.project_id,
                routing_info=metadata.get('routing_info'),
                safety_info=metadata.get('safety_info')
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}"
        )


@router.post("/api/clear", response_model=ClearResponse)
async def clear_history(session_id: Optional[str] = Query(None, description="Session ID to clear (if not provided, clears current session)")):
    """
    Clear conversation history (memory) for a session.
    
    Args:
        session_id: Optional session ID to clear
        
    Returns:
        ClearResponse: Confirmation message
        
    Raises:
        HTTPException: If clear operation fails
    """
    try:
        service = get_rag_service()
        service.clear_memory(session_id)
        
        return ClearResponse(
            message="Conversation history cleared successfully",
            session_id=session_id
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


# Session Management Endpoints

@router.post("/api/sessions", response_model=SessionResponse)
async def create_session(request: SessionRequest):
    """
    Create a new conversation session.
    
    Args:
        request: Session creation request
        
    Returns:
        SessionResponse: Created session information
        
    Raises:
        HTTPException: If session creation fails
    """
    try:
        service = get_rag_service()
        session_info = service.create_session(
            user_id=request.user_id,
            project_id=request.project_id,
            session_name=request.session_name
        )
        
        return SessionResponse(
            session_id=session_info.session_id,
            user_id=session_info.user_id,
            project_id=session_info.project_id,
            session_name=session_info.session_name,
            created_at=session_info.created_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create session: {str(e)}"
        )


@router.get("/api/sessions", response_model=SessionListResponse)
async def list_sessions(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of sessions to return")
):
    """
    List conversation sessions with optional filtering.
    
    Args:
        user_id: Optional user ID filter
        project_id: Optional project ID filter
        limit: Maximum number of sessions to return
        
    Returns:
        SessionListResponse: List of sessions
        
    Raises:
        HTTPException: If listing fails
    """
    try:
        service = get_rag_service()
        sessions = service.list_sessions(
            user_id=user_id,
            project_id=project_id,
            limit=limit
        )
        
        session_responses = []
        for session in sessions:
            session_responses.append(SessionResponse(
                session_id=session.session_id,
                user_id=session.user_id,
                project_id=session.project_id,
                session_name=session.session_name,
                created_at=session.created_at.isoformat()
            ))
        
        return SessionListResponse(
            sessions=session_responses,
            total_count=len(session_responses)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list sessions: {str(e)}"
        )


@router.get("/api/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """
    Get information about a specific session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        SessionResponse: Session information
        
    Raises:
        HTTPException: If session not found or retrieval fails
    """
    try:
        service = get_rag_service()
        session_info = service.get_session(session_id)
        
        if not session_info:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        return SessionResponse(
            session_id=session_info.session_id,
            user_id=session_info.user_id,
            project_id=session_info.project_id,
            session_name=session_info.session_name,
            created_at=session_info.created_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session: {str(e)}"
        )


@router.delete("/api/sessions/{session_id}", response_model=ClearResponse)
async def delete_session(session_id: str):
    """
    Delete a conversation session and all its data.
    
    Args:
        session_id: Session identifier
        
    Returns:
        ClearResponse: Confirmation message
        
    Raises:
        HTTPException: If deletion fails
    """
    try:
        service = get_rag_service()
        success = service.delete_session(session_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        return ClearResponse(
            message=f"Session {session_id} deleted successfully",
            session_id=session_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete session: {str(e)}"
        )


@router.get("/api/sessions/{session_id}/stats")
async def get_session_stats(session_id: str):
    """
    Get memory and usage statistics for a session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Dict: Session statistics
        
    Raises:
        HTTPException: If session not found or retrieval fails
    """
    try:
        service = get_rag_service()
        stats = service.get_session_stats(session_id)
        
        if not stats:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session stats: {str(e)}"
        )
