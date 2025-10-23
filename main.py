from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import uvicorn

# Load environment variables
load_dotenv()

# Import routers
from routes import (
    forecast_router,
    flood_zones_router,
    system_router,
    history_router,
    feedback_router
)

# Create FastAPI application
app = FastAPI(
    title=os.getenv('APP_NAME', 'Vonus AR Flood Forecasting System'),
    description="""
    🌊 **Vonus: AR + Fuzzy Logic Flood Forecasting System**
    
    A sophisticated flood prediction API that combines:
    - **Fuzzy Logic** for intelligent risk assessment
    - **Environmental Data** from PAGASA, LiPAD, and UP NOAH
    - **Real-time Predictions** for AR mobile integration
    - **Localized Forecasts** for Quezon City areas
    
    ## Features
    
    * **🔮 Flood Prediction**: Advanced fuzzy logic algorithms
    * **📍 Location-based**: Tailored for Quezon City barangays  
    * **📱 AR Ready**: Optimized for mobile AR applications
    * **📊 Historical Data**: Access to past forecasts and feedback
    * **🔄 Real-time**: Live environmental data processing
    
    ## Team PJDSC 2025
    Colasino • Olata • Pasamante • Rafa • Tolentino
    """,
    version=os.getenv('APP_VERSION', '1.0.0'),
    contact={
        "name": "PJDSC 2025 Team",
        "email": "vonus.team@pjdsc.edu.ph",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Configure CORS for AR mobile app integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv('CORS_ORIGINS', '*').split(','),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# API prefix
API_PREFIX = os.getenv('API_PREFIX', '/api')

# Register routers
app.include_router(
    forecast_router, 
    prefix=API_PREFIX, 
    tags=["🔮 Flood Prediction"],
    responses={
        500: {"description": "Internal server error"},
        422: {"description": "Validation error"}
    }
)

app.include_router(
    flood_zones_router, 
    prefix=API_PREFIX, 
    tags=["📍 Flood Zones"],
    responses={
        500: {"description": "Internal server error"}
    }
)

app.include_router(
    system_router, 
    prefix=API_PREFIX, 
    tags=["⚙️ System Health"],
    responses={
        500: {"description": "Internal server error"}
    }
)

app.include_router(
    history_router, 
    prefix=API_PREFIX, 
    tags=["📊 Forecast History"],
    responses={
        500: {"description": "Internal server error"}
    }
)

app.include_router(
    feedback_router, 
    prefix=API_PREFIX, 
    tags=["💬 User Feedback"],
    responses={
        500: {"description": "Internal server error"},
        422: {"description": "Validation error"}
    }
)

# Root endpoint
@app.get("/", tags=["🏠 Welcome"])
async def root():
    """
    Welcome endpoint for the Vonus AR Flood Forecasting System
    """
    return {
        "message": "Welcome to Vonus AR Flood Forecasting System! 🌊",
        "description": "Advanced flood prediction using fuzzy logic and environmental data",
        "team": "PJDSC 2025 - Colasino, Olata, Pasamante, Rafa, Tolentino",
        "version": os.getenv('APP_VERSION', '1.0.0'),
        "documentation": "/docs",
        "api_prefix": API_PREFIX,
        "endpoints": {
            "forecast": f"{API_PREFIX}/forecast",
            "flood_zones": f"{API_PREFIX}/flood-zones", 
            "system_status": f"{API_PREFIX}/test",
            "history": f"{API_PREFIX}/history",
            "feedback": f"{API_PREFIX}/feedback"
        }
    }

# Health check endpoint
@app.get("/health", tags=["⚙️ System Health"])
async def health_check():
    """
    Simple health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": "2024-10-23T10:00:00Z",
        "service": "Vonus AR Flood Forecasting System"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "timestamp": "2024-10-23T10:00:00Z"
        }
    )

# Run the application
if __name__ == "__main__":
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )