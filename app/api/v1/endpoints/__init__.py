"""API endpoints module exports."""

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.usuarios import router as usuarios_router
from app.api.v1.endpoints.files import router as files_router
from app.api.v1.endpoints.datasets import router as datasets_router
from app.api.v1.endpoints.ml import router as ml_router

__all__ = ["auth_router", "usuarios_router", "files_router", "datasets_router", "ml_router"]
