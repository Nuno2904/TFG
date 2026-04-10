"""
🤖 ARIMA/SARIMA Model Training

Entrena modelos ARIMA o SARIMA con auto_arima detectando automáticamente si hay estacionalidad.
"""

import pandas as pd
import numpy as np
import joblib
import logging
from pathlib import Path
from sqlalchemy.orm import Session

from app.services.ml_storage_service import MLStorageService
from app.models.ml import MLModel
from app.ml.arima.utils import validate_arima_series

from statsmodels.tsa.arima.model import ARIMA
import json

# Import auto_arima from pmdarima
try:
    from pmdarima import auto_arima
except ImportError:
    raise ImportError("⚠️ pmdarima required. Install with: pip install pmdarima")

logger = logging.getLogger(__name__)


def train_arima_model(
    df: pd.DataFrame,
    model_name: str,
    user_id: int,
    dataset_id: int,
    model_path: str
) -> dict:
    """
    Entrena un modelo ARIMA o SARIMA con auto_arima.
    
    Detecta automáticamente si la serie tiene estacionalidad:
    - Si TIENE estacionalidad → Entrena SARIMA(p,d,q)(P,D,Q,m)
    - Si NO tiene estacionalidad → Entrena ARIMA(p,d,q)
    
    ⚡ Ejecuta en background durante creación del modelo.
    
    Args:
        df (pd.DataFrame): DataFrame con índice datetime + 1 columna numérica
        model_name (str): Nombre del modelo a guardar
        user_id (int): ID del usuario
        dataset_id (int): ID del dataset usado para entrenar
        model_path (str): Ruta local donde guardar el modelo (directorio completo)
    
    Returns:
        dict: {
            'status': 'éxito' o 'error',
            'model_file': ruta del archivo .pkl,
            'metadata_file': ruta del archivo metadata.json,
            'metadata': {
                'model_type': 'ARIMA' o 'SARIMA',
                'order': (p, d, q),
                'seasonal_order': (P, D, Q, m) o None,
                'tiene_estacionalidad': bool,
                'aic': float,
                'bic': float,
                'rmse': float,
                'mae': float,
                'longitud': int
            }
        }
    
    Raises:
        ValueError: Si el DataFrame no es válido
        Exception: Si el entrenamiento falla
    """
    
    try:
        logger.info(f"🤖 Iniciando entrenamiento ARIMA/SARIMA: {model_name}")
        
        # 1. Validar dataset
        logger.info("🔍 Validando dataset y detectando estacionalidad...")
        validation = validate_arima_series(df)
        
        if not validation['valido']:
            raise ValueError(f"Dataset inválido: {validation.get('error', 'Error desconocido')}")
        
        serie_numerica = validation['serie_numerica']
        series = df[serie_numerica].dropna()
        
        logger.info(f"✅ Validación OK. Serie 📊 {serie_numerica} con {len(series)} datos")
        logger.info(f"   Longitud: {len(series)}")
        
        # 2. Detectar estacionalidad
        tiene_estacionalidad = validation.get('tiene_estacionalidad', False)
        periodo_estacional = validation.get('periodo_estacional', 12)
        
        if tiene_estacionalidad is True:
            logger.info(f"✅ ESTACIONALIDAD DETECTADA")
            logger.info(f"   Período estacional: {periodo_estacional}")
            logger.info(f"   → Usando SARIMA")
            usar_sarima = True
        elif tiene_estacionalidad is False:
            logger.info(f"❌ Sin estacionalidad detectada")
            logger.info(f"   → Usando ARIMA")
            usar_sarima = False
        else:
            logger.warning(f"⚠️ Estacionalidad indeterminada. Usando ARIMA por defecto")
            usar_sarima = False
            tiene_estacionalidad = False
        
        # 3. Preparar datos (interpolar nulos si los hay)
        if series.isnull().sum() > 0:
            logger.warning(f"⚠️ Interpolando {series.isnull().sum()} nulos...")
            series = series.interpolate(method='linear', limit_direction='both')
        
        # 3b. Asegurar frecuencia en el índice para evitar warnings de statsmodels
        if hasattr(series.index, 'inferred_freq') and series.index.freq is None:
            inferred = pd.infer_freq(series.index)
            if inferred:
                series = series.asfreq(inferred)
                logger.info(f"📅 Frecuencia establecida: {inferred}")
        
        # 4. Encontrar parámetros óptimos con auto_arima
        logger.info("🔎 Buscando parámetros óptimos...")
        
        if usar_sarima:
            logger.info("   Modo: SARIMA con búsqueda de estacionalidad")
            auto_model = auto_arima(
                series,
                start_p=0,
                start_q=0,
                max_p=3,              # Reducido para SARIMA (más costoso)
                max_q=3,              # Reducido para SARIMA
                max_d=1,              # Diferenciación
                start_P=0,
                start_Q=0,
                max_P=1,              # Componentes estacionales
                max_Q=1,
                max_D=1,
                m=periodo_estacional, # Período estacional
                seasonal=True,        # ✅ ACTIVAR ESTACIONALIDAD
                stepwise=True,        # Búsqueda rápida
                information_criterion='aic',
                trace=True,
                error_action='ignore',
                suppress_warnings=True,
                disp=False
            )
        else:
            logger.info("   Modo: ARIMA sin componente estacional")
            auto_model = auto_arima(
                series,
                start_p=0,
                start_q=0,
                max_p=5,
                max_q=5,
                max_d=2,
                seasonal=False,       # ❌ SIN ESTACIONALIDAD
                stepwise=True,
                information_criterion='aic',
                trace=True,
                error_action='ignore',
                suppress_warnings=True,
                disp=False
            )
        
        best_order = auto_model.order
        best_seasonal_order = auto_model.seasonal_order if usar_sarima else None
        
        if usar_sarima:
            logger.info(f"✅ Parámetros óptimos encontrados:")
            logger.info(f"   SARIMA{best_order}{best_seasonal_order}")
        else:
            logger.info(f"✅ Parámetros óptimos encontrados:")
            logger.info(f"   ARIMA{best_order}")
        
        try:
            aic_val = auto_model.aic() if callable(auto_model.aic) else auto_model.aic
            bic_val = auto_model.bic() if callable(auto_model.bic) else auto_model.bic
            logger.info(f"   AIC: {float(aic_val):.2f}, BIC: {float(bic_val):.2f}")
        except Exception:
            logger.info("   AIC/BIC: no disponible")
        
        # 5. Entrenar modelo final con los parámetros encontrados
        if usar_sarima:
            logger.info(f"🎯 Entrenando SARIMA{best_order}{best_seasonal_order}...")
        else:
            logger.info(f"🎯 Entrenando ARIMA{best_order}...")
        
        # Usar el modelo ya ajustado de auto_arima
        fitted_model = auto_model
        
        if usar_sarima:
            logger.info(f"✅ Modelo SARIMA entrenado exitosamente")
        else:
            logger.info(f"✅ Modelo ARIMA entrenado exitosamente")
        
        # 6. Calcular métricas
        predictions = fitted_model.fittedvalues if not callable(fitted_model.fittedvalues) else fitted_model.fittedvalues()
        rmse = np.sqrt(np.mean((series - predictions) ** 2))
        mae = np.mean(np.abs(series - predictions))
        nonzero_mask = series != 0
        if nonzero_mask.sum() > 0:
            mape = float(np.mean(np.abs((series[nonzero_mask] - predictions[nonzero_mask]) / series[nonzero_mask])) * 100)
        else:
            mape = None
        
        logger.info(f"📊 Métricas de entrenamiento:")
        logger.info(f"   RMSE: {rmse:.4f}")
        logger.info(f"   MAE: {mae:.4f}")
        logger.info(f"   MAPE: {mape:.4f}%" if mape is not None else "   MAPE: N/A (valores cero en la serie)")
        
        # 7. Crear directorio
        model_dir = Path(model_path)
        try:
            model_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Directorio creado: {model_dir}")
        except Exception as e:
            logger.error(f"❌ Error creando directorio: {str(e)}")
            raise
        
        # 8. Guardar modelo con joblib
        model_file = model_dir / f"{model_name}.pkl"
        try:
            joblib.dump(fitted_model, model_file)
            logger.info(f"💾 Modelo guardado en: {model_file}")
        except Exception as e:
            logger.error(f"❌ Error guardando modelo: {str(e)}")
            raise
        
        # 9. Guardar metadatos como JSON
        aic_val = fitted_model.aic() if callable(fitted_model.aic) else fitted_model.aic
        bic_val = fitted_model.bic() if callable(fitted_model.bic) else fitted_model.bic
        
        metadata = {
            'model_type': 'SARIMA' if usar_sarima else 'ARIMA',
            'order': best_order,
            'seasonal_order': best_seasonal_order,
            'tiene_estacionalidad': bool(tiene_estacionalidad),
            'periodo_estacional': periodo_estacional if usar_sarima else None,
            'aic': float(aic_val),
            'bic': float(bic_val),
            'rmse': float(rmse),
            'mae': float(mae),
            'mape': mape,
            'longitud': len(series)
        }
        
        metadata_file = model_dir / f"{model_name}_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        logger.info(f"📝 Metadatos guardados en: {metadata_file}")
        
        return {
            'status': 'éxito',
            'model_file': str(model_file),
            'metadata_file': str(metadata_file),
            'metadata': metadata
        }
        
    except Exception as e:
        logger.error(f"❌ Error entrenando ARIMA/SARIMA: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'model_file': None
        }



def prepare_dataframe_for_arima(df_raw: pd.DataFrame, date_col: str, value_col: str) -> pd.DataFrame:
    """
    Prepara un DataFrame para ARIMA (convierte a índice datetime).
    
    Convierte de formato "plano" a formato con índice datetime.
    
    Args:
        df_raw: DataFrame sin procesar
        date_col: Nombre de la columna con fechas
        value_col: Nombre de la columna con valores numéricos
    
    Returns:
        DataFrame con índice datetime y 1 columna numérica
    """
    df = df_raw.copy()
    
    # Convertir columna de fecha
    df[date_col] = pd.to_datetime(df[date_col])
    
    # Establecer como índice
    df = df.set_index(date_col)
    
    # Ordenar por fecha
    df = df.sort_index()
    
    # Seleccionar solo la columna de valores
    df = df[[value_col]]
    
    return df
