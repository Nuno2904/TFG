"""
📊 ARIMA/SARIMA Utils - Validación de Series Temporales

Validaciones para ARIMA/SARIMA (asume 2 columnas: fecha + valores desde file_service):
- Estacionalidad (detección automática)
- Valores nulos
- Outliers
- Longitud mínima
- Frecuencia/continuidad
"""

import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.tsa.seasonal import seasonal_decompose
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# VALIDACIONES BÁSICAS (LA ESTRUCTURA YA VIENE DEL FILE_SERVICE)
# ============================================================================

def validate_frequency(df: pd.DataFrame) -> dict:
    """
    Valida frecuencia e índice datetime.
    
    Args:
        df: DataFrame con índice datetime
        
    Returns:
        dict con frecuencia detectada y avisos
    """
    resultado = {
        'valido': True,
        'avisos': [],
        'frecuencia': None
    }
    
    # Detectar frecuencia
    freq = pd.infer_freq(df.index)
    if freq is None:
        resultado['avisos'].append("⚠️ No se detecta frecuencia constante")
        resultado['frecuencia'] = "IRREGULAR"
    else:
        resultado['frecuencia'] = freq
        logger.info(f"✅ Frecuencia: {freq}")
    
    return resultado


# ============================================================================
# DETECCION DE ESTACIONALIDAD
# ============================================================================

def detect_seasonality(series: pd.Series, max_period: int = 24) -> dict:
    """
    Detecta estacionalidad en la serie temporal.
    
    La estacionalidad es un patrón que se repite en ciclos (ej: ventas en navidad).
    
    Args:
        series: Serie temporal a analizar
        max_period: Período máximo a considerar (default: 24, típico para datos mensales=12 años)
        
    Returns:
        dict: {
            'tiene_estacionalidad': bool,
            'periodo_estacional': int o None,
            'fuerza_estacional': float (0-1),
            'descripcion': str
        }
    """
    try:
        series_clean = series.dropna()
        
        if len(series_clean) < max_period * 2:
            logger.warning(f"⚠️ Serie muy corta ({len(series_clean)} obs) para detectar estacionalidad")
            return {
                'tiene_estacionalidad': None,
                'periodo_estacional': None,
                'fuerza_estacional': None,
                'descripcion': f"⚠️ Insuficientes datos ({len(series_clean)} < {max_period*2})"
            }
        
        # Descomponer la serie para analizar estacionalidad
        try:
            # Intentar descomposición con período automático
            decomposition = seasonal_decompose(series_clean, period=12, model='additive')
            seasonal = decomposition.seasonal
            residual = decomposition.resid
            
            # Calcular fuerza de estacionalidad
            # Varianza de la componente estacional vs. varianza total
            var_seasonal = np.var(seasonal.dropna())
            var_residual = np.var(residual.dropna())
            fuerza = var_seasonal / (var_seasonal + var_residual) if (var_seasonal + var_residual) > 0 else 0
            
            tiene_estacionalidad = fuerza > 0.1  # >10% indica estacionalidad
            
            logger.info(f"🔍 Estacionalidad detectada: {tiene_estacionalidad}")
            logger.info(f"   Fuerza estacional: {fuerza:.4f}")
            
            if tiene_estacionalidad:
                return {
                    'tiene_estacionalidad': True,
                    'periodo_estacional': 12,  # Asumiendo datos mensuales
                    'fuerza_estacional': float(fuerza),
                    'descripcion': f"✅ Estacionalidad detectada (período=12, fuerza={fuerza:.4f})"
                }
            else:
                return {
                    'tiene_estacionalidad': False,
                    'periodo_estacional': None,
                    'fuerza_estacional': float(fuerza),
                    'descripcion': f"❌ Sin estacionalidad significativa (fuerza={fuerza:.4f})"
                }
                
        except Exception as decomp_error:
            logger.warning(f"⚠️ Error en descomposición: {decomp_error}")
            return {
                'tiene_estacionalidad': None,
                'periodo_estacional': None,
                'fuerza_estacional': None,
                'descripcion': f"⚠️ No se pudo detectar estacionalidad: {str(decomp_error)}"
            }
            
    except Exception as e:
        logger.error(f"Error en detección de estacionalidad: {str(e)}")
        return {
            'tiene_estacionalidad': None,
            'periodo_estacional': None,
            'fuerza_estacional': None,
            'error': str(e)
        }



# ============================================================================
# DETECCION DE OUTLIERS
# ============================================================================

def detect_outliers(series: pd.Series, method: str = 'iqr', threshold: float = 1.5) -> dict:
    """
    Detecta outliers en la serie usando IQR o Z-score.
    
    Args:
        series: Serie a analizar
        method: 'iqr' (Interquartile Range) o 'zscore'
        threshold: Multiplicador para IQR (default: 1.5) o desviaciones sigma para Z-score (default: 3)
        
    Returns:
        dict: {
            'num_outliers': int,
            'pct_outliers': float,
            'outlier_indices': [indices],
            'metodo': str,
            'es_problematico': bool (si >5% outliers)
        }
    """
    series_clean = series.dropna()
    
    if method == 'iqr':
        Q1 = series_clean.quantile(0.25)
        Q3 = series_clean.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        
        outlier_mask = (series_clean < lower_bound) | (series_clean > upper_bound)
    
    elif method == 'zscore':
        z_scores = np.abs(stats.zscore(series_clean))
        outlier_mask = z_scores > threshold
    
    else:
        raise ValueError(f"Método desconocido: {method}")
    
    num_outliers = outlier_mask.sum()
    pct_outliers = (num_outliers / len(series_clean)) * 100
    
    return {
        'num_outliers': num_outliers,
        'pct_outliers': pct_outliers,
        'outlier_indices': series_clean[outlier_mask].index.tolist(),
        'metodo': method,
        'es_problematico': pct_outliers > 5  # >5% es problemático para ARIMA
    }



