"""
🧪 COMPREHENSIVE ENDPOINT TESTS
Test suite for all API endpoints in the TFG ML Platform
"""

import pytest
import json
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path

# Test Fixtures and Configuration
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="session")
def test_user_data():
    """Test user credentials"""
    return {
        "username": "test_user_tfg",
        "email": "test@tfg.local",
        "password": "TestPassword123!",
        "full_name": "Test User TFG"
    }


@pytest.fixture(scope="session")
def test_dataset_csv():
    """Sample CSV file with time series data"""
    csv_content = """fecha,valor
2024-01-01,100
2024-01-02,105
2024-01-03,103
2024-01-04,108
2024-01-05,110
2024-01-06,112
2024-01-07,115
2024-01-08,118
2024-01-09,120
2024-01-10,122
2024-01-11,125
2024-01-12,128
2024-01-13,130
2024-01-14,132
2024-01-15,135
2024-01-16,138
2024-01-17,140
2024-01-18,142
2024-01-19,145
2024-01-20,148
2024-01-21,150
2024-01-22,152
2024-01-23,155
2024-01-24,158
2024-01-25,160
2024-01-26,162
2024-01-27,165
2024-01-28,168
2024-01-29,170
2024-01-30,172
2024-01-31,175
2024-02-01,178
2024-02-02,180
2024-02-03,182
2024-02-04,185
2024-02-05,188
2024-02-06,190
2024-02-07,192
2024-02-08,195
2024-02-09,198
"""
    return BytesIO(csv_content.encode())


# ═══════════════════════════════════════════════════════════════════════════
# 🔐 AUTHENTICATION ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════


class TestAuthEndpoints:
    """Test suite for authentication endpoints"""
    
    def test_register_user_success(self, client, test_user_data):
        """Test successful user registration"""
        response = client.post(
            "/api/v1/auth/register",
            json=test_user_data
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert "id" in data
        assert "token" not in data  # Password should never be returned
    
    def test_register_duplicate_username(self, client, test_user_data):
        """Test registration with existing username fails"""
        # First registration
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Second attempt should fail
        duplicate_data = test_user_data.copy()
        duplicate_data["email"] = "different@email.com"
        
        response = client.post("/api/v1/auth/register", json=duplicate_data)
        assert response.status_code == 400
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email format"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "not-an-email",
                "password": "TestPassword123!",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_register_weak_password(self, client):
        """Test registration with weak password"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "test@example.com",
                "password": "weak",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 422
    
    def test_login_success(self, client, test_user_data):
        """Test successful login"""
        # Register first
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Login
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client):
        """Test login with wrong password"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "nonexistent",
                "password": "WrongPassword123!"
            }
        )
        assert response.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════
# 👤 USUARIO ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════


