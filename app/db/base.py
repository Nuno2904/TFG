"""
🗄️ Database Base Configuration

Centralized database setup including:
- SQLAlchemy declarative base
- Engine initialization
- Session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from app.config import settings


class Base(DeclarativeBase):
    """
    SQLAlchemy declarative base for all ORM models.
    
    All model classes inherit from this to enable:
    - Automatic table creation
    - ORM session management
    - Query operations
    """
    pass


# 🔌 Database engine initialization
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Show SQL queries in debug mode
    pool_pre_ping=True,  # Validate connections before use
)


# 📋 Create all tables from models
def init_db() -> None:
    """Initialize database by creating all tables defined in models."""
    Base.metadata.create_all(bind=engine)
