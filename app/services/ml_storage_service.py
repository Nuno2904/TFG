"""
📂 ML Storage Service

Manages ML model storage paths and file organization.
Handles directory creation and path management for model files.
"""

import logging
from pathlib import Path
from app.paths import MODELS_DIR
import joblib
        

logger = logging.getLogger(__name__)


class MLStorageService:
    """
    Service for managing ML model storage.
    
    Organizes models in the following structure:
    storage/models/
    ├── user_{user_id}/
    │   ├── dataset_{dataset_id}/
    │   │   ├── {model_name}/
    │   │   │   ├── model.json          (Prophet)
    │   │   │   ├── model.pkl           (ARIMA)
    │   │   │   ├── model_metadata.json (ARIMA)
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
    def get_model_file_path(user_id: int, dataset_id: int, model_name: str, filename: str = "model.json") -> Path:
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
    
    @staticmethod
    def load_prophet_model_from_directory(model_dir_path: str):
        """
        Load a Prophet model from a directory by finding and loading the .json file.
        
        This function automatically searches for .json files in the model directory,
        which is necessary because model_path points to a directory, not a file.
        
        Args:
            model_dir_path (str): Path to the model directory
            
        Returns:
            Prophet model object loaded from JSON
            
        Raises:
            FileNotFoundError: If no .json file found in directory
            Exception: If loading fails
        """
        from prophet.serialize import model_from_json
        
        model_dir = Path(model_dir_path)
        
        # Search for .json file in directory, excluding metadata files
        json_files = [f for f in model_dir.glob("*.json") if not f.name.endswith("_metadata.json")]
        
        if not json_files:
            raise FileNotFoundError(f"No JSON model file found in directory: {model_dir}")
        
        # Use the first .json file found
        model_file = json_files[0]
        logger.info(f"📁 Loading Prophet model from: {model_file}")
        
        # Load model from JSON
        with open(model_file, 'r') as f:
            model_json = f.read()
            prophet_model = model_from_json(model_json)
        
        logger.info(f"✅ Prophet model loaded successfully")
        return prophet_model
    
    @staticmethod
    def load_arima_model_from_directory(model_dir_path: str):
        """
        Load an ARIMA model from a directory by finding and loading the .pkl file.
        
        Args:
            model_dir_path (str): Path to the model directory
            
        Returns:
            ARIMA model object loaded from pickle
            
        Raises:
            FileNotFoundError: If no .pkl file found in directory
            Exception: If loading fails
        """
       
        model_dir = Path(model_dir_path)
        
        # Search for .pkl file in directory
        pkl_files = list(model_dir.glob("*.pkl"))
        
        if not pkl_files:
            raise FileNotFoundError(f"No PKL model file found in directory: {model_dir}")
        
        # Use the first .pkl file found
        model_file = pkl_files[0]
        logger.info(f"📁 Loading ARIMA model from: {model_file}")
        
        # Load model from pickle
        try:
            arima_model = joblib.load(model_file)
            logger.info(f"✅ ARIMA model loaded successfully")
            return arima_model
        except Exception as e:
            logger.error(f"❌ Error loading ARIMA model: {str(e)}")
            raise
    
    @staticmethod
    def load_arima_metadata(model_dir_path: str) -> dict:
        """
        Load ARIMA model metadata from JSON file.
        
        Args:
            model_dir_path (str): Path to the model directory
            
        Returns:
            dict: Metadata dictionary with model info
            
        Raises:
            FileNotFoundError: If no metadata file found
        """
        import json
        
        model_dir = Path(model_dir_path)
        metadata_files = list(model_dir.glob("*_metadata.json"))
        
        if not metadata_files:
            raise FileNotFoundError(f"No metadata file found in directory: {model_dir}")
        
        metadata_file = metadata_files[0]
        logger.info(f"📁 Loading metadata from: {metadata_file}")
        
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            logger.info(f"✅ Metadata loaded successfully")
            return metadata
        except Exception as e:
            logger.error(f"❌ Error loading metadata: {str(e)}")
            raise
    
    @staticmethod
    def load_prophet_metadata(model_dir_path: str) -> dict:
        """
        Load Prophet model metadata from JSON file.
        
        Args:
            model_dir_path (str): Path to the model directory
            
        Returns:
            dict: Metadata dictionary with model info (mae, rmse, mape, longitud)
            
        Raises:
            FileNotFoundError: If no metadata file found
        """
        import json
        
        model_dir = Path(model_dir_path)
        metadata_files = list(model_dir.glob("*_metadata.json"))
        
        if not metadata_files:
            raise FileNotFoundError(f"No metadata file found in directory: {model_dir}")
        
        metadata_file = metadata_files[0]
        logger.info(f"📁 Loading Prophet metadata from: {metadata_file}")
        
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            logger.info(f"✅ Prophet metadata loaded successfully")
            return metadata
        except Exception as e:
            logger.error(f"❌ Error loading Prophet metadata: {str(e)}")
            raise
