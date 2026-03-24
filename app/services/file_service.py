"""
📁 File Service

Handles file upload, validation, and database operations for CSV/XLSX files.
- Validates file type (CSV/XLSX)
- Validates file size (≤ 5MB)
- Validates presence of date and numeric columns
- Converts dates to YYYY-MM-DD format for DS column
- Handles file upload/retrieval/deletion with user authorization
"""

from io import BytesIO
from datetime import datetime
from typing import Optional, Tuple, List
import pandas as pd
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from app.models.data import Data
from app.models.dataset import Dataset
from app.models.usuario import Usuario


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_file_type(filename: str) -> bool:
    """
    Valida que el archivo sea CSV o XLSX.
    
    Args:
        filename: Nombre del archivo
        
    Returns:
        True si el formato es válido, False en caso contrario
    """
    allowed_extensions = {'.csv', '.xlsx'}
    file_extension = filename.lower().split('.')[-1]
    return f'.{file_extension}' in allowed_extensions


def validate_file_size(file_content: bytes, max_size_mb: int = 5) -> bool:
    """
    Valida que el tamaño del archivo no supere el límite.
    
    Args:
        file_content: Contenido del archivo en bytes
        max_size_mb: Tamaño máximo permitido en MB (default: 5)
        
    Returns:
        True si el tamaño es válido, False en caso contrario
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    return len(file_content) <= max_size_bytes


def find_date_column(df: pd.DataFrame) -> Optional[str]:
    """
    Busca automáticamente la columna que contiene fechas con detección inteligente de formato.
    
    Intenta detectar automáticamente si el formato es DD-MM-YYYY, MM-DD-YYYY, etc.
    mediante análisis heurístico de los valores.
    
    Args:
        df: DataFrame a analizar
        
    Returns:
        Nombre de la columna con fechas, None si no encuentra
    """
    for column in df.columns:
        # Estrategia 1: Intentar con dayfirst=True (para DD-MM-YYYY)
        parsed_dayfirst = pd.to_datetime(
            df[column],
            errors="coerce",
            dayfirst=True
        )
        
        # Estrategia 2: Intentar con dayfirst=False (para MM-DD-YYYY)
        parsed_monthfirst = pd.to_datetime(
            df[column],
            errors="coerce",
            dayfirst=False
        )
        
        # Usar la estrategia que tenga más conversiones exitosas
        valid_dayfirst = parsed_dayfirst.notna().sum()
        valid_monthfirst = parsed_monthfirst.notna().sum()
        
        # Elegir la mejor opción
        if valid_dayfirst >= valid_monthfirst and valid_dayfirst / len(df) >= 0.5:
            return column
        elif valid_monthfirst / len(df) >= 0.5:
            return column
    
    return None



def find_numeric_column(df: pd.DataFrame, exclude_columns: List[str] = None) -> Optional[str]:
    """
    Busca automáticamente la columna que contiene valores numéricos.
    
    Args:
        df: DataFrame a analizar
        exclude_columns: Columnas a excluir de la búsqueda
        
    Returns:
        Nombre de la columna numérica, None si no encuentra
    """
    if exclude_columns is None:
        exclude_columns = []
    
    for column in df.columns:
        if column not in exclude_columns:
            try:
                pd.to_numeric(df[column], errors='coerce')
                # Si al menos el 50% de los valores son numéricos, es probablemente la columna de valores
                if pd.to_numeric(df[column], errors='coerce').notna().sum() / len(df) >= 0.5:
                    return column
            except:
                continue
    return None


def validate_columns(df: pd.DataFrame) -> Tuple[Optional[str], Optional[str]]:
    """
    Valida que el archivo tenga exactamente 2 columnas: fecha y numérica.
    Detecta automáticamente el formato de fecha (DD-MM-YYYY o MM-DD-YYYY) y lo convierte a YYYY-MM-DD.
    
    Args:
        df: DataFrame a validar
        
    Returns:
        Tupla (nombre_columna_fecha, nombre_columna_numerica)
        
    Raises:
        HTTPException: Si el número de columnas no es exactamente 2
    """
    # Validar que haya exactamente 2 columnas
    if len(df.columns) != 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El archivo debe tener exactamente 2 columnas (fecha y valor). Se encontraron {len(df.columns)} columnas."
        )
    
    date_col = find_date_column(df)
    
    if date_col:
        try:
            # Intentar con dayfirst=True (DD-MM-YYYY)
            parsed_dayfirst = pd.to_datetime(df[date_col], errors='coerce', dayfirst=True)
            # Intentar con dayfirst=False (MM-DD-YYYY)
            parsed_monthfirst = pd.to_datetime(df[date_col], errors='coerce', dayfirst=False)
            
            # Elegir la estrategia con más conversiones exitosas
            valid_dayfirst = parsed_dayfirst.notna().sum()
            valid_monthfirst = parsed_monthfirst.notna().sum()
            
            if valid_dayfirst >= valid_monthfirst:
                df[date_col] = parsed_dayfirst.dt.strftime('%Y-%m-%d')
            else:
                df[date_col] = parsed_monthfirst.dt.strftime('%Y-%m-%d')
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al convertir la columna de fecha: {str(e)}"
            )
    
    numeric_col = find_numeric_column(df, exclude_columns=[date_col] if date_col else [])
    
    return date_col, numeric_col


def validate_no_duplicate_dates(df: pd.DataFrame, date_col: str) -> None:
    """
    Valida que no haya fechas duplicadas en la columna de fecha.
    Una serie temporal requiere variación temporal (fechas diferentes).
    
    Args:
        df: DataFrame a validar
        date_col: Nombre de la columna de fecha
        
    Raises:
        HTTPException: Si hay 2 o más fechas iguales
    """
    # Contar fechas duplicadas (excluyendo NaN)
    valid_dates = df[date_col].dropna()
    duplicate_dates = valid_dates[valid_dates.duplicated(keep=False)]
    
    if len(duplicate_dates) > 0:
        unique_duplicates = duplicate_dates.unique()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El archivo contiene fechas duplicadas: {', '.join(unique_duplicates[:5])}. La serie temporal requiere fechas únicas."
        )




# ============================================================================
# FILE UPLOAD/RETRIEVAL/DELETION FUNCTIONS
# ============================================================================

class FileService:
    """Servicio para gestionar archivos de datos."""
    
    @staticmethod
    async def upload_file(
        file: UploadFile,
        user_id: int,
        db: Session
    ) -> List[Data]:
        """
        Sube un archivo CSV/XLSX a la base de datos.
        
        Validaciones:
        - Tipo de archivo: CSV o XLSX
        - Tamaño: ≤ 5MB
        - Columnas: Debe tener fecha y valor numérico
        
        Args:
            file: Archivo a subir
            user_id: ID del usuario propietario
            db: Sesión de base de datos
            
        Returns:
            Lista de objetos Data creados
            
        Raises:
            HTTPException: Si la validación falla
        """
        # Verificar que el usuario existe
        user = db.scalars(select(Usuario).where(Usuario.id == user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Leer contenido del archivo
        file_content = await file.read()
        
        # Validar tipo de archivo
        if not validate_file_type(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se permiten archivos CSV o XLSX"
            )
        
        # Validar tamaño
        if not validate_file_size(file_content, max_size_mb=5):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo no puede superar 5MB"
            )
        
        # Leer archivo según tipo
        try:
            if file.filename.lower().endswith('.csv'):
                df = pd.read_csv(BytesIO(file_content), sep =None, engine='python')
            else:  # xlsx
                df = pd.read_excel(BytesIO(file_content))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al leer el archivo: {str(e)}"
            )
        
        # Validar que tiene columnas de fecha y numérica
        date_col, numeric_col = validate_columns(df)
        
        if date_col is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo debe contener una columna con fechas"
            )
        
        if numeric_col is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo debe contener una columna con valores numéricos"
            )
        
        # Validar que no haya fechas duplicadas
        validate_no_duplicate_dates(df, date_col)
        
        #comprobar que el usuario no ha subido ningún archivo con el mismo nombre
        existing_file = db.scalars(
            select(Dataset).where((Dataset.user_id == user_id) & (Dataset.name == file.filename)) ).first()
        if existing_file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya has subido un archivo con ese nombre. Por favor, renómbralo e inténtalo de nuevo."
            )
        
        # Procesar y guardar datos
        data_entries = []
        errors = []
        
        # Crear el Dataset primero
        try:
            dataset = Dataset(
                user_id=user_id,
                name=file.filename
            )
            db.add(dataset)
            db.commit()
            db.refresh(dataset)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear el dataset: {str(e)}"
            )
        
        for idx, row in df.iterrows():
            try:
                # Obtener valor numérico
                numeric_value = pd.to_numeric(row[numeric_col], errors='coerce')
                date_value = row[date_col]
                
                # Validar que la fecha no sea NaN
                if pd.isna(date_value):
                    errors.append(f"Fila {idx + 1}: Fecha faltante o inválida")
                    continue
                
                # Validar que el valor numérico no sea NaN
                if pd.isna(numeric_value):
                    errors.append(f"Fila {idx + 1}: Valor numérico inválido")
                    continue
                
                # Crear objeto Data
                data_obj = Data(
                    dataset_id=dataset.id,
                    DS=date_value,
                    y=float(numeric_value)
                )
                data_entries.append(data_obj)
                
            except Exception as e:
                errors.append(f"Fila {idx + 1}: {str(e)}")
        
        if not data_entries:
            error_msg = "\n".join(errors)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se pudieron procesar las filas:\n{error_msg}"
            )
        
        # Guardar en base de datos
        try:
            for data_obj in data_entries:
                db.add(data_obj)
            db.commit()
            
            # Refrescar los objetos para obtener los IDs
            for data_obj in data_entries:
                db.refresh(data_obj)
                
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al guardar en la base de datos: {str(e)}"
            )
        
        if errors:
            # Advertencia: algunas filas tuvieron problemas pero otras se guardaron
            return {
                "success": True,
                "dataset": dataset,
                "data_entries": data_entries,
                "warnings": errors
            }
        
        return {
            "success": True,
            "dataset": dataset,
            "data_entries": data_entries
        }
    
    @staticmethod
    def get_user_files(user_id: int, db: Session) -> List[Dataset]:
        """
        Recupera todos los datasets de un usuario.
        
        Args:
            user_id: ID del usuario
            db: Sesión de base de datos
            
        Returns:
            Lista de objetos Dataset del usuario
            
        Raises:
            HTTPException: Si el usuario no existe
        """
        user = db.scalars(select(Usuario).where(Usuario.id == user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        datasets = db.scalars(
            select(Dataset).where(Dataset.user_id == user_id)
        ).all()
        
        return datasets
    
    @staticmethod
    def get_file_by_id(file_id: int, user_id: int, db: Session) -> Optional[Dataset]:
        """
        Recupera un dataset específico verificando que pertenece al usuario.
        
        Args:
            file_id: ID del dataset
            user_id: ID del usuario propietario
            db: Sesión de base de datos
            
        Returns:
            Objeto Dataset si existe y pertenece al usuario, None en caso contrario
            
        Raises:
            HTTPException: Si el dataset no existe o no pertenece al usuario
        """
        dataset_obj = db.scalars(
            select(Dataset).where(
                (Dataset.id == file_id) & (Dataset.user_id == user_id)
            )
        ).first()
        
        if not dataset_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Archivo no encontrado o no tienes acceso"
            )
        
        return dataset_obj
    
    @staticmethod
    def get_file_by_name(dataset_name: str, user_id: int, db: Session) -> Optional[Dataset]:
        """
        Recupera un dataset específico por su nombre verificando que pertenece al usuario.
        
        Args:
            dataset_name: Nombre del dataset
            user_id: ID del usuario propietario
            db: Sesión de base de datos
            
        Returns:
            Objeto Dataset si existe y pertenece al usuario, None en caso contrario
            
        Raises:
            HTTPException: Si el dataset no existe o no pertenece al usuario
        """
        dataset_obj = db.scalars(
            select(Dataset).where(
                (Dataset.name == dataset_name) & (Dataset.user_id == user_id)
            )
        ).first()
        
        if not dataset_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Archivo no encontrado o no tienes acceso"
            )
        
        return dataset_obj
    
    @staticmethod
    def delete_file(file_id: int, user_id: int, db: Session) -> dict:
        """
        Elimina un dataset verificando que pertenece al usuario.
        
        Args:
            file_id: ID del dataset a eliminar
            user_id: ID del usuario propietario
            db: Sesión de base de datos
            
        Returns:
            Diccionario con confirmación de eliminación
            
        Raises:
            HTTPException: Si el dataset no existe o no pertenece al usuario
        """
        # Verificar que el dataset existe y pertenece al usuario
        dataset_obj = FileService.get_file_by_id(file_id, user_id, db)
        
        try:
            db.delete(dataset_obj)
            db.commit()
            return {
                "message": "Archivo eliminado correctamente",
                "file_id": file_id
            }
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al eliminar el archivo: {str(e)}"
            )
