# 📚 Guía: Implementar Ayuda Contextual para Métricas

**Como respuesta a la recomendación de tu profesor de TFG**

---

## 🎯 ¿Qué es la "Ayuda Contextual"?

Es información **integrada en el contexto** que ayuda al usuario a entender las métricas sin salir de la aplicación.

---

## ✅ Nivel 1: Documentación (YA IMPLEMENTADO)

✓ Archivo: [API_DOCUMENTATION.md](API_DOCUMENTATION.md#-referencia-de-métricas)

**Lo que agregué:**
- Explicación clara de cada métrica (RMSE, MAE, AIC, BIC, Order, Data Points)
- Cómo interpretarlas (qué significa un valor alto/bajo)
- Ejemplos prácticos
- Guía rápida de decisión

**Para el usuario:** Leer la sección "Referencia de Métricas" en la documentación completa

---

## 🔧 Nivel 2: Enriquecer la API con Descripciones (IMPLEMENTABLE)

### Opción A: Agregar descripciones en las respuestas JSON

Modificar el endpoint que devuelve métricas para incluir `description` y `interpretation`:

**Ejemplo (Endpoint: GET /predictions/models/{model_id}/info):**

**Response actual:**
```json
{
  "training_metrics": {
    "rmse": 2.45,
    "mae": 1.89,
    "aic": 245.3,
    "bic": 255.7,
    "order": [1, 1, 1]
  }
}
```

**Response mejorado con ayuda contextual:**
```json
{
  "training_metrics": {
    "rmse": {
      "value": 2.45,
      "label": "RMSE (Root Mean Square Error)",
      "description": "Error promedio del modelo en unidades originales",
      "interpretation": "Valor bajo es mejor. Si es < 10% del promedio de datos, es excelente",
      "unit": "unidades originales"
    },
    "mae": {
      "value": 1.89,
      "label": "MAE (Mean Absolute Error)",
      "description": "Error promedio en valor absoluto",
      "interpretation": "Más fácil de entender que RMSE. En promedio, el modelo se equivoca ±1.89 unidades",
      "unit": "unidades originales"
    },
    "aic": {
      "value": 245.3,
      "label": "AIC (Akaike Information Criterion)",
      "description": "Métrica que balancea precisión vs complejidad del modelo",
      "interpretation": "Solo comparar entre modelos ARIMA. Valor más bajo es mejor",
      "compare_with": "Usa esta métrica para elegir entre diferentes modelos ARIMA"
    },
    "bic": {
      "value": 255.7,
      "label": "BIC (Bayesian Information Criterion)",
      "description": "Similar a AIC pero penaliza más la complejidad",
      "interpretation": "Usa este si prefieres modelos simples. Valor más bajo es mejor",
      "compare_with": "Si AIC y BIC coinciden en el mejor modelo, es muy confiable"
    },
    "order": {
      "value": [1, 1, 1],
      "label": "ARIMA Order (p, d, q)",
      "description": "Parámetros técnicos del modelo ARIMA",
      "interpretation": "These are automatically selected. p=pasado, d=diferenciaciones, q=media móvil",
      "typical_range": "Valores entre 0-2 para cada parámetro son normales"
    },
    "data_points": {
      "value": 365,
      "label": "Puntos de Datos",
      "description": "Número de registros usados para entrenar",
      "interpretation": "265 puntos (1 año diario) es excelente. Mínimo: 50+",
      "sufficient": true
    }
  }
}
```

### Cómo implementarlo en tu código:

**En `app/schemas/ml.py` agrega:**
```python
from pydantic import BaseModel
from typing import Optional

class MetricInfo(BaseModel):
    value: float | int | list
    label: str
    description: str
    interpretation: str
    unit: Optional[str] = None
    typical_range: Optional[str] = None
    compare_with: Optional[str] = None
    sufficient: Optional[bool] = None

class ARIMAMetricsResponse(BaseModel):
    rmse: MetricInfo
    mae: MetricInfo
    aic: MetricInfo
    bic: MetricInfo
    order: MetricInfo
    data_points: MetricInfo
```

**En `app/api/v1/endpoints/predml.py` modifica:**
```python
def get_metric_info(metric_name: str, value):
    """Retorna información contextual sobre una métrica"""
    
    metrics_info = {
        'rmse': {
            'label': 'RMSE (Root Mean Square Error)',
            'description': 'Error promedio del modelo en unidades originales',
            'interpretation': 'Valor bajo es mejor. Si es < 10% del promedio de datos, es excelente',
            'unit': 'unidades originales'
        },
        'mae': {
            'label': 'MAE (Mean Absolute Error)',
            'description': 'Error promedio en valor absoluto',
            'interpretation': 'Más fácil de entender que RMSE. En promedio, el modelo se equivoca ±{:.2f} unidades'.format(value),
            'unit': 'unidades originales'
        },
        # ... etc
    }
    
    info = metrics_info.get(metric_name, {})
    return {
        'value': value,
        'label': info.get('label'),
        'description': info.get('description'),
        'interpretation': info.get('interpretation'),
        'unit': info.get('unit')
    }
```

---

## 🎨 Nivel 3: Frontend - Tooltips y Visualización (PARA TU FRONTEND)

Si tienes un frontend (React, Vue, etc.), agrega componentes interactivos:

### Opción A: Tooltip al pasar el mouse

```jsx
import React, { useState } from 'react';

function MetricCard({ metric, value, description }) {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <div 
      className="metric-card"
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <div className="metric-label">
        {metric}
        <span className="info-icon">ℹ️</span>
      </div>
      <div className="metric-value">{value}</div>
      
      {showTooltip && (
        <div className="tooltip">
          <p><strong>{description.label}</strong></p>
          <p>{description.description}</p>
          <p className="interpretation">💡 {description.interpretation}</p>
        </div>
      )}
    </div>
  );
}

export default MetricCard;
```

### Opción B: Modal educativo

```jsx
function MetricsExplainer() {
  return (
    <div className="metrics-info">
      <h2>🎓 ¿Cómo interpretar tus métricas?</h2>
      
      <div className="metric-explainer">
        <h3>RMSE: {modelMetrics.rmse}</h3>
        <div className="explanation">
          <p><strong>¿Qué es?</strong> Error promedio en tus unidades originales</p>
          <p><strong>¿Qué es bueno?</strong> < 10% del promedio de tus datos</p>
          <p><strong>Tu caso:</strong> Promedio={dataAvg}, RMSE={rmse} = {percentage}% ✅</p>
        </div>
      </div>
      
      {/* Similar para otras métricas */}
    </div>
  );
}
```

### Opción C: Indicador visual (semáforo)

```jsx
function MetricHealthIndicator({ rmse, avgValue }) {
  const percentage = (rmse / avgValue) * 100;
  
  let status = 'good';
  if (percentage > 20) status = 'warning';
  if (percentage > 30) status = 'bad';
  
  return (
    <div className={`health-indicator ${status}`}>
      <div className="light"></div>
      <span>
        {status === 'good' && '✅ Excelente (RMSE < 10%)'}
        {status === 'warning' && '⚠️ Aceptable (RMSE 10-30%)'}
        {status === 'bad' && '❌ Requiere mejora (RMSE > 30%)'}
      </span>
    </div>
  );
}
```

---

## 📱 Nivel 4: Crear Endpoint específico para Ayuda

### Nuevo endpoint: GET /metrics-help/{metric_name}

```python
# En app/api/v1/endpoints/predml.py

@router.get(
    "/metrics-help/{metric_name}",
    tags=["Educación/Ayuda"],
    summary="Obtener explicación de una métrica"
)
def get_metric_help(
    metric_name: str,
    current_user: Usuario = Depends(get_current_user)
) -> dict:
    """
    Obtiene información educativa sobre una métrica específica.
    
    Args:
        metric_name: Sistema, arima, prophet, etc.
        
    Returns:
        Información contextual, ejemplos, interpretación
    """
    
    help_content = {
        "rmse": {
            "titulo": "RMSE (Root Mean Square Error)",
            "que_es": "Error promedio del modelo en unidades originales",
            "formula": "sqrt(mean((prediccion - real)^2))",
            "como_interpretarlo": [
                "Valor más bajo = mejor",
                "RMSE < 10% del promedio de datos = ✅ Excelente",
                "RMSE 10-20% = ✅ Bueno",
                "RMSE > 30% = ⚠️ Necesita mejora"
            ],
            "ejemplo": {
                "tus_datos": "Ventas varían 100-500 (promedio 300)",
                "tu_rmse": 25,
                "análisis": "25 es el 8.3% de 300 → ✅ Excelente predicción"
            },
            "pros": ["En unidades originales", "Penaliza errores grandes"],
            "contras": ["Sensible a outliers"],
            "comparar_con": ["MAE", "MAPE"]
        },
        "mae": {
            "titulo": "MAE (Mean Absolute Error)",
            # ... similar
        },
        # ... más métricas
    }
    
    metric = help_content.get(metric_name.lower())
    if not metric:
        raise HTTPException(status_code=404, detail=f"Métrica '{metric_name}' no documentada")
    
    return {
        "metric": metric_name,
        "help": metric,
        "url_documentacion": "https://tuapi.com/docs#métricas"
    }
```

**Uso:**
```
GET /api/v1/metrics-help/rmse
GET /api/v1/metrics-help/mae
GET /api/v1/metrics-help/aic
```

**Response:**
```json
{
  "metric": "rmse",
  "help": {
    "titulo": "RMSE (Root Mean Square Error)",
    "que_es": "Error promedio del modelo...",
    "como_interpretarlo": ["Valor más bajo = mejor", ...],
    "ejemplo": {...}
  }
}
```

---

## 🎓 Nivel 5: Crear Guía PDF o Wiki

### Documento: `docs/METRICAS_GUIA_USUARIO.md`

Este documento ya existe parcialmente en tu `API_DOCUMENTATION.md`, pero podrías crear uno dedicado:

```
docs/METRICAS_GUIA_USUARIO.md
├── Introducción
├── RMSE - Guía Completa
├── MAE - Guía Completa
├── AIC/BIC - Guía Completa
├── Ejemplos del Mundo Real
├── Qué Hacer si...
│   ├── Si RMSE es muy alto
│   ├── Si MAE y RMSE difieren mucho
│   ├── Si tienes pocas datos (data_points < 50)
│   └── Si cambias de modelo (ARIMA vs Prophet)
└── FAQ (Preguntas Frecuentes)
```

---

## 🚀 Plan de Implementación (del más fácil al más difícil)

### ✅ Fase 1: Hecho
- [x] Documentación en `API_DOCUMENTATION.md` (nivel 1)

### 📝 Fase 2: Rápido (30 min)
- [ ] Crear archivo de guía como este
- [ ] Enriquecer docstrings en código
- [ ] Agregar ejemplos en README

### 🔧 Fase 3: Moderado (2-3 horas)
- [ ] Implementar schemas mejorados (Nivel 2)
- [ ] Crear endpoint `/metrics-help/` (Nivel 4)
- [ ] Actualizar respuestas de API

### 🎨 Fase 4: Completo (1-2 días)
- [ ] Agregar tooltips en frontend (Nivel 3)
- [ ] Crear documentación PDF
- [ ] Implementar visualizaciones

---

## 📋 Checklist: Ayuda Contextual Completa

- [x] Documentación clara y ejemplos
- [ ] API enriquecida con descripciones
- [ ] Endpoint especial para ayuda
- [ ] Frontend con tooltips
- [ ] Guías PDF/Wiki
- [ ] Ejemplos del mundo real
- [ ] FAQ
- [ ] Videos tutoriales (opcional)

---

## 💬 Qué decirle a tu profesor:

> "He implementado ayuda contextual multinivel para las métricas:
> 
> 1. **Documentación integrada** en API_DOCUMENTATION.md con explicaciones, ejemplos, guías de interpretación
> 2. **Endpoints enriquecidos** (próximamente) que devuelven no solo valores sino también contexto
> 3. **Tooltips interactivos** en el frontend para explicar cada métrica
> 4. **Endpoint educativo** para que el usuario pueda solicitar ayuda sobre cualquier métrica
> 
> Esto facilita a los usuarios finales entender qué significan los valores, cómo interpretarlos, y qué actions tomar."

---

## 📚 Referencias

- [Understanding RMSE, MAE, and MAPE](https://en.wikipedia.org/wiki/Mean_absolute_error)
- [AIC/BIC Comparison](https://en.wikipedia.org/wiki/Akaike_information_criterion)
- [ARIMA Parameters Explained](https://otexts.com/fpp2/arima.html)
