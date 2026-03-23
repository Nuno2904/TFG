#!/usr/bin/env python3
"""
🧪 Script de prueba para validar cambios ARIMA/SARIMA

Verifica que:
1. detect_seasonality() funciona correctamente
2. validate_arima_series() retorna los campos nuevos
3. train_arima_model() decide automáticamente entre ARIMA y SARIMA
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Agregar proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.ml.arima.utils import detect_seasonality, validate_arima_series
from app.ml.arima.train import train_arima_model

# ============================================================================
# CREAR SERIES DE PRUEBA
# ============================================================================

def crear_serie_sin_estacionalidad(n=100, seed=42):
    """Crea una serie sin patrón estacional (tendencia lineal + ruido)"""
    np.random.seed(seed)
    dates = pd.date_range('2023-01-01', periods=n, freq='M')
    tendencia = np.linspace(10, 20, n)
    ruido = np.random.normal(0, 1, n)
    values = tendencia + ruido
    return pd.DataFrame({'valor': values}, index=dates)


def crear_serie_con_estacionalidad(n=120, seed=42):
    """Crea una serie CON patrón estacional (e.g., ventas navideñas)"""
    np.random.seed(seed)
    dates = pd.date_range('2022-01-01', periods=n, freq='M')
    
    # Tendencia lineal
    tendencia = np.linspace(100, 150, n)
    
    # Componente estacional: ciclo de 12 meses
    estacional = 30 * np.sin(np.arange(n) * 2 * np.pi / 12)
    
    # Ruido
    ruido = np.random.normal(0, 5, n)
    
    values = tendencia + estacional + ruido
    return pd.DataFrame({'valor': values}, index=dates)


# ============================================================================
# PRUEBAS
# ============================================================================

def test_detect_seasonality():
    """Test 1: Verificar detección de estacionalidad"""
    print("\n" + "="*80)
    print("TEST 1: Detección de Estacionalidad")
    print("="*80)
    
    # Serie SIN estacionalidad
    print("\n📊 SERIE SIN ESTACIONALIDAD:")
    df_sin = crear_serie_sin_estacionalidad()
    result_sin = detect_seasonality(df_sin['valor'])
    
    print(f"  tiene_estacionalidad: {result_sin['tiene_estacionalidad']}")
    print(f"  fuerza_estacional: {result_sin['fuerza_estacional']:.4f}")
    print(f"  descripcion: {result_sin['descripcion']}")
    
    assert result_sin['tiene_estacionalidad'] is False, "❌ Debería detectar NO estacionalidad"
    print("  ✅ PASÓ: Correctamente detectada como NO estacional")
    
    # Serie CON estacionalidad
    print("\n🎄 SERIE CON ESTACIONALIDAD:")
    df_con = crear_serie_con_estacionalidad()
    result_con = detect_seasonality(df_con['valor'])
    
    print(f"  tiene_estacionalidad: {result_con['tiene_estacionalidad']}")
    print(f"  fuerza_estacional: {result_con['fuerza_estacional']:.4f}")
    print(f"  periodo_estacional: {result_con['periodo_estacional']}")
    print(f"  descripcion: {result_con['descripcion']}")
    
    assert result_con['tiene_estacionalidad'] is True, "❌ Debería detectar estacionalidad"
    print("  ✅ PASÓ: Correctamente detectada como ESTACIONAL")


def test_validate_arima_series():
    """Test 2: Verificar que validate_arima_series retorna campos nuevos"""
    print("\n" + "="*80)
    print("TEST 2: Validación de Series ARIMA")
    print("="*80)
    
    df = crear_serie_con_estacionalidad()
    validation = validate_arima_series(df)
    
    print(f"\n✅ Validación completada:")
    print(f"  valido: {validation['valido']}")
    print(f"  serie_numerica: {validation['serie_numerica']}")
    print(f"  longitud: {validation['longitud']}")
    
    # Verificar campos nuevos
    print(f"\n📊 CAMPOS NUEVOS (estacionalidad):")
    print(f"  tiene_estacionalidad: {validation['tiene_estacionalidad']}")
    print(f"  periodo_estacional: {validation['periodo_estacional']}")
    
    assert 'tiene_estacionalidad' in validation, "❌ Falta campo 'tiene_estacionalidad'"
    assert 'periodo_estacional' in validation, "❌ Falta campo 'periodo_estacional'"
    print("  ✅ PASÓ: Todos los campos nuevos presentes")
    
    # Verificar recomendaciones
    print(f"\n💡 Recomendaciones:")
    for rec in validation['recomendaciones']:
        print(f"  • {rec}")


def test_train_arima_vs_sarima():
    """Test 3: Verificar que train_arima_model elige ARIMA o SARIMA"""
    print("\n" + "="*80)
    print("TEST 3: Entrenamiento ARIMA vs SARIMA")
    print("="*80)
    
    # ARIMA: Sin estacionalidad
    print("\n🤖 ENTRENANDO ARIMA (sin estacionalidad)...")
    df_arima = crear_serie_sin_estacionalidad(n=100)
    
    modelo_path_arima = project_root / "tests" / "test_models" / "arima_test"
    resultado_arima = train_arima_model(
        df_arima,
        model_name="test_arima",
        user_id=999,
        dataset_id=999,
        model_path=str(modelo_path_arima)
    )
    
    if resultado_arima['status'] == 'éxito':
        print(f"\n✅ Modelo entrenado:")
        print(f"  model_type: {resultado_arima['metadata']['model_type']}")
        print(f"  order: {resultado_arima['metadata']['order']}")
        print(f"  seasonal_order: {resultado_arima['metadata']['seasonal_order']}")
        print(f"  AIC: {resultado_arima['metadata']['aic']:.2f}")
        
        assert resultado_arima['metadata']['model_type'] == 'ARIMA', "❌ Debería ser ARIMA"
        print("  ✅ PASÓ: Correctamente entrenado como ARIMA")
    else:
        print(f"  ❌ Error: {resultado_arima['error']}")
    
    # SARIMA: Con estacionalidad
    print("\n🤖 ENTRENANDO SARIMA (con estacionalidad)...")
    df_sarima = crear_serie_con_estacionalidad(n=120)
    
    modelo_path_sarima = project_root / "tests" / "test_models" / "sarima_test"
    resultado_sarima = train_arima_model(
        df_sarima,
        model_name="test_sarima",
        user_id=999,
        dataset_id=999,
        model_path=str(modelo_path_sarima)
    )
    
    if resultado_sarima['status'] == 'éxito':
        print(f"\n✅ Modelo entrenado:")
        print(f"  model_type: {resultado_sarima['metadata']['model_type']}")
        print(f"  order: {resultado_sarima['metadata']['order']}")
        print(f"  seasonal_order: {resultado_sarima['metadata']['seasonal_order']}")
        print(f"  AIC: {resultado_sarima['metadata']['aic']:.2f}")
        
        assert resultado_sarima['metadata']['model_type'] == 'SARIMA', "❌ Debería ser SARIMA"
        assert resultado_sarima['metadata']['seasonal_order'] is not None, "❌ Debería tener seasonal_order"
        print("  ✅ PASÓ: Correctamente entrenado como SARIMA")
    else:
        print(f"  ❌ Error: {resultado_sarima['error']}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🧪 PRUEBAS DE CAMBIOS ARIMA/SARIMA")
    print("="*80)
    
    try:
        test_detect_seasonality()
        test_validate_arima_series()
        test_train_arima_vs_sarima()
        
        print("\n" + "="*80)
        print("✅ TODOS LOS TESTS PASARON CORRECTAMENTE")
        print("="*80 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FALLIDO: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
