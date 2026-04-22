"""
📝 Usuario (User) Schemas

Pydantic models for request/response validation.
Defines data structures for API endpoints.
"""

import re
from pydantic import BaseModel, EmailStr, Field, field_validator
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
        - username: Unique username
        - password: Plain text password (will be hashed)
        - tipo: Optional user type (defaults to 'usuario')
    """
    
    username: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Unique username (3-100 characters)"
    )
    password: str = Field(
        ...,
        min_length=10,
        description="Password (minimum 10 characters, requires uppercase, lowercase, digit and special character)"
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        errors = []
        if len(v) < 10:
            errors.append("al menos 10 caracteres")
        if not re.search(r"[A-Z]", v):
            errors.append("al menos una letra mayúscula")
        if not re.search(r"[a-z]", v):
            errors.append("al menos una letra minúscula")
        if not re.search(r"\d", v):
            errors.append("al menos un dígito")
        if not re.search(r"[!@#$%^&*()\-_=+\[\]{};:',.<>?/\\|`~\"£€]", v):
            errors.append("al menos un carácter especial (!@#$%^&*...)")
        if errors:
            raise ValueError("La contraseña debe tener: " + ", ".join(errors))
        return v


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


class ChangePasswordRequest(BaseModel):
    """
    Schema for changing user password.
    
    Requires verification of current password for security.
    """
    
    current_password: str = Field(
        ...,
        min_length=8,
        description="Current password for verification"
    )
    new_password: str = Field(
        ...,
        min_length=8,
        description="New password (minimum 8 characters)"
    )


class ChangeUsernameRequest(BaseModel):
    """Schema for changing the authenticated user's username."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="New username (3-100 characters)"
    )


class PasswordResetRequest(BaseModel):
    """Schema for requesting a password-reset email."""

    email: EmailStr = Field(..., description="Email address of the account to reset")


class PasswordResetConfirm(BaseModel):
    """Schema for confirming a password reset with a token."""

    token: str = Field(..., description="Password-reset JWT token received by email")
    new_password: str = Field(
        ...,
        min_length=10,
        description="New password (minimum 10 characters)"
    )

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        errors = []
        if len(v) < 10:
            errors.append("al menos 10 caracteres")
        if not re.search(r"[A-Z]", v):
            errors.append("al menos una letra mayúscula")
        if not re.search(r"[a-z]", v):
            errors.append("al menos una letra minúscula")
        if not re.search(r"\d", v):
            errors.append("al menos un dígito")
        if not re.search(r"[!@#$%^&*()\-_=+\[\]{};:',.<>?/\\|`~\"£€]", v):
            errors.append("al menos un carácter especial (!@#$%^&*...)")
        if errors:
            raise ValueError("La contraseña debe tener: " + ", ".join(errors))
        return v


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
