import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_recommendation_agent
from ..models import RecommendationRequest, RecommendationResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/recommend",
    response_model=RecommendationResponse,
    summary="Get paint recommendations",
)
async def get_paint_recommendation(
    request: RecommendationRequest, paint_agent=Depends(get_recommendation_agent)
):
    """
    Get AI-powered paint recommendations based on natural language queries.

    This endpoint accepts natural language queries in Portuguese or English and returns
    personalized paint recommendations using the AI agent.

    Example queries:
    - "Preciso de tinta azul para o quarto"
    - "Quero uma cor que traga tranquilidade"

    Features:
    - Product-specific recommendations with prices and features
    - Conversational memory within session
    """
    try:
        logger.info(f"Recommendation request: {request.message}")
        response = paint_agent.get_recommendation(request.message)

        return RecommendationResponse(response=response, session_id=request.session_id)
    except Exception as e:
        logger.error(f"Error in recommendation endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")


@router.post("/chat/reset", summary="Reset chat session")
async def reset_chat_session(
    session_id: Optional[str] = None, paint_agent=Depends(get_recommendation_agent)
):
    """
    Reset the conversation memory for the chat session.

    This clears the agent's memory of previous interactions, allowing for
    a fresh conversation context.
    """
    try:
        paint_agent.reset_conversation()
        return {"message": "Chat session reset successfully", "session_id": session_id}
    except Exception as e:
        logger.error(f"Error resetting chat session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

