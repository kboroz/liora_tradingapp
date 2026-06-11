import pandas as pd
import numpy as np

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy().sort_values("open_time")

    # Returns
    df["return_1h"] = df["close"].pct_change(1)
    df["return_4h"] = df["close"].pct_change(4)
    df["return_24h"] = df["close"].pct_change(24)

    # Moving Averages
    df["ma_7"] = df["close"].rolling(7).mean()
    df["ma_25"] = df["close"].rolling(25).mean()

    # MA Ratios
    df["ma_7_25_ratio"] = df["ma_7"] / df["ma_25"]

    # Volume
    df["volume_ratio"] = df["volume"] / df["volume"].rolling(24).mean()

    # Target
    df["target"] = (df["close"].shift(-1) > df["close"]).astype(int)

    df.dropna(inplace=True)

    return df
