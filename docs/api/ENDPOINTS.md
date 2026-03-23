# 🔮 API ENDPOINTS DOCUMENTATION

Documentación completa de todos los endpoints de la API TFG ML Platform.

## 📋 TABLE OF CONTENTS

1. [🔐 Authentication](#authentication)
2. [👤 User Management](#user-management)
3. [📁 File Management](#file-management)
4. [📊 Datasets](#datasets)
5. [🤖 ML Models](#ml-models)
6. [🔮 Predictions (Prophet)](#predictions-prophet)
7. [🔮 Predictions (ARIMA)](#predictions-arima)

---

# 🔐 AUTHENTICATION

## POST /api/v1/auth/register

**Register a new user**

### Request
```json
{
  "username": "string (3-50 chars)",
  "email": "valid@email.com",
  "password": "string (min 8 chars, uppercase, number, special char)",
  "full_name": "string"
}
```

### Response (201 Created)
```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "full_name": "string",
  "created_at": "2024-03-11T10:30:00"
}
```

### Error Cases
- `400`: Username already exists
- `422`: Invalid data format or password too weak

---

## POST /api/v1/auth/login

**Authenticate user and get token**

### Request
```json
{
  "username": "string",
  "password": "string"
}
```

### Response (200 OK)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Error Cases
- `401`: Invalid username or password
- `404`: User not found

---

# 👤 USER MANAGEMENT

All endpoints require authentication header: `Authorization: Bearer <token>`

## GET /api/v1/usuarios/me

**Get current user profile**

### Response (200 OK)
```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "full_name": "string",
  "created_at": "2024-03-11T10:30:00"
}
```

### Error Cases
- `401`: Unauthorized (no valid token)

---

## GET /api/v1/usuarios/{user_id}

**Get user profile by ID**

### Response (200 OK)
```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "full_name": "string",
  "created_at": "2024-03-11T10:30:00"
}
```

### Error Cases
- `401`: Unauthorized
- `404`: User not found

---

## PUT /api/v1/usuarios/{user_id}

**Update user profile**

### Request
```json
{
  "full_name": "string (optional)",
  "email": "string (optional)"
}
```

### Response (200 OK)
```json
{
  "id": 1,
  "username": "string",
  "email": "string (updated)",
  "full_name": "string (updated)",
  "created_at": "2024-03-11T10:30:00"
}
```

### Error Cases
- `401`: Unauthorized
- `404`: User not found
- `403`: Cannot modify other users

---

## DELETE /api/v1/usuarios/{user_id}

**Delete user account**

### Response (204 No Content)
Empty response

### Error Cases
- `401`: Unauthorized
- `404`: User not found
- `403`: Cannot delete other users

---

## DELETE /api/v1/usuarios/datos

**Delete all user data (GDPR)**

### Response (204 No Content)
Empty response - deletes all datasets, models, files

### Error Cases
- `401`: Unauthorized

---

# 📁 FILE MANAGEMENT

All endpoints require authentication.

## POST /api/v1/files/upload

**Upload a CSV file**

### Request
- Multipart form
- File field: `file` (CSV format)
- Accepted: `.csv`, `.json` (time series format)

### Response (201 Created)
```json
{
  "id": 1,
  "filename": "data.csv",
  "file_size": 2048,
  "file_type": "csv",
  "upload_date": "2024-03-11T10:30:00",
  "status": "processed"
}
```

### Error Cases
- `400`: Invalid file type
- `413`: File too large (>50MB)
- `422`: Malformed file

---

## GET /api/v1/files/my-files

**List all uploaded files**

### Response (200 OK)
```json
[
  {
    "id": 1,
    "filename": "data.csv",
    "file_size": 2048,
    "file_type": "csv",
    "upload_date": "2024-03-11T10:30:00"
  },
  ...
]
```

---

## GET /api/v1/files/{file_id}

**Get file metadata**

### Response (200 OK)
```json
{
  "id": 1,
  "filename": "data.csv",
  "file_size": 2048,
  "file_type": "csv",
  "upload_date": "2024-03-11T10:30:00",
  "status": "processed"
}
```

### Error Cases
- `404`: File not found

---

## DELETE /api/v1/files/{file_id}

**Delete uploaded file**

### Response (200 OK)
```json
{
  "message": "File deleted successfully"
}
```

### Error Cases
- `404`: File not found

---

# 📊 DATASETS

All endpoints require authentication.

## GET /api/v1/datasets

**List all user datasets**

### Response (200 OK)
```json
[
  {
    "id": 1,
    "name": "ventas_2024",
    "file_id": 1,
    "row_count": 365,
    "created_at": "2024-03-11T10:30:00",
    "columns": ["fecha", "valor"]
  },
  ...
]
```

---

## GET /api/v1/datasets/id/{dataset_id}/data

**Get dataset by ID with data**

### Query Parameters
- `limit` (optional): Max rows to return (default: 1000)
- `offset` (optional): Offset for pagination

### Response (200 OK)
```json
{
  "id": 1,
  "name": "ventas_2024",
  "total_rows": 365,
  "columns": ["fecha", "valor"],
  "data": [
    {"fecha": "2024-01-01", "valor": 100},
    ...
  ]
}
```

### Error Cases
- `404`: Dataset not found

---

## GET /api/v1/datasets/{dataset_name}/data

**Get dataset by name with data**

### Query Parameters
- `limit` (optional): Max rows to return
- `offset` (optional): Offset for pagination

### Response (200 OK)
```json
{
  "id": 1,
  "name": "ventas_2024",
  "data": [...]
}
```

### Error Cases
- `404`: Dataset not found

---

# 🤖 ML MODELS

All endpoints require authentication.

## POST /api/v1/models

**Create new ML model (auto-trains)**

### Request
```json
{
  "name": "model_name (unique per user)",
  "model_type": "prophet | arima",
  "dataset_id": 1
}
```

### Response (201 Created)
```json
{
  "id": 1,
  "name": "model_name",
  "model_type": "prophet",
  "dataset_id": 1,
  "status": "en_entrenamiento",
  "model_path": "/storage/models/user_1/dataset_1/model_name",
  "created_at": "2024-03-11T10:30:00",
  "error_message": null
}
```

### Workflow
1. Model created with status `en_entrenamiento`
2. Background task starts training
3. Status changes to `entrenado` or `error`
4. Check status with GET /models/{id}

### Error Cases
- `400`: Duplicate model name for user
- `404`: Dataset not found
- `422`: Invalid model type

---

## GET /api/v1/models

**List all user models**

### Response (200 OK)
```json
[
  {
    "id": 1,
    "name": "model_name",
    "model_type": "prophet",
    "status": "entrenado",
    "created_at": "2024-03-11T10:30:00"
  },
  ...
]
```

---

## GET /api/v1/models/dataset/{dataset_id}

**Get models by dataset**

### Response (200 OK)
```json
[
  {
    "id": 1,
    "name": "model_name",
    "model_type": "prophet",
    "status": "entrenado",
    "dataset_id": 1
  },
  ...
]
```

### Error Cases
- `404`: Dataset not found

---

## GET /api/v1/models/{model_id}

**Get model details**

### Response (200 OK)
```json
{
  "id": 1,
  "name": "model_name",
  "model_type": "prophet",
  "dataset_id": 1,
  "status": "entrenado",
  "model_path": "/storage/models/...",
  "created_at": "2024-03-11T10:30:00",
  "error_message": null,
  "user": {
    "id": 1,
    "username": "user"
  },
  "dataset": {
    "id": 1,
    "name": "dataset_name"
  }
}
```

### Error Cases
- `404`: Model not found

---

## PUT /api/v1/models/{model_id}

**Update model information**

### Request
```json
{
  "name": "new_name (optional)",
  "status": "entrenado | error (optional)",
  "error_message": "string (optional)"
}
```

### Response (200 OK)
Updated model object

### Error Cases
- `404`: Model not found

---

## DELETE /api/v1/models/{model_id}

**Delete model and remove files**

### Response (204 No Content)
Empty response

### Error Cases
- `404`: Model not found

---

# 🔮 PREDICTIONS (PROPHET)

All endpoints require authentication.

## POST /api/v1/predictions/predict

**Generate Prophet predictions**

### Request
```json
{
  "model_id": 1,
  "periods": 30  (1-365)
}
```

### Response (200 OK)
```json
{
  "model_id": 1,
  "model_name": "model_name",
  "model_path": "/storage/...",
  "dataset_id": 1,
  "periods": 30,
  "forecast": [
    {
      "ds": "2024-04-11",
      "yhat": 125.5,
      "yhat_lower": 120.2,
      "yhat_upper": 130.8,
      "trend": 0.5,
      "yearly": 2.3
    },
    ...
  ],
  "created_at": "2024-03-11T10:30:00"
}
```

### Error Cases
- `404`: Model not found or not trained
- `400`: Model type is not Prophet
- `422`: Invalid periods

---

## GET /api/v1/predictions/plots/prophet/{model_id}

**Generate Prophet forecast plot**

### Query Parameters
- `periods` (default: 30)
- `historical_periods` (default: 50)

### Response (200 OK)
```json
{
  "model_id": 1,
  "model_name": "model_name",
  "model_type": "prophet",
  "image": "data:image/png;base64,...",
  "parameters": {
    "future_periods": 30,
    "historical_periods": 50,
    "rmse": 15.23,
    "mae": 12.45
  },
  "created_at": "2024-03-11T10:30:00"
}
```

---

## GET /api/v1/predictions/models/{model_id}/info

**Get Prophet model info**

### Response (200 OK)
```json
{
  "model_id": 1,
  "model_name": "model_name",
  "model_type": "prophet",
  "status": "entrenado",
  "parameters": {
    "interval_width": 0.95,
    "seasonality_mode": "additive"
  },
  "metrics": {
    "rmse": 15.23,
    "mae": 12.45
  }
}
```

---

# 🔮 PREDICTIONS (ARIMA)

All endpoints require authentication.

## POST /api/v1/predictions/arima/predict

**Generate ARIMA predictions**

### Request
```json
{
  "model_id": 1,
  "periods": 30  (1-365)
}
```

### Response (200 OK)
```json
{
  "model_id": 1,
  "model_name": "model_name",
  "model_type": "arima",
  "dataset_id": 1,
  "periods": 30,
  "forecast": [
    {
      "date": "2024-04-11",
      "yhat": 125.5,
      "yhat_lower": 120.2,
      "yhat_upper": 130.8
    },
    ...
  ],
  "params": {
    "order": [1, 1, 1],
    "periods": 30,
    "confidence": 0.95
  },
  "metadata": {
    "aic": 256.3,
    "bic": 263.1,
    "rmse": 15.23,
    "mae": 12.45
  },
  "created_at": "2024-03-11T10:30:00"
}
```

### Error Cases
- `404`: Model not found or not trained
- `400`: Model type is not ARIMA
- `422`: Invalid periods

---

## GET /api/v1/predictions/arima/models/{model_id}/info

**Get ARIMA model info**

### Response (200 OK)
```json
{
  "model_id": 1,
  "model_name": "model_name",
  "model_type": "arima",
  "status": "entrenado",
  "parameters": {
    "order": [1, 1, 1],
    "aic": 256.3,
    "bic": 263.1,
    "rmse": 15.23,
    "mae": 12.45,
    "longitud": 100
  }
}
```

---

## GET /api/v1/predictions/arima/models/{model_id}/training-data

**Get ARIMA training data**

### Query Parameters
- `samples` (default: 100): Number of samples to return

### Response (200 OK)
```json
{
  "model_id": 1,
  "model_name": "model_name",
  "training_data": [
    {
      "date": "2024-01-01",
      "y": 100
    },
    ...
  ],
  "total_training_points": 365
}
```

---

## GET /api/v1/predictions/plots/arima/{model_id}

**Generate ARIMA forecast plot**

### Query Parameters
- `periods` (default: 30)
- `historical_periods` (default: 50)

### Response (200 OK)
```json
{
  "model_id": 1,
  "model_name": "model_name",
  "model_type": "arima",
  "image": "data:image/png;base64,...",
  "parameters": {
    "order": [1, 1, 1],
    "future_periods": 30,
    "historical_periods": 50,
    "aic": 256.3,
    "bic": 263.1,
    "rmse": 15.23,
    "mae": 12.45
  },
  "created_at": "2024-03-11T10:30:00"
}
```

---

## ERROR HANDLING

### Standard Error Response
```json
{
  "detail": "Error message",
  "status_code": 400
}
```

### Common Status Codes
- `200`: Success
- `201`: Created
- `204`: No Content (successful delete)
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `500`: Server Error

---

## AUTHENTICATION

All endpoints except `/auth/register` and `/auth/login` require:

```
Authorization: Bearer {access_token}
```

#### Example
```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
     https://api.tfg.local/api/v1/usuarios/me
```

---

## RATE LIMITING

- **Default**: 100 requests per minute
- **Auth endpoints**: No limit
- **Prediction endpoints**: 50 per minute (intensive operations)

---

## PAGINATION

For list endpoints:
- Default limit: 100
- Max limit: 1000
- Sort by: created_at (default, descending)

### Example
```
GET /api/v1/datasets?limit=50&offset=100
```

---

## VERSIONING

API routes use `/api/v1/` prefix. Future versions will be available at `/api/v2/`, etc.

