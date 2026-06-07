# 📖 Backend API - Documentación Completa

**Versión:** 1.0.0  
**Framework:** FastAPI  
**Autenticación:** JWT (Bearer Token)  
**Documentación Interactiva:** `/docs` (Swagger UI)  

---

## 📋 Tabla de Contenidos

1. [Descripción General](#-descripción-general)
2. [Configuración Base](#-configuración-base)
3. [Autenticación y Seguridad](#-autenticación-y-seguridad)
4. [Endpoints Detallados](#-endpoints-detallados)
5. [Modelos de Datos](#-modelos-de-datos)

---

## Endpoint: Ayuda Contextual para Frontend

### Obtener Explicación de una Métrica

**Endpoint:** GET /metrics-help/{metric_name}

**Descripción:** El frontend usa este endpoint para mostrar explicaciones, benchmarks y ejemplos sobre cada métrica sin duplicar información. No requiere autenticación.

**Headers:**
`\`
(ninguno requerido)
`\`

**Path Parameters:**
`\`
metric_name = rmse, mae, aic, bic, order, data_points
`\`

**Response (200 OK):**
`\`json
{
  "label": "RMSE (Root Mean Square Error)",
  "description": "Error promedio del modelo en unidades originales",
  "interpretation": "Cuanto más bajo, mejor. Penaliza errores grandes.",
  "unit": "unidades originales",
  "benchmark": "< 10% del promedio de tus datos = Excelente",
  "examples": [
    {
      "case": "Promedio=300, RMSE=25",
      "result": "8.3% → Excelente"
    }
  ]
}
`\`

---

### Cómo usarlo desde el Frontend

#### **Opción 1: Tooltip al pasar el mouse**

`\`javascript
async function showMetricHelp(metricName) {
  const response = await fetch(\/api/v1/metrics-help/\\);
  const help = await response.json();
  // Mostrar tooltip
}
`\`

#### **Opción 2: Panel educativo**

`\`javascript
async function loadMetricsExplanations() {
  const metrics = ['rmse', 'mae', 'aic', 'bic', 'order', 'data_points'];
  const explanations = {};
  for (const metric of metrics) {
    const response = await fetch(\/api/v1/metrics-help/\\);
    explanations[metric] = await response.json();
  }
  return explanations;
}
`\`

#### **Opción 3: Hook React**

`\`javascript
import { useState, useEffect } from 'react';

export function useMetricExplanation(metricName) {
  const [help, setHelp] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetch(\/api/v1/metrics-help/\\)
      .then(r => r.json())
      .then(data => {
        setHelp(data);
        setLoading(false);
      });
  }, [metricName]);
  
  return { help, loading };
}
`\`

7. [Ejemplos de Integración](#-ejemplos-de-integración)
8. [Códigos de Error](#-códigos-de-error)

---

## 🎯 Descripción General

### ¿Qué es este Backend?

Este es un backend FastAPI diseñado para gestionar:
- **Autenticación de usuarios** mediante JWT tokens
- **Gestión de datasets** (archivos CSV/XLSX con series temporales)
- **Modelos de Machine Learning** (Prophet y ARIMA)
- **Predicciones** con modelos entrenados

### Arquitectura General

```
┌─────────────────────────────────────────────────┐
│              Frontend (React/Vue/etc)            │
└────────────────────┬────────────────────────────┘
                     │ HTTP Requests
                     ▼
┌─────────────────────────────────────────────────┐
│           FastAPI Backend (Python)              │
│  • Authentication (JWT)                         │
│  • File Upload & Processing                     │
│  • ML Model Training (Prophet/ARIMA)            │
│  • Predictions                                  │
└────────────────────┬────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
   SQLite Database        Storage (Models)
     (usuarios)           (storage/models/)
     (datasets)
     (data)
     (ml_models)
```

---

## ⚙️ Configuración Base

### URL Base de la API

```
http://localhost:8000/api/v1
```

### Headers Obligatorios (en todos los endpoints)

Excepto en `/auth/register` y `/auth/login`:

```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

### Respuesta Estándar

Todas las respuestas vienen en JSON con la siguiente estructura:

**Éxito (200-201):**
```json
{
  "id": 1,
  "email": "user@example.com",
  // ... otros campos
}
```

**Error (400-500):**
```json
{
  "detail": "Descripción del error"
}
```

---

## 🔐 Autenticación y Seguridad

### Flujo de Autenticación

```
1. Usuario se registra → POST /auth/register
2. Usuario hace login → POST /auth/login → Recibe JWT token
3. Usuario usa token en header → Authorization: Bearer {token}
4. Token válido por 30 minutos (configurable)
5. Token expira → Usuario debe login de nuevo
```

### Token JWT

- **Formato:** `Bearer eyJhbGc...` (después de /login)
- **Duración:** 30 minutos
- **Incluye:** user_id y user_type
- **Renovación:** Login nuevamente para obtener nuevo token

### Password Requirements

- Mínimo 8 caracteres
- Se almacena hasheado con bcrypt (irreversible)
- Nunca se envía en respuestas API

---

## 📡 Endpoints Detallados

### 🔓 AUTENTICACIÓN

#### 1. Registro de Usuario
**Endpoint:** `POST /auth/register`

**Descripción:** Crea una nueva cuenta de usuario

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "usuario@example.com",
  "password": "MiPassword123",
  "username": "usuario_username"
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user_id": 1,
  "email": "usuario@example.com"
}
```

**Posibles Errores:**
```json
{
  "detail": "Email already registered"
}
```
```json
{
  "detail": "Username already taken"
}
```

---

#### 2. Login de Usuario
**Endpoint:** `POST /auth/login`

**Descripción:** Autentica usuario y devuelve JWT token

**Headers:**
```
Content-Type: application/x-www-form-urlencoded
```

**Request Body (Form Data):**
```
username = usuario@example.com
password = MiPassword123
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Uso del Token:**
```
Header en próximas requests:
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Posibles Errores:**
```json
{
  "detail": "Invalid email or password"
}
```

---

### 👤 USUARIOS

#### 3. Obtener Perfil Actual
**Endpoint:** `GET /usuarios/me`

**Descripción:** Obtiene el perfil del usuario autenticado

**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "usuario@example.com",
  "tipo": "usuario",
  "created_at": "2024-03-23T10:15:30.123456"
}
```

---

#### 4. Obtener Usuario por Email
**Endpoint:** `GET /usuarios/{email}`

**Descripción:** Obtiene información de un usuario específico (requiere autenticación)

**Headers:**
```
Authorization: Bearer {token}
```

**Path Parameters:**
```
email = otro@example.com
```

**Response (200 OK):**
```json
{
  "id": 2,
  "email": "otro@example.com",
  "tipo": "usuario",
  "created_at": "2024-03-20T14:30:00.000000"
}
```

**Posibles Errores:**
```json
{
  "detail": "User with email 'no_existe@example.com' not found"
}
```

---

#### 5. Actualizar Perfil
**Endpoint:** `PUT /usuarios/me`

**Descripción:** Actualiza información del usuario autenticado

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body (todos los campos son opcionales):**
```json
{
  "email": "nuevo_email@example.com",
  "password": "NuevaPassword123"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "nuevo_email@example.com",
  "tipo": "usuario",
  "created_at": "2024-03-23T10:15:30.123456"
}
```

---

### 📁 ARCHIVOS Y DATASETS

#### 6. Subir un Archivo (CSV/XLSX)
**Endpoint:** `POST /files/upload`

**Descripción:** Sube un archivo con datos de series temporales

**Headers:**
```
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

**Request Body:**
```
file = (archivo CSV o XLSX)
```

**Validaciones:**
- ✅ Tipos: `.csv` o `.xlsx`
- ✅ Tamaño máximo: 5MB
- ✅ Debe contener columna de fecha y columna numérica

**Formato del archivo esperado:**

Opción 1 - Con encabezado:
```
fecha,valor
2024-01-01,100.5
2024-01-02,105.3
2024-01-03,103.2
```

Opción 2 - Nombres personalizados:
```
date,sales
2024-01-01,1000
2024-01-02,1050
```

**Response (201 Created):**
```json
{
  "message": "Archivo subido correctamente",
  "dataset": {
    "id": 1,
    "user_id": 1,
    "name": "datos_ventas.csv"
  },
  "entries_count": 3,
  "data": [
    {
      "DS": "2024-01-01",
      "y": 100.5
    },
    {
      "DS": "2024-01-02",
      "y": 105.3
    },
    {
      "DS": "2024-01-03",
      "y": 103.2
    }
  ]
}
```

---

#### 7. Obtener mis Archivos
**Endpoint:** `GET /files/my-files`

**Descripción:** Lista todos los archivos subidos por el usuario

**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "user_id": 1,
  "total_files": 2,
  "data": [
    {
      "id": 1,
      "user_id": 1,
      "name": "datos_ventas.csv"
    },
    {
      "id": 2,
      "user_id": 1,
      "name": "datos_produccion.xlsx"
    }
  ]
}
```

---

#### 8. Obtener Archivo por ID
**Endpoint:** `GET /files/{file_id}`

**Descripción:** Obtiene un archivo específico con todos sus datos

**Headers:**
```
Authorization: Bearer {token}
```

**Path Parameters:**
```
file_id = 1
```

**Response (200 OK):**
```json
{
  "dataset_id": 1,
  "user_id": 1,
  "name": "datos_ventas.csv",
  "total_entries": 3,
  "data_entries": [
    {
      "id": 1,
      "dataset_id": 1,
      "DS": "2024-01-01",
      "y": 100.5
    },
    {
      "id": 2,
      "dataset_id": 1,
      "DS": "2024-01-02",
      "y": 105.3
    },
    {
      "id": 3,
      "dataset_id": 1,
      "DS": "2024-01-03",
      "y": 103.2
    }
  ]
}
```

---

#### 9. Eliminar un Archivo
**Endpoint:** `DELETE /files/{file_id}`

**Descripción:** Elimina un archivo y todos sus datos asociados

**Headers:**
```
Authorization: Bearer {token}
```

**Path Parameters:**
```
file_id = 1
```

**Response (200 OK):**
```json
{
  "message": "Archivo eliminado correctamente",
  "file_id": 1
}
```

**Posibles Errores:**
```json
{
  "detail": "File not found"
}
```

---

#### 10. Obtener todos los Datasets
**Endpoint:** `GET /datasets`

**Descripción:** Lista todos los datasets del usuario autenticado

**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "user_id": 1,
  "total_datasets": 2,
  "datasets": [
    {
      "id": 1,
      "name": "datos_ventas.csv"
    },
    {
      "id": 2,
      "name": "datos_produccion.xlsx"
    }
  ]
}
```

---

#### 11. Obtener Datos de un Dataset (por ID)
**Endpoint:** `GET /datasets/id/{dataset_id}/data`

**Descripción:** Obtiene todos los puntos de datos de un dataset

**Headers:**
```
Authorization: Bearer {token}
```

**Path Parameters:**
```
dataset_id = 1
```

**Response (200 OK):**
```json
{
  "dataset_id": 1,
  "total_points": 3,
  "data": [
    {
      "DS": "2024-01-01",
      "y": 100.5
    },
    {
      "DS": "2024-01-02",
      "y": 105.3
    },
    {
      "DS": "2024-01-03",
      "y": 103.2
    }
  ]
}
```

---

#### 12. Obtener Datos de un Dataset (por Nombre)
**Endpoint:** `GET /datasets/{dataset_name}/data`

**Descripción:** Obtiene datos usando el nombre del dataset

**Headers:**
```
Authorization: Bearer {token}
```

**Path Parameters:**
```
dataset_name = datos_ventas.csv
```

**Response (200 OK):**
```json
{
  "dataset_name": "datos_ventas.csv",
  "total_points": 3,
  "data": [
    {
      "DS": "2024-01-01",
      "y": 100.5
    },
    {
      "DS": "2024-01-02",
      "y": 105.3
    },
    {
      "DS": "2024-01-03",
      "y": 103.2
    }
  ]
}
```

---

### 🤖 MODELOS DE MACHINE LEARNING

#### 13. Crear y Entrenar un Modelo
**Endpoint:** `POST /models`

**Descripción:** Crea un nuevo modelo ML y comienza el entrenamiento automáticamente en background

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "mi_modelo_prophet",
  "dataset_id": 1,
  "model_type": "prophet"
}
```

**Valores válidos para `model_type`:**
- `"prophet"` - Facebook Prophet (ideal para series temporales con estacionalidad)
- `"arima"` - ARIMA (ideal para series temporales simples)

**Response (201 Created):**
```json
{
  "id": 1,
  "user_id": 1,
  "dataset_id": 1,
  "name": "mi_modelo_prophet",
  "model_type": "prophet",
  "created_at": "2024-03-23T15:30:00.123456",
  "model_path": "storage/models/user_1/dataset_1/mi_modelo_prophet",
  "status": "en_entrenamiento",
  "error_message": null
}
```

**⚠️ Nota Importante sobre el entrenamiento:**
- El modelo se devuelve **inmediatamente** con estado `"en_entrenamiento"`
- El entrenamiento ocurre en **background** (no bloquea la API)
- Después de ~30 segundos el estado cambia a `"entrenado"` o `"error"`
- **Consulta el estado** con el endpoint GET `/models/{model_id}` para verificar

**Posibles Errores:**
```json
{
  "detail": "Dataset 999 not found"
}
```
```json
{
  "detail": "You already have a model named 'mi_modelo_prophet'. Model names must be unique per user."
}
```

---

#### 14. Obtener todos los Modelos del Usuario
**Endpoint:** `GET /models`

**Descripción:** Lista todos los modelos ML creados por el usuario

**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "dataset_id": 1,
    "name": "mi_modelo_prophet",
    "model_type": "prophet",
    "created_at": "2024-03-23T15:30:00.123456",
    "model_path": "storage/models/user_1/dataset_1/mi_modelo_prophet",
    "status": "entrenado",
    "error_message": null
  },
  {
    "id": 2,
    "user_id": 1,
    "dataset_id": 1,
    "name": "mi_modelo_arima",
    "model_type": "arima",
    "created_at": "2024-03-23T16:00:00.123456",
    "model_path": "storage/models/user_1/dataset_1/mi_modelo_arima",
    "status": "en_entrenamiento",
    "error_message": null
  }
]
```

---

#### 15. Obtener Modelos de un Dataset
**Endpoint:** `GET /models/dataset/{dataset_id}`

**Descripción:** Obtiene todos los modelos entrenados con un dataset específico

**Headers:**
```
Authorization: Bearer {token}
```

**Path Parameters:**
```
dataset_id = 1
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "dataset_id": 1,
    "name": "mi_modelo_prophet",
    "model_type": "prophet",
    "created_at": "2024-03-23T15:30:00.123456",
    "model_path": "storage/models/user_1/dataset_1/mi_modelo_prophet",
    "status": "entrenado",
    "error_message": null
  }
]
```

---

#### 16. Obtener Detalles de un Modelo
**Endpoint:** `GET /models/{model_id}`

**Descripción:** Obtiene información detallada de un modelo específico

**Headers:**
```
Authorization: Bearer {token}
```

**Path Parameters:**
```
model_id = 1
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": 1,
  "dataset_id": 1,
  "name": "mi_modelo_prophet",
  "model_type": "prophet",
  "created_at": "2024-03-23T15:30:00.123456",
  "model_path": "storage/models/user_1/dataset_1/mi_modelo_prophet",
  "status": "entrenado",
  "error_message": null,
  "usuario": {
    "id": 1,
    "email": "usuario@example.com"
  },
  "dataset": {
    "id": 1,
    "name": "datos_ventas.csv"
  }
}
```

---

#### 17. Obtener Información del Modelo (Status Checker)
**Endpoint:** `GET /predictions/models/{model_id}/info`

**Descripción:** Verifica el estado actual del modelo (útil después de crear)

**Headers:**
```
Authorization: Bearer {token}
```

**Path Parameters:**
```
model_id = 1
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "mi_modelo_prophet",
  "path": "storage/models/user_1/dataset_1/mi_modelo_prophet",
  "status": "entrenado",
  "dataset_id": 1,
  "created_at": "2024-03-23T15:30:00.123456",
  "error_message": null
}
```

**⚠️ Estados posibles:**
- `"en_entrenamiento"` - Modelo siendo entrenado (espera un poco)
- `"entrenado"` - Listo para hacer predicciones
- `"error"` - Falló el entrenamiento, ver `error_message`

---

### 🔮 PREDICCIONES

#### 18. Hacer Predicción con Prophet
**Endpoint:** `POST /predictions/predict`

**Descripción:** Realiza predicciones con un modelo Prophet entrenado

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "model_id": 1,
  "periods": 30
}
```

