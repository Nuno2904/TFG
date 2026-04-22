# 🔬 Datasets de Comparación: Prophet vs ARIMA/SARIMA

Colección de 6 datasets diseñados para mostrar empíricamente las diferencias de
comportamiento entre **Prophet** y **ARIMA/SARIMA** ante distintos tipos de series
temporales. Cada dataset aísla una característica concreta que hace que los dos
modelos se comporten de forma diferente.

Para regenerarlos ejecuta:
```bash
python setsPrueba/generar_datasets_comparacion.py
```

---

## 📁 Descripción de cada dataset

---

### `comparacion_01_cambio_tendencia.csv`

| Característica | Valor |
|---|---|
| Frecuencia | Mensual |
| Registros | 60 (5 años) |
| Columnas | `ds`, `y` |

**Qué tiene de especial:**  
La serie tiene una **tendencia ascendente durante los primeros 30 meses** (+2.5/mes)
y después gira bruscamente a una **tendencia descendente** (−4.5/mes). El punto de
cambio está en el mes 30.

**Comportamiento esperado:**
- **Prophet** → Detecta el *changepoint* automáticamente gracias a su mecanismo de
  puntos de cambio de tendencia. Las predicciones futuras reflejan correctamente
  el giro.
- **ARIMA** → No tiene mecanismo para detectar cambios de tendencia. Extrapola la
  tendencia media de toda la serie y produce predicciones que se alejan
  progresivamente de la realidad.

---

### `comparacion_02_multiples_estacionalidades.csv`

| Característica | Valor |
|---|---|
| Frecuencia | Horaria |
| Registros | 336 (14 días) |
| Columnas | `ds`, `y` |

**Qué tiene de especial:**  
La serie combina **dos estacionalidades simultáneas**:
- **Ciclo diario**: pico al mediodía, mínimo en la madrugada (amplitud ±35).
- **Ciclo semanal**: valores ~25 unidades más altos en días laborables que en fin
  de semana.

**Comportamiento esperado:**
- **Prophet** → Modela ambos ciclos al mismo tiempo con series de Fourier para cada
  período. Captura con precisión los picos diarios diferenciando laborables de
  fin de semana.
- **ARIMA/SARIMA** → Solo puede especificar **un único período estacional** en el
  parámetro `m`. Si elige el ciclo diario (m=24), pierde el semanal, y viceversa.
  Las predicciones suavizan uno de los dos patrones y tienen error sistemático.

---

### `comparacion_03_valores_atipicos.csv`

| Característica | Valor |
|---|---|
| Frecuencia | Mensual |
| Registros | 72 (6 años) |
| Columnas | `ds`, `y` |

**Qué tiene de especial:**  
Serie con tendencia lineal suave + estacionalidad anual, pero con **6 outliers
extremos** (±140–190 unidades sobre el nivel esperado) distribuidos a lo largo de
la serie. Los outliers alternan entre picos positivos y negativos.

**Comportamiento esperado:**
- **Prophet** → Trata los outliers como ruido irreducible. El modelo aprende la
  tendencia y estacionalidad reales ignorando los picos extremos. Las predicciones
  no se ven afectadas.
- **ARIMA** → Los outliers forman parte de la serie que el modelo intenta ajustar.
  Los términos AR y MA se calibran parcialmente en torno a ellos, sesgando las
  predicciones hacia valores más altos o bajos de lo que la serie "real" indicaría.

**Qué ocurre realmente al predecir:**

| | Lo que pasa | Por qué |
|---|---|---|
| **ARIMA** | Predicción plana, pierde la tendencia | Los outliers sesgan la media y los coeficientes AR/MA |
| **Prophet** | Predicción se dispara a valores absurdos | Confunde los outliers con un patrón estacional real |

Ambos modelos fallan, pero de formas distintas. ARIMA produce una línea plana
perdiendo completamente la tendencia ascendente y la estacionalidad. Prophet,
en cambio, interpreta los picos extremos como si fueran parte de un patrón
estacional recurrente y los proyecta hacia el futuro, generando predicciones
disparadas muy por encima del rango real de los datos.

Esto demuestra que **la robustez de Prophet frente a outliers tiene un límite**:
funciona bien con valores atípicos moderados y aislados, pero cuando los outliers
son suficientemente extremos y frecuentes, Prophet los confunde con estacionalidad
real. Con outliers de esta magnitud, ningún modelo es inmune sin un preprocesado
previo que los elimine o atenúe.

---

### `comparacion_04_datos_con_huecos.csv`

| Característica | Valor |
|---|---|
| Frecuencia | Mensual irregular |
| Registros | 61 (de 72 posibles; 11 meses eliminados) |
| Columnas | `ds`, `y` |

