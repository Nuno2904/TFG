"""
🌱 Database Initialization & Seeding

Creates database tables and optionally seeds initial data.

Responsibilities:
- Initialize database schema
- Optionally create default data (models, admin users, etc.)
- Handle migration strategies
"""

from sqlalchemy.orm import Session

from app.db.base import init_db as base_init_db
from app.models import PredictionModel
from app.core.constants import ModelType


def init_db_with_defaults(db: Session) -> None:
    """
    Initialize database with default data.
    
    TODO: Implement:
    - Create prediction models (Prophet, ARIMA)
    - Store default model configurations
    - Create any other seed data needed
    
    Args:
        db: Database session
    """
    # TODO: Check if default models exist
    # TODO: If not, create them:
    #   - PredictionModel(name=ModelType.PROPHET, ...)
    #   - PredictionModel(name=ModelType.ARIMA, ...)
    pass


def reset_db(db: Session) -> None:
    """
    Delete all data AND tables (for development/testing only).
    
    WARNING: This is destructive and should only be used in dev/test.
    
    TODO: Implement:
    - Drop all tables
    - Recreate tables
    """
    # TODO: Use DeclarativeBase.metadata.drop_all()
    # TODO: Then call base_init_db()
    pass
