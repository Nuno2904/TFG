"""
📈 PredictionMetric ORM Model

Stores statistical performance metrics for predictions.

Responsibilities:
- Store calculated metrics (MAE, RMSE, MAPE, R², etc.)
- Link metrics to their corresponding prediction
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import DeclarativeBase


class PredictionMetric(DeclarativeBase):
    """
    PredictionMetric ORM Model
    
    Stores statistical metrics calculated for a prediction.
    
    Attributes:
        id: Primary key
        prediction_id: FK to Prediction
        metric_name: Name of metric (mae, rmse, mape, r_squared)
        metric_value: Calculated metric value
    
    Relationships:
        - prediction: Prediction this metric belongs to
    """
    
    __tablename__ = "prediction_metric"
    
    # ═══════════════════════════════════════════════════════════════
    # 🔑 PRIMARY KEY
    # ═══════════════════════════════════════════════════════════════
    
    id = Column(Integer, primary_key=True, index=True)
    
    # ═══════════════════════════════════════════════════════════════
    # 🔗 FOREIGN KEY
    # ═══════════════════════════════════════════════════════════════
    
    prediction_id = Column(Integer, ForeignKey("prediction.id", ondelete="CASCADE"), nullable=False)
    
    # ═══════════════════════════════════════════════════════════════
    # 📊 METRIC DATA
    # ═══════════════════════════════════════════════════════════════
    
    metric_name = Column(String(100), nullable=False)
    # TODO: Should use constant from core/constants.py AVAILABLE_METRICS
    # Examples: "mae", "rmse", "mape", "r_squared"
    
    metric_value = Column(Float, nullable=False)
    
    # ═══════════════════════════════════════════════════════════════
    # 🔗 RELATIONSHIPS
    # ═══════════════════════════════════════════════════════════════
    
    # TODO: Relationship to Prediction (back_populates="metrics")
    predictions = relationship("Prediction", back_populates="metrics")
    
    # ═══════════════════════════════════════════════════════════════
    # 🔒 CONSTRAINTS
    # ═══════════════════════════════════════════════════════════════
    
    __table_args__ = (
        UniqueConstraint("prediction_id", "metric_name", name="uq_prediction_metric"),
    )
    # TODO: Ensure only one value per metric per prediction
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<PredictionMetric(prediction_id={self.prediction_id}, metric={self.metric_name})>"
