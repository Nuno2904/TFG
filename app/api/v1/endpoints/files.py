"""
📁 Files Endpoints

Handles file upload, retrieval, and deletion with user authentication.
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.services.file_service import FileService
from app.db.session import get_db
from app.models import Usuario, Dataset, Data
from app.security import get_current_user


router = APIRouter(
    prefix="/files",
    tags=["📁 Files"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
        status.HTTP_404_NOT_FOUND: {"description": "File not found"},
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid file"},
    }
)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sube un archivo CSV/XLSX y almacena los datos en la base de datos.
    
    Validaciones:
    - Tipo: Solo CSV/XLSX
    - Tamaño: Máximo 5MB
    - Columnas: Debe contener una columna de fecha y otra numérica
    
    La columna de fecha se convierte a formato YYYY-MM-DD y se almacena en DS.
    La columna numérica se almacena en y.
    """
    try:
        result = await FileService.upload_file(file, current_user.id, db)
        
        # Verificar si hay warnings
        if "warnings" in result:
            return {
                "message": "Archivo subido con advertencias",
                "dataset": result["dataset"],
                "entries_count": len(result["data_entries"]),
                "warnings": result["warnings"]
            }
        
        return {
            "message": "Archivo subido correctamente",
            "dataset": result["dataset"],
            "entries_count": len(result["data_entries"]),
            "data": result["data_entries"]
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar el archivo: {str(e)}"
        )


@router.get("/my-files")
def get_my_files(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los archivos subidos por el usuario autenticado.
    
    Solo el usuario que subió el archivo puede verlo.
    """
    try:
        files = FileService.get_user_files(current_user.id, db)
        
        return {
            "user_id": current_user.id,
            "total_files": len(files),
            "data": files
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los archivos: {str(e)}"
        )


@router.get("/{file_id}")
def get_file(
    file_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene un dataset específico por ID con todos sus datos relacionados.
    
    Solo el usuario propietario puede acceder a él.
    """
    try:
        dataset = FileService.get_file_by_id(file_id, current_user.id, db)
        
        return {
            "dataset_id": dataset.id,
            "user_id": dataset.user_id,
            "name": dataset.name,
            "data_entries": dataset.data_entries,
            "total_entries": len(dataset.data_entries)
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el archivo: {str(e)}"
        )


@router.delete("/{file_id}", status_code=status.HTTP_200_OK)
def delete_file(
    file_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Elimina un archivo específico.
    
    Solo el usuario propietario puede eliminarlo.
    Requiere token válido y actualizado.
    """
    try:
        result = FileService.delete_file(file_id, current_user.id, db)
        
        return {
            "message": "Archivo eliminado correctamente",
            "file_id": file_id
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el archivo: {str(e)}"
        )
