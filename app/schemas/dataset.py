"""
📋 Dataset Pydantic Schemas

Request/response validation schemas for dataset endpoints.

Responsibilities:
- Validate dataset creation requests
- Define response shapes for API
- Document API contract with examples
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class DatasetBase(BaseModel):
    """Base schema with common dataset fields."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Dataset name")
    description: Optional[str] = Field(None, max_length=1000, description="Optional description")
    date_column_name: str = Field(..., description="Name of date/datetime column in CSV")
    value_column_name: str = Field(..., description="Name of value column to predict")
    frequency: Optional[str] = Field(None, description="Time series frequency (D, H, W, M, Y)")


class DatasetCreate(DatasetBase):
    """
    TODO: Schema for creating a new dataset (CSV upload)
    
    Should include:
    - Inherit from DatasetBase
    - Add any create-specific validations
    - Add any computed fields if needed
    """
    pass


class DatasetUpdate(BaseModel):
    """
    TODO: Schema for updating dataset metadata
    
    Should include:
    - name (optional)
    - description (optional)
    - frequency (optional if not auto-detected)
    - Any other updatable fields
    """
    pass


class DatasetOut(DatasetBase):
    """
    Response schema when returning dataset.
    
    TODO: Include:
    - All base fields
    - Computed fields (file_size_bytes, num_records, date range)
    - Timestamps (created_at, updated_at)
    - Status
    - Exclude: file_path (security)
    """
    
    id: int = Field(..., description="Dataset ID")
    user_id: int
    file_size_bytes: Optional[int] = None
    original_filename: Optional[str] = None
    num_records: Optional[int] = None
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    status: str = Field(default="active")
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class DatasetListOut(BaseModel):
    """Response for list datasets endpoint with pagination."""
    
    # TODO: Include pagination info
    # - items: List[DatasetOut]
    # - total: int
    # - skip: int
    # - limit: int
    pass
