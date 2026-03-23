# 📚 COMPLETE USAGE GUIDE

Step-by-step guide for using the TFG ML Platform.

## 📋 TABLE OF CONTENTS

1. [Getting Started](#getting-started)
2. [User Registration & Setup](#user-registration--setup)
3. [Uploading Data](#uploading-data)
4. [Creating Models](#creating-models)
5. [Making Predictions](#making-predictions)
6. [Visualizing Results](#visualizing-results)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## GETTING STARTED

### Prerequisites
- Internet connection
- API base URL: `http://localhost:8000` (development) or your deployment URL
- API key/token: (provided after registration)

### API Documentation Reference
- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

---

## USER REGISTRATION & SETUP

### Step 1: Register Account

**Endpoint**: `POST /api/v1/auth/register`

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "myusername",
    "email": "my.email@example.com",
    "password": "SecurePassword123!",
    "full_name": "My Full Name"
  }'
```

**Response**:
```json
{
  "id": 1,
  "username": "myusername",
  "email": "my.email@example.com",
  "full_name": "My Full Name",
  "created_at": "2024-03-11T10:30:00"
}
```

**Password Requirements**:
- Minimum 8 characters
- At least one uppercase letter (A-Z)
- At least one number (0-9)
- At least one special character (!@#$%^&*)

---

### Step 2: Login & Get Token

**Endpoint**: `POST /api/v1/auth/login`

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "myusername",
    "password": "SecurePassword123!"
  }'
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Store the `access_token`** - You'll need it for all subsequent requests!

### Using the Token

Add it to the Authorization header:
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     http://localhost:8000/api/v1/usuarios/me
```

---

## UPLOADING DATA

### Requirements

Data must be in **CSV format** with exactly **2 columns**:
1. **Date column** (format: YYYY-MM-DD or any ISO format)
2. **Value column** (numeric: integer or float)

### Example CSV Format

```csv
fecha,valor
2024-01-01,100
2024-01-02,105
2024-01-03,103
2024-01-04,108
2024-01-05,110
```

### Upload File

**Endpoint**: `POST /api/v1/files/upload`

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/data.csv"
```

**Response**:
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

### Common Issues

| Issue | Solution |
|-------|----------|
| **"Invalid file type"** | Ensure file is CSV, not Excel or other format |
| **"File too large"** | Max size is 50MB. Split large files. |
| **"Invalid CSV structure"** | Check that you have exactly 2 columns with a date and a numeric value |
| **"Invalid date format"** | Use ISO format: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS |

### Retrieve File List

**Endpoint**: `GET /api/v1/files/my-files`

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     http://localhost:8000/api/v1/files/my-files
```

**Response**:
```json
[
  {
    "id": 1,
    "filename": "sales_2024.csv",
    "file_size": 2048,
    "file_type": "csv",
    "upload_date": "2024-03-11T10:30:00"
  },
  ...
]
```

---

## CREATING MODELS

### Supported Models

1. **Prophet** - Additive/multiplicative seasonal decomposition
2. **ARIMA** - AutoRegressive Integrated Moving Average with auto-parameter search

### Create Prophet Model

**Endpoint**: `POST /api/v1/models`

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/models" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "sales_forecast_prophet",
    "model_type": "prophet",
    "dataset_id": 1
  }'
```

**Response** (201 Created):
```json
{
  "id": 1,
  "name": "sales_forecast_prophet",
  "model_type": "prophet",
  "dataset_id": 1,
  "status": "en_entrenamiento",
  "model_path": "/storage/models/user_1/dataset_1/sales_forecast_prophet",
  "created_at": "2024-03-11T10:30:00",
  "error_message": null
}
```

⏳ **Training starts immediately in the background!**

### Create ARIMA Model

**Endpoint**: `POST /api/v1/models`

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/models" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "sales_forecast_arima",
    "model_type": "arima",
    "dataset_id": 1
  }'
```

**Special Features of ARIMA**:
- ✅ Auto-searches optimal (p, d, q) parameters
- ✅ Uses ADF test for stationarity
- ✅ Detects and warns about outliers
- ✅ Validates data sufficiency (minimum 50 observations)

### Check Model Status

**Endpoint**: `GET /api/v1/models/{model_id}`

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     http://localhost:8000/api/v1/models/1
```

**Possible Status Values**:
- `en_entrenamiento` - Currently training (wait for completion)
- `entrenado` - Ready for predictions (✅ training successful)
- `error` - Training failed (check error_message)

### List All Your Models

**Endpoint**: `GET /api/v1/models`

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     http://localhost:8000/api/v1/models
```

---

## MAKING PREDICTIONS

### Prophet Predictions

**Endpoint**: `POST /api/v1/predictions/predict`

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/predictions/predict" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": 1,
    "periods": 30
  }'
```

**Response** (200 OK):
```json
{
  "model_id": 1,
  "model_name": "sales_forecast_prophet",
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

**Fields Explained**:
- `ds` - Prediction date
- `yhat` - Predicted value (mean)
- `yhat_lower` - Lower confidence bound (80%)
- `yhat_upper` - Upper confidence bound (80%)
- `trend` - Trend component
- `yearly` - Yearly seasonality component

### ARIMA Predictions

**Endpoint**: `POST /api/v1/predictions/arima/predict`

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/predictions/arima/predict" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": 2,
    "periods": 30
  }'
```

**Response** (200 OK):
```json
{
  "model_id": 2,
  "model_name": "sales_forecast_arima",
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

**ARIMA-Specific Fields**:
- `order` - ARIMA(p,d,q) parameters found automatically
- `aic` / `bic` - Model selection criteria (lower is better)
- `rmse` / `mae` - Prediction error metrics

---

## VISUALIZING RESULTS

### Generate Prophet Plot

**Endpoint**: `GET /api/v1/predictions/plots/prophet/{model_id}`

**Request**:
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     "http://localhost:8000/api/v1/predictions/plots/prophet/1?periods=30&historical_periods=50"
```

**Query Parameters**:
- `periods` (default: 30) - Days to forecast
- `historical_periods` (default: 50) - Historical days to show

**Response** (200 OK):
```json
{
  "model_id": 1,
  "model_name": "sales_forecast_prophet",
  "model_type": "prophet",
  "image": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "parameters": {
    "future_periods": 30,
    "historical_periods": 50,
    "rmse": 15.23,
    "mae": 12.45
  },
  "created_at": "2024-03-11T10:30:00"
}
```

### Generate ARIMA Plot

**Endpoint**: `GET /api/v1/predictions/plots/arima/{model_id}`

**Request**:
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     "http://localhost:8000/api/v1/predictions/plots/arima/2?periods=30&historical_periods=50"
```

**Response**: Similar to Prophet (includes model-specific parameters)

### Using the Plot Image

The `image` field contains a **base64-encoded PNG**. Use it in:

**HTML**:
```html
<img src="data:image/png;base64,iVBORw0KGgo..." alt="Forecast">
```

**Python**:
```python
import base64
from PIL import Image
import io

# Extract base64
b64_string = response['image'].replace('data:image/png;base64,', '')
image_data = base64.b64decode(b64_string)
image = Image.open(io.BytesIO(image_data))
image.show()
```

**Save as File**:
```python
import base64

b64_string = response['image'].replace('data:image/png;base64,', '')
with open('forecast.png', 'wb') as f:
    f.write(base64.b64decode(b64_string))
```

---

## BEST PRACTICES

### Data Preparation

✅ **DO**:
- Use at least 50-100 observations for accurate models
- Ensure consistent time intervals (daily, weekly, monthly)
- Remove obvious data errors (negative values if they're impossible)
- Use recent data (models assume historical patterns continue)

❌ **DON'T**:
- Use sparse or irregular time series
- Mix different time intervals in one dataset
- Include structural breaks (model won't handle major changes)
- Use extremely short datasets (<50 points)

### Model Selection

| Use Prophet when... | Use ARIMA when... |
|-------------------|------------------|
| Data has clear seasonality | Simple, stationary time series |
| Strong yearly/weekly patterns | Short-term forecasting (1-30 days) |
| Need component decomposition | Automated parameter search preferred |
| Have domain knowledge of holidays | Limited domain knowledge |

### Prediction Horizon

**Recommended time horizons**:
- **Short-term**: 1-7 periods (most accurate)
- **Medium-term**: 8-30 periods (good accuracy)
- **Long-term**: 31-365 periods (use with caution)

**Why short-term is better**:
- Forecasts degrade over long horizons
- Confidence intervals widen
- Assumes historical patterns continue

### Model Comparison

Create multiple models and compare:

```python
# Get both forecasts
prophet_forecast = predict_prophet(model_id=1, periods=30)
arima_forecast = predict_arima(model_id=2, periods=30)

# Compare mean values
prophet_avg = mean(prophet_forecast['forecast'].yhat)
arima_avg = mean(arima_forecast['forecast'].yhat)

# Average both forecasts for ensemble prediction
ensemble = (prophet_avg + arima_avg) / 2
```

---

## TROUBLESHOOTING

### Model Training Won't Complete

**Problem**: Status stays `en_entrenamiento` after 5 minutes

**Solutions**:
1. Check server logs for errors
2. Verify dataset has enough data (>50 rows for ARIMA)
3. Check for invalid data in CSV (NaN, inf, non-numeric values)
4. Delete model and try again

### Prediction Returns 404 Error

**Problem**: "Model not found"

**Solutions**:
1. Verify model is fully trained (status: `entrenado`)
2. Check model_id is correct: `GET /api/v1/models`
3. Ensure you're using your own model (not another user's)
4. Try refreshing: `GET /api/v1/models/{model_id}`

### Prediction Accuracy is Poor

**Problem**: Forecasts don't match expectations

**Solutions**:
1. **Increase historical data**: Use longer time series (1-2 years)
2. **Check for outliers**: Remove anomalies before training
3. **Try different model**: Compare Prophet vs ARIMA
4. **Validate data quality**: Ensure no missing values
5. **Check seasonality**: Models work better with seasonal data

### File Upload Fails

**Problem**: "Invalid CSV structure"

**Solutions**:
1. Verify exactly 2 columns
2. Check column headers (must exist)
3. Validate all values are numeric or dates
4. Check file encoding (should be UTF-8)
5. Remove empty rows/columns

**Example Valid CSV**:
```csv
date,value
2024-01-01,100
2024-01-02,105
```

### Authorization Errors

**Problem**: "Unauthorized" (401) or "Forbidden" (403)

**Solutions**:
1. Verify token in Authorization header
2. Check token hasn't expired (24 hours)
3. Re-login to get new token: `POST /auth/login`
4. Include correct header format: `Authorization: Bearer TOKEN`

---

## API RATE LIMITS

- **General endpoints**: 100 requests/minute
- **Prediction endpoints**: 50 requests/minute (intensive operations)
- **Auth endpoints**: No limit

When rate limited, you'll receive:
```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds."
}
```

Solution: Wait before retrying.

---

## DATA RETENTION

- **User data**: Kept as long as account active
- **Models**: Kept as long as dataset active (delete model to free space)
- **Upload files**: Can be deleted manually via `DELETE /api/v1/files/{id}`
- **Predictions**: Not stored (generated on-demand)

