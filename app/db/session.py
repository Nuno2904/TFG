"""
🔗 Database Session Management

Provides session factory and dependency for FastAPI.
Ensures each request gets an isolated database session.
"""

from sqlalchemy.orm import sessionmaker, Session
from app.db.base import engine


# 📦 Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Session:
    """
    Dependency to provide database session to endpoints.
    
    Yields:
        Session: SQLAlchemy database session
        
    Note:
        Automatically closes session after request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
