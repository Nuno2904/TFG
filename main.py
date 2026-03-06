"""
🚀 FastAPI Application Factory

Main application initialization and configuration.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.db import init_db
from app.api.v1 import router as api_v1_router


# 📋 Setup Logging
logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


# ═══════════════════════════════════════════════════════════════════════════
# 🔄 Application Lifespan
# ═══════════════════════════════════════════════════════════════════════════


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown events.
    
    Startup:
    - Initialize database tables
    
    Shutdown:
    - Cleanup resources if needed
    """
    # 🟢 Startup
    logger.info("🚀 Starting up application...")
    try:
        init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    yield
    
    # 🔴 Shutdown
    logger.info("🛑 Shutting down application...")


# ═══════════════════════════════════════════════════════════════════════════
# 🏗️ Application Factory
# ═══════════════════════════════════════════════════════════════════════════


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application instance
    """
    
    # 📦 Create app instance
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="🎯 Modern FastAPI application with user management and authentication",
        lifespan=lifespan,
    )
    
    # 🌐 CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # ⚠️ Configure for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 📡 Include routers
    app.include_router(api_v1_router)
    
    # 🏥 Health check
    @app.get(
        "/health",
        tags=["🏥 Health"],
        summary="Health Check",
        description="Check if the API is running"
    )
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "✅ healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION
        }
    
    # 📖 Root endpoint
    @app.get(
        "/",
        tags=["📖 Info"],
        summary="API Information",
        description="Get API information and documentation links"
    )
    async def root():
        """
        Root endpoint with API information.
        
        Visit `/docs` for interactive API documentation (Swagger UI)
        Visit `/redoc` for ReDoc documentation
        """
        return {
            "message": f"👋 Welcome to {settings.APP_NAME}",
            "version": settings.APP_VERSION,
            "docs": {
                "swagger": "/docs",
                "redoc": "/redoc",
                "openapi": "/openapi.json"
            }
        }
    
    logger.info(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} application created")
    
    return app


# 🌍 Create application instance
app = create_app()
