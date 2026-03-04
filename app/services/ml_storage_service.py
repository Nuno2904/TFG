"""
📂 ML Storage Service

Manages ML model storage paths and file organization.
Handles directory creation and path management for model files.
"""

import os
from pathlib import Path
from app.config import settings


class MLStorageService:
    """
    Service for managing ML model storage.
    
    Organizes models in the following structure:
    /app/storage/models/
    ├── user_{user_id}/
    │   ├── dataset_{dataset_id}/
    │   │   ├── {model_name}/
    │   │   │   ├── model.pkl
    │   │   │   ├── metadata.json
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
        base_path = Path(settings.MODEL_STORAGE_PATH)
        model_dir = base_path / f"user_{user_id}" / f"dataset_{dataset_id}" / model_name
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
        model_dir.mkdir(parents=True, exist_ok=True)
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
        base_path = Path(settings.MODEL_STORAGE_PATH)
        user_dir = base_path / f"user_{user_id}"
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
        base_path = Path(settings.MODEL_STORAGE_PATH)
        dataset_dir = base_path / f"user_{user_id}" / f"dataset_{dataset_id}"
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
                return True
            return False
        except Exception as e:
            print(f"Error deleting model directory: {e}")
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
