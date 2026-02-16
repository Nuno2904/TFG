"""
🎛️ Model Configuration Endpoints

API endpoints for viewing available models and their parameters.

Responsibilities:
- List available models
- Get model information and default parameters
- Validate model parameters
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.v1.dependencies import get_current_user_v1
from app.services.model_factory import ModelFactory
from app.schemas.model_config import PredictionModelOut, ModelListOut


# ═══════════════════════════════════════════════════════════════════════════
# 🔧 ROUTER SETUP
# ═══════════════════════════════════════════════════════════════════════════

router = APIRouter(prefix="/models", tags=["models"])


# ═══════════════════════════════════════════════════════════════════════════
# 📖 GET: List Available Models
# ═══════════════════════════════════════════════════════════════════════════

@router.get("", response_model=ModelListOut)
async def list_models(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_v1)
):
    """
    TODO: Get list of available prediction models
    
    Endpoint: GET /api/v1/models
    
    Returns all active models (Prophet, ARIMA) with their:
    - Names and display names
    - Descriptions
    - Parameter schemas
    - Default parameters
    
    Args:
        db: Database session
        current_user: Authenticated user
        
    Returns:
        ModelListOut with list of PredictionModelOut
    """
    pass


# ═══════════════════════════════════════════════════════════════════════════
# 📖 GET: Get Single Model Details
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/{model_id}", response_model=PredictionModelOut)
async def get_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_v1)
):
    """
    TODO: Get details of specific model
    
    Endpoint: GET /api/v1/models/{model_id}
    
    Returns:
    - Model information
    - Parameter schema
    - Usage examples (optional)
    
    Args:
        model_id: Model ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        PredictionModelOut instance
    """
    pass


# ═══════════════════════════════════════════════════════════════════════════
# 📖 GET: Model Default Parameters
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/{model_id}/defaults")
async def get_model_defaults(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_v1)
):
    """
    TODO: Get default parameters for a model
    
    Endpoint: GET /api/v1/models/{model_id}/defaults
    
    Returns:
    {
        "p": 1,
        "d": 1,
        "q": 1,
        ...
    }
    
    Args:
        model_id: Model ID
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Dict of default parameters
    """
    pass
