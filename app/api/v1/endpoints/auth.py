"""
🔐 Authentication Endpoints

Handles user login and token generation.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.models import Usuario
from app.schemas import Token
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