# ============================================================================
# VALIDACIONES DE LONGITUD Y NULOS
# ============================================================================

def validate_minimum_length(series: pd.Series, min_length: int = 50) -> dict:
    """
    Valida longitud mínima.
    
    ARIMA requiere al menos 50 datos para estimaciones confiables de parámetros.
    Con menos de 50 puntos, la varianza de los parámetros es muy alta.
    """
    longitud = len(series.dropna())
    es_valido = longitud >= min_length
    
    return {
        'valido': es_valido,
        'longitud': longitud,
        'min_recomendado': min_length,
        'aviso': (
            f"❌ ARIMA requiere ≥{min_length} datos. Solo tienes {longitud}. "
            f"Con pocas observaciones, los parámetros ARIMA(p,d,q) no se estiman de forma confiable. "
            f"Considera: (1) Agregar más datos históricos, (2) Usar Prophet en su lugar (más flexible con datos cortos), "
            f"o (3) Usar ARIMA estándar con parámetros (1,1,1) fijos (no automático)."
            if not es_valido else (
                f"⚠️ Solo {longitud} obs. Se recomienda ≥100 para estimaciones más robustas."
                if longitud < 100 else None
            )
        )
    }


def validate_nulls(series: pd.Series) -> dict:
    """
    Valida presencia de nulos.
    """
    num_nulos = series.isnull().sum()
    pct_nulos = (num_nulos / len(series)) * 100 if len(series) > 0 else 0
    
    return {
        'num_nulos': int(num_nulos),
        'pct_nulos': round(pct_nulos, 2),
        'aviso': (
            f"⚠️ {num_nulos} nulos ({pct_nulos:.2f}%). Interpolar recomendado."
            if num_nulos > 0 else None
        )
    }


# ============================================================================
# VALIDACION GENERAL COMPLETA
# ============================================================================

def validate_arima_series(df: pd.DataFrame) -> dict:
    """
    Validación COMPLETA para ARIMA/SARIMA (asume 2 columnas: fecha + valores).
    
    Args:
        df: DataFrame con índice datetime + 1 columna numérica
        
    Returns:
        dict con reporte completo o error crítico
    """
    
    try:
        # 1. Obtener la serie numérica
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) != 1:
            return {
                'valido': False,
                'error': f"❌ Se esperaba 1 columna numérica, se encontraron {len(numeric_cols)}"
            }
        
        numeric_col = numeric_cols[0]
        series = df[numeric_col]
        
        # 2. Realizar validaciones
        length_check = validate_minimum_length(series)
        nulls_check = validate_nulls(series)
        freq_check = validate_frequency(df)
        seasonality_check = detect_seasonality(series)
        outlier_check = detect_outliers(series)
        
        # 3. Determinar validez general
        es_valido = (
            length_check['valido'] and 
            not outlier_check['es_problematico']
        )
        
        return {
            'valido': es_valido,
            'serie_numerica': numeric_col,
            'longitud': series.shape[0],
            'tiene_estacionalidad': seasonality_check.get('tiene_estacionalidad'),
            'periodo_estacional': seasonality_check.get('periodo_estacional'),
            'validaciones': {
                'longitud': length_check,
                'nulos': nulls_check,
                'frecuencia': freq_check,
                'estacionalidad': seasonality_check,
                'outliers': outlier_check
            },
            'recomendaciones': _generate_recommendations(seasonality_check, nulls_check, outlier_check)
        }
        
    except Exception as e:
        logger.error(f"Error en validación ARIMA/SARIMA: {str(e)}")
        return {
            'valido': False,
            'error': f"Error: {str(e)}"
        }


# ============================================================================
# RECOMENDACIONES
# ============================================================================

def _generate_recommendations(seasonality: dict, nulls: dict, outliers: dict) -> list:
    """
    Genera recomendaciones basadas en validaciones.
    """
    recs = []
    
    if seasonality.get('tiene_estacionalidad') is True:
        recs.append(f"📌 Estacionalidad detectada → Usar SARIMA(p,d,q)(P,D,Q,m={seasonality['periodo_estacional']})")
    elif seasonality.get('tiene_estacionalidad') is False:
        recs.append(f"📌 Sin estacionalidad → Usar ARIMA(p,d,q)")
    else:
        recs.append(f"📌 Estacionalidad indeterminada → Verificar manualmente")
    
    if nulls['pct_nulos'] > 0:
        recs.append(f"📌 Interpolar {nulls['num_nulos']} nulos antes de entrenar")
    
    if outliers['pct_outliers'] > 2:
        recs.append(f"📌 Limpiar {outliers['num_outliers']} outliers ({outliers['pct_outliers']:.1f}%)")
    
    return recs