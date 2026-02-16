"""
🔮 Prediction Endpoints

API endpoints for running predictions and retrieving results.

Responsibilities:
- Create predictions (run ML model)
- List user predictions
- Get prediction results and metrics
- Compare multiple predictions
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.v1.dependencies import get_current_user_v1
from app.services.prediction_service import PredictionService
from app.schemas.prediction import PredictionCreate, PredictionOut, PredictionDetailOut


# ═══════════════════════════════════════════════════════════════════════════
# 🔧 ROUTER SETUP
# ═══════════════════════════════════════════════════════════════════════════

router = APIRouter(prefix="/predictions", tags=["predictions"])


# ═══════════════════════════════════════════════════════════════════════════
# 🚀 POST: Create Prediction
# ═══════════════════════════════════════════════════════════════════════════

@router.post("", response_model=PredictionDetailOut, status_code=201)
async def create_prediction(
    prediction_create: PredictionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_v1)
):
    """
    TODO: Create new prediction (run ML model)
    
    Endpoint: POST /api/v1/predictions
    
    Steps:
    1. Validate user owns the dataset
    2. Validate model exists and is active
    3. Create Prediction in DB with status="pending"
    4. Call PredictionService.create_prediction()
    5. Wait for completion (or implement async)
    6. Return completed prediction with results/metrics
    
    Args:
        prediction_create: Request data
        db: Database session
        current_user: Authenticated user
        
    Returns:
        PredictionDetailOut with results
        
    Raises:
        TODO: HTTPException (400, 403, 404, 422)
    """
    pass


# ═══════════════════════════════════════════════════════════════════════════
# 📖 GET: List Predictions
# ═══════════════════════════════════════════════════════════════════════════

@router.get("", response_model=list)
async def list_predictions(
    dataset_id: int = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_v1)
):
    """
    TODO: List all predictions (optionally filtered by dataset)
    
    Endpoint: GET /api/v1/predictions
    
    Query Parameters:
    - dataset_id (optional): Filter to specific dataset
    - skip: Pagination offset
    - limit: Pagination limit
    
    Args:
        dataset_id: Optional dataset filter
        skip, limit: Pagination
        db: Database session
        current_user: Authenticated user
        
    Returns:
        List of PredictionOut instances
    """
    pass


# ═══════════════════════════════════════════════════════════════════════════
# 📖 GET: Get Single Prediction with Results
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/{prediction_id}", response_model=PredictionDetailOut)
async def get_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_v1)
):
    """
    TODO: Get full prediction details including results and metrics
    
    Endpoint: GET /api/v1/predictions/{prediction_id}
    
    Args:
        prediction_id: Prediction to retrieve
        db: Database session
        current_user: Authenticated user
        
    Returns:
        PredictionDetailOut with all results
        
    Raises:
        TODO: HTTPException (403, 404)
    """
    pass


# ═══════════════════════════════════════════════════════════════════════════
# 🗑️ DELETE: Delete Prediction
# ═══════════════════════════════════════════════════════════════════════════

@router.delete("/{prediction_id}", status_code=204)
async def delete_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_v1)
):
    """
    TODO: Delete prediction and all associated results/metrics
    
    Endpoint: DELETE /api/v1/predictions/{prediction_id}
    
    Args:
        prediction_id: Prediction to delete
        db: Database session
        current_user: Authenticated user
        
    Raises:
        TODO: HTTPException (403, 404)
    """
    pass


# ═══════════════════════════════════════════════════════════════════════════
# 🔄 POST: Compare Predictions (Future Feature)
# ═══════════════════════════════════════════════════════════════════════════

# TODO: Implement comparison endpoint when needed
# @router.post("/compare", response_model=dict)
# async def compare_predictions(...):
#     """Compare multiple predictions and return metrics comparison"""
