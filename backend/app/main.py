"""Main FastAPI application entry point."""

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1.api import api_router

# Configure logging based on DEBUG setting
if settings.DEBUG:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    logger.info("Debug mode enabled - detailed logging active")
else:
    logging.basicConfig(level=logging.INFO)


def create_app():
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Agentic RAG-Based Knowledge App with Smart Upload and Semantic Search",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        debug=settings.DEBUG
    )
    
    # Add global exception handler for development debugging
    if settings.DEBUG:
        @app.exception_handler(Exception)
        async def debug_exception_handler(request: Request, exc: Exception):
            import traceback
            logger.error(f"Unhandled exception: {exc}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return JSONResponse(
                status_code=500,
                content={
                    "detail": str(exc),
                    "type": type(exc).__name__,
                    "traceback": traceback.format_exc() if settings.DEBUG else None
                }
            )
    
    # Set up CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:8000", "*"],  # '*' for debug; restrict in prod!
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_origin_regex="https://.*\.vercel\.app",
    )
    
    # Include API routes
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    return app


# Create the app instance
app = create_app()


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "message": "Agentic RAG-Based Knowledge App",
        "version": settings.VERSION,
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "RAG Knowledge App"
    }
