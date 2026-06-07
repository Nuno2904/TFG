# Prophet — Explicación para la defensa

## Qué es Prophet

Prophet es una herramienta de código abierto desarrollada por Meta (antes Facebook) y publicada en 2017. Está diseñada para hacer accesible la predicción de series temporales a analistas sin conocimientos estadísticos avanzados, ofreciendo resultados de calidad con una configuración mínima.

A diferencia de ARIMA, que es un modelo estadístico que trabaja con los valores pasados de la serie de forma directa, Prophet es un **modelo aditivo descomponible**: en lugar de modelar la serie entera de golpe, la divide en componentes separadas y las modela de forma independiente.

---

## La ecuación de Prophet

```
Y(t) = g(t) + s(t) + h(t) + e(t)
```

- **Y(t)** — el valor predicho en el instante t
- **g(t)** — tendencia: la dirección general de los datos (crece, decrece o se estabiliza)
- **s(t)** — estacionalidad: los patrones que se repiten con periodicidad fija (semanal, anual...)
- **h(t)** — efectos de festivos o eventos especiales sobre el pronóstico
- **e(t)** — error residual: lo que el modelo no consigue explicar

El modelo aprende cada componente por separado y las suma para obtener la predicción final. Esto lo hace especialmente robusto porque un cambio brusco en la tendencia no arrastra al resto de componentes.

---

## Cómo funciona cada componente

**Tendencia g(t)**

Prophet detecta automáticamente cambios en la tendencia (*changepoints*), es decir, momentos en los que la serie cambia de dirección o de ritmo de crecimiento. No hace falta indicarle al modelo cuándo ocurren estos cambios: los identifica solo.

**Estacionalidad s(t)**

Prophet modela la estacionalidad mediante series de Fourier, que son combinaciones de funciones seno y coseno que permiten representar cualquier patrón periódico. En este proyecto se activa la estacionalidad anual (`yearly_seasonality=True`), lo que significa que el modelo busca patrones que se repiten cada 12 meses.

**Festivos h(t)**

Esta componente permite incorporar el efecto de fechas especiales (navidades, puentes, eventos concretos). En TimeSeriesLab esta componente no está implementada ya que quedaría fuera del alcance del proyecto, pero Prophet la incluye de forma nativa.

---

## Configuración usada en TimeSeriesLab

```python
model = Prophet(interval_width=0.95, yearly_seasonality=True)
```

- **`interval_width=0.95`** — el modelo genera intervalos de confianza del 95%. Esto significa que junto al valor predicho central (`yhat`) el modelo devuelve una banda superior (`yhat_upper`) e inferior (`yhat_lower`) entre las que se espera que caiga el valor real con una probabilidad del 95%.
- **`yearly_seasonality=True`** — activa la detección de patrones anuales.

---

## Formato de los datos

Prophet requiere que los datos de entrada tengan exactamente dos columnas:

- `ds` — la fecha de cada observación
- `y` — el valor numérico correspondiente

Este formato es obligatorio. El sistema transforma los datos del usuario a este formato automáticamente antes de pasárselos al modelo.

---

## Qué devuelve Prophet

Una vez entrenado, Prophet genera predicciones para períodos futuros mediante `make_future_dataframe`. Por cada período predicho devuelve:

- `yhat` — valor predicho central
- `yhat_lower` — límite inferior del intervalo de confianza al 95%
- `yhat_upper` — límite superior del intervalo de confianza al 95%

---

## Métricas de evaluación

Tras el entrenamiento, el sistema calcula tres métricas sobre los propios datos de entrenamiento para evaluar la calidad del ajuste:

- **MAE** (Error Absoluto Medio) — promedio de las diferencias absolutas entre el valor real y el predicho. Fácil de interpretar: está en las mismas unidades que los datos.
- **RMSE** (Raíz del Error Cuadrático Medio) — similar al MAE pero penaliza más los errores grandes al elevarlos al cuadrado. Más sensible a valores atípicos.
- **MAPE** (Error Porcentual Absoluto Medio) — expresa el error como porcentaje del valor real, lo que facilita comparar la calidad del modelo independientemente de la escala de los datos.

Estas métricas se guardan junto al modelo y se muestran al usuario en la interfaz.

---

## Cómo se persiste el modelo

El modelo entrenado se serializa en formato JSON y se guarda en disco. Esto permite cargarlo en cualquier momento posterior para generar nuevas predicciones sin necesidad de reentrenarlo. Prophet almacena también los datos de entrenamiento en `model.history`, lo que permite recuperar los valores históricos para mostrarlos junto a las predicciones en las gráficas.

---

## Ventajas e inconvenientes

**Ventajas:**
- Configuración mínima — funciona bien sin ajuste manual de parámetros
- Robusto ante valores ausentes y cambios de tendencia
- Genera intervalos de confianza de forma nativa
- Muy adecuado para el objetivo didáctico del proyecto

**Inconvenientes:**
- No es adecuado para series muy cortas
- Solo trabaja con series univariantes — no incorpora variables externas
- La componente de festivos requiere configuración manual y no está implementada en este proyecto

---

## Diferencia clave con ARIMA

| | Prophet | ARIMA/SARIMA |
|---|---|---|
| Enfoque | Modelo aditivo descomponible | Modelo estadístico autorregresivo |
| Parámetros | Automáticos | Automáticos via auto_arima |
| Estacionalidad | Múltiple (semanal, anual...) | Un único período estacional |
| Intervalos de confianza | Nativos | Nativos |
| Datos mínimos | Flexible | 50+ observaciones (ARIMA), 100+ (SARIMA) |
| Ideal para | Patrones estacionales fuertes y tendencias cambiantes | Series más cortas o sin estacionalidad compleja |
