from fastapi import FastAPI

from .middleware import setup_middleware
from .routes import admin, health, recommendations, search


def create_app() -> FastAPI:
    app = FastAPI(
        title="pAInt AI Service",
        description="AI-powered paint catalog recommendation service with PostgreSQL vector storage",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    setup_middleware(app)

    app.include_router(health.router, tags=["Health"])
    app.include_router(recommendations.router, prefix="/api/v1", tags=["Recommendations"])
    app.include_router(search.router, prefix="/api/v1", tags=["Search"])
    app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])

    return app
