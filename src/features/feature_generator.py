"""
Feature engineering pipeline for trading ML models
Optimized set of features for price prediction
"""
import pandas as pd
import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class FeatureGenerator:
    """Generate optimized technical features"""
    
    def __init__(self):
        self.required_columns = ['open', 'high', 'low', 'close', 'volume']
    
    def generate_features(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Generate optimized features for a symbol
        
        Args:
            df: DataFrame with OHLCV data sorted by open_time
            symbol: Trading pair symbol
            
        Returns:
            DataFrame with features added
        """
        df = df.copy().reset_index(drop=True)
        
        # Feature engineering
        df = self._add_returns(df)
        df = self._add_volatility(df)
        df = self._add_volume_features(df)
        df = self._add_trend_features(df)
        
        # Target: Next hour close vs current close (binary classification)
        df['next_close'] = df['close'].shift(-1)
        df['target'] = (df['next_close'] > df['close']).astype(int)  # 1: up, 0: down
        
        logger.info(f"Generated features for {symbol}: {df.shape}")
        
        return df
    
    def _add_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add return features
        Returns: 1h, 4h, 24h percentage changes
        """
        df['return_1h'] = df['close'].pct_change() * 100
        df['return_4h'] = df['close'].pct_change(4) * 100
        df['return_24h'] = df['close'].pct_change(24) * 100
        
        return df
    
    def _add_volatility(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add volatility features
        - Rolling standard deviation (20-period)
        - High-Low range as % of close
        """
        # Rolling volatility (std of 1h returns)
        df['volatility_20'] = df['return_1h'].rolling(window=20, min_periods=1).std()
        
        # High-Low range as percentage
        df['hl_range_pct'] = ((df['high'] - df['low']) / df['close']) * 100
        
        return df
    
    def _add_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add volume-based features
        - Volume ratio (current vs 20-period MA)
        - Relative Volume (RVOL): current vs average
        """
        # Volume SMA (20-period)
        df['volume_sma_20'] = df['volume'].rolling(window=20, min_periods=1).mean()
        
        # Volume ratio
        df['volume_ratio'] = df['volume'] / (df['volume_sma_20'] + 1e-8)
        
        # Relative Volume (RVOL) - volume compared to average
        df['rvol'] = df['volume'] / (df['volume_sma_20'] + 1e-8)
        
        return df
    
    def _add_trend_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add trend features
        - Consecutive ups/downs count
        - Higher Highs (HH) and Lower Lows (LL) in 10-period window
        """
        # Price change direction
        df['price_change'] = df['close'].diff()
        df['is_up'] = (df['price_change'] > 0).astype(int)
        
        # Consecutive ups/downs
        # Count consecutive 1s or 0s
        change_groups = (df['is_up'] != df['is_up'].shift()).cumsum()
        df['consecutive_count'] = df.groupby(change_groups).cumcount() + 1
        df['consecutive_ups'] = df['consecutive_count'] * df['is_up']
        df['consecutive_downs'] = df['consecutive_count'] * (1 - df['is_up'])
        
        # Higher Highs and Lower Lows (10-period lookback)
        df['hh_10'] = df['high'].rolling(window=10, min_periods=1).max()
        df['ll_10'] = df['low'].rolling(window=10, min_periods=1).min()
        
        # Is current high a new 10-period high?
        df['is_higher_high'] = (df['high'] >= df['hh_10']).astype(int)
        
        # Is current low a new 10-period low?
        df['is_lower_low'] = (df['low'] <= df['ll_10']).astype(int)
        
        return df


def generate_all_features(symbols: List[str]) -> Dict[str, pd.DataFrame]:
    """Generate features for all symbols"""
    from src.utils.database import execute_query
    
    generator = FeatureGenerator()
    features_dict = {}
    
    for symbol in symbols:
        logger.info(f"Generating features for {symbol}...")
        
        # Load data - use :symbol syntax for SQLAlchemy
        result = execute_query("""
            SELECT symbol, open_time, open, high, low, close, volume
            FROM raw_ohlcv
            WHERE symbol = :symbol
            ORDER BY open_time
        """, {"symbol": symbol})
        
        df = pd.DataFrame(result)
        df['open_time'] = pd.to_datetime(df['open_time'])
        df = df.astype({'open': float, 'high': float, 'low': float, 'close': float, 'volume': float})
        
        # Generate features
        df_features = generator.generate_features(df, symbol)
        features_dict[symbol] = df_features
    
    return features_dict
