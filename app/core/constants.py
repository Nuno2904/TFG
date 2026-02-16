"""
⚙️ Application Constants & Enumerations

Centralized constants used throughout the application.
Prevents magic strings and improves maintainability.
"""

from enum import Enum


class ModelType(str, Enum):
    """
    Available time series prediction models.
    
    Responsibilities:
    - Define all supported model types
    - Provide human-readable names
    """
    
    PROPHET = "prophet"
    ARIMA = "arima"
    # TODO: Add more models as needed (LSTM, Exponential Smoothing, etc.)


class DatasetStatus(str, Enum):
    """Dataset lifecycle status."""
    
    ACTIVE = "active"           # Available for use
    ARCHIVED = "archived"       # Hidden but not deleted
    DELETED = "deleted"         # Soft deleted
    # TODO: Add processing status if needed


class PredictionStatus(str, Enum):
    """Prediction job status."""
    
    PENDING = "pending"         # Queued but not started
    PROCESSING = "processing"   # Currently running
    COMPLETED = "completed"     # Successfully finished
    FAILED = "failed"           # Error occurred
    # TODO: Add CANCELLED status if async jobs can be cancelled


class FrequencyType(str, Enum):
    """Time series frequency types."""
    
    DAILY = "D"
    HOURLY = "H"
    WEEKLY = "W"
    MONTHLY = "M"
    YEARLY = "Y"
    # TODO: Add more frequencies as needed (T=minute, H_INTERVALS, etc.)


# 📊 Metric definitions
AVAILABLE_METRICS = [
    "mae",       # Mean Absolute Error
    "rmse",      # Root Mean Square Error
    "mape",      # Mean Absolute Percentage Error
    "r_squared", # Coefficient of determination
    # TODO: Add more metrics (mase, smape, etc.)
]

# 🎯 Error messages
ERROR_MESSAGES = {
    "FILE_NOT_FOUND": "Uploaded file not found in storage",
    "INVALID_CSV": "Invalid CSV format or structure",
    "INSUFFICIENT_DATA": "Dataset has insufficient historical data for prediction",
    "MODEL_NOT_FOUND": "Requested model is not available",
    "PREDICTION_FAILED": "Prediction generation failed",
    # TODO: Add more error messages as needed
}
