"""
LIORA - Run model on all symbols, save signals to DB
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from src.utils.database import execute_query, execute_write

SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "SOLUSDT", "USDCUSDT"]

def make_features(df):
    df = df.copy()
    df["return_1"] = df["close"].pct_change(1)
    df["return_3"] = df["close"].pct_change(3)
    df["return_6"] = df["close"].pct_change(6)
    df["return_12"] = df["close"].pct_change(12)
    df["vol_change"] = df["volume"].pct_change(1)
    df["hl_range"] = (df["high"] - df["low"]) / df["close"]
    df["target"] = (df["close"].shift(-1) > df["close"]).astype(int)
    df.dropna(inplace=True)
    return df

FEATURES = ["return_1","return_3","return_6","return_12","vol_change","hl_range"]

def run(symbol):
    print(f"\n{'─'*50}")
    print(f"  {symbol}")
    rows = execute_query("""
        SELECT open_time, open, high, low, close, volume
        FROM raw_ohlcv
        WHERE symbol = :symbol
        ORDER BY open_time ASC
    """, {"symbol": symbol})

    df = pd.DataFrame(rows, columns=["open_time","open","high","low","close","volume"])
    for c in ["open","high","low","close","volume"]:
        df[c] = df[c].astype(float)

    df = make_features(df)

    split = int(len(df) * 0.8)
    train, test = df.iloc[:split], df.iloc[split:]

    X_train, y_train = train[FEATURES], train["target"]
    X_test,  y_test  = test[FEATURES],  test["target"]

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    probs = model.predict_proba(X_test)[:,1]
    preds = (probs > 0.5).astype(int)

    test = test.copy()
    test["pred"] = preds
    test["ret"] = test["close"].pct_change().shift(-1)
    test["strat"] = test["ret"] * (test["pred"] * 2 - 1)
    cumret = (1 + test["strat"]).cumprod()
    bh = (test["close"].iloc[-1] / test["close"].iloc[0] - 1) * 100
    strat_ret = (cumret.iloc[-1] - 1) * 100
    sharpe = test["strat"].mean() / test["strat"].std() * np.sqrt(8760)
    drawdown = ((cumret / cumret.cummax()) - 1).min() * 100
    winrate = (test["strat"] > 0).mean() * 100

    print(f"  Buy & Hold : {bh:.2f}%")
    print(f"  Strategy   : {strat_ret:.2f}%")
    print(f"  Sharpe     : {sharpe:.2f}")
    print(f"  Drawdown   : {drawdown:.2f}%")
    print(f"  Win rate   : {winrate:.1f}%")

    execute_write("DELETE FROM signals WHERE symbol = :symbol", {"symbol": symbol})
    for i, (_, row) in enumerate(test.iterrows()):
        execute_write("""
            INSERT INTO signals (symbol, open_time, signal, confidence)
            VALUES (:symbol, :open_time, :signal, :confidence)
        """, {
            "symbol":    symbol,
            "open_time": row["open_time"],
            "signal":    "UP" if preds[i] == 1 else "DOWN",
            "confidence": float(probs[i])
        })

    print(f"  Signals saved: {len(test)}")

if __name__ == "__main__":
    for s in SYMBOLS:
        run(s)
    print("\n✅ Done")
