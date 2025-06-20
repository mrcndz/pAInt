import logging

from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_vector_store_instance
from ..models import FilterRequest, ProductResponse, SearchRequest, SearchResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/search", response_model=SearchResponse, summary="Semantic search")
async def semantic_search(
    request: SearchRequest, vector_store=Depends(get_vector_store_instance)
):
    """
    Perform semantic search on paint products using vector similarity.

    This endpoint uses AI embeddings to find products that are semantically similar
    to your search query, even if they don't contain the exact words.

    Example queries:
    - "tinta tranquila para quarto"
    - "cor que traz serenidade"
    - "pintura resistente para cozinha"

    Parameters:
    - `query`: Natural language search query
    - `k`: Number of results to return (1-20)
    - `threshold`: Minimum similarity score (0.0-1.0)
    """
    try:
        logger.info(f"Semantic search: {request.query}")
        results = vector_store.search(
            query=request.query, k=request.k, threshold=request.threshold
        )

        products = [ProductResponse(**result) for result in results]

        return SearchResponse(
            query=request.query,
            results=products,
            count=len(products),
            search_type="semantic",
        )
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/filter", response_model=SearchResponse, summary="Filter products")
async def filter_products(
    request: FilterRequest, vector_store=Depends(get_vector_store_instance)
):
    """
    Filter paint products by specific attributes and characteristics.

    This endpoint allows precise filtering based on product specifications.
    You can combine multiple filters to narrow down your search.

    Available filters:
    - `environment`: "Interno", "Externo", "Ambos"
    - `finish_type`: "Matte", "satin", "semi-gloss", "gloss"
    - `product_line`: "Premium", "Padrão", "Econômico", "Especial"
    - `color`: Any color name (supports partial matching)
    - `features`: List of features like ["lavável", "antimofo", "ecológico"]
    - `surface_types`: List of surfaces like ["parede", "teto", "madeira"]

    Example filter combinations:**
    - Tintas laváveis para uso interno
    - Linha premium para uso externo
    """
    try:
        logger.info(f"Filter request: {request.dict(exclude_none=True)}")

        # Build filter kwargs
        filter_kwargs = {}
        if request.environment:
            filter_kwargs["environment"] = request.environment
        if request.finish_type:
            filter_kwargs["finish_type"] = request.finish_type
        if request.product_line:
            filter_kwargs["product_line"] = request.product_line
        if request.color:
            filter_kwargs["color"] = request.color
        if request.features:
            filter_kwargs["features"] = request.features
        if request.surface_types:
            filter_kwargs["surface_types"] = request.surface_types

        results = vector_store.search(
            query="", k=request.k, **filter_kwargs  # Empty query for pure filtering
        )

        products = [ProductResponse(**result) for result in results]

        return SearchResponse(
            query="", results=products, count=len(products), search_type="filter"
        )
    except Exception as e:
        logger.error(f"Error in filter endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Filter failed: {str(e)}")

