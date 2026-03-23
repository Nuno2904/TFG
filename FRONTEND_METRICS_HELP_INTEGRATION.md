# 🎓 Guía para Frontend: Integración de Ayuda Contextual de Métricas

**Para el equipo de frontend - Cómo consumir el endpoint `/metrics-help/`**

---

## 📍 Endpoint Nueva

```
GET /api/v1/metrics-help/{metric_name}

No requiere autenticación (Bearer token)
```

---

## 📊 Métricas Disponibles

```
rmse        → Root Mean Square Error
mae         → Mean Absolute Error  
aic         → Akaike Information Criterion
bic         → Bayesian Information Criterion
order       → ARIMA Order (p, d, q)
data_points → Número de puntos de entrenamiento
```

---

## 🔌 Estructura de Respuesta

```json
{
  "label": "Nombre legible de la métrica",
  "description": "Qué mide esta métrica",
  "interpretation": "Cómo interpretarla",
  "unit": "unidades originales",  // si aplica
  "benchmark": "< 10% = Excelente",  // si aplica
  "examples": [  // si aplica
    {
      "case": "Escenario ejemplo",
      "result": "Resultado esperado"
    }
  ],
  "vs_rmse": "Comparación con RMSE",  // si aplica
  "note": "Nota importante",  // si aplica
  "when_to_use": "Cuándo usar esta métrica",  // si aplica
  "components": { ... },  // si aplica (ej: order)
  "typical_range": "Rango típico"  // si aplica
}
```

---

## 💻 Cómo Usarlo

### Opción 1: Tooltip Simple (RECOMENDADO)

```javascript
// Al hacer hover sobre icono ℹ️
async function showMetricTooltip(metricName) {
  const response = await fetch(`/api/v1/metrics-help/${metricName}`);
  const help = await response.json();
  
  // Mostrar tooltip con:
  console.log(help.label);           // "RMSE (Root Mean Square Error)"
  console.log(help.description);     // "Error promedio del modelo..."
  console.log(help.interpretation);  // "Cuanto más bajo, mejor..."
  console.log(help.benchmark);       // "< 10%... = Excelente"
  
  // Construir tooltip HTML
  const tooltipHTML = `
    <div class="metric-tooltip">
      <h4>${help.label}</h4>
      <p>${help.description}</p>
      <p class="highlight">${help.interpretation}</p>
      ${help.benchmark ? `<p class="benchmark">${help.benchmark}</p>` : ''}
    </div>
  `;
  
  showTooltip(tooltipHTML);
}
```

**Uso en HTML:**
```html
<div class="metric-card">
  <span class="metric-label">RMSE</span>
  <span class="metric-value">2.45</span>
  <button class="info-icon" onclick="showMetricTooltip('rmse')">ℹ️</button>
</div>
```

---

### Opción 2: Panel Educativo

```javascript
// Cargar todas las métricas al iniciar
async function initMetricsPanel() {
  const metrics = ['rmse', 'mae', 'aic', 'bic', 'order', 'data_points'];
  const helpData = {};
  
  for (const metric of metrics) {
    const response = await fetch(`/api/v1/metrics-help/${metric}`);
    helpData[metric] = await response.json();
  }
  
  renderMetricsPanel(helpData);
}

function renderMetricsPanel(helpData) {
  const html = Object.entries(helpData).map(([key, help]) => `
    <div class="metric-explanation">
      <h3>${help.label}</h3>
      <p><strong>Qué es:</strong> ${help.description}</p>
      <p><strong>Cómo lo usas:</strong> ${help.interpretation}</p>
      ${help.benchmark ? `<p><strong>Referencia:</strong> ${help.benchmark}</p>` : ''}
      ${help.examples ? `
        <div class="examples">
          ${help.examples.map(ex => `
            <p><code>${ex.case}</code> → ${ex.result}</p>
          `).join('')}
        </div>
      ` : ''}
    </div>
  `).join('');
  
  document.getElementById('metrics-panel').innerHTML = html;
}
```

---

### Opción 3: Hook React (RECOMENDADO PARA REACT)

```javascript
// hooks/useMetricHelp.ts
import { useState, useEffect } from 'react';

export interface MetricHelp {
  label: string;
  description: string;
  interpretation: string;
  unit?: string;
  benchmark?: string;
  examples?: Array<{ case: string; result: string }>;
  [key: string]: any;
}

export function useMetricHelp(metricName: string) {
  const [help, setHelp] = useState<MetricHelp | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    (async () => {
      try {
        const response = await fetch(
          `/api/v1/metrics-help/${metricName.toLowerCase()}`
        );
        
        if (!response.ok) {
          throw new Error(`Métrica no encontrada: ${metricName}`);
        }
        
        const data = await response.json();
        setHelp(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error desconocido');
      } finally {
        setLoading(false);
      }
    })();
  }, [metricName]);
  
  return { help, loading, error };
}
```

**Uso en componente React:**

```jsx
import { useMetricHelp } from '@/hooks/useMetricHelp';

function MetricCard({ name, value }) {
  const { help, loading } = useMetricHelp(name);
  const [showTooltip, setShowTooltip] = useState(false);
  
  if (loading) return <div>Cargando...</div>;
  
  return (
    <div className="metric-card">
      <div className="metric-header">
        <span className="label">{help?.label}</span>
        <button 
          className="info-btn"
          onMouseEnter={() => setShowTooltip(true)}
          onMouseLeave={() => setShowTooltip(false)}
        >
          ℹ️
        </button>
      </div>
      
      <div className="metric-value">{value}</div>
      
      <p className="metric-unit">{help?.unit}</p>
      
      {showTooltip && (
        <div className="tooltip">
          <p>{help?.description}</p>
          <p className="highlight">{help?.interpretation}</p>
          {help?.benchmark && <p className="bench">{help?.benchmark}</p>}
        </div>
      )}
    </div>
  );
}
```

