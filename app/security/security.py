"""
🔐 Security & Cryptography Module

Handles:
- Password hashing and verification with bcrypt
- JWT token creation and validation
- OAuth2 authentication flow
"""

from datetime import datetime, timedelta
from typing import Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.config import settings
from app.schemas import TokenData
from app.db.session import get_db
from app.models import Usuario


# 🔒 Password Hashing Configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Security strength
)


# 🎫 OAuth2 Configuration
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    description="JWT Bearer token for authentication"
)


# ═══════════════════════════════════════════════════════════════════════════
# 🔑 Password Functions
# ═══════════════════════════════════════════════════════════════════════════


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


# ═══════════════════════════════════════════════════════════════════════════
# 🎫 JWT Token Functions
# ═══════════════════════════════════════════════════════════════════════════


def create_access_token(data: Dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary with claims to encode (typically {"user_id": id, "user_type": type})
        expires_delta: Optional custom expiration time (defaults to ACCESS_TOKEN_EXPIRE_MINUTES)
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    # ⏰ Set expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    
    # 🔐 Encode with SECRET_KEY
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def create_password_reset_token(user_id: int, email: str) -> str:
    """
    Create a short-lived JWT token used for password reset.

    Args:
        user_id: ID of the user requesting the reset
        email: Email of the user (extra verification layer)

    Returns:
        Encoded JWT token valid for PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
    """
    expire = datetime.utcnow() + timedelta(
        minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "purpose": "password_reset",
        "user_id": user_id,
        "email": email,
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_password_reset_token(token: str) -> dict:
    """
    Decode and validate a password-reset JWT token.

    Args:
        token: JWT token from the reset email link

    Returns:
        Decoded payload dict with user_id and email

    Raises:
        HTTPException 400: If the token is invalid, expired, or not a reset token
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("purpose") != "password_reset":
            raise ValueError("Token no es de restablecimiento de contraseña")
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El enlace de restablecimiento no es válido o ha expirado. Solicita uno nuevo."
        )


def verify_token(token: str) -> TokenData:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token to verify
        
    Returns:
        TokenData with extracted user_id and user_type
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 🔓 Decode token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # 📋 Extract claims
        user_id: str | None = payload.get("user_id")
        user_type: str | None = payload.get("user_type")
        
        if user_id is None or user_type is None:
            raise credentials_exception
            
        token_data = TokenData(user_id=int(user_id), user_type=user_type)
        
    except JWTError:
        raise credentials_exception
    
    return token_data


# ═══════════════════════════════════════════════════════════════════════════
# 👤 Current User Dependency
# ═══════════════════════════════════════════════════════════════════════════


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Dependency to get the current authenticated user.
    
    Args:
        token: JWT token from Authorization header
        db: Database session
        
    Returns:
        Current Usuario object from database
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    # 🔍 Verify token
    token_data = verify_token(token)
    
    # 🗄️ Query user from database
    user = db.scalars(
        select(Usuario).where(Usuario.id == token_data.user_id)
    ).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_admin_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """
    Dependency to ensure current user is an admin.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if they are an admin
        
    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.tipo != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions - admin access required"
        )
    
    return current_user
