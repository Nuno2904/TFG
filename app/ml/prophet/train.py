#.py para entrenar al modelo Prophet
import pandas as pd 
from prophet import Prophet
from prophet.serialize import model_to_json, model_from_json
import logging
from pathlib import Path
from sqlalchemy.orm import Session
from app.services.ml_storage_service import MLStorageService
from app.models.data import Data
from app.models.ml import MLModel

logger = logging.getLogger(__name__)


def train_prophet_model(
    df: pd.DataFrame, 
    model_name: str, 
    user_id: int, 
    dataset_id: int,
    model_path: str
) -> str:
    """
    Entrena un modelo Prophet con los datos proporcionados y lo guarda en el almacenamiento.
    
    ⚡ Esta función se ejecuta en background durante la creación del modelo.
    
    Args:
        df (pd.DataFrame): DataFrame con las columnas 'ds' (fecha) y 'y' (valor).
        model_name (str): Nombre del modelo a guardar.
        user_id (int): ID del usuario que entrena el modelo.
        dataset_id (int): ID del dataset utilizado para entrenar el modelo.
        model_path (str): Ruta local donde guardar el modelo.
    
    Returns:
        str: Ruta del modelo guardado en el almacenamiento.
        
    Raises:
        ValueError: Si el DataFrame no tiene las columnas necesarias.
        Exception: Si el entrenamiento falla.
    """
    
    try:
        logger.info(f"🤖 Iniciando entrenamiento de Prophet para modelo: {model_name}")
        
        # Verificar que el DataFrame tenga las columnas necesarias
        if 'ds' not in df.columns or 'y' not in df.columns:
            raise ValueError("El DataFrame debe contener las columnas 'ds' y 'y'")
        
        # Convertir la columna 'ds' a formato datetime si no lo está
        if not pd.api.types.is_datetime64_any_dtype(df['ds']):
            df['ds'] = pd.to_datetime(df['ds'])
        
        logger.info(f"📊 Datos preparados: {len(df)} registros cargados")
        
        # Entrenar el modelo Prophet
        logger.info("🎯 Entrenando modelo Prophet...")
        model = Prophet(interval_width=0.95, yearly_seasonality=True)
        model.fit(df)
        
        logger.info("✅ Modelo entrenado exitosamente")
        
        # Crear directorio si no existe
        model_dir = Path(model_path)
        try:
            model_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Directorio de modelo creado/verificado: {model_dir}")
        except Exception as e:
            logger.error(f"❌ Error creando directorio: {str(e)}")
            raise
        
        # Guardar el modelo entrenado como json
        model_file = model_dir / f"{model_name}.json"
        try:
            with open(model_file, 'w') as f:
                f.write(model_to_json(model))
            logger.info(f"💾 Modelo guardado en: {model_file}")
        except Exception as e:
            logger.error(f"❌ Error guardando modelo: {str(e)}")
            raise
        
        return str(model_file)
        
    except Exception as e:
        logger.error(f"❌ Error entrenando modelo Prophet: {str(e)}")
        raise


def get_dataset_as_dataframe(db: Session, dataset_id: int) -> pd.DataFrame:
    """
    Obtiene los datos del dataset de la BD y los convierte a DataFrame con formato Prophet.
    
    Args:
        db (Session): Sesión de base de datos.
        dataset_id (int): ID del dataset.
    
    Returns:
        pd.DataFrame: DataFrame con columnas 'ds' y 'y'.
    """
    
    logger.info(f"📥 Cargando datos del dataset {dataset_id} desde BD...")
    
    # Cargar todos los registros de la tabla Data para este dataset
    data_entries = db.query(Data).filter(
        Data.dataset_id == dataset_id
    ).all()
    
    if not data_entries:
        raise ValueError(f"No hay datos en el dataset {dataset_id}")
    
    # Convertir a diccionario para crear DataFrame
    data_list = [
        {
            "ds": entry.DS,
            "y": entry.y
        }
        for entry in data_entries
    ]
    
    df = pd.DataFrame(data_list)
    logger.info(f"✅ {len(df)} registros cargados desde BD")
    
    return df