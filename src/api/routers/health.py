"""Health Check Endpoints"""

from fastapi import APIRouter
from datetime import datetime, timezone
from src.database.db import DatabaseManager
from src.database.redis_client import RedisClient

router = APIRouter()

@router.get("/health")
async def health_check():
    """Overall system health check"""
    db = DatabaseManager()
    redis = RedisClient()
    
    db_status = db.health_check()
    redis_status = redis.health_check()
    
    return {
        "status": "healthy" if (db_status and redis_status) else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {
            "database": "✅ OK" if db_status else "❌ FAILED",
            "redis": "✅ OK" if redis_status else "❌ FAILED",
            "api": "✅ OK"
        }
    }

@router.get("/health/db")
async def database_health():
    """Database health check"""
    db = DatabaseManager()
    status = db.health_check()
    return {"database": "✅ OK" if status else "❌ FAILED"}

@router.get("/health/redis")
async def redis_health():
    """Redis health check"""
    redis = RedisClient()
    status = redis.health_check()
    return {"redis": "✅ OK" if status else "❌ FAILED"}
