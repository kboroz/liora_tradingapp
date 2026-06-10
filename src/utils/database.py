"""
SQLAlchemy database connection singleton for LIORA TradingApp
"""

import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base

from config.settings import settings

logger = logging.getLogger(__name__)

# ─── Base class for ORM models ────────────────────────────
Base = declarative_base()

# ─── Engine (created once) ────────────────────────────────
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,        # test connection before using
    pool_recycle=3600,         # recycle connections every hour
    echo=False,                # set True to see SQL queries
)

# ─── Session factory ──────────────────────────────────────
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# ─── Context manager for safe sessions ───────────────────
@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Use this everywhere you need a DB session:

        with get_db_session() as session:
            session.execute(...)
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()


# ─── FastAPI dependency ───────────────────────────────────
def get_db() -> Generator[Session, None, None]:
    """
    Use this in FastAPI route dependencies:

        def my_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─── Health check ─────────────────────────────────────────
def check_db_connection() -> bool:
    """Returns True if database is reachable."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


# ─── Convenience query helpers ────────────────────────────
def execute_query(query: str, params: dict = None) -> list:
    """
    Run a raw SQL query and return results as list of dicts.

    Example:
        rows = execute_query(
            "SELECT * FROM raw_ohlcv WHERE symbol = :sym",
            {"sym": "BTCUSDT"}
        )
    """
    with get_db_session() as session:
        result = session.execute(text(query), params or {})
        columns = result.keys()
        return [dict(zip(columns, row)) for row in result.fetchall()]


def execute_write(query: str, params: dict = None) -> int:
    """
    Run an INSERT/UPDATE/DELETE and return rows affected.
    """
    with get_db_session() as session:
        result = session.execute(text(query), params or {})
        return result.rowcount
