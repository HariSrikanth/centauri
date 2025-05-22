from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from structlog import get_logger

from apps.api.core.config import settings
from apps.api.core.logging import configure_logging
from apps.api.routers import auth, context, deltas, match, newsletter, system

logger = get_logger()

def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    configure_logging()

    app = FastAPI(
        title="alpha.me API",
        description="backend API for alpha.me",
        version=settings.API_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add OpenTelemetry instrumentation
    if settings.ENVIRONMENT != "development":
        FastAPIInstrumentor.instrument_app(app)

    # Include routers
    app.include_router(auth.router, prefix="/v1", tags=["auth"])
    app.include_router(context.router, prefix="/v1", tags=["context"])
    app.include_router(deltas.router, prefix="/v1", tags=["deltas"])
    app.include_router(match.router, prefix="/v1/match", tags=["match"])
    app.include_router(newsletter.router, prefix="/v1", tags=["newsletter"])
    app.include_router(system.router, prefix="/v1", tags=["system"])

    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting up alpha.me API", version=settings.API_VERSION)

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down alpha.me API")

    return app

app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "apps.api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
    ) 