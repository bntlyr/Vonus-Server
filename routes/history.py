from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import Optional
from models.schemas import HistoryResponse, HistoricalRecord, ForecastRequest, ForecastResponse
from services.data_service import history_service

router = APIRouter()


@router.get("/history", response_model=HistoryResponse)
async def get_forecast_history(
    limit: int = Query(default=20, ge=1, le=100, description="Number of records to retrieve")
):
    """
    Retrieve historical flood forecast records
    
    Returns previously generated flood predictions for analysis and validation.
    Useful for tracking prediction accuracy and system performance.
    """
    try:
        # Get history from service
        history_records = history_service.get_history(limit=limit)
        
        # Convert to HistoricalRecord models
        historical_records = []
        for record in history_records:
            historical_record = HistoricalRecord(
                record_id=record['record_id'],
                request_data=ForecastRequest(**record['request_data']),
                response_data=ForecastResponse(**record['response_data'])
            )
            historical_records.append(historical_record)
        
        # Create response
        response = HistoryResponse(
            records=historical_records,
            total_records=len(historical_records)
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving forecast history: {str(e)}"
        )