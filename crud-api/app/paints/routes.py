from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_async_db
from ..core.entities import User
from ..core.repositories import SQLAlchemyPaintProductRepository
from ..core.security import get_current_user, get_optional_current_user, require_admin
from .schemas import (
    Environment,
    PaintProductCreate,
    PaintProductResponse,
    PaintProductUpdate,
)
from .services import PaintProductUseCases

router = APIRouter(prefix="/paints", tags=["paint products"])


# helper function to get the use cases
async def get_paint_product_use_cases(
    db: AsyncSession = Depends(get_async_db),
) -> PaintProductUseCases:
    """Get paint product use cases."""
    repository = SQLAlchemyPaintProductRepository(db)
    return PaintProductUseCases(repository)


# route for listing all paint products
@router.get("/", response_model=List[PaintProductResponse])
async def list_paint_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    use_cases: PaintProductUseCases = Depends(get_paint_product_use_cases),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """List all paint products with pagination."""
    products = await use_cases.list_paint_products(skip=skip, limit=limit)
    response = []

    for product in products:
        if product is None or product.id is None:
            continue

        response.append(
            PaintProductResponse(
                id=product.id,
                name=product.name,
                color=product.color,
                surface_types=product.surface_types,
                environment=product.environment,
                finish_type=product.finish_type,
                features=product.features,
                product_line=product.product_line,
                price=product.price,
                ai_summary=product.ai_summary,
                usage_tags=product.usage_tags,
                created_at=product.created_at or datetime.now(),  # Temporary fix
                updated_at=product.updated_at or datetime.now(),  # Temporary fix
            )
        )

    return response


# route for searching paint products
@router.get("/search", response_model=List[PaintProductResponse])
async def search_paint_products(
    color: Optional[str] = Query(None, description="Filter by color"),
    environment: Optional[Environment] = Query(
        None, description="Filter by environment"
    ),
    finish_type: Optional[str] = Query(None, description="Filter by finish type"),
    product_line: Optional[str] = Query(None, description="Filter by product line"),
    surface_type: Optional[str] = Query(None, description="Filter by surface type"),
    feature: Optional[str] = Query(None, description="Filter by feature"),
    usage_tag: Optional[str] = Query(None, description="Filter by usage tag"),
    name: Optional[str] = Query(None, description="Search by name"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    use_cases: PaintProductUseCases = Depends(get_paint_product_use_cases),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Search paint products with filters."""
    filters = {}

    if color:
        filters["color"] = color
    if environment:
        filters["environment"] = environment.value
    if finish_type:
        filters["finish_type"] = finish_type
    if product_line:
        filters["product_line"] = product_line
    if surface_type:
        filters["surface_types"] = surface_type
    if feature:
        filters["features"] = feature
    if usage_tag:
        filters["usage_tags"] = usage_tag
    if name:
        filters["name"] = name

    products = await use_cases.search_paint_products(filters, skip=skip, limit=limit)
    response = []

    for product in products:
        if product is None or product.id is None:
            continue

        response.append(
            PaintProductResponse(
                id=product.id,
                name=product.name,
                color=product.color,
                surface_types=product.surface_types,
                environment=product.environment,
                finish_type=product.finish_type,
                features=product.features,
                product_line=product.product_line,
                price=product.price,
                ai_summary=product.ai_summary,
                usage_tags=product.usage_tags,
                created_at=product.created_at or datetime.now(),  # Temporary fix
                updated_at=product.updated_at or datetime.now(),  # Temporary fix
            )
        )

    return response


# route for getting a paint product by ID
@router.get("/{product_id}", response_model=PaintProductResponse)
async def get_paint_product(
    product_id: int,
    use_cases: PaintProductUseCases = Depends(get_paint_product_use_cases),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Get paint product by ID."""
    product = await use_cases.get_paint_product(product_id)
    if not product or product.id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Paint product not found"
        )

    return PaintProductResponse(
        id=product.id,
        name=product.name,
        color=product.color,
        surface_types=product.surface_types,
        environment=product.environment,
        finish_type=product.finish_type,
        features=product.features,
        product_line=product.product_line,
        price=product.price,
        ai_summary=product.ai_summary,
        usage_tags=product.usage_tags,
        created_at=product.created_at or datetime.now(),
        updated_at=product.updated_at or datetime.now(),
    )


# route for creating a paint product
@router.post(
    "/", response_model=PaintProductResponse, status_code=status.HTTP_201_CREATED
)
async def create_paint_product(
    product_data: PaintProductCreate,
    use_cases: PaintProductUseCases = Depends(get_paint_product_use_cases),
    current_user: User = Depends(require_admin),
):
    """Create a new paint product (admin only)."""
    try:
        product = await use_cases.create_paint_product(product_data.model_dump())

        if not product or product.id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Paint product not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return PaintProductResponse(
            id=product.id,
            name=product.name,
            color=product.color,
            surface_types=product.surface_types,
            environment=product.environment,
            finish_type=product.finish_type,
            features=product.features,
            product_line=product.product_line,
            price=product.price,
            ai_summary=product.ai_summary,
            usage_tags=product.usage_tags,
            created_at=product.created_at or datetime.now(),
            updated_at=product.updated_at or datetime.now(),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# route for updating a paint product
@router.put("/{product_id}", response_model=PaintProductResponse)
async def update_paint_product(
    product_id: int,
    product_data: PaintProductUpdate,
    use_cases: PaintProductUseCases = Depends(get_paint_product_use_cases),
    current_user: User = Depends(require_admin),
):
    """Update paint product (admin only)."""
    # Only include non-None values
    update_data = {k: v for k, v in product_data.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No update data provided"
        )

    product = await use_cases.update_paint_product(product_id, update_data)
    if not product or product.id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Paint product not found"
        )

    return PaintProductResponse(
        id=product.id,
        name=product.name,
        color=product.color,
        surface_types=product.surface_types,
        environment=product.environment,
        finish_type=product.finish_type,
        features=product.features,
        product_line=product.product_line,
        price=product.price,
        ai_summary=product.ai_summary,
        usage_tags=product.usage_tags,
        created_at=product.created_at or datetime.now(),
        updated_at=product.updated_at or datetime.now(),
    )


# route for deleting a paint product
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_paint_product(
    product_id: int,
    use_cases: PaintProductUseCases = Depends(get_paint_product_use_cases),
    current_user: User = Depends(require_admin),
):
    """Delete paint product (admin only)."""
    success = await use_cases.delete_paint_product(product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Paint product not found"
        )
