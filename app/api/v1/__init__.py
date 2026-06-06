"""API v1 routes."""

from fastapi import APIRouter
from app.api.v1.endpoints import auth_router, usuarios_router, files_router, datasets_router, ml_router, predictions_router, admin_router

router = APIRouter(prefix="/api/v1")

# 📡 Include all routers
router.include_router(auth_router)
router.include_router(usuarios_router)
router.include_router(files_router)
router.include_router(datasets_router)
router.include_router(ml_router)
router.include_router(predictions_router)
router.include_router(admin_router)

__all__ = ["router"]
