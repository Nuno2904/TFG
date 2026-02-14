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
    """
    
    # 🗄️ Database Configuration
    DATABASE_URL: str
    
    # 🔐 Security Configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 📱 Application Configuration
    APP_NAME: str = "TFG API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    class Config:
        """Pydantic configuration for Settings."""
        env_file = ".env"
        case_sensitive = True


# 🌍 Global settings instance
settings = Settings()
