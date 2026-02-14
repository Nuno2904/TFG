"""
📝 Usuario (User) Schemas

Pydantic models for request/response validation.
Defines data structures for API endpoints.
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Literal


class UsuarioBase(BaseModel):
    """Base schema with common user fields."""
    
    email: EmailStr = Field(..., description="User email address")
    tipo: Optional[Literal["usuario", "admin"]] = Field(
        default="usuario",
        description="User type: 'usuario' or 'admin'"
    )


class UsuarioRegister(UsuarioBase):
    """
    Schema for user registration.
    
    Required fields:
        - email: User email
        - password: Plain text password (will be hashed)
        - tipo: Optional user type (defaults to 'usuario')
    """
    
    password: str = Field(
        ...,
        min_length=8,
        description="Password (minimum 8 characters)"
    )


class UsuarioUpdate(BaseModel):
    """
    Schema for updating user information.
    
    All fields are optional - only provided fields will be updated.
    """
    
    email: Optional[EmailStr] = Field(
        None,
        description="New email address"
    )
    password: Optional[str] = Field(
        None,
        min_length=8,
        description="New password (minimum 8 characters)"
    )


class UsuarioOut(BaseModel):
    """
    Schema for user response (public data only).
    
    Never exposes sensitive information like passwords.
    """
    
    id: int = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    tipo: str = Field(..., description="User type")
    created_at: datetime = Field(..., description="Account creation date")
    
    model_config = {"from_attributes": True}


# 🔐 Authentication Schemas

class Token(BaseModel):
    """
    Schema for JWT token response.
    
    Attributes:
        access_token: JWT token string
        token_type: Token type (typically "bearer")
    """
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    """
    Schema for decoded token data.
    
    Extracted from JWT payload after validation.
    """
    
    user_id: int = Field(..., description="User ID from token")
    user_type: str = Field(..., description="User type from token")
