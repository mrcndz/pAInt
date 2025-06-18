from typing import Any, Dict, List, Optional

from ..core.entities import PaintProduct
from ..core.repositories_interfaces import PaintProductRepository


class PaintProductUseCases:
    """Use cases for paint product operations."""

    def __init__(self, repository: PaintProductRepository):
        self.repository = repository

    async def create_paint_product(self, product_data: dict) -> PaintProduct:
        """Create a new paint product."""
        product = PaintProduct(
            name=product_data["name"],
            color=product_data["color"],
            surface_types=product_data.get("surface_types", []),
            environment=product_data["environment"],
            finish_type=product_data["finish_type"],
            features=product_data.get("features", []),
            product_line=product_data["product_line"],
            price=product_data.get("price"),
            ai_summary=product_data.get("ai_summary"),
            usage_tags=product_data.get("usage_tags", []),
        )

        # Save through repository
        return await self.repository.create(product)

    async def get_paint_product(self, product_id: int) -> Optional[PaintProduct]:
        """Get paint product by ID."""
        return await self.repository.get_by_id(product_id)

    async def list_paint_products(
        self, skip: int = 0, limit: int = 100
    ) -> List[PaintProduct]:
        """List all paint products with pagination."""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def search_paint_products(
        self, filters: Dict[str, Any], skip: int = 0, limit: int = 100
    ) -> List[PaintProduct]:
        """Search paint products with filters."""
        return await self.repository.search(filters, skip=skip, limit=limit)

    async def update_paint_product(
        self, product_id: int, product_data: dict
    ) -> Optional[PaintProduct]:
        """Update paint product."""
        # Get existing product
        existing_product = await self.repository.get_by_id(product_id)
        if not existing_product:
            return None

        # Update fields
        for field, value in product_data.items():
            if hasattr(existing_product, field):
                setattr(existing_product, field, value)

        return await self.repository.update(product_id, existing_product)

    async def delete_paint_product(self, product_id: int) -> bool:
        """Delete paint product."""
        return await self.repository.delete(product_id)

    async def search_by_color(self, color: str) -> List[PaintProduct]:
        """Search paint products by color."""
        filters = {"color": color}
        return await self.repository.search(filters)

    async def search_by_surface_type(self, surface_type: str) -> List[PaintProduct]:
        """Search paint products by surface type."""
        filters = {"surface_types": surface_type}
        return await self.repository.search(filters)

    async def search_by_environment(self, environment: str) -> List[PaintProduct]:
        """Search paint products by environment."""
        filters = {"environment": environment}
        return await self.repository.search(filters)

    async def search_by_product_line(self, product_line: str) -> List[PaintProduct]:
        """Search paint products by product line."""
        filters = {"product_line": product_line}
        return await self.repository.search(filters)
