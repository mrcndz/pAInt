from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RecommendationResponse(BaseModel):
    response: str = Field(..., description="AI-generated recommendation response")
    session_id: Optional[str] = Field(None, description="Session ID for conversation tracking")


class ProductResponse(BaseModel):
    id: int = Field(..., description="Unique product identifier")
    name: str = Field(..., description="Product name")
    color: str = Field(..., description="Product color")
    surface_types: List[str] = Field(..., description="Compatible surface types")
    environment: str = Field(..., description="Suitable environment (internal/external)")
    finish_type: str = Field(..., description="Paint finish type")
    features: List[str] = Field(..., description="Product features and characteristics")
    product_line: str = Field(..., description="Product line category")
    price: Optional[float] = Field(None, description="Product price in BRL")
    ai_summary: Optional[str] = Field(None, description="AI-generated product summary")
    usage_tags: List[str] = Field(..., description="Usage and application tags")
    relevance_score: float = Field(..., description="Relevance score for search results")


class SearchResponse(BaseModel):
    query: str = Field(..., description="Original search query")
    results: List[ProductResponse] = Field(..., description="List of matching products")
    count: int = Field(..., description="Number of results found")
    search_type: str = Field(..., description="Type of search performed")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service health status")
    service: str = Field(..., description="Service name")
    components: Dict[str, Any] = Field(..., description="Component health status")


class ServiceStatusResponse(BaseModel):
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    status: str = Field(..., description="Overall service status")
    components: Dict[str, Any] = Field(..., description="Detailed component information")
    capabilities: List[str] = Field(..., description="Service capabilities")