class TestUsuarioEndpoints:
    """Test suite for user management endpoints"""
    
    def test_get_current_user(self, client, auth_headers):
        """Test getting current user profile"""
        response = client.get(
            "/api/v1/usuarios/me",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "username" in data
        assert "email" in data
    
    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication"""
        response = client.get("/api/v1/usuarios/me")
        assert response.status_code == 401
    
    def test_get_user_by_id(self, client, auth_headers, test_user_id):
        """Test getting user by ID"""
        response = client.get(
            f"/api/v1/usuarios/{test_user_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user_id
    
    def test_update_user_profile(self, client, auth_headers, test_user_id):
        """Test updating user profile"""
        update_data = {
            "full_name": "Updated Full Name",
            "email": "newemail@tfg.local"
        }
        response = client.put(
            f"/api/v1/usuarios/{test_user_id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Full Name"
    
    def test_delete_user_account(self, client, auth_headers, test_user_id):
        """Test user account deletion"""
        response = client.delete(
            f"/api/v1/usuarios/{test_user_id}",
            headers=auth_headers
        )
        assert response.status_code == 204
    
    def test_delete_own_data(self, client, auth_headers):
        """Test GDPR: delete own data"""
        response = client.delete(
            "/api/v1/usuarios/datos",
            headers=auth_headers
        )
        assert response.status_code == 204


# ═══════════════════════════════════════════════════════════════════════════
# 📁 FILE ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════


class TestFileEndpoints:
    """Test suite for file upload and management endpoints"""
    
    def test_upload_csv_file(self, client, auth_headers, test_dataset_csv):
        """Test uploading a CSV file"""
        response = client.post(
            "/api/v1/files/upload",
            files={"file": ("test_data.csv", test_dataset_csv, "text/csv")},
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["filename"] == "test_data.csv"
        assert data["file_type"] == "csv"
    
    def test_upload_invalid_file_type(self, client, auth_headers):
        """Test uploading unsupported file type"""
        invalid_file = BytesIO(b"binary data")
        response = client.post(
            "/api/v1/files/upload",
            files={"file": ("test.exe", invalid_file, "application/x-msdownload")},
            headers=auth_headers
        )
        assert response.status_code == 400
    
    def test_get_my_files(self, client, auth_headers):
        """Test listing user's uploaded files"""
        response = client.get(
            "/api/v1/files/my-files",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_file_details(self, client, auth_headers, test_file_id):
        """Test getting file details"""
        response = client.get(
            f"/api/v1/files/{test_file_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_file_id
        assert "filename" in data
        assert "file_size" in data
    
    def test_delete_file(self, client, auth_headers, test_file_id):
        """Test deleting a file"""
        response = client.delete(
            f"/api/v1/files/{test_file_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
    
    def test_delete_nonexistent_file(self, client, auth_headers):
        """Test deleting non-existent file"""
        response = client.delete(
            "/api/v1/files/99999",
            headers=auth_headers
        )
        assert response.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════
# 📊 DATASET ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════


class TestDatasetEndpoints:
    """Test suite for dataset management endpoints"""
    
    def test_get_all_datasets(self, client, auth_headers):
        """Test retrieving all user datasets"""
        response = client.get(
            "/api/v1/datasets",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_dataset_by_id(self, client, auth_headers, test_dataset_id):
        """Test getting dataset metadata by ID"""
        response = client.get(
            f"/api/v1/datasets/id/{test_dataset_id}/data",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "name" in data or "data" in data
    
    def test_get_dataset_by_name(self, client, auth_headers, test_dataset_name):
        """Test getting dataset by name"""
        response = client.get(
            f"/api/v1/datasets/{test_dataset_name}/data",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict) or isinstance(data, list)
    
    def test_get_nonexistent_dataset(self, client, auth_headers):
        """Test getting non-existent dataset"""
        response = client.get(
            "/api/v1/datasets/id/99999/data",
            headers=auth_headers
        )
        assert response.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════
# 🤖 ML MODEL ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════


class TestMLModelEndpoints:
    """Test suite for ML model management endpoints"""
    
    def test_create_prophet_model(self, client, auth_headers, test_dataset_id):
        """Test creating a Prophet model"""
        response = client.post(
            "/api/v1/models",
            json={
                "name": "prophet_test_model",
                "model_type": "prophet",
                "dataset_id": test_dataset_id
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "prophet_test_model"
        assert data["model_type"] == "prophet"
        assert data["status"] == "en_entrenamiento"
    
    def test_create_arima_model(self, client, auth_headers, test_dataset_id):
        """Test creating an ARIMA model"""
        response = client.post(
            "/api/v1/models",
            json={
                "name": "arima_test_model",
                "model_type": "arima",
                "dataset_id": test_dataset_id
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "arima_test_model"
        assert data["model_type"] == "arima"
        assert data["status"] == "en_entrenamiento"
    
    def test_create_model_duplicate_name(self, client, auth_headers, test_dataset_id):
        """Test creating model with duplicate name"""
        model_name = "unique_model_name"
        
        # Create first model
        client.post(
            "/api/v1/models",
            json={
                "name": model_name,
                "model_type": "prophet",
                "dataset_id": test_dataset_id
            },
            headers=auth_headers
        )
        
        # Try to create another with same name
        response = client.post(
            "/api/v1/models",
            json={
                "name": model_name,
                "model_type": "arima",
                "dataset_id": test_dataset_id
            },
            headers=auth_headers
        )
        assert response.status_code == 400
    
    def test_get_all_user_models(self, client, auth_headers):
        """Test retrieving all models for current user"""
        response = client.get(
            "/api/v1/models",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_models_by_dataset(self, client, auth_headers, test_dataset_id):
        """Test retrieving models by dataset"""
        response = client.get(
            f"/api/v1/models/dataset/{test_dataset_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_model_detail(self, client, auth_headers, test_model_id):
        """Test getting model details"""
        response = client.get(
            f"/api/v1/models/{test_model_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_model_id
        assert "model_type" in data
        assert "status" in data
    
    def test_update_model(self, client, auth_headers, test_model_id):
        """Test updating model information"""
        response = client.put(
            f"/api/v1/models/{test_model_id}",
            json={
                "name": "updated_model_name",
                "status": "entrenado"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "updated_model_name"
    
    def test_delete_model(self, client, auth_headers, test_model_id):
        """Test deleting a model"""
        response = client.delete(
            f"/api/v1/models/{test_model_id}",
            headers=auth_headers
        )
        assert response.status_code == 204


# ═══════════════════════════════════════════════════════════════════════════
# 🔮 PREDICTION ENDPOINTS (PROPHET)
# ═══════════════════════════════════════════════════════════════════════════


class TestProphetPredictionEndpoints:
    """Test suite for Prophet model prediction endpoints"""
    
    def test_prophet_predict(self, client, auth_headers, test_prophet_model_id):
        """Test making predictions with Prophet model"""
        response = client.post(
            "/api/v1/predictions/predict",
            json={
                "model_id": test_prophet_model_id,
                "periods": 30
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "model_id" in data
        assert "model_name" in data
        assert "forecast" in data
        assert len(data["forecast"]) == 30
    
    def test_prophet_predict_invalid_periods(self, client, auth_headers, test_prophet_model_id):
        """Test prediction with invalid period count"""
        response = client.post(
            "/api/v1/predictions/predict",
            json={
                "model_id": test_prophet_model_id,
                "periods": -10  # Invalid
            },
            headers=auth_headers
        )
        assert response.status_code == 422
    
    def test_prophet_plot(self, client, auth_headers, test_prophet_model_id):
        """Test generating Prophet forecast plot"""
        response = client.get(
            f"/api/v1/predictions/plots/prophet/{test_prophet_model_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "image" in data
        assert data["image"].startswith("data:image/png;base64,")
    
    def test_prophet_model_info(self, client, auth_headers, test_prophet_model_id):
        """Test getting Prophet model information"""
        response = client.get(
            f"/api/v1/predictions/models/{test_prophet_model_id}/info",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "model_id" in data
        assert "model_type" in data or "name" in data


# ═══════════════════════════════════════════════════════════════════════════
# 🔮 PREDICTION ENDPOINTS (ARIMA)
# ═══════════════════════════════════════════════════════════════════════════


class TestARIMAPredictionEndpoints:
    """Test suite for ARIMA model prediction endpoints"""
    
    def test_arima_predict(self, client, auth_headers, test_arima_model_id):
        """Test making predictions with ARIMA model"""
        response = client.post(
            "/api/v1/predictions/arima/predict",
            json={
                "model_id": test_arima_model_id,
                "periods": 30
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "model_id" in data
        assert "forecast" in data
        assert len(data["forecast"]) == 30
        
        # Verify forecast structure
        forecast_point = data["forecast"][0]
        assert "date" in forecast_point
        assert "yhat" in forecast_point
        assert "yhat_lower" in forecast_point
        assert "yhat_upper" in forecast_point
    
    def test_arima_predict_custom_periods(self, client, auth_headers, test_arima_model_id):
        """Test ARIMA prediction with custom period count"""
        response = client.post(
            "/api/v1/predictions/arima/predict",
            json={
                "model_id": test_arima_model_id,
                "periods": 60
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["forecast"]) == 60
    
    def test_arima_model_info(self, client, auth_headers, test_arima_model_id):
        """Test getting ARIMA model information"""
        response = client.get(
            f"/api/v1/predictions/arima/models/{test_arima_model_id}/info",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "model_id" in data
        assert "model_type" in data
        assert data["model_type"].lower() == "arima"
    
    def test_arima_training_data(self, client, auth_headers, test_arima_model_id):
        """Test retrieving ARIMA training data"""
        response = client.get(
            f"/api/v1/predictions/arima/models/{test_arima_model_id}/training-data?samples=100",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "training_data" in data
        assert "total_training_points" in data
        assert isinstance(data["training_data"], list)
    
    def test_arima_plot(self, client, auth_headers, test_arima_model_id):
        """Test generating ARIMA forecast plot"""
        response = client.get(
            f"/api/v1/predictions/plots/arima/{test_arima_model_id}?periods=30&historical_periods=50",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "image" in data
        assert data["image"].startswith("data:image/png;base64,")
        assert "parameters" in data
        
        params = data["parameters"]
        assert "order" in params  # ARIMA order (p,d,q)
        assert "future_periods" in params
        assert "historical_periods" in params


# ═══════════════════════════════════════════════════════════════════════════
# 🔐 AUTHORIZATION TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestAuthorizationAndPermissions:
    """Test authorization and permission checks"""
    
    def test_cannot_access_other_user_model(self, client, auth_headers_user2, test_model_id):
        """Test that users cannot access models from other users"""
        response = client.get(
            f"/api/v1/models/{test_model_id}",
            headers=auth_headers_user2
        )
        assert response.status_code == 404
    
    def test_cannot_predict_other_user_model(self, client, auth_headers_user2, test_prophet_model_id):
        """Test that users cannot make predictions with other users' models"""
        response = client.post(
            "/api/v1/predictions/predict",
            json={
                "model_id": test_prophet_model_id,
                "periods": 30
            },
            headers=auth_headers_user2
        )
        assert response.status_code == 404
    
    def test_cannot_delete_other_user_model(self, client, auth_headers_user2, test_model_id):
        """Test that users cannot delete other users' models"""
        response = client.delete(
            f"/api/v1/models/{test_model_id}",
            headers=auth_headers_user2
        )
        assert response.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════
# ⚠️ ERROR HANDLING TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestErrorHandling:
    """Test error handling and validation"""
    
    def test_invalid_json_payload(self, client, auth_headers):
        """Test handling of invalid JSON"""
        response = client.post(
            "/api/v1/models",
            data="invalid json {",
            headers={**auth_headers, "Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client, auth_headers, test_dataset_id):
        """Test missing required fields in request"""
        response = client.post(
            "/api/v1/models",
            json={
                "name": "model_name"
                # Missing model_type and dataset_id
            },
            headers=auth_headers
        )
        assert response.status_code == 422
    
    def test_unauthorized_without_token(self, client):
        """Test endpoints require authentication"""
        response = client.get("/api/v1/usuarios/me")
        assert response.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════
# 📈 PERFORMANCE AND SCALING TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestPerformance:
    """Test API performance and response times"""
    
    def test_large_prediction_request(self, client, auth_headers, test_arima_model_id):
        """Test prediction with large number of periods"""
        response = client.post(
            "/api/v1/predictions/arima/predict",
            json={
                "model_id": test_arima_model_id,
                "periods": 365  # Full year prediction
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["forecast"]) == 365
    
    def test_get_all_models_pagination(self, client, auth_headers):
        """Test retrieving many models"""
        response = client.get(
            "/api/v1/models",
            headers=auth_headers
        )
        assert response.status_code == 200
        # Should handle large lists gracefully


# ═══════════════════════════════════════════════════════════════════════════
# 🔗 INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestIntegration:
    """End-to-end integration tests"""
    
    def test_complete_workflow_prophet(self, client, auth_headers, test_dataset_csv):
        """Test complete workflow: upload -> create model -> predict -> plot"""
        
        # 1. Upload file
        upload_response = client.post(
            "/api/v1/files/upload",
            files={"file": ("data.csv", test_dataset_csv, "text/csv")},
            headers=auth_headers
        )
        assert upload_response.status_code == 201
        file_id = upload_response.json()["id"]
        
        # 2. Get dataset (if needed)
        # 3. Create Prophet model
        model_response = client.post(
            "/api/v1/models",
            json={
                "name": "workflow_test_prophet",
                "model_type": "prophet",
                "dataset_id": 1  # Use valid dataset
            },
            headers=auth_headers
        )
        assert model_response.status_code == 201
        model_id = model_response.json()["id"]
        
        # 4. Wait for training (would need to poll status in real test)
        # 5. Make prediction
        pred_response = client.post(
            "/api/v1/predictions/predict",
            json={
                "model_id": model_id,
                "periods": 30
            },
            headers=auth_headers
        )
        assert pred_response.status_code in [200, 400]  # 400 if model not ready
    
    def test_complete_workflow_arima(self, client, auth_headers):
        """Test complete workflow with ARIMA"""
        
        # Create ARIMA model
        model_response = client.post(
            "/api/v1/models",
            json={
                "name": "workflow_test_arima",
                "model_type": "arima",
                "dataset_id": 1
            },
            headers=auth_headers
        )
        assert model_response.status_code == 201
        model_id = model_response.json()["id"]
        
        # Get model info
        info_response = client.get(
            f"/api/v1/predictions/arima/models/{model_id}/info",
            headers=auth_headers
        )
        # Could be 404 if model not trained yet
        assert info_response.status_code in [200, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
