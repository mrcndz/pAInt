from typing import List, Optional

from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    message: str = Field(
        ..., description="Natural language query for paint recommendations"
    )
    session_uuid: Optional[str] = Field(
        None, description="Optional session UUID for conversation tracking"
    )
    image_base64: Optional[str] = Field(
        None, description="Optional base64 encoded image for paint simulation"
    )


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query for semantic similarity")
    k: int = Field(5, ge=1, le=20, description="Maximum number of results to return")
    threshold: float = Field(
        0.7, ge=0.0, le=1.0, description="Minimum similarity threshold"
    )


class FilterRequest(BaseModel):
    environment: Optional[str] = Field(
        None, description="Environment type: 'interno', 'externo', or 'ambos'"
    )
    finish_type: Optional[str] = Field(
        None,
        description="Finish type: 'fosco', 'acetinado', 'semi-brilho', 'brilhante'",
    )
    product_line: Optional[str] = Field(
        None, description="Product line: 'Premium', 'Padrão', 'Econômico', 'Especial'"
    )
    color: Optional[str] = Field(None, description="Color name or partial match")
    features: Optional[List[str]] = Field(None, description="List of required features")
    surface_types: Optional[List[str]] = Field(
        None, description="List of compatible surface types"
    )
    k: int = Field(5, ge=1, le=20, description="Maximum number of results to return")


class EmbeddingRequest(BaseModel):
    force: bool = Field(False, description="Force rebuild all embeddings if True")
