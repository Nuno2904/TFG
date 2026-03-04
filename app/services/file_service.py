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
    Busca automáticamente la columna que contiene fechas.
    
    Args:
        df: DataFrame a analizar
        
    Returns:
        Nombre de la columna con fechas, None si no encuentra
    """
    for column in df.columns:
        try:
            pd.to_datetime(df[column], format='%Y-%m-%d', errors='coerce')
            # Si al menos el 50% de los valores se pueden convertir a fecha, es probablemente la columna de fechas
            if pd.to_datetime(df[column], format='%Y-%m-%d', errors='coerce').notna().sum() / len(df) >= 0.5:
                return column
        except:
            continue
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
    Valida que el archivo tenga columnas de fecha y numérica.
    
    Args:
        df: DataFrame a validar
        
    Returns:
        Tupla (nombre_columna_fecha, nombre_columna_numerica)
    """
    date_col = find_date_column(df)
    numeric_col = find_numeric_column(df, exclude_columns=[date_col] if date_col else [])
    
    return date_col, numeric_col


# ============================================================================
# DATA TRANSFORMATION FUNCTIONS
# ============================================================================

def transform_date_to_ds_format(date_str: str) -> Optional[str]:
    """
    Transforma una fecha a formato YYYY-MM-DD para la columna DS.
    
    Args:
        date_str: String de fecha en cualquier formato común
        
    Returns:
        Fecha en formato YYYY-MM-DD, None si no es válida
    """
    common_formats = [
        '%Y-%m-%d',
        '%d-%m-%Y',
        '%m-%d-%Y',
        '%d/%m/%Y',
        '%m/%d/%Y',
        '%Y/%m/%d',
        '%d.%m.%Y',
        '%Y.%m.%d',
    ]
    
    for date_format in common_formats:
        try:
            parsed_date = datetime.strptime(str(date_str).strip(), date_format)
            return parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    return None


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
                df = pd.read_csv(BytesIO(file_content))
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
        
        # Procesar y guardar datos
        data_entries = []
        errors = []
        
        for idx, row in df.iterrows():
            try:
                # Transformar fecha a formato YYYY-MM-DD
                date_value = row[date_col]
                ds_value = transform_date_to_ds_format(str(date_value))
                
                if ds_value is None:
                    errors.append(f"Fila {idx + 1}: Fecha inválida")
                    continue
                
                # Obtener valor numérico
                numeric_value = pd.to_numeric(row[numeric_col], errors='coerce')
                
                if pd.isna(numeric_value):
                    errors.append(f"Fila {idx + 1}: Valor numérico inválido")
                    continue
                
                # Crear objeto Data
                data_obj = data(
                    user_id=user_id,
                    DS=ds_value,
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
                "data_entries": data_entries,
                "warnings": errors
            }
        
        return data_entries
    
    @staticmethod
    def get_user_files(user_id: int, db: Session) -> List[Data]:
        """
        Recupera todos los archivos de un usuario.
        
        Args:
            user_id: ID del usuario
            db: Sesión de base de datos
            
        Returns:
            Lista de objetos Data del usuario
            
        Raises:
            HTTPException: Si el usuario no existe
        """
        user = db.scalars(select(Usuario).where(Usuario.id == user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        data_entries = db.scalars(
            select(Data).where(Data.user_id == user_id)
        ).all()
        
        return data_entries
    
    @staticmethod
    def get_file_by_id(file_id: int, user_id: int, db: Session) -> Optional[Data]:
        """
        Recupera un archivo específico verificando que pertenece al usuario.
        
        Args:
            file_id: ID del archivo
            user_id: ID del usuario propietario
            db: Sesión de base de datos
            
        Returns:
            Objeto Data si existe y pertenece al usuario, None en caso contrario
            
        Raises:
            HTTPException: Si el archivo no existe o no pertenece al usuario
        """
        data_obj = db.scalars(
            select(Data).where(
                (Data.id == file_id) & (Data.user_id == user_id)
            )
        ).first()
        
        if not data_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Archivo no encontrado o no tienes acceso"
            )
        
        return data_obj
    
    @staticmethod
    def delete_file(file_id: int, user_id: int, db: Session) -> dict:
        """
        Elimina un archivo verificando que pertenece al usuario.
        
        Args:
            file_id: ID del archivo a eliminar
            user_id: ID del usuario propietario
            db: Sesión de base de datos
            
        Returns:
            Diccionario con confirmación de eliminación
            
        Raises:
            HTTPException: Si el archivo no existe o no pertenece al usuario
        """
        # Verificar que el archivo existe y pertenece al usuario
        data_obj = FileService.get_file_by_id(file_id, user_id, db)
        
        try:
            db.delete(data_obj)
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
