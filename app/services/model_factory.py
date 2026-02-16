"""
🏭 Model Factory

Creates appropriate ML model instances based on model type.

Responsibilities:
- Instantiate correct model class
- Pass hyperparameters to models
- Provide interface to get available models
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from app.core.constants import ModelType
# TODO: Import from app.ml.models import BasePredictionModel, ProphetModel, ARIMAModel


class ModelFactory:
    """
    Factory for creating ML model instances.
    """
    
    # ═══════════════════════════════════════════════════════════════
    # 🏗️ MODEL CREATION
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def create_model(model_type: str, parameters: Dict[str, Any] = None):
        """
        TODO: Create model instance based on type
        
        Logic:
        1. Validate model_type is in ModelType enum
        2. If parameters is None, use defaults
        3. Create appropriate model class instance:
           - ModelType.PROPHET → ProphetModel(**parameters)
           - ModelType.ARIMA → ARIMAModel(**parameters)
        4. Return model instance
        
        Args:
            model_type: String model type (prophet, arima)
            parameters: Dict of hyperparameters or None for defaults
            
        Returns:
            Model instance (subclass of BasePredictionModel)
            
        Raises:
            TODO: ModelNotFoundError, InvalidParametersError
        """
        pass
    
    # ═══════════════════════════════════════════════════════════════
    # ℹ️ MODEL INFORMATION
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def get_available_models(db: Session) -> list:
        """
        TODO: Get list of available models from database
        
        Args:
            db: Database session
            
        Returns:
            List of PredictionModel instances where is_active=True
        """
        pass
    
    @staticmethod
    def get_model_defaults(model_type: str) -> Dict[str, Any]:
        """
        TODO: Get default hyperparameters for model type
        
        Returns default values for:
        - Prophet: seasonality_mode, interval_width, etc.
        - ARIMA: p, d, q defaults
        
        Args:
            model_type: Model type string
            
        Returns:
            Dict of default parameters
            
        Raises:
            TODO: ModelNotFoundError
        """
        pass
