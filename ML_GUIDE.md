"""
🤖 ML Models Implementation Guide

Complete documentation of the ML models system including database structure,
API endpoints, storage management, and file organization.
"""

# 🤖 ML Models System Documentation

## 📋 Overview

This document explains the complete ML (Machine Learning) models system implementation, including:
- Database schema and relationships
- API endpoints for model management
- File storage organization
- Frontend integration guidelines

---

## 🗂️ What Changed

### 1. **New Database Table: `ml_models`**

A new table was created to store information about ML models trained by users.

**Table: `ml_models`**
```
Column Name      | Type        | Description
─────────────────┼─────────────┼────────────────────────────────
id               | INTEGER     | Primary Key - unique model ID
user_id          | INTEGER     | FK → usuarios.id (who created it)
dataset_id       | INTEGER     | FK → datasets.id (training data)
name             | VARCHAR     | Model name (e.g., "prophet", "lstm")
created_at       | TIMESTAMP   | Auto-generated creation date
model_path       | VARCHAR     | Full file system path to model
status           | VARCHAR     | Model state (entrenado/en_entrenamiento/error)
error_message    | VARCHAR     | Error details (nullable)
```

### 2. **Relationship Updates**

The following tables now have relationships to `ml_models`:

**Usuario → MLModel (One-to-Many)**
- Each user can create multiple models
- Cascade delete: deleting a user deletes their models
- Access: `usuario.ml_models`

**Dataset → MLModel (One-to-Many)**
- Each dataset can be used to train multiple models
- Cascade delete: deleting a dataset deletes models trained with it
- Access: `dataset.ml_models`

### 3. **New Files Created**

```
app/
├── models/
│   └── ml.py                    ← 🆕 MLModel ORM model
│
├── schemas/
│   └── ml.py                    ← 🆕 MLModel Pydantic schemas
│
├── services/
│   └── ml_storage_service.py    ← 🆕 Storage management service
│
└── api/v1/endpoints/
    └── ml.py                    ← 🆕 ML model endpoints
```

---

## 📁 Project Structure - ML Components

### Detailed File Breakdown

#### **1. `app/models/ml.py`** - Database Model
```python
# What it does:
# - Defines the MLModel ORM class using SQLAlchemy
# - Creates database table schema
# - Establishes relationships with Usuario and Dataset
# - Uses modern typing with Mapped and relationship()

# Key components:
- MLModel class          → Represents a trained ML model in the database
- ModelStatus enum       → Defines valid model states (TRAINED, TRAINING, ERROR)
- Relationships          → Bidirectional links to Usuario and Dataset
```

**Status Values:**
- `"entrenado"` - Model is trained and ready
- `"en_entrenamiento"` - Model is currently training
- `"error"` - Training failed (check error_message)

---

#### **2. `app/schemas/ml.py`** - Validation Schemas
```python
# What it does:
# - Defines Pydantic models for request/response validation
# - Ensures data integrity for API communication
# - Provides documentation for API requests

# Key components:
```

**Schema Classes:**

| Schema | Purpose |
|--------|---------|
| `MLModelBase` | Base fields: name, dataset_id |
| `MLModelCreate` | Request to create new model (user provides: name, dataset_id) |
| `MLModelUpdate` | Request to update model (status, error_message) |
| `MLModelOut` | Response with all model info (includes id, created_at, path, etc.) |
| `MLModelDetailOut` | Extended response with nested usuario and dataset info |

---

#### **3. `app/services/ml_storage_service.py`** - Storage Management
```python
# What it does:
# - Manages file system paths for model storage
# - Creates directory structure automatically
# - Handles file operations (creation, deletion)
# - Generates consistent path naming

# Key methods:
```

**Important Methods:**

| Method | Returns | Purpose |
|--------|---------|---------|
| `create_model_directory()` | Path | Creates `/app/storage/models/user_{id}/dataset_{id}/{model_name}` |
| `get_model_directory()` | Path | Returns path without creating |
| `get_model_file_path()` | Path | Returns path to specific file (e.g., model.pkl) |
| `delete_model_directory()` | bool | Removes entire directory tree |
| `get_relative_path()` | str | Returns: `user_1/dataset_3/prophet` |

---

#### **4. `app/api/v1/endpoints/ml.py`** - API Endpoints
```python
# What it does:
# - Handles HTTP requests for ML model operations
# - Validates permissions (user owns the model)
# - Manages database transactions
# - Handles file system operations
```

---

## 🔌 API Endpoints

### 📝 Create New Model
```http
POST /api/v1/models
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "prophet_model",
  "dataset_id": 3
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "dataset_id": 3,
  "name": "prophet_model",
  "created_at": "2026-03-04T10:30:00Z",
  "model_path": "/app/storage/models/user_1/dataset_3/prophet_model",
  "status": "en_entrenamiento",
  "error_message": null
}
```

