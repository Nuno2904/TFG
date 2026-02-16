"""
📈 Facebook Prophet Model Implementation

Implements BasePredictionModel for Prophet library.

Responsibilities:
- Implement fit and predict for Prophet
- Handle Prophet-specific parameters
- Format data for Prophet API
"""

from typing import Dict, Any, Tuple, List
import pandas as pd

from app.ml.models.base_model import BasePredictionModel
# TODO: from prophet import Prophet


class ProphetModel(BasePredictionModel):
    """
    Prophet time series model implementation.
    
    Default parameters:
    - seasonality_mode: 'additive'
    - interval_width: 0.95
    - yearly_seasonality: True
    - weekly_seasonality: True
    - daily_seasonality: False
    """
    
    def __init__(self, parameters: Dict[str, Any] = None):
        """
        TODO: Initialize Prophet model
        
        Steps:
        1. Call super().__init__(parameters)
        2. Initialize Prophet instance with parameters:
           - yearly_seasonality from params or default True
           - weekly_seasonality from params or default True
           - daily_seasonality from params or default False
           - interval_width from params or default 0.95
        3. Store as self.model
        """
        pass
    
    def fit(self, data: pd.DataFrame) -> None:
        """
        TODO: Train Prophet model on data
        
        Steps:
        1. Validate data using self.validate_data()
        2. Prepare data for Prophet:
           - Rename columns to 'ds' (date) and 'y' (value)
           - Ensure datetime type for dates
        3. Call self.model.fit(prepared_data)
        4. Set self.is_fitted = True
        5. Handle any exceptions
        """
        pass
    
    def predict(self, periods: int) -> Tuple[List[float], List[float], List[float]]:
        """
        TODO: Generate forecast using Prophet
        
        Steps:
        1. Check if self.is_fitted is True
        2. Create future DataFrame for 'periods' ahead
        3. Call self.model.predict(future)
        4. Extract:
           - Point forecasts from 'yhat' column
           - Upper CI from 'yhat_upper' column
           - Lower CI from 'yhat_lower' column
        5. Return as (predictions, upper, lower) lists
        """
        pass
    
    def get_model_name(self) -> str:
        """Return model name."""
        return "Prophet"