**Parámetros:**
- `model_id` (required): ID del modelo entrenado
- `periods` (default: 30): Número de periodos a predecir (1-365)

**Response (200 OK):**
```json
{
  "model_id": 1,
  "model_name": "mi_modelo_prophet",
  "model_path": "storage/models/user_1/dataset_1/mi_modelo_prophet",
  "dataset_id": 1,
  "periods": 30,
  "forecast": [
    {
      "ds": "2024-01-04",
      "yhat": 102.5,
      "yhat_lower": 98.3,
      "yhat_upper": 106.7
    },
    {
      "ds": "2024-01-05",
      "yhat": 104.1,
      "yhat_lower": 99.2,
      "yhat_upper": 108.9
    },
    {
      "ds": "2024-01-06",
      "yhat": 103.8,
      "yhat_lower": 98.9,
      "yhat_upper": 108.6
    },
    // ... más predicciones ...
  ],
  "created_at": "2024-03-23T16:15:00.123456"
}
```

**Interpretación de resultados:**
- `ds`: Fecha de la predicción
- `yhat`: Valor predicho (medio)
- `yhat_lower`: Límite inferior del intervalo de confianza (95%)
- `yhat_upper`: Límite superior del intervalo de confianza (95%)

**Posibles Errores:**
```json
{
  "detail": "Model not found or does not belong to current user"
}
```
```json
{
  "detail": "Model is not trained. Current status: en_entrenamiento"
}
```

