from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis, from_url
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from apps.api.core.config import settings
from apps.api.core.database import get_db

logger = get_logger(__name__)
router = APIRouter()

async def get_redis() -> Redis:
    """Get Redis connection."""
    redis = from_url(str(settings.REDIS_URL))
    try:
        yield redis
    finally:
        await redis.close()

@router.get("/health")
async def health_check(
    db: Annotated[AsyncSession, Depends(get_db)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> dict:
    """Health check endpoint that verifies database and Redis connectivity."""
    status = {
        "status": "healthy",
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
        "services": {
            "database": "healthy",
            "redis": "healthy",
        },
    }

    try:
        # Test database connection
        await db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error("database_health_check_failed", error=str(e))
        status["services"]["database"] = "unhealthy"
        status["status"] = "degraded"

    try:
        # Test Redis connection
        await redis.ping()
    except Exception as e:
        logger.error("redis_health_check_failed", error=str(e))
        status["services"]["redis"] = "unhealthy"
        status["status"] = "degraded"

    if status["status"] == "degraded":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=status,
        )

    return status 