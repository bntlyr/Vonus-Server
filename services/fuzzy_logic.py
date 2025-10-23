import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import os
from typing import Dict, Tuple
from dotenv import load_dotenv

load_dotenv()


class FloodFuzzySystem:
    """
    Fuzzy Logic System for Flood Risk Assessment
    
    This system uses fuzzy inference to determine flood risk levels based on:
    - Rainfall intensity (mm/hr)
    - Soil saturation level (0.0-1.0)
    - Drainage capacity (0.0-1.0)
    """
    
    def __init__(self):
        self.setup_fuzzy_variables()
        self.setup_fuzzy_rules()
        self.create_control_system()
        
        # Load configuration from environment
        self.rainfall_threshold_low = float(os.getenv('RAINFALL_THRESHOLD_LOW', 30))
        self.rainfall_threshold_high = float(os.getenv('RAINFALL_THRESHOLD_HIGH', 80))
        self.drainage_threshold_poor = float(os.getenv('DRAINAGE_THRESHOLD_POOR', 0.3))
        self.drainage_threshold_good = float(os.getenv('DRAINAGE_THRESHOLD_GOOD', 0.7))
        self.confidence_threshold = float(os.getenv('CONFIDENCE_THRESHOLD', 0.6))
    
    def setup_fuzzy_variables(self):
        """Define fuzzy variables and their membership functions"""
        
        # Input variables
        self.rainfall = ctrl.Antecedent(np.arange(0, 201, 1), 'rainfall')
        self.soil_saturation = ctrl.Antecedent(np.arange(0, 1.1, 0.01), 'soil_saturation')
        self.drainage_capacity = ctrl.Antecedent(np.arange(0, 1.1, 0.01), 'drainage_capacity')
        
        # Output variable
        self.flood_risk = ctrl.Consequent(np.arange(0, 101, 1), 'flood_risk')
        
        # Rainfall membership functions (mm/hr)
        self.rainfall['light'] = fuzz.trimf(self.rainfall.universe, [0, 0, 40])
        self.rainfall['moderate'] = fuzz.trimf(self.rainfall.universe, [20, 50, 80])
        self.rainfall['heavy'] = fuzz.trimf(self.rainfall.universe, [60, 100, 140])
        self.rainfall['extreme'] = fuzz.trimf(self.rainfall.universe, [120, 200, 200])
        
        # Soil saturation membership functions
        self.soil_saturation['low'] = fuzz.trimf(self.soil_saturation.universe, [0, 0, 0.4])
        self.soil_saturation['medium'] = fuzz.trimf(self.soil_saturation.universe, [0.2, 0.5, 0.8])
        self.soil_saturation['high'] = fuzz.trimf(self.soil_saturation.universe, [0.6, 1.0, 1.0])
        
        # Drainage capacity membership functions
        self.drainage_capacity['poor'] = fuzz.trimf(self.drainage_capacity.universe, [0, 0, 0.4])
        self.drainage_capacity['fair'] = fuzz.trimf(self.drainage_capacity.universe, [0.2, 0.5, 0.8])
        self.drainage_capacity['good'] = fuzz.trimf(self.drainage_capacity.universe, [0.6, 1.0, 1.0])
        
        # Flood risk membership functions
        self.flood_risk['low'] = fuzz.trimf(self.flood_risk.universe, [0, 0, 30])
        self.flood_risk['moderate'] = fuzz.trimf(self.flood_risk.universe, [10, 40, 70])
        self.flood_risk['high'] = fuzz.trimf(self.flood_risk.universe, [50, 75, 90])
        self.flood_risk['critical'] = fuzz.trimf(self.flood_risk.universe, [80, 100, 100])
    
    def setup_fuzzy_rules(self):
        """Define fuzzy inference rules"""
        
        self.rules = [
            # Low risk scenarios
            ctrl.Rule(self.rainfall['light'] & self.soil_saturation['low'] & self.drainage_capacity['good'], 
                     self.flood_risk['low']),
            ctrl.Rule(self.rainfall['light'] & self.soil_saturation['medium'] & self.drainage_capacity['good'], 
                     self.flood_risk['low']),
            ctrl.Rule(self.rainfall['moderate'] & self.soil_saturation['low'] & self.drainage_capacity['good'], 
                     self.flood_risk['low']),
            
            # Moderate risk scenarios
            ctrl.Rule(self.rainfall['light'] & self.soil_saturation['high'] & self.drainage_capacity['fair'], 
                     self.flood_risk['moderate']),
            ctrl.Rule(self.rainfall['moderate'] & self.soil_saturation['medium'] & self.drainage_capacity['fair'], 
                     self.flood_risk['moderate']),
            ctrl.Rule(self.rainfall['moderate'] & self.soil_saturation['low'] & self.drainage_capacity['poor'], 
                     self.flood_risk['moderate']),
            ctrl.Rule(self.rainfall['heavy'] & self.soil_saturation['low'] & self.drainage_capacity['good'], 
                     self.flood_risk['moderate']),
            
            # High risk scenarios
            ctrl.Rule(self.rainfall['heavy'] & self.soil_saturation['medium'] & self.drainage_capacity['fair'], 
                     self.flood_risk['high']),
            ctrl.Rule(self.rainfall['heavy'] & self.soil_saturation['high'] & self.drainage_capacity['poor'], 
                     self.flood_risk['high']),
            ctrl.Rule(self.rainfall['moderate'] & self.soil_saturation['high'] & self.drainage_capacity['poor'], 
                     self.flood_risk['high']),
            ctrl.Rule(self.rainfall['extreme'] & self.soil_saturation['low'] & self.drainage_capacity['fair'], 
                     self.flood_risk['high']),
            
            # Critical risk scenarios
            ctrl.Rule(self.rainfall['extreme'] & self.soil_saturation['medium'] & self.drainage_capacity['poor'], 
                     self.flood_risk['critical']),
            ctrl.Rule(self.rainfall['extreme'] & self.soil_saturation['high'] & self.drainage_capacity['poor'], 
                     self.flood_risk['critical']),
            ctrl.Rule(self.rainfall['heavy'] & self.soil_saturation['high'] & self.drainage_capacity['poor'], 
                     self.flood_risk['critical']),
            ctrl.Rule(self.rainfall['extreme'] & self.soil_saturation['high'] & self.drainage_capacity['fair'], 
                     self.flood_risk['critical']),
        ]
    
    def create_control_system(self):
        """Create the fuzzy control system"""
        self.flood_ctrl = ctrl.ControlSystem(self.rules)
        self.flood_simulation = ctrl.ControlSystemSimulation(self.flood_ctrl)
    
    def predict_flood_risk(self, rainfall_mm: float, soil_saturation: float, 
                          drainage_capacity: float) -> Dict:
        """
        Predict flood risk based on input parameters
        
        Args:
            rainfall_mm: Rainfall in millimeters per hour
            soil_saturation: Soil saturation level (0.0-1.0)
            drainage_capacity: Drainage capacity (0.0-1.0)
            
        Returns:
            Dictionary containing risk level, confidence, and predicted depth
        """
        
        # Set inputs
        self.flood_simulation.input['rainfall'] = min(200, max(0, rainfall_mm))
        self.flood_simulation.input['soil_saturation'] = min(1.0, max(0.0, soil_saturation))
        self.flood_simulation.input['drainage_capacity'] = min(1.0, max(0.0, drainage_capacity))
        
        # Compute result
        self.flood_simulation.compute()
        
        # Get risk score (0-100)
        risk_score = self.flood_simulation.output['flood_risk']
        
        # Convert to categorical risk level
        risk_level = self._get_risk_level(risk_score)
        
        # Calculate confidence based on input consistency
        confidence = self._calculate_confidence(rainfall_mm, soil_saturation, drainage_capacity, risk_score)
        
        # Estimate flood depth
        predicted_depth = self._estimate_flood_depth(risk_score, rainfall_mm)
        
        # Generate advisory message
        advisory = self._generate_advisory(risk_level, predicted_depth)
        
        return {
            'risk_score': round(risk_score, 2),
            'risk_level': risk_level,
            'confidence': round(confidence, 2),
            'predicted_depth_m': round(predicted_depth, 2),
            'advisory': advisory
        }
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Convert numeric risk score to categorical level"""
        if risk_score <= 30:
            return "Low"
        elif risk_score <= 55:
            return "Moderate"
        elif risk_score <= 80:
            return "High"
        else:
            return "Critical"
    
    def _calculate_confidence(self, rainfall: float, soil_sat: float, 
                            drainage: float, risk_score: float) -> float:
        """Calculate prediction confidence based on input parameters"""
        
        # Base confidence
        confidence = 0.7
        
        # Adjust based on extreme conditions (higher confidence)
        if rainfall > 100 or rainfall < 10:
            confidence += 0.1
        
        if soil_sat > 0.8 or soil_sat < 0.2:
            confidence += 0.05
            
        if drainage < 0.3 or drainage > 0.8:
            confidence += 0.05
        
        # Adjust based on risk consistency
        if (rainfall > 80 and risk_score > 60) or (rainfall < 30 and risk_score < 40):
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _estimate_flood_depth(self, risk_score: float, rainfall: float) -> float:
        """Estimate flood depth based on risk score and rainfall"""
        
        # Base depth calculation
        base_depth = (risk_score / 100) * 3.0  # Max 3 meters
        
        # Adjust for rainfall intensity
        rainfall_factor = min(2.0, rainfall / 50)  # Rainfall intensity factor
        
        # Calculate estimated depth
        estimated_depth = base_depth * rainfall_factor * 0.7
        
        return max(0.0, estimated_depth)
    
    def _generate_advisory(self, risk_level: str, depth: float) -> str:
        """Generate human-readable advisory message"""
        
        advisories = {
            "Low": f"Minimal flood risk. Expected depth: {depth:.1f}m. Normal activities can continue with weather monitoring.",
            "Moderate": f"Moderate flood risk. Expected depth: {depth:.1f}m. Avoid low-lying areas and monitor weather updates.",
            "High": f"High flood risk. Expected depth: {depth:.1f}m. Evacuate flood-prone areas and seek higher ground within 2 hours.",
            "Critical": f"Critical flood risk. Expected depth: {depth:.1f}m. Immediate evacuation required. Move to higher ground now!"
        }
        
        return advisories.get(risk_level, "Unknown risk level. Please contact local authorities.")


# Singleton instance
flood_fuzzy_system = FloodFuzzySystem()