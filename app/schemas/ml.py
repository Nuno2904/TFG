"""
🤖 ML Model Schemas

Pydantic models for ML model request/response validation.
Defines data structures for API endpoints related to ML models.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal


class MLModelBase(BaseModel):
    """Base schema with common ML model fields."""
    
    name: str = Field(..., description="Name of the ML model")
    dataset_id: int = Field(..., description="ID of the dataset used for training")


class MLModelCreate(MLModelBase):
    """
    Schema for creating a new ML model.
    
    Required fields:
        - name: Model name
        - dataset_id: Dataset ID for training
    
    The model_path is generated automatically based on:
    /app/storage/models/user_{user_id}/dataset_{dataset_id}/{model_name}
    """
    pass


class MLModelUpdate(BaseModel):
    """
    Schema for updating ML model information.
    
    All fields are optional - only provided fields will be updated.
    """
    
    name: Optional[str] = Field(None, description="New model name")
    status: Optional[Literal["entrenado", "en_entrenamiento", "error"]] = Field(
        None, description="Model status"
    )
    error_message: Optional[str] = Field(None, description="Error details if training failed")


class MLModelOut(BaseModel):
    """
    Schema for ML model response (public data).
    
    Shows all model information including status and error details.
    """
    
    id: int = Field(..., description="Model ID")
    user_id: int = Field(..., description="ID of the user who created the model")
    dataset_id: int = Field(..., description="ID of the dataset used for training")
    name: str = Field(..., description="Name of the ML model")
    created_at: datetime = Field(..., description="Model creation date")
    model_path: str = Field(..., description="File path where the model is stored")
    status: str = Field(..., description="Model status: entrenado, en_entrenamiento, or error")
    error_message: Optional[str] = Field(None, description="Error details if training failed")
    
    model_config = {"from_attributes": True}


class MLModelDetailOut(MLModelOut):
    """
    Extended schema for detailed ML model response.
    
    Includes related user and dataset information.
    """
    
    class UsuarioDetail(BaseModel):
        """Simple user detail."""
        id: int
        email: str
        
        model_config = {"from_attributes": True}
    
    class DatasetDetail(BaseModel):
        """Simple dataset detail."""
        id: int
        name: str
        
        model_config = {"from_attributes": True}
    
    usuario: UsuarioDetail = Field(..., description="User who created the model")
    dataset: DatasetDetail = Field(..., description="Dataset used for training")
