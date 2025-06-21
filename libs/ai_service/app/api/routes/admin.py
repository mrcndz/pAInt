import logging

from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_enrichment_agent, get_vector_store_instance
from ..models import EmbeddingRequest

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/embeddings/populate", summary="Populate vector embeddings")
async def populate_embeddings(
    request: EmbeddingRequest, vector_store=Depends(get_vector_store_instance)
):
    """
    Populate or rebuild vector embeddings for all products.

    ## @! Em produção isso deve ser feito com autenticação

    This endpoint generates vector embeddings for paint products that don't have them,
    or optionally rebuilds all embeddings if `force=True`.

    Use cases:
    - Initial setup after adding new products
    - Rebuilding embeddings after model changes
    - Fixing corrupted or missing embeddings

    Parameters:
    - `force`: If True, regenerates embeddings for ALL products (expensive operation)

    **Note:** This operation consumes OpenAI API tokens and may take several minutes
    for large product catalogs.
    """
    try:
        logger.info(f"Populating embeddings, force={request.force}")
        count = vector_store.populate_embeddings(force=request.force)

        return {
            "message": f"Successfully processed {count} products",
            "products_processed": count,
            "force_rebuild": request.force,
        }
    except Exception as e:
        logger.error(f"Error populating embeddings: {e}")
        raise HTTPException(
            status_code=500, detail=f"Embedding population failed: {str(e)}"
        )


@router.post("/enrich/all", summary="Enrich all products with AI content")
async def enrich_all_products(
    batch_size: int = 5, enricher=Depends(get_enrichment_agent)
):
    """
    Enrich all products with AI-generated summaries and usage tags.

    ## @! Em produção isso deve ser feito com autenticação

    This endpoint processes all products in the database and generates:
    - Portuguese product summaries (2-3 sentences)
    - Usage tags for better categorization

    **Parameters:**
    - `batch_size`: Number of products to process before pausing (default: 5)

    **Note:** This operation consumes OpenAI API tokens and may take several minutes
    depending on the number of products to enrich.
    """
    try:
        logger.info(f"Starting bulk enrichment with batch_size={batch_size}")
        enricher.enrich_all_products(batch_size=batch_size)

        return {
            "message": "All products enriched successfully",
            "batch_size": batch_size,
        }
    except Exception as e:
        logger.error(f"Error in bulk enrichment: {e}")
        raise HTTPException(status_code=500, detail=f"Enrichment failed: {str(e)}")
