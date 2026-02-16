"""
🎛️ Model Configuration Pydantic Schemas

Schemas for model information endpoints.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class PredictionModelOut(BaseModel):
    """Response schema for available model."""
    
    id: int
    name: str = Field(..., description="Machine name: prophet, arima")
    display_name: Optional[str] = None
    description: Optional[str] = None
    parameters_schema: Optional[Dict[str, Any]] = None
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)


class ModelListOut(BaseModel):
    """Response for list available models."""
    
    # TODO: Include:
    # - items: List[PredictionModelOut]
    # - total: int
    pass
