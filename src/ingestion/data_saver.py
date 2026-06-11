"""
Saves OHLCV data into PostgreSQL (TimescaleDB)
"""

import logging
from datetime import datetime

import pandas as pd
from sqlalchemy import text

from src.utils.database import get_db_session, execute_query

logger = logging.getLogger(__name__)


class DataSaver:

    # ─── Save DataFrame to DB ─────────────────────────────
    def save_ohlcv(self, df: pd.DataFrame) -> int:
        if df.empty:
            return 0

        # Build list of dicts for bulk insert
        rows = []
        for _, row in df.iterrows():
            rows.append({
                "open_time":       row["open_time"].to_pydatetime(),
                "symbol":          row["symbol"],
                "open":            float(row["open"]),
                "high":            float(row["high"]),
                "low":             float(row["low"]),
                "close":           float(row["close"]),
                "volume":          float(row["volume"]),
                "quote_volume":    float(row["quote_volume"]),
                "trades":          int(row["trades"]),
                "taker_buy_base":  float(row["taker_buy_base"]),
                "taker_buy_quote": float(row["taker_buy_quote"]),
            })

        sql = text("""
            INSERT INTO raw_ohlcv (
                open_time, symbol, open, high, low, close,
                volume, quote_volume, trades,
                taker_buy_base, taker_buy_quote
            ) VALUES (
                :open_time, :symbol, :open, :high, :low, :close,
                :volume, :quote_volume, :trades,
                :taker_buy_base, :taker_buy_quote
            )
            ON CONFLICT (open_time, symbol) DO NOTHING
        """)

        symbol = df["symbol"].iloc[0]

        try:
            with get_db_session() as session:
                result = session.execute(sql, rows)
                # rowcount may be -1 for some drivers; use len(rows) as fallback
                inserted = result.rowcount if result.rowcount >= 0 else len(rows)
                session.commit()
        except Exception as e:
            logger.error(f"Bulk insert failed for {symbol}: {e}")
            return 0

        logger.info(f"Saved {inserted} rows for {symbol}")
        return inserted

    # ─── Load OHLCV from DB ───────────────────────────────
    def load_ohlcv(
        self,
        symbol:     str,
        start_date: datetime = None,
        end_date:   datetime = None,
        limit:      int = None,
    ) -> pd.DataFrame:
        query = """
            SELECT
                open_time, symbol, open, high, low, close,
                volume, quote_volume, trades,
                taker_buy_base, taker_buy_quote
            FROM raw_ohlcv
            WHERE symbol = :symbol
        """
        params = {"symbol": symbol}

        if start_date:
            query += " AND open_time >= :start_date"
            params["start_date"] = start_date

        if end_date:
            query += " AND open_time <= :end_date"
            params["end_date"] = end_date

        query += " ORDER BY open_time ASC"

        if limit:
            query += " LIMIT :limit"
            params["limit"] = limit

        rows = execute_query(query, params)

        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(rows)
        df["open_time"] = pd.to_datetime(df["open_time"], utc=True)
        return df

    # ─── Check last saved timestamp ───────────────────────
    def get_last_saved_time(self, symbol: str) -> datetime:
        rows = execute_query("""
            SELECT MAX(open_time) as last_time
            FROM raw_ohlcv
            WHERE symbol = :symbol
        """, {"symbol": symbol})

        if rows and rows[0]["last_time"]:
            return rows[0]["last_time"]
        return None

    # ─── Count rows for a symbol ──────────────────────────
    def count_rows(self, symbol: str) -> int:
        rows = execute_query("""
            SELECT COUNT(*) as total
            FROM raw_ohlcv
            WHERE symbol = :symbol
        """, {"symbol": symbol})

        return rows[0]["total"] if rows else 0
