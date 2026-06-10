"""Feature Engineering Tests"""

import pytest
import pandas as pd
import numpy as np
from src.features.feature_generator import generate_all_features

class TestFeatureGeneration:
    def test_feature_generation(self):
        """Test feature generation"""
        symbols = ['BTCUSDT', 'ETHUSDT']
        features_dict = generate_all_features(symbols)
        
        assert len(features_dict) == len(symbols)
        for symbol in symbols:
            assert symbol in features_dict
            assert isinstance(features_dict[symbol], pd.DataFrame)

