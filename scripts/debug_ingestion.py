import sys, os, logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s | %(levelname)s | %(message)s")

print("\n─── Step 1: Test raw Binance API ─────────────")
import requests
response = requests.get(
    "https://api.binance.com/api/v3/klines",
    params={"symbol": "BTCUSDT", "interval": "1h", "limit": 5},
    timeout=30,
)
print(f"  Status code : {response.status_code}  ✅")

print("\n─── Step 2: Test settings load ───────────────")
from config.settings import settings
print(f"  DATABASE_URL : {settings.DATABASE_URL}")
print(f"  REDIS_HOST   : {settings.REDIS_HOST}")
print(f"  REDIS_PORT   : {settings.REDIS_PORT}")

print("\n─── Step 3: Test DB connection ───────────────")
from src.utils.database import check_db_connection
ok = check_db_connection()
print(f"  DB connected: {ok}")

print("\n─── Step 4: Check tables ─────────────────────")
from src.utils.database import execute_query
rows = execute_query("""
    SELECT table_name FROM information_schema.tables
    WHERE table_schema = 'public'
""")
print(f"  Tables: {[r['table_name'] for r in rows]}")

print("\n─── Step 5: Test BinanceClient ───────────────")
from src.ingestion.binance_client import BinanceClient
client = BinanceClient()
df = client.fetch_klines("BTCUSDT", interval="1h", limit=5)
print(f"  DataFrame shape : {df.shape}")
print(df.head())

print("\n─── Step 6: Test DataSaver ───────────────────")
from src.ingestion.data_saver import DataSaver
saver = DataSaver()
if not df.empty:
    inserted = saver.save_ohlcv(df)
    print(f"  Inserted rows: {inserted}")
    total = saver.count_rows("BTCUSDT")
    print(f"  Total in DB  : {total}")
else:
    print("  ❌ DataFrame empty")
