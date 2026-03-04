"""
📝 Updated Project README

Your FastAPI application has been restructured with best practices!
"""

# 🎯 TFG - Modern FastAPI Application

A production-ready FastAPI application with user management, authentication, and role-based access control.

## ✨ Features

- ✅ **FastAPI Framework** - Fast, modern, and intuitive web framework
- 🔐 **JWT Authentication** - Secure token-based authentication
- 👤 **User Management** - Complete user CRUD operations
- � **Dataset Management** - Upload and manage datasets
- 🤖 **ML Model Management** ✨ - Create, train, and manage ML models with automatic storage
- �🛡️ **Role-Based Access** - Admin and user role differentiation
- 🗄️ **SQLAlchemy ORM** - Modern async-ready database layer
- ⚙️ **Pydantic Settings** - Environment-based configuration management
- 📖 **Auto Documentation** - Interactive API docs (Swagger & ReDoc)
- 🔒 **Password Security** - Bcrypt hashing with configurable rounds
- 🎯 **Type Hints** - Full Python type annotations
- 📝 **Comprehensive Docstrings** - Well-documented code with examples

## 📁 Project Structure

```
TFG/
├── app/                          # 📦 Main application package
│   ├── __init__.py              # Package initialization
│   ├── config.py                # ⚙️ Settings with BaseSettings
│   ├── core/                    # 🔧 Core utilities
│   │   └── __init__.py
│   ├── db/                      # 🗄️ Database configuration
│   │   ├── __init__.py
│   │   ├── base.py              # SQLAlchemy base & engine
│   │   └── session.py           # Session management
│   ├── models/                  # 📊 SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── usuario.py           # User model
│   │   ├── dataset.py           # Dataset model
│   │   ├── data.py              # Data model
│   │   └── ml.py                # 🤖 ML Model (NEW)
│   ├── schemas/                 # 📋 Pydantic validation schemas
│   │   ├── __init__.py
│   │   ├── usuario.py           # User schemas
│   │   └── ml.py                # 🤖 ML Model schemas (NEW)
│   ├── services/                # 🔧 Business logic services
│   │   ├── __init__.py
│   │   ├── file_service.py      # File handling
│   │   └── ml_storage_service.py # 🤖 ML storage management (NEW)
│   ├── security/                # 🔐 Authentication & security
│   │   ├── __init__.py
│   │   └── security.py          # JWT & password utilities
│   └── api/                     # 📡 API endpoints
│       ├── __init__.py
│       └── v1/                  # API v1
│           ├── __init__.py
│           └── endpoints/       # Route handlers
│               ├── __init__.py
│               ├── auth.py      # 🔑 Login endpoint
│               ├── usuarios.py  # 👤 User endpoints
│               ├── datasets.py  # 📊 Dataset endpoints
│               └── ml.py        # 🤖 ML Model endpoints (NEW)
├── main.py                      # 🚀 Application entry point
├── .env                         # 🔐 Environment variables (local)
├── .env.example                 # 📝 Environment template
├── requirements.txt             # 📦 Python dependencies
├── ML_GUIDE.md                  # 📖 ML System documentation (NEW)
├── README.md                    # 📖 This file
├── STRUCTURE.md                 # 📊 Project architecture
├── MIGRATION_GUIDE.md           # 🔄 Migration reference
└── RESTRUCTURING_SUMMARY.md    # 📝 Change summary
```

## 🚀 Getting Started

### 1️⃣ Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\\Scripts\\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2️⃣ Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
```

### 3️⃣ Initialize Database

```bash
# The database will be automatically initialized on app startup
# For SQLite: test.db will be created automatically
```

### 4️⃣ Run Application

```bash
# Using uvicorn directly
uvicorn main:app --reload

# The app will be available at: http://localhost:8000
```

## 📖 API Documentation

Once the app is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔐 Authentication Flow

### 1. Register User

```bash
POST /api/v1/usuarios
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "tipo": "usuario"
}
```

### 2. Login

```bash
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword123
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### 3. Use Token

```bash
GET /api/v1/usuarios/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

## 🛠️ Development Tools

### Code Formatting

```bash
# Format code with Black
black app/ main.py

# Sort imports with isort
isort app/ main.py
```

### Linting

```bash
# Check code style with flake8
flake8 app/ main.py

# Type checking with mypy
mypy app/ main.py
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## 📝 Key Improvements Made

✅ **Project Structure**
- Organized into logical modules (db, models, schemas, security, api)
- Clear separation of concerns
- Easy to scale and maintain

✅ **Configuration Management**
- Uses Pydantic BaseSettings from `pydantic-settings`
- Environment variables loaded from `.env` file
- Type-safe configuration

✅ **Security**
- Bcrypt password hashing with configurable rounds
- JWT token authentication with expiration
- Admin role verification
- OAuth2 scheme implementation

✅ **Code Quality**
- Full type hints throughout
- Comprehensive docstrings with emojis
- Descriptive comments explaining logic
- PEP 8 compliant formatting

✅ **API Documentation**
- Field descriptions in schemas
- Endpoint summaries and descriptions
- HTTP status code documentation
- Clear error responses

✅ **Bug Fixes**
- Fixed typo: "Usuaario" → "Usuario"
- Fixed password field mapping in user update
- Improved error handling and messages
- Better validation messages

✅ **Developer Experience**
- Clear logging setup
- Health check endpoint
- Root endpoint with documentation links
- Modular router structure
- Easy dependency injection with FastAPI

## 🔄 Environment Variables

```env
# Database connection
DATABASE_URL=postgresql://user:pass@localhost/dbname

# JWT Configuration
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
APP_NAME=TFG API
APP_VERSION=1.0.0
DEBUG=False
```

## 📚 API Endpoints Summary

### 🔐 Authentication
- `POST /api/v1/auth/login` - User login

### 👤 Users
- `POST /api/v1/usuarios` - Register new user
- `GET /api/v1/usuarios/me` - Get current user
- `GET /api/v1/usuarios/{email}` - Get user by email
- `PUT /api/v1/usuarios/me` - Update current user
- `DELETE /api/v1/usuarios/me` - Delete current user
- `DELETE /api/v1/usuarios/{email}` - Delete user (admin only)

### 📊 Datasets
- `GET /api/v1/datasets` - Get all user datasets
- `POST /api/v1/datasets` - Create new dataset
- `GET /api/v1/datasets/{id}` - Get dataset details
- `DELETE /api/v1/datasets/{id}` - Delete dataset

### 🤖 ML Models ✨ NEW
- `POST /api/v1/models` - Create new ML model
- `GET /api/v1/models` - Get all user ML models
- `GET /api/v1/models/{model_id}` - Get model details
- `GET /api/v1/models/dataset/{dataset_id}` - Get models by dataset
- `PUT /api/v1/models/{model_id}` - Update model
- `DELETE /api/v1/models/{model_id}` - Delete model

For detailed ML Model documentation, see [ML_GUIDE.md](ML_GUIDE.md)

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run linting and tests
4. Submit a pull request

## 📄 License

This project is part of TFG (Trabajo Fin de Grado).
