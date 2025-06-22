import logging
import random
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from ...agents.intent_router import QueryRouter, intent_router
from ...auth.dependencies import get_current_user_id
from ..dependencies import get_conversation_manager_instance, get_session_aware_agent
from ..models import RecommendationRequest, RecommendationResponse, UserSessionsResponse

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

    This endpoint accepts natural language queries in Portuguese and returns
    personalized paint recommendations using the AI agent with persistent conversation memory.

    **Authentication Required**: This endpoint requires a valid JWT token.

    Example queries:
    - "Preciso de tinta azul para o quarto"
    - "Quero uma cor que traga tranquilidade"
    - "Que cor você recomenda para uma sala de estar moderna?"
    - "Simule uma cor de tinta para uma imagem"

    Features:
    - Product-specific recommendations with prices and features
    - Persistent conversational memory across sessions
    - Session-based conversation tracking
    - User-specific conversation isolation

    Parameters:
    - `message`: Natural language query for paint recommendations
    - `session_uuid`: Optional session UUID. If not provided, a new session will be created.
    - `image_base64`: Optional base64 encoded image for paint simulation
    """
    try:
        logger.info(f"Processing message from user {user_id}: {request.message}")

        # First classify the intent of the user's message
        intent_category = intent_router.route_query(request.message)
        logger.info(f"Intent classification for user {user_id}: {intent_category}")

        # Handle session UUID
        session_uuid = request.session_uuid
        if not session_uuid or session_uuid == "string":
            # Create new session if none provided or if invalid
            session_uuid = conversation_manager.create_new_session(user_id)
            logger.info(f"Created new session {session_uuid} for user {user_id}")
        else:
            logger.info(f"Using existing session {session_uuid} for user {user_id}")

        # Route based on detected intent
        if intent_category == "paint_question":
            # Handle paint-related questions using the main AI agent
            logger.info(f"Processing paint question for user {user_id}")
            result = paint_agent.get_recommendation(
                message=request.message,
                session_uuid=session_uuid,
                user_id=user_id,
                image_base64=request.image_base64,
            )
            # Handle both string and dict responses for backward compatibility
            if isinstance(result, dict):
                response = result.get("response", "")
                image_data = result.get("image_data")
            else:
                response = result
                image_data = None

        elif intent_category == "simple_greeting":
            # Handle greetings with friendly responses
            logger.info(f"Responding to greeting from user {user_id}")
            response = random.choice(QueryRouter.GREETING_RESPONSES)
            image_data = None

        elif intent_category == "off_topic":
            # Handle off-topic questions
            logger.info(f"Redirecting off-topic question from user {user_id}")
            response = QueryRouter.OFF_TOPIC_RESPONSE
            image_data = None

        else:
            # Fallback - treat as paint question
            logger.warning(
                f"Unknown intent category '{intent_category}' for user {user_id}, treating as paint question"
            )
            result = paint_agent.get_recommendation(
                message=request.message,
                session_uuid=session_uuid,
                user_id=user_id,
                image_base64=request.image_base64,
            )
            # Handle both string and dict responses for backward compatibility
            if isinstance(result, dict):
                response = result.get("response", "")
                image_data = result.get("image_data")
            else:
                response = result
                image_data = None

        return RecommendationResponse(
            response=response, session_uuid=session_uuid, image_data=image_data
        )

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


@router.get(
    "/chat/sessions",
    response_model=UserSessionsResponse,
    summary="Get user's chat sessions",
)
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
        conversation_manager = get_conversation_manager_instance()
        sessions = conversation_manager.get_user_sessions(user_id, limit=50)

        return {
            "user_id": user_id,
            "sessions": sessions,
            "total_sessions": len(sessions),
            "message": f"Retrieved {len(sessions)} chat sessions for user {user_id}",
        }
    except Exception as e:
        logger.error(f"Error getting user sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))
