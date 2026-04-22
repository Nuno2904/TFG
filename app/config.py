"""
⚙️ Configuration Module

Centralized environment variable management using Pydantic BaseSettings.
Loads configuration from .env file and system environment variables.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Attributes:
        - Database configuration
        - JWT/Security tokens
        - Application metadata
        - Email / SMTP
    """
    
    # 🗄️ Database Configuration
    DATABASE_URL: str
    
    # 🔐 Security Configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 60
    
    # 📂 Storage Configuration
    STORAGE_PATH: str = "storage"
    MODEL_STORAGE_PATH: str = "storage/models"
    
    # 📱 Application Configuration
    APP_NAME: str = "TFG API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 🌐 Frontend URL (used in password-reset links)
    FRONTEND_URL: str = "http://91.9.101.47:81"
    
    # 📧 SMTP / Email Configuration
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = False   # True = SMTP_SSL (port 465); False = STARTTLS (port 587)
    FROM_EMAIL: Optional[str] = None
    
    class Config:
        """Pydantic configuration for Settings."""
        env_file = ".env"
        case_sensitive = True


# 🌍 Global settings instance
settings = Settings()