---

### 🏥 HEALTH CHECK

#### 19. Health Check
**Endpoint:** `GET /health`

**Descripción:** Verifica si la API está funcionando

**Headers:**
```
(ninguno requerido)
```

**Response (200 OK):**
```json
{
  "status": "✅ healthy",
  "app": "TFG API",
  "version": "1.0.0"
}
```

---

### 📖 INFO

#### 20. Información de la API
**Endpoint:** `GET /`

**Descripción:** Obtiene información general y links de documentación

**Headers:**
```
(ninguno requerido)
```

**Response (200 OK):**
```json
{
  "message": "👋 Welcome to TFG API",
  "version": "1.0.0",
  "docs": {
    "swagger": "/docs",
    "redoc": "/redoc",
    "openapi": "/openapi.json"
  }
}
```

---

## 📊 Modelos de Datos

### Usuario (Usuario)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | ID único del usuario |
| `email` | String | Email (único) |
| `password` | String (hasheado) | Contraseña hasheada |
| `tipo` | String | "usuario" o "admin" |
| `created_at` | DateTime | Fecha de creación |

### Dataset (Dataset)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | ID único del dataset |
| `user_id` | Integer | FK al usuario propietario |
| `name` | String | Nombre del archivo |

### Data Entry (Data)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | ID único del registro |
| `dataset_id` | Integer | FK al dataset |
| `DS` | String (YYYY-MM-DD) | Fecha (timestamp) |
| `y` | Float | Valor numérico |

