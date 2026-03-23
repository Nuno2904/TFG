# 🔄 Cambios ARIMA → ARIMA/SARIMA

## 📋 Resumen de Modificaciones

Se ha convertido el sistema de entrenamiento de ARIMA a un sistema híbrido que detecta automáticamente si la serie tiene estacionalidad y entrena el modelo correspondiente.

---

## 🗑️ Funciones Eliminadas

### ❌ `validate_stationarity()` - YA NO SE USA
- **Motivo**: La estacionariedad se maneja automáticamente con el parámetro `d` en auto_arima
- **Eliminada de**: `app/ml/arima/utils.py`
- **Importación eliminada**: `from statsmodels.tsa.stattools import adfuller`

---

## ✨ Funciones Nuevas

### ✅ `detect_seasonality()` - NUEVA
**Ubicación**: `app/ml/arima/utils.py`

```python
def detect_seasonality(series: pd.Series, max_period: int = 24) -> dict:
    """
    Detecta estacionalidad en la serie temporal usando descomposición seasonal_decompose.
    
    Retorna:
        - tiene_estacionalidad: bool
        - periodo_estacional: int (típicamente 12 para datos mensuales)
        - fuerza_estacional: float (0-1, donde >0.1 = hay estacionalidad)
        - descripcion: str con explicación
    """
```

**Lógica**:
- Descompone la serie en Tendencia + Estacionalidad + Residuos
- Calcula relación: `fuerza = var(seasonal) / (var(seasonal) + var(residual))`
- Si `fuerza > 0.1` → Hay estacionalidad significativa

---

## 📝 Funciones Modificadas

### 1. `validate_arima_series()` 
**Cambios**:
- Ahora llama a `detect_seasonality()` en lugar de `validate_stationarity()`
- Retorna nuevos campos:
  - `tiene_estacionalidad`: bool
  - `periodo_estacional`: int
  
```python
return {
    'valido': es_valido,
    'serie_numerica': numeric_col,
    'longitud': series.shape[0],
    'tiene_estacionalidad': seasonality_check.get('tiene_estacionalidad'),  # ✨ NUEVO
    'periodo_estacional': seasonality_check.get('periodo_estacional'),      # ✨ NUEVO
    'validaciones': {...},
    'recomendaciones': [...]
}
```

### 2. `_generate_recommendations()`
**Cambios en recomendaciones**:
```python
if seasonality.get('tiene_estacionalidad') is True:
    # Recomienda SARIMA
    recs.append(f"📌 Estacionalidad detectada → Usar SARIMA(p,d,q)(P,D,Q,m=12)")

elif seasonality.get('tiene_estacionalidad') is False:
    # Recomienda ARIMA
    recs.append(f"📌 Sin estacionalidad → Usar ARIMA(p,d,q)")
```

---

## 🤖 `train_arima_model()` - COMPLETAMENTE REFACTORIZADO

### Nuevo Flujo:

```
1. Validar dataset → validate_arima_series()
2. Detectar estacionalidad → tiene_estacionalidad?
3. Si TIENE estacionalidad:
   ├─ seasonal=True en auto_arima
   ├─ Buscar SARIMA(p,d,q)(P,D,Q,m=12)
   └─ Guardar como modelo_type='SARIMA'
4. Si NO tiene estacionalidad:
   ├─ seasonal=False en auto_arima
   ├─ Buscar ARIMA(p,d,q)
   └─ Guardar como modelo_type='ARIMA'
5. Guardar metadatos con info de modelo
```

### Auto_arima con Estacionalidad (SARIMA):
```python
auto_model = auto_arima(
    series,
    # Componentes no-estacionales
    start_p=0, max_p=3,
    start_q=0, max_q=3,
    max_d=1,
    # Componentes estacionales (NUEVO)
    start_P=0, max_P=1,
    start_Q=0, max_Q=1,
    max_D=1,
    m=12,              # Período estacional
    seasonal=True,     # ← ACTIVADO si detecta estacionalidad
    stepwise=True,
    information_criterion='aic',
    ...
)
```

