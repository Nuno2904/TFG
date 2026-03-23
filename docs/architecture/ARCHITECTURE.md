# 🏗️ SYSTEM ARCHITECTURE

Complete system architecture documentation for TFG ML Platform.

## 📋 TABLE OF CONTENTS

1. [Overview](#overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [System Workflows](#system-workflows)

---

## OVERVIEW

TFG ML Platform is a comprehensive time-series forecasting application that integrates multiple ML models (Prophet, ARIMA, and SARIMA) with a modern REST API backend.

### Key Features
- **User Authentication**: Secure JWT-based authentication
- **File Management**: Upload and manage CSV datasets
- **ML Models**: Train Prophet, ARIMA, or SARIMA models (auto-selected based on seasonality)
- **Predictions**: Generate forecasts with confidence intervals
- **Visualizations**: Automatic chart generation with model predictions
- **Background Tasks**: Asynchronous model training
- **Database**: Persistent storage of models and results
- **✨ NEW**: Automatic seasonality detection → Chooses ARIMA or SARIMA

---

## ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
│  (Web Browser, Mobile App, Third-party Integrations)            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FASTAPI APPLICATION                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │           API ENDPOINTS (/api/v1/...)                    │  │
│  ├─────────────────────────────────────────────────────────────┤  │
│  │  /auth        - User authentication & registration        │  │
│  │  /usuarios    - User profile management                   │  │
│  │  /files       - File upload & management                  │  │
│  │  /datasets    - Dataset access                            │  │
│  │  /models      - ML model CRUD operations                  │  │
│  │  /predictions - Forecast generation & visualization       │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │        MIDDLEWARE & SECURITY LAYER                        │  │
│  ├─────────────────────────────────────────────────────────────┤  │
│  │  • JWT Authentication (get_current_user dependency)       │  │
│  │  • Request validation (Pydantic schemas)                  │  │
│  │  • CORS & Security headers                                │  │
│  │  • Error handling & logging                               │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │        SERVICE LAYER (Business Logic)                     │  │
│  ├─────────────────────────────────────────────────────────────┤  │
│  │  • MLStorageService - Model file I/O                      │  │
│  │  • FileService - File processing                          │  │
│  │  • Background task orchestration                          │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │     ML MODULES (Training & Prediction)                    │  │
│  ├─────────────────────────────────────────────────────────────┤  │
│  │                                                             │  │
│  │  ┌─────────────────┐      ┌──────────────────────┐            │  │
│  │  │    PROPHET      │      │   ARIMA / SARIMA    │            │  │
│  │  ├─────────────────┤      ├──────────────────────┤            │  │
│  │  │ • train.py      │      │ • train.py           │            │  │
│  │  │ • predict.py    │      │ • predict.py         │            │  │
│  │  │ • utils.py      │      │ • utils.py           │            │  │
│  │  │                 │      │                      │            │  │
│  │  │ Uses:          │      │ ✨ Auto-selects:    │            │  │
│  │  │ fbprophet      │      │ ├─ ARIMA (no season) │            │  │
│  │  │ matplotlib     │      │ └─ SARIMA (seasonal) │            │  │
│  │  │ pandas         │      │                      │            │  │
│  │  │                 │      │ Uses:                │            │  │
│  │  │                 │      │ statsmodels          │            │  │
│  │  │                 │      │ pmdarima             │            │  │
│  │  │                 │      │ matplotlib           │            │  │
│  │  └─────────────────┘      └──────────────────────┘            │  │
│  │                                                             │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┼─────────┐
                    │         │         │
                    ▼         ▼         ▼
        ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
        │  DATABASE    │ │   STORAGE    │ │   LOGGING    │
        │  (SQLite/    │ │   LAYER      │ │   SYSTEM     │
        │  PostgreSQL) │ │              │ │              │
        │              │ │ /storage/    │ │              │
        │ • Models     │ │ models/      │ │ Application  │
        │ • Datasets   │ │ • .pkl files │ │ events &     │
        │   Users      │ │ • metadata   │ │ errors       │
        │ • Files      │ │ • JSON       │ │              │
        └──────────────┘ └──────────────┘ └──────────────┘
```

---

## CORE COMPONENTS

### 1. Authentication Module (`app/security/`)

**Responsibilities:**
- JWT token generation and validation
- Password hashing and verification
- Current user dependency injection

**Key Functions:**
- `get_password_hash()` - Hash passwords securely
- `verify_password()` - Verify password
- `create_access_token()` - Generate JWT
- `get_current_user()` - FastAPI dependency for authorization

### 2. Database Layer (`app/db/`)

**SQLAlchemy ORM Models:**

```
├── Usuario
│   ├── id (Primary Key)
│   ├── username (Unique)
│   ├── email (Unique)
│   ├── hashed_password
│   ├── full_name
│   └── created_at
│
├── Dataset
│   ├── id (Primary Key)
│   ├── user_id (Foreign Key)
│   ├── file_id (Foreign Key)
│   ├── name
│   ├── row_count
│   └── created_at
│
├── MLModel
│   ├── id (Primary Key)
│   ├── user_id (Foreign Key)
│   ├── dataset_id (Foreign Key)
│   ├── name (Unique per user)
│   ├── model_type (prophet | arima)
│   ├── status (en_entrenamiento | entrenado | error)
│   ├── model_path
│   ├── error_message
│   └── created_at
│
└── File
    ├── id (Primary Key)
    ├── user_id (Foreign Key)
    ├── filename
    ├── file_size
    ├── file_type (csv | json)
    ├── file_path
    └── upload_date
```

### 3. File Management (`app/services/file_service.py`)

**Responsibilities:**
- File upload processing
- CSV parsing and validation
- File storage management

**Key Methods:**
- `upload_file()` - Handle file upload
- `validate_csv_structure()` - Validate 2-column structure (date, value)
- `parse_csv_to_dataframe()` - Convert to pandas DataFrame
- `delete_file()` - Remove uploaded file

### 4. ML Storage Service (`app/services/ml_storage_service.py`)

**Responsibilities:**
- Model file I/O operations
- Directory structure management
- Model serialization/deserialization

**Directory Structure:**
```
storage/
└── models/
    └── user_{user_id}/
        └── dataset_{dataset_id}/
            ├── model_name/
            │   ├── model.pkl          (ARIMA model)
            │   └── model_metadata.json (ARIMA metadata)
            └── prophet_model/
                ├── model.json         (Prophet model)
                └── metadata.json      (Prophet metadata)
```

**Key Methods:**
- `create_model_directory()` - Create storage directory
- `load_arima_model_from_directory()` - Load joblib model
- `load_arima_metadata()` - Load ARIMA. metadata JSON
- `save_model_metadata()` - Persist metadata

### 5. ML Training Modules

#### Prophet Module (`app/ml/prophet/`)

```
├── train.py
│   ├── train_prophet_model()    - Main training
│   ├── get_dataset_as_dataframe() - Load dataset
│   └── calculate_metrics()      - Compute RMSE, MAE
│
├── predict.py
│   ├── predict_prophet_model()  - Generate forecasts
│   ├── prophet_plot()           - Create visualization
│   └── get_training_samples()   - Historical data
│
└── utils.py
    └── validate_prophet_data() - Input validation
```

#### ARIMA Module (`app/ml/arima/`)

```
├── train.py
│   ├── train_arima_model()      - Auto ARIMA training
│   ├── prepare_dataframe_for_arima() - Format conversion
│   └── _get_current_timestamp() - Utility
│
├── predict.py
│   ├── predict_arima_model()    - Generate forecasts
│   ├── get_training_samples()   - Historical data
│   └── plot_arima_forecast()    - Create visualization
│
└── utils.py
    ├── validate_arima_series()  - Master validation
    ├── validate_stationarity()  - ADF test
    ├── detect_outliers()        - Outlier detection
    ├── validate_frequency()     - Time series regularity
    ├── validate_minimum_length() - Data sufficiency
    ├── validate_nulls()         - Missing values
    └── _generate_recommendations() - Suggestions
```

### 6. API Endpoints (`app/api/v1/endpoints/`)

**Endpoint Modules:**
- `auth.py` - Authentication (register, login)
- `usuarios.py` - User management
- `files.py` - File upload/management
- `datasets.py` - Dataset access
- `crudml.py` - Model CRUD + background training
- `predml.py` - Predictions and visualizations

---

## DATA FLOW

### 1. User Registration & Authentication Flow

```
Client                     API                    Database
  │                         │                         │
  ├─ POST /auth/register ──>│                         │
  │                         ├─ Validate input         │
  │                         ├─ Hash password          │
  │                         ├─ Create Usuario record ─>│
  │                         │<─ User created ─────────┤
  │<─ 201 Created ──────────┤                         │
  │  (user data)            │                         │
  │                         │                         │
  ├─ POST /auth/login ──────>│                         │
  │                         ├─ Find user ────────────>│
  │                         │<─ User data ───────────┤
  │                         ├─ Verify password        │
  │                         ├─ Generate JWT token     │
  │<─ 200 OK ───────────────┤                         │
  │  (access_token)         │                         │
```

### 2. File Upload & Dataset Creation Flow

```
Client                     API                    Storage          Database
  │                         │                         │                 │
  ├─ POST /files/upload ────>│                         │                 │
  │  (CSV file)             │                         │                 │
  │                         ├─ Validate file          │                 │
  │                         ├─ Save to disk ─────────>│                 │
  │                         │<─ File saved ───────────┤                 │
  │                         ├─ Parse CSV ─────────────────────────────>│
  │                         │  (validate, create Dataset)               │
  │<─ 201 Created ──────────┤<─ Dataset created ─────────────────────┤
  │  (file_id)              │                         │                 │
```

### 3. Model Training Workflow (Background Task)

```
Client                    API                 Background Task          Storage          Database
  │                        │                        │                      │              │
  ├─ POST /models ────────>│                        │                      │              │
  │  (model_type,          │                        │                      │              │
  │   dataset_id)          │                        │                      │              │
  │                        ├─ Create record ───────────────────────────────────────────>│
  │                        │  (status: en_entrenamiento)                  │              │
  │<─ 201 Created ─────────┤                        │                      │              │
  │  (model_id)            │                        │                      │              │
  │                        ├─ Dispatch BG task ────>│                      │              │
  │                        │  (fire & forget)       │                      │              │
  │                        │                        ├─ Load dataset data   │              │
  │                        │                        │                      │              │
  │                        │                        ├─ Train model ────────────────────>│
  │                        │                        │                      │              │
  │                        │                        ├─ Validate data       │              │
  │  (Client polls)        │                        │                      │              │
  ├─ GET /models/1 ───────>│                        ├─ Save model ──────>│              │
  │                        │                        │  & metadata          │              │
  │<─ 200 OK ──────────────┤                        │                      │              │
  │  (status: en...)       │                        ├─ Update status ────────────────────>│
  │                        │                        │  (entrenado)         │              │
  │                        │                        │                      │              │
  │  (after training done) │                        │                      │              │
  ├─ GET /models/1 ───────>│                        │                      │              │
  │<─ 200 OK ──────────────┤                        │                      │              │
  │  (status: entrenado)   │                        │                      │              │
```

### 4. Prediction & Visualization Flow

```
Client                        API                    Storage        Database
  │                           │                          │              │
  ├─ POST /predictions/predict ──>│                      │              │
  │  (model_id, periods)      │                          │              │
  │                           ├─ Get model ─────────────────────────────>│
  │                           │<─ model_path ──────────────────────────┤
  │                           ├─ Load model ───────────>│              │
  │                           │  & metadata             │              │
  │                           ├─ Generate forecast      │              │
  │                           ├─ Format response        │              │
  │<─ 200 OK ─────────────────┤                          │              │
  │  (forecast data)          │                          │              │
  │                           │                          │              │
  ├─ GET /plots/prophet/{id} ─>│                        │              │
  │  ?periods=30              │                          │              │
  │                           ├─ Load model             │              │
  │                           ├─ Generate forecast      │              │
  │                           ├─ Create matplotlib plot │              │
  │                           ├─ Encode PNG to base64   │              │
  │<─ 200 OK ─────────────────┤                          │              │
  │  (image: data:image/...)  │                          │              │
```

---

## TECHNOLOGY STACK

### Backend Framework
- **FastAPI** (0.104+) - Modern async web framework
- **Python** (3.10+) - Programming language
- **Uvicorn** - ASGI server

### Database
- **SQLite** (development) / **PostgreSQL** (production)
- **SQLAlchemy** (2.0+) - ORM
- **Alembic** - Database migrations

### ML & Data Processing
- **statsmodels** (0.14+) - ARIMA models
- **pmdarima** (2.0+) - Auto ARIMA
- **fbprophet** (1.1+) - Prophet timeseries
- **pandas** (2.0+) - Data manipulation
- **numpy** (1.24+) - Numerical computing
- **matplotlib** (3.7+) - Visualization
- **joblib** (1.3+) - Model serialization

### Authentication & Security
- **python-jose** - JWT tokens
- **passlib** - Password hashing
- **bcrypt** - Cryptography
- **python-multipart** - Form handling

### Testing & Development
- **pytest** (7.0+) - Testing framework
- **pytest-cov** - Coverage reports
- **httpx** - Async HTTP client
- **black** - Code formatting
- **pylint** - Code linting

### Deployment & DevOps
- **Docker** - Containerization
- **docker-compose** - Multi-container orchestration
- **GitHub Actions** - CI/CD (optional)

---

## SYSTEM WORKFLOWS

### Workflow 1: Complete Model Training & Prediction

#### Step 1: User Registration
```python
POST /api/v1/auth/register
{
  "username": "researcher",
  "email": "researcher@tfg.edu",
  "password": "SecurePass123!",
  "full_name": "Juan Pérez"
}
→ Creates Usuario record
→ Returns user_id = 1
```

#### Step 2: File Upload
```python
POST /api/v1/files/upload
File: sales_data.csv
→ Validates CSV structure (date, value)
→ Saves to /storage/uploads/
→ Creates File record
→ Returns file_id = 1
```

#### Step 3: Dataset Creation
```python
Dataset created automatically from file parsing
→ Stores data rows
→ Links to file_id = 1
→ Returns dataset_id = 1
```

#### Step 4: Model Creation (Auto-Training)
```python
POST /api/v1/models
{
  "name": "sales_forecast",
  "model_type": "prophet",
  "dataset_id": 1
}
→ Creates MLModel record (status: en_entrenamiento)
→ Dispatches background training task
→ Returns model_id = 1 immediately
```

#### Step 5: Background Training
```
BG Task:
1. Load dataset from DB (365 rows)
2. Parse as Prophet DataFrame
3. Call Prophet.fit()
4. Calculate metrics (RMSE, MAE)
5. Save model to /storage/models/user_1/dataset_1/sales_forecast/
6. Update MLModel.status = "entrenado"
```

#### Step 6: Predictions
```python
POST /api/v1/predictions/predict
{
  "model_id": 1,
  "periods": 30
}
→ Load model from storage
→ Generate 30-day forecast
→ Return forecast points with confidence intervals
```

#### Step 7: Visualization
```python
GET /api/v1/predictions/plots/prophet/1
?periods=30&historical_periods=50
→ Load model
→ Generate forecast
→ Create matplotlib chart (historical + forecast)
→ Encode as base64 PNG
→ Return as data:image/png;base64,...
```

### Workflow 2: ARIMA / SARIMA Model with Automatic Selection

#### Step 1-4: Same as Prophet (File → Model Creation)

#### Step 5: Automatic Seasonality Detection & Training (NEW!)
```
BG Task:
1. Load dataset (must have ≥50 observations)
2. Validate data:
   - Check for nulls
   - Validate minimum length
   - Validate frequency regularity
   - Detect outliers (IQR method)
3. DETECT SEASONALITY (✨ NEW):
   - Decompose series: seasonal_decompose()
   - Calculate seasonal strength
   - If strength > 0.1 → HAS SEASONALITY
4. CHOOSE MODEL AUTOMATICALLY:
   ├─ If HAS SEASONALITY:
   │  ├─ Use seasonal=True in auto_arima
   │  ├─ Search SARIMA(p,d,q)(P,D,Q,m=12)
   │  ├─ p,q ∈ [0,3], P,Q ∈ [0,1], d,D ∈ [0,1]
   │  └─ Train SARIMA model
   │
   └─ If NO SEASONALITY:
      ├─ Use seasonal=False in auto_arima
      ├─ Search ARIMA(p,d,q)
      ├─ p,q ∈ [0,5], d ∈ [0,2]
      └─ Train ARIMA model
5. Select best parameters by AIC
6. Generate metrics & metadata (including model_type)
7. Save model.pkl + metadata.json
8. Update MLModel.status = "entrenado"
```

#### Metadata Examples

**ARIMA (No Seasonality):**
```json
{
  "model_type": "ARIMA",
  "order": [2, 1, 1],
  "seasonal_order": null,
  "tiene_estacionalidad": false,
  "aic": 1234.56,
  "bic": 1245.67
}
```

**SARIMA (With Seasonality):**
```json
{
  "model_type": "SARIMA",
  "order": [1, 1, 1],
  "seasonal_order": [0, 0, 1, 12],
  "tiene_estacionalidad": true,
  "periodo_estacional": 12,
  "aic": 1200.45,
  "bic": 1220.34
}
```

#### Step 6-7: Predictions & Plots (Same as Prophet)

### Workflow 3: Data Validation & Error Handling

#### ARIMA/SARIMA Validation Pipeline
```
Input Data
    ↓
validate_arima_series() {
    ├─ validate_nulls()
    │  └─ If >30% missing → FAIL
    ├─ validate_minimum_length()
    │  └─ If <50 observations → FAIL
    ├─ validate_frequency()
    │  └─ If irregular timestamps → WARN
    ├─ detect_seasonality() (✨ NEW)
    │  ├─ seasonal_decompose()
    │  ├─ Calculate seasonal strength
    │  └─ If >0.1 → has_seasonality = True
    └─ detect_outliers()
       └─ If >5% outliers → WARN, suggest cleaning
}
    ↓
If all pass: PROCEED to training
If validation fails: error_message + status=ERROR
```

#### Error Recovery
```
Exception during training:
    ↓
catch Exception as e:
    ├─ Log full traceback
    ├─ Update MLModel.error_message = str(e)[:500]
    ├─ Update MLModel.status = "error"
    └─ User can retry model creation
```

---

## PERFORMANCE CONSIDERATIONS

### Model Training Times (Approximate)
- **Prophet**: 500-2000 samples → 2-10 seconds
- **ARIMA**: 50-500 samples → 1-5 seconds
- **ARIMA Auto-search**: 500+ samples → 5-15 seconds

### Memory Usage
- Prophet model: 10-50 MB
- ARIMA model: 1-5 MB
- Large datasets (100K rows): 50-200 MB

### Database Query Performance
- Indexed columns: user_id, dataset_id, model_id
- Typical query times: <100ms for single model retrieval

---

## SECURITY ARCHITECTURE

### Authentication
- JWT tokens (HS256 signing)
- Token expiration: 24 hours (configurable)
- Refresh tokens: Not yet implemented

### Authorization
- Row-level security: Users can only access own resources
- Model-level checks: Verify user_id before operations
- File access: Tied to user_id

### Password Security
- Bcrypt hashing (cost factor: 12)
- Minimum requirements: 8 chars, uppercase, number, special char
- No password recovery (use email-based flow if needed)

### Data Protection
- File uploads validated (type, size, content)
- No sensitive data in logs
- Model files: Not exposed directly (only through API)

