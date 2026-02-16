"""
🎛️ PredictionModel ORM Model

Represents available machine learning models (Prophet, ARIMA).

Responsibilities:
- Store available model definitions
- Store default hyperparameters schema
- Track model availability and metadata
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship

from app.db.base import DeclarativeBase


class PredictionModel(DeclarativeBase):
    """
    PredictionModel ORM Model
    
    Represents available ML models for time series forecasting.
    
    Attributes:
        id: Primary key
        name: Machine name (prophet, arima)
        display_name: Human-readable name (Prophet, Auto ARIMA)
        description: Model description
        parameters_schema: JSON schema for model hyperparameters
        is_active: Whether model is available for use
        created_at: Creation timestamp
    
    Relationships:
        - predictions: Predictions using this model
    """
    
    __tablename__ = "prediction_model"
    
    # ═══════════════════════════════════════════════════════════════
    # 🔑 PRIMARY KEY
    # ═══════════════════════════════════════════════════════════════
    
    id = Column(Integer, primary_key=True, index=True)
    
    # ═══════════════════════════════════════════════════════════════
    # 📝 MODEL INFORMATION
    # ═══════════════════════════════════════════════════════════════
    
    name = Column(String(100), unique=True, nullable=False)
    # Example: "prophet", "arima"
    
    display_name = Column(String(200), nullable=True)
    # Example: "Facebook Prophet", "ARIMA (Auto)"
    
    description = Column(Text, nullable=True)
    # Detailed description and use cases
    
    # ═══════════════════════════════════════════════════════════════
    # ⚙️ CONFIGURATION
    # ═══════════════════════════════════════════════════════════════
    
    parameters_schema = Column(JSON, nullable=True)
    # TODO: Example for ARIMA:
    # {
    #   "p": {"type": "integer", "min": 0, "max": 5, "default": 1},
    #   "d": {"type": "integer", "min": 0, "max": 2, "default": 1},
    #   "q": {"type": "integer", "min": 0, "max": 5, "default": 1}
    # }
    
    is_active = Column(Boolean, default=True, nullable=False)
    
    # ═══════════════════════════════════════════════════════════════
    # ⏰ METADATA
    # ═══════════════════════════════════════════════════════════════
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # ═══════════════════════════════════════════════════════════════
    # 🔗 RELATIONSHIPS
    # ═══════════════════════════════════════════════════════════════
    
    # TODO: Relationship to Prediction (back_populates="model")
    predictions = relationship("Prediction", back_populates="model")
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<PredictionModel(id={self.id}, name={self.name})>"
