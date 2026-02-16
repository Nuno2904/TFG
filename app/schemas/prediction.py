"""
🔮 Prediction Pydantic Schemas

Request/response validation for prediction endpoints.

Responsibilities:
- Validate prediction creation requests
- Define response shapes
- Validate model parameters
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class PredictionCreate(BaseModel):
    """
    TODO: Schema for creating a new prediction
    
    Should include:
    - dataset_id: Which dataset to predict on
    - model_id: Which model to use
    - model_parameters: Hyperparameters (optional, use defaults)
    - forecast_periods: How many periods ahead (optional)
    - confidence_level: CI level (optional)
    - prediction_name: User-given name (optional)
    """
    
    dataset_id: int = Field(..., description="Dataset ID to predict on")
    model_id: int = Field(..., description="Model ID to use")
    model_parameters: Optional[Dict[str, Any]] = Field(None, description="Hyperparameters")
    forecast_periods: Optional[int] = Field(None, ge=1, description="Periods ahead to forecast")
    confidence_level: Optional[float] = Field(0.95, ge=0.5, le=0.99)
    prediction_name: Optional[str] = None


class PredictionResult(BaseModel):
    """
    TODO: Single prediction result point
    
    Should include:
    - period_index: 0, 1, 2... n ahead
    - forecast_date: Predicted timestamp
    - predicted_value: Forecast value
    - upper_confidence_bound: Upper CI
    - lower_confidence_bound: Lower CI
    """
    
    period_index: int
    forecast_date: datetime
    predicted_value: float
    upper_confidence_bound: float
    lower_confidence_bound: float


class PredictionMetric(BaseModel):
    """Single metric result."""
    
    metric_name: str = Field(..., description="MAE, RMSE, MAPE, R_SQUARED")
    metric_value: float


class PredictionOut(BaseModel):
    """
    Response schema for prediction.
    
    TODO: Include:
    - id, dataset_id, model_id
    - prediction_name, status
    - model_parameters used
    - forecast_periods, confidence_level
    - execution_time_seconds
    - error message if failed
    - timestamps
    """
    
    id: int
    dataset_id: int
    model_id: int
    user_id: int
    prediction_name: Optional[str] = None
    status: str
    model_parameters: Optional[Dict[str, Any]] = None
    forecast_periods: int
    confidence_level: float
    error_message: Optional[str] = None
    execution_time_seconds: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class PredictionDetailOut(PredictionOut):
    """
    Detailed prediction response with results and metrics.
    
    TODO: Include:
    - All fields from PredictionOut
    - results: List[PredictionResult]
    - metrics: List[PredictionMetric]
    """
    
    results: List[PredictionResult] = Field(default_factory=list)
    metrics: List[PredictionMetric] = Field(default_factory=list)
