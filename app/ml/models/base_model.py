"""
🔧 Base ML Model

Abstract base class for all prediction models.

Responsibilities:
- Define common interface all models must implement
- Force implementation of key methods
- Store common data and parameters
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple
import pandas as pd


class BasePredictionModel(ABC):
    """
    Abstract base class for time series prediction models.
    
    All concrete models (Prophet, ARIMA) inherit from this.
    
    Responsibilities:
    - Define contract that all models must fulfill
    - Store training data
    - Provide common attributes
    """
    
    def __init__(self, parameters: Dict[str, Any] = None):
        """
        TODO: Initialize base model
        
        Stores:
        - parameters: Hyperparameters dict
        - model: The actual ML model instance (initialized by subclass)
        - is_fitted: Boolean tracking if model is trained
        
        Args:
            parameters: Model hyperparameters dict
        """
        self.parameters = parameters or {}
        self.model = None
        self.is_fitted = False
    
    # ═══════════════════════════════════════════════════════════════
    # 🎯 REQUIRED ABSTRACT METHODS
    # ═══════════════════════════════════════════════════════════════
    
    @abstractmethod
    def fit(self, data: pd.DataFrame) -> None:
        """
        TODO: Train model on historical data
        
        Each subclass must implement:
        - Load data into model-specific format
        - Train/fit the model
        - Set self.is_fitted = True
        - Handle any training errors
        
        Args:
            data: Historical time series DataFrame
                 Must have datetime index and value column
        
        Raises:
            TODO: Appropriate exceptions on training failure
        """
        pass
    
    @abstractmethod
    def predict(self, periods: int) -> Tuple[List[float], List[float], List[float]]:
        """
        TODO: Generate forecast
        
        Each subclass must implement:
        - Create forecast for specified periods ahead
        - Return predictions with confidence intervals
        
        Args:
            periods: Number of periods ahead to forecast
            
        Returns:
            Tuple of (predictions, upper_ci, lower_ci)
            Where each is a list of floats
            
        Raises:
            TODO: ModelNotFittedError
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """
        TODO: Return human-readable model name
        
        Returns:
            String like "Prophet" or "ARIMA(1,1,1)"
        """
        pass
    
    # ═══════════════════════════════════════════════════════════════
    # 📊 UTILITY METHODS (optional to override)
    # ═══════════════════════════════════════════════════════════════
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        TODO: Validate input data has minimum requirements
        
        Checks:
        - Has at least MIN_HISTORICAL_PERIODS rows
        - Has datetime index
        - Has numeric values
        
        Args:
            data: DataFrame to validate
            
        Returns:
            True if valid, raises exception otherwise
        """
        pass
