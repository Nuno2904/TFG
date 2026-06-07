# ARIMA y SARIMA — Explicación para la defensa

## Qué es ARIMA

ARIMA (*Autoregressive Integrated Moving Average*) es un modelo estadístico clásico para la predicción de series temporales univariantes. Su nombre describe los tres mecanismos que lo componen:

- **AR (Autorregresivo, p)** — el valor actual depende de los valores anteriores de la propia serie. El parámetro p indica cuántos valores pasados se tienen en cuenta.
- **I (Integrado, d)** — la serie se diferencia d veces para hacerla estacionaria, es decir, para eliminar la tendencia y que la media sea constante a lo largo del tiempo.
- **MA (Media Móvil, q)** — el valor actual depende de los errores de predicción anteriores. El parámetro q indica cuántos errores pasados se incorporan.

Un modelo ARIMA se denota como **ARIMA(p, d, q)**.

---

## Qué es SARIMA

SARIMA (*Seasonal ARIMA*) es una extensión de ARIMA que añade una capa adicional de parámetros para modelar la estacionalidad, es decir, los patrones que se repiten con una periodicidad fija (mensual, anual, etc.).

A los parámetros (p, d, q) de ARIMA se añaden cuatro parámetros estacionales:

- **P** — componente autorregresiva estacional
- **D** — diferenciación estacional
- **Q** — media móvil estacional
- **m** — período estacional (ej: 12 para datos mensuales)

Un modelo SARIMA se denota como **SARIMA(p, d, q)(P, D, Q, m)**.

---

## Cómo se detecta la estacionalidad en TimeSeriesLab

Antes de decidir qué modelo entrenar, el sistema necesita responder una pregunta: ¿esta serie tiene un patrón que se repite con una periodicidad fija o no?

Para responderla, aplica una técnica llamada **descomposición estacional**, que consiste en desmontar la serie en tres partes separadas:

- **Tendencia** — la dirección general de los datos (sube, baja o se mantiene estable)
- **Estacionalidad** — el patrón que se repite cada cierto tiempo (por ejemplo, ventas que suben cada diciembre)
- **Residuo** — lo que queda después de extraer la tendencia y la estacionalidad, es decir, el ruido aleatorio que el modelo no puede explicar

Una vez separadas estas tres partes, el sistema mide cuánto "pesa" la componente estacional en comparación con el residuo. Si la estacionalidad es grande y el residuo es pequeño, significa que hay un patrón claro y repetido. Si la estacionalidad es pequeña y el residuo es grande, significa que los datos son básicamente ruido sin patrón definido.

Esta medida se llama **fuerza estacional** y se calcula así:

```
fuerza = varianza(estacional) / (varianza(estacional) + varianza(residual))
```

El resultado es un número entre 0 y 1. Si supera el umbral de **0.1** — es decir, si la componente estacional explica más del 10% de la variación total de los datos — el sistema considera que la serie tiene estacionalidad y elige SARIMA. Si no lo supera, elige ARIMA.

En la práctica, esto significa que el usuario no necesita saber si su serie es estacional o no. El sistema lo detecta automáticamente y elige el modelo más adecuado sin que el usuario tenga que tomar ninguna decisión.

El código responsable de esta detección está en `app/ml/arima/utils.py`, función `detect_seasonality()`.

---

## Cómo se calculan los parámetros p, d y q

Una vez decidido el tipo de modelo, el sistema necesita encontrar los valores óptimos de los parámetros. Esto se hace mediante la función `auto_arima` de la librería **pmdarima**, que prueba distintas combinaciones de parámetros y selecciona automáticamente la que minimiza el **criterio de información de Akaike (AIC)** — cuanto menor es el AIC, mejor equilibrio entre precisión y complejidad tiene el modelo.

Los rangos de búsqueda son distintos según el modelo:

**Para ARIMA** (sin estacionalidad):
- p entre 0 y 5
- d entre 0 y 2
- q entre 0 y 5

**Para SARIMA** (con estacionalidad), los rangos se reducen porque añadir los parámetros estacionales hace la búsqueda mucho más costosa computacionalmente:
- p, q entre 0 y 3
- d entre 0 y 1
- P, Q entre 0 y 1
- D entre 0 y 1
- m = período estacional detectado automáticamente

El parámetro `stepwise=True` activa una búsqueda inteligente en lugar de probar todas las combinaciones posibles, lo que reduce notablemente el tiempo de entrenamiento.

El código responsable está en `app/ml/arima/train.py`, líneas 122–167.

---

## AIC y BIC — cómo se elige el mejor modelo