### ML Model (MLModel)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | ID único del modelo |
| `user_id` | Integer | FK al usuario |
| `dataset_id` | Integer | FK al dataset de entrenamiento |
| `name` | String | Nombre del modelo |
| `model_type` | String | "prophet" o "arima" |
| `model_path` | String | Ruta del archivo del modelo |
| `status` | String | "entrenado", "en_entrenamiento", "error" |
| `error_message` | String (nullable) | Detalle del error si falló |
| `created_at` | DateTime | Fecha de creación |

---

## � Referencia de Métricas

### ¿Por qué son importantes las métricas?

Las métricas de evaluación te ayudan a:
- ✅ **Medir la precisión** del modelo entrenado
- ✅ **Comparar diferentes modelos** para elegir el mejor
- ✅ **Entender si el modelo es confiable** para hacer predicciones
- ✅ **Detectar problemas** en el entrenamiento

---

### 📈 Métricas de ARIMA

Cuando entrenas un modelo **ARIMA**, obtendrás estas métricas en la respuesta:

#### **Order (p, d, q)**
```
"order": [1, 1, 1]
```
**¿Qué es?** Tres números que definen la estructura ARIMA:
- **p**: Número de términos autorregresivos (autocorrelación pasada)
- **d**: Número de diferenciaciones (para hacer la serie estacionaria)
- **q**: Número de términos de media móvil (ruido pasado)

