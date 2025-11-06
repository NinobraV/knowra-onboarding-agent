"""
FastAPI application entry point for RAG Ingestion Service.

Handles:
- Document ingestion (PDF, TXT, DOCX, MD)
- Chunking
- Embedding generation
- Persisting to vector store (Pinecone)
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import router
from app.utils.logger import app_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler for startup and shutdown events.
    
    Args:
        app: FastAPI application instance
    """
    # Startup
    app_logger.info("🚀 Starting RAG Ingestion Service...")
    
    try:
        # Initialize services on startup if needed
        app_logger.info("✅ Ingestion Service initialized successfully")
    except Exception as e:
        app_logger.error(f"❌ Failed to initialize ingestion service: {e}")
        raise
    
    yield
    
    # Shutdown
    app_logger.info("👋 Shutting down...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan
)


# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routes
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    
    app_logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
