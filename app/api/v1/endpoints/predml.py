#endpoints para que los modelos predigan:
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.services.ml_storage_service import MLStorageService
from app.ml.prophet.train import train_prophet_model
from app.ml.prophet.predict import predict_prophet_model
from app.models.ml import MLModel, ModelType
from app.models.usuario import Usuario
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/models",
    tags=["models"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/predict")
async def predict_model(
    model_id: int,
    future_periods: int = 30,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
)-> dict:
    """
     Endpoint para realizar predicciones con un modelo entrenado.
    Endpoint para realizar predicciones con un modelo entrenado.
    
    Args:
        model_id (int): ID del modelo a utilizar para la predicción.
        future_periods (int): Número de períodos futuros a predecir (default: 30).
        db (Session): Sesión de base de datos inyectada por Depends.
        current_user (Usuario): Usuario autenticado inyectado por Depends.
    
    Returns:
        dict: Predicciones generadas por el modelo.
    