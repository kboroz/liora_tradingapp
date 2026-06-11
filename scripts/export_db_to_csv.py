"""Export raw_ohlcv from DB to CSV files for feature engineering"""
import pandas as pd
from pathlib import Path
from src.utils.database import execute_query

SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "SOLUSDT"]
OUT_DIR = Path("data/raw")
OUT_DIR.mkdir(parents=True, exist_ok=True)

for sym in SYMBOLS:
    rows = execute_query("""
        SELECT open_time AS timestamp, open, high, low, close, volume
        FROM raw_ohlcv
        WHERE symbol = %s AND interval = '1h'
        ORDER BY open_time ASC
    """, (sym,))
    df = pd.DataFrame(rows)
    out = OUT_DIR / f"{sym}_1h.csv"
    df.to_csv(out, index=False)
    print(f"✅ {sym}: {len(df)} rows → {out}")

