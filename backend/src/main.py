"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.database import Base, engine

# Import routers
from src.auth.router import router as auth_router
from src.activities.router import router as activities_router
from src.goals.router import router as goals_router
from src.statistics.router import router as statistics_router
from src.sync.router import router as sync_router
from src.live.router import router as live_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup/shutdown."""
    # Startup: create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: dispose engine
    await engine.dispose()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Backend API for Sports Tracker mobile application",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers under /api/v1
    api_prefix = "/api/v1"
    app.include_router(auth_router, prefix=api_prefix)
    app.include_router(activities_router, prefix=api_prefix)
    app.include_router(goals_router, prefix=api_prefix)
    app.include_router(statistics_router, prefix=api_prefix)
    app.include_router(sync_router, prefix=api_prefix)
    app.include_router(live_router, prefix=api_prefix)

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy", "version": settings.app_version}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