### Metadatos Guardados:
```json
{
    "model_type": "SARIMA",  // o "ARIMA"
    "order": [p, d, q],      // ARIMA/SARIMA
    "seasonal_order": [P, D, Q, m],  // SARIMA solamente
    "tiene_estacionalidad": true,
    "periodo_estacional": 12,
    "aic": 1234.56,
    "bic": 1245.67,
    "rmse": 0.1234,
    "mae": 0.0987,
    "longitud": 120
}
```

---

## 📊 Ejemplo de Flujo Completo

### Serie SIN Estacionalidad:
```
Input: Serie de 100 datos sin patrón cíclico
  ↓
Validación: longitud ✅, nulos ✅, outliers ✅
  ↓
Detección: fuerza_estacional = 0.08 (< 0.1)
  → tiene_estacionalidad = False
  ↓
Entrenamiento: ARIMA con seasonal=False
  ↓
Output: ARIMA(3,1,2)
  Metadatos: {
    "model_type": "ARIMA",
    "order": [3, 1, 2],
    "seasonal_order": null,
    "tiene_estacionalidad": false
  }
```

### Serie CON Estacionalidad:
```
Input: Series de 120 datos mensuales (picos en diciembre)
  ↓
Validación: longitud ✅, nulos ✅, outliers ✅
  ↓
Detección: fuerza_estacional = 0.35 (> 0.1)
  → tiene_estacionalidad = True
  → periodo_estacional = 12
  ↓
Entrenamiento: SARIMA con seasonal=True, m=12
  ↓
Output: SARIMA(2,1,1)(1,0,1,12)
  Metadatos: {
    "model_type": "SARIMA",
    "order": [2, 1, 1],
    "seasonal_order": [1, 0, 1, 12],
    "tiene_estacionalidad": true,
    "periodo_estacional": 12
  }
```

---

## 🔧 Cambios en Importaciones

**Antes**:
```python
from statsmodels.tsa.stattools import adfuller
```

**Ahora**:
```python
from statsmodels.tsa.seasonal import seasonal_decompose
```

---

## ✅ Verificación de Compatibilidad

| Archivo | Estado | Detalles |
|---------|--------|----------|
| `utils.py` | ✅ Actualizado | Función detect_seasonality() nueva, validate_stationarity() eliminada |
| `train.py` | ✅ Actualizado | Lógica SARIMA automática implementada |
| `predict.py` | ✅ Compatible | No requiere cambios, lee metadatos normalmente |
| `endpoints/crudml.py` | ✅ Compatible | Usa train_arima_model() sin cambios en interfaz |

---

## 📌 Notas Importantes

1. **Detección Automática**: El usuario NO especifica ARIMA o SARIMA. El sistema decide automáticamente.

2. **Período Estacional Fijo**: Actualmente se asume `m=12` (datos mensuales anuales). Para otros datos:
   - Datos semanales → `m=52`
   - Datos diarios → `m=365`
   - Datos trimestrales → `m=4`
   - Se puede configurar dinámicamente si es necesario

3. **Estacionariedad**: Ya NO se valida manualmente. Los parámetros `d` (ARIMA) y `D` (SARIMA) se ajustan automáticamente por auto_arima.

4. **Parámetros P,D,Q**: Para SARIMA, se usa rango pequeño (max_P=1, max_Q=1) por eficiencia computacional.

---

## 🧪 Prueba Rápida

```python
# Las series estacionarias/sin estacionalidad ahora se entrenan con ARIMA
validation = validate_arima_series(df)
print(validation['tiene_estacionalidad'])  # True o False

# El modelo se entrena automáticamente
resultado = train_arima_model(df, "mi_modelo", user_id=1, dataset_id=1, model_path="./models/")
print(resultado['metadata']['model_type'])  # 'ARIMA' o 'SARIMA'
```

---

## ⚠️ Si Necesitas Cambiar el Período Estacional

En `train.py`, línea ~110, cambiar:
```python
m=periodo_estacional,  # Actualmente 12, cambiar según necesidad
```

O hacer dinámico basado en frecuencia detectada:
```python
# Detectar período automático según frecuencia
freq = pd.infer_freq(df.index)
periodo_map = {'M': 12, 'MS': 12, 'W': 52, 'D': 365, 'Q': 4}
m = periodo_map.get(freq, 12)
```
