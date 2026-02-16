"""
📊 ARIMA Model Implementation

Implements BasePredictionModel for ARIMA (Auto ARIMA or manual).

Responsibilities:
- Implement fit and predict for ARIMA
- Handle p, d, q parameters
- Format data for ARIMA
"""

from typing import Dict, Any, Tuple, List
import pandas as pd

from app.ml.models.base_model import BasePredictionModel
# TODO: from statsmodels.tsa.statespace.sarimax import SARIMAX
# TODO: from statsmodels.tsa.arima.auto_arima import auto_arima (optional for auto detection)


class ARIMAModel(BasePredictionModel):
    """
    ARIMA time series model implementation.
    
    Parameters:
    - p: AutoRegressive order
    - d: Integrated (differencing) order
    - q: Moving Average order
    
    Can use manual (p,d,q) or auto_arima for auto-detection.
    """
    
    def __init__(self, parameters: Dict[str, Any] = None):
        """
        TODO: Initialize ARIMA model
        
        Steps:
        1. Call super().__init__(parameters)
        2. Extract p, d, q from parameters or use defaults (1,1,1)
        3. Store order as self.order = (p, d, q)
        4. Initialize self.model = None (will be created in fit())
        """
        pass
    
    def fit(self, data: pd.DataFrame) -> None:
        """
        TODO: Train ARIMA model on data
        
        Steps:
        1. Validate data
        2. Extract value column as 1D array
        3. Create SARIMAX model with self.order
        4. Call fit() on model
        5. Set self.is_fitted = True
        
        Note: Using SARIMAX with seasonal=False gives ARIMA behavior
        """
        pass
    
    def predict(self, periods: int) -> Tuple[List[float], List[float], List[float]]:
        """
        TODO: Generate forecast using ARIMA
        
        Steps:
        1. Check if self.is_fitted
        2. Get forecast using:
           - get_forecast(steps=periods)
           - .summary_frame()
        3. Extract mean predictions
        4. Extract confidence interval bounds
        5. Return as (predictions, upper, lower)
        """
        pass
    
    def get_model_name(self) -> str:
        """Return model name with ARIMA order."""
        # TODO: Return f"ARIMA{self.order}" or similar
        pass