**Interpreta como:** Números técnicos que el modelo selecciona automáticamente. Valores típicos están entre 0-2 para cada parámetro.

---

#### **RMSE (Root Mean Square Error)** ⭐
```
"rmse": 2.45
```
**¿Qué mide?** El error promedio del modelo en unidades originales de tus datos.

**Cómo interpretarlo:**
- **Valor más bajo = mejor** (modelo más preciso)
- Si tus ventas varían entre 100-200, un RMSE de 5 es excelente
- Si tus ventas varían entre 100-200, un RMSE de 50 es malo
- **Regla de oro**: RMSE < 10% del promedio de tus datos = ✅ Bueno

**Ejemplo:**
- Promedio de datos: 500
- RMSE: 25
- Interpretación: En promedio, las predicciones se desvían ~25 unidades (5% de error) ✅

---

#### **MAE (Mean Absolute Error)** ⭐
```
"mae": 1.89
```
**¿Qué mide?** Error promedio en valor absoluto (sin considerar si es por arriba o abajo).

**Cómo interpretarlo:**
- **Valor más bajo = mejor** (modelo más preciso)
- **Es más fácil de entender que RMSE** porque está en unidades reales
- Penaliza todos los errores por igual
- Si MAE = 10, significa que en promedio el modelo se equivoca ±10 unidades

