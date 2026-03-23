# 🎓 TFG ML Platform - Complete Documentation

**Trabajo de Fin de Grado: Machine Learning Time-Series Forecasting Platform**

A modern, production-ready REST API for time-series forecasting using Prophet and ARIMA models with automatic training, predictions, and interactive visualizations.

---

## 📚 Documentation Structure

```
docs/
├── README.md (you are here)
├── api/
│   └── ENDPOINTS.md ..................... Complete API reference
├── architecture/
│   └── ARCHITECTURE.md .................. System design & components
└── guides/
    └── USAGE_GUIDE.md ................... Step-by-step user guide
```

---

## 🎯 Quick Navigation

| Section | Purpose | Link |
|---------|---------|------|
| 📖 **Getting Started** | Installation & setup | See [Setup](#setup) below |
| 🔌 **API Endpoints** | All endpoints with examples | [api/ENDPOINTS.md](api/ENDPOINTS.md) |
| 🏗️ **Architecture** | System design & workflows | [architecture/ARCHITECTURE.md](architecture/ARCHITECTURE.md) |
| 📘 **Usage Guide** | Step-by-step tutorial | [guides/USAGE_GUIDE.md](guides/USAGE_GUIDE.md) |

---

## 🚀 SETUP

### Prerequisites
- Python 3.10+
- pip or conda
- 2GB RAM minimum

### Quick Start
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialize database
python rebuild_db.py

# 3. Start server
python main.py

# 4. Access API
# Interactive docs: http://localhost:8000/docs
```

---

## 📊 PROJECT OVERVIEW

This platform provides:
- ✅ **User Management**: Secure JWT authentication
- ✅ **Data Upload**: CSV time-series management
- ✅ **Prophet Models**: Seasonal decomposition forecasting
- ✅ **ARIMA Models**: Auto-parameter search forecasting
- ✅ **Predictions**: Automatic forecast generation
- ✅ **Visualization**: Base64-encoded PNG charts
- ✅ **API**: Complete REST API with comprehensive docs

---

## 📖 DOCUMENTATION BY TOPIC

- **[API Reference](api/ENDPOINTS.md)** - All endpoints, requests, responses
- **[Architecture](architecture/ARCHITECTURE.md)** - System design, workflows, components
- **[Usage Guide](guides/USAGE_GUIDE.md)** - Step-by-step tutorials and examples
- **[Testing](../tests/README.md)** - Test suite and coverage

---

## 🤖 ML MODELS

### Prophet
- Seasonal decomposition
- Trend & holiday detection
- Additive/multiplicative seasonality
- Best for: Daily/weekly/yearly patterns

### ARIMA / SARIMA (NEW!)
- AutoRegressive Integrated Moving Average / Seasonal ARIMA
- **Automatic model selection**: Detects seasonality → Chooses ARIMA or SARIMA
- Automatic (p,d,q) or (p,d,q)(P,D,Q,m) parameter search
- Detects estacionalidad automáticamente mediante descomposición seasonal_decompose
- **Best for**: Short-term univariate forecasting with optional seasonality

---

## 🔐 Security Highlights

- JWT token-based authentication
- Password hashing with bcrypt
- Row-level access control
- HTTPS-ready
- Input validation on all endpoints

---

## 📁 Project Structure

```
app/
├── api/v1/endpoints/    # REST API endpoints
├── ml/                  # ML modules (Prophet, ARIMA)
├── models/             # Database models
├── services/           # Business logic
└── security/           # Authentication

docs/
├── api/                # API documentation
├── architecture/       # System design
└── guides/            # User guides

tests/                  # Test suite
storage/               # Model storage
```

---

## 🚀 DEPLOYMENT

### Development
```bash
python main.py
```

### Production
```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Docker
```bash
docker-compose up -d
```

---

## ✅ STATUS

**Version**: 1.0.0 - Production Ready

All features implemented:
- [x] Authentication
- [x] File upload
- [x] Prophet models
- [x] ARIMA models (with auto_arima)
- [x] Predictions
- [x] Visualizations
- [x] Testing
- [x] Documentation

---

## 📞 SUPPORT

- **API Docs**: http://localhost:8000/docs
- **Architecture**: [ARCHITECTURE.md](architecture/ARCHITECTURE.md)
- **Usage**: [USAGE_GUIDE.md](guides/USAGE_GUIDE.md)
- **Endpoints**: [ENDPOINTS.md](api/ENDPOINTS.md)

---

**Happy forecasting! 🚀📊**
