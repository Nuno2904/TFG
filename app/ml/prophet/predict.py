#para poder predecir lo primero que tenemos qeu asegurarnos es de que el modelo está entrenado, esto hay que mirarlo. 
#si el modelo está entrenado, lo cargamos y hacemos la predicción.
#si el modelo no está entrenado, devolvemos un error diciendo que el modelo no está entrenado y que no se pueden hacer predicciones.
#tiene que poder predecir: intervalso de confianza, erores relativ, error absoluto, ha de ser capaz de ostrar varios tipos de gráficas. 
from prophet.serialize import model_to_json, model_from_json
from prophet.plot import plot_plotly, plot_components_plotly
import pandas as pd
import logging
from pathlib import Path
from sqlalchemy.orm import Session
from app.services.ml_storage_service import MLStorageService
from app.models.data import Data
from app.models.ml import MLModel
import matplotlib.pyplot as plt

# Importar plotly de forma segura
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    logger_setup = logging.getLogger(__name__)
    logger_setup.warning("⚠️ Plotly not installed. Interactive plots will not be available.")


logger = logging.getLogger(__name__)

def predict_prophet_model(
    model_path: str, 
    future_periods: int = 30
) -> dict:
    """
    Realiza predicciones utilizando un modelo Prophet previamente entrenado.
    
    Args:
        model_path (str): Ruta local donde se encuentra el directorio del modelo guardado.
        future_periods (int): Número de períodos futuros a predecir (default: 30).
    
    Returns:
        dict: Diccionario con las predicciones y métricas de evaluación.
        
    Raises:
        FileNotFoundError: Si el modelo no se encuentra en la ruta especificada.
        Exception: Si la predicción falla por cualquier otro motivo.
    """
    
    try:
        logger.info(f"🔍 Cargando modelo Prophet desde: {model_path}")
        
        # Usar la función centralizada que busca el .json en el directorio
        prophet_model = MLStorageService.load_prophet_model_from_directory(model_path)
        
        logger.info("✅ Modelo cargado exitosamente")
        
        # Crear un DataFrame vacío para generar las fechas futuras
        future_df = prophet_model.make_future_dataframe(periods=future_periods)
        
        logger.info(f"📅 Generando predicciones para los próximos {future_periods} períodos...")
        
        # Realizar la predicción
        forecast = prophet_model.predict(future_df)
        
        logger.info("✅ Predicciones generadas exitosamente")
        
        # Devolver las predicciones como un diccionario
        return forecast.to_dict(orient='records')
    
    except FileNotFoundError:
        logger.error(f"❌ Modelo no encontrado en la ruta: {model_path}")
        raise FileNotFoundError(f"Modelo no encontrado en la ruta: {model_path}")
    
    except Exception as e:
        logger.error(f"❌ Error durante la predicción: {str(e)}")
        raise Exception(f"Error durante la predicción: {str(e)}")
    


def prophet_plot(model, forecast):
    """
    Genera gráficos de las predicciones del modelo Prophet.
    
    Args:
        model: El modelo Prophet entrenado.
        forecast: El DataFrame con las predicciones generadas por el modelo.
    Returns:
        dict: Diccionario con las figuras de los gráficos generados.
    """
    try:
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly is not installed. Install it with: pip install plotly")
        
        # Gráfico de la predicción
        fig1 = plot_plotly(model, forecast)
        
        # Gráfico de los componentes (tendencia, estacionalidad, etc.)
        fig2 = plot_components_plotly(model, forecast)
        
        return {
            "forecast_plot": fig1.to_json(),
            "components_plot": fig2.to_json()    
        }
    
    except ImportError as e:
        logger.error(f"❌ Error importando librerías de gráficos: {str(e)}")
        raise ImportError(f"Error importando librerías de gráficos: {str(e)}")
    
    except Exception as e:
        logger.error(f"❌ Error generando gráficos: {str(e)}")
        raise Exception(f"Error generando gráficos: {str(e)}")


def get_training_samples(model_path: str, n_samples: int = 100) -> dict:
    """
    Obtiene valores de entrenamiento del modelo Prophet para visualización.
    
    Args:
        model_path: Ruta del directorio del modelo
        n_samples: Número de muestras a retornar
    
    Returns:
        dict con datos de entrenamiento
    """
    try:
        logger.info(f"📥 Cargando datos de entrenamiento Prophet desde: {model_path}")
        
        prophet_model = MLStorageService.luego (model_path)
        
        # Prophet almacena los datos de entrenamiento en model.history
        history = prophet_model.history
        
        if history is None or history.empty:
            raise ValueError("No training data found in Prophet model")
        
        # Tomar últimas n_samples
        training_data = history.tail(n_samples)
        
        train_list = []
        for _, row in training_data.iterrows():
            train_list.append({
                'date': row['ds'].strftime('%Y-%m-%d') if hasattr(row['ds'], 'strftime') else str(row['ds']),
                'y': float(row['y'])
            })
        
        logger.info(f"✅ {len(train_list)} muestras de entrenamiento Prophet cargadas")
        
        return {
            'training_samples': train_list,
            'total_training_points': len(history)
        }
        
    except Exception as e:
        logger.error(f"❌ Error cargando datos de entrenamiento Prophet: {str(e)}")
        raise