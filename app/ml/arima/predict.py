"""
🔮 ARIMA Model Predictions

Realiza predicciones con modelos ARIMA previamente entrenados.
"""

import joblib
import pandas as pd
import numpy as np
import logging
import warnings
from pathlib import Path
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

from app.services.ml_storage_service import MLStorageService
from app.models.ml import MLModel

logger = logging.getLogger(__name__)


def predict_arima_model(
    model_path: str,
    future_periods: int = 30
) -> dict:
    """
    Realiza predicciones con un modelo ARIMA entrenado.
    
    Args:
        model_path (str): Ruta del directorio del modelo
        future_periods (int): Períodos a predecir (default: 30)
    
    Returns:
        dict: {
            'forecast': [
                {
                    'date': str (YYYY-MM-DD),
                    'yhat': float,
                    'yhat_lower': float,
                    'yhat_upper': float
                },
                ...
            ],
            'params': {
                'order': (p, d, q),
                'periods': int
            }
        }
    
    Raises:
        FileNotFoundError: Si no se encuentra el modelo
        Exception: Si la predicción falla
    """
    try:
        logger.info(f"🔍 Cargando modelo ARIMA desde: {model_path}")
        
        # Cargar modelo entrenado
        arima_model = MLStorageService.load_arima_model_from_directory(model_path)
        logger.info("✅ Modelo cargado exitosamente")
        
        # Cargar metadatos
        try:
            metadata = MLStorageService.load_arima_metadata(model_path)
            order = metadata.get('order', None)
            logger.info(f"📊 Modelo: ARIMA{order}")
        except:
            metadata = {}
            order = None
        
        # Realizar predicciones
        logger.info(f"📅 Generando predicciones para {future_periods} períodos...")
        
        # pmdarima predict: retorna forecast + intervalos de confianza
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=FutureWarning)
            warnings.simplefilter("ignore", category=UserWarning)
            forecast_values, conf_int = arima_model.predict(
                n_periods=future_periods,
                return_conf_int=True,
                alpha=0.05
            )
        # Asegurar arrays numpy para indexación posicional
        forecast_values = np.asarray(forecast_values)
        conf_int = np.asarray(conf_int)
        
        logger.info("✅ Predicciones generadas exitosamente")
        
        # Preparar respuesta con fechas
        forecast_list = []
        
        # Generar índice de fechas a partir de los datos de entrenamiento
        try:
            last_date = arima_model.arima_res_.data.dates[-1]
            date_index = pd.date_range(
                start=last_date + pd.tseries.frequencies.to_offset(pd.infer_freq(arima_model.arima_res_.data.dates)),
                periods=future_periods
            )
        except Exception:
            # Fallback: índices numéricos
            date_index = range(future_periods)
        
        for i, pred_date in enumerate(date_index):
            conf_lower = float(conf_int[i, 0]) if conf_int is not None else None
            conf_upper = float(conf_int[i, 1]) if conf_int is not None else None
            
            forecast_list.append({
                'date': pred_date.strftime('%Y-%m-%d') if hasattr(pred_date, 'strftime') else str(pred_date),
                'yhat': float(forecast_values[i]),
                'yhat_lower': conf_lower,
                'yhat_upper': conf_upper
            })
        
        return {
            'forecast': forecast_list,
            'params': {
                'order': order,
                'periods': future_periods,
                'confidence': 0.95
            },
            'metadata': metadata
        }
        
    except FileNotFoundError as e:
        logger.error(f"❌ Modelo no encontrado: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Error en predicción ARIMA: {str(e)}")
        raise


def get_training_samples(model_path: str, n_samples: int = 100) -> dict:
    """
    Obtiene valores de entrenamiento del modelo para visualización.
    
    Args:
        model_path: Ruta del modelo
        n_samples: Número de muestras a retornar
    
    Returns:
        dict con datos de entrenamiento
    """
    try:
        logger.info(f"📥 Cargando datos de entrenamiento desde: {model_path}")
        
        arima_model = MLStorageService.load_arima_model_from_directory(model_path)
        
        # Obtener datos de entrenamiento desde pmdarima
        try:
            endog = arima_model.arima_res_.data.endog.flatten()
            try:
                index = arima_model.arima_res_.data.dates
            except Exception:
                index = pd.RangeIndex(len(endog))
            endog_values = pd.Series(endog, index=index)
        except Exception:
            # Fallback
            endog_values = pd.Series(arima_model.arima_res_.data.endog.flatten())
        
        # Tomar últimas n_samples
        training_data = endog_values.iloc[-n_samples:] if len(endog_values) > n_samples else endog_values
        
        train_list = []
        for date, value in training_data.items():
            train_list.append({
                'date': date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date),
                'y': float(value)
            })
        
        logger.info(f"✅ {len(train_list)} muestras de entrenamiento cargadas")
        
        return {
            'training_samples': train_list,
            'total_training_points': len(endog_values)
        }
        
    except Exception as e:
        logger.error(f"❌ Error cargando datos de entrenamiento: {str(e)}")
        raise


