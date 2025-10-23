from fastapi import APIRouter, HTTPException
from datetime import datetime
from models.schemas import ForecastRequest, ForecastResponse, ErrorResponse
from services.data_service import data_service, history_service

router = APIRouter()


@router.post("/forecast", response_model=ForecastResponse)
async def predict_flood_risk(request: ForecastRequest):
    """
    Predict flood risk based on environmental parameters
    
    This endpoint uses fuzzy logic to analyze rainfall, soil saturation,
    and drainage capacity to provide flood risk predictions.
    """
    try:
        # Generate prediction using data service
        prediction = data_service.predict_flood_risk(
            latitude=request.latitude,
            longitude=request.longitude,
            rainfall_mm=request.rainfall_mm,
            soil_saturation=request.soil_saturation,
            drainage_capacity=request.drainage_capacity
        )
        
        # Create response
        response = ForecastResponse(
            location=prediction['location'],
            flood_risk_level=prediction['flood_risk_level'],
            predicted_depth_m=prediction['predicted_depth_m'],
            confidence=prediction['confidence'],
            advisory=prediction['advisory']
        )
        
        # Save to history
        history_service.save_forecast(
            request_data=request.dict(),
            response_data=response.dict()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating flood prediction: {str(e)}"
        )