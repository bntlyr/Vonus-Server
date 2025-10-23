from fastapi import APIRouter, HTTPException
from datetime import datetime
from models.schemas import FeedbackRequest, FeedbackResponse
from services.data_service import history_service

router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit user feedback on flood prediction accuracy
    
    Allows users to report actual flood conditions compared to predictions.
    This data helps improve the fuzzy logic system accuracy over time.
    """
    try:
        # Save feedback using history service
        feedback_id = history_service.save_feedback(feedback.dict())
        
        # Create response
        response = FeedbackResponse(
            feedback_id=feedback_id,
            status="success",
            message="Thank you for your feedback! This helps us improve our predictions."
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saving feedback: {str(e)}"
        )