# 🧪 TEST SUITE DOCUMENTATION

Complete testing guide for TFG ML Platform

---

## RUNNING TESTS

### Prerequisites

```bash
pip install pytest pytest-cov httpx
```

### Run All Tests

```bash
# Run all tests with verbose output
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_endpoints.py -v

# Run specific test class
pytest tests/test_endpoints.py::TestAuthEndpoints -v

# Run specific test method
pytest tests/test_endpoints.py::TestAuthEndpoints::test_register_user_success -v
```

### Test Organization

```
tests/
├── conftest.py .................... Pytest configuration, fixtures
├── test_endpoints.py .............. All endpoint tests (~600 tests)
└── example_test.py ................ Example test template
```

---

## TEST COVERAGE

### Current Test Suites

1. **Authentication Tests** `TestAuthEndpoints`
   - User registration
   - Login
   - Invalid credentials
   - Email validation
   - Password strength

2. **User Management** `TestUsuarioEndpoints`
   - Get current user
   - Get user by ID
   - Update profile
   - Delete account
   - GDPR data deletion

3. **File Management** `TestFileEndpoints`
   - File upload
   - File type validation
   - File listing
   - Get file details
   - File deletion

4. **Datasets** `TestDatasetEndpoints`
   - List datasets
   - Get by ID
   - Get by name
   - Error handling

5. **ML Models** `TestMLModelEndpoints`
   - Create Prophet model
   - Create ARIMA model
   - Duplicate name detection
   - List models
   - List by dataset
   - Get details
   - Update
   - Delete

6. **Prophet Predictions** `TestProphetPredictionEndpoints`
   - Generate predictions
   - Invalid periods
   - Generate plot
   - Model info

7. **ARIMA Predictions** `TestARIMAPredictionEndpoints`
   - Generate predictions
   - Custom periods
   - Model info
   - Training data retrieval
   - Plot generation

8. **Authorization** `TestAuthorizationAndPermissions`
   - Cross-user access prevention
   - Model access control
   - Deletion prevention

9. **Error Handling** `TestErrorHandling`
   - Invalid JSON
   - Missing fields
   - Unauthorized access

10. **Integration** `TestIntegration`
    - Complete workflows
    - End-to-end scenarios

---

## FIXTURES AVAILABLE

### Authentication Fixtures

```python
@pytest.fixture
def auth_headers:
    """Returns Authorization header with valid JWT token"""
    # Usage: client.get("/api/v1/usuarios/me", headers=auth_headers)

@pytest.fixture
def auth_headers_user2:
    """Returns auth header for second test user"""
    # For testing cross-user access control
```

### User Fixtures

```python
@pytest.fixture
def test_user_data:
    """Test user registration data"""
    return {
        "username": "test_user_tfg",
        "email": "test@tfg.local",
        "password": "TestPassword123!",
        "full_name": "Test User TFG"
    }

@pytest.fixture
def test_user_id:
    """ID of authenticated test user"""
```

### File Fixtures

```python
@pytest.fixture
def test_dataset_csv:
    """Sample CSV file with 40 rows of time-series data"""
    # Automatically loaded in test

@pytest.fixture
def test_file_id:
    """ID of uploaded test file"""
```

### Model Fixtures

```python
@pytest.fixture
def test_model_id:
    """ID of general test model"""

@pytest.fixture
def test_prophet_model_id:
    """ID of Prophet model for testing"""

@pytest.fixture
def test_arima_model_id:
    """ID of ARIMA model for testing"""
```

---

## WRITING TESTS

### Test Template

```python
import pytest
from fastapi.testclient import TestClient

class TestMyFeature:
    """Test suite for my feature"""
    
    def test_success_case(self, client, auth_headers):
        """Test happy path"""
        response = client.get(
            "/api/v1/endpoint",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "expected_field" in data
    
    def test_error_case(self, client, auth_headers):
        """Test error handling"""
        response = client.post(
            "/api/v1/endpoint",
            json={"invalid": "data"},
            headers=auth_headers
        )
        assert response.status_code == 422
```

### HTTP Methods

```python
# GET
client.get("/api/v1/endpoint", headers=auth_headers)

# POST
client.post(
    "/api/v1/endpoint",
    json={"key": "value"},
    headers=auth_headers
)

# PUT
client.put(
    "/api/v1/endpoint/1",
    json={"updated": "data"},
    headers=auth_headers
)

# DELETE
client.delete(
    "/api/v1/endpoint/1",
    headers=auth_headers
)

# FILE UPLOAD
client.post(
    "/api/v1/files/upload",
    files={"file": ("filename.csv", file_contents, "text/csv")},
    headers=auth_headers
)
```

### Assertions

```python
# Status codes
assert response.status_code == 200
assert response.status_code in [200, 201]

# Response JSON
data = response.json()
assert data["id"] == 1
assert "token" in data
assert isinstance(data["items"], list)

# Response headers
assert response.headers["content-type"] == "application/json"
```

---

## CONTINUOUS INTEGRATION

### GitHub Actions (Optional)

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    - name: Run tests
      run: pytest --cov=app --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

---

## COVERAGE REPORT

### Generate HTML Coverage Report

```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

### Coverage Targets

- **Authentication**: 95%+
- **API Endpoints**: 90%+
- **Database**: 85%+
- **ML Modules**: 80%+
- **Overall**: 85%+

###  Check Coverage

```bash
# Generate coverage table
pytest --cov=app --cov-report=term-missing

