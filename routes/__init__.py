# Routes package
from .forecast import router as forecast_router
from .flood_zones import router as flood_zones_router
from .system import router as system_router
from .history import router as history_router
from .feedback import router as feedback_router

__all__ = [
    "forecast_router",
    "flood_zones_router", 
    "system_router",
    "history_router",
    "feedback_router"
]