"""
Load full 365-day history for ALL symbols
Run ONCE to populate the database
Takes about 5-10 minutes
"""
import sys, os, logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)

from src.ingestion.historical_loader import HistoricalLoader

loader = HistoricalLoader()
loader.load_all_symbols(interval="1h", lookback_days=365)
loader.print_status()
