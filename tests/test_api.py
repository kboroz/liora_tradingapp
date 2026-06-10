"""FastAPI Tests"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

class TestHealth:
    def test_health_check(self):
        """Test health endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert "status" in response.json()
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["name"] == "Liora Trading App"

class TestPredictions:
    def test_predict_endpoint(self):
        """Test prediction endpoint"""
        payload = {
            "symbol": "BTCUSDT",
            "features": {
                "volatility_20": 0.02,
                "volume_ratio": 1.1
            }
        }
        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 200
        assert "prediction" in response.json()

class TestData:
    def test_get_data(self):
        """Test get data endpoint"""
        response = client.get("/api/v1/data/BTCUSDT?limit=10")
        assert response.status_code == 200
        assert "symbol" in response.json()

