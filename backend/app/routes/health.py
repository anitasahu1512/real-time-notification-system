from fastapi import APIRouter
from sqlalchemy import text

from app.database.database import SessionLocal
from app.services.redis_client import get_redis_client


router = APIRouter()


@router.get("/health")
async def health_check():

    # Check database
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        database_status = "ok"
    except Exception:
        database_status = "error"

    # Check Redis
    try:
        redis_client = get_redis_client()
        await redis_client.ping()
        await redis_client.aclose()
        redis_status = "ok"
    except Exception:
        redis_status = "error"

    if database_status == "ok" and redis_status == "ok":
        status = "healthy"
    else:
        status = "unhealthy"

    return {
        "status": status,
        "database": database_status,
        "redis": redis_status
    }