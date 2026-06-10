"""Model Tests"""

import pytest
import numpy as np
import pandas as pd
from src.models.lstm_model import LSTMModel
from src.models.lightgbm_model import LightGBMModel

class TestLSTMModel:
    @pytest.fixture
    def lstm_model(self):
        return LSTMModel(epochs=2)
    
    @pytest.fixture
    def sample_data(self):
        X = pd.DataFrame(np.random.randn(100, 6), columns=[f'f{i}' for i in range(6)])
        y = pd.Series(np.random.randint(0, 2, 100))
        return X, y
    
    def test_model_build(self, lstm_model):
        lstm_model.build_model()
        assert lstm_model.model is not None
    
    def test_model_fit(self, lstm_model, sample_data):
        X, y = sample_data
        lstm_model.fit(X, y, epochs=1, verbose=0)
        assert lstm_model.history is not None
    
    def test_model_predict(self, lstm_model, sample_data):
        X, y = sample_data
        lstm_model.fit(X, y, epochs=1, verbose=0)
        predictions = lstm_model.predict(X)
        assert len(predictions) > 0
        assert all(p in [0, 1] for p in predictions)

