"""
📊 Statistical Metrics Calculation

Computes performance metrics for predictions.

Responsibilities:
- Calculate MAE, RMSE, MAPE
- Calculate R² score
- Compare predictions to actuals
"""

from typing import List, Dict, Any
import pandas as pd


class MetricsCalculator:
    """Calculate prediction performance metrics."""
    
    # ═══════════════════════════════════════════════════════════════
    # 🎯 METRIC CALCULATIONS
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def calculate_mae(actual: List[float], predicted: List[float]) -> float:
        """
        TODO: Calculate Mean Absolute Error
        
        Formula: MAE = mean(|actual - predicted|)
        
        Args:
            actual: Actual values
            predicted: Predicted values
            
        Returns:
            MAE value
        """
        pass
    
    @staticmethod
    def calculate_rmse(actual: List[float], predicted: List[float]) -> float:
        """
        TODO: Calculate Root Mean Squared Error
        
        Formula: RMSE = sqrt(mean((actual - predicted)²))
        
        Args:
            actual: Actual values
            predicted: Predicted values
            
        Returns:
            RMSE value
        """
        pass
    
    @staticmethod
    def calculate_mape(actual: List[float], predicted: List[float]) -> float:
        """
        TODO: Calculate Mean Absolute Percentage Error
        
        Formula: MAPE = mean(|actual - predicted| / |actual|) * 100
        
        Args:
            actual: Actual values
            predicted: Predicted values
            
        Returns:
            MAPE value (percentage)
        """
        pass
    
    @staticmethod
    def calculate_r_squared(actual: List[float], predicted: List[float]) -> float:
        """
        TODO: Calculate R² Score
        
        Formula: R² = 1 - (SS_res / SS_tot)
        
        Args:
            actual: Actual values
            predicted: Predicted values
            
        Returns:
            R² value (0-1, higher is better)
        """
        pass
    
    # ═══════════════════════════════════════════════════════════════
    # 📦 BATCH CALCULATION
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def calculate_all_metrics(
        actual: List[float],
        predicted: List[float]
    ) -> Dict[str, Any]:
        """
        TODO: Calculate all metrics at once
        
        Returns:
        {
            "mae": float,
            "rmse": float,
            "mape": float,
            "r_squared": float
        }
        
        Args:
            actual: Actual values
            predicted: Predicted values
            
        Returns:
            Dict of all metrics
        """
        pass