---

### Opción 4: Vue 3 Composable

```javascript
// composables/useMetricHelp.js
import { ref, onMounted } from 'vue';

export function useMetricHelp(metricName) {
  const help = ref(null);
  const loading = ref(true);
  
  onMounted(async () => {
    const response = await fetch(`/api/v1/metrics-help/${metricName}`);
    help.value = await response.json();
    loading.value = false;
  });
  
  return { help, loading };
}
```

**Uso en template Vue:**

```vue
<template>
  <div class="metric-card">
    <span class="label">{{ help.label }}</span>
    <span class="value">{{ metricValue }}</span>
    
    <button @mouseenter="showTooltip = true" @mouseleave="showTooltip = false">
      ℹ️
    </button>
    
    <div v-if="showTooltip" class="tooltip">
      <p>{{ help.description }}</p>
      <p class="highlight">{{ help.interpretation }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useMetricHelp } from '@/composables/useMetricHelp';

const { help, loading } = useMetricHelp('rmse');
const showTooltip = ref(false);
const metricValue = 2.45;
</script>
```

---

## 🎨 Ejemplo de Información por Métrica

### RMSE

```
GET /api/v1/metrics-help/rmse

{
  "label": "RMSE (Root Mean Square Error)",
  "description": "Error promedio del modelo en unidades originales",
  "interpretation": "Cuanto más bajo, mejor. Penaliza errores grandes.",
  "unit": "unidades originales",
  "benchmark": "< 10% del promedio de tus datos = ✅ Excelente",
  "examples": [
    {
      "case": "Promedio=300, RMSE=25",
      "result": "8.3% → ✅ Excelente"
    },
    {
      "case": "Promedio=300, RMSE=60",
      "result": "20% → ⚠️ Aceptable"
    },
    {
      "case": "Promedio=300, RMSE=100",
      "result": "33% → ❌ Necesita mejora"
    }
  ]
}
```

### AIC

```
GET /api/v1/metrics-help/aic

{
  "label": "AIC (Akaike Information Criterion)",
  "description": "Métrica que balancea precisión vs complejidad del modelo",
  "interpretation": "Solo comparar entre modelos ARIMA. Valor más bajo es mejor.",
  "note": "Número absoluto no tiene significado. Solo importa la comparación.",
  "when_to_use": "Comparar 2+ modelos ARIMA."
}
```

### ORDER (ARIMA)

```
GET /api/v1/metrics-help/order

{
  "label": "ARIMA Order (p, d, q)",
  "description": "Parámetros técnicos del modelo ARIMA",
  "interpretation": "These are automatically selected. p=pasado, d=diferenciaciones, q=media móvil",
  "components": {
    "p": "Términos autorregresivos (dependencia del pasado)",
    "d": "Diferenciaciones (para hacer la serie estacionaria)",
    "q": "Términos de media móvil (ruido pasado)"
  },
  "typical_range": "Valores entre 0-2 para cada parámetro son normales",
  "note": "El modelo selecciona automáticamente estos valores."
}
```

---

## 🛡️ Manejo de Errores

```javascript
async function getMetricHelp(metricName) {
  try {
    const response = await fetch(`/api/v1/metrics-help/${metricName}`);
    
    if (!response.ok) {
      if (response.status === 404) {
        console.error(`Métrica '${metricName}' no existe`);
        return null;
      }
      throw new Error(`HTTP ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error cargando ayuda de métrica:', error);
    return null;
  }
}
```

---

## 📱 CSS Recomendado

```css
.metric-card {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  background: #f9f9f9;
}

.metric-card .label {
  font-weight: 600;
  color: #333;
}

.metric-card .value {
  font-size: 1.2em;
  font-weight: bold;
  color: #0066cc;
}

.info-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2em;
  padding: 0;
  margin-left: auto;
}

.info-btn:hover {
  transform: scale(1.2);
}

.tooltip {
  position: absolute;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 12px;
  max-width: 300px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  z-index: 1000;
  margin-top: 8px;
}

.tooltip p {
  margin: 8px 0;
  font-size: 0.9em;
  line-height: 1.4;
}

.tooltip .highlight {
  color: #0066cc;
  font-weight: 600;
}

.tooltip .bench {
  color: #27ae60;
  font-weight: 600;
}
```

---

## ✅ Checklist para Implementar

- [ ] Llamadas al endpoint `/api/v1/metrics-help/{metric}`
- [ ] Tooltips al pasar mouse sobre ℹ️
- [ ] Indicadores visuales (colores verde/amarillo/rojo)
- [ ] Mostrar `help.benchmark` o indicador de calidad
- [ ] Manejo de errores (métrica no encontrada)
- [ ] Cache las respuestas para no llamar múltiples veces
- [ ] Responsive design en móvil

---

## 🔗 Referencia Rápida

| Métrica | Usa | Para Qué |
|---------|-----|---------|
| **RMSE** | Siempre | Medir error en unidades reales |
| **MAE** | Siempre | Error más estable que RMSE |
| **AIC** | Comparación | Elegir mejor modelo ARIMA |
| **BIC** | Comparación | Elegir modelo ARIMA (conservador) |
| **Order** | Referencia | Entender parámetros del modelo |
| **Data Points** | Referencia | Verificar suficiencia de datos |

---

## 📞 Soporte

Si necesitas más información sobre cómo integrar esto, revisa:
- `API_DOCUMENTATION.md` - Sección "Referencia de Métricas"
- `GUIA_AYUDA_CONTEXTUAL_METRICAS.md` - Guía completa de implementación
