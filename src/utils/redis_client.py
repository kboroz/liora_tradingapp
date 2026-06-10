"""
Redis client singleton for LIORA TradingApp
Used for: caching prices, storing predictions, rate limiting
"""

import json
import logging
from typing import Any, Optional

import redis

from config.settings import settings

logger = logging.getLogger(__name__)

# ─── Redis client (created once) ─────────────────────────
_redis_client: Optional[redis.Redis] = None


def get_redis() -> redis.Redis:
    """
    Returns the Redis client singleton.
    Creates it on first call.
    """
    global _redis_client

    if _redis_client is None:
        _redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,   # always return strings not bytes
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True,
        )
        logger.info("Redis client created")

    return _redis_client


# ─── Health check ─────────────────────────────────────────
def check_redis_connection() -> bool:
    """Returns True if Redis is reachable."""
    try:
        return get_redis().ping()
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return False


# ─── Simple get/set with JSON ────────────────────────────
def cache_set(key: str, value: Any, ttl_seconds: int = 300) -> bool:
    """
    Store any Python object in Redis as JSON.

    Example:
        cache_set("price:BTCUSDT", {"price": 65000}, ttl_seconds=60)
    """
    try:
        get_redis().setex(
            name=key,
            time=ttl_seconds,
            value=json.dumps(value)
        )
        return True
    except Exception as e:
        logger.error(f"Redis SET failed for key {key}: {e}")
        return False


def cache_get(key: str) -> Optional[Any]:
    """
    Retrieve a cached value. Returns None if not found or expired.

    Example:
        data = cache_get("price:BTCUSDT")
    """
    try:
        raw = get_redis().get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as e:
        logger.error(f"Redis GET failed for key {key}: {e}")
        return None


def cache_delete(key: str) -> bool:
    """Delete a cached key."""
    try:
        get_redis().delete(key)
        return True
    except Exception as e:
        logger.error(f"Redis DELETE failed for key {key}: {e}")
        return False


# ─── Price caching helpers ───────────────────────────────
def cache_latest_price(symbol: str, price_data: dict) -> bool:
    """
    Cache latest price for a symbol (expires in 30 seconds).

    Example:
        cache_latest_price("BTCUSDT", {"price": 65000, "time": "..."})
    """
    key = f"price:latest:{symbol}"
    return cache_set(key, price_data, ttl_seconds=30)


def get_latest_price(symbol: str) -> Optional[dict]:
    """
    Get cached latest price for a symbol.
    Returns None if no recent price cached.
    """
    key = f"price:latest:{symbol}"
    return cache_get(key)


# ─── Prediction caching helpers ──────────────────────────
def cache_prediction(symbol: str, prediction: dict) -> bool:
    """
    Cache latest model prediction (expires in 1 hour).
    """
    key = f"prediction:latest:{symbol}"
    return cache_set(key, prediction, ttl_seconds=3600)


def get_cached_prediction(symbol: str) -> Optional[dict]:
    """
    Get latest cached prediction for a symbol.
    """
    key = f"prediction:latest:{symbol}"
    return cache_get(key)


# ─── Correlation caching helpers ─────────────────────────
def cache_correlations(window: str, data: dict) -> bool:
    """
    Cache correlation matrix (expires in 1 hour).
    """
    key = f"correlations:{window}"
    return cache_set(key, data, ttl_seconds=3600)


def get_cached_correlations(window: str) -> Optional[dict]:
    """
    Get cached correlation matrix.
    """
    key = f"correlations:{window}"
    return cache_get(key)
