# API Quick Reference - Lovable Ready

**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** Bearer token (JWT) - 30 min expiry  
**Content-Type:** `application/json`

---

## 🔓 AUTHENTICATION (2 Endpoints)

### POST /auth/register
Create user account
```json
REQUEST: { "email": "user@test.com", "password": "Pass123!", "username": "testuser" }
RESPONSE (201): { "id": 1, "email": "user@test.com", "username": "testuser" }
```

### POST /auth/login
Get JWT token
```json
REQUEST: { "email": "user@test.com", "password": "Pass123!" }
RESPONSE (200): { "access_token": "eyJ...", "token_type": "bearer" }
```

---

## 👤 USERS (3 Endpoints)

### GET /users/me
Get logged-in user profile
```json
HEADERS: { "Authorization": "Bearer {token}" }
RESPONSE (200): { "id": 1, "email": "user@test.com", "username": "testuser" }
```

### GET /users/email/{email}
Get user by email
```json
HEADERS: { "Authorization": "Bearer {token}" }
RESPONSE (200): { "id": 1, "email": "user@test.com", "username": "testuser" }
ERROR (404): { "detail": "Usuario no encontrado" }
```

### PUT /users/me
Update user profile
```json
HEADERS: { "Authorization": "Bearer {token}" }
REQUEST: { "username": "newusername", "password": "NewPass123!" }
RESPONSE (200): { "id": 1, "email": "user@test.com", "username": "newusername" }
```

---

## 📁 FILES (3 Endpoints)

### POST /files/upload
Upload CSV/XLSX file
```json
HEADERS: { "Authorization": "Bearer {token}" }
REQUEST: FormData { "file": <binary>, "dataset_name": "mi_dataset" }
RESPONSE (201): { "id": 1, "filename": "data.csv", "dataset_name": "mi_dataset", "rows": 100 }
ERROR (400): { "detail": "Formato no soportado o archivo vacío" }
```

### GET /files/list
List user's uploaded files
```json
HEADERS: { "Authorization": "Bearer {token}" }
RESPONSE (200): [
  { "id": 1, "filename": "data.csv", "dataset_name": "dataset1", "rows": 100 },
  { "id": 2, "filename": "data2.csv", "dataset_name": "dataset2", "rows": 50 }
]
```

### DELETE /files/{file_id}
Delete uploaded file
```json
HEADERS: { "Authorization": "Bearer {token}" }
RESPONSE (200): { "message": "Archivo eliminado" }
ERROR (404): { "detail": "Archivo no encontrado" }
```

---

## 📊 DATASETS (4 Endpoints)

### GET /datasets
List all user datasets
```json
HEADERS: { "Authorization": "Bearer {token}" }
RESPONSE (200): [
  { "id": 1, "name": "dataset1", "created_at": "2026-03-20", "file_count": 1 },
  { "id": 2, "name": "dataset2", "created_at": "2026-03-21", "file_count": 2 }
]
```

### GET /datasets/{dataset_id}
Get dataset details with data points
```json
HEADERS: { "Authorization": "Bearer {token}" }
RESPONSE (200): {
  "id": 1, "name": "dataset1", "created_at": "2026-03-20",
  "data": [
    { "date": "2026-01-01", "value": 100.5 },
    { "date": "2026-01-02", "value": 102.3 }
  ]
}
ERROR (404): { "detail": "Dataset no encontrado" }
```

### POST /datasets
Create new dataset
```json
HEADERS: { "Authorization": "Bearer {token}" }
REQUEST: { "name": "nuevo_dataset" }
RESPONSE (201): { "id": 3, "name": "nuevo_dataset", "created_at": "2026-03-23" }
```

### DELETE /datasets/{dataset_id}
Delete dataset
```json
HEADERS: { "Authorization": "Bearer {token}" }
RESPONSE (200): { "message": "Dataset eliminado" }
ERROR (404): { "detail": "Dataset no encontrado" }
```

---

## 🤖 ML MODELS (5 Endpoints)

### POST /ml/create
Create and train ML model
```json
HEADERS: { "Authorization": "Bearer {token}" }
REQUEST: {
  "model_name": "modelo_prophet",
  "model_type": "prophet",  // or "arima"
  "dataset_id": 1,
  "train_size_percent": 80,
  "order": [1, 0, 1]  // ONLY for ARIMA: (p,d,q)
}
RESPONSE (201): {
  "id": 1, "model_name": "modelo_prophet", "model_type": "prophet",
  "status": "entrenando", "created_at": "2026-03-23"
}
```

### GET /ml
List user's ML models
```json
HEADERS: { "Authorization": "Bearer {token}" }
RESPONSE (200): [
  { "id": 1, "model_name": "modelo1", "model_type": "prophet", "status": "completado" },
  { "id": 2, "model_name": "modelo2", "model_type": "arima", "status": "entrenando" }
]
```

