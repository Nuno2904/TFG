# MAE, RMSE y MAPE — Métricas de Error

Estas tres métricas se calculan sobre los **datos de entrenamiento** (ajuste in-sample) en ambos modelos (ARIMA/SARIMA y Prophet).

---

## 1. MAE — Error Absoluto Medio

**Significado:** "me equivoco X unidades de media."

### Fórmula

$$\text{MAE} = \frac{1}{n} \sum_{i=1}^{n} |y_i - \hat{y}_i|$$

| Símbolo | Significado |
|---------|-------------|
| $n$ | Número de observaciones |
| $y_i$ | Valor real en el instante $i$ |
| $\hat{y}_i$ | Valor predicho en el instante $i$ |

### Implementación manual (NumPy)
```python
mae = np.mean(np.abs(y_true - y_pred))
```

### ¿Viene en alguna librería integrada?
- **scikit-learn**: `sklearn.metrics.mean_absolute_error(y_true, y_pred)` ✅
- **statsmodels / pmdarima**: No expone MAE directamente. Se calcula manualmente sobre `fittedvalues`.
- **Prophet**: No expone MAE directamente. Se calcula sobre `predict(df)['yhat']`.

---

## 2. RMSE — Raíz del Error Cuadrático Medio

**Significado:** "como MAE pero penalizando más los errores grandes."

### Fórmula

$$\text{RMSE} = \sqrt{\frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2}$$

### Implementación manual (NumPy)
```python
rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
```

### ¿Viene en alguna librería integrada?
- **scikit-learn**: `sklearn.metrics.root_mean_squared_error(y_true, y_pred)` (≥1.4) o `np.sqrt(mean_squared_error(...))` ✅
- **statsmodels / pmdarima**: No expone RMSE directamente. Se calcula manualmente.
- **Prophet**: No expone RMSE directamente. Se calcula sobre `predict(df)['yhat']`.

---

## 3. MAPE — Error Porcentual Absoluto Medio

**Significado:** "me equivoco un X % de media respecto al valor real."

### Fórmula

$$\text{MAPE} = \frac{100}{n} \sum_{i=1}^{n} \left| \frac{y_i - \hat{y}_i}{y_i} \right|$$

> **Advertencia:** Si algún $y_i = 0$, se produce división por cero. En este proyecto se excluyen los puntos con valor real cero del cálculo:

```python
nonzero_mask = y_true != 0
mape = np.mean(np.abs((y_true[nonzero_mask] - y_pred[nonzero_mask])
                       / y_true[nonzero_mask])) * 100
# Si todos los valores son cero → mape = None
```

### ¿Viene en alguna librería integrada?
- **scikit-learn**: `sklearn.metrics.mean_absolute_percentage_error(y_true, y_pred)` ✅  
  Usa la misma lógica (aunque no multiplica por 100 — devuelve fracción, p.ej. 0.05 = 5 %).
- **statsmodels / pmdarima**: **No** incluye MAPE. Se calcula manualmente. ← **Esto es lo que se añadió en este proyecto.**
- **Prophet**: **No** incluye MAPE. Se calcula sobre `predict(df)['yhat']`. ← **También añadido.**

---

## Dónde se calcula en el código

### ARIMA/SARIMA — `app/ml/arima/train.py`

```python
predictions = fitted_model.fittedvalues          # valores ajustados in-sample
rmse = np.sqrt(np.mean((series - predictions) ** 2))
mae  = np.mean(np.abs(series - predictions))
nonzero_mask = series != 0
mape = float(np.mean(np.abs(
    (series[nonzero_mask] - predictions[nonzero_mask])
    / series[nonzero_mask]
)) * 100) if nonzero_mask.sum() > 0 else None
```

Las métricas se guardan en `{model_name}_metadata.json`:
```json
{
  "model_type": "ARIMA",
  "order": [p, d, q],
  "aic": 123.45,
  "bic": 130.21,
  "rmse": 4.56,
  "mae":  3.12,
  "mape": 7.89,
  "longitud": 240
}
```

### Prophet — `app/ml/prophet/train.py`

```python
train_forecast = model.predict(df)   # predicción in-sample sobre datos de entrenamiento
y_true = df['y'].values
y_pred = train_forecast['yhat'].values

mae  = float(np.mean(np.abs(y_true - y_pred)))
rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
nonzero_mask = y_true != 0
mape = float(np.mean(np.abs(
    (y_true[nonzero_mask] - y_pred[nonzero_mask])
    / y_true[nonzero_mask]
)) * 100) if nonzero_mask.sum() > 0 else None
```

Las métricas se guardan en `{model_name}_metadata.json`:
```json
{
  "model_type": "prophet",
  "longitud": 240,
  "mae":  5.30,
  "rmse": 7.11,
  "mape": 9.45
}
```

---

## Dónde se exponen al frontend

**Endpoint:** `GET /api/v1/predictions/models/{model_id}/info`

Devuelve el bloque `training_metrics` para **ambos** tipos de modelo:

```json
{
  "id": 42,
  "name": "mi_modelo",
  "model_type": "prophet",
  "status": "entrenado",
  "training_metrics": {
    "mae":  5.30,
    "rmse": 7.11,
    "mape": 9.45,
    "data_points": 240
  }
}
```

Para ARIMA/SARIMA se añaden también `order`, `seasonal_order`, `aic` y `bic`.

---

## Comparabilidad entre modelos

| Métrica | Prophet | ARIMA/SARIMA | ¿Comparables? |
|---------|---------|--------------|---------------|
| MAE     | ✅       | ✅            | ✅ Sí          |
| RMSE    | ✅       | ✅            | ✅ Sí          |
| MAPE    | ✅       | ✅            | ✅ Sí          |
| AIC/BIC | ❌       | ✅            | ❌ Solo ARIMA  |

MAE, RMSE y MAPE se calculan de forma idéntica en ambos modelos sobre los residuos de entrenamiento, por lo que son **directamente comparables** para elegir el mejor modelo sobre un mismo dataset.
