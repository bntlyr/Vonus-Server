from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ForecastRequest(BaseModel):
    """Request model for flood forecast prediction"""
    latitude: float = Field(..., description="Latitude coordinate", ge=-90, le=90)
    longitude: float = Field(..., description="Longitude coordinate", ge=-180, le=180)
    rainfall_mm: float = Field(..., description="Rainfall in millimeters", ge=0)
    soil_saturation: float = Field(..., description="Soil saturation level (0.0-1.0)", ge=0.0, le=1.0)
    drainage_capacity: float = Field(..., description="Drainage capacity level (0.0-1.0)", ge=0.0, le=1.0)


class ForecastResponse(BaseModel):
    """Response model for flood forecast prediction"""
    location: str
    flood_risk_level: str = Field(..., description="Risk level: Low, Moderate, High, Critical")
    predicted_depth_m: float = Field(..., description="Predicted flood depth in meters")
    confidence: float = Field(..., description="Prediction confidence (0.0-1.0)")
    advisory: str
    timestamp: datetime = Field(default_factory=datetime.now)


class FloodZone(BaseModel):
    """Model for flood hazard zones"""
    zone_id: str
    barangay: str
    city: str
    province: str
    hazard_level: str = Field(..., description="Hazard level: Low, Medium, High")
    coordinates: List[List[float]] = Field(..., description="Polygon coordinates")
    population_at_risk: int
    last_updated: datetime


class FloodZonesResponse(BaseModel):
    """Response model for flood zones"""
    zones: List[FloodZone]
    total_zones: int
    query_timestamp: datetime = Field(default_factory=datetime.now)


class SystemStatus(BaseModel):
    """Response model for system status"""
    status: str
    message: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.now)


class HistoricalRecord(BaseModel):
    """Model for historical forecast records"""
    record_id: str
    request_data: ForecastRequest
    response_data: ForecastResponse
    actual_outcome: Optional[str] = None
    accuracy_score: Optional[float] = None


class HistoryResponse(BaseModel):
    """Response model for forecast history"""
    records: List[HistoricalRecord]
    total_records: int
    query_timestamp: datetime = Field(default_factory=datetime.now)


class FeedbackRequest(BaseModel):
    """Request model for user feedback"""
    forecast_id: str
    user_location: str
    actual_flood_level: str = Field(..., description="Actual flood level experienced")
    accuracy_rating: int = Field(..., description="Rating 1-5", ge=1, le=5)
    comments: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class FeedbackResponse(BaseModel):
    """Response model for feedback submission"""
    feedback_id: str
    status: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)