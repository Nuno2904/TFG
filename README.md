# TimeSeriesLab — Backend API

Plataforma REST API para forecasting de series temporales con modelos de Machine Learning.

**Tecnología:** Python · FastAPI · Prophet · ARIMA/SARIMA · SQLite/PostgreSQL · Docker

---

## Qué hace este proyecto

Permite a usuarios registrados:

1. Subir datasets con series temporales (CSV o XLSX, máx. 5 MB, 2 columnas: fecha + valor).
2. Entrenar modelos Prophet o ARIMA/SARIMA (entrenamiento en background, sin bloquear el cliente).
3. Obtener predicciones futuras con intervalos de confianza del 95%.
4. Visualizar resultados mediante gráficas PNG codificadas en Base64.
5. Gestionar su perfil, cambiar contraseña y recuperarla por email.

El panel de administración permite a usuarios con rol `admin` listar, ver y eliminar usuarios, datasets y modelos.

---

## Puesta en marcha en desarrollo

```bash
# 1. Entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 2. Dependencias
pip install -r requirements.txt

# 3. Variables de entorno
cp .env.example .env
# Editar .env: DATABASE_URL, SECRET_KEY (mínimo 32 chars)

# 4. Servidor
python main.py
# API en http://localhost:8000
# Docs en http://localhost:8000/docs
```

## Despliegue en producción (Docker)

```bash
docker compose up -d --build
```

Ver [setup_server.md](setup_server.md) para la guía completa paso a paso.

---

## Variables de entorno clave (`.env`)

| Variable | Obligatoria | Descripción |
|----------|-------------|-------------|
| `DATABASE_URL` | Sí | `sqlite:///./app.db` o cadena PostgreSQL |
| `SECRET_KEY` | Sí | Clave aleatoria (≥ 32 chars) para firmar JWT |
| `ALGORITHM` | No | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` (minutos) |
| `SMTP_HOST` / `SMTP_USER` / `SMTP_PASSWORD` | No | Para emails de bienvenida y reset de contraseña |
| `FRONTEND_URL` | No | URL base para los enlaces del email de reset |

---

## Endpoints principales

**Auth:** `POST /api/v1/auth/register` · `POST /api/v1/auth/login` · `POST /api/v1/auth/request-password-reset` · `POST /api/v1/auth/reset-password`

**Usuarios:** `GET /usuarios/me` · `PUT /usuarios/me` · `PATCH /usuarios/me/username` · `POST /usuarios/me/change-password` · `DELETE /usuarios/me`

**Ficheros/Datasets:** `POST /files/upload` · `GET /files/my-files` · `DELETE /files/{id}` · `GET /datasets` · `GET /datasets/id/{id}/data`

**Modelos ML:** `POST /models` · `GET /models` · `GET /models/{id}` · `PUT /models/{id}` · `DELETE /models/{id}`

**Predicciones:** `POST /predictions/predict` · `POST /predictions/arima/predict` · `GET /predictions/models/{id}/info` · `GET /predictions/plots/{id}` · `GET /predictions/arima/plots/{id}`

**Admin:** `GET /admin/dashboard` · `GET /admin/users` · `GET /admin/users/{id}` · `DELETE /admin/users/{id}` · `DELETE /admin/datasets/{id}` · `DELETE /admin/models/{id}`

Documentación interactiva completa en `http://localhost:8000/docs`.

---

## Tests

```bash
pytest tests/ -v
pytest tests/ --cov=app --cov-report=html
```

Ver [tests/README.md](tests/README.md) para detalles de la suite de tests.

---

## Documentación

| Documento | Contenido |
|-----------|-----------|
| [Memoria.md](Memoria.md) | Documentación técnica completa del TFG (arquitectura, requisitos, decisiones de diseño) |
| [docs/api/API_DOCUMENTATION.md](docs/api/API_DOCUMENTATION.md) | Referencia detallada de todos los endpoints con ejemplos |
| [docs/guides/BACKEND_FRONTEND_INTEGRATION_GUIDE.md](docs/guides/BACKEND_FRONTEND_INTEGRATION_GUIDE.md) | Guía de integración para el equipo frontend |
| [docs/guides/setup_server.md](docs/guides/setup_server.md) | Guía de despliegue en servidor con Docker |
| [docs/guides/variasSesionesEnNav.md](docs/guides/variasSesionesEnNav.md) | sessionStorage vs localStorage y gestión multi-sesión |
| [docs/ml/CAMBIOS_ARIMA_SARIMA.md](docs/ml/CAMBIOS_ARIMA_SARIMA.md) | Implementación de la detección automática ARIMA/SARIMA |
| [docs/ml/MAERMSEMAPE.md](docs/ml/MAERMSEMAPE.md) | Explicación de métricas de evaluación (MAE, RMSE, MAPE) |
| [docs/CambiosGordos.md](docs/CambiosGordos.md) | Historial de cambios del proyecto |
| [docs/bibliografia.md](docs/bibliografia.md) | Bibliografía académica (formato APA 7ª ed.) |
| [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md) | Diseño del sistema, componentes y flujo de datos |
| [docs/api/ENDPOINTS.md](docs/api/ENDPOINTS.md) | Documentación completa de endpoints con ejemplos cURL |
| [docs/guides/USAGE_GUIDE.md](docs/guides/USAGE_GUIDE.md) | Guía paso a paso para usuarios finales |
| [setsPrueba/README.md](setsPrueba/README.md) | Descripción de los datasets de prueba para validación |
| [setsPrueba/README_COMPARACION_PROPHET_ARIMA.md](setsPrueba/README_COMPARACION_PROPHET_ARIMA.md) | Comparación empírica Prophet vs ARIMA con datasets específicos |
