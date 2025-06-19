import logging
from typing import Any, Dict, List, Optional

from config import config
from langchain_openai import OpenAIEmbeddings
from pgvector.sqlalchemy import Vector
from shared.database import get_db
from shared.models import PaintProductModel as PaintProduct
from sqlalchemy import text
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PaintVectorStorePG:
    """
    PostgreSQL-based vector store using pgvector for paint product embeddings.
    """

    def __init__(self):
        """Initialize vector store with OpenAI embeddings and PostgreSQL connection."""
        self.embeddings = OpenAIEmbeddings(
            api_key=config.OPENAI_API_KEY, model="text-embedding-ada-002"
        )

    def _create_product_content(self, product: PaintProduct) -> str:
        """Create searchable text content from a paint product."""
        content_parts = [
            f"Product: {product.name}",
            f"Color: {product.color}",
            f"Environment: {product.environment}",
            f"Finish: {product.finish_type}",
            f"Product Line: {product.product_line}",
        ]

        if product.surface_types:
            content_parts.append(f"Surface Types: {', '.join(product.surface_types)}")

        if product.features:
            content_parts.append(f"Features: {', '.join(product.features)}")

        if product.ai_summary:
            content_parts.append(f"Summary: {product.ai_summary}")

        if product.usage_tags:
            content_parts.append(f"Usage Tags: {', '.join(product.usage_tags)}")

        return "\n".join(content_parts)

    def populate_embeddings(self, force: bool = False) -> int:
        """
        Populate embeddings for products that don't have them.

        Args:
            force: If True, regenerate embeddings for all products

        Returns:
            Number of products processed
        """
        db = next(get_db())
        processed_count = 0

        try:
            # Get products that need embeddings
            if force:
                products = db.query(PaintProduct).all()
                logger.info(f"Force rebuilding embeddings for {len(products)} products")
            else:
                products = (
                    db.query(PaintProduct)
                    .filter(PaintProduct.embedding.is_(None))
                    .all()
                )
                logger.info(f"Found {len(products)} products without embeddings")

            if not products:
                logger.info("No products need embedding generation")
                return 0

            # Process in batches
            batch_size = 10
            for i in range(0, len(products), batch_size):
                batch = products[i : i + batch_size]

                # Generate content for batch
                batch_contents = []
                for product in batch:
                    content = self._create_product_content(product)
                    batch_contents.append(content)

                # Get embeddings for batch
                logger.info(f"Generating embeddings for batch {i//batch_size + 1}")
                batch_embeddings = self.embeddings.embed_documents(batch_contents)

                # Update products with embeddings
                for product, embedding in zip(batch, batch_embeddings):
                    product.embedding = embedding
                    processed_count += 1

                # Commit batch
                db.commit()
                logger.info(f"Processed {len(batch)} products in batch")

            logger.info(
                f"Successfully populated embeddings for {processed_count} products"
            )
            return processed_count

        except Exception as e:
            logger.error(f"Error populating embeddings: {e}")
            db.rollback()
            raise
        finally:
            db.close()

    def search(
        self,
        query: str = "",
        k: int = 5,
        threshold: float = 0.7,
        environment: Optional[str] = None,
        finish_type: Optional[str] = None,
        product_line: Optional[str] = None,
        color: Optional[str] = None,
        features: Optional[List[str]] = None,
        surface_types: Optional[List[str]] = None,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Search method that handles all scenarios:
        Semantic search eg. : search("blue paint for bedroom")
        Filtered search eg. : search("", environment="internal", features=["washable"])
        Hybrid search eg. : search("washable paint", environment="internal")

        Args:
            query: Search query for semantic similarity (optional)
            k: Number of results to return
            threshold: Minimum similarity threshold for vector search
            **filters: Metadata filters

        Returns:
            List of products with relevance scores
        """
        db = next(get_db())

        try:
            # Determine search mode
            has_query = query.strip() != ""
            has_filters = any(
                [environment, finish_type, product_line, color, features, surface_types]
            )

            if has_query:
                # Generate embedding for semantic search
                query_embedding = self.embeddings.embed_query(query)
                where_conditions = ["embedding IS NOT NULL"]
                params = {
                    "query_embedding": str(query_embedding),
                    "threshold": threshold,
                    "k": k,
                }

                # Add similarity threshold condition
                similarity_condition = (
                    "1 - (embedding <=> CAST(:query_embedding AS vector)) >= :threshold"
                )

                # Add metadata filters
                if environment:
                    where_conditions.append("environment = :environment")
                    params["environment"] = environment

                if finish_type:
                    where_conditions.append("finish_type = :finish_type")
                    params["finish_type"] = finish_type

                if product_line:
                    where_conditions.append("product_line = :product_line")
                    params["product_line"] = product_line

                if color:
                    where_conditions.append("LOWER(color) LIKE LOWER(:color)")
                    params["color"] = f"%{color}%"

                if features:
                    for i, feature in enumerate(features):
                        where_conditions.append(f":feature_{i} = ANY(features)")
                        params[f"feature_{i}"] = feature

                if surface_types:
                    for i, surface_type in enumerate(surface_types):
                        where_conditions.append(
                            f":surface_type_{i} = ANY(surface_types)"
                        )
                        params[f"surface_type_{i}"] = surface_type

                where_clause = " AND ".join(where_conditions)

                # Execute vector + filter search
                sql_query = f"""
                    SELECT 
                        id, name, color, surface_types, environment, finish_type, 
                        features, product_line, price, ai_summary, usage_tags,
                        1 - (embedding <=> CAST(:query_embedding AS vector)) as similarity_score
                    FROM paint_products 
                    WHERE {where_clause} AND {similarity_condition}
                    ORDER BY embedding <=> CAST(:query_embedding AS vector)
                    LIMIT :k
                """

                results = db.execute(text(sql_query), params).fetchall()

            else:
                # Pure filtering mode (no vector search)
                sql_query = db.query(PaintProduct)

                # Apply filters
                if environment:
                    sql_query = sql_query.filter(
                        PaintProduct.environment == environment
                    )

                if finish_type:
                    sql_query = sql_query.filter(
                        PaintProduct.finish_type == finish_type
                    )

                if product_line:
                    sql_query = sql_query.filter(
                        PaintProduct.product_line == product_line
                    )

                if color:
                    sql_query = sql_query.filter(PaintProduct.color.ilike(f"%{color}%"))

                if features:
                    for feature in features:
                        sql_query = sql_query.filter(
                            PaintProduct.features.any(feature)
                        )

                if surface_types:
                    for surface_type in surface_types:
                        sql_query = sql_query.filter(
                            PaintProduct.surface_types.any(surface_type)
                        )

                products = sql_query.limit(k).all()

                # Convert SQLAlchemy objects to result format
                results = []
                for product in products:
                    result = type(
                        "Result",
                        (),
                        {
                            "id": product.id,
                            "name": product.name,
                            "color": product.color,
                            "surface_types": product.surface_types,
                            "environment": product.environment,
                            "finish_type": product.finish_type,
                            "features": product.features,
                            "product_line": product.product_line,
                            "price": product.price,
                            "ai_summary": product.ai_summary,
                            "usage_tags": product.usage_tags,
                            "similarity_score": 1.0,  # No vector similarity
                        },
                    )()
                    results.append(result)

            # Convert to dictionaries
            products = []
            for row in results:
                product_dict = {
                    "id": row.id,
                    "name": row.name,
                    "color": row.color,
                    "surface_types": row.surface_types or [],
                    "environment": row.environment,
                    "finish_type": row.finish_type,
                    "features": row.features or [],
                    "product_line": row.product_line,
                    "price": float(row.price) if row.price else None,
                    "ai_summary": row.ai_summary,
                    "usage_tags": row.usage_tags or [],
                    "relevance_score": float(row.similarity_score),
                }
                products.append(product_dict)

            # Log search details
            search_type = (
                "vector+filter"
                if has_query and has_filters
                else "vector" if has_query else "filter"
            )
            applied_filters = [
                f for f in [environment, finish_type, product_line, color] if f
            ]
            if features:
                applied_filters.extend(features)
            if surface_types:
                applied_filters.extend(surface_types)

            logger.info(
                f"{search_type.title()} search found {len(products)} products "
                f"for query: '{query}' with filters: {applied_filters}"
            )
            return products

        except Exception as e:
            logger.error(f"Error in search: {e}")
            return []
        finally:
            db.close()


# Global instance
paint_vector_store_pg = PaintVectorStorePG()


def get_vector_store() -> PaintVectorStorePG:
    """Get the global PostgreSQL vector store instance."""
    return paint_vector_store_pg
