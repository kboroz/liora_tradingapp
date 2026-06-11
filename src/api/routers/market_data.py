from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from src.api.database import get_db

router = APIRouter()

class OHLCVIn(BaseModel):
    symbol: str
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

class AssetIn(BaseModel):
    symbol: str
    name: Optional[str] = None
    asset_type: Optional[str] = "crypto"

@router.post("/assets")
async def create_asset(asset: AssetIn, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("""
            INSERT INTO assets (symbol, name, asset_type)
            VALUES (:symbol, :name, :asset_type)
            ON CONFLICT (symbol) DO UPDATE SET name=EXCLUDED.name
            RETURNING id, symbol, name, asset_type
        """),
        asset.model_dump()
    )
    await db.commit()
    row = result.fetchone()
    return {"id": row.id, "symbol": row.symbol, "name": row.name, "asset_type": row.asset_type}

@router.post("/ohlcv")
async def ingest_ohlcv(data: OHLCVIn, db: AsyncSession = Depends(get_db)):
    # Get or create asset
    result = await db.execute(
        text("SELECT id FROM assets WHERE symbol = :symbol"),
        {"symbol": data.symbol}
    )
    asset = result.fetchone()
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {data.symbol} not found. Create it first.")

    await db.execute(
        text("""
            INSERT INTO ohlcv (time, asset_id, open, high, low, close, volume)
            VALUES (:time, :asset_id, :open, :high, :low, :close, :volume)
            ON CONFLICT DO NOTHING
        """),
        {
            "time": data.time,
            "asset_id": asset.id,
            "open": data.open,
            "high": data.high,
            "low": data.low,
            "close": data.close,
            "volume": data.volume
        }
    )
    await db.commit()
    return {"status": "ok", "symbol": data.symbol, "time": data.time}

@router.get("/ohlcv/{symbol}")
async def get_ohlcv(
    symbol: str,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        text("""
            SELECT o.time, o.open, o.high, o.low, o.close, o.volume
            FROM ohlcv o
            JOIN assets a ON a.id = o.asset_id
            WHERE a.symbol = :symbol
            ORDER BY o.time DESC
            LIMIT :limit
        """),
        {"symbol": symbol, "limit": limit}
    )
    rows = result.fetchall()
    return [
        {"time": r.time, "open": r.open, "high": r.high,
         "low": r.low, "close": r.close, "volume": r.volume}
        for r in rows
    ]
