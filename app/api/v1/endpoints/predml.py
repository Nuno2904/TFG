"""
🔮 Prophet Predictions Endpoints

Endpoints for making predictions with trained Prophet ML models.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
import logging
from datetime import datetime
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

from app.db.session import get_db
from app.models import MLModel, Usuario, Dataset
from app.models.ml import ModelStatus
from app.security import get_current_user
from app.ml.prophet.predict import predict_prophet_model, prophet_plot
from app.ml.prophet.predict import get_training_samples as get_prophet_training_samples
from app.ml.arima.predict import predict_arima_model, get_training_samples as get_arima_training_samples
from app.services.ml_storage_service import MLStorageService

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════


class PredictionRequest(BaseModel):
    """Schema for prediction request."""
    
    model_id: int = Field(..., description="ID of the trained Prophet model")
    periods: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Number of periods to predict (1-365)"
    )


class PredictionPoint(BaseModel):
    """Single prediction point."""
    
    ds: str = Field(..., description="Date of prediction")
    yhat: float = Field(..., description="Predicted value")
    yhat_lower: Optional[float] = Field(None, description="Lower confidence bound")
    yhat_upper: Optional[float] = Field(None, description="Upper confidence bound")


class PredictionResponse(BaseModel):
    """Schema for prediction response."""
    
    model_id: int = Field(..., description="ID of model used")
    model_name: str = Field(..., description="Name of the model")
    model_path: str = Field(..., description="Path to model file")
    dataset_id: int = Field(..., description="ID of training dataset")
    periods: int = Field(..., description="Number of periods predicted")
    forecast: List[dict] = Field(..., description="List of predictions")
    created_at: str = Field(..., description="Timestamp of prediction generation")


# ═══════════════════════════════════════════════════════════════════════════
# ARIMA SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════


class ARIMAForecastPoint(BaseModel):
    """Single ARIMA forecast point."""
    
    date: str = Field(..., description="Forecast date (YYYY-MM-DD)")
    yhat: float = Field(..., description="Predicted value")
    yhat_lower: Optional[float] = Field(None, description="95% lower confidence bound")
    yhat_upper: Optional[float] = Field(None, description="95% upper confidence bound")


class ARIMAPredictionResponse(BaseModel):
    """Response for ARIMA predictions."""
    
    model_id: int = Field(..., description="ID of model used")
    model_name: str = Field(..., description="Name of the model")
    model_type: str = Field(..., description="Model type (arima)")
    dataset_id: int = Field(..., description="ID of training dataset")
    periods: int = Field(..., description="Number of periods predicted")
    forecast: List[ARIMAForecastPoint] = Field(..., description="List of predictions")
    created_at: str = Field(..., description="Timestamp of prediction generation")


# ═══════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════

router = APIRouter(
    prefix="/predictions",
    tags=["🔮 ML Predictions (Prophet & ARIMA)"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
        status.HTTP_404_NOT_FOUND: {"description": "Model not found"},
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid request"},
    }
)


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════


def get_trained_model(
    model_id: int,
    user_id: int,
    db: Session
) -> MLModel:
    """
    Retrieve and validate model ownership and training status.
    
    Args:
        model_id: ID of the model
        user_id: ID of authenticated user
        db: Database session
        
    Returns:
        MLModel object
        
    Raises:
        HTTPException: If model not found, ownership mismatch, or not trained
    """
    model = db.query(MLModel).filter(
        MLModel.id == model_id,
        MLModel.user_id == user_id
    ).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found or does not belong to current user"
        )
    
    # Validar que el modelo está entrenado
    if model.status != ModelStatus.TRAINED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model is not trained. Current status: {model.status}"
        )
    
    return model


# ═══════════════════════════════════════════════════════════════════════════
# 🔮 MAKE PREDICTION ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════


@router.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Make Prophet Prediction",
    description="Make predictions using a trained Prophet ML model"
)
def predict(
    request: PredictionRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    🔮 Make predictions with a trained Prophet model.
    
    Uses the specified Prophet model to generate forecasts for the requested
    number of periods. The model must be in "entrenado" (trained) status.
    
    Args:
        request: Prediction request with model_id and periods
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Predictions with forecast values and confidence intervals
    """
    try:
        # Get and validate model
        model = get_trained_model(request.model_id, current_user.id, db)
        
        # Get dataset info for context
        dataset = db.query(Dataset).filter(
            Dataset.id == model.dataset_id
        ).first()
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Associated dataset not found"
            )
        
        logger.info(f"Making prediction with model {model.id} for {request.periods} periods")
        
        # Call Prophet prediction service using centralized model loading
        forecast_data = predict_prophet_model(
            model_path=model.model_path,
            future_periods=request.periods
        )
        
        # Filter to only future predictions (last 'periods' rows)
        future_forecast = forecast_data[-request.periods:] if len(forecast_data) > request.periods else forecast_data
        
        return {
            "model_id": model.id,
            "model_name": model.name,
            "model_path": model.model_path,
            "dataset_id": model.dataset_id,
            "periods": request.periods,
            "forecast": future_forecast,
            "created_at": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# 📊 MODEL INFO ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════


@router.get(
    "/models/{model_id}/info",
    status_code=status.HTTP_200_OK,
    summary="Get Model Information",
    description="Get details about a specific Prophet model"
)
def get_model_info(
    model_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    📊 Get information about a Prophet model.
    
    Args:
        model_id: ID of the model
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Model details including status, path, and dataset
    """
    model = db.query(MLModel).filter(
        MLModel.id == model_id,
        MLModel.user_id == current_user.id
    ).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    return {
        "id": model.id,
        "name": model.name,
        "path": model.model_path,
        "status": model.status.value,
        "dataset_id": model.dataset_id,
        "created_at": model.created_at.isoformat() if model.created_at else None,
        "error_message": model.error_message
    }


# ═══════════════════════════════════════════════════════════════════════════
# 📈 PLOT PREDICTIONS ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════


@router.get(
    "/plots/{model_id}",
    status_code=status.HTTP_200_OK,
    summary="Get Prediction Plots",
    description="Get forecast and components plots for a Prophet model"
)
def get_plots(
    model_id: int,
    periods: int = 30,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    📈 Get visualization plots for Prophet model predictions.
    
    Generates Prophet forecast and components plots using Prophet's .plot() methods.
    Returns plots as base64-encoded images in JSON.
    
    Args:
        model_id: ID of the model
        periods: Number of forecast periods (default 30)
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Dictionary with base64-encoded images of forecast and components plots
    """
    try:
        # Get and validate model
        model = get_trained_model(model_id, current_user.id, db)
        
        logger.info(f"Generating plots for model {model_id}")
        
        # Load Prophet model using centralized function
        prophet_model = MLStorageService.load_prophet_model_from_directory(model.model_path)
        
        # Make forecast
        future_df = prophet_model.make_future_dataframe(periods=periods)
        forecast = prophet_model.predict(future_df)
        
                # Helper function to convert matplotlib figure to base64
        def fig_to_base64(fig):
            """Convert matplotlib figure to base64 string"""
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)
            return image_base64
        
        # Generate forecast plot using Prophet's .plot() method
        logger.info("📈 Generating forecast plot...")
        forecast_fig = prophet_model.plot(forecast)
        forecast_plot_b64 = fig_to_base64(forecast_fig)
        
        # Generate components plot using Prophet's .plot_components() method
        logger.info("📊 Generating components plot...")
        components_fig = prophet_model.plot_components(forecast)
        components_plot_b64 = fig_to_base64(components_fig)
        
        return {
            "model_id": model.id,
            "model_name": model.name,
            "periods": periods,
            "forecast_plot": f"data:image/png;base64,{forecast_plot_b64}",
            "components_plot": f"data:image/png;base64,{components_plot_b64}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Plot generation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Plot generation failed: {str(e)}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# 🔮 ARIMA PREDICT ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════


@router.post(
    "/arima/predict",
    response_model=ARIMAPredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Make ARIMA Prediction",
    description="Make predictions using a trained ARIMA ML model"
)
def predict_arima(
    request: PredictionRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    🔮 Make predictions with a trained ARIMA model.
    
    Uses the specified ARIMA model to generate forecasts with confidence intervals.
    
    Args:
        request: Prediction request with model_id and periods
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Predictions with forecast values and 95% confidence intervals
    """
    try:
        # Get and validate model
        model = get_trained_model(request.model_id, current_user.id, db)
        
        # Verify it's an ARIMA model
        if model.model_type.lower() != "arima":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Model is not ARIMA type. Model type: {model.model_type}"
            )
        
        logger.info(f"Making ARIMA prediction with model {model.id} for {request.periods} periods")
        
        # Call ARIMA prediction service
        prediction_result = predict_arima_model(
            model_path=model.model_path,
            future_periods=request.periods
        )
        
        return {
            "model_id": model.id,
            "model_name": model.name,
            "model_type": "arima",
            "dataset_id": model.dataset_id,
            "periods": request.periods,
            "forecast": prediction_result['forecast'],
            "created_at": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ARIMA prediction error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ARIMA prediction failed: {str(e)}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# 📊 ARIMA MODEL INFO ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════


@router.get(
    "/arima/models/{model_id}/info",
    status_code=status.HTTP_200_OK,
    summary="Get ARIMA Model Information",
    description="Get detailed information about a trained ARIMA model"
)
def get_arima_model_info(
    model_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    📊 Get detailed information about an ARIMA model.
    
    Includes model parameters (p,d,q), training metrics (AIC, BIC, RMSE, MAE).
    
    Args:
        model_id: ID of the model
        current_user: Authenticated user
        db: Database session
        
    Returns:
        ARIMA model details with training parameters and metrics
    """
    try:
        model = db.query(MLModel).filter(
            MLModel.id == model_id,
            MLModel.user_id == current_user.id
        ).first()
        
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model not found"
            )
        
        if model.model_type.lower() != "arima":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Model is not ARIMA type. Model type: {model.model_type}"
            )
        
        # Load metadata
        metadata = MLStorageService.load_arima_metadata(model.model_path)
        
        return {
            "id": model.id,
            "name": model.name,
            "model_type": "arima",
            "path": model.model_path,
            "status": model.status,
            "dataset_id": model.dataset_id,
            "created_at": model.created_at.isoformat() if model.created_at else None,
            "error_message": model.error_message,
            "training_metrics": {
                "order": metadata.get('order'),
                "aic": metadata.get('aic'),
                "bic": metadata.get('bic'),
                "rmse": metadata.get('rmse'),
                "mae": metadata.get('mae'),
                "data_points": metadata.get('longitud', metadata.get('length'))
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving ARIMA model info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve model information: {str(e)}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# 📈 ARIMA TRAINING DATA ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════


@router.get(
    "/arima/models/{model_id}/training-data",
    status_code=status.HTTP_200_OK,
    summary="Get ARIMA Training Data",
    description="Get training data samples used to train the ARIMA model"
)
def get_arima_training_data(
    model_id: int,
    samples: int = 100,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    📈 Get training data samples from an ARIMA model.
    
    Useful for visualizing historical data alongside predictions.
    
    Args:
        model_id: ID of the model
        samples: Number of training samples to return (default: 100)
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Historical training data points with dates and values
    """
    try:
        model = db.query(MLModel).filter(
            MLModel.id == model_id,
            MLModel.user_id == current_user.id
        ).first()
        
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model not found"
            )
        
        if model.model_type.lower() != "arima":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Model is not ARIMA type. Model type: {model.model_type}"
            )
        
        logger.info(f"Retrieving training data for model {model_id}")
        
        training_data = get_arima_training_samples(model.model_path, n_samples=samples)
        
        return {
            "model_id": model.id,
            "model_name": model.name,
            "training_data": training_data['training_samples'],
            "total_training_points": training_data['total_training_points']
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving training data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve training data: {str(e)}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# 📊 ARIMA FORECAST PLOT ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════


@router.get(
    "/plots/arima/{model_id}",
    status_code=status.HTTP_200_OK,
    summary="Get ARIMA Forecast Plot",
    description="Generate and return a plot of ARIMA forecasts with confidence intervals"
)
def get_arima_plot(
    model_id: int,
    periods: int = 30,
    historical_periods: int = 50,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    📊 Generate a forecast plot for an ARIMA model.
    
    Creates a plot showing historical data, predictions, and 95% confidence intervals.
    The plot is returned as a base64-encoded PNG image.
    
    Args:
        model_id: ID of the ARIMA model
        periods: Number of periods to forecast (default: 30)
        historical_periods: Number of historical periods to display (default: 50)
        current_user: Authenticated user
        db: Database session
        
    Returns:
        PNG image as base64 with model parameters
    """
    try:
        # Verify model exists and belongs to user
        model = db.query(MLModel).filter(
            MLModel.id == model_id,
            MLModel.user_id == current_user.id
        ).first()
        
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model not found"
            )
        
        if model.model_type.lower() != "arima":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Model is not ARIMA type. Model type: {model.model_type}"
            )
        
        if model.status.lower() != "entrenado":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Model is not trained. Status: {model.status}"
            )
        
        logger.info(f"Generating forecast plot for ARIMA model {model_id}")
        
        # Import plot function
        from app.ml.arima.predict import plot_arima_forecast
        
        # Generate plot
        plot_result = plot_arima_forecast(
            model_path=model.model_path,
            future_periods=periods,
            historical_periods=historical_periods
        )
        
        if plot_result['status'] != 'éxito':
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate plot: {plot_result.get('error', 'Unknown error')}"
            )
        
        logger.info(f"✅ Plot generated successfully for model {model_id}")
        
        return {
            "model_id": model.id,
            "model_name": model.name,
            "model_type": "arima",
            "image": plot_result['image'],
            "parameters": plot_result['parameters'],
            "created_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating ARIMA plot: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate plot: {str(e)}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# 📈 UNIFIED TRAINING DATA ENDPOINT (ARIMA + PROPHET)
# ═══════════════════════════════════════════════════════════════════════════


@router.get(
    "/models/{model_id}/training-data",
    status_code=status.HTTP_200_OK,
    summary="Get Model Training Data",
    description="Get training data samples for any model type (ARIMA or Prophet)"
)
def get_model_training_data(
    model_id: int,
    samples: int = 100,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    📈 Get training data samples from any model (ARIMA or Prophet).
    
    Args:
        model_id: ID of the model
        samples: Number of training samples to return (default: 100)
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Historical training data points with dates and values
    """
    try:
        model = db.query(MLModel).filter(
            MLModel.id == model_id,
            MLModel.user_id == current_user.id
        ).first()
        
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model not found"
            )
        
        if model.status != ModelStatus.TRAINED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Model is not trained. Current status: {model.status}"
            )
        
        logger.info(f"Retrieving training data for model {model_id} (type: {model.model_type})")
        
        model_type = model.model_type.lower()
        
        if model_type == "arima":
            training_data = get_arima_training_samples(model.model_path, n_samples=samples)
        elif model_type == "prophet":
            training_data = get_prophet_training_samples(model.model_path, n_samples=samples)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported model type: {model.model_type}"
            )
        
        return {
            "model_id": model.id,
            "model_name": model.name,
            "model_type": model_type,
            "training_data": training_data['training_samples'],
            "total_training_points": training_data['total_training_points']
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving training data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve training data: {str(e)}"
        )