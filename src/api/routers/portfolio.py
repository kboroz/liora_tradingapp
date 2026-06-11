from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from datetime import datetime
from src.api.database import get_db

router = APIRouter()

class SnapshotIn(BaseModel):
    total_value: float
    cash: float
    invested: float
    time: datetime = None

@router.post("/snapshot")  # POST to CREATE a snapshot
async def add_snapshot(snap: SnapshotIn, db: AsyncSession = Depends(get_db)):
    await db.execute(
        text("""
            INSERT INTO portfolio_snapshots (time, total_value, cash, invested)
            VALUES (COALESCE(:time, NOW()), :total_value, :cash, :invested)
        """),
        snap.model_dump()
    )
    await db.commit()
    return {"status": "ok"}

@router.get("/history")  # GET to RETRIEVE history
async def get_history(limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("""
            SELECT time, total_value, cash, invested
            FROM portfolio_snapshots
            ORDER BY time DESC LIMIT :limit
        """),
        {"limit": limit}
    )
    return [dict(r._mapping) for r in result.fetchall()]
