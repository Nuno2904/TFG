"""
🔧 PYTEST CONFIGURATION AND FIXTURES

Provides test client, database sessions, and authentication fixtures
for comprehensive API testing.
"""

import pytest
import sys
from pathlib import Path
import uuid

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from main import app
from app.db.base import Base
from app.db.session import get_db


# ═══════════════════════════════════════════════════════════════════════════
# DATABASE FIXTURES
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="session")
def test_db():
    """Create test database"""
    # Use in-memory SQLite for testing
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    yield SessionLocal()
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def client(test_db):
    """Create test client"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    return TestClient(app)


# ═══════════════════════════════════════════════════════════════════════════
# AUTHENTICATION FIXTURES
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="session")
def test_user_data():
    """Test user registration data - with unique email"""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "email": f"testuser_{unique_id}@tfg.local",
        "password": "TestPassword123!"
    }


@pytest.fixture(scope="session")
def auth_headers(client, test_user_data):
    """Create auth headers for test user"""
    # Register user (use /usuarios endpoint)
    client.post("/api/v1/usuarios", json=test_user_data)
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
    )
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="session")
def auth_headers_user2(client):
    """Create auth headers for second test user"""
    unique_id = str(uuid.uuid4())[:8]
    user2_data = {
        "email": f"testuser2_{unique_id}@tfg.local",
        "password": "TestPassword123!"
    }
    
    # Register user (use /usuarios endpoint)
    client.post("/api/v1/usuarios", json=user2_data)
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": user2_data["email"],
            "password": user2_data["password"]
        }
    )
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ═══════════════════════════════════════════════════════════════════════════
# USER FIXTURES
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="session")
def test_user_id(client, auth_headers):
    """Get ID of test user"""
    response = client.get("/api/v1/usuarios/me", headers=auth_headers)
    return response.json()["id"]


# ═══════════════════════════════════════════════════════════════════════════
# FILE FIXTURES
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="session")
def test_file_id(client, auth_headers, test_dataset_csv):
    """Create and return test file ID"""
    response = client.post(
        "/api/v1/files/upload",
        files={"file": ("test_data.csv", test_dataset_csv, "text/csv")},
        headers=auth_headers
    )
    return response.json()["id"]


# ═══════════════════════════════════════════════════════════════════════════
# DATASET FIXTURES
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="session")
def test_dataset_id():
    """Return ID of a test dataset (should exist in test DB)"""
    # This assumes a dataset is created during fixture setup
    return 1


@pytest.fixture(scope="session")
def test_dataset_name():
    """Return name of a test dataset"""
    return "test_dataset"


# ═══════════════════════════════════════════════════════════════════════════
# ML MODEL FIXTURES
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="session")
def test_model_id(client, auth_headers, test_dataset_id):
    """Create and return test model ID"""
    response = client.post(
        "/api/v1/models",
        json={
            "name": "test_model_general",
            "model_type": "prophet",
            "dataset_id": test_dataset_id
        },
        headers=auth_headers
    )
    if response.status_code == 201:
        return response.json()["id"]
    return 1


@pytest.fixture(scope="session")
def test_prophet_model_id(client, auth_headers, test_dataset_id):
    """Create and return test Prophet model ID"""
    response = client.post(
        "/api/v1/models",
        json={
            "name": "test_prophet_model",
            "model_type": "prophet",
            "dataset_id": test_dataset_id
        },
        headers=auth_headers
    )
    if response.status_code == 201:
        return response.json()["id"]
    return 1


@pytest.fixture(scope="session")
def test_arima_model_id(client, auth_headers, test_dataset_id):
    """Create and return test ARIMA model ID"""
    response = client.post(
        "/api/v1/models",
        json={
            "name": "test_arima_model",
            "model_type": "arima",
            "dataset_id": test_dataset_id
        },
        headers=auth_headers
    )
    if response.status_code == 201:
        return response.json()["id"]
    return 2


# ═══════════════════════════════════════════════════════════════════════════
# PYTEST HOOKS AND CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════


def pytest_configure(config):
    """Pytest configuration hook"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "endpoints: mark test as endpoint test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    for item in items:
        # Add markers
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        if "test_endpoints" in item.nodeid:
            item.add_marker(pytest.mark.endpoints)
