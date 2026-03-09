"""
🤖 ML Models Endpoints

Handles ML model creation, retrieval, update, and deletion.
Automatic training triggered on model creation via background tasks.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.models import MLModel, Usuario, Dataset
from app.schemas.ml import MLModelCreate, MLModelOut, MLModelUpdate, MLModelDetailOut
from app.security import get_current_user
from app.services.ml_storage_service import MLStorageService
from app.ml.prophet.train import train_prophet_model, get_dataset_as_dataframe

logger = logging.getLogger(__name__)

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
# � Background Task: Train Model
# ═══════════════════════════════════════════════════════════════════════════


def train_model_background(
    model_id: int,
    user_id: int,
    dataset_id: int,
    model_name: str,
    model_type: str,
    model_path: str,
    db_dependency=get_db
):
    """
    🔄 Background task que entrena el modelo automáticamente.
    
    Se ejecuta de forma asincrónica después de crear el registro en BD.
    Crea su propia sesión de BD para no interferir con la request.
    
    Args:
        model_id: ID del modelo en la BD
        user_id: ID del usuario
        dataset_id: ID del dataset
        model_name: Nombre del modelo
        model_type: Tipo del modelo (prophet, arima, etc)
        model_path: Ruta donde guardar el modelo
        db_dependency: Función para obtener nueva sesión BD
    """
    # Obtener nueva sesión de BD para esta tarea
    db = next(db_dependency())
    
    try:
        logger.info(f"🚀 Iniciando entrenamiento en background del modelo {model_id}")
        
        try:
            # Cargar datos del dataset desde BD
            logger.info(f"📥 Cargando datos del dataset {dataset_id}...")
            df = get_dataset_as_dataframe(db, dataset_id)
            
            # Entrenar modelo según su tipo
            if model_type == "prophet":
                logger.info(f"🤖 Entrenando modelo Prophet...")
                train_prophet_model(df, model_name, user_id, dataset_id, model_path)
                
                # Actualizar estado a "entrenado" en BD
                model = db.query(MLModel).filter(MLModel.id == model_id).first()
                if model:
                    model.status = "entrenado"
                    model.error_message = None
                    db.commit()
                    logger.info(f"✅ Modelo {model_id} entrenado exitosamente")
            
            elif model_type == "arima":
                # Future: Implementar ARIMA
                logger.warning(f"⚠️ Modelo ARIMA aún no implementado")
                raise NotImplementedError(f"Modelo {model_type} no está implementado aún")
            
            else:
                raise ValueError(f"Tipo de modelo no soportado: {model_type}")
                
        except Exception as e:
            logger.error(f"❌ Error entrenando modelo {model_id}: {str(e)}")
            
            # Actualizar estado a "error" en BD
            model = db.query(MLModel).filter(MLModel.id == model_id).first()
            if model:
                model.status = "error"
                model.error_message = str(e)[:500]  # Limitar a 500 chars
                db.commit()
            
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════════
# 📝 Create ML Model (Auto-Train)
# ═══════════════════════════════════════════════════════════════════════════


@router.post(
    "",
    response_model=MLModelOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create & Train New ML Model",
    description="Create a new ML model and automatically train it with the dataset"
)
def create_ml_model(
    model_data: MLModelCreate,
    background_tasks: BackgroundTasks,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> MLModel:
    """
    ✍️ Create a new ML model and START TRAINING IMMEDIATELY.
    
    ⚡ The workflow is:
    1. Validate dataset belongs to user
    2. Create ML model record in BD with status "en_entrenamiento"
    3. Return model immediately to client
    4. 🚀 START background training task (no wait)
    
    During training:
    - Dataset data is loaded from BD
    - Model is trained with the data
    - Model file is saved to storage
    - Status updated to "entrenado" (or "error" if fails)
    
    Model storage path format:
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
    
    # ✅ Check if model with same name already exists for this user
    existing_model = db.query(MLModel).filter(
        MLModel.user_id == current_user.id,
        MLModel.name == model_data.name
    ).first()
    
    if existing_model:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You already have a model named '{model_data.name}'. Model names must be unique per user."
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
    
    # 1️⃣ Create new ML model in BD with status "en_entrenamiento"
    new_model = MLModel(
        user_id=current_user.id,
        dataset_id=model_data.dataset_id,
        name=model_data.name,
        model_type=model_data.model_type,
        model_path=model_path,
        status="en_entrenamiento",
        error_message=None
    )
    
    db.add(new_model)
    db.commit()
    db.refresh(new_model)
    
    logger.info(f"📝 Modelo {new_model.id} creado en BD. Status: en_entrenamiento")
    
    # 2️⃣ 🚀 Dispatch background training task (fire and forget)
    background_tasks.add_task(
        train_model_background,
        model_id=new_model.id,
        user_id=current_user.id,
        dataset_id=model_data.dataset_id,
        model_name=model_data.name,
        model_type=model_data.model_type,
        model_path=model_path
    )
    
    logger.info(f"🚀 Background training task lanzado para modelo {new_model.id}")
    
    # 3️⃣ Return model immediately
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



