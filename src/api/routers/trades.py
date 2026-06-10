from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
from src.api.database import get_db

router = APIRouter()

class TradeIn(BaseModel):
    symbol: str
    side: str  # buy/sell
    quantity: float
    price: float
    strategy: Optional[str] = None
    pnl: Optional[float] = None

@router.post("/")
async def create_trade(trade: TradeIn, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT id FROM assets WHERE symbol = :symbol"),
        {"symbol": trade.symbol}
    )
    asset = result.fetchone()
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {trade.symbol} not found")

    result = await db.execute(
        text("""
            INSERT INTO trades (asset_id, side, quantity, price, strategy, pnl)
            VALUES (:asset_id, :side, :quantity, :price, :strategy, :pnl)
            RETURNING id, executed_at
        """),
        {
            "asset_id": asset.id,
            "side": trade.side,
            "quantity": trade.quantity,
            "price": trade.price,
            "strategy": trade.strategy,
            "pnl": trade.pnl
        }
    )
    await db.commit()
    row = result.fetchone()
    return {"id": row.id, "executed_at": row.executed_at, **trade.model_dump()}

@router.get("/")
async def get_trades(limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("""
            SELECT t.id, a.symbol, t.side, t.quantity, t.price,
                   t.strategy, t.pnl, t.executed_at
            FROM trades t JOIN assets a ON a.id = t.asset_id
            ORDER BY t.executed_at DESC LIMIT :limit
        """),
        {"limit": limit}
    )
    rows = result.fetchall()
    return [dict(r._mapping) for r in rows]
