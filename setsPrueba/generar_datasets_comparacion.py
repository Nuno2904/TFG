"""
Genera 6 datasets CSV diseñados para mostrar las diferencias de comportamiento
entre Prophet y ARIMA/SARIMA ante distintos tipos de series temporales.
"""
import pandas as pd
import numpy as np
from pathlib import Path

np.random.seed(42)
output_dir = Path(__file__).parent


# ─────────────────────────────────────────────────────────────────────────────
# DATASET 1 — Cambio brusco de tendencia (changepoint)
# Prophet detecta el punto de cambio. ARIMA extrapola la tendencia anterior y
# falla al predecir lo que viene después del giro.
# ─────────────────────────────────────────────────────────────────────────────
dates1 = pd.date_range(start='2019-01-01', periods=60, freq='MS')
i1 = np.arange(60)
y1 = np.where(
    i1 < 30,
    100 + 2.5 * i1 + np.random.normal(0, 3, 60),
    175 - 4.5 * (i1 - 30) + np.random.normal(0, 3, 60)
)
y1 = np.round(y1, 2)
pd.DataFrame({'ds': dates1.strftime('%Y-%m-%d'), 'y': y1}).to_csv(
    output_dir / 'comparacion_01_cambio_tendencia.csv', index=False
)
print("✅ comparacion_01_cambio_tendencia.csv")


# ─────────────────────────────────────────────────────────────────────────────
# DATASET 2 — Múltiples estacionalidades (horaria + semanal)
# Prophet modela ambos ciclos simultáneamente. ARIMA/SARIMA solo puede capturar
# un período estacional a la vez (o el diario o el semanal, no los dos).
# ─────────────────────────────────────────────────────────────────────────────
dates2 = pd.date_range(start='2024-01-01', periods=336, freq='h')
hours    = dates2.hour
weekdays = dates2.dayofweek  # 0=lunes … 6=domingo

daily_pattern  = 35 * np.sin(2 * np.pi * (hours - 6) / 24)   # pico al mediodía
weekly_pattern = np.where(weekdays < 5, 25, -25)              # laborable vs fin de semana
y2 = 100 + daily_pattern + weekly_pattern + np.random.normal(0, 6, 336)
y2 = np.round(np.maximum(y2, 0), 2)
pd.DataFrame({'ds': dates2.strftime('%Y-%m-%d %H:%M:%S'), 'y': y2}).to_csv(
    output_dir / 'comparacion_02_multiples_estacionalidades.csv', index=False
)
print("✅ comparacion_02_multiples_estacionalidades.csv")


# ─────────────────────────────────────────────────────────────────────────────
# DATASET 3 — Valores atípicos (outliers) pronunciados
# Prophet trata los outliers como ruido y no deja que distorsionen el modelo.
# ARIMA los incorpora como parte de la serie y sesga todas las predicciones.
# ─────────────────────────────────────────────────────────────────────────────
dates3 = pd.date_range(start='2019-01-01', periods=72, freq='MS')
i3 = np.arange(72)
y3 = 200 + 2 * i3 + 40 * np.sin(2 * np.pi * i3 / 12) + np.random.normal(0, 5, 72)

outlier_positions = [5, 15, 27, 41, 55, 67]
signs = [1, -1, 1, -1, 1, -1]
for pos, sign in zip(outlier_positions, signs):
    y3[pos] += sign * np.random.uniform(140, 190)

y3 = np.round(y3, 2)
pd.DataFrame({'ds': dates3.strftime('%Y-%m-%d'), 'y': y3}).to_csv(
    output_dir / 'comparacion_03_valores_atipicos.csv', index=False
)
print("✅ comparacion_03_valores_atipicos.csv")


# ─────────────────────────────────────────────────────────────────────────────
# DATASET 4 — Serie con huecos (fechas irregulares)
# Prophet acepta fechas irregulares directamente. ARIMA necesita una serie
# con frecuencia regular; los huecos rompen su estructura interna.
# ─────────────────────────────────────────────────────────────────────────────
dates4_full = pd.date_range(start='2019-01-01', periods=72, freq='MS')
i4 = np.arange(72)
y4_full = 300 + 1.5 * i4 + 35 * np.sin(2 * np.pi * i4 / 12) + np.random.normal(0, 4, 72)

# Eliminar 11 meses dispersos para crear huecos realistas
gaps = [3, 4, 12, 13, 14, 29, 30, 45, 46, 61, 62]
mask = np.ones(72, dtype=bool)
mask[gaps] = False

y4 = np.round(y4_full[mask], 2)
dates4 = dates4_full[mask]
pd.DataFrame({'ds': dates4.strftime('%Y-%m-%d'), 'y': y4}).to_csv(
    output_dir / 'comparacion_04_datos_con_huecos.csv', index=False
)
print("✅ comparacion_04_datos_con_huecos.csv")


# ─────────────────────────────────────────────────────────────────────────────
# DATASET 5 — Serie muy corta (24 registros, 2 años de datos mensuales)
# Prophet con 24 puntos aún puede trazar tendencia + estacionalidad anual.
# SARIMA(m=12) apenas tiene 2 ciclos completos; sus estimaciones son inestables.
# ─────────────────────────────────────────────────────────────────────────────
dates5 = pd.date_range(start='2023-01-01', periods=24, freq='MS')
i5 = np.arange(24)
y5 = 500 + 3 * i5 + 60 * np.sin(2 * np.pi * i5 / 12) + np.random.normal(0, 8, 24)
y5 = np.round(y5, 2)
pd.DataFrame({'ds': dates5.strftime('%Y-%m-%d'), 'y': y5}).to_csv(
    output_dir / 'comparacion_05_serie_corta.csv', index=False
)
print("✅ comparacion_05_serie_corta.csv")


# ─────────────────────────────────────────────────────────────────────────────
# DATASET 6 — Control: serie larga, limpia y regular (ambos modelos coinciden)
# 120 registros mensuales sin outliers, sin huecos, con tendencia suave y
# estacionalidad anual simple. Escenario ideal para ambos algoritmos.
# Sus predicciones deben ser casi idénticas.
# ─────────────────────────────────────────────────────────────────────────────
dates6 = pd.date_range(start='2014-01-01', periods=120, freq='MS')
i6 = np.arange(120)
y6 = 300 + 1.5 * i6 + 40 * np.sin(2 * np.pi * i6 / 12) + np.random.normal(0, 4, 120)
y6 = np.round(y6, 2)
pd.DataFrame({'ds': dates6.strftime('%Y-%m-%d'), 'y': y6}).to_csv(
    output_dir / 'comparacion_06_control_ambos_correctos.csv', index=False
)
print("✅ comparacion_06_control_ambos_correctos.csv")


print("\n✅ Todos los datasets generados en:", output_dir)
