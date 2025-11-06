"""
API route definitions for the RAG Ingestion Service.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.models.schemas import (
    RootResponse,
    HealthResponse,
    IngestionRequest,
    IngestionResponse,
    StatusResponse,
    ErrorResponse
)
from app.core.dependencies import get_ingestion_service
from app.utils.logger import app_logger


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
        message="RAG Ingestion Service API",
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
        service = get_ingestion_service()
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


@router.get("/api/status", response_model=StatusResponse)
async def get_status():
    """
    Get vector store status.
    
    Returns:
        StatusResponse: Vector store status information
        
    Raises:
        HTTPException: If unable to retrieve status
    """
    try:
        service = get_ingestion_service()
        status = service.get_status()
        
        return StatusResponse(**status)
    except Exception as e:
        app_logger.error(f"Failed to get status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve status: {str(e)}"
        )


@router.post("/api/ingest", response_model=IngestionResponse)
async def ingest_documents(request: IngestionRequest = IngestionRequest()):
    """
    Trigger document ingestion.
    
    Args:
        request: Ingestion request with optional force_rebuild flag
        
    Returns:
        IngestionResponse: Ingestion results and statistics
        
    Raises:
        HTTPException: If ingestion fails
    """
    try:
        service = get_ingestion_service()
        
        app_logger.info(f"📥 Ingestion requested (force={request.force_rebuild})")
        
        result = service.ingest_documents(force=request.force_rebuild)
        
        return IngestionResponse(
            success=True,
            message=result["message"],
            stats=result["stats"]
        )
        
    except Exception as e:
        app_logger.error(f"❌ Ingestion failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion failed: {str(e)}"
        )


@router.post("/api/rebuild")
async def rebuild_vectorstore():
    """
    Force rebuild of the vector store.
    
    Returns:
        IngestionResponse: Rebuild results and statistics
        
    Raises:
        HTTPException: If rebuild fails
    """
    try:
        service = get_ingestion_service()
        
        app_logger.info("🔄 Force rebuild requested")
        
        result = service.ingest_documents(force=True)
        
        return IngestionResponse(
            success=True,
            message="Vector store rebuilt successfully",
            stats=result["stats"]
        )
        
    except Exception as e:
        app_logger.error(f"❌ Rebuild failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Rebuild failed: {str(e)}"
        )