**What happens:**
1. ✅ Verifies dataset exists and belongs to user
2. ✅ Creates directory structure
3. ✅ Saves model in database
4. ✅ Status set to "en_entrenamiento"

---

### 📖 Get All User Models
```http
GET /api/v1/models
Authorization: Bearer {token}
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "prophet_model",
    "dataset_id": 3,
    "status": "en_entrenamiento",
    "created_at": "2026-03-04T10:30:00Z",
    ...
  },
  {
    "id": 2,
    "name": "lstm_model",
    "dataset_id": 5,
    "status": "entrenado",
    "created_at": "2026-03-04T11:15:00Z",
    ...
  }
]
```

---

### 🔍 Get Model Details
```http
GET /api/v1/models/{model_id}
Authorization: Bearer {token}
```

**Response (includes nested data):**
```json
{
  "id": 1,
  "name": "prophet_model",
  "status": "entrenado",
  "usuario": {
    "id": 1,
    "email": "user@example.com"
  },
  "dataset": {
    "id": 3,
    "name": "sales_data.csv"
  },
  ...
}
```

---

### 📊 Get Models by Dataset
```http
GET /api/v1/models/dataset/{dataset_id}
Authorization: Bearer {token}
```

Returns all models trained with a specific dataset.

---

### ✏️ Update Model
```http
PUT /api/v1/models/{model_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "entrenado",
  "error_message": null
}
```

**Valid statuses:**
- `"entrenado"` - Mark as successfully trained
- `"en_entrenamiento"` - Still training
- `"error"` - Training failed (set error_message too)

---

### 🗑️ Delete Model
```http
DELETE /api/v1/models/{model_id}
Authorization: Bearer {token}
```

**What happens:**
1. ✅ Deletes model from database
2. ✅ Removes entire directory (`/app/storage/models/user_1/dataset_3/prophet_model/`)
3. ✅ Response: 204 No Content

---

## 📂 Storage Organization

### Directory Structure

```
/app/storage/models/
│
├── user_1/                          ← Each user has their own folder
│   ├── dataset_3/                   ← Each dataset has subfolder
│   │   ├── prophet/                 ← Each model has its folder
│   │   │   ├── model.pkl            ← Trained model binary
│   │   │   ├── metadata.json        ← Model metadata
│   │   │   ├── scaler.pkl           ← Preprocessing objects
│   │   │   └── ...
│   │   ├── arima/
│   │   │   ├── model.pkl
│   │   │   └── ...
│   │   └── lstm/
│   │       ├── model.h5
│   │       └── ...
│   │
│   └── dataset_5/
│       ├── xgboost/
│       └── ...
│
├── user_2/
│   ├── dataset_1/
│   │   └── random_forest/
│   └── dataset_8/
│       └── gradient_boosting/
│
└── user_3/
    └── ...
```

### Example Paths

```python
# When user 1 creates model "prophet" with dataset 3:
model_path = "/app/storage/models/user_1/dataset_3/prophet"

# To save the trained model:
model_file = "/app/storage/models/user_1/dataset_3/prophet/model.pkl"

# To save preprocessing info:
scaler_file = "/app/storage/models/user_1/dataset_3/prophet/scaler.pkl"

# Metadata about training:
metadata_file = "/app/storage/models/user_1/dataset_3/prophet/metadata.json"
```

---

## 🔒 Security & Permissions

### Access Control

**Only authenticated users can:**
- Create models
- View their own models
- Update their own models
- Delete their own models

**Cannot access:**
- ❌ Other users' models
- ❌ Other users' storage directories
- ❌ Endpoints without authentication token

**Validation in code:**
```python
# Every endpoint checks:
model = db.query(MLModel).filter(
    MLModel.id == model_id,
    MLModel.user_id == current_user.id  # ← Ensure ownership
).first()

if not model:
    raise HTTPException(status_code=404, detail="Model not found")
```

---

## 🎯 Frontend Integration Guide

### Step 1: Display Available Datasets
```javascript
// Call this endpoint to get user's datasets
const response = await fetch('/api/v1/datasets', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const datasets = await response.json();

// datasets = [
//   { id: 1, name: "sales_2024.csv" },
//   { id: 3, name: "weather_data.csv" },
//   ...
// ]
```

### Step 2: User Creates Model
```javascript
// User fills form:
const modelForm = {
  name: "prophet_sales",  // User-friendly name
  dataset_id: 3           // Selected from dropdown
};

// Send to API
const response = await fetch('/api/v1/models', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(modelForm)
});

const newModel = await response.json();
// newModel.id = 1
// newModel.status = "en_entrenamiento"
// newModel.model_path = "/app/storage/models/user_1/dataset_3/prophet_sales"
```