**Comparación RMSE vs MAE:**
- RMSE penaliza más los errores grandes (más sensible a outliers)
- MAE es más estable y fácil de interpretar

**Ejemplo:**
- MAE: 15
- Interpretación: En promedio, las predicciones se desvían ±15 unidades

---

#### **AIC (Akaike Information Criterion)**
```
"aic": 245.3
```
**¿Qué es?** Una puntuación que balancean:
- Lo bien que el modelo ajusta los datos
- La complejidad del modelo (penaliza modelos muy complejos)

**Cómo interpretarlo:**
- **El valor AIC más bajo es mejor** (comparando entre modelos ARIMA)
- **Solo sirve para comparar modelos ARIMA** (no comparar con Prophet)
- Número absoluto no tiene significado, solo importa la comparación

**Ejemplo:**
- Modelo A: AIC = 240
- Modelo B: AIC = 250
- Conclusión: Modelo A es mejor ✅

---

#### **BIC (Bayesian Information Criterion)**
```
"bic": 255.7
```
**¿Qué es?** Similar a AIC, pero penaliza más la complejidad (favorece modelos simples).

**Cómo interpretarlo:**
- **El valor BIC más bajo es mejor** (comparando entre modelos ARIMA)
- Más conservador que AIC (elige modelos más simples)
- Solo sirve para comparar modelos ARIMA

**Regla de oro:** 
- BIC > AIC siempre en los mismos datos
- Si AIC y BIC coinciden en el mejor modelo → muy confiable

---

#### **Data Points (Longitud del dataset)**
```
"data_points": 365
```
**¿Qué es?** Cantidad de registros usados para entrenar el modelo.

**Cómo interpretarlo:**
- **Más datos = modelos más confiables**
- Mínimo recomendado: 50-100 puntos
- Ideal: 200+ puntos
- ARIMA necesita menos datos que otros modelos (puede funcionar con 30-50 puntos)

