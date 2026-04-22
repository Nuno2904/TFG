"""
👤 User Management Endpoints

Handles user registration, retrieval, update, and deletion.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.models import Usuario
from app.schemas import UsuarioRegister, UsuarioOut, UsuarioUpdate, ChangePasswordRequest, ChangeUsernameRequest, DeleteAccountRequest
from app.security import (
    hash_password,
    get_current_user,
    get_admin_user,
    verify_password,
)


router = APIRouter(
    prefix="/usuarios",
    tags=["👤 Users"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
    }
)


# ═══════════════════════════════════════════════════════════════════════════
# 📝 User Registration
# ═══════════════════════════════════════════════════════════════════════════


@router.post(
    "",
    response_model=UsuarioOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register New User",
    description="Create a new user account"
)
def register_user(
    user_data: UsuarioRegister,
    db: Session = Depends(get_db)
) -> Usuario:
    """
    ✍️ Register a new user.
    
    Creates a new user account with email and password.
    Password is automatically hashed before storage.
    
    Args:
        user_data: User registration data (email, password, optional tipo)
        db: Database session
        
    Returns:
        Created UsuarioOut (excludes password)
        
    Raises:
        HTTPException 400: Email already registered
    """
    # 🔍 Check if email already exists
    existing_user = db.scalars(
        select(Usuario).where(Usuario.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{user_data.email}' is already registered"
        )
    
    # 🔐 Hash password
    hashed_password = hash_password(user_data.password)
    
    # 👤 Create new user
    new_user = Usuario(
        email=user_data.email,
        password=hashed_password,
        tipo=user_data.tipo or "usuario"
    )
    
    # 💾 Save to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


# ═══════════════════════════════════════════════════════════════════════════
# 🔍 User Retrieval
# ═══════════════════════════════════════════════════════════════════════════


@router.get(
    "/me",
    response_model=UsuarioOut,
    status_code=status.HTTP_200_OK,
    summary="Get Current User",
    description="Retrieve authenticated user's profile"
)
def get_me(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """
    👤 Get current authenticated user's profile.
    
    Args:
        current_user: Current authenticated user (from token)
        
    Returns:
        Current user's UsuarioOut
    """
    return current_user


@router.get(
    "/{email}",
    response_model=UsuarioOut,
    status_code=status.HTTP_200_OK,
    summary="Get User by Email",
    description="Retrieve a specific user by email",
    dependencies=[Depends(get_current_user)]  # ✅ Must be authenticated
)
def get_user_by_email(
    email: EmailStr,
    db: Session = Depends(get_db)
) -> Usuario:
    """
    🔍 Get user by email address.
    
    Args:
        email: Email address to search for
        db: Database session
        
    Returns:
        User information (UsuarioOut)
        
    Raises:
        HTTPException 404: User not found
    """
    # 🔍 Query user
    user = db.scalars(
        select(Usuario).where(Usuario.email == email)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email '{email}' not found"
        )
    
    return user


# ═══════════════════════════════════════════════════════════════════════════
# ✏️ User Update
# ═══════════════════════════════════════════════════════════════════════════


@router.put(
    "/me",
    response_model=UsuarioOut,
    status_code=status.HTTP_200_OK,
    summary="Update Current User",
    description="Update authenticated user's profile"
)
def update_me(
    user_update: UsuarioUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    ✏️ Update current authenticated user's profile.
    
    Only provided fields will be updated.
    If password is updated, it will be automatically hashed.
    
    Args:
        user_update: Updated user data (all fields optional)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated user information
    """
    # ⚙️ Update fields
    update_data = user_update.model_dump(exclude_unset=True)
    
    # 🔐 Hash password if being updated
    if "password" in update_data and update_data["password"]:
        update_data["password"] = hash_password(update_data["password"])
    
    # 🔄 Apply updates
    for key, value in update_data.items():
        setattr(current_user, key, value)
    
    # 💾 Save changes
    db.commit()
    db.refresh(current_user)
    
    return current_user


# ═══════════════════════════════════════════════════════════════════════════
# � Password Management
# ═══════════════════════════════════════════════════════════════════════════


@router.post(
    "/me/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change Password",
    description="Change authenticated user's password"
)
def change_password(
    password_data: ChangePasswordRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    🔑 Change current user's password.
    
    Requires verification of current password for security.
    
    Args:
        password_data: Current and new password
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException 400: Current password is incorrect
    """
    # ✅ Verify current password
    if not verify_password(password_data.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta"
        )
    
    # 🔐 Hash new password
    current_user.password = hash_password(password_data.new_password)
    
    # 💾 Save changes
    db.commit()
    
    return {
        "message": "Contraseña actualizada exitosamente",
        "email": current_user.email
    }


# ═══════════════════════════════════════════════════════════════════════════
# ✏️ Change Username
# ═══════════════════════════════════════════════════════════════════════════


@router.patch(
    "/me/username",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Change Username",
    description="Change authenticated user's username"
)
def change_username(
    data: ChangeUsernameRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    ✏️ Change current user's username.

    Raises:
        HTTPException 400: Username is already taken
    """
    existing = db.scalars(
        select(Usuario).where(
            Usuario.username == data.username,
            Usuario.id != current_user.id
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ese nombre de usuario ya está en uso"
        )

    current_user.username = data.username
    db.commit()

    return {
        "message": "Nombre de usuario actualizado exitosamente",
        "username": current_user.username
    }


# ═══════════════════════════════════════════════════════════════════════════
# 🗑️ User Deletion
# ═══════════════════════════════════════════════════════════════════════════


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Current User",
    description="Delete authenticated user's account"
)
def delete_me(
    body: DeleteAccountRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    \U0001f5d1\ufe0f Delete current authenticated user's account.
    
    Requires password confirmation for security.
    
    Args:
        body: Request body with password confirmation
        current_user: Current authenticated user
        db: Database session
    """
    # \u2705 Verify password before deleting
    if not verify_password(body.password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contrase\u00f1a incorrecta"
        )
    # \U0001f5d1\ufe0f Delete user (cascades to datasets and models)
    db.delete(current_user)
    db.commit()


@router.delete(
    "/{email}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete User (Admin)",
    description="Delete a user by email (admin only)"
)
def delete_user_admin(
    email: EmailStr,
    admin_user: Usuario = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> None:
    """
    🗑️ Delete a user by email (admin only).
    
    Args:
        email: Email of user to delete
        admin_user: Current admin user (verified via dependency)
        db: Database session
        
    Raises:
        HTTPException 403: User is not admin
        HTTPException 404: User not found
    """
    # 🔍 Find user to delete
    user_to_delete = db.scalars(
        select(Usuario).where(Usuario.email == email)
    ).first()
    
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email '{email}' not found"
        )
    
    # 🗑️ Delete user
    db.delete(user_to_delete)
    db.commit()
