import logging

from fastapi import APIRouter, Depends, HTTPException

from ...config import config
from ..dependencies import get_session_aware_agent, get_vector_store_instance
from ..models.responses import HealthResponse, ServiceStatusResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", summary="Service information")
async def root():
    """Get basic service information"""
    return {
        "service": "pAInt AI Service",
        "version": "2.0.0",
        "description": "AI-powered paint recommendation service with PostgreSQL vector storage",
    }


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health_check(
    paint_agent=Depends(get_session_aware_agent),
    vector_store=Depends(get_vector_store_instance),
):
    """
    Perform a health check on the AI service.

    Returns the health status of all major components:
    - Recommendation agent
    - Vector store
    - Enrichment agent
    """
    try:
        # Check agent status
        agent_ready = paint_agent.agent_executor is not None
        vector_store_ready = vector_store is not None

        return HealthResponse(
            status="healthy",
            service="ai_service",
            components={
                "agent": agent_ready,
                "vector_store": vector_store_ready,
                "enricher": True,
            },
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            service="ai_service",
            components={
                "agent": False,
                "vector_store": False,
                "enricher": False,
                "error": str(e),
            },
        )


@router.get(
    "/api/v1/status",
    response_model=ServiceStatusResponse,
    summary="Detailed service status",
)
async def get_service_status(
    paint_agent=Depends(get_session_aware_agent),
    vector_store=Depends(get_vector_store_instance),
):
    """
    Get detailed status information about the AI service.

    Provides information about:
    - Service version and status
    - Component health and configuration
    - Available capabilities
    """
    try:
        # Check agent status
        agent_ready = paint_agent.agent_executor is not None
        vector_store_ready = vector_store is not None

        return ServiceStatusResponse(
            service="pAInt AI Service",
            version="2.0.0",
            status="operational",
            components={
                "recommendation_agent": {
                    "status": "ready" if agent_ready else "not_ready",
                    "llm_model": config.OPENAI_MODEL,
                },
                "vector_store": {
                    "status": "ready" if vector_store_ready else "not_ready",
                    "type": "PostgreSQL + pgvector",
                    "embedding_model": "text-embedding-ada-002",
                },
                "enrichment_agent": {
                    "status": "ready",
                    "capabilities": ["Portuguese summaries", "usage tags"],
                },
            },
            capabilities=[
                "Natural language paint recommendations",
                "Semantic product search",
                "Attribute-based filtering",
                "Multilingual support (PT/EN)",
                "AI content enrichment",
            ],
        )
    except Exception as e:
        logger.error(f"Error getting service status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
