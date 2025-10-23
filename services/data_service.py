import json
import os
from typing import List, Dict, Optional
from datetime import datetime
from .fuzzy_logic import flood_fuzzy_system


class DataService:
    """Service for handling data operations and location-based queries"""
    
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self._load_datasets()
    
    def _load_datasets(self):
        """Load all JSON datasets into memory"""
        try:
            # Load PAGASA climate data
            with open(os.path.join(self.data_dir, 'pagasa_climap.json'), 'r') as f:
                self.pagasa_data = json.load(f)
            
            # Load LiPAD flood zones
            with open(os.path.join(self.data_dir, 'lipad_flood_zones.json'), 'r') as f:
                self.lipad_data = json.load(f)
            
            # Load NOAH rainfall events
            with open(os.path.join(self.data_dir, 'noah_rainfall_events.json'), 'r') as f:
                self.noah_data = json.load(f)
                
        except FileNotFoundError as e:
            print(f"Warning: Could not load dataset: {e}")
            self.pagasa_data = {}
            self.lipad_data = {}
            self.noah_data = {}
    
    def get_location_info(self, latitude: float, longitude: float) -> str:
        """Get location name based on coordinates"""
        
        # Simple distance calculation to find nearest barangay
        min_distance = float('inf')
        nearest_location = "Quezon City, Unknown Barangay"
        
        if 'rainfall_data' in self.pagasa_data:
            for location in self.pagasa_data['rainfall_data']:
                coords = location['coordinates']
                distance = ((latitude - coords[0]) ** 2 + (longitude - coords[1]) ** 2) ** 0.5
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_location = f"Quezon City, {location['barangay']}"
        
        return nearest_location
    
    def get_historical_rainfall(self, latitude: float, longitude: float) -> float:
        """Get historical average rainfall for location"""
        
        # Find nearest location and return average rainfall
        min_distance = float('inf')
        avg_rainfall = 50.0  # Default value
        
        if 'rainfall_data' in self.pagasa_data:
            for location in self.pagasa_data['rainfall_data']:
                coords = location['coordinates']
                distance = ((latitude - coords[0]) ** 2 + (longitude - coords[1]) ** 2) ** 0.5
                
                if distance < min_distance:
                    min_distance = distance
                    monthly_data = location['monthly_average_mm']
                    # Calculate daily average from annual average
                    avg_rainfall = location['annual_average_mm'] / 365
        
        return avg_rainfall
    
    def get_flood_zones(self) -> List[Dict]:
        """Get all flood zones from LiPAD data"""
        
        if 'flood_zones' in self.lipad_data:
            return self.lipad_data['flood_zones']
        
        return []
    
    def get_drainage_capacity(self, latitude: float, longitude: float) -> float:
        """Estimate drainage capacity based on location and historical data"""
        
        # Find corresponding flood zone
        min_distance = float('inf')
        drainage_capacity = 0.5  # Default moderate capacity
        
        flood_zones = self.get_flood_zones()
        
        for zone in flood_zones:
            # Calculate distance to zone center (simplified)
            if zone['coordinates']:
                zone_center = zone['coordinates'][0]  # First coordinate
                distance = ((latitude - zone_center[0]) ** 2 + (longitude - zone_center[1]) ** 2) ** 0.5
                
                if distance < min_distance:
                    min_distance = distance
                    # Estimate drainage based on hazard level
                    hazard_level = zone['hazard_level']
                    if hazard_level == 'Low':
                        drainage_capacity = 0.8
                    elif hazard_level == 'Medium':
                        drainage_capacity = 0.6
                    elif hazard_level == 'High':
                        drainage_capacity = 0.4
                    elif hazard_level == 'Critical':
                        drainage_capacity = 0.2
        
        return drainage_capacity
    
    def predict_flood_risk(self, latitude: float, longitude: float, rainfall_mm: float, 
                          soil_saturation: float, drainage_capacity: float) -> Dict:
        """Generate flood prediction using fuzzy logic"""
        
        # Get location information
        location = self.get_location_info(latitude, longitude)
        
        # Use fuzzy logic system for prediction
        prediction = flood_fuzzy_system.predict_flood_risk(
            rainfall_mm, soil_saturation, drainage_capacity
        )
        
        # Enhance prediction with location-specific data
        enhanced_prediction = {
            'location': location,
            'flood_risk_level': prediction['risk_level'],
            'predicted_depth_m': prediction['predicted_depth_m'],
            'confidence': prediction['confidence'],
            'advisory': prediction['advisory']
        }
        
        return enhanced_prediction


class HistoryService:
    """Service for managing forecast history and feedback"""
    
    def __init__(self):
        self.history_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'data', 
            'forecast_history.json'
        )
        self.feedback_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'data', 
            'user_feedback.json'
        )
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """Ensure history and feedback files exist"""
        
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w') as f:
                json.dump({'records': []}, f)
        
        if not os.path.exists(self.feedback_file):
            with open(self.feedback_file, 'w') as f:
                json.dump({'feedback': []}, f)
    
    def save_forecast(self, request_data: Dict, response_data: Dict) -> str:
        """Save forecast to history"""
        
        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
        except:
            history = {'records': []}
        
        record_id = f"FC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        record = {
            'record_id': record_id,
            'request_data': request_data,
            'response_data': response_data,
            'timestamp': datetime.now().isoformat()
        }
        
        history['records'].append(record)
        
        # Keep only last 100 records
        if len(history['records']) > 100:
            history['records'] = history['records'][-100:]
        
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        return record_id
    
    def get_history(self, limit: int = 50) -> List[Dict]:
        """Get forecast history"""
        
        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
                return history['records'][-limit:]
        except:
            return []
    
    def save_feedback(self, feedback_data: Dict) -> str:
        """Save user feedback"""
        
        try:
            with open(self.feedback_file, 'r') as f:
                feedback = json.load(f)
        except:
            feedback = {'feedback': []}
        
        feedback_id = f"FB-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        feedback_record = {
            'feedback_id': feedback_id,
            **feedback_data,
            'timestamp': datetime.now().isoformat()
        }
        
        feedback['feedback'].append(feedback_record)
        
        with open(self.feedback_file, 'w') as f:
            json.dump(feedback, f, indent=2)
        
        return feedback_id


# Service instances
data_service = DataService()
history_service = HistoryService()