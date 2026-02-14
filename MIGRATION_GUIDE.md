"""
📋 Migration Guide: Old → New Structure

This document explains how to migrate from the old project structure
to the new, improved FastAPI application structure.
"""

## 🔄 File Mapping

### Old Structure → New Structure

```
OLD                              NEW
backend/main.py              →   app/config.py + main.py
                             +   app/db/base.py + session.py
                             +   app/api/v1/__init__.py

backend/database.py          →   app/db/base.py
                             +   app/db/session.py

backend/models.py            →   app/models/usuario.py

backend/schemas.py           →   app/schemas/usuario.py

backend/oauth2.py            →   app/security/security.py

backend/utils.py             →   app/security/security.py
                             (hash & verify functions moved)

backend/routers/auth.py      →   app/api/v1/endpoints/auth.py

backend/routers/usuarios.py  →   app/api/v1/endpoints/usuarios.py
```

## 🎯 Key Improvements

### 1. Environment Variables (BaseSettings)

**Before:**
```python
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
```

**After:**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

**Benefits:**
- ✅ Type-safe configuration
- ✅ Automatic validation
- ✅ IDE autocompletion
- ✅ Environment file support by default

### 2. Password Hashing

**Before:**
```python
# In utils.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str):
    return pwd_context.hash(password)

def verify(plain, hashed):
    return pwd_context.verify(plain, hashed)
```

**After:**
```python
# In security/security.py with better naming and docs
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Configurable security
)

def hash_password(password: str) -> str:
    """Hash a plain text password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)
```

**Benefits:**
- ✅ More descriptive naming
- ✅ Better documentation
- ✅ Configurable security parameters
- ✅ Type hints throughout

### 3. JWT Authentication

**Before:**
```python
# Mixed in oauth2.py
tokenBearer = OAuth2PasswordBearer(tokenUrl='login')
SECRET_KEY = os.getenv("SECRET_KEY")

def crear_token(data:dict):
    # Implementation...
    
def usuario_actual(token :str = Depends(tokenBearer), db...):
    # Implementation...
```

**After:**
```python
# Organized in security/security.py
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    description="JWT Bearer token for authentication"
)

def create_access_token(data: Dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token with clear documentation."""

def verify_token(token: str) -> TokenData:
    """Verify and decode a JWT token."""

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    """Dependency to get the current authenticated user."""

def get_admin_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """Ensure current user is an admin."""
```

**Benefits:**
- ✅ Clear function names
- ✅ Separate concerns (creation, verification, dependencies)
- ✅ Role-based access control built-in
- ✅ Better error handling

### 4. Database Models

**Before:**
```python
from .database import Base, engine

class Usuario(Base):
    __tablename__ = "usuarios"
    id : Mapped[int] = mapped_column(Integer, primary_key = True, index = True)
    email : Mapped[String] = mapped_column(String, nullable = False)
    # Comments in Spanish with technical details
```

**After:**
```python
from app.db.base import Base

class Usuario(Base):
    """
    Usuario database model.
    
    Represents a user in the system with authentication and type information.
    """
    __tablename__ = "usuarios"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        doc="Unique user identifier"
    )
    email: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,  # Added constraint
        index=True,
        doc="User email address"
    )
    
    def __repr__(self) -> str:
        """String representation of Usuario object."""
        return f"<Usuario(id={self.id}, email='{self.email}', tipo='{self.tipo}')>"
```

**Benefits:**
- ✅ Clear docstrings and documentation
- ✅ Better field constraints (unique)
- ✅ Field descriptions for clarity
- ✅ Good representation method

### 5. Schemes/Validation

**Before:**
```python
from typing import Optional
from pydantic import BaseModel, EmailStr

class UsuarioRegister (BaseModel):
    password : str
    email : EmailStr
    tipo : Optional[str] = None
    
class UsuarioOut (BaseModel): #devuelve una vez registrado el usuario. 
    email:EmailStr
```

**After:**
```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal

class UsuarioRegister(UsuarioBase):
    """Schema for user registration."""
    password: str = Field(
        ...,
        min_length=8,
        description="Password (minimum 8 characters)"
    )

class UsuarioOut(BaseModel):
    """Schema for user response (public data only)."""
    id: int = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    tipo: str = Field(..., description="User type")
    created_at: datetime = Field(..., description="Account creation date")
    
    model_config = {"from_attributes": True}
```

**Benefits:**
- ✅ Field descriptions for API docs
- ✅ Validation constraints (min_length)
- ✅ Better typing (Literal for choices)
- ✅ Type-safe response models

### 6. API Routes

**Before:**
```python
@router.post('/login')
def login(user_credential :OAuth2PasswordRequestForm = Depends(), db : Session = Depends(get_db)):
    user = db.scalars(select(models.Usuario).where(models.Usuario.email == user_credential.username)).first()
    if not user:
        raise HTTPException(...)
    # ...
```

**After:**
```python
@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticate user and return JWT access token"
)
def login(
    credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Token:
    """
    🔓 Login endpoint.
    
    Authenticates a user using email and password.
    Returns a JWT token valid for API requests.
    """
    # Cleaner implementation
```

**Benefits:**
- ✅ Full endpoint documentation
- ✅ Clean code formatting
- ✅ Type hints
- ✅ Status codes specified
- ✅ Response models defined

## 🚀 Migration Steps

1. **Install New Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Update Imports:**
   Change from:
   ```python
   from backend.database import get_db
   from backend import models, schemas
   ```
   To:
   ```python
   from app.db import get_db
   from app.models import Usuario
   from app.schemas import UsuarioRegister
   from app.security import get_current_user
   ```

3. **Update Configuration:**
   - Copy `.env.example` to `.env`
   - Update `DATABASE_URL` and `SECRET_KEY`

4. **Run Application:**
   ```bash
   uvicorn main:app --reload
   ```

5. **Verify Endpoints:**
   Visit http://localhost:8000/docs

## 📝 Bug Fixes Applied

✅ Fixed typo: "Usuaario" → "Usuario"
✅ Fixed password update handling (now uses `model_dump(exclude_unset=True)`)
✅ Added constraint: email must be unique
✅ Better error messages
✅ Improved validation

## 🎨 Code Quality Improvements

✅ Added comprehensive docstrings
✅ Added type hints throughout
✅ Proper error handling with clear messages
✅ Descriptive field names
✅ PEP 8 compliant formatting
✅ Logging setup
✅ Security best practices

## 📚 Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org
- **Pydantic Docs**: https://docs.pydantic.dev
- **JWT Blog**: https://jwt.io/introduction

## ❓ FAQ

**Q: Do I need to recreate my database?**
A: Yes for the new structure, but the migration is automatic with SQLAlchemy.

**Q: Can I keep using the old code?**
A: Yes, but new code should follow the new structure for consistency.

**Q: How do I run tests?**
A: Run `pytest` from the project root.

**Q: How do I format code?**
A: Run `black app/ main.py` and `isort app/ main.py`
