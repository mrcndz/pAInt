import json
import logging
import time
from typing import Any, Dict, List

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from shared.database import get_db
from shared.models import PaintProductModel as PaintProduct

from ..config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnrichedContent(BaseModel):
    summary: str = Field(
        description="Summary of 2-3 sentences in Portuguese (Brazil) about the product."
    )
    tags: List[str] = Field(description="List of 3 to 5 relevant usage tags.")


class PaintProductEnricher:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=config.OPENAI_API_KEY,
            model=config.OPENAI_MODEL,
            temperature=config.TEMPERATURE,
        )

        self.structured_llm = self.llm.with_structured_output(EnrichedContent)

    def _get_enrichment_prompt(self, paint_data: Dict[str, Any]) -> str:
        """Create the prompt for the LLM focused on the task of enrichment."""

        return f"""
            You are an AI assistant specialized in creating marketing content for Suvinil paints.
            Your task is to generate a product summary and relevant usage tags based on the provided data.

            PRODUCT DATA:
            - Product: {paint_data['name']}
            - Color: {paint_data['color']}
            - Surface Types: {', '.join(paint_data['surface_types'])}
            - Environment: {paint_data['environment']}
            - Finish: {paint_data['finish_type']}
            - Features: {', '.join(paint_data.get('features', []))}
            - Product Line: {paint_data['product_line']}

            INSTRUCTIONS:
            1.  **Summary:** Write in Portuguese (Brazilian), focusing on practical benefits, aesthetic appeal, and special features.
            2.  **Tags:** Generate 3-5 relevant tags in Portuguese (Brazilian) from the following categories:
                -   Room types: sala de estar, quarto, cozinha, banheiro, escritório, quarto infantil
                -   Style: moderno, clássico, minimalista, rústico, elegante, aconchegante, vibrante
                -   Usage: alto tráfego, baixa manutenção, família, profissional, luxo
                -   Features: durável, fácil limpeza, resistente ao tempo, ecológico, secagem rápida
        """

    def enrich_product(self, product: PaintProduct) -> Dict[str, Any]:
        """Enrich a single product with AI-generated content"""
        paint_data = {
            "name": product.name,
            "color": product.color,
            "surface_types": product.surface_types or [],
            "environment": product.environment,
            "finish_type": product.finish_type,
            "features": product.features or [],
            "product_line": product.product_line,
        }
        logger.info(f"Enriching product: {product.name}")

        try:
            prompt = self._get_enrichment_prompt(paint_data)

            enriched_data_obj = self.structured_llm.invoke(prompt)

            if isinstance(enriched_data_obj, EnrichedContent):
                return enriched_data_obj.dict()

            return enriched_data_obj

        except Exception as e:
            logger.error(f"Error with LLM enrichment for product {product.id}: {e}")

            # Fallback
            fallback_summary = f"Tinta {paint_data.get('color', '')} da linha {paint_data.get('product_line', '')} ideal para {paint_data.get('environment', '')}."
            fallback_tags = [paint_data.get("environment", "interior")]

            return {"summary": fallback_summary, "tags": fallback_tags}

    def enrich_all_products(self, batch_size: int = 5):
        """Enrich all products in the database"""
        db = next(get_db())
        try:
            products_to_enrich = (
                db.query(PaintProduct).filter(PaintProduct.ai_summary.is_(None)).all()
            )
            logger.info(f"Found {len(products_to_enrich)} products to enrich")

            for i, product in enumerate(products_to_enrich):
                logger.info(
                    f"Processing product {i+1}/{len(products_to_enrich)}: {product.name}"
                )

                enriched_data = self.enrich_product(product)

                # Rename keys
                product.ai_summary = enriched_data["summary"]
                product.usage_tags = enriched_data["tags"]

                db.commit()
                logger.info(f"Successfully updated product {product.id}")

                # Little delay to avoid overloading the OpenAI API
                if (i + 1) % batch_size == 0 and i + 1 < len(products_to_enrich):
                    logger.info(
                        f"Processed batch of {batch_size}. Pausing for 5 seconds..."
                    )
                    time.sleep(5)

        except Exception as e:
            logger.error(f"An error occurred during enrichment: {e}")
            db.rollback()
        finally:
            db.close()
