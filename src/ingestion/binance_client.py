"""
Binance REST API client for LIORA TradingApp
Handles historical OHLCV data download
"""

import time
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import requests
import pandas as pd

from config.settings import settings
from config.symbols import SYMBOLS, DEFAULT_INTERVAL, DEFAULT_LOOKBACK_DAYS

logger = logging.getLogger(__name__)


class BinanceClient:
    """
    Fetches historical OHLCV kline data from Binance REST API.
    No API key needed for public market data.
    """

    BASE_URL    = "https://api.binance.com"
    MAX_CANDLES = 1000   # Binance max per request

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "X-MBX-APIKEY": settings.BINANCE_API_KEY,
        })

    # ─── Fetch klines (OHLCV) ─────────────────────────────
    def fetch_klines(
        self,
        symbol:    str,
        interval:  str = DEFAULT_INTERVAL,
        start_time: Optional[datetime] = None,
        end_time:   Optional[datetime] = None,
        limit:      int = MAX_CANDLES,
    ) -> pd.DataFrame:
        params = {
            "symbol":   symbol,
            "interval": interval,
            "limit":    limit,
        }

        if start_time:
            params["startTime"] = int(start_time.timestamp() * 1000)
        if end_time:
            params["endTime"] = int(end_time.timestamp() * 1000)

        try:
            response = self.session.get(
                f"{self.BASE_URL}/api/v3/klines",
                params=params,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            if not data:
                logger.warning(f"No data returned for {symbol}")
                return pd.DataFrame()

            return self._parse_klines(data, symbol)

        except requests.RequestException as e:
            logger.error(f"Binance API error for {symbol}: {e}")
            raise

    # ─── Parse raw klines into DataFrame ──────────────────
    def _parse_klines(self, raw: list, symbol: str) -> pd.DataFrame:
        columns = [
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_volume", "trades",
            "taker_buy_base", "taker_buy_quote", "ignore"
        ]

        df = pd.DataFrame(raw, columns=columns)
        df.drop(columns=["ignore"], inplace=True)

        df["open_time"]  = pd.to_datetime(df["open_time"],  unit="ms", utc=True)
        df["close_time"] = pd.to_datetime(df["close_time"], unit="ms", utc=True)

        for col in ["open", "high", "low", "close", "volume",
                    "quote_volume", "taker_buy_base", "taker_buy_quote"]:
            df[col] = df[col].astype(float)

        df["trades"] = df["trades"].astype(int)
        df["symbol"] = symbol

        return df.sort_values("open_time").reset_index(drop=True)

    # ─── Fetch full history in batches ────────────────────
    def fetch_full_history(
        self,
        symbol:       str,
        interval:     str = DEFAULT_INTERVAL,
        lookback_days: int = DEFAULT_LOOKBACK_DAYS,
    ) -> pd.DataFrame:
        logger.info(f"Fetching full history: {symbol} | {interval} | {lookback_days} days")

        # Use timezone-aware UTC datetimes throughout
        end_time      = datetime.now(timezone.utc)
        start_time    = end_time - timedelta(days=lookback_days)
        current_start = start_time

        all_frames    = []
        request_count = 0

        while current_start < end_time:
            df = self.fetch_klines(
                symbol=symbol,
                interval=interval,
                start_time=current_start,
                end_time=end_time,
                limit=self.MAX_CANDLES,
            )

            if df.empty:
                break

            all_frames.append(df)
            request_count += 1

            # last_time is tz-aware (utc=True in _parse_klines)
            last_time     = df["open_time"].max()
            current_start = last_time.to_pydatetime() + timedelta(seconds=1)

            logger.debug(f"  Batch {request_count}: {len(df)} candles up to {last_time}")

            time.sleep(0.1)

            if len(df) < self.MAX_CANDLES:
                break

        if not all_frames:
            logger.warning(f"No historical data found for {symbol}")
            return pd.DataFrame()

        result = pd.concat(all_frames, ignore_index=True)
        result = result.drop_duplicates(subset=["open_time"]).sort_values("open_time")

        logger.info(f"  Total candles fetched: {len(result)}")
        return result.reset_index(drop=True)

    # ─── Get current price ────────────────────────────────
    def get_current_price(self, symbol: str) -> Optional[float]:
        try:
            response = self.session.get(
                f"{self.BASE_URL}/api/v3/ticker/price",
                params={"symbol": symbol},
                timeout=10,
            )
            response.raise_for_status()
            return float(response.json()["price"])
        except Exception as e:
            logger.error(f"Failed to get price for {symbol}: {e}")
            return None

    # ─── Get all current prices ───────────────────────────
    def get_all_prices(self) -> dict:
        prices = {}
        for symbol in SYMBOLS:
            price = self.get_current_price(symbol)
            if price:
                prices[symbol] = price
        return prices
