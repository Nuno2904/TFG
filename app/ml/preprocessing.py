"""
📊 Data Preprocessing Utilities

Handles data cleaning, normalization, and preparation for ML models.

Responsibilities:
- Clean time series data
- Handle missing values
- Normalize/denormalize if needed
- Resample time series
"""

import pandas as pd
from typing import Tuple


class DataPreprocessor:
    """Preprocessing utilities for time series data."""
    
    # ═══════════════════════════════════════════════════════════════
    # 🧹 DATA CLEANING
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        TODO: Clean and prepare data
        
        Steps:
        1. Remove rows with NaN values
        2. Remove duplicates based on date
        3. Sort by date ascending
        4. Ensure numeric values
        5. Handle outliers if needed
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        pass
    
    # ═══════════════════════════════════════════════════════════════
    # 📈 MISSING VALUES
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def handle_missing_values(df: pd.DataFrame, method: str = "interpolate") -> pd.DataFrame:
        """
        TODO: Handle missing values
        
        Methods:
        - "interpolate": Linear interpolation
        - "forward_fill": Last observation forward
        - "drop": Remove rows with NaN
        
        Args:
            df: DataFrame with potential NaN
            method: Handling method
            
        Returns:
            DataFrame with missing values handled
        """
        pass
    
    # ═══════════════════════════════════════════════════════════════
    # 📊 NORMALIZATION
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def normalize(data: pd.Series) -> Tuple[pd.Series, float, float]:
        """
        TODO: Normalize data (0-1 scaling)
        
        Also return min/max for denormalization
        
        Args:
            data: Data to normalize
            
        Returns:
            Tuple of (normalized_data, min_val, max_val)
        """
        pass
    
    @staticmethod
    def denormalize(normalized_data: pd.Series, min_val: float, max_val: float) -> pd.Series:
        """
        TODO: Reverse normalization
        
        Args:
            normalized_data: Normalized values
            min_val: Original min
            max_val: Original max
            
        Returns:
            Denormalized data
        """
        pass
    
    # ═══════════════════════════════════════════════════════════════
    # 📅 RESAMPLING
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def resample_data(df: pd.DataFrame, frequency: str, method: str = "mean") -> pd.DataFrame:
        """
        TODO: Resample time series to different frequency
        
        Example: Daily data to weekly average
        
        Args:
            df: DataFrame with datetime index
            frequency: Target frequency (D, H, W, M)
            method: Aggregation method (mean, sum, last, first)
            
        Returns:
            Resampled DataFrame
        """
        pass
