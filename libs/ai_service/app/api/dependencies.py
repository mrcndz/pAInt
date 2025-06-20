from ..agents.paint_product_enrichment_agent import PaintProductEnricher
from ..agents.paint_recommendation_agent import get_paint_agent
from ..rag.vector_store_pg import get_vector_store


def get_recommendation_agent():
    """Get the paint recommendation agent instance"""
    return get_paint_agent()


def get_enrichment_agent():
    """Get the paint product enrichment agent instance"""
    return PaintProductEnricher()


def get_vector_store_instance():
    """Get the vector store instance"""
    return get_vector_store()
