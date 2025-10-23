from fastapi import APIRouter
from datetime import datetime
import os
from models.schemas import SystemStatus

router = APIRouter()


@router.get("/test", response_model=SystemStatus)
async def get_system_status():
    """
    Check system health and status
    
    Returns basic system information and confirms the server is running.
    """
    
    app_name = os.getenv('APP_NAME', 'Vonus AR Flood Forecasting System')
    app_version = os.getenv('APP_VERSION', '1.0.0')
    
    return SystemStatus(
        status="online",
        message=f"{app_name} server is running successfully",
        version=app_version
    )