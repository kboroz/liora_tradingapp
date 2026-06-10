"""API Tests"""
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health():
    """Test basic health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "components" in data
    assert data["components"]["database"] == "✅ OK"
    assert data["components"]["redis"] == "✅ OK"
    assert data["components"]["api"] == "✅ OK"

def test_health_routes_exist():
    """Test that health check routes exist"""
    response = client.get("/health/db")
    # Should not be 404 (route exists)
    assert response.status_code != 404
    
    response = client.get("/health/redis")
    assert response.status_code != 404