**Qué tiene de especial:**  
Serie mensual a la que se le han eliminado **11 meses** en distintos puntos
(algunos aislados, otros en rachas de 2–3 meses consecutivos), creando una serie
con **fechas irregulares**. El patrón subyacente es tendencia + estacionalidad anual.

**Comportamiento esperado:**
- **Prophet** → Acepta fechas irregulares de forma nativa. El modelo recibe las
  fechas tal cual y reconstruye la tendencia y la estacionalidad sin necesidad de
  imputar los huecos.
- **ARIMA** → Requiere una serie con **frecuencia fija y regular**. Los huecos
  rompen la estructura de autocorrelación. El sistema necesita imputar los valores
  faltantes antes de poder entrenar, lo que introduce un error adicional que puede
  distorsionar los parámetros (p, d, q).

**Qué ocurre realmente al entrenar:**

| | Lo que pasa | Por qué |
|---|---|---|
| **Prophet** | Entrena y predice con normalidad | Trabaja directamente con las fechas que hay, sin asumir regularidad |
| **ARIMA** | **Error al entrenar: no puede entrenar** | Al detectar fechas irregulares, `auto_arima` no puede inferir la frecuencia de la serie y el proceso falla antes de llegar a la predicción |

Este dataset demuestra una de las limitaciones más prácticas de ARIMA: en el
mundo real los datos casi nunca son perfectamente regulares (festivos, fines de
semana sin registros, errores de captura...). **Con ARIMA cualquier hueco requiere
un paso previo de imputación o relleno**; con Prophet ese paso no es necesario.

---

### `comparacion_05_serie_corta.csv`

| Característica | Valor |
|---|---|
| Frecuencia | Mensual |
| Registros | 24 (2 años exactos) |
| Columnas | `ds`, `y` |

**Qué tiene de especial:**  
Serie deliberadamente corta con **solo 2 ciclos completos** de estacionalidad
anual. Es el límite inferior práctico para intentar modelar estacionalidad de
período 12.

**Comportamiento esperado:**
- **Prophet** → Con 24 puntos puede trazar la tendencia y la estacionalidad anual
  de forma razonable. Las predicciones son imperfectas pero tienen sentido.
- **SARIMA (m=12)** → Necesita al menos 3–4 ciclos completos para estimar de forma
  fiable los parámetros estacionales (P, D, Q). Con solo 2 ciclos y la
  diferenciación estacional (D=1) consumiendo 12 observaciones, el modelo queda
  con muy pocos grados de libertad. Los errores estándar de los coeficientes se
  disparan y las predicciones son inestables.

---

### `comparacion_06_control_ambos_correctos.csv`

| Característica | Valor |
|---|---|
| Frecuencia | Mensual |
| Registros | 120 (10 años) |
| Columnas | `ds`, `y` |

**Qué tiene de especial:**  
Dataset de **control**: serie larga, limpia, sin outliers, sin huecos, con
tendencia lineal suave (+1.5/mes) y estacionalidad anual simple (amplitud ±40).
Es el escenario ideal para ambos modelos.

**Comportamiento esperado:**
- **Prophet** → Predicciones precisas y suaves.
- **ARIMA/SARIMA** → Predicciones precisas y suaves.
- **Ambos modelos deberían producir predicciones casi idénticas**, ya que la serie
  no presenta ninguna característica que favorezca a uno sobre el otro. Este
  dataset sirve de línea base para comparar visualmente qué tan distintas son las
  predicciones en los otros 5 casos.

---

## 📊 Resumen comparativo

| Dataset | Nº registros | Frecuencia | Característica diferenciadora | Ventaja |
|---|---|---|---|---|
| 01 Cambio tendencia | 60 | Mensual | Giro brusco de pendiente en t=30 | **Prophet** |
| 02 Múlt. estacionalidades | 336 | Horaria | Ciclo diario + ciclo semanal simultáneos | **Prophet** |
| 03 Valores atípicos | 72 | Mensual | 6 outliers extremos ±140–190 | **Prophet** |
| 04 Datos con huecos | 61 | Mensual irregular | 11 meses eliminados, fechas irregulares | **Prophet** |
| 05 Serie corta | 24 | Mensual | Solo 2 ciclos anuales completos | **Prophet** |
| 06 Control | 120 | Mensual | Larga, limpia, regular, sin anomalías | **Empate** |

En todos los casos donde Prophet tiene ventaja, ARIMA no falla por ser un mal
modelo sino porque **la naturaleza de los datos viola alguno de sus supuestos
fundamentales** (regularidad, estacionariedad, ausencia de outliers, un solo
período estacional). Prophet, al modelar los componentes explícitamente en lugar
de depender de la autocorrelación, es más robusto frente a estas situaciones.
