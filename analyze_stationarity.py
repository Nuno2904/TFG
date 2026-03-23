import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller, kpss
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# Leer el archivo Excel
file_path = r'Datos para Pruebas Estacionarias.xlsx'
df = pd.read_excel(file_path)

print('=' * 80)
print('ANÁLISIS DE ESTACIONARIEDAD DE SERIES TEMPORALES')
print('=' * 80)

print(f'\nDimensiones de los datos: {df.shape}')
print(f'\nColumnas: {list(df.columns)}')
print(f'\nPrimeras 10 filas:')
print(df.head(10))
print(f'\nÚltimas 10 filas:')
print(df.tail(10))
print(f'\nEstadísticas descriptivas:')
print(df.describe())

# Analizar cada columna numérica
numeric_cols = df.select_dtypes(include=[np.number]).columns

print('\n' + '=' * 80)
print('PRUEBAS DE ESTACIONARIEDAD')
print('=' * 80)

for col in numeric_cols:
    print(f'\n\n{"=" * 40}')
    print(f'Columna: {col}')
    print(f'{"=" * 40}')
    
    # Usar solo valores no nulos
    series = df[col].dropna()
    
    if len(series) < 4:
        print(f'⚠️  Insuficientes datos para análisis ({len(series)} valores)')
        continue
    
    print(f'\nNúmero de observaciones: {len(series)}')
    print(f'Media: {series.mean():.4f}')
    print(f'Desviación estándar: {series.std():.4f}')
    print(f'Min: {series.min():.4f}')
    print(f'Max: {series.max():.4f}')
    
    # Prueba ADF (Augmented Dickey-Fuller)
    print(f'\n--- Prueba ADF (Augmented Dickey-Fuller) ---')
    try:
        adf_result = adfuller(series, autolag='AIC')
        print(f'Estadístico ADF: {adf_result[0]:.6f}')
        print(f'P-valor: {adf_result[1]:.6f}')
        print(f'Número de rezagos: {adf_result[2]}')
        print(f'Número de observaciones: {adf_result[3]}')
        print(f'Valores críticos:')
        for key, value in adf_result[4].items():
            print(f'  {key}: {value:.4f}')
        
        if adf_result[1] < 0.05:
            print(f'✅ RESULTADO: SERIE ESTACIONARIA (rechazamos H0, p < 0.05)')
        else:
            print(f'❌ RESULTADO: SERIE NO ESTACIONARIA (no rechazamos H0, p >= 0.05)')
    except Exception as e:
        print(f'Error en ADF: {e}')
    
    # Prueba KPSS (Kwiatkowski-Phillips-Schmidt-Shin)
    print(f'\n--- Prueba KPSS (Kwiatkowski-Phillips-Schmidt-Shin) ---')
    try:
        kpss_result = kpss(series, regression='c', nlags='auto')
        print(f'Estadístico KPSS: {kpss_result[0]:.6f}')
        print(f'P-valor: {kpss_result[1]:.6f}')
        print(f'Número de rezagos: {kpss_result[2]}')
        print(f'Valores críticos:')
        for key, value in kpss_result[3].items():
            print(f'  {key}: {value:.4f}')
        
        if kpss_result[1] > 0.05:
            print(f'✅ RESULTADO: SERIE ESTACIONARIA (no rechazamos H0, p > 0.05)')
        else:
            print(f'❌ RESULTADO: SERIE NO ESTACIONARIA (rechazamos H0, p <= 0.05)')
    except Exception as e:
        print(f'Error en KPSS: {e}')

print('\n' + '=' * 80)
print('CONCLUSIÓN GENERAL')
print('=' * 80)
print('\nUNA SERIE ES ESTACIONARIA SI:')
print('  • P-valor en ADF < 0.05 (rechaza H0: existe raíz unitaria)')
print('  • P-valor en KPSS > 0.05 (no rechaza H0: serie es estacionaria)')
print('  • Ambas pruebas coinciden en que la serie es estacionaria')
