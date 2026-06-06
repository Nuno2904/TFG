"""
🔐 Authentication Endpoints

Handles user registration, login, and password reset via email.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.models import Usuario
from app.schemas import Token, UsuarioRegister
from app.schemas.usuario import PasswordResetRequest, PasswordResetConfirm
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_password_reset_token,
    verify_password_reset_token,
)
from app.config import settings
from app.security.security import get_current_user
from app.services.email_service import send_welcome_email, send_password_reset_email, send_password_reset_link_email


router = APIRouter(
    prefix="/auth",
    tags=["🔐 Authentication"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid credentials"},
    }
)


@router.post(
    "/register",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="User Registration",
    description="Register a new user account"
)
def register(
    user_data: UsuarioRegister,
    db: Session = Depends(get_db)
) -> dict:
    """
    📝 Registration endpoint.

    Creates a new user account. Sends a welcome email after creation (no confirmation required).
    """
    # ✅ Check if email already exists
    existing_email = db.scalars(
        select(Usuario).where(Usuario.email == user_data.email)
    ).first()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # ✅ Check if username already exists
    existing_username = db.scalars(
        select(Usuario).where(Usuario.username == user_data.username)
    ).first()
    
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # 🔐 Hash password and create user
    hashed_password = hash_password(user_data.password)
    
    new_user = Usuario(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password,
        tipo="usuario"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 📧 Send welcome email (fire-and-forget — do not block if it fails)
    try:
        send_welcome_email(new_user.email, new_user.username or new_user.email)
    except Exception:
        pass
    
    return {
        "message": "User registered successfully",
        "user_id": new_user.id,
        "email": new_user.email
    }


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
    # 🔍 Query user by email
    user = db.scalars(
        select(Usuario).where(Usuario.email == credentials.username)
    ).first()
    
    # ✅ Validate user exists and password is correct
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid email or password"
        )
    
    # 🎫 Generate JWT token
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "user_type": user.tipo
        }
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.post(
    "/request-password-reset",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Request Password Reset",
    description="Send a password-reset link to the user's email address"
)
def request_password_reset(
    data: PasswordResetRequest,
    db: Session = Depends(get_db)
) -> dict:
    """
    📧 Request a password-reset email.

    Always returns HTTP 200 regardless of whether the email exists, to prevent
    user-enumeration attacks. The reset link is valid for 1 hour.
    """
    user = db.scalars(
        select(Usuario).where(Usuario.email == data.email)
    ).first()

    if user:
        reset_token = create_password_reset_token(user.id, user.email)
        try:
            send_password_reset_link_email(
                to_email=user.email,
                username=user.username or user.email,
                reset_token=reset_token,
                base_url=settings.FRONTEND_URL,
            )
        except Exception:
            pass  # Log is handled inside the email service

    return {
        "message": (
            "Si el email está registrado recibirás un enlace para restablecer tu contraseña. "
            "Revisa también la carpeta de spam."
        )
    }


@router.post(
    "/reset-password",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Reset Password",
    description="Set a new password using a reset token received by email"
)
def reset_password(
    data: PasswordResetConfirm,
    db: Session = Depends(get_db)
) -> dict:
    """
    🔑 Reset password using a one-time token from email.
    """
    payload = verify_password_reset_token(data.token)
    user_id = payload.get("user_id")
    email = payload.get("email")

    user = db.scalars(
        select(Usuario).where(Usuario.id == user_id, Usuario.email == email)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario no encontrado. El enlace puede ser inválido."
        )

    user.password = hash_password(data.new_password)
    db.commit()

    try:
        send_password_reset_email(
            to_email=user.email,
            username=user.username or user.email,
        )
    except Exception:
        pass  # Log is handled inside the email service

    return {"message": "Contraseña restablecida exitosamente. Ya puedes iniciar sesión."}



# ═══════════════════════════════════════════════════════════════════════════
# 🔧 Debug Endpoint
# ═══════════════════════════════════════════════════════════════════════════


@router.get(
    "/debug-token",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Debug Token",
    description="Debug endpoint to verify JWT token is valid"
)
def debug_token(
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    """
    🔧 Debug endpoint to verify token and user info.
    """
    return {
        "status": "✅ Token is valid",
        "user_id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "tipo": current_user.tipo,
    }
