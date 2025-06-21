"""
pAInt AI Service - Main application entry point

A microservice for AI-powered paint recommendations using:
- LangChain agents for natural language understanding
- PostgreSQL + pgvector for semantic search
- OpenAI embeddings and chat models
- FastAPI for REST API endpoints
"""

import logging

from .api import create_app
from .config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = create_app()

if __name__ == "__main__":
    import uvicorn

    # Configuration from environment or defaults
    host = getattr(config, "API_HOST", "0.0.0.0")
    port = getattr(config, "API_PORT", 8001)

    logger.info(f"Starting pAInt AI Service on {host}:{port}")

    uvicorn.run("main:app", host=host, port=port, reload=True, log_level="info")
