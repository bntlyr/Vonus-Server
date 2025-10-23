from fastapi import APIRouter, HTTPException
from datetime import datetime
from models.schemas import FloodZonesResponse, FloodZone
from services.data_service import data_service

router = APIRouter()


@router.get("/flood-zones", response_model=FloodZonesResponse)
async def get_flood_zones():
    """
    Retrieve flood hazard zones from LiPAD database
    
    Returns a comprehensive list of flood-prone areas in Quezon City
    with hazard levels and population data.
    """
    try:
        # Get flood zones from data service
        zones_data = data_service.get_flood_zones()
        
        # Convert to FloodZone models
        flood_zones = []
        for zone_data in zones_data:
            flood_zone = FloodZone(
                zone_id=zone_data['zone_id'],
                barangay=zone_data['barangay'],
                city=zone_data['city'],
                province=zone_data['province'],
                hazard_level=zone_data['hazard_level'],
                coordinates=zone_data['coordinates'],
                population_at_risk=zone_data['population_at_risk'],
                last_updated=datetime.fromisoformat(zone_data['last_updated'].replace('Z', '+00:00'))
            )
            flood_zones.append(flood_zone)
        
        # Create response
        response = FloodZonesResponse(
            zones=flood_zones,
            total_zones=len(flood_zones)
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving flood zones: {str(e)}"
        )