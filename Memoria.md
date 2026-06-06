# Memoria del Trabajo de Fin de Grado

## Plataforma de Predicción de Series Temporales con Modelos de Machine Learning

**Título:** TimeSeriesLab — Plataforma REST API para Forecasting de Series Temporales  
**Tecnología principal:** Python · FastAPI · Prophet · ARIMA/SARIMA · SQLite/PostgreSQL  
**Tipo:** Trabajo de Fin de Grado (TFG) — Ingeniería Informática  

---

## Índice

1. [Introducción y Contexto](#1-introducción-y-contexto)
2. [Objetivos del Proyecto](#2-objetivos-del-proyecto)
3. [Especificación de Requisitos](#3-especificación-de-requisitos)
   - 3.1 [Requisitos Funcionales](#31-requisitos-funcionales)
   - 3.2 [Requisitos No Funcionales](#32-requisitos-no-funcionales)
4. [Arquitectura del Sistema](#4-arquitectura-del-sistema)
   - 4.1 [Vista General](#41-vista-general)
   - 4.2 [Capas de la Arquitectura](#42-capas-de-la-arquitectura)
   - 4.3 [Estructura de Directorios](#43-estructura-de-directorios)
5. [Modelo de Datos](#5-modelo-de-datos)
   - 5.1 [Entidades y Atributos](#51-entidades-y-atributos)
   - 5.2 [Diagrama Entidad-Relación](#52-diagrama-entidad-relación)
6. [Diseño de la API REST](#6-diseño-de-la-api-rest)
   - 6.1 [Módulo de Autenticación](#61-módulo-de-autenticación)
   - 6.2 [Módulo de Usuarios](#62-módulo-de-usuarios)
   - 6.3 [Módulo de Ficheros](#63-módulo-de-ficheros)
   - 6.4 [Módulo de Datasets](#64-módulo-de-datasets)
   - 6.5 [Módulo de Modelos ML](#65-módulo-de-modelos-ml)
   - 6.6 [Módulo de Predicciones](#66-módulo-de-predicciones)
7. [Módulos de Machine Learning](#7-módulos-de-machine-learning)
   - 7.1 [Prophet](#71-prophet)
   - 7.2 [ARIMA / SARIMA](#72-arima--sarima)
   - 7.3 [Detección Automática de Estacionalidad](#73-detección-automática-de-estacionalidad)
   - 7.4 [Validación de Series Temporales](#74-validación-de-series-temporales)
   - 7.5 [Métricas de Evaluación](#75-métricas-de-evaluación)
8. [Seguridad del Sistema](#8-seguridad-del-sistema)
9. [Flujos de Trabajo Principales](#9-flujos-de-trabajo-principales)
   - 9.1 [Flujo de Registro y Login](#91-flujo-de-registro-y-login)
   - 9.2 [Flujo de Subida de Datos](#92-flujo-de-subida-de-datos)
   - 9.3 [Flujo de Entrenamiento de Modelos](#93-flujo-de-entrenamiento-de-modelos)
   - 9.4 [Flujo de Predicción y Visualización](#94-flujo-de-predicción-y-visualización)
10. [Almacenamiento de Modelos](#10-almacenamiento-de-modelos)
11. [Stack Tecnológico](#11-stack-tecnológico)
12. [Configuración y Despliegue](#12-configuración-y-despliegue)
13. [Pruebas](#13-pruebas)
14. [Casos de Uso Detallados](#14-casos-de-uso-detallados)
15. [Decisiones de Diseño](#15-decisiones-de-diseño)
16. [Limitaciones y Trabajo Futuro](#16-limitaciones-y-trabajo-futuro)

---

## 1. Introducción y Contexto

El análisis de series temporales es una disciplina clave en multitud de ámbitos: sanidad (predicción de demanda quirúrgica), logística, economía y muchos otros. Sin embargo, el acceso a herramientas de forecasting suele requerir conocimientos avanzados de programación o software de licencia costosa.

**TimeSeriesLab** es una plataforma REST API que democratiza el acceso al forecasting de series temporales. Permite que cualquier usuario (sin conocimientos de Python ni estadística avanzada) pueda:

1. Subir sus datos históricos en formato CSV o XLSX.
2. Entrenar automáticamente modelos de predicción (Prophet o ARIMA/SARIMA).
3. Obtener predicciones futuras con intervalos de confianza.
4. Visualizar los resultados mediante gráficas codificadas como imágenes PNG.

El sistema ha sido desarrollado como un **backend REST API** con FastAPI, pensado para ser consumido desde cualquier cliente (aplicación web, móvil, notebook de Jupyter, etc.). Toda la lógica de negocio, entrenamiento ML y almacenamiento se gestiona del lado del servidor.

---

## 2. Objetivos del Proyecto

### Objetivo General

Desarrollar una plataforma backend completa de forecasting de series temporales, accesible mediante API REST, que permita a usuarios registrados gestionar sus datos y obtener predicciones con modelos de Machine Learning.

### Objetivos Específicos

| ID | Objetivo |
|----|----------|
| OBJ-01 | Implementar un sistema completo de gestión de usuarios con autenticación JWT |
| OBJ-02 | Permitir la carga y validación automática de ficheros CSV/XLSX con series temporales |
| OBJ-03 | Integrar el modelo Prophet para forecasting de series con estacionalidad compleja |
| OBJ-04 | Integrar modelos ARIMA/SARIMA con selección automática de parámetros via `auto_arima` |
| OBJ-05 | Implementar detección automática de estacionalidad para elegir entre ARIMA y SARIMA |
| OBJ-06 | Generar predicciones con intervalos de confianza del 95% |
| OBJ-07 | Generar visualizaciones automáticas (gráficas PNG en Base64) de las predicciones |
| OBJ-08 | Asegurar el aislamiento de datos por usuario (cada usuario solo accede a sus propios recursos) |
| OBJ-09 | Implementar recuperación de contraseña por email con tokens de expiración |
| OBJ-10 | Proveer documentación interactiva automática de la API (Swagger UI / ReDoc) |
| OBJ-11 | Diseñar el sistema para ser desplegable en contenedor Docker |

---

## 3. Especificación de Requisitos

### 3.1 Requisitos Funcionales

Los requisitos funcionales describen **qué debe hacer** el sistema.

---

#### RF-01 — Registro de Usuario

**Descripción:** El sistema debe permitir registrar nuevas cuentas de usuario.  
**Actores:** Usuario anónimo  
**Entradas:**
- `username` (3–100 caracteres, único)
- `email` (formato válido, único)
- `password` (mínimo 10 caracteres, con mayúsculas, minúsculas, dígito y carácter especial)
- `tipo` (opcional; "usuario" o "admin", por defecto "usuario")

**Procesamiento:**
1. Verificar unicidad de email y username.
2. Hashear la contraseña con bcrypt (12 rounds).
3. Persistir el usuario en la base de datos.
4. Enviar email de bienvenida (si SMTP configurado).

**Salidas:** Datos del usuario creado (sin contraseña). HTTP 201.  
**Errores:** HTTP 400 si email o username ya existen.

---

#### RF-02 — Autenticación (Login)

**Descripción:** El sistema debe autenticar usuarios y emitir tokens JWT.  
**Entradas:** `username`, `password`  
**Procesamiento:**
1. Buscar usuario por username.
2. Verificar contraseña con bcrypt.
3. Generar JWT con `user_id` y `user_type` (expiración configurable, por defecto 30 minutos).

**Salidas:** `access_token` (JWT Bearer) y `token_type`. HTTP 200.  
**Errores:** HTTP 401 si credenciales incorrectas.

---

#### RF-03 — Recuperación de Contraseña por Email

**Descripción:** El sistema debe permitir recuperar contraseñas olvidadas mediante un enlace enviado por email.  
**Entradas:** `email` del usuario.  
**Procesamiento:**
1. Verificar que el email existe en el sistema.
2. Generar un JWT de reset con propósito específico (`"purpose": "password_reset"`) y expiración de 60 minutos.
3. Enviar email con enlace que incluye el token.
4. En la confirmación, verificar el token y actualizar la contraseña hasheada.

**Errores:** HTTP 400 si token inválido o expirado.

---

#### RF-04 — Gestión del Perfil de Usuario

**Descripción:** El sistema debe permitir a cada usuario consultar y actualizar su propio perfil.  
**Sub-requisitos:**
- **RF-04a:** Consultar perfil propio (`GET /api/v1/usuarios/me`).
- **RF-04b:** Actualizar email o contraseña (`PUT /api/v1/usuarios/me`).
- **RF-04c:** Cambiar contraseña con verificación de la actual (`POST /api/v1/usuarios/me/change-password`).
- **RF-04d:** Cambiar nombre de usuario con comprobación de unicidad (`PATCH /api/v1/usuarios/me/username`).
- **RF-04e:** Eliminar cuenta propia previa verificación de contraseña.

---

#### RF-05 — Subida de Ficheros de Datos

**Descripción:** El sistema debe permitir subir ficheros CSV o XLSX con series temporales.  
**Validaciones aplicadas:**
1. Extensión del fichero: únicamente `.csv` o `.xlsx`.
2. Tamaño máximo: 5 MB.
3. Número de columnas: exactamente 2 (una de fecha y una numérica).
4. Detección automática de la columna de fechas (compatible con formatos `DD-MM-YYYY`, `MM-DD-YYYY`, `YYYY-MM-DD`).
5. Todas las fechas convertidas al formato estándar `YYYY-MM-DD` antes de almacenar.
6. Sin fechas duplicadas (la serie temporal requiere timestamps únicos).
7. Sin nombre de fichero repetido para el mismo usuario.
8. Al menos una fila válida con fecha y valor numérico.

**Almacenamiento:** Cada fila válida se almacena como un objeto `Data` (campos `DS`, `y`) vinculado a un `Dataset`.  
**Salidas:** ID del dataset creado, número de entradas procesadas, advertencias si alguna fila fue descartada. HTTP 201.

---

#### RF-06 — Gestión de Ficheros y Datasets

**Sub-requisitos:**
- **RF-06a:** Listar todos los datasets del usuario autenticado.
- **RF-06b:** Obtener un dataset por ID con todos sus puntos de datos.
- **RF-06c:** Eliminar un dataset (y en cascada sus datos y modelos asociados).
- **RF-06d:** Consultar los puntos de datos de un dataset ordenados por fecha ascendente.

---

#### RF-07 — Creación y Entrenamiento de Modelos ML

**Descripción:** El sistema debe permitir crear modelos de ML asociados a un dataset y entrenarlos automáticamente.  
**Entradas:**
- `name` (único por usuario)
- `dataset_id` (debe pertenecer al usuario)
- `model_type`: `"prophet"` o `"arima"`

**Procesamiento:**
1. Verificar que el dataset existe y pertenece al usuario.
2. Verificar unicidad del nombre de modelo para ese usuario.
3. Crear el registro en BD con estado `"en_entrenamiento"`.
4. Retornar la respuesta HTTP inmediatamente (no bloquear al cliente).
5. Lanzar una **tarea de background** que:
   - Carga los datos del dataset desde la BD.
   - Entrena el modelo (Prophet o ARIMA/SARIMA según el tipo elegido).
   - Guarda el fichero del modelo en disco (`storage/models/user_{id}/dataset_{id}/{name}/`).
   - Guarda un fichero `{name}_metadata.json` con parámetros y métricas.
   - Actualiza el estado en BD a `"entrenado"` o `"error"`.

---

#### RF-08 — Selección Automática ARIMA vs. SARIMA

**Descripción:** Cuando se solicita tipo `"arima"`, el sistema debe detectar automáticamente si la serie tiene estacionalidad y elegir el modelo más adecuado.

**Lógica:**
1. Ejecutar descomposición estacional (`seasonal_decompose` con período=12).
2. Calcular la **fuerza estacional** = `var(seasonal) / (var(seasonal) + var(residual))`.
3. Si fuerza > 0.1 → **SARIMA** con período estacional 12.
4. Si fuerza ≤ 0.1 → **ARIMA** sin componente estacional.
5. En ambos casos, `auto_arima` (pmdarima) busca los órdenes `(p,d,q)` óptimos por criterio AIC.
6. El tipo real del modelo (`arima` o `sarima`) se actualiza en la BD tras el entrenamiento.

---

#### RF-09 — CRUD de Modelos ML

**Sub-requisitos:**
- **RF-09a:** Listar todos los modelos del usuario.
- **RF-09b:** Listar modelos entrenados con un dataset específico.
- **RF-09c:** Obtener detalle de un modelo por ID (parámetros, estado, ruta, métricas).
- **RF-09d:** Actualizar el nombre de un modelo.
- **RF-09e:** Eliminar un modelo (registro en BD + directorio en disco).

---

#### RF-10 — Predicción con Modelos Entrenados

**Descripción:** El sistema debe generar predicciones futuras con un modelo previamente entrenado.  
**Entradas:**
- `model_id`: ID del modelo (debe estar en estado `"entrenado"`)
- `periods`: Número de períodos a predecir (1–365)

**Salidas:**
- Lista de puntos predichos: `date`, `yhat`, `yhat_lower` (IC 95%), `yhat_upper` (IC 95%).
- Metadatos: `model_id`, `model_name`, `model_type`, `dataset_id`, `created_at`.

**El sistema detecta automáticamente el tipo de modelo** (Prophet o ARIMA/SARIMA) y delega a la función correspondiente.

---

#### RF-11 — Visualización de Predicciones (Gráficas)

**Descripción:** El sistema debe generar gráficas de predicción y componentes del modelo como imágenes PNG codificadas en Base64.  
**Para modelos Prophet:**
- Gráfica de **tendencia** (`trend`).
- Gráfica de **estacionalidad semanal** (`weekly`), si está disponible.
- Gráfica de **estacionalidad diaria** (`daily`), si está disponible.

**Para modelos ARIMA/SARIMA:**
- Gráfica de serie histórica + pronóstico con banda de confianza.

**Formato de respuesta:** `data:image/png;base64,<datos>` para su uso directo en atributos `src` de HTML.

---

#### RF-12 — Información Detallada del Modelo

**Descripción:** El sistema debe exponer las métricas de entrenamiento de cada modelo.  
**Para Prophet:** MAE, RMSE, MAPE, número de datos de entrenamiento.  
**Para ARIMA/SARIMA:** Órdenes `(p,d,q)` y `(P,D,Q,m)`, AIC, BIC, RMSE, MAE, MAPE, número de datos.

---

#### RF-13 — Envío de Emails Transaccionales

**Descripción:** El sistema debe enviar emails automáticos en eventos clave.  
**Eventos:**
- Registro exitoso → email de bienvenida con descripción de funcionalidades.
- Solicitud de reset de contraseña → email con enlace de restablecimiento.

**Comportamiento:** Si SMTP no está configurado, el sistema registra un aviso en el log pero no interrumpe el flujo.

---

#### RF-14 — Control de Acceso Basado en Roles

**Descripción:** El sistema distingue entre usuarios de tipo `"usuario"` y `"admin"`.  
**Admin:** Acceso a endpoints de gestión (consultar usuarios por email, etc.).  
**Usuario:** Solo accede a sus propios recursos.

---

### 3.2 Requisitos No Funcionales

Los requisitos no funcionales describen **cómo debe comportarse** el sistema.

---

#### RNF-01 — Seguridad

| Aspecto | Implementación |
|---------|---------------|
| Contraseñas | Hashing con bcrypt, 12 rounds de coste |
| Tokens de acceso | JWT firmados con SECRET_KEY (HS256), expiración configurable |
| Tokens de reset | JWT con campo `"purpose": "password_reset"` y expiración de 60 min |
| Autorización | Todos los endpoints (salvo `/auth/register` y `/auth/login`) requieren Bearer token válido |
| Aislamiento de datos | Cada consulta a BD filtra por `user_id` del usuario autenticado; nunca se exponen datos de otros usuarios |
| Validación de entrada | Pydantic valida esquemas en cada endpoint antes de procesar |
| CORS | Configurable via variables de entorno |

---

#### RNF-02 — Rendimiento

| Aspecto | Requisito |
|---------|-----------|
| Respuesta a creación de modelo | ≤ 200ms (el entrenamiento ocurre en background) |
| Tamaño máximo de fichero | 5 MB |
| Predicción (modelo ya entrenado) | Respuesta razonable para 1-365 períodos |
| Entrenamiento Prophet | Depende del volumen de datos (típicamente < 60 s para series de 1000 obs) |
| Entrenamiento ARIMA | Depende de la búsqueda `auto_arima`; puede tardar varios minutos en series largas |

---

#### RNF-03 — Escalabilidad

- La arquitectura está organizada en capas independientes (API → Servicio → ML → BD).
- El almacenamiento de modelos es en sistema de ficheros, escalable a almacenamiento en la nube (S3, Azure Blob) con cambios mínimos en `MLStorageService`.
- La base de datos es configurable: SQLite para desarrollo, PostgreSQL para producción (vía variable `DATABASE_URL`).

---

#### RNF-04 — Mantenibilidad

- Código estructurado siguiendo el principio de **separación de responsabilidades** (capas: API, servicio, ML, BD).
- Configuración centralizada en `app/config.py` mediante `pydantic-settings` (variables de entorno).
- Logging estructurado en todos los módulos con niveles INFO/WARNING/ERROR.
- Documentación automática de la API generada por FastAPI (OpenAPI 3.0).

---

#### RNF-05 — Disponibilidad y Operación

- Endpoint `/health` para monitorización del estado del servicio.
- Inicialización automática de la base de datos al arranque (`init_db()`).
- Soporte para despliegue en Docker (dockerfile + docker-compose.yml incluidos).
- Configuración de servidor Nginx como proxy inverso (incluida en `nginx/default.conf`).

---

#### RNF-06 — Usabilidad de la API

- Documentación interactiva en `/docs` (Swagger UI) y `/redoc` (ReDoc).
- Mensajes de error descriptivos en español e inglés.
- Versionado de la API bajo el prefijo `/api/v1/`.

---

#### RNF-07 — Portabilidad

- Compatible con Python 3.10+.
- Dependencias declaradas en `requirements.txt` y `pyproject.toml`.
- Configurable completamente por variables de entorno (sin hardcoding de rutas o credenciales).

---

#### RNF-08 — Restricciones de Datos

| Restricción | Valor |
|-------------|-------|
| Tamaño máximo fichero | 5 MB |
| Columnas requeridas | Exactamente 2 (fecha + numérico) |
| Períodos de predicción | 1 a 365 |
| Longitud mínima de serie (ARIMA) | 50 observaciones |
| Contraseña mínima | 10 caracteres + mayúscula + minúscula + dígito + especial |
| Username | 3 a 100 caracteres |
| Mensaje de error máximo | 500 caracteres |

---

## 4. Arquitectura del Sistema

### 4.1 Vista General

El sistema sigue una **arquitectura en capas** (Layered Architecture) con los siguientes niveles:

```
┌──────────────────────────────────────────────┐
│              CLIENTE (HTTP)                   │
│   Navegador / App móvil / Script Python       │
└───────────────────┬──────────────────────────┘
                    │ HTTP/REST (JSON)
                    ▼
┌──────────────────────────────────────────────┐
│          FASTAPI APPLICATION                 │
│                                              │
│  ┌───────────────────────────────────────┐   │
│  │   CAPA DE API  (/api/v1/...)          │   │
│  │  auth · usuarios · files · datasets  │   │
│  │  models (crudml) · predictions       │   │
│  └──────────────┬────────────────────────┘   │
│                 │                            │
│  ┌──────────────▼────────────────────────┐   │
│  │  CAPA DE SEGURIDAD                    │   │
│  │  JWT validation · bcrypt · Pydantic   │   │
│  └──────────────┬────────────────────────┘   │
│                 │                            │
│  ┌──────────────▼────────────────────────┐   │
│  │  CAPA DE SERVICIOS                    │   │
│  │  FileService · MLStorageService       │   │
│  │  EmailService                         │   │
│  └──────────────┬────────────────────────┘   │
│                 │                            │
│  ┌──────────────▼────────────────────────┐   │
│  │  MÓDULOS ML                           │   │
│  │  Prophet (train/predict)              │   │
│  │  ARIMA/SARIMA (train/predict/utils)   │   │
│  └──────────────┬────────────────────────┘   │
│                 │                            │
└─────────────────┼────────────────────────────┘
                  │
     ┌────────────┼───────────┐
     ▼            ▼           ▼
┌─────────┐ ┌──────────┐ ┌──────────┐
│   BD    │ │ STORAGE  │ │  LOGGING │
│SQLite/  │ │/storage/ │ │ stdout   │
│Postgres │ │ models/  │ │          │
└─────────┘ └──────────┘ └──────────┘
```

### 4.2 Capas de la Arquitectura

#### Capa de API (`app/api/v1/endpoints/`)

Gestiona las peticiones HTTP entrantes:
- **`auth.py`** — Registro, login, recuperación de contraseña.
- **`usuarios.py`** — CRUD de perfil de usuario.
- **`files.py`** — Upload, listado, descarga y eliminación de ficheros.
- **`datasets.py`** — Acceso a datasets y sus puntos de datos.
- **`crudml.py`** — CRUD de modelos ML + lanzamiento del entrenamiento en background.
- **`predml.py`** — Predicciones y visualizaciones para todos los tipos de modelo.

#### Capa de Seguridad (`app/security/security.py`)

- Gestión de contraseñas: `hash_password()`, `verify_password()` (bcrypt).
- Gestión de tokens: `create_access_token()`, `create_password_reset_token()`, `verify_password_reset_token()`.
- Dependencia FastAPI: `get_current_user()` — extrae y valida el JWT del header `Authorization`.
- `get_admin_user()` — dependencia para endpoints exclusivos de administrador.

#### Capa de Servicios (`app/services/`)

- **`FileService`** — Lógica de subida, validación, almacenamiento en BD y eliminación de ficheros.
- **`MLStorageService`** — Gestión de rutas de almacenamiento de modelos, carga de modelos Prophet (`.json`) y ARIMA (`.pkl`), carga de metadatos.
- **`email_service`** — Envío de emails transaccionales via SMTP.

#### Módulos ML (`app/ml/`)

- **`prophet/train.py`** — Entrenamiento del modelo Prophet, cálculo de métricas, guardado del modelo JSON y metadatos.
- **`prophet/predict.py`** — Carga del modelo entrenado, generación de forecast, obtención de datos de entrenamiento para visualización.
- **`arima/train.py`** — Entrenamiento ARIMA/SARIMA con `auto_arima`, detección de estacionalidad, guardado `.pkl` y metadatos JSON.
- **`arima/predict.py`** — Predicción con ARIMA/SARIMA entrenado, cálculo de intervalos de confianza, generación de gráfica.
- **`arima/utils.py`** — Validaciones específicas para ARIMA: longitud mínima, valores nulos, detección de estacionalidad, detección de outliers, validación de frecuencia.

#### Capa de Base de Datos (`app/db/`)

- **`base.py`** — Configuración del motor SQLAlchemy y la base declarativa.
- **`session.py`** — Gestión de sesiones de BD, función `get_db()` como dependencia FastAPI.

### 4.3 Estructura de Directorios

```
TFG/
├── main.py                    # Punto de entrada; crea la app FastAPI
├── app/
│   ├── config.py              # Settings (pydantic-settings + .env)
│   ├── paths.py               # Rutas absolutas del sistema de ficheros
│   ├── api/v1/endpoints/      # Routers HTTP
│   │   ├── auth.py
│   │   ├── usuarios.py
│   │   ├── files.py
│   │   ├── datasets.py
│   │   ├── crudml.py
│   │   └── predml.py
│   ├── models/                # Modelos ORM SQLAlchemy
│   │   ├── usuario.py
│   │   ├── dataset.py
│   │   ├── data.py
│   │   └── ml.py
│   ├── schemas/               # Esquemas Pydantic (validación E/S)
│   │   ├── usuario.py
│   │   └── ml.py
│   ├── services/              # Lógica de negocio
│   │   ├── file_service.py
│   │   ├── ml_storage_service.py
│   │   └── email_service.py
│   ├── security/
│   │   └── security.py        # JWT, bcrypt, dependencias auth
│   ├── ml/
│   │   ├── prophet/
│   │   │   ├── train.py
│   │   │   └── predict.py
│   │   └── arima/
│   │       ├── train.py
│   │       ├── predict.py
│   │       └── utils.py
│   └── db/
│       ├── base.py
│       └── session.py
├── storage/
│   └── models/
│       └── user_{id}/
│           └── dataset_{id}/
│               └── {model_name}/
│                   ├── {model_name}.json        # Prophet
│                   ├── {model_name}.pkl         # ARIMA/SARIMA
│                   └── {model_name}_metadata.json
├── tests/
│   ├── conftest.py
│   ├── test_endpoints.py
│   └── example_test.py
├── setsPrueba/                # Datasets de prueba
├── nginx/default.conf         # Configuración Nginx
├── docker-compose.yml
├── dockerfile
└── requirements.txt
```

---

## 5. Modelo de Datos

### 5.1 Entidades y Atributos

#### Tabla `usuarios`

| Campo | Tipo | Restricciones | Descripción |
|-------|------|--------------|-------------|
| `id` | INTEGER | PK, AUTO | Identificador único |
| `username` | VARCHAR(100) | UNIQUE, NOT NULL, INDEX | Nombre de usuario único |
| `email` | VARCHAR | UNIQUE, NOT NULL, INDEX | Correo electrónico |
| `password` | VARCHAR(255) | NOT NULL | Contraseña hasheada (bcrypt) |
| `tipo` | VARCHAR | NOT NULL, DEFAULT 'usuario' | Rol: `'usuario'` o `'admin'` |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Fecha de creación |

**Relaciones:**
- 1 usuario → N datasets (CASCADE DELETE)
- 1 usuario → N modelos ML (CASCADE DELETE)

---

#### Tabla `datasets`

| Campo | Tipo | Restricciones | Descripción |
|-------|------|--------------|-------------|
| `id` | INTEGER | PK, AUTO | Identificador único |
| `user_id` | INTEGER | FK → usuarios.id, NOT NULL | Propietario |
| `name` | VARCHAR | NOT NULL | Nombre original del fichero |

**Relaciones:**
- 1 dataset → N data entries (CASCADE DELETE)
- 1 dataset → N modelos ML (CASCADE DELETE)

---

#### Tabla `data`

| Campo | Tipo | Restricciones | Descripción |
|-------|------|--------------|-------------|
| `id` | INTEGER | PK, AUTO | Identificador único |
| `dataset_id` | INTEGER | FK → datasets.id, NOT NULL | Dataset al que pertenece |
| `DS` | VARCHAR/DATE | NOT NULL | Fecha del punto (YYYY-MM-DD) |
| `y` | FLOAT | NOT NULL | Valor numérico |

---

#### Tabla `ml_models`

| Campo | Tipo | Restricciones | Descripción |
|-------|------|--------------|-------------|
| `id` | INTEGER | PK, AUTO | Identificador único |
| `user_id` | INTEGER | FK → usuarios.id, NOT NULL | Propietario del modelo |
| `dataset_id` | INTEGER | FK → datasets.id, NOT NULL | Dataset de entrenamiento |
| `name` | VARCHAR | NOT NULL | Nombre del modelo (único por usuario) |
| `model_type` | VARCHAR | NOT NULL | `'prophet'`, `'arima'` o `'sarima'` |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Fecha de creación |
| `model_path` | VARCHAR | NOT NULL | Ruta al directorio del modelo en disco |
| `status` | VARCHAR | NOT NULL | `'en_entrenamiento'`, `'entrenado'` o `'error'` |
| `error_message` | VARCHAR(500) | NULLABLE | Detalle del error si status='error' |

### 5.2 Diagrama Entidad-Relación

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   usuarios   │──1:N───▶│   datasets   │──1:N───▶│     data     │
│              │         │              │         │              │
│ id (PK)      │         │ id (PK)      │         │ id (PK)      │
│ username     │         │ user_id (FK) │         │ dataset_id   │
│ email        │         │ name         │         │ DS           │
│ password     │         └──────┬───────┘         │ y            │
│ tipo         │                │ 1:N              └──────────────┘
│ created_at   │                ▼
└──────┬───────┘         ┌──────────────┐
       │                 │  ml_models   │
       └──────1:N────────│              │
                         │ id (PK)      │
                         │ user_id (FK) │
                         │ dataset_id   │
                         │ name         │
                         │ model_type   │
                         │ model_path   │
                         │ status       │
                         │ error_msg    │
                         │ created_at   │
                         └──────────────┘
```

---

## 6. Diseño de la API REST

Todos los endpoints (excepto registro y login) requieren el header:
```
Authorization: Bearer <access_token>
```

Base URL: `http://<host>:8000/api/v1`

### 6.1 Módulo de Autenticación

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register` | Registrar nuevo usuario | No |
| POST | `/auth/login` | Obtener token JWT | No |
| POST | `/auth/password-reset/request` | Solicitar reset de contraseña | No |
| POST | `/auth/password-reset/confirm` | Confirmar nuevo password con token | No |

### 6.2 Módulo de Usuarios

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/usuarios/me` | Perfil del usuario actual | Sí |
| PUT | `/usuarios/me` | Actualizar email/contraseña | Sí |
| POST | `/usuarios/me/change-password` | Cambiar contraseña | Sí |
| PATCH | `/usuarios/me/username` | Cambiar nombre de usuario | Sí |
| DELETE | `/usuarios/me` | Eliminar cuenta propia | Sí |
| GET | `/usuarios/{email}` | Buscar usuario por email | Admin |

### 6.3 Módulo de Ficheros

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/files/upload` | Subir fichero CSV/XLSX | Sí |
| GET | `/files/my-files` | Listar ficheros del usuario | Sí |
| GET | `/files/{file_id}` | Obtener fichero por ID | Sí |
| DELETE | `/files/{file_id}` | Eliminar fichero | Sí |

### 6.4 Módulo de Datasets

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/datasets` | Listar datasets del usuario | Sí |
| GET | `/datasets/id/{dataset_id}/data` | Obtener puntos de datos del dataset | Sí |

### 6.5 Módulo de Modelos ML

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/models` | Crear modelo y lanzar entrenamiento | Sí |
| GET | `/models` | Listar todos los modelos del usuario | Sí |
| GET | `/models/dataset/{dataset_id}` | Modelos de un dataset específico | Sí |
| GET | `/models/{model_id}` | Detalle de un modelo | Sí |
| PUT | `/models/{model_id}` | Actualizar nombre del modelo | Sí |
| DELETE | `/models/{model_id}` | Eliminar modelo (BD + disco) | Sí |

### 6.6 Módulo de Predicciones

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/predictions/predict` | Predecir con cualquier modelo | Sí |
| GET | `/predictions/models/{model_id}/info` | Métricas de un modelo | Sí |
| GET | `/predictions/plots/{model_id}` | Gráficas de componentes (Prophet) | Sí |
| POST | `/predictions/arima/predict` | Predecir específicamente con ARIMA | Sí |
| GET | `/predictions/arima/models/{model_id}/info` | Detalle ARIMA | Sí |
| GET | `/predictions/arima/plots/{model_id}` | Gráfica ARIMA con histórico | Sí |

---

## 7. Módulos de Machine Learning

### 7.1 Prophet

**Librería:** `prophet` (Meta / Facebook)

**¿Qué es Prophet?**  
Prophet es un modelo de regresión aditiva diseñado para series temporales con patrones estacionales marcados. Descompone la serie en:
- **Tendencia** (`trend`): Modelada con funciones lineales o logísticas.
- **Estacionalidad** (`yearly`, `weekly`, `daily`): Modelada con series de Fourier.
- **Efectos de vacaciones** (no usados en este TFG).

**Entrenamiento (`prophet/train.py`):**
1. Recibe un `DataFrame` con columnas `ds` (fecha) y `y` (valor).
2. Instancia `Prophet(interval_width=0.95, yearly_seasonality=True)`.
3. Llama a `model.fit(df)`.
4. Genera predicciones sobre los datos de entrenamiento para calcular métricas.
5. Serializa el modelo como JSON (`model_to_json`) en `{model_name}.json`.
6. Guarda metadatos (MAE, RMSE, MAPE, longitud) en `{model_name}_metadata.json`.

**Predicción (`prophet/predict.py`):**
1. Carga el modelo desde el directorio vía `MLStorageService.load_prophet_model_from_directory()`.
2. Genera un dataframe de fechas futuras con `model.make_future_dataframe(periods=n)`.
3. Llama a `model.predict(future_df)`.
4. Devuelve los últimos `n` registros del forecast (solo los futuros).

**Visualización:**
- Gráfica de **tendencia**: columna `forecast["trend"]`.
- Gráfica de **estacionalidad semanal**: columna `forecast["weekly"]` (si existe).
- Gráfica de **estacionalidad diaria**: columna `forecast["daily"]` (si existe).
- Cada figura se convierte a PNG en memoria (BytesIO) y se codifica en Base64.

---

### 7.2 ARIMA / SARIMA

**Librerías:** `pmdarima` (para `auto_arima`), `statsmodels` (motor interno).

**¿Qué es ARIMA?**  
ARIMA(*p*, *d*, *q*) es un modelo estadístico para series temporales que combina:
- **AR(*p*)**: Autoregresivo — la serie depende de sus *p* valores pasados.
- **I(*d*)**: Integrado — número de diferenciaciones para lograr estacionariedad.
- **MA(*q*)**: Media móvil — dependencia de los *q* errores pasados.

**SARIMA** añade componentes estacionales: SARIMA(*p*,*d*,*q*)×(*P*,*D*,*Q*,*m*) donde *m* es el período estacional.

**Entrenamiento (`arima/train.py`):**
1. Valida la serie con `validate_arima_series()` (longitud, nulos, outliers, estacionalidad).
2. Determina si usar SARIMA o ARIMA en base a la detección de estacionalidad.
3. Llama a `auto_arima()` con los parámetros apropiados para encontrar los órdenes óptimos por AIC.
4. El modelo ajustado se guarda como `.pkl` con `joblib.dump()`.
5. Se calculan métricas sobre los valores ajustados (`fittedvalues`).
6. Los metadatos (órdenes, AIC, BIC, RMSE, MAE, MAPE) se guardan en JSON.

**Predicción (`arima/predict.py`):**
1. Carga el modelo desde el directorio.
2. Llama a `arima_model.predict(n_periods=n, return_conf_int=True, alpha=0.05)`.
3. Construye índice de fechas futuras a partir de la última fecha del entrenamiento.
4. Devuelve lista de puntos con `date`, `yhat`, `yhat_lower`, `yhat_upper`.

---

### 7.3 Detección Automática de Estacionalidad

**Módulo:** `app/ml/arima/utils.py` — función `detect_seasonality()`

**Algoritmo:**
1. Verifica que la serie tenga al menos `2 × max_period` observaciones (por defecto 48).
2. Aplica `seasonal_decompose(series, period=12, model='additive')`.
3. Calcula la **fuerza estacional**:
   $$F_s = \frac{Var(S)}{Var(S) + Var(R)}$$
   donde $S$ es la componente estacional y $R$ el residuo.
4. Si $F_s > 0.1$ → hay estacionalidad → SARIMA con período 12.
5. Si $F_s \leq 0.1$ → no hay estacionalidad → ARIMA puro.

---

### 7.4 Validación de Series Temporales

Antes de entrenar ARIMA, la función `validate_arima_series()` ejecuta:

| Validación | Criterio de fallo |
|------------|-------------------|
| **Longitud mínima** | < 50 observaciones |
| **Valores nulos** | Se interpolan linealmente si los hay |
| **Outliers (IQR)** | > 5% de valores atípicos → serie problemática |
| **Frecuencia** | Se intenta inferir y asignar con `pd.infer_freq()` |
| **Estacionalidad** | Reportada, no es criterio de fallo |

Los criterios reales de invalidación son: longitud insuficiente y exceso de outliers. Los nulos se corrigen automáticamente mediante interpolación lineal.

---

### 7.5 Métricas de Evaluación

Las métricas se calculan sobre los **datos de entrenamiento** (ajuste in-sample) al finalizar el entrenamiento:

| Métrica | Fórmula | Descripción |
|---------|---------|-------------|
| **MAE** | $\frac{1}{n}\sum|y_i - \hat{y}_i|$ | Error absoluto medio |
| **RMSE** | $\sqrt{\frac{1}{n}\sum(y_i - \hat{y}_i)^2}$ | Raíz del error cuadrático medio |
| **MAPE** | $\frac{100}{n}\sum\left|\frac{y_i - \hat{y}_i}{y_i}\right|$ | Error porcentual absoluto medio (excluye ceros) |
| **AIC** | Solo ARIMA | Criterio de información de Akaike (selección de orden) |
| **BIC** | Solo ARIMA | Criterio de información bayesiano |

---

## 8. Seguridad del Sistema

### Autenticación y Autorización

El sistema implementa **OAuth2 con JWT Bearer tokens**:

1. El cliente obtiene un token via `POST /api/v1/auth/login`.
2. El token se incluye en cada petición como `Authorization: Bearer <token>`.
3. La dependencia `get_current_user()` decodifica el JWT, extrae el `user_id` y carga el usuario desde la BD.
4. Si el token es inválido o expirado, se devuelve HTTP 401.

**Payload del JWT de acceso:**
```json
{
  "user_id": 42,
  "user_type": "usuario",
  "exp": 1714000000
}
```

**Payload del JWT de reset de contraseña:**
```json
{
  "purpose": "password_reset",
  "user_id": 42,
  "email": "user@example.com",
  "exp": 1714003600
}
```

### Hashing de Contraseñas

Se usa `passlib` con bcrypt y 12 rounds de coste:
```python
CryptContext(schemes=["bcrypt"], bcrypt__rounds=12)
```

### Aislamiento de Datos

Toda consulta a datasets, modelos y datos filtra por `user_id` del usuario autenticado. No existe ningún endpoint que retorne datos de otro usuario sin privilegios de administrador.

### Validación de Entrada

Pydantic valida automáticamente todos los cuerpos de petición y parámetros de ruta. Los errores de validación resultan en HTTP 422 con descripción detallada.

---

## 9. Flujos de Trabajo Principales

### 9.1 Flujo de Registro y Login

```
Cliente                    API                      BD
  │                          │                        │
  │──POST /auth/register──▶  │                        │
  │    {username, email,      │──SELECT email/user──▶  │
  │     password}             │◀─── no existe ─────────│
  │                          │──hash password          │
  │                          │──INSERT usuario──────▶  │
  │                          │──send_welcome_email()   │
  │◀── 201 {id, username} ───│                        │
  │                          │                        │
  │──POST /auth/login──────▶ │                        │
  │    {username, password}   │──SELECT usuario──────▶ │
  │                          │◀─── usuario ───────────│
  │                          │──verify_password()      │
  │                          │──create_access_token()  │
  │◀── 200 {access_token} ───│                        │
```

### 9.2 Flujo de Subida de Datos

```
Cliente                    API                       BD
  │                          │                         │
  │──POST /files/upload──▶   │                         │
  │   (multipart/form-data)   │                         │
  │   Authorization: Bearer   │                         │
  │                          │──get_current_user()      │
  │                          │──validate_file_type()    │
  │                          │──validate_file_size()    │
  │                          │──pd.read_csv()           │
  │                          │──validate_columns()      │
  │                          │   (detecta fecha+valor)  │
  │                          │──validate_no_duplicate() │
  │                          │──INSERT Dataset──────▶   │
  │                          │──INSERT Data×N───────▶   │
  │◀── 201 {dataset, count} ─│                         │
```

### 9.3 Flujo de Entrenamiento de Modelos

```
Cliente           API (request thread)      Background thread         BD / Disco
  │                       │                         │                      │
  │──POST /models──────▶  │                         │                      │
  │  {name, dataset_id,   │──verificar dataset────▶  │                      │
  │   model_type}         │──verificar nombre        │                      │
  │                       │──MLStorageService        │                      │
  │                       │   .create_model_dir()    │                      │
  │                       │──INSERT MLModel──────────────────────────────▶  │
  │                       │   status=en_entrenamiento                       │
  │◀── 201 {model} ───────│                         │                      │
  │                       │──add_background_task()──▶│                      │
  │  (responde <200ms)    │                         │──get_dataset_as_df() │
  │                       │                         │──train_prophet/arima │
  │                       │                         │──guardar .json/.pkl──▶│
  │                       │                         │──guardar metadata.json│
  │                       │                         │──UPDATE status────▶  │
  │                       │                         │   ="entrenado"/"error"│
```

### 9.4 Flujo de Predicción y Visualización

```
Cliente                    API                      Disco
  │                          │                         │
  │──POST /predictions/predict│                         │
  │  {model_id, periods}      │──get_current_user()     │
  │  Authorization: Bearer    │──query MLModel──────▶   │
  │                          │──check status='entrenado'│
  │                          │──[Prophet]               │
  │                          │   load .json ────────────▶│
  │                          │   make_future_dataframe() │
  │                          │   model.predict()         │
  │                          │◀── forecast ─────────────│
  │                          │                          │
  │                          │──[ARIMA]                 │
  │                          │   load .pkl ─────────────▶│
  │                          │   model.predict(n_periods)│
  │                          │   + conf_int              │
  │                          │◀── forecast ─────────────│
  │                          │                          │
  │◀── 200 {forecast[...]} ──│                         │
  │     yhat, yhat_lower,     │                         │
  │     yhat_upper, dates     │                         │
```

---

## 10. Almacenamiento de Modelos

Los modelos entrenados se organizan en el sistema de ficheros con la siguiente estructura jerárquica:

```
storage/
└── models/
    └── user_{user_id}/
        └── dataset_{dataset_id}/
            └── {model_name}/
                ├── {model_name}.json           ← Prophet (serialización JSON)
                ├── {model_name}.pkl            ← ARIMA/SARIMA (joblib pickle)
                └── {model_name}_metadata.json  ← Métricas y parámetros
```

**Ejemplo:**
```
storage/models/user_3/dataset_7/mi_modelo_prophet/
  ├── mi_modelo_prophet.json
  └── mi_modelo_prophet_metadata.json
```

**Metadatos Prophet (JSON):**
```json
{
  "model_type": "prophet",
  "longitud": 365,
  "mae": 12.45,
  "rmse": 18.32,
  "mape": 5.67
}
```

**Metadatos ARIMA/SARIMA (JSON):**
```json
{
  "model_type": "SARIMA",
  "order": [1, 1, 1],
  "seasonal_order": [1, 0, 1, 12],
  "tiene_estacionalidad": true,
  "periodo_estacional": 12,
  "aic": 1234.56,
  "bic": 1250.12,
  "rmse": 15.23,
  "mae": 10.81,
  "mape": 4.32,
  "longitud": 480
}
```

La ruta completa del directorio del modelo se almacena en el campo `model_path` de la tabla `ml_models` para recuperarlo rápidamente.

---

## 11. Stack Tecnológico

| Categoría | Tecnología | Versión / Notas |
|-----------|-----------|-----------------|
| **Framework web** | FastAPI | Async-ready, OpenAPI automático |
| **Servidor ASGI** | Uvicorn | Servidor de producción |
| **ORM** | SQLAlchemy | Mapeo objeto-relacional |
| **Base de datos** | SQLite / PostgreSQL | Configurable por `DATABASE_URL` |
| **Validación** | Pydantic v2 | Esquemas E/S, settings |
| **Autenticación** | python-jose (JWT) | Tokens HS256 |
| **Hashing** | passlib / bcrypt | 12 rounds |
| **ML — Forecasting** | Prophet (Meta) | Series con estacionalidad |
| **ML — Forecasting** | pmdarima / statsmodels | ARIMA/SARIMA con auto_arima |
| **Procesamiento datos** | pandas, numpy | DataFrames, cálculos numéricos |
| **Estadística** | scipy, statsmodels | Análisis estacional, descomposición |
| **Gráficas** | matplotlib | PNG codificado en Base64 |
| **Serialización ML** | joblib | Modelos ARIMA `.pkl` |
| **Email** | smtplib (stdlib) | SMTP/STARTTLS configurable |
| **Contenedor** | Docker + Docker Compose | Despliegue en producción |
| **Proxy inverso** | Nginx | Configurado en `nginx/default.conf` |
| **Gestión de entornos** | python-dotenv / pydantic-settings | Variables de entorno (.env) |

---

## 12. Configuración y Despliegue

### Variables de Entorno (`.env`)

| Variable | Obligatoria | Ejemplo | Descripción |
|----------|-------------|---------|-------------|
| `DATABASE_URL` | Sí | `sqlite:///./app.db` | Cadena de conexión a la BD |
| `SECRET_KEY` | Sí | `<clave aleatoria>` | Clave para firmar JWT |
| `ALGORITHM` | No | `HS256` | Algoritmo JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | Expiración de tokens de acceso |
| `PASSWORD_RESET_TOKEN_EXPIRE_MINUTES` | No | `60` | Expiración tokens de reset |
| `FRONTEND_URL` | No | `http://localhost:3000` | URL base para enlaces de email |
| `SMTP_HOST` | No | `smtp.gmail.com` | Servidor SMTP |
| `SMTP_PORT` | No | `587` | Puerto SMTP |
| `SMTP_USER` | No | `user@gmail.com` | Usuario SMTP |
| `SMTP_PASSWORD` | No | `app_password` | Contraseña/App Password SMTP |
| `SMTP_USE_TLS` | No | `False` | True para SMTP_SSL (465), False para STARTTLS (587) |
| `FROM_EMAIL` | No | `noreply@app.com` | Remitente de emails |

### Despliegue en Desarrollo

```bash
# 1. Crear entorno virtual
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate  # Linux/Mac

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con los valores apropiados

# 4. Inicializar base de datos
python rebuild_db.py

# 5. Arrancar servidor
python main.py
# API disponible en http://localhost:8000
# Docs en http://localhost:8000/docs
```

### Despliegue en Producción (Docker)

```bash
docker-compose up -d
```

El `docker-compose.yml` levanta:
- Contenedor de la aplicación FastAPI.
- Nginx como proxy inverso.

---

## 13. Pruebas

El directorio `tests/` contiene pruebas de integración con `pytest`:

- **`conftest.py`** — Fixtures compartidos: cliente de prueba, headers de autenticación, IDs de modelos y datasets de prueba.
- **`test_endpoints.py`** — Tests de todos los endpoints principales (autenticación, ficheros, modelos, predicciones).
- **`example_test.py`** — Tests de ejemplo.

Los ficheros de prueba en `setsPrueba/` cubren distintos escenarios:

| Fichero | Tipo | Descripción |
|---------|------|-------------|
| `01_VALIDO_datos_normales.csv` | Válido | Datos normales |
| `02_INVALIDO_tres_columnas.csv` | Inválido | 3 columnas |
| `03_INVALIDO_datos_faltantes.csv` | Inválido | Datos nulos |
| `04_INVALIDO_valores_texto.csv` | Inválido | Valores no numéricos |
| `06_INVALIDO_fechas_invalidas.csv` | Inválido | Fechas no parseables |
| `08_VALIDO_fechas_DD-MM-YYYY.csv` | Válido | Formato DD-MM-YYYY |
| `09_VALIDO_nombres_columnas_diferentes.csv` | Válido | Columnas con nombres personalizados |
| `11_INVALIDO_todas_fechas_iguales.csv` | Inválido | Fechas duplicadas |
| `12–15_INVALIDO_extension_*` | Inválido | Formatos no permitidos |

Para ejecutar los tests:
```bash
pytest tests/ -v
# o bien
python run_tests.py
```

---

## 14. Casos de Uso Detallados

### CU-01: Registrar cuenta y hacer login

**Actor:** Usuario nuevo  
**Precondición:** Ninguna  
**Flujo principal:**
1. Usuario envía `POST /api/v1/auth/register` con username, email y contraseña.
2. El sistema valida la fortaleza de la contraseña.
3. El sistema comprueba que no existe ya ese email ni username.
4. Se crea la cuenta y se envía email de bienvenida.
5. Usuario envía `POST /api/v1/auth/login` con username y contraseña.
6. El sistema devuelve un `access_token` JWT.

**Postcondición:** El usuario dispone de un token para hacer peticiones autenticadas.

---

### CU-02: Subir y analizar un dataset

**Actor:** Usuario autenticado  
**Precondición:** Token JWT válido  
**Flujo principal:**
1. Usuario envía `POST /api/v1/files/upload` con su fichero CSV/XLSX.
2. El sistema valida formato, tamaño, columnas, fechas y duplicados.
3. Crea el registro `Dataset` y almacena cada fila como objeto `Data`.
4. Devuelve el ID del dataset y el número de filas procesadas.
5. (Opcional) Usuario puede consultar los puntos via `GET /api/v1/datasets/id/{id}/data`.

---

### CU-03: Entrenar y consultar un modelo Prophet

**Actor:** Usuario autenticado  
**Precondición:** Dataset ya subido  
**Flujo principal:**
1. Usuario envía `POST /api/v1/models` con `{name, dataset_id, model_type: "prophet"}`.
2. El sistema crea el modelo en BD con `status="en_entrenamiento"` y responde en < 200ms.
3. En background: carga datos, entrena Prophet, guarda `.json` y metadatos.
4. Usuario consulta `GET /api/v1/models/{id}` hasta que `status="entrenado"`.
5. Puede obtener métricas de entrenamiento en `GET /api/v1/predictions/models/{id}/info`.

---

### CU-04: Generar predicciones con un modelo entrenado

**Actor:** Usuario autenticado  
**Precondición:** Modelo en estado `"entrenado"`  
**Flujo principal:**
1. Usuario envía `POST /api/v1/predictions/predict` con `{model_id, periods: 30}`.
2. El sistema detecta el tipo de modelo y delega a Prophet o ARIMA.
3. Devuelve lista de `periods` puntos: `date`, `yhat`, `yhat_lower`, `yhat_upper`.

---

### CU-05: Visualizar componentes del modelo Prophet

**Actor:** Usuario autenticado  
**Precondición:** Modelo Prophet en estado `"entrenado"`  
**Flujo principal:**
1. Usuario envía `GET /api/v1/predictions/plots/{model_id}?periods=30`.
2. El sistema carga el modelo, genera el forecast y construye figuras matplotlib.
3. Devuelve `trend_plot`, `weekly_plot` y `daily_plot` en formato `data:image/png;base64,<datos>`.
4. El cliente puede mostrar la imagen directamente en un `<img src="...">`.

---

### CU-06: Recuperar contraseña

**Actor:** Usuario registrado que olvidó su contraseña  
**Flujo principal:**
1. Usuario envía `POST /api/v1/auth/password-reset/request` con su `email`.
2. El sistema genera un token JWT de reset y envía un email con el enlace.
3. El usuario hace clic en el enlace (que contiene el token).
4. El frontend envía `POST /api/v1/auth/password-reset/confirm` con `{token, new_password}`.
5. El sistema verifica el token, valida la nueva contraseña y la actualiza en BD.

---

## 15. Decisiones de Diseño

### Por qué FastAPI

FastAPI fue elegido frente a Flask o Django REST Framework por:
- **Rendimiento**: Basado en Starlette y Uvicorn (ASGI), comparable a NodeJS.
- **Validación automática**: Pydantic integrado elimina código de validación manual.
- **Documentación automática**: OpenAPI/Swagger UI generado sin esfuerzo adicional.
- **Background tasks nativas**: `BackgroundTasks` de FastAPI permite lanzar el entrenamiento asíncrono sin necesidad de Celery.
- **Tipado**: Soporte de tipo hints de Python 3.10+.

### Por qué Prophet + ARIMA (dos modelos)

La inclusión de ambos modelos responde a sus diferentes fortalezas:

| Aspecto | Prophet | ARIMA/SARIMA |
|---------|---------|-------------|
| **Series con estacionalidad fuerte** | Excelente | Bueno (SARIMA) |
| **Series sin estacionalidad** | Aceptable | Excelente |
| **Datos escasos** | Robusto (>= 10 obs) | Requiere >= 50 obs |
| **Velocidad de entrenamiento** | Rápido | Lento (búsqueda auto_arima) |
| **Interpretabilidad** | Alta (componentes) | Alta (parámetros p,d,q) |
| **Manejo de valores atípicos** | Robusto | Sensible |

### Por qué entrenamiento en background

El entrenamiento de modelos ARIMA con `auto_arima` puede tardar varios minutos en series largas. Bloqueando el hilo HTTP durante ese tiempo se agotaría el timeout del cliente. Con `BackgroundTasks` de FastAPI:
- El cliente recibe respuesta inmediata (< 200 ms).
- El entrenamiento ocurre en un hilo separado.
- El cliente puede consultar el estado del modelo periódicamente.

### Por qué SQLAlchemy con SQLite en desarrollo

SQLite es suficiente para desarrollo y pruebas (no requiere servidor). La configuración de SQLAlchemy permite cambiar a PostgreSQL en producción con solo modificar `DATABASE_URL`, sin cambiar ningún código.

### Por qué almacenamiento en ficheros (no en BD)

Los modelos Prophet (JSON) y ARIMA (`.pkl`) pueden pesar varios MB. Almacenarlos en la BD como BLOB degradaría el rendimiento de las consultas. El sistema de ficheros es más adecuado para artefactos binarios grandes, y la ruta se almacena en BD para recuperación rápida.

---

## 16. Limitaciones y Trabajo Futuro

### Limitaciones Actuales

| Limitación | Descripción |
|------------|-------------|
| **Entrenamiento síncrono in-process** | El background task usa un hilo del mismo proceso de la app. En producción con múltiples workers, el estado de entrenamiento no se comparte entre instancias. |
| **Sin comparación directa de modelos** | No existe un endpoint que compare métricas de dos modelos en el mismo dataset. |
| **Sin reentrenamiento incremental** | Para actualizar un modelo con nuevos datos hay que eliminarlo y crear uno nuevo. |
| **Estacionalidad fija en período 12** | La detección asume datos mensuales (período=12). Datos diarios o semanales requirían lógica adicional. |
| **Sin autenticación OAuth externa** | No hay login con Google/GitHub. Solo usuario/contraseña propio. |
| **CORS abierto** | En el código actual `allow_origins=["*"]` — debe restringirse para producción. |

### Posibles Mejoras Futuras

1. **Cola de tareas (Celery + Redis)** — Para escalar el entrenamiento a múltiples workers.
2. **Reentrenamiento incremental** — Añadir nuevos datos a un modelo ya entrenado.
3. **Comparación de modelos** — Endpoint que calcule métricas cross-validation para Prophet y ARIMA sobre el mismo dataset.
4. **Detección automática de período estacional** — Usar análisis espectral (FFT) para detectar períodos distintos de 12.
5. **Exportación de predicciones** — Descargar el forecast como CSV.
6. **Almacenamiento en la nube** — Migrar `MLStorageService` a Amazon S3 o Azure Blob.
7. **Websockets** — Notificación en tiempo real del estado del entrenamiento.
8. **Frontend** — Interfaz web que consuma esta API REST.

---

*Documento generado a partir del código fuente del proyecto TFG — TimeSeriesLab. Sirve como referencia técnica para la redacción de la memoria académica.*
