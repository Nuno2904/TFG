"""
🔮 Prediction ORM Model

Represents a machine learning prediction job result.

Responsibilities:
- Store prediction job metadata and status
- Track what model was used and its parameters
- Store execution time and errors
- Relate to dataset and prediction results
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.base import DeclarativeBase


class Prediction(DeclarativeBase):
    """
    Prediction ORM Model
    
    Represents a prediction job: running a ML model on a dataset.
    
    Attributes:
        id: Primary key
        dataset_id: FK to Dataset used for prediction
        model_id: FK to PredictionModel used
        user_id: FK to User who requested prediction
        prediction_name: User-given name for this prediction
        model_parameters: Hyperparameters used (JSON)
        forecast_periods: Number of periods forecasted ahead
        confidence_level: Confidence interval level (0-1)
        status: Job status (pending, processing, completed, failed)
        error_message: Error message if failed
        execution_time_seconds: How long prediction took
        created_at: Job creation time
        completed_at: Job completion time
    
    Relationships:
        - dataset: Dataset used
        - model: Model used
        - user: User who requested
        - results: Prediction results
        - metrics: Performance metrics
    """
    
    __tablename__ = "prediction"
    
    # ═══════════════════════════════════════════════════════════════
    # 🔑 PRIMARY KEY
    # ═══════════════════════════════════════════════════════════════
    
    id = Column(Integer, primary_key=True, index=True)
    
    # ═══════════════════════════════════════════════════════════════
    # 🔗 FOREIGN KEYS
    # ═══════════════════════════════════════════════════════════════
    
    dataset_id = Column(Integer, ForeignKey("dataset.id", ondelete="CASCADE"), nullable=False)
    model_id = Column(Integer, ForeignKey("prediction_model.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    
    # ═══════════════════════════════════════════════════════════════
    # 📝 PREDICTION METADATA
    # ═══════════════════════════════════════════════════════════════
    
    prediction_name = Column(String(255), nullable=True)
    # TODO: Optionally: Default to "model_name_dataset_name_timestamp"
    
    # ═══════════════════════════════════════════════════════════════
    # 🎛️ MODEL CONFIGURATION
    # ═══════════════════════════════════════════════════════════════
    
    model_parameters = Column(JSON, nullable=True)
    # Example: {"p": 1, "d": 1, "q": 1} for ARIMA
    
    forecast_periods = Column(Integer, nullable=False)
    confidence_level = Column(Float, default=0.95, nullable=False)
    
    # ═══════════════════════════════════════════════════════════════
    # 📊 EXECUTION STATUS
    # ═══════════════════════════════════════════════════════════════
    
    status = Column(String(50), default="pending", nullable=False)
    # TODO: Use PredictionStatus enum
    
    error_message = Column(Text, nullable=True)
    execution_time_seconds = Column(Float, nullable=True)
    
    # ═══════════════════════════════════════════════════════════════
    # ⏰ TIMESTAMPS
    # ═══════════════════════════════════════════════════════════════
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # ═══════════════════════════════════════════════════════════════
    # 🔗 RELATIONSHIPS
    # ═══════════════════════════════════════════════════════════════
    
    # TODO: Relationship to Dataset
    dataset = relationship("Dataset", back_populates="predictions")
    
    # TODO: Relationship to PredictionModel -> model_config.py
    model = relationship("PredictionModel", back_populates="predictions")
    
    # TODO: Relationship to User
    user = relationship("Usuario", back_populates="predictions")
    
    # TODO: Relationship to PredictionResult (back_populates="prediction")
   # results = relationship("PredictionResult", back_populates="prediction")
    
    # TODO: Relationship to PredictionMetric (back_populates="prediction") -> para metric.py
    metrics = relationship("PredictionMetric", back_populates="predictions")
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<Prediction(id={self.id}, status={self.status}, model_id={self.model_id})>"
