"""
🤖 ML Models Endpoints

Handles ML model creation, retrieval, update, and deletion.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.models import MLModel, Usuario, Dataset
from app.schemas.ml import MLModelCreate, MLModelOut, MLModelUpdate, MLModelDetailOut
from app.security import get_current_user
from app.services.ml_storage_service import MLStorageService


router = APIRouter(
    prefix="/models",
    tags=["🤖 ML Models"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
        status.HTTP_404_NOT_FOUND: {"description": "Model not found"},
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid request"},
    }
)


# ═══════════════════════════════════════════════════════════════════════════
# 📝 Create ML Model
# ═══════════════════════════════════════════════════════════════════════════


@router.post(
    "",
    response_model=MLModelOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create New ML Model",
    description="Create a new ML model entry"
)
def create_ml_model(
    model_data: MLModelCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> MLModel:
    """
    ✍️ Create a new ML model.
    
    Creates a new ML model with training information.
    The model is automatically associated with the authenticated user.
    The model storage path is generated automatically as:
    /app/storage/models/user_{user_id}/dataset_{dataset_id}/{model_name}
    """
    
    # Verify dataset exists and belongs to the current user
    dataset = db.query(Dataset).filter(
        Dataset.id == model_data.dataset_id,
        Dataset.user_id == current_user.id
    ).first()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found or does not belong to the current user"
        )
    
    # Generate model storage path
    try:
        model_dir = MLStorageService.create_model_directory(
            user_id=current_user.id,
            dataset_id=model_data.dataset_id,
            model_name=model_data.name
        )
        model_path = str(model_dir)
    except OSError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create model directory: {str(e)}"
        )
    
    # Create new ML model
    new_model = MLModel(
        user_id=current_user.id,
        dataset_id=model_data.dataset_id,
        name=model_data.name,
        model_path=model_path,
        status="en_entrenamiento"
    )
    
    db.add(new_model)
    db.commit()
    db.refresh(new_model)
    
    return new_model


# ═══════════════════════════════════════════════════════════════════════════
# 📖 Get All ML Models
# ═══════════════════════════════════════════════════════════════════════════


@router.get(
    "",
    response_model=list[MLModelOut],
    status_code=status.HTTP_200_OK,
    summary="Get All User ML Models",
    description="Retrieve all ML models created by the authenticated user"
)
def get_user_ml_models(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> list[MLModel]:
    """
    📖 Get all ML models for the current user.
    
    Returns list with id, name, status and other info for each model.
    Only shows models belonging to the authenticated user.
    """
    
    models = db.query(MLModel).filter(
        MLModel.user_id == current_user.id
    ).all()
    
    return models


# ═══════════════════════════════════════════════════════════════════════════
# � Get Models by Dataset (debe estar ANTES de /{model_id})
# ═══════════════════════════════════════════════════════════════════════════


@router.get(
    "/dataset/{dataset_id}",
    response_model=list[MLModelOut],
    status_code=status.HTTP_200_OK,
    summary="Get Models by Dataset",
    description="Retrieve all ML models trained with a specific dataset"
)
def get_models_by_dataset(
    dataset_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> list[MLModel]:
    """
    📊 Get all ML models for a specific dataset.
    
    Returns all models trained with the specified dataset.
    Only shows models and datasets belonging to the authenticated user.
    """
    
    # Verify dataset belongs to the current user
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.user_id == current_user.id
    ).first()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    models = db.query(MLModel).filter(
        MLModel.dataset_id == dataset_id,
        MLModel.user_id == current_user.id
    ).all()
    
    return models


# ═══════════════════════════════════════════════════════════════════════════
# 🔍 Get ML Model by ID
# ═══════════════════════════════════════════════════════════════════════════


@router.get(
    "/{model_id}",
    response_model=MLModelDetailOut,
    status_code=status.HTTP_200_OK,
    summary="Get ML Model Details",
    description="Retrieve details of a specific ML model"
)
def get_ml_model_detail(
    model_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> MLModel:
    """
    🔍 Get details of a specific ML model.
    
    Returns complete information including user and dataset details.
    Only accessible by the user who created the model.
    """
    
    model = db.query(MLModel).filter(
        MLModel.id == model_id,
        MLModel.user_id == current_user.id
    ).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ML model not found"
        )
    
    return model


# ═══════════════════════════════════════════════════════════════════════════
# ✏️ Update ML Model
# ═══════════════════════════════════════════════════════════════════════════


@router.put(
    "/{model_id}",
    response_model=MLModelOut,
    status_code=status.HTTP_200_OK,
    summary="Update ML Model",
    description="Update ML model information"
)
def update_ml_model(
    model_id: int,
    model_data: MLModelUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> MLModel:
    """
    ✏️ Update an ML model.
    
    Updates model information like status, name, and error messages.
    Only the user who created the model can update it.
    """
    
    model = db.query(MLModel).filter(
        MLModel.id == model_id,
        MLModel.user_id == current_user.id
    ).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ML model not found"
        )
    
    # Update fields if provided
    if model_data.name is not None:
        model.name = model_data.name
    if model_data.status is not None:
        model.status = model_data.status
    if model_data.error_message is not None:
        model.error_message = model_data.error_message
    
    db.commit()
    db.refresh(model)
    
    return model


# ═══════════════════════════════════════════════════════════════════════════
# 🗑️ Delete ML Model
# ═══════════════════════════════════════════════════════════════════════════


@router.delete(
    "/{model_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete ML Model",
    description="Delete an ML model"
)
def delete_ml_model(
    model_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    🗑️ Delete an ML model.
    
    Removes the model and all associated information.
    Also deletes the model directory and all files.
    Only the user who created the model can delete it.
    """
    
    model = db.query(MLModel).filter(
        MLModel.id == model_id,
        MLModel.user_id == current_user.id
    ).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ML model not found"
        )
    
    # Delete model directory
    MLStorageService.delete_model_directory(
        user_id=model.user_id,
        dataset_id=model.dataset_id,
        model_name=model.name
    )
    
    # Delete from database
    db.delete(model)
    db.commit()

