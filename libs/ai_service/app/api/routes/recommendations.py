import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from ...auth.dependencies import get_current_user_id
from ..dependencies import get_conversation_manager_instance, get_session_aware_agent
from ..models import RecommendationRequest, RecommendationResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/recommend",
    response_model=RecommendationResponse,
    summary="Get paint recommendations",
)
async def get_paint_recommendation(
    request: RecommendationRequest,
    user_id: int = Depends(get_current_user_id),
    paint_agent=Depends(get_session_aware_agent),
    conversation_manager=Depends(get_conversation_manager_instance),
):
    """
    Get AI-powered paint recommendations based on natural language queries.

    This endpoint accepts natural language queries in Portuguese or English and returns
    personalized paint recommendations using the AI agent with persistent conversation memory.

    **Authentication Required**: This endpoint requires a valid JWT token.

    Example queries:
    - "Preciso de tinta azul para o quarto"
    - "Quero uma cor que traga tranquilidade"
    - "Que cor você recomenda para uma sala de estar moderna?"

    Features:
    - Product-specific recommendations with prices and features
    - Persistent conversational memory across sessions
    - Session-based conversation tracking
    - User-specific conversation isolation

    Parameters:
    - `message`: Natural language query for paint recommendations
    - `session_uuid`: Optional session UUID. If not provided, a new session will be created.
    """
    try:
        logger.info(f"Recommendation request from user {user_id}: {request.message}")

        # Handle session UUID
        session_uuid = request.session_uuid
        if not session_uuid:
            # Create new session if none provided
            session_uuid = conversation_manager.create_new_session(user_id)
            logger.info(f"Created new session {session_uuid} for user {user_id}")
        else:
            logger.info(f"Using existing session {session_uuid} for user {user_id}")

        # Get recommendation using session-aware agent
        response = paint_agent.get_recommendation(
            message=request.message, session_uuid=session_uuid, user_id=user_id
        )

        return RecommendationResponse(response=response, session_uuid=session_uuid)

    except Exception as e:
        logger.error(f"Error in recommendation endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")


@router.post("/chat/reset", summary="Reset chat session")
async def reset_chat_session(
    session_uuid: str,
    user_id: int = Depends(get_current_user_id),
    conversation_manager=Depends(get_conversation_manager_instance),
):
    """
    Reset the conversation memory for a specific chat session.

    **Authentication Required**: This endpoint requires a valid JWT token.

    This clears the session's conversation memory, allowing for a fresh conversation context.
    The session will be removed from the in-memory cache and the database record will be cleared.

    Parameters:
    - `session_uuid`: The UUID of the session to reset

    Security:
    - Only the session owner can reset their own sessions
    """
    try:
        logger.info(f"Resetting session {session_uuid} for user {user_id}")

        # Clear session from cache
        conversation_manager.clear_session_cache(session_uuid, user_id)

        # Create fresh session in database
        conversation_manager.create_new_session(user_id)

        return {
            "message": "Chat session reset successfully",
            "session_uuid": session_uuid,
            "user_id": user_id,
        }
    except Exception as e:
        logger.error(f"Error resetting chat session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/sessions", summary="Get user's chat sessions")
async def get_user_sessions(
    user_id: int = Depends(get_current_user_id),
):
    """
    Get all chat sessions for the current user.

    **Authentication Required**: This endpoint requires a valid JWT token.

    Returns a list of the user's chat sessions with basic information:
    - Session UUID
    - Creation date
    - Last activity
    - Message count

    This can be used by the frontend to show conversation history or allow
    users to continue previous conversations.
    """
    try:
        # This would be implemented to query user's sessions from database
        # For now, return a placeholder
        return {
            "message": "Get user sessions endpoint - to be implemented",
            "user_id": user_id,
        }
    except Exception as e:
        logger.error(f"Error getting user sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))