Cuando `auto_arima` prueba distintas combinaciones de parámetros necesita una forma objetiva de compararlas y decidir cuál es la mejor. Para eso usa dos criterios estadísticos: AIC y BIC.

**AIC — Criterio de Información de Akaike**

El AIC mide el equilibrio entre lo bien que el modelo ajusta los datos y la complejidad del modelo. La idea es que un modelo más complejo (más parámetros) siempre ajustará mejor los datos de entrenamiento, pero corre el riesgo de aprenderse el ruido en lugar del patrón real — lo que se conoce como sobreajuste. El AIC penaliza la complejidad para evitarlo.

```
AIC = 2k - 2ln(L)
```

Donde `k` es el número de parámetros del modelo y `L` es la verosimilitud (lo bien que el modelo explica los datos). **Cuanto menor es el AIC, mejor es el modelo.**

**BIC — Criterio de Información Bayesiano**

El BIC funciona de forma similar al AIC pero penaliza la complejidad de forma más severa, especialmente cuando el conjunto de datos es grande. Tiende a favorecer modelos más simples.

```
BIC = k·ln(n) - 2ln(L)
```

Donde `n` es el número de observaciones. **Cuanto menor es el BIC, mejor es el modelo.**

**En la práctica**

En TimeSeriesLab, `auto_arima` usa el AIC como criterio principal de selección (`information_criterion='aic'`). Una vez entrenado el modelo ganador, tanto el AIC como el BIC se guardan en los metadatos del modelo y se muestran al usuario como indicadores de la calidad del ajuste, permitiéndole comparar distintos modelos entrenados sobre el mismo dataset.

---

## Por qué ARIMA tiene un límite mínimo de observaciones y Prophet no

**Pregunta:** ¿Por qué ARIMA exige al menos 50 observaciones mientras que Prophet no tiene ningún límite?

ARIMA es mucho más sensible a la cantidad de datos que Prophet. La razón técnica es que ARIMA estima sus parámetros p, d y q mediante métodos estadísticos que requieren suficientes observaciones para que la estimación sea fiable. Con pocos datos la varianza de esos parámetros es muy alta, lo que significa que el modelo podría encontrar parámetros completamente distintos si se añadiera un solo dato más — es decir, el modelo sería inestable.

Además, en este proyecto se usa `auto_arima`, que no solo estima un modelo sino que prueba decenas de combinaciones de parámetros y las compara. Con series cortas ese proceso puede fallar directamente o devolver un modelo sobreajustado a los pocos datos disponibles, aprendiendo el ruido en lugar del patrón real.

Prophet en cambio está diseñado desde el principio para ser más tolerante con datos escasos porque su enfoque es distinto: no estima parámetros estadísticos sino que ajusta componentes de tendencia y estacionalidad mediante regresión, lo que es un proceso más robusto ante la falta de datos aunque la calidad del resultado también se resienta.

En resumen: se puso el límite en ARIMA porque sin él el sistema podría entrenar modelos que matemáticamente son incorrectos o directamente fallar con errores difíciles de interpretar para el usuario. Prophet no tiene ese límite en el código, lo que supone una limitación del proyecto ya que no avisa al usuario cuando la serie es demasiado corta para obtener predicciones fiables.

---

## Tratamiento de valores faltantes

El sistema gestiona los valores faltantes en dos momentos distintos del proceso:

**1. Durante la carga del fichero**

Al subir un dataset, el sistema recorre fila por fila y rechaza cualquier fila que tenga una fecha vacía o un valor numérico no válido. Estas filas no se guardan en la base de datos. Es decir, el sistema no permite almacenar datos con huecos.

**2. Durante el entrenamiento ARIMA**

Como medida de seguridad, antes de entrenar el modelo el sistema comprueba si quedan nulos en la serie. Si los hay, los rellena automáticamente mediante **interpolación lineal**:

```python
series = series.interpolate(method='linear', limit_direction='both')
```

La interpolación lineal calcula el valor faltante trazando una línea recta entre el punto anterior y el siguiente y estimando el valor intermedio. Este tratamiento ocurre de forma interna y transparente para el usuario.

Prophet, por su parte, es robusto a valores ausentes de forma nativa y no requiere este paso adicional.

---

## Flujo completo resumido

```
Serie temporal del usuario
        │
        ▼
detect_seasonality() — descomposición estacional
        │
   fuerza > 0.1?
   /           \
  SÍ            NO
  │              │
  ▼              ▼
SARIMA        ARIMA
  │              │
  └──── auto_arima() busca p,d,q (y P,D,Q,m si SARIMA)
                │
                ▼
        Modelo entrenado + métricas (RMSE, AIC, BIC)
```
