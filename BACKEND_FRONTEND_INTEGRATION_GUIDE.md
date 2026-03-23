# 📚 Documentación Completa del Backend para Frontend

**Versión:** 1.0  
**Fecha:** Marzo 2026  
**Destinatario:** Equipo de Frontend  
**Objetivo:** Integración completa del backend para crear una **plataforma educativa de series temporales**

---

## 📖 Tabla de Contenidos

1. [Visión General del Proyecto](#-visión-general-del-proyecto)
2. [Estructura del Backend](#-estructura-del-backend)
3. [Autenticación y Seguridad](#-autenticación-y-seguridad)
4. [Configuración Base](#-configuración-base)
5. [Documentación de Endpoints](#-documentación-de-endpoints)
6. [Modelos de Datos](#-modelos-de-datos)
7. [Flujos de Uso Principales](#-flujos-de-uso-principales)
8. [Integración Frontend](#-integración-frontend)

---

## 🎯 Visión General del Proyecto

### Objetivo de la Aplicación

Crear una **plataforma educativa web** que permita a usuarios:

1. **Cargar datos** de series temporales (CSV/XLSX)
2. **Entrenar modelos** de Machine Learning (Prophet, ARIMA)
3. **Visualizar métricas** de evaluación con explicaciones didácticas
4. **Hacer predicciones** y entender cómo funcionan
5. **Comparar modelos** y elegir el mejor

### Público Objetivo

Estudiantes, investigadores y profesionales que quieren aprender:
- Cómo funcionan los modelos de series temporales
- Cómo interpretar métricas y predicciones
- La diferencia entre Prophet y ARIMA

### Valor Agregado: Ayuda Contextual

Cada métrica, parámetro y resultado incluye **explicación educativa**:
- ¿Qué significa?
- ¿Por qué importa?
- ¿Cómo lo interpretamos?

---

## 🏗️ Estructura del Backend

### Arquitectura General

```
Backend (FastAPI - Python)
│
├── 🔐 Authentication (JWT)
│   ├── Registro de usuarios
│   ├── Login/Login
│   ├── Token management
│   └── Validación de usuarios
│
├── 👤 User Management
│   ├── Perfil de usuario
│   ├── Actualizar credenciales
│   └── Seguridad (bcrypt)
│
├── 📁 File & Dataset Management
│   ├── Upload de archivos (CSV/XLSX)
│   ├── Parseo automático
│   ├── Almacenamiento en DB
│   └── Gestión de datasets
│
├── 🤖 Machine Learning Models
│   ├── Prophet (Facebook)
│   ├── ARIMA (Estadístico)
│   ├── Entrenamiento en background
│   ├── Almacenamiento en disco
│   └── Gestión de estado
│
├── 🔮 Predictions
│   ├── Generación de predicciones
│   ├── Cálculo de intervalos de confianza
│   ├── Visualización de gráficos
│   └── Exportación de resultados
│
├── 📊 Metrics & Help
│   ├── Evaluación de modelos (RMSE, MAE, AIC, BIC)
│   ├── Explicaciones educativas
│   ├── Benchmarks y interpretación
│   └── Ejemplos prácticos
│
└── 💾 Storage & Database
    ├── SQLite (usuarios, datasets, modelos)
    ├── Disco (archivos de modelos pkl)
    └── Cache temporal
```

### Estructura de Carpetas

```
app/
├── api/v1/
│   └── endpoints/
│       ├── auth.py           ← Autenticación
│       ├── usuarios.py       ← Gestión de usuarios
│       ├── files.py          ← Carga de archivos
│       ├── datasets.py       ← Gestión de datasets
│       ├── crudml.py         ← CRUD de modelos
│       ├── predml.py         ← Predicciones y métricas
│       └── __init__.py
│
├── ml/
│   ├── prophet/
│   │   ├── train.py          ← Entrenar Prophet
│   │   ├── predict.py        ← Predecir con Prophet
│   │   └── utils.py
│   │
│   └── arima/
│       ├── train.py          ← Entrenar ARIMA
│       ├── predict.py        ← Predecir con ARIMA
│       └── utils.py
│
├── models/
│   ├── usuario.py            ← Modelo Usuario (DB)
│   ├── dataset.py            ← Modelo Dataset (DB)
│   ├── data.py               ← Modelo Data (DB)
│   ├── ml.py                 ← Modelo MLModel (DB)
│   └── __init__.py
│
├── schemas/                  ← Validación Pydantic
│   ├── usuario.py
│   ├── ml.py
│   └── __init__.py
│
├── db/
│   ├── base.py               ← Configuración DB
│   ├── session.py            ← Sesión DB
│   └── __init__.py
│
├── services/
│   ├── file_service.py       ← Procesamiento de archivos
│   ├── ml_storage_service.py ← Gestión de modelos
│   └── __init__.py
│
├── security/
│   └── security.py           ← JWT, bcrypt
│
└── config.py                 ← Configuración global
```

---

## 🔐 Autenticación y Seguridad

### Sistema de Autenticación (JWT)

**Flujo:**
1. Usuario se registra con email + contraseña
2. Backend hashea contraseña con bcrypt (irreversible)
3. Usuario hace login con email + contraseña
4. Backend verifica y devuelve **JWT token** (Bearer)
5. Frontend envía token en header `Authorization: Bearer {token}`
6. Token válido por **30 minutos**
7. Caducidad → usuario debe hacer login otra vez

### Requisitos de Contraseña

- Mínimo 8 caracteres
- Se recomienda: mayúscula, minúscula, número, símbolo

### Headers Requeridos (excepto auth)

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

---

## ⚙️ Configuración Base

### URL Base de la API

```
http://localhost:8000/api/v1
```

### Documentación Interactiva

```
http://localhost:8000/docs          ← Swagger UI
http://localhost:8000/redoc         ← ReDoc
http://localhost:8000/openapi.json  ← OpenAPI Schema
```

### Respuestas Estándar

**Éxito (200-201):**
```json
{
  "id": 1,
  "email": "usuario@example.com",
  "status": "éxito",
  "data": { ... }
}
```

**Error (400-500):**
```json
{
  "detail": "Descripción clara del error"
}
```

---

## 📡 Documentación de Endpoints

### 🔓 AUTENTICACIÓN

---

#### 1. Registrar Usuario

**Endpoint:**
```
POST /auth/register
```

**Descripción:** Crear una nueva cuenta de usuario

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
- `400`: Email ya registrado
- `400`: Username ya en uso
- `400`: Contraseña muy débil

---

#### 2. Login

**Endpoint:**
```
POST /auth/login
```

**Descripción:** Autenticar usuario y obtener JWT token

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
```javascript
const token = response.access_token;
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};
```

**Posibles Errores:**
- `401`: Email o contraseña incorrectos
- `400`: Campos incompletos

---

### 👤 USUARIOS

---

#### 3. Obtener Perfil Actual

**Endpoint:**
```
GET /usuarios/me
```

**Descripción:** Obtener perfil del usuario autenticado

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

**Endpoint:**
```
GET /usuarios/{email}
```

**Descripción:** Obtener información de un usuario específico

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
- `404`: Usuario no encontrado

---

#### 5. Actualizar Perfil

**Endpoint:**
```
PUT /usuarios/me
```

**Descripción:** Actualizar información del usuario autenticado

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body (campos opcionales):**
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

---

#### 6. Subir Archivo (CSV/XLSX)

**Endpoint:**
```
POST /files/upload
```

**Descripción:** Cargar archivo con datos de series temporales

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
- Formatos: `.csv` o `.xlsx`
- Tamaño máximo: 5MB
- Debe contener columna de fecha y columna numérica

**Formato esperado del archivo:**

Opción 1:
```
fecha,valor
2024-01-01,100.5
2024-01-02,105.3
2024-01-03,103.2
```

Opción 2:
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

**Nota sobre el formato:** El backend convierte automáticamente cualquier fecha y valor a formato estándar `DS` (date) y `y` (value) para compatibilidad con Prophet y ARIMA.

---

#### 7. Obtener Mis Archivos

**Endpoint:**
```
GET /files/my-files
```

**Descripción:** Listar todos los archivos del usuario autenticado

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

**Endpoint:**
```
GET /files/{file_id}
```

**Descripción:** Obtener un archivo específico con todos sus datos

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

#### 9. Eliminar Archivo

**Endpoint:**
```
DELETE /files/{file_id}
```

**Descripción:** Eliminar un archivo y todos sus datos asociados

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
- `404`: Archivo no encontrado

---

#### 10. Obtener Todos los Datasets

**Endpoint:**
```
GET /datasets
```

**Descripción:** Listar todos los datasets del usuario autenticado

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

#### 11. Obtener Datos de Dataset (por ID)

**Endpoint:**
```
GET /datasets/id/{dataset_id}/data
```

**Descripción:** Obtener todos los puntos de datos de un dataset

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

#### 12. Obtener Datos de Dataset (por Nombre)

**Endpoint:**
```
GET /datasets/{dataset_name}/data
```

**Descripción:** Obtener datos usando el nombre del dataset

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
    }
  ]
}
```

---

### 🤖 MODELOS DE MACHINE LEARNING

---

#### 13. Crear y Entrenar Modelo

**Endpoint:**
```
POST /models
```

**Descripción:** Crear nuevo modelo ML y comenzar entrenamiento en background

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
- `"prophet"` → Facebook Prophet (ideal para estacionalidad)
- `"arima"` → ARIMA estadístico (ideal para series simples)

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

**⚠️ Nota Importante:**
- El modelo se devuelve **inmediatamente** con estado `"en_entrenamiento"`
- El entrenamiento ocurre en **background** (no bloquea la API)
- Después de ~30 segundos el estado cambia a `"entrenado"` o `"error"`
- **Consulta el estado** con GET `/models/{model_id}` para verificar

**Posibles Errores:**
- `404`: Dataset no encontrado
- `400`: Ya existe modelo con ese nombre para este usuario

---

#### 14. Obtener Todos los Modelos del Usuario

**Endpoint:**
```
GET /models
```

**Descripción:** Listar todos los modelos entrenados por el usuario

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

**Endpoint:**
```
GET /models/dataset/{dataset_id}
```

**Descripción:** Obtener todos los modelos entrenados con un dataset específico

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
    "status": "entrenado",
    "error_message": null
  }
]
```

---

#### 16. Obtener Detalles de un Modelo

**Endpoint:**
```
GET /models/{model_id}
```

**Descripción:** Obtener información completa de un modelo específico

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

#### 17. Obtener Información Detallada del Modelo (ARIMA)

**Endpoint:**
```
GET /predictions/models/{model_id}/info
```

**Descripción:** Obtener métricas de entrenamiento y parámetros del modelo (especialmente útil para ARIMA)

**Headers:**
```
Authorization: Bearer {token}
```

**Path Parameters:**
```
model_id = 1
```

**Response (200 OK) - Para Prophet:**
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

**Response (200 OK) - Para ARIMA (con métricas):**
```json
{
  "id": 1,
  "name": "mi_modelo_arima",
  "model_type": "arima",
  "path": "storage/models/user_1/dataset_1/mi_modelo_arima",
  "status": "entrenado",
  "dataset_id": 1,
  "created_at": "2024-03-23T15:30:00.123456",
  "error_message": null,
  "training_metrics": {
    "order": [1, 1, 1],
    "aic": 245.3,
    "bic": 255.7,
    "rmse": 2.45,
    "mae": 1.89,
    "data_points": 365
  }
}
```

**⚠️ Estados posibles:**
- `"en_entrenamiento"` - Modelo siendo entrenado (espera un poco)
- `"entrenado"` - Listo para hacer predicciones
- `"error"` - Falló el entrenamiento, ver `error_message`

---

### 🔮 PREDICCIONES

---

#### 18. Hacer Predicción

**Endpoint:**
```
POST /predictions/predict
```

**Descripción:** Realizar predicciones con un modelo entrenado

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
- `model_id` (requerido): ID del modelo entrenado
- `periods` (opcional, default: 30): Número de periodos a predecir (1-365)

**Response (200 OK):**
```json
{
  "model_id": 1,
  "model_name": "mi_modelo_prophet",
  "model_type": "prophet",
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
    }
  ],
  "created_at": "2024-03-23T16:15:00.123456"
}
```

**Interpretación de la respuesta:**
- `ds`: Fecha de la predicción
- `yhat`: Valor predicho (centro del intervalo)
- `yhat_lower`: Límite inferior del intervalo de confianza (95%)
- `yhat_upper`: Límite superior del intervalo de confianza (95%)

**Posibles Errores:**
- `404`: Modelo no encontrado
- `400`: Modelo no entrenado aún
- `500`: Error durante predicción

---

#### 19. Obtener Gráfico de Predicción (ARIMA)

**Endpoint:**
```
GET /plots/arima/{model_id}
```

**Descripción:** Generar gráfico de pronóstico con intervalos de confianza

**Headers:**
```
Authorization: Bearer {token}
```

**Path Parameters:**
```
model_id = 1
periods = 30 (opcional)
historical_periods = 50 (opcional)
```

**Response (200 OK):**
```json
{
  "model_id": 1,
  "model_name": "mi_modelo_arima",
  "model_type": "arima",
  "image": "iVBORw0KGgoAAAANSUhEUgAAA...",
  "parameters": {
    "order": [1, 1, 1],
    "periods": 30
  },
  "created_at": "2024-03-23T16:20:00.123456"
}
```

**Nota:** La imagen viene en base64. Frontend debe decodificarlo para mostrar:
```javascript
const imageSrc = `data:image/png;base64,${response.image}`;
document.getElementById('plot').src = imageSrc;
```

---

#### 20. Obtener Datos de Entrenamiento

**Endpoint:**
```
GET /predictions/models/{model_id}/training-data
```

**Descripción:** Obtener los datos usados para entrenar el modelo

**Headers:**
```
Authorization: Bearer {token}
```

**Path Parameters:**
```
model_id = 1
samples = 100 (opcional, default: 20)
```

**Response (200 OK):**
```json
{
  "model_id": 1,
  "model_name": "mi_modelo_arima",
  "training_data": [
    {
      "DS": "2024-01-01",
      "y": 100.5
    },
    {
      "DS": "2024-01-02",
      "y": 105.3
    }
  ],
  "total_training_points": 365
}
```

---

### 📚 AYUDA CONTEXTUAL PARA MÉTRICAS

---

#### 21. Obtener Explicación de una Métrica

**Endpoint:**
```
GET /metrics-help/{metric_name}
```

**Descripción:** Obtener información educativa sobre una métrica específica (para mostrar tooltips y explicaciones)

**No requiere autenticación**

**Path Parameters:**
```
metric_name = rmse, mae, aic, bic, order, data_points
```

**Response (200 OK) - Ejemplo RMSE:**
```json
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

**Response (200 OK) - Ejemplo AIC:**
```json
{
  "label": "AIC (Akaike Information Criterion)",
  "description": "Métrica que balancea precisión vs complejidad del modelo",
  "interpretation": "Solo comparar entre modelos ARIMA. Valor más bajo es mejor.",
  "note": "Número absoluto no tiene significado. Solo importa la comparación.",
  "when_to_use": "Comparar 2+ modelos ARIMA."
}
```

**Response (200 OK) - Ejemplo ARIMA ORDER:**
```json
{
  "label": "ARIMA Order (p, d, q)",
  "description": "Parámetros técnicos del modelo ARIMA",
  "components": {
    "p": "Términos autorregresivos (dependencia del pasado)",
    "d": "Diferenciaciones (para hacer la serie estacionaria)",
    "q": "Términos de media móvil (ruido pasado)"
  },
  "typical_range": "Valores entre 0-2 para cada parámetro son normales",
  "note": "El modelo selecciona automáticamente estos valores."
}
```

**Posibles Errores:**
- `404`: Métrica no documentada

**Métricas disponibles:**
- `rmse` - Root Mean Square Error
- `mae` - Mean Absolute Error
- `aic` - Akaike Information Criterion
- `bic` - Bayesian Information Criterion
- `order` - ARIMA Order (p, d, q)
- `data_points` - Número de puntos de entrenamiento

---

### 🏥 HEALTH & INFO

---

#### 22. Health Check

**Endpoint:**
```
GET /health
```

**Descripción:** Verificar si la API está funcionando

**No requiere autenticación**

**Response (200 OK):**
```json
{
  "status": "✅ healthy",
  "app": "TFG API",
  "version": "1.0.0"
}
```

---

#### 23. Información de la API

**Endpoint:**
```
GET /
```

**Descripción:** Obtener información general y links de documentación

**No requiere autenticación**

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

### Usuario

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | ID único del usuario |
| `email` | String | Email único |
| `password` | String (hasheado) | Contraseña con bcrypt |
| `tipo` | String | "usuario" o "admin" |
| `created_at` | DateTime | Fecha de creación |

### Dataset

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | ID único del dataset |
| `user_id` | Integer | FK al usuario propietario |
| `name` | String | Nombre del archivo |

### Data (Puntos de datos)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | ID único del registro |
| `dataset_id` | Integer | FK al dataset |
| `DS` | String (YYYY-MM-DD) | Fecha |
| `y` | Float | Valor numérico |

### MLModel (Modelo de Machine Learning)

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

## 🔄 Flujos de Uso Principales

### Flujo 1: Crear Cuenta y Subir Primer Dataset

```
1. POST /auth/register
   ├─ Email: usuario@example.com
   ├─ Password: MiPassword123
   └─ Username: mi_usuario

2. POST /auth/login
   ├─ Username: usuario@example.com
   ├─ Password: MiPassword123
   └─ Response: access_token (guardarlo en localStorage)

3. POST /files/upload
   ├─ Header: Authorization: Bearer {token}
   ├─ File: datos_ventas.csv
   └─ Response: dataset_id = 1

4. GET /datasets
   └─ Ver: [{"id": 1, "name": "datos_ventas.csv"}]
```

---

### Flujo 2: Entrenar Modelo y Visualizar Métricas

```
1. POST /models
   ├─ name: "mi_primer_modelo"
   ├─ dataset_id: 1
   ├─ model_type: "arima"
   └─ Response: model_id = 1 (status: en_entrenamiento)

2. GET /predictions/models/1/info (polling cada 2 seg)
   ├─ Esperar: status = "entrenado"
   └─ Obtener: training_metrics (rmse, mae, aic, bic, order)

3. GET /metrics-help/rmse (para mostrar tooltip)
   └─ Frontend: Mostrar explicación de RMSE

4. Mostrar métricas con colores:
   ├─ RMSE < 10% → Verde ✅
   ├─ RMSE 10-30% → Amarillo ⚠️
   └─ RMSE > 30% → Rojo ❌
```

---

### Flujo 3: Hacer Predicción y Visualizar

```
1. POST /predictions/predict
   ├─ model_id: 1
   ├─ periods: 30
   └─ Response: forecast array

2. Frontend procesa:
   ├─ Extrae: ds, yhat, yhat_lower, yhat_upper
   └─ Dibuja: gráfico con área sombrada entre lower/upper

3. GET /plots/arima/1 (opcional)
   ├─ Response: imagen base64
   └─ Frontend: Mostrar gráfico pre-generado
```

---

### Flujo 4: Comparar Modelos

```
1. GET /models/dataset/1
   │
   ├─ Modelo A: ARIMA
   │  ├─ AIC: 240
   │  ├─ BIC: 250
   │  ├─ RMSE: 2.45
   │  └─ MAE: 1.89
   │
   └─ Modelo B: Prophet
      ├─ Sin AIC/BIC (Prophet no los usa)
      ├─ Intervalo: yhat_lower - yhat_upper
      └─ Se ve en predicciones

2. Frontend:
   ├─ Crear tabla de comparación
   ├─ Destacar mejores valores
   └─ Mostrar recomendación: "Modelo A es mejor"
```

---

## 🚀 Integración Frontend

### Requisitos para el Frontend

1. **Gestión de estado:**
   - Usuario autenticado (token)
   - Datasets disponibles
   - Modelos entrenados
   - Predicciones actuales

2. **Componentes principales:**
   - Login/Register
   - Upload de archivos
   - Visualización de datasets
   - Formulario de creación de modelos
   - Panel de métricas (con explicaciones)
   - Gráficos de predicciones
   - Comparación de modelos

3. **Manejo de estados de modelo:**
   ```
   en_entrenamiento → (polling) → entrenado/error
   ```

4. **Ayuda contextual:**
   - Tooltips al pasar mouse sobre ℹ️
   - Colores indicadores (✅ ⚠️ ❌)
   - Explicaciones basadas en `/metrics-help/`

5. **Responsividad:**
   - Mobile-first
   - Gráficos escalables
   - Tablas adaptables

---

## 📝 Notas Importantes

### Seguridad

- Guardar token en `localStorage` o `sessionStorage`
- Incluir token en header `Authorization: Bearer {token}` en todas las solicitudes
- No mostrar tokens en logs ni en la UI
- Token caduca en 30 minutos → usuario debe login de nuevo

### Performance

- Cachear datasets y modelos en estado del frontend
- Implementar polling o WebSockets para estado de entrenamiento
- Mostrar spinners mientras se entrenan modelos
- Limitar número de predicciones a 365 periodos máximo

### Validación

- Email válido en login/registro
- Contraseña mínimo 8 caracteres
- Archivos CSV/XLSX máximo 5MB
- Nombres de modelo únicos por usuario
- Periodos de predicción entre 1-365

### Error Handling

- Mostrar mensajes de error claros al usuario
- Reintentar requests fallidas
- Manejar token expirado (redirigir a login)
- Logging de errores para debugging

---

## 📞 Contacto y Soporte

Para dudas sobre la integración:
1. Revisar documentación Swagger: `/docs`
2. Revisar este documento completo
3. Consultar logs del backend: `app.log`

---

**Última actualización:** Marzo 2026  
**Versión API:** 1.0.0  
**Estado:** Listo para desarrollo frontend
