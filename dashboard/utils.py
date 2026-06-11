# dashboard/utils.py
import pandas as pd
import psycopg2
import os

SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]

def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", 5432),
        dbname=os.getenv("DB_NAME", "trading"),
        user=os.getenv("DB_USER", "trader"),
        password=os.getenv("DB_PASSWORD", "")
    )

def get_ohlcv(symbol: str, limit: int = 200) -> pd.DataFrame:
    try:
        conn = get_conn()
        df = pd.read_sql(
            """
            SELECT open_time, open, high, low, close, volume
            FROM ohlcv
            WHERE symbol = %s
            ORDER BY open_time DESC
            LIMIT %s
            """,
            conn, params=(symbol, limit)
        )
        conn.close()
        return df.sort_values("open_time").reset_index(drop=True)
    except Exception as e:
        return pd.DataFrame()

def get_signals(symbol: str, limit: int = 50) -> pd.DataFrame:
    try:
        conn = get_conn()
        df = pd.read_sql(
            """
            SELECT created_at, symbol, signal, price, confidence
            FROM signals
            WHERE symbol = %s
            ORDER BY created_at DESC
            LIMIT %s
            """,
            conn, params=(symbol, limit)
        )
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()

def get_backtest_results(symbol: str) -> pd.DataFrame:
    try:
        conn = get_conn()
        df = pd.read_sql(
            """
            SELECT entry_time, exit_time, symbol, side, entry_price, exit_price, pnl
            FROM backtest_trades
            WHERE symbol = %s
            ORDER BY exit_time DESC
            """,
            conn, params=(symbol,)
        )
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()
