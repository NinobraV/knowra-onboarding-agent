"""
API route definitions for the Knowledge Chatbot.
"""
import uuid
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    ClearResponse,
    HealthResponse,
    RootResponse,
    SessionRequest,
    SessionResponse,
    SessionListResponse,
    MessageListResponse,
    ChatSessionListResponse
)
from app.core.dependencies import get_rag_service, rebuild_rag_service, get_chat_persistence
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
    Chat endpoint - returns complete response (non-streaming).
    Persists user message and assistant response to MongoDB.
    
    Args:
        request: Chat request with message and session info
        
    Returns:
        ChatResponse: Complete JSON response with metadata
        
    Raises:
        HTTPException: If chat processing fails
    """
    try:
        service = get_rag_service()
        persistence = get_chat_persistence()
        
        # Get or create session
        session_id = request.session_id
        if not session_id:
            # Create a new session if none provided
            session_response = await persistence.create_session(
                user_id=None,
                project_id=request.project_id or "default",
                title=None  # Will be auto-generated from first message
            )
            session_id = session_response.session_id
        else:
            # Verify session exists
            existing_session = await persistence.get_session(session_id)
            if not existing_session:
                # Create session if it doesn't exist
                session_response = await persistence.create_session(
                    user_id=None,
                    project_id=request.project_id or "default",
                    title=None
                )
                session_id = session_response.session_id
        
        # Persist user message
        await persistence.add_message(
            session_id=session_id,
            role="user",
            content=request.message,
            sources=None,
            routing_info=None,
            safety_info=None,
            tokens=None
        )
        
        # Check if this is the first message and generate title
        session = await persistence.get_session(session_id)
        if session and session.message_count == 1:  # First message just added
            from app.utils.title_generator import generate_session_title
            try:
                title = await generate_session_title(request.message, llm_service=service)
                await persistence.update_session_title(session_id, title)
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Failed to generate session title: {e}")
        
        # Get RAG response
        response_text, metadata = service.chat_with_metadata(
            request.message,
            session_id=session_id,
            project_id=request.project_id
        )
        
        # Prepare sources for persistence
        sources = None
        if metadata.get('sources'):
            sources = [
                {
                    "id": src.get("id", "unknown"),
                    "score": src.get("score", 0.0),
                    "text": src.get("text", ""),
                    "metadata": src.get("metadata", {})
                }
                for src in metadata.get('sources', [])
            ]
        
        # Persist assistant message with metadata
        await persistence.add_message(
            session_id=session_id,
            role="assistant",
            content=response_text,
            sources=sources,
            routing_info=metadata.get('routing_info'),
            safety_info=metadata.get('safety_info'),
            tokens=metadata.get('tokens')
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
        persistence = get_chat_persistence()
        session_response = await persistence.create_session(
            user_id=request.user_id,
            project_id=request.project_id or "default",
            title=request.session_name
        )

        service.create_session(
            session_id = session_response.session_id, 
            user_id=request.user_id,
            project_id=request.project_id,
            session_name=request.session_name)
        
        return SessionResponse(
            session_id=session_response.session_id,
            user_id=session_response.user_id,
            project_id=session_response.project_id,
            session_name=session_response.title,
            created_at=session_response.created_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create session: {str(e)}"
        )


@router.get("/api/sessions", response_model=ChatSessionListResponse)
async def list_sessions(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=200, description="Maximum number of sessions to return")
):
    """
    List conversation sessions with optional filtering and pagination.
    
    Args:
        user_id: Optional user ID filter
        project_id: Optional project ID filter
        page: Page number
        page_size: Maximum number of sessions to return
        
    Returns:
        ChatSessionListResponse: Paginated list of sessions
        
    Raises:
        HTTPException: If listing fails
    """
    try:
        persistence = get_chat_persistence()
        sessions = await persistence.list_sessions(
            user_id=user_id,
            project_id=project_id,
            page=page,
            page_size=page_size
        )
        
        return sessions
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
        persistence = get_chat_persistence()
        session_response = await persistence.get_session(session_id)
        
        if not session_response:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )

        return SessionResponse(
            session_id=session_response.session_id,
            user_id=session_response.user_id,
            project_id=session_response.project_id,
            session_name=session_response.title,
            created_at=session_response.created_at.isoformat()
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
        persistence = get_chat_persistence()
        success = await persistence.delete_session(session_id, cascade=True)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        # Also clear from RAG service if it has the session
        try:
            service = get_rag_service()
            service.delete_session(session_id)
        except Exception as e:
            # Log but don't fail if RAG service cleanup fails
            import logging
            logging.getLogger(__name__).warning(f"Failed to clean up RAG session: {e}")
        
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


# ============================================================================
# Message History Endpoints (MongoDB-backed)
# ============================================================================

@router.get("/api/sessions/{session_id}/messages", response_model=MessageListResponse)
async def get_session_messages(
    session_id: str,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=200, description="Messages per page"),
    ascending: bool = Query(True, description="Sort order: true for oldest first, false for newest first")
):
    """
    Get paginated messages for a session.
    
    Args:
        session_id: Session identifier
        page: Page number (1-indexed)
        page_size: Number of messages per page
        ascending: Sort order (true = oldest first, false = newest first)
        
    Returns:
        MessageListResponse: Paginated message list with metadata
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        persistence = get_chat_persistence()
        
        # Check if session exists
        session = await persistence.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        # Get paginated messages
        messages = await persistence.get_messages(
            session_id=session_id,
            page=page,
            page_size=page_size,
            ascending=ascending
        )
        
        return messages
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve messages: {str(e)}"
        )


@router.get("/api/sessions/{session_id}/messages/recent")
async def get_recent_messages(
    session_id: str,
    limit: int = Query(10, ge=1, le=100, description="Number of recent messages")
):
    """
    Get the most recent messages for a session.
    
    Args:
        session_id: Session identifier
        limit: Number of recent messages to return
        
    Returns:
        List[ChatMessageResponse]: Recent messages (chronological order)
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        persistence = get_chat_persistence()
        
        # Check if session exists
        session = await persistence.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        # Get recent messages
        messages = await persistence.get_recent_messages(
            session_id=session_id,
            limit=limit
        )
        
        return messages
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve recent messages: {str(e)}"
        )


@router.get("/api/sessions/{session_id}/history-stats")
async def get_session_history_stats(session_id: str):
    """
    Get detailed statistics for a session including message history.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Dict: Detailed session statistics
        
    Raises:
        HTTPException: If session not found or retrieval fails
    """
    try:
        persistence = get_chat_persistence()
        
        stats = await persistence.get_session_stats(session_id)
        
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
            detail=f"Failed to get session statistics: {str(e)}"
        )


@router.get("/api/stats/global")
async def get_global_stats():
    """
    Get global statistics across all sessions and messages.
    
    Returns:
        Dict: Global statistics
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        persistence = get_chat_persistence()
        stats = await persistence.get_global_stats()
        
        # Also include RAG service stats
        rag_service = get_rag_service()
        rag_stats = rag_service.get_stats()
        
        return {
            "chat_history": stats,
            "rag_system": rag_stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get global statistics: {str(e)}"
        )