def plot_arima_forecast(
    model_path: str,
    future_periods: int = 30,
    historical_periods: int = 50,
    figsize: tuple = (12, 5)
) -> dict:
    """
    Genera una gráfica de pronóstico ARIMA con histórico e intervalos de confianza.
    
    Args:
        model_path: Ruta al directorio del modelo
        future_periods: Número de periodos a pronosticar
        historical_periods: Número de periodos históricos a mostrar
        figsize: Tamaño de la figura (ancho, alto)
        
    Returns:
        Dict con imagen base64 y metadata
    """
    try:
        logger.info(f"📊 Generando gráfica de pronóstico ARIMA...")
        
        model_dir = Path(model_path)
        
        # Cargar modelo y metadatos
        arima_model = MLStorageService.load_arima_model_from_directory(str(model_dir))
        metadata = MLStorageService.load_arima_metadata(str(model_dir))
        
        if arima_model is None or metadata is None:
            raise ValueError("No se pudo cargar el modelo o metadatos")
        
        # Generar predicciones con pmdarima
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=FutureWarning)
            warnings.simplefilter("ignore", category=UserWarning)
            forecast_mean, conf_int = arima_model.predict(
                n_periods=future_periods,
                return_conf_int=True,
                alpha=0.05
            )
        forecast_mean = np.asarray(forecast_mean)
        conf_int = np.asarray(conf_int)
        
        # Obtener histórico - últimas N observaciones
        # pmdarima guarda los datos en arima_res_.data.endog
        try:
            endog = arima_model.arima_res_.data.endog
            try:
                hist_index = arima_model.arima_res_.data.dates
            except Exception:
                hist_index = range(len(endog))
            historical_data = pd.Series(endog.flatten(), index=hist_index)
        except Exception:
            historical_data = pd.Series(range(10))
        
        if len(historical_data) > historical_periods:
            historical_data = historical_data[-historical_periods:]
        
        # Crear figura
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plotear histórico
        ax.plot(
            historical_data.index,
            historical_data.values,
            'steelblue',
            label='Datos históricos',
            linewidth=2
        )
        
        # Generar índice de fechas para las predicciones
        try:
            last_hist_idx = historical_data.index[-1]
            freq = pd.infer_freq(historical_data.index)
            forecast_index = pd.date_range(
                start=last_hist_idx + pd.tseries.frequencies.to_offset(freq),
                periods=future_periods
            )
        except Exception:
            forecast_index = range(len(historical_data), len(historical_data) + future_periods)
        
        # Plotear pronóstico
        ax.plot(
            forecast_index,
            forecast_mean,
            'darkred',
            label='Pronóstico',
            linewidth=2,
            marker='o',
            markersize=5
        )
        
        # Intervalos de confianza (95%)
        ax.fill_between(
            forecast_index,
            conf_int[:, 0],
            conf_int[:, 1],
            color='red',
            alpha=0.2,
            label='95% Intervalo de confianza'
        )
        
        # Línea vertical separadora
        last_hist_date = historical_data.index[-1]
        ax.axvline(x=last_hist_date, color='gray', linestyle='--', alpha=0.7, linewidth=1)
        
        # Etiquetas y leyenda
        ax.set_xlabel('Fecha', fontsize=11)
        ax.set_ylabel('Valor', fontsize=11)
        order = metadata.get('order', (0, 0, 0))
        ax.set_title(f'Pronóstico ARIMA{order}', fontsize=13, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Rotar etiquetas x
        fig.autofmt_xdate()
        
        # Convertir a base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)
        
        logger.info("✅ Gráfica generada exitosamente")
        
        return {
            'status': 'éxito',
            'image': f'data:image/png;base64,{image_base64}',
            'parameters': {
                'order': order,
                'future_periods': future_periods,
                'historical_periods': len(historical_data),
                'aic': metadata.get('aic'),
                'bic': metadata.get('bic'),
                'rmse': metadata.get('rmse'),
                'mae': metadata.get('mae')
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error generando gráfica ARIMA: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }
