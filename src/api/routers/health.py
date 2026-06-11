from fastapi import APIRouter
from src.utils.database import check_db_connection
from src.utils.redis_client import check_redis_connection

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.get("/health/db")
async def database_health():
    status = check_db_connection()
    return {"database": "✅ OK" if status else "❌ FAILED"}

@router.get("/health/redis")
async def redis_health():
    status = check_redis_connection()
    return {"redis": "✅ OK" if status else "❌ FAILED"}
