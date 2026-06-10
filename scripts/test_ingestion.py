"""
Test Binance data ingestion
Run with: python scripts/test_ingestion.py
"""

import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup logging so we can see what's happening
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)

from src.ingestion.binance_client import BinanceClient
from src.ingestion.historical_loader import HistoricalLoader
from src.utils.redis_client import get_latest_price


def test_binance_api():
    print("\n─── Testing Binance API ──────────────────")
    client = BinanceClient()

    # Test single price fetch
    price = client.get_current_price("BTCUSDT")
    print(f"  ✅ BTC Price: ${price:,.2f}")

    # Test small kline fetch (just 10 candles)
    df = client.fetch_klines("BTCUSDT", interval="1h", limit=10)
    print(f"  ✅ Fetched {len(df)} candles")
    print(f"  Latest candle: {df['open_time'].iloc[-1]}")
    return True


def test_historical_load():
    print("\n─── Testing Historical Load (BTCUSDT only) ───")
    loader = HistoricalLoader()

    # Load just 7 days for testing (faster)
    inserted = loader.load_symbol(
        symbol="BTCUSDT",
        interval="1h",
        lookback_days=7,
    )
    print(f"  ✅ Inserted {inserted} candles")
    loader.print_status()
    return True


if __name__ == "__main__":
    print("=" * 50)
    print("  LIORA TradingApp — Ingestion Tests")
    print("=" * 50)

    api_ok  = test_binance_api()
    load_ok = test_historical_load()

    print("\n─── Summary ──────────────────────────────")
    print(f"  Binance API    : {'✅ OK' if api_ok  else '❌ FAILED'}")
    print(f"  Historical Load: {'✅ OK' if load_ok else '❌ FAILED'}")
    print("=" * 50)
