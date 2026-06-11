import pandas as pd
import numpy as np
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
DATA_DIR     = Path(__file__).resolve().parents[2] / "data" / "raw"
FEATURE_DIR  = Path(__file__).resolve().parents[2] / "data" / "features"
FEATURE_DIR.mkdir(parents=True, exist_ok=True)

SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "SOLUSDT"]
LAG_WINDOWS    = [1, 2, 3, 6, 12, 24]   # hours  (from ACF/PACF analysis)
ROLLING_WINDOWS = [6, 12, 24]            # hours

# ── Load all symbols ───────────────────────────────────────────────────────
def load_all(symbols):
    frames = {}
    for sym in symbols:
        f = DATA_DIR / f"{sym}_1h.csv"
        df = pd.read_csv(f, parse_dates=["timestamp"]).set_index("timestamp")
        df["return"] = df["close"].pct_change()
        frames[sym] = df
    return frames

# ── Build features for one symbol ─────────────────────────────────────────
def build_symbol_features(sym, df, frames):
    feat = pd.DataFrame(index=df.index)
    feat["symbol"]  = sym
    feat["close"]   = df["close"]
    feat["return"]  = df["return"]
    feat["volume"]  = df["volume"]

    # ── Lag features (AR terms) ──────────────────────────────────────────
    for lag in LAG_WINDOWS:
        feat[f"lag_{lag}"] = df["return"].shift(lag)

    # ── Rolling statistics ───────────────────────────────────────────────
    for w in ROLLING_WINDOWS:
        feat[f"roll_mean_{w}h"]  = df["return"].shift(1).rolling(w).mean()
        feat[f"roll_std_{w}h"]   = df["return"].shift(1).rolling(w).std()
        feat[f"roll_min_{w}h"]   = df["return"].shift(1).rolling(w).min()
        feat[f"roll_max_{w}h"]   = df["return"].shift(1).rolling(w).max()

    # ── Volume features ──────────────────────────────────────────────────
    feat["vol_lag1"]       = df["volume"].shift(1)
    feat["vol_roll_mean24"] = df["volume"].shift(1).rolling(24).mean()

    # ── Cross-symbol spread & correlation ────────────────────────────────
    btc_ret = frames["BTCUSDT"]["return"]
    if sym != "BTCUSDT":
        feat["spread_vs_btc"]    = df["return"] - btc_ret
        feat["roll_corr_btc_24h"] = (
            df["return"].shift(1)
            .rolling(24)
            .corr(btc_ret.shift(1))
        )

    eth_ret = frames["ETHUSDT"]["return"]
    if sym not in ("BTCUSDT", "ETHUSDT"):
        feat["roll_corr_eth_24h"] = (
            df["return"].shift(1)
            .rolling(24)
            .corr(eth_ret.shift(1))
        )

    # ── Time features ────────────────────────────────────────────────────
    feat["hour"]        = feat.index.hour
    feat["dow"]         = feat.index.dayofweek
    feat["hour_sin"]    = np.sin(2 * np.pi * feat["hour"] / 24)
    feat["hour_cos"]    = np.cos(2 * np.pi * feat["hour"] / 24)
    feat["dow_sin"]     = np.sin(2 * np.pi * feat["dow"]  / 7)
    feat["dow_cos"]     = np.cos(2 * np.pi * feat["dow"]  / 7)

    # ── Target: next-hour return ─────────────────────────────────────────
    feat["target_return_1h"] = df["return"].shift(-1)

    return feat

# ── Main ───────────────────────────────────────────────────────────────────
def main():
    print("=" * 50)
    print("  LIORA — Feature Engineering")
    print("=" * 50)

    frames = load_all(SYMBOLS)
    all_features = []

    for sym in SYMBOLS:
        print(f"\n  Building features for {sym} ...")
        feat = build_symbol_features(sym, frames[sym], frames)
        feat.dropna(inplace=True)
        out = FEATURE_DIR / f"{sym}_features.csv"
        feat.to_csv(out)
        print(f"  ✅ {sym}: {feat.shape[0]} rows × {feat.shape[1]} cols → {out.name}")
        all_features.append(feat.reset_index())

    # combined file
    combined = pd.concat(all_features, ignore_index=True)
    combined.to_csv(FEATURE_DIR / "all_features.csv", index=False)
    print(f"\n  ✅ Combined dataset: {combined.shape}")
    print("\n  Feature columns:")
    for c in combined.columns:
        print(f"    {c}")

if __name__ == "__main__":
    main()