**Ejemplo:**
- 365 puntos (un año de datos diarios) ✅ Excelente
- 52 puntos (un año de datos semanales) ✅ Aceptable
- 12 puntos (un año de datos mensuales) ⚠️ Muy poco

---

### 📊 Métricas de Prophet

**Nota:** Prophet no retorna explícitamente métricas en el endpoint de predicción, pero usa internamente:
- **MAPE (Mean Absolute Percentage Error)**: Error porcentual
- **Intervalos de confianza**: Las predicciones incluyen límites inferior/superior

**En la respuesta de predicción ves:**
```json
{
  "ds": "2024-01-04",
  "yhat": 102.5,           // Predicción
  "yhat_lower": 98.3,      // Límite inferior (95% confianza)
  "yhat_upper": 106.7      // Límite superior (95% confianza)
}
```

**Cómo interpretarlo:**
- **yhat**: Mejor estimación del modelo
- **Intervalo**: El modelo está 95% seguro que el valor real caerá entre lower y upper
- **Intervalo muy ancho**: Modelo menos confiado (incertidumbre alta)
- **Intervalo muy estrecho**: Modelo muy confiado en su predicción

---

### 🎯 Guía Rápida de Decisión

| Situación | Acción |
|-----------|--------|
| ¿Es RMSE muy alto? | Dataset muy pequeño o serie muy ruidosa. Intenta recopilar más datos |
| ¿MAE y RMSE muy diferentes? | Hay valores extremos (outliers). Considera limpiar datos |
| ¿AIC/BIC muy altos? | El modelo no se ajusta bien. Intenta otro modelo (Prophet) |
| ¿Intervalos de confianza muy anchos? | Modelo inseguro. Necesitas más datos de entrenamiento |
| ¿Modelo A vs B: compara AIC/BIC? | El AIC/BIC más bajo gana |

---

### 📝 Checklist: Evalúa tu Modelo

- [ ] RMSE < 10% del promedio de datos
- [ ] MAE comparable a RMSE (no muy diferente)
- [ ] Data points >= 100
- [ ] AIC/BIC mínimo comparado con otros modelos
- [ ] Intervalos de confianza razonables (no extremadamente anchos)

Si cumples 4+ ✅ → **Tu modelo es confiable**

---

## �💡 Ejemplos de Integración

### Ejemplo 1: Flujo Completo desde Cero

```javascript
// 1. Registrarse
const registerRes = await fetch('http://localhost:8000/api/v1/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'usuario@gmail.com',
    password: 'Password123',
    username: 'mi_usuario'
  })
});

// 2. Login
const loginRes = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: 'username=usuario@gmail.com&password=Password123'
});
const { access_token } = await loginRes.json();

// 3. Subir archivo
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const uploadRes = await fetch('http://localhost:8000/api/v1/files/upload', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${access_token}` },
  body: formData
});
const uploadData = await uploadRes.json();
const dataset_id = uploadData.dataset.id;

// 4. Crear modelo
const modelRes = await fetch('http://localhost:8000/api/v1/models', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'mi_primer_modelo',
    dataset_id: dataset_id,
    model_type: 'prophet'
  })
});
const model = await modelRes.json();
const model_id = model.id;

// 5. Esperar a que se entrene (polling)
let trained = false;
while (!trained) {
  const checkRes = await fetch(
    `http://localhost:8000/api/v1/predictions/models/${model_id}/info`,
    { headers: { 'Authorization': `Bearer ${access_token}` } }
  );
  const { status } = await checkRes.json();
  
  if (status === 'entrenado') {
    trained = true;
  } else if (status === 'error') {
    console.error('Entrenamiento falló');
    break;
  } else {
    // Esperar 2 segundos antes de reintentar
    await new Promise(r => setTimeout(r, 2000));
  }
}

// 6. Hacer predicción
const predRes = await fetch('http://localhost:8000/api/v1/predictions/predict', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    model_id: model_id,
    periods: 30
  })
});
const predictions = await predRes.json();
console.log(predictions.forecast);
```

---

### Ejemplo 2: Usar TypeScript/Axios

```typescript
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

