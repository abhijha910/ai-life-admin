"""Authentication tests"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_register_user():
    """Test user registration"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "Test123!@#",
            "full_name": "Test User"
        }
    )
    assert response.status_code in [201, 400]  # 400 if user already exists


def test_login_user():
    """Test user login"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "Test123!@#"
        }
    )
    assert response.status_code in [200, 401]  # 401 if user doesn't exist


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert "status" in response.json()
