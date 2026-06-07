"""
🤖 ML Model (Machine Learning Model) database table.

Stores information about ML models created by users:
- User who created it (FK to usuarios)
- Model name and creation date
- Model file path
- Training status (trained/training/error)
- Associated dataset used for training (FK to datasets)
- Error information if training failed
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from typing import TYPE_CHECKING, List
import enum

if TYPE_CHECKING:
    from app.models.usuario import Usuario
    from app.models.dataset import Dataset


class ModelType(str, enum.Enum):
    """Enum for available ML model types."""
    PROPHET = "prophet"
    ARIMA = "arima"


class ModelStatus(str, enum.Enum):
    """Enum for model training status."""
    TRAINED = "entrenado"
    TRAINING = "en_entrenamiento"
    ERROR = "error"


class MLModel(Base):
    """
    MLModel database model.
    
    Represents a machine learning model trained by a user using a specific dataset.
    
    Attributes:
        id: Primary key - unique model identifier
        user_id: Foreign key referencing the user who created the model
        dataset_id: Foreign key referencing the dataset used for training
        name: Name of the ML model
        model_type: Type of ML model (prophet, arima, etc)
        created_at: Timestamp of model creation
        model_path: Path where the model file is stored
        status: Current status of the model (trained/training/error)
        error_message: Error details if training failed (nullable)
    """
    
    __tablename__ = "ml_models"
    
    # 🔑 Primary Key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        doc="Unique ML model identifier"
    )
    
    # 🔗 Foreign Key to Usuario
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=False,
        doc="Foreign key referencing the user who created the model"
    )
    
    # 🔗 Foreign Key to Dataset
    dataset_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("datasets.id"),
        nullable=False,
        doc="Foreign key referencing the dataset used for training"
    )
    
    # 📝 Model Name
    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="Name of the ML model"
    )
    
    # 🤖 Model Type
    model_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="prophet",
        doc="Type of ML model (prophet, arima, etc)"
    )
    
    # ⏰ Creation Timestamp
    # ⏰ Creation Timestamp
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        doc="Model creation timestamp"
    )
    
    # 📂 Model Path
    model_path: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="File path where the model is stored"
    )
    
    # 📊 Model Status
    status: Mapped[str] = mapped_column(
        String,
        default=ModelStatus.TRAINING.value,
        nullable=False,
        doc="Model status: entrenado, en_entrenamiento, or error"
    )
    
    # ⚠️ Error Message (nullable)
    error_message: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
        doc="Error details if training failed"
    )

    # ⚠️ Low Data Warning (Prophet only)
    low_data_warning: Mapped[bool] = mapped_column(
        Boolean,
        nullable=True,
        default=False,
        doc="True if model was trained with fewer than 24 observations — predictions may not be reliable"
    )
    
    # 🔄 Relationships
    usuario: Mapped["Usuario"] = relationship(
        "Usuario",
        back_populates="ml_models",
        doc="Relationship to the user who created the model"
    )
    
    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        back_populates="ml_models",
        doc="Relationship to the dataset used for training"
    )
    
    def __repr__(self) -> str:
        """String representation of MLModel object."""
        return f"<MLModel(id={self.id}, name='{self.name}', status='{self.status}', user_id={self.user_id})>"

