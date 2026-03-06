"""
📂 ML Storage Service

Manages ML model storage paths and file organization.
Handles directory creation and path management for model files.
"""

import logging
from pathlib import Path
from app.paths import MODELS_DIR

logger = logging.getLogger(__name__)


class MLStorageService:
    """
    Service for managing ML model storage.
    
    Organizes models in the following structure:
    storage/models/
    ├── user_{user_id}/
    │   ├── dataset_{dataset_id}/
    │   │   ├── {model_name}/
    │   │   │   ├── model.json
    │   │   │   └── ...
    """
    
    @staticmethod
    def get_model_directory(user_id: int, dataset_id: int, model_name: str) -> Path:
        """
        Get the directory path for a model.
        
        Args:
            user_id: ID of the user who created the model
            dataset_id: ID of the dataset used for training
            model_name: Name of the model
            
        Returns:
            Path object pointing to the model directory
        """
        model_dir = MODELS_DIR / f"user_{user_id}" / f"dataset_{dataset_id}" / model_name
        
        logger.debug(f"Model directory path: {model_dir}")
        
        return model_dir
    
    @staticmethod
    def create_model_directory(user_id: int, dataset_id: int, model_name: str) -> Path:
        """
        Create the directory structure for a model if it doesn't exist.
        
        Args:
            user_id: ID of the user who created the model
            dataset_id: ID of the dataset used for training
            model_name: Name of the model
            
        Returns:
            Path object pointing to the created model directory
            
        Raises:
            OSError: If directory creation fails
        """
        model_dir = MLStorageService.get_model_directory(user_id, dataset_id, model_name)
        
        try:
            model_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Created model directory: {model_dir}")
        except Exception as e:
            logger.error(f"❌ Failed to create model directory {model_dir}: {str(e)}")
            raise OSError(f"Failed to create directory {model_dir}: {str(e)}")
        
        return model_dir
    
    @staticmethod
    def get_user_models_directory(user_id: int) -> Path:
        """
        Get the directory path for all models of a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Path object pointing to the user's models directory
        """
        user_dir = MODELS_DIR / f"user_{user_id}"
        return user_dir
    
    @staticmethod
    def get_dataset_models_directory(user_id: int, dataset_id: int) -> Path:
        """
        Get the directory path for all models of a specific dataset.
        
        Args:
            user_id: ID of the user
            dataset_id: ID of the dataset
            
        Returns:
            Path object pointing to the dataset models directory
        """
        dataset_dir = MODELS_DIR / f"user_{user_id}" / f"dataset_{dataset_id}"
        return dataset_dir
    
    @staticmethod
    def get_model_file_path(user_id: int, dataset_id: int, model_name: str, filename: str = "model.pkl") -> Path:
        """
        Get the full file path for a model file.
        
        Args:
            user_id: ID of the user
            dataset_id: ID of the dataset
            model_name: Name of the model
            filename: Name of the file (default: model.pkl)
            
        Returns:
            Path object pointing to the model file
        """
        model_dir = MLStorageService.get_model_directory(user_id, dataset_id, model_name)
        return model_dir / filename
    
    @staticmethod
    def delete_model_directory(user_id: int, dataset_id: int, model_name: str) -> bool:
        """
        Delete the entire model directory including all files.
        
        Args:
            user_id: ID of the user
            dataset_id: ID of the dataset
            model_name: Name of the model
            
        Returns:
            True if deletion was successful, False otherwise
        """
        import shutil
        model_dir = MLStorageService.get_model_directory(user_id, dataset_id, model_name)
        
        try:
            if model_dir.exists():
                shutil.rmtree(model_dir)
                logger.info(f"✅ Deleted model directory: {model_dir}")
                return True
            logger.warning(f"⚠️ Model directory does not exist: {model_dir}")
            return False
        except Exception as e:
            logger.error(f"❌ Error deleting model directory {model_dir}: {str(e)}")
            return False
    
    @staticmethod
    def get_relative_path(user_id: int, dataset_id: int, model_name: str) -> str:
        """
        Get the relative path for database storage.
        
        Args:
            user_id: ID of the user
            dataset_id: ID of the dataset
            model_name: Name of the model
            
        Returns:
            String with relative path format: user_{user_id}/dataset_{dataset_id}/{model_name}
        """
        return f"user_{user_id}/dataset_{dataset_id}/{model_name}"
