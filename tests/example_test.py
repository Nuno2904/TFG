"""
🧪 Example Test File

Shows how to structure tests for the application.
Run with: pytest
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from app.db.base import Base
from app.db.session import get_db


# 🗄️ Set up test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_db.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# ═══════════════════════════════════════════════════════════════════════════
# 🧪 Health Check Tests
# ═══════════════════════════════════════════════════════════════════════════


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "✅ healthy"


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data


# ═══════════════════════════════════════════════════════════════════════════
# 👤 User Registration Tests
# ═══════════════════════════════════════════════════════════════════════════


def test_register_user():
    """Test user registration."""
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
    }
    response = client.post("/api/v1/usuarios", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "password" not in data  # Password should not be returned


def test_register_duplicate_email():
    """Test registering with duplicate email."""
    user_data = {
        "email": "duplicate@example.com",
        "password": "testpassword123",
    }
    
    # First registration should succeed
    response1 = client.post("/api/v1/usuarios", json=user_data)
    assert response1.status_code == 201
    
    # Second registration with same email should fail
    response2 = client.post("/api/v1/usuarios", json=user_data)
    assert response2.status_code == 400


# ═══════════════════════════════════════════════════════════════════════════
# 🔐 Authentication Tests
# ═══════════════════════════════════════════════════════════════════════════


def test_login():
    """Test user login."""
    # First, register a user
    user_data = {
        "email": "login@example.com",
        "password": "testpassword123",
    }
    client.post("/api/v1/usuarios", json=user_data)
    
    # Then, try to login
    response = client.post(
        "/api/v1/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials():
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "nonexistent@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════
# 👤 User Profile Tests
# ═══════════════════════════════════════════════════════════════════════════


def test_get_current_user():
    """Test getting current authenticated user."""
    # Register and login
    user_data = {
        "email": "profile@example.com",
        "password": "testpassword123",
    }
    client.post("/api/v1/usuarios", json=user_data)
    
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]},
    )
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/api/v1/usuarios/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]


def test_get_current_user_no_token():
    """Test getting current user without token."""
    response = client.get("/api/v1/usuarios/me")
    assert response.status_code == 403  # Forbidden
