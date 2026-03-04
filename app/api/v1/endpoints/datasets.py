"""
📊 Datasets Endpoints

Handles dataset management and data retrieval with user authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.services.file_service import FileService
from app.db.session import get_db
from app.models import Usuario
from app.security import get_current_user


router = APIRouter(
    prefix="/datasets",
    tags=["📊 Datasets"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
        status.HTTP_404_NOT_FOUND: {"description": "Dataset not found"},
    }
)


@router.get("", status_code=status.HTTP_200_OK)
def get_datasets(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los datasets del usuario autenticado.
    
    Devuelve lista con id y name de cada dataset.
    Solo se muestran datasets pertenecientes al usuario.
    """
    try:
        datasets = FileService.get_user_files(current_user.id, db)
        
        dataset_list = [
            {
                "id": dataset.id,
                "name": dataset.name
            }
            for dataset in datasets
        ]
        
        return {
            "user_id": current_user.id,
            "total_datasets": len(dataset_list),
            "datasets": dataset_list
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los datasets: {str(e)}"
        )


@router.get("/{dataset_id}/data", status_code=status.HTTP_200_OK)
def get_dataset_data(
    dataset_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los data points de un dataset específico.
    
    Solo el propietario del dataset puede acceder.
    Los puntos se devuelven ordenados por DS (timestamp ascendente).
    
    Response fields:
        - DS: Timestamp en formato ISO (datetime)
        - y: Valor numérico del punto de datos
    """
    try:
        dataset = FileService.get_file_by_id(dataset_id, current_user.id, db)
        
        points_list = [
            {
                "DS": str(data_point.DS),
                "y": data_point.y
            }
            for data_point in dataset.data_entries
        ]
        
        return {
            "dataset_id": dataset_id,
            "total_points": len(points_list),
            "data": points_list
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los datos del dataset: {str(e)}"
        )
