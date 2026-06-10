"""
Quick test to verify DB and Redis connections are working.
Run with: python scripts/test_connections.py
"""

import sys
import os

# Make sure Python finds our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.database import check_db_connection, execute_query
from src.utils.redis_client import check_redis_connection, cache_set, cache_get


def test_database():
    print("\n─── Testing PostgreSQL ───────────────────")
    
    ok = check_db_connection()
    if ok:
        print("  ✅ Connection: OK")
    else:
        print("  ❌ Connection: FAILED")
        return False

    # Check tables exist
    rows = execute_query("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    
    tables = [r["table_name"] for r in rows]
    print(f"  ✅ Tables found: {tables}")
    return True


def test_redis():
    print("\n─── Testing Redis ────────────────────────")
    
    ok = check_redis_connection()
    if ok:
        print("  ✅ Connection: OK")
    else:
        print("  ❌ Connection: FAILED")
        return False

    # Test write and read
    cache_set("test_key", {"hello": "liora"}, ttl_seconds=60)
    result = cache_get("test_key")

    if result and result.get("hello") == "liora":
        print("  ✅ Write/Read: OK")
    else:
        print("  ❌ Write/Read: FAILED")
        return False

    return True


if __name__ == "__main__":
    print("=" * 45)
    print("  LIORA TradingApp — Connection Tests")
    print("=" * 45)

    db_ok    = test_database()
    redis_ok = test_redis()

    print("\n─── Summary ──────────────────────────────")
    print(f"  PostgreSQL : {'✅ OK' if db_ok    else '❌ FAILED'}")
    print(f"  Redis      : {'✅ OK' if redis_ok else '❌ FAILED'}")
    print("=" * 45)

    if not (db_ok and redis_ok):
        sys.exit(1)