### Step 3: Display User's Models
```javascript
// Fetch all user's models
const response = await fetch('/api/v1/models', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const userModels = await response.json();

// Display in table/list:
// | ID | Name | Dataset | Status | Created | Actions |
// | 1  | prophet_sales | sales_2024.csv | en_entrenamiento | 2026-03-04 | Edit Delete |
// | 2  | lstm_temp | weather_data.csv | entrenado | 2026-03-03 | Edit Delete |
```

### Step 4: Update Model Status
```javascript
// After training completes (backend process)
await fetch(`/api/v1/models/${modelId}`, {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    status: "entrenado"  // Update status to trained
  })
});
```

### Step 5: Delete Model
```javascript
await fetch(`/api/v1/models/${modelId}`, {
  method: 'DELETE',
  headers: { 'Authorization': `Bearer ${token}` }
});
// Model deleted + directory removed
```

---

## ⚙️ Configuration

### Environment Variables (.env)

```env
# Storage paths
STORAGE_PATH=/app/storage
MODEL_STORAGE_PATH=/app/storage/models

# Database
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost/TFGdb

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Create Storage Directory
```bash
# Linux/macOS
mkdir -p /app/storage/models

# Windows (PowerShell)
New-Item -ItemType Directory -Path "C:\app\storage\models" -Force

# Windows (cmd)
mkdir C:\app\storage\models
```

---

## 📊 Database Diagram

```
usuarios (users)
├── id (PK)
├── email
├── password
├── tipo
└── created_at
    ├─────1────→ MANY ─── datasets
    │                    (user can have many datasets)
    │
    └─────1────→ MANY ─── ml_models
                         (user can have many models)

datasets
├── id (PK)
├── user_id (FK → usuarios.id)
├── name
└── created_at
    └─────1────→ MANY ─── ml_models
                         (dataset can train many models)

ml_models ✨ NEW TABLE
├── id (PK)
├── user_id (FK → usuarios.id)
├── dataset_id (FK → datasets.id)
├── name
├── model_path
├── status
├── error_message
└── created_at
```

---

## 🔄 Workflow Example

### Scenario: User "Juan" trains a model

```
1. Juan logs in → Gets token
   
2. Juan requests datasets
   GET /api/v1/datasets
   Response: [
     { id: 3, name: "sales_2024.csv" },
     { id: 5, name: "weather_2024.csv" }
   ]

3. Juan selects "sales_2024.csv" and names model "prophet_v1"
   POST /api/v1/models
   {
     "name": "prophet_v1",
     "dataset_id": 3
   }
   
   ✅ Creates: /app/storage/models/user_2/dataset_3/prophet_v1/
   ✅ Database record created with status="en_entrenamiento"

4. Backend training process:
   - Loads data from dataset 3
   - Trains model in /app/storage/models/user_2/dataset_3/prophet_v1/
   - Saves model.pkl and metadata.json

5. Backend updates status
   PUT /api/v1/models/{id}
   {
     "status": "entrenado"
   }

6. Juan views his models
   GET /api/v1/models
   Response: [
     {
       id: 1,
       name: "prophet_v1",
       dataset_id: 3,
       status: "entrenado",
       model_path: "/app/storage/models/user_2/dataset_3/prophet_v1",
       created_at: "2026-03-04T10:30:00Z"
     }
   ]

7. Juan deletes old model "prophet_v1"
   DELETE /api/v1/models/1
   ✅ Removes database record
   ✅ Deletes entire directory: /app/storage/models/user_2/dataset_3/prophet_v1/
```

---

## 🐛 Troubleshooting

### Issue: "Dataset not found or does not belong to the current user"
**Cause:** Dataset doesn't exist or belongs to another user
**Solution:** Verify dataset_id and that user owns the dataset

### Issue: "ML model not found"
**Cause:** Model ID doesn't exist or belongs to another user
**Solution:** Verify model_id and check user authentication

### Issue: Directory not created
**Cause:** Permission issues or incorrect STORAGE_PATH
**Solution:** Check file system permissions and .env configuration

### Issue: Model path not updating
**Cause:** Database transaction failed
**Solution:** Check error_message field and logs for details

---

## 📚 Related Documentation

- See [README.md](README.md) for general project setup
- See [STRUCTURE.md](STRUCTURE.md) for complete project architecture
- See [QUICKSTART.md](QUICKSTART.md) for quick setup guide

---

## ✅ Summary

The ML Models system provides:

✅ **Database Integration**
- Stores model metadata and relationships
- Tracks training status and errors
- Maintains audit trail (created_at)

✅ **Automatic Storage Management**
- Creates organized directory structure
- Enforces user/dataset/model hierarchy
- Automatic cleanup on deletion

✅ **RESTful APIs**
- Full CRUD operations
- Proper status codes
- Comprehensive error handling

✅ **Security**
- Authentication required
- User ownership validation
- Permission-based access control

✅ **Scalability**
- Ready for multiple concurrent trainings
- Organized file structure
- Metadata-driven design
