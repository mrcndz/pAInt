import logging
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .auth import routes as auth_routes
from .paints import routes as paint_routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create application
app = FastAPI(
    title="pAInt CRUD API",
    description="Intelligent Paint Catalog Assistant - CRUD API Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router)
app.include_router(paint_routes.router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "pAInt CRUD API",
        "version": "1.0.0",
        "description": "Intelligent Paint Catalog Assistant - CRUD API Service",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "auth": "/auth",
            "paints": "/paints",
            "health": "/health",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and load balancers."""
    try:
        # For simplicity, assume database is healthy if API is running
        # More detailed checks can be added later if needed
        return {
            "status": "healthy",
            "service": "api_service",
            "version": "1.0.0",
            "components": {
                "database": True,  # Simplified - assume healthy
                "api": True,
                "auth": True,
            },
            "environment": os.environ.get("ENVIRONMENT", "development"),
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "api_service",
            "components": {
                "database": False,
                "api": False,
                "auth": False,
                "error": str(e),
            },
        }


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Global HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unexpected errors."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "status_code": 500,
            "path": str(request.url),
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )

