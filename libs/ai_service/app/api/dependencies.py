from ..agents.paint_product_enrichment_agent import PaintProductEnricher
from ..agents.paint_recommendation_agent import create_session_recommendation_agent
from ..rag.vector_store_pg import get_vector_store
from ..services.conversation_manager import get_conversation_manager


def get_session_aware_agent():
    """Get the session-aware paint recommendation agent instance"""
    conversation_manager = get_conversation_manager()
    return create_session_recommendation_agent(conversation_manager)


def get_enrichment_agent():
    """Get the paint product enrichment agent instance"""
    return PaintProductEnricher()


def get_vector_store_instance():
    """Get the vector store instance"""
    return get_vector_store()


def get_conversation_manager_instance():
    """Get the conversation manager instance"""
    return get_conversation_manager()
