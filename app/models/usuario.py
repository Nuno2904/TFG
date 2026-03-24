"""
👤 Usuario (User) Model

SQLAlchemy ORM model for user database table.
Defines user structure with email, password, and type fields.
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.dataset import Dataset
    from app.models.ml import MLModel


class Usuario(Base):
    """
    Usuario database model.
    
    Represents a user in the system with authentication and type information.
    
    Attributes:
        id: Primary key - unique user identifier
        email: User email address (unique, required)
        password: Hashed password (required)
        tipo: User type - "usuario" or "admin" (required)
        created_at: Timestamp of user creation (auto-generated)
    """
    
    __tablename__ = "usuarios"
    
    # 🔑 Primary Key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        doc="Unique user identifier"
    )
    
    # � Username
    username: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        doc="Unique username"
    )

    # �📧 Email
    email: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
        index=True,
        doc="User email address"
    )
    
    # 🔒 Password
    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Hashed password"
    )
    
    # 👨‍💼 User Type
    tipo: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="usuario",
        doc="User type: 'usuario' or 'admin'"
    )
    
    # ⏰ Timestamps
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        doc="User creation timestamp"
    )
    
    
    
    datasets: Mapped[List["Dataset"]] = relationship(
        "Dataset",
        back_populates="usuario",
        cascade="all, delete-orphan",
        doc="Datasets uploaded by this user"
    )
    
    ml_models: Mapped[List["MLModel"]] = relationship(
        "MLModel",
        back_populates="usuario",
        cascade="all, delete-orphan",
        doc="ML models created by this user"
    )
    
    
    def __repr__(self) -> str:
        """String representation of Usuario object."""
        return f"<Usuario(id={self.id}, email='{self.email}', tipo='{self.tipo}')>"