// Crear instancia de axios
const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' }
});

// Interceptor para agregar token automáticamente
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Login
async function login(email: string, password: string) {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);
  
  const res = await axios.post(`${API_BASE}/auth/login`, formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  });
  
  localStorage.setItem('access_token', res.data.access_token);
  return res.data;
}

// Obtener datasets
async function getDatasets() {
  const res = await api.get('/datasets');
  return res.data;
}

// Crear modelo
async function createModel(
  name: string,
  dataset_id: number,
  model_type: 'prophet' | 'arima'
) {
  const res = await api.post('/models', {
    name,
    dataset_id,
    model_type
  });
  return res.data;
}

// Hacer predicción
async function predict(model_id: number, periods: number = 30) {
  const res = await api.post('/predictions/predict', {
    model_id,
    periods
  });
  return res.data;
}

// Uso
await login('user@example.com', 'password123');
const datasets = await getDatasets();
const model = await createModel('mi_modelo', 1, 'prophet');
const predictions = await predict(model.id, 30);
```

---

### Ejemplo 3: React Hook para Login

```typescript
import { useState } from 'react';

function useAuth() {
  const [token, setToken] = useState<string | null>(
    localStorage.getItem('access_token')
  );
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = async (email: string, password: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);
      
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData.toString()
      });
      
      if (!res.ok) {
        throw new Error('Login failed');
      }
      
      const data = await res.json();
      setToken(data.access_token);
      localStorage.setItem('access_token', data.access_token);
      
      // Obtener datos del usuario
      const userRes = await fetch('/api/v1/usuarios/me', {
        headers: { 'Authorization': `Bearer ${data.access_token}` }
      });
      const userData = await userRes.json();
      setUser(userData);
      
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('access_token');
  };

  return { token, user, loading, error, login, logout };
}

export default useAuth;
```

---

## ⚠️ Códigos de Error

### 400 Bad Request
```json
{
  "detail": "Email already registered"
}
```
Causas:
- Email/username ya existe (registro)
- Datos inválidos en request
- Validación de formato fallida

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```
Causas:
- Token no incluido en header
- Token expirado
- Token inválido

### 403 Forbidden
```json
{
  "detail": "Invalid email or password"
}
```
Causas:
- Credenciales incorrectas
- Usuario intenta acceder a recurso de otro usuario

### 404 Not Found
```json
{
  "detail": "Model not found"
}
```
Causas:
- Recurso no existe
- ID inválido

### 500 Internal Server Error
```json
{
  "detail": "Error processing file: ..."
}
```
Causas:
- Error en el servidor
- Problema con el almacenamiento
- Fallo del entrenamiento del modelo

---

## 🔗 Links Importantes

**Documentación Interactiva (Swagger UI):**
```
http://localhost:8000/docs
```

**Documentación ReDoc:**
```
http://localhost:8000/redoc
```

**OpenAPI JSON:**
```
http://localhost:8000/openapi.json
```

---

## 📋 Checklist para el Equipo Frontend

**Antes de empezar a integrar:**

- [ ] Backend corriendo en `http://localhost:8000`
- [ ] Probar `/health` endpoint
- [ ] Probar flujo de registro y login
- [ ] Subir un archivo de prueba
- [ ] Crear un modelo de prueba
- [ ] Hacer una predicción de prueba
- [ ] Importar correctamente los tokens o usar interceptores
- [ ] Manejar estados de carga (`"en_entrenamiento"`)
- [ ] Mostrar mensajes de error adecuadamente
- [ ] Implementar logout (limpiar token)

---

## 📞 Soporte

En caso de dudas o problemas:

1. **Verificar el endpoint en `/docs`** - Documentación interactiva
2. **Revisar ejemplos de integración** - Sección de ejemplos
3. **Verificar códigos de error** - Sección de errores
4. **Consultar estructura de modelos** - Sección de modelos de datos

---

**Versión:** 1.0.0  
**Última actualización:** 23 de Marzo de 2024  
**Framework:** FastAPI 0.100+  
**Base de datos:** SQLite