# Show uncovered lines
pytest --cov=app --cov-report=term-missing:skip-covered
```

---

## PYTEST CONFIGURATION

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers
markers =
    integration: integration tests
    endpoints: endpoint tests
    slow: slow tests
```

### Running with Marks

```bash
# Only integration tests
pytest -m integration

# Only endpoint tests
pytest -m endpoints

# Skip slow tests
pytest -m "not slow"
```

---

## COMMON TEST PATTERNS

### Testing Authentication

```python
def test_requires_auth(self, client):
    """Test endpoint requires authentication"""
    response = client.get("/api/v1/protected-endpoint")
    assert response.status_code == 401
    assert "authorization" in response.json()["detail"].lower()
```

### Testing Permissions

```python
def test_user_can_access_own_resource(self, client, auth_headers, user_id):
    response = client.get(
        f"/api/v1/usuarios/{user_id}",
        headers=auth_headers
    )
    assert response.status_code == 200

def test_user_cannot_access_other_resource(self, client, auth_headers_user2, user1_id):
    response = client.get(
        f"/api/v1/usuarios/{user1_id}",
        headers=auth_headers_user2
    )
    assert response.status_code == 404
```

### Testing Validation

```python
def test_schema_validation(self, client, auth_headers):
    """Test Pydantic schema validation"""
    response = client.post(
        "/api/v1/models",
        json={
            "name": "model",
            # Missing required field: model_type
        },
        headers=auth_headers
    )
    assert response.status_code == 422
    assert "model_type" in response.json()["detail"]
```

### Testing File Upload

```python
def test_upload_csv(self, client, auth_headers):
    """Test CSV file upload"""
    csv_content = "date,value\n2024-01-01,100\n"
    
    response = client.post(
        "/api/v1/files/upload",
        files={"file": ("test.csv", csv_content, "text/csv")},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["filename"] == "test.csv"
```

---

## DEBUGGING TESTS

### Detailed Output

```bash
# Show print statements
pytest -s tests/test_endpoints.py::TestClass::test_method

# Show local variables on failures
pytest -l tests/test_endpoints.py

# Extra verbose
pytest -vv tests/test_endpoints.py
```

### Using pdb

```python
def test_something(self, client):
    response = client.get("/api/v1/endpoint")
    breakpoint()  # Breaks here to inspect
    assert response.status_code == 200
```

### Using pytest fixtures for debugging

```python
def test_with_logging(self, client, caplog):
    """Capture logs during test"""
    response = client.get("/api/v1/endpoint")
    assert "expected_log" in caplog.text
```

---

## PERFORMANCE TESTING

### Test Response Times

```python
import time

def test_response_time(self, client, auth_headers):
    """Test endpoint responds within SLA"""
    start = time.time()
    response = client.get("/api/v1/models", headers=auth_headers)
    elapsed = time.time() - start
    
    assert response.status_code == 200
    assert elapsed < 0.5  # Must complete in 500ms
```

### Load Testing

```bash
# Using locust (install: pip install locust)
# Create locustfile.py and run:
locust -f locustfile.py --host=http://localhost:8000
```

---

## TROUBLESHOOTING TESTS

### ModuleNotFoundError

```bash
# Solution: Install in development mode
pip install -e .
```

### Database Issues

```bash
# Solution: Reset database before tests
python rebuild_db.py
pytest
```

### Port Already in Use

```bash
# Solution: Use different port
pytest --cov=app --cov-report=html -- --port=8001
```

### Tests Pass Locally but Fail in CI

```bash
# Check Python version matches
python --version

# Ensure all dependencies installed
pip install -r requirements-dev.txt

# Run tests in CI environment
python -m pytest tests/
```

---

## BEST PRACTICES

✅ **DO:**
- Write one test per feature
- Use descriptive test names
- Test both success and failure paths
- Keep fixtures simple and focused
- Use appropriate assertions
- Clean up after tests (via fixtures)

❌ **DON'T:**
- Test multiple features in one test
- Use generic test names like "test_api"
- Depend on test execution order
- Create large, complex fixtures
- Mock unnecessarily
- Commit broken tests

---

## TEST EXAMPLES

### Example 1: User Registration

```python
def test_register_user_success(self, client, test_user_data):
    """Successful user registration"""
    response = client.post(
        "/api/v1/auth/register",
        json=test_user_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == test_user_data["username"]
    assert data["email"] == test_user_data["email"]
    assert "id" in data
    assert "password" not in data
```

### Example 2: Model Creation & Prediction

```python
def test_model_prediction_workflow(self, client, auth_headers, test_dataset_id):
    """Complete model training and prediction"""
    
    # Create model
    model_response = client.post(
        "/api/v1/models",
        json={
            "name": "test_model",
            "model_type": "prophet",
            "dataset_id": test_dataset_id
        },
        headers=auth_headers
    )
    assert model_response.status_code == 201
    model_id = model_response.json()["id"]
    
    # Wait for training (would poll in real test)
    # Make prediction
    pred_response = client.post(
        "/api/v1/predictions/predict",
        json={"model_id": model_id, "periods": 30},
        headers=auth_headers
    )
    # May be 400 if not trained yet, which is expected
    assert pred_response.status_code in [200, 400]
```

---

## RESOURCES

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/advanced/testing-dependencies/)
- [httpx Documentation](https://www.python-httpx.org/)
