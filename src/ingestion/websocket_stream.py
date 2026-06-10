"""
Binance WebSocket live price streaming for LIORA TradingApp
Streams real-time kline data and caches to Redis
"""

import json
import logging
import asyncio
import threading
from datetime import datetime
from typing import Callable, Optional

import websockets

from config.symbols import SYMBOLS
from src.utils.redis_client import cache_latest_price

logger = logging.getLogger(__name__)


class BinanceWebSocketStream:
    """
    Connects to Binance WebSocket streams for live kline data.
    Runs in background thread.
    Caches latest prices to Redis automatically.
    """

    WS_BASE = "wss://stream.binance.com:9443/stream"

    def __init__(
        self,
        symbols:   list = None,
        interval:  str  = "1m",
        on_candle: Optional[Callable] = None,
    ):
        self.symbols   = symbols or list(SYMBOLS.keys())
        self.interval  = interval
        self.on_candle = on_candle   # optional callback for each candle
        self._running  = False
        self._thread   = None

    # ─── Build stream URL ─────────────────────────────────
    def _build_stream_url(self) -> str:
        """
        Builds a combined stream URL for all symbols.
        Example: wss://stream.binance.com:9443/stream?streams=btcusdt@kline_1m/ethusdt@kline_1m
        """
        streams = [
            f"{symbol.lower()}@kline_{self.interval}"
            for symbol in self.symbols
        ]
        return f"{self.WS_BASE}?streams={'/'.join(streams)}"

    # ─── Process incoming message ─────────────────────────
    def _process_message(self, raw: str):
        """Parse WebSocket message and cache to Redis."""
        try:
            msg  = json.loads(raw)
            data = msg.get("data", {})

            if data.get("e") != "kline":
                return

            kline  = data["k"]
            symbol = kline["s"]

            candle = {
                "symbol":     symbol,
                "open_time":  datetime.utcfromtimestamp(kline["t"] / 1000).isoformat(),
                "close_time": datetime.utcfromtimestamp(kline["T"] / 1000).isoformat(),
                "open":       float(kline["o"]),
                "high":       float(kline["h"]),
                "low":        float(kline["l"]),
                "close":      float(kline["c"]),
                "volume":     float(kline["v"]),
                "trades":     int(kline["n"]),
                "is_closed":  kline["x"],   # True when candle is complete
            }

            # Always cache latest price to Redis
            cache_latest_price(symbol, {
                "price":     candle["close"],
                "open_time": candle["open_time"],
                "volume":    candle["volume"],
            })

            # Call optional callback if provided
            if self.on_candle:
                self.on_candle(candle)

            logger.debug(
                f"  {symbol} | "
                f"close={candle['close']} | "
                f"closed={candle['is_closed']}"
            )

        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")

    # ─── Async WebSocket loop ─────────────────────────────
    async def _stream_loop(self):
        """Main async WebSocket loop with auto-reconnect."""
        url = self._build_stream_url()
        logger.info(f"Connecting to Binance WebSocket...")
        logger.info(f"  Symbols: {self.symbols}")
        logger.info(f"  Interval: {self.interval}")

        while self._running:
            try:
                async with websockets.connect(
                    url,
                    ping_interval=20,
                    ping_timeout=10,
                ) as ws:
                    logger.info("WebSocket connected ✅")

                    async for message in ws:
                        if not self._running:
                            break
                        self._process_message(message)

            except websockets.ConnectionClosed:
                if self._running:
                    logger.warning("WebSocket disconnected. Reconnecting in 5s...")
                    await asyncio.sleep(5)

            except Exception as e:
                if self._running:
                    logger.error(f"WebSocket error: {e}. Reconnecting in 10s...")
                    await asyncio.sleep(10)

    # ─── Run in background thread ─────────────────────────
    def _run_in_thread(self):
        """Creates event loop and runs WebSocket in background thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._stream_loop())
        loop.close()

    # ─── Start / Stop ─────────────────────────────────────
    def start(self):
        """Start WebSocket streaming in background thread."""
        if self._running:
            logger.warning("Stream already running")
            return

        self._running = True
        self._thread  = threading.Thread(
            target=self._run_in_thread,
            name="BinanceWebSocket",
            daemon=True,
        )
        self._thread.start()
        logger.info("WebSocket stream started in background")

    def stop(self):
        """Stop the WebSocket stream."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=10)
        logger.info("WebSocket stream stopped")

    def is_running(self) -> bool:
        return self._running and self._thread and self._thread.is_alive()
