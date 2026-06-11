# src/analysis/eda.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.stattools import adfuller, ccf
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from sqlalchemy import create_engine
from pathlib import Path
import sys
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from config.settings import settings


# ── Config ──────────────────────────────────────────────
engine    = create_engine(settings.DATABASE_URL)
OUT_DIR   = Path("reports/eda")
SYMBOLS   = ["ETHUSDT", "BNBUSDT", "XRPUSDT", "SOLUSDT", "USDCUSDT"]
LAGS      = 40
# ────────────────────────────────────────────────────────

OUT_DIR.mkdir(parents=True, exist_ok=True)

def load_close_prices() -> pd.DataFrame:
    frames = []
    for sym in SYMBOLS:
        df = pd.read_sql(
            f"SELECT open_time, close FROM raw_ohlcv WHERE symbol='{sym}' ORDER BY open_time",
            engine, parse_dates=["open_time"]
        )
        df = df.set_index("open_time")["close"].rename(sym)
        frames.append(df)
    return pd.concat(frames, axis=1).dropna()

def load_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return np.log(prices / prices.shift(1)).dropna()

# ── 1. Price correlation heatmap ────────────────────────
def plot_price_corr(prices: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 6))
    corr = prices.corr()
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
    ax.set_title("Price Cross-Correlation Heatmap")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "price_correlation.png")
    plt.close(fig)
    print("  ✅ Price correlation heatmap saved")

# ── 2. Returns correlation heatmap ──────────────────────
def plot_returns_corr(returns: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 6))
    corr = returns.corr()
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
    ax.set_title("Log-Returns Cross-Correlation Heatmap")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "returns_correlation.png")
    plt.close(fig)
    print("  ✅ Returns correlation heatmap saved")

# ── 3. Rolling correlation ───────────────────────────────
def plot_rolling_corr(returns: pd.DataFrame, base="ETHUSDT", window=168):
    other = [s for s in SYMBOLS if s != base]
    fig, ax = plt.subplots(figsize=(14, 5))
    for sym in other:
        roll = returns[base].rolling(window).corr(returns[sym])
        ax.plot(roll.index, roll, label=f"{base} vs {sym}")
    ax.axhline(0, color="black", linestyle="--", linewidth=0.8)
    ax.set_title(f"Rolling {window}h Correlation vs {base}")
    ax.set_ylabel("Pearson r")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "rolling_correlation.png")
    plt.close(fig)
    print("  ✅ Rolling correlation plot saved")

# ── 4. ACF / PACF ───────────────────────────────────────
def plot_acf_pacf(returns: pd.DataFrame):
    for sym in SYMBOLS:
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))
        plot_acf(returns[sym].dropna(),  lags=LAGS, ax=axes[0], title=f"{sym} — ACF")
        plot_pacf(returns[sym].dropna(), lags=LAGS, ax=axes[1], title=f"{sym} — PACF")
        fig.tight_layout()
        fig.savefig(OUT_DIR / f"acf_pacf_{sym}.png")
        plt.close(fig)
    print("  ✅ ACF/PACF plots saved for all symbols")

# ── 5. ADF Stationarity Test ────────────────────────────
def run_adf(returns: pd.DataFrame) -> pd.DataFrame:
    results = []
    for sym in SYMBOLS:
        stat, p, _, _, crit, _ = adfuller(returns[sym].dropna())
        results.append({
            "symbol":    sym,
            "adf_stat":  round(stat, 4),
            "p_value":   round(p, 6),
            "stationary": "Yes" if p < 0.05 else "No",
            "crit_1%":   round(crit["1%"], 4),
            "crit_5%":   round(crit["5%"], 4),
        })
    df = pd.DataFrame(results)
    df.to_csv(OUT_DIR / "adf_results.csv", index=False)
    print("  ✅ ADF stationarity results saved")
    print(df.to_string(index=False))
    return df

# ── 6. CCF ──────────────────────────────────────────────
def plot_ccf(returns: pd.DataFrame, base="ETHUSDT"):
    other = [s for s in SYMBOLS if s != base]
    fig, axes = plt.subplots(len(other), 1, figsize=(12, 4 * len(other)))
    for ax, sym in zip(axes, other):
        cc = ccf(returns[base].dropna(), returns[sym].dropna(), unbiased=False)[:LAGS]
        ax.bar(range(len(cc)), cc)
        ax.axhline( 1.96 / np.sqrt(len(returns)), color="red", linestyle="--", label="95% CI")
        ax.axhline(-1.96 / np.sqrt(len(returns)), color="red", linestyle="--")
        ax.set_title(f"CCF: {base} → {sym}")
        ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "ccf_plots.png")
    plt.close(fig)
    print("  ✅ CCF plots saved")

# ── Main ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*50)
    print("  LIORA — EDA: Cross-Correlations & AR Features")
    print("="*50 + "\n")

    prices  = load_close_prices()
    returns = load_returns(prices)

    print(f"  Loaded {len(prices)} rows for {len(SYMBOLS)} symbols\n")

    plot_price_corr(prices)
    plot_returns_corr(returns)
    plot_rolling_corr(returns)
    plot_acf_pacf(returns)
    run_adf(returns)
    plot_ccf(returns)

    print(f"\n  All outputs saved to: {OUT_DIR}/")
    print("="*50)