### GET /ml/{model_id}
Get model details and status
```json
HEADERS: { "Authorization": "Bearer {token}" }
RESPONSE (200): {
  "id": 1, "model_name": "modelo1", "model_type": "prophet", "status": "completado",
  "dataset_id": 1, "train_size_percent": 80,
  "metrics": { "rmse": 15.3, "mae": 12.1, "mape": 5.2 }
}
ERROR (404): { "detail": "Modelo no encontrado" }
```

### GET /ml/by-dataset/{dataset_id}
Get all models for a dataset
```json
HEADERS: { "Authorization": "Bearer {token}" }
RESPONSE (200): [
  { "id": 1, "model_name": "modelo1", "model_type": "prophet" },
  { "id": 2, "model_name": "modelo2", "model_type": "arima" }
]
ERROR (404): { "detail": "Dataset no encontrado" }
```

### DELETE /ml/{model_id}
Delete model
```json
HEADERS: { "Authorization": "Bearer {token}" }
RESPONSE (200): { "message": "Modelo eliminado" }
ERROR (404): { "detail": "Modelo no encontrado" }
```

---

## 🔮 PREDICTIONS (3 Endpoints)

### POST /predict
Make prediction with trained model
```json
HEADERS: { "Authorization": "Bearer {token}" }
REQUEST: {
  "model_id": 1,
  "periods": 30  // days ahead
}
RESPONSE (200): {
  "model_id": 1, "periods_predicted": 30,
  "predictions": [
    { "date": "2026-04-01", "value": 150.2, "lower_bound": 145.1, "upper_bound": 155.3 },
    { "date": "2026-04-02", "value": 151.5, "lower_bound": 145.8, "upper_bound": 157.2 }
  ]
}
ERROR (404): { "detail": "Modelo no encontrado o no entrenado" }
```

### GET /predict/plot/{model_id}
Get prediction plot (PNG)
```json
HEADERS: { "Authorization": "Bearer {token}" }
RESPONSE (200): <PNG binary data>
ERROR (404): { "detail": "Modelo no encontrado" }
```

### GET /predict/training-data/{model_id}
Get training data used for model
```json
HEADERS: { "Authorization": "Bearer {token}" }
RESPONSE (200): {
  "model_id": 1,
  "training_data": [
    { "date": "2026-01-01", "value": 100.5 },
    { "date": "2026-01-02", "value": 102.3 }
  ]
}
ERROR (404): { "detail": "Modelo no encontrado" }
```

---

## 📈 METRICS HELP (1 Endpoint - No Auth Required)

### GET /metrics-help/{metric_name}
Get explanation for metric
```json
METRIC_NAMES: rmse | mae | aic | bic | order | data_points
RESPONSE (200): {
  "label": "RMSE (Root Mean Square Error)",
  "description": "Error promedio del modelo en unidades originales",
  "interpretation": "Cuanto más bajo, mejor. Penaliza errores grandes.",
  "unit": "unidades originales",
  "benchmark": "< 10% del promedio de tus datos = ✅ Excelente",
  "examples": [...]
}
ERROR (404): { "detail": "Métrica no encontrada" }
```

---

## ❤️ HEALTH (2 Endpoints - No Auth Required)

### GET /health
Check API status
```json
RESPONSE (200): { "status": "ok" }
```

### GET /
API root
```json
RESPONSE (200): { "message": "API de Series Temporales v1.0" }
```

---

## 📋 COMMON ERROR CODES

| Code | Message | Cause |
|------|---------|-------|
| 400 | `Bad Request` | Invalid JSON/params |
| 401 | `Unauthorized` | Missing/invalid token |
| 403 | `Forbidden` | Token expired (>30 min) |
| 404 | `Not Found` | Resource doesn't exist |
| 422 | `Validation Error` | Invalid field types |
| 500 | `Internal Server Error` | Backend crash |

---

## 🚀 QUICK START FOR LOVABLE

**Step 1:** User registers (POST /auth/register)  
**Step 2:** User logs in (POST /auth/login) → get token  
**Step 3:** User uploads CSV (POST /files/upload)  
**Step 4:** Create dataset (POST /datasets)  
**Step 5:** Train model (POST /ml/create) → status="entrenando"  
**Step 6:** Poll model status (GET /ml/{model_id}) until status="completado"  
**Step 7:** Get predictions (POST /predict)  
**Step 8:** Get metrics help (GET /metrics-help/{metric}) for explanations  

---

## 📊 DATA MODELS (DB Schema)

### Usuario
```
id (int), email (str), username (str), password_hash (str)
```

### Dataset
```
id (int), user_id (int), name (str), created_at (datetime)
```

### Data (time series points)
```
id (int), dataset_id (int), date (date), value (float)
```

### MLModel
```
id (int), user_id (int), model_name (str), model_type (str),
dataset_id (int), status (enum: pendiente|entrenando|completado|error),
train_size_percent (int), metrics (json), created_at (datetime)
```

---

**Total Endpoints:** 23  
**Authentication:** JWT Bearer token (except /health, /metrics-help/*, /)  
**Models:** Prophet + ARIMA
