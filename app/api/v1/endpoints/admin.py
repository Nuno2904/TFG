"""
👨‍💼 Admin Management Endpoints

Handles admin-only operations: user management, dataset management, model management.
All endpoints require admin role.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.models import Usuario, Dataset, MLModel
from app.schemas.usuario import UsuarioOut
from app.security import get_admin_user
from app.services.file_service import FileService
from app.services.ml_storage_service import MLStorageService


router = APIRouter(
    prefix="/admin",
    tags=["👨‍💼 Admin"],
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Admin access required"},
    }
)


# ═══════════════════════════════════════════════════════════════════════════
# 👥 User Management
# ═══════════════════════════════════════════════════════════════════════════


@router.get(
    "/users",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="List All Users",
    description="Get all registered users (admin only)"
)
def list_all_users(
    admin_user: Usuario = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    👥 List all registered users.
    
    Returns all users with their basic information.
    """
    users = db.scalars(select(Usuario)).all()
    
    users_data = [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "tipo": user.tipo,
            "created_at": user.created_at,
            "datasets_count": len(user.datasets),
            "models_count": len(user.ml_models),
        }
        for user in users
    ]
    
    return {
        "total_users": len(users_data),
        "users": users_data
    }


@router.get(
    "/users/{user_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get User Details",
    description="Get detailed information about a specific user (admin only)"
)
def get_user_details(
    user_id: int,
    admin_user: Usuario = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    🔍 Get detailed user information.
    
    Returns user profile, datasets count, and models count.
    """
    user = db.scalars(
        select(Usuario).where(Usuario.id == user_id)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado"
        )
    
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "tipo": user.tipo,
            "created_at": user.created_at,
        },
        "statistics": {
            "datasets_count": len(user.datasets),
            "models_count": len(user.ml_models),
            "total_data_points": sum(len(d.data_entries) for d in user.datasets),
        }
    }


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete User",
    description="Delete a user and all their associated data (admin only)"
)
def delete_user_by_id(
    user_id: int,
    admin_user: Usuario = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> None:
    """
    🗑️ Delete a user and all associated data.
    
    Cascading delete: removes user, datasets, models, and data points.
    """
    user = db.scalars(
        select(Usuario).where(Usuario.id == user_id)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado"
        )
    
    if user.tipo == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No se pueden eliminar usuarios administrador"
        )
    
    db.delete(user)
    db.commit()


# ═══════════════════════════════════════════════════════════════════════════
# 📊 Dataset Management
# ═══════════════════════════════════════════════════════════════════════════


@router.get(
    "/datasets",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="List All Datasets",
    description="Get all datasets from all users (admin only)"
)
def list_all_datasets(
    admin_user: Usuario = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    📊 List all datasets from all users.
    
    Returns all datasets with their metadata.
    """
    datasets = db.scalars(select(Dataset)).all()
    
    datasets_data = [
        {
            "id": dataset.id,
            "nombre": dataset.name,
            "usuario_id": dataset.user_id,
        }
        for dataset in datasets
    ]
    
    return {
        "total_datasets": len(datasets_data),
        "datasets": datasets_data
    }


@router.get(
    "/users/{user_id}/datasets",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get User Datasets",
    description="List all datasets uploaded by a specific user (admin only)"
)
def get_user_datasets(
    user_id: int,
    admin_user: Usuario = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    📂 Get all datasets for a user.
    
    Returns list of datasets with their metadata.
    """
    user = db.scalars(
        select(Usuario).where(Usuario.id == user_id)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado"
        )
    
    datasets_data = [
        {
            "id": dataset.id,
            "name": dataset.name,
            "data_points": len(dataset.data_entries),
        }
        for dataset in user.datasets
    ]
    
    return {
        "user_id": user_id,
        "total_datasets": len(datasets_data),
        "datasets": datasets_data
    }


@router.delete(
    "/datasets/{dataset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Dataset",
    description="Delete a dataset and all its data (admin only)"
)
def delete_dataset_by_id(
    dataset_id: int,
    admin_user: Usuario = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> None:
    """
    🗑️ Delete a dataset.
    
    Cascading delete: removes dataset and all associated data points.
    """
    dataset = db.scalars(
        select(Dataset).where(Dataset.id == dataset_id)
    ).first()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset con ID {dataset_id} no encontrado"
        )
    
    db.delete(dataset)
    db.commit()


# ═══════════════════════════════════════════════════════════════════════════
# 🤖 Model Management
# ═══════════════════════════════════════════════════════════════════════════


@router.get(
    "/models",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="List All Models",
    description="Get all ML models from all users (admin only)"
)
def list_all_models(
    admin_user: Usuario = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    🤖 List all ML models from all users.
    
    Returns all models with their metadata.
    """
    models = db.scalars(select(MLModel)).all()
    
    models_data = [
        {
            "id": model.id,
            "nombre": model.name,
            "usuario_id": model.user_id,
            "tipo_modelo": model.model_type,
            "created_at": model.created_at,
        }
        for model in models
    ]
    
    return {
        "total_models": len(models_data),
        "models": models_data
    }


@router.get(
    "/users/{user_id}/models",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get User Models",
    description="List all ML models trained by a specific user (admin only)"
)
def get_user_models(
    user_id: int,
    admin_user: Usuario = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    🤖 Get all ML models for a user.
    
    Returns list of models with their metadata.
    """
    user = db.scalars(
        select(Usuario).where(Usuario.id == user_id)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado"
        )
    
    models_data = [
        {
            "id": model.id,
            "name": model.name,
            "model_type": model.model_type,
            "dataset_id": model.dataset_id,
            "status": model.status,
            "created_at": model.created_at,
        }
        for model in user.ml_models
    ]
    
    return {
        "user_id": user_id,
        "total_models": len(models_data),
        "models": models_data
    }


@router.delete(
    "/models/{model_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Model",
    description="Delete a trained ML model (admin only)"
)
def delete_model_by_id(
    model_id: int,
    admin_user: Usuario = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> None:
    """
    🗑️ Delete an ML model.
    
    Removes the model from database and storage.
    """
    model = db.scalars(
        select(MLModel).where(MLModel.id == model_id)
    ).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Modelo con ID {model_id} no encontrado"
        )
    
    # Delete model from storage
    try:
        MLStorageService.delete_model(model.id)
    except Exception as e:
        # Continue deletion even if file removal fails
        pass
    
    db.delete(model)
    db.commit()


# ═══════════════════════════════════════════════════════════════════════════
# 📈 Admin Dashboard Summary
# ═══════════════════════════════════════════════════════════════════════════


@router.get(
    "/dashboard",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Admin Dashboard",
    description="Get admin dashboard statistics (admin only)"
)
def get_admin_dashboard(
    admin_user: Usuario = Depends(get_admin_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    📊 Get admin dashboard statistics.
    
    Returns summary of users, datasets, and models.
    """
    users = db.scalars(select(Usuario)).all()
    datasets = db.scalars(select(Dataset)).all()
    models = db.scalars(select(MLModel)).all()
    
    total_data_points = sum(len(d.data_entries) for d in datasets)
    
    return {
        "statistics": {
            "total_users": len(users),
            "total_datasets": len(datasets),
            "total_models": len(models),
            "total_data_points": total_data_points,
        },
        "users_breakdown": {
            "admins": len([u for u in users if u.tipo == "admin"]),
            "regular_users": len([u for u in users if u.tipo == "usuario"]),
        },
        "models_breakdown": {
            "prophet": len([m for m in models if m.model_type == "prophet"]),
            "arima": len([m for m in models if m.model_type == "arima"]),
        }
    }
