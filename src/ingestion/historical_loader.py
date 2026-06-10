"""
Orchestrates downloading and saving historical data
for all configured symbols
"""

import logging
from datetime import datetime, timezone, timedelta

from config.symbols import SYMBOLS, DEFAULT_INTERVAL, DEFAULT_LOOKBACK_DAYS
from src.ingestion.binance_client import BinanceClient
from src.ingestion.data_saver import DataSaver

logger = logging.getLogger(__name__)


class HistoricalLoader:
    """
    Downloads historical OHLCV data for all symbols
    and saves to PostgreSQL.

    Smart: only downloads missing data (checks last saved timestamp).
    """

    def __init__(self):
        self.client = BinanceClient()
        self.saver  = DataSaver()

    # ─── Load one symbol ──────────────────────────────────
    def load_symbol(
        self,
        symbol:        str,
        interval:      str = DEFAULT_INTERVAL,
        lookback_days: int = DEFAULT_LOOKBACK_DAYS,
        force_reload:  bool = False,
    ) -> int:
        """
        Download and save historical data for one symbol.

        If data already exists and force_reload=False,
        only downloads missing (new) candles.

        Returns number of new rows inserted.
        """
        logger.info(f"Loading {symbol}...")

        # Check what we already have
        if not force_reload:
            last_saved = self.saver.get_last_saved_time(symbol)
            if last_saved:
                # Ensure both datetimes are offset-aware (UTC)
                now_utc = datetime.now(timezone.utc)
                last_saved_utc = last_saved if last_saved.tzinfo else last_saved.replace(tzinfo=timezone.utc)
                days_missing = (now_utc - last_saved_utc).days
                logger.info(f"  Last saved: {last_saved_utc} ({days_missing} days ago)")
                lookback_days = min(days_missing + 1, lookback_days)

        logger.info(f"  Fetching full history: {symbol} | {interval} | {lookback_days} days")

        # Fetch from Binance
        df = self.client.fetch_full_history(
            symbol=symbol,
            interval=interval,
            lookback_days=lookback_days,
        )

        if df.empty:
            logger.warning(f"  No data fetched for {symbol}")
            return 0

        # Save to database
        inserted = self.saver.save_ohlcv(df)
        total    = self.saver.count_rows(symbol)

        logger.info(f"  Inserted: {inserted} | Total in DB: {total}")
        return inserted

    # ─── Load all symbols ─────────────────────────────────
    def load_all_symbols(
        self,
        interval:      str  = DEFAULT_INTERVAL,
        lookback_days: int  = DEFAULT_LOOKBACK_DAYS,
        force_reload:  bool = False,
    ) -> dict:
        """
        Download and save historical data for ALL configured symbols.

        Returns dict with results per symbol:
            {"BTCUSDT": 8760, "ETHUSDT": 8760, ...}
        """
        results = {}

        logger.info("=" * 50)
        logger.info(f"Loading all symbols | interval={interval} | days={lookback_days}")
        logger.info("=" * 50)

        for symbol in SYMBOLS:
            try:
                inserted = self.load_symbol(
                    symbol=symbol,
                    interval=interval,
                    lookback_days=lookback_days,
                    force_reload=force_reload,
                )
                results[symbol] = inserted

            except Exception as e:
                logger.error(f"Failed to load {symbol}: {e}", exc_info=True)
                results[symbol] = 0

        # Summary
        logger.info("\n─── Summary ──────────────────────")
        for symbol, count in results.items():
            total = self.saver.count_rows(symbol)
            logger.info(f"  {symbol:12} | new={count:5} | total={total:6}")

        return results

    # ─── Print status ─────────────────────────────────────
    def print_status(self):
        """Print current data status for all symbols."""
        print("\n─── Data Status ──────────────────────────")
        print(f"  {'Symbol':<12} {'Rows':>8} {'Last Candle':<25}")
        print("  " + "-" * 47)

        for symbol in SYMBOLS:
            total     = self.saver.count_rows(symbol)
            last_time = self.saver.get_last_saved_time(symbol)
            last_str  = str(last_time)[:19] if last_time else "No data"
            print(f"  {symbol:<12} {total:>8} {last_str:<25}")

        print()
