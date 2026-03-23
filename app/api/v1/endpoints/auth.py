"""
🔐 Authentication Endpoints

Handles user registration and login with token generation.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.models import Usuario
from app.schemas import Token, UsuarioRegister
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
)


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
    
    Creates a new user account with the provided credentials.
    
    Args:
        user_data: UsuarioCreate with email, password, username, full_name
        db: Database session
        
    Returns:
        Success message and user ID
        
    Raises:
        HTTPException 400: Email or username already exists
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
        full_name=user_data.full_name,
        tipo="usuario"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
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
    
    Args:
        credentials: OAuth2 form with username (email) and password
        db: Database session
        
    Returns:
        Token with access_token and token_type
        
    Raises:
        HTTPException 403: Invalid email or password
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
