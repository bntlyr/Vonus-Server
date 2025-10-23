import numpy as np
import os
from typing import Dict, Tuple
from dotenv import load_dotenv

load_dotenv()


class FloodFuzzySystem:
    """
    Simplified Fuzzy Logic System for Flood Risk Assessment
    
    This system uses manual fuzzy inference to determine flood risk levels based on:
    - Rainfall intensity (mm/hr)
    - Soil saturation level (0.0-1.0)
    - Drainage capacity (0.0-1.0)
    """
    
    def __init__(self):
        # Load configuration from environment
        self.rainfall_threshold_low = float(os.getenv('RAINFALL_THRESHOLD_LOW', 30))
        self.rainfall_threshold_high = float(os.getenv('RAINFALL_THRESHOLD_HIGH', 80))
        self.drainage_threshold_poor = float(os.getenv('DRAINAGE_THRESHOLD_POOR', 0.3))
        self.drainage_threshold_good = float(os.getenv('DRAINAGE_THRESHOLD_GOOD', 0.7))
        self.confidence_threshold = float(os.getenv('CONFIDENCE_THRESHOLD', 0.6))
    
    def _triangular_membership(self, x: float, a: float, b: float, c: float) -> float:
        """Calculate triangular membership function value"""
        if x <= a or x >= c:
            return 0.0
        elif a < x <= b:
            return (x - a) / (b - a)
        elif b < x < c:
            return (c - x) / (c - b)
        else:
            return 0.0
    
    def _get_rainfall_membership(self, rainfall: float) -> Dict[str, float]:
        """Get membership values for rainfall categories"""
        return {
            'light': self._triangular_membership(rainfall, 0, 0, 40),
            'moderate': self._triangular_membership(rainfall, 20, 50, 80),
            'heavy': self._triangular_membership(rainfall, 60, 100, 140),
            'extreme': self._triangular_membership(rainfall, 120, 200, 200)
        }
    
    def _get_soil_membership(self, soil_saturation: float) -> Dict[str, float]:
        """Get membership values for soil saturation categories"""
        return {
            'low': self._triangular_membership(soil_saturation, 0, 0, 0.4),
            'medium': self._triangular_membership(soil_saturation, 0.2, 0.5, 0.8),
            'high': self._triangular_membership(soil_saturation, 0.6, 1.0, 1.0)
        }
    
    def _get_drainage_membership(self, drainage_capacity: float) -> Dict[str, float]:
        """Get membership values for drainage capacity categories"""
        return {
            'poor': self._triangular_membership(drainage_capacity, 0, 0, 0.4),
            'fair': self._triangular_membership(drainage_capacity, 0.2, 0.5, 0.8),
            'good': self._triangular_membership(drainage_capacity, 0.6, 1.0, 1.0)
        }
    
    def _apply_fuzzy_rules(self, rainfall_mem: Dict, soil_mem: Dict, drainage_mem: Dict) -> Dict[str, float]:
        """Apply fuzzy rules and return risk level memberships"""
        
        risk_memberships = {'low': 0, 'moderate': 0, 'high': 0, 'critical': 0}
        
        # Low risk scenarios
        low_rules = [
            min(rainfall_mem['light'], soil_mem['low'], drainage_mem['good']),
            min(rainfall_mem['light'], soil_mem['medium'], drainage_mem['good']),
            min(rainfall_mem['moderate'], soil_mem['low'], drainage_mem['good'])
        ]
        risk_memberships['low'] = max(low_rules)
        
        # Moderate risk scenarios
        moderate_rules = [
            min(rainfall_mem['light'], soil_mem['high'], drainage_mem['fair']),
            min(rainfall_mem['moderate'], soil_mem['medium'], drainage_mem['fair']),
            min(rainfall_mem['moderate'], soil_mem['low'], drainage_mem['poor']),
            min(rainfall_mem['heavy'], soil_mem['low'], drainage_mem['good'])
        ]
        risk_memberships['moderate'] = max(moderate_rules)
        
        # High risk scenarios
        high_rules = [
            min(rainfall_mem['heavy'], soil_mem['medium'], drainage_mem['fair']),
            min(rainfall_mem['heavy'], soil_mem['high'], drainage_mem['poor']),
            min(rainfall_mem['moderate'], soil_mem['high'], drainage_mem['poor']),
            min(rainfall_mem['extreme'], soil_mem['low'], drainage_mem['fair'])
        ]
        risk_memberships['high'] = max(high_rules)
        
        # Critical risk scenarios
        critical_rules = [
            min(rainfall_mem['extreme'], soil_mem['medium'], drainage_mem['poor']),
            min(rainfall_mem['extreme'], soil_mem['high'], drainage_mem['poor']),
            min(rainfall_mem['heavy'], soil_mem['high'], drainage_mem['poor']),
            min(rainfall_mem['extreme'], soil_mem['high'], drainage_mem['fair'])
        ]
        risk_memberships['critical'] = max(critical_rules)
        
        return risk_memberships
    
    def _defuzzify(self, risk_memberships: Dict[str, float]) -> float:
        """Convert fuzzy output to crisp risk score using centroid method"""
        
        # Center points for each risk category
        centers = {'low': 15, 'moderate': 40, 'high': 70, 'critical': 90}
        
        # Calculate weighted average
        numerator = sum(membership * centers[level] for level, membership in risk_memberships.items())
        denominator = sum(risk_memberships.values())
        
        if denominator == 0:
            return 15  # Default to low risk
        
        return numerator / denominator
    
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
        
        # Normalize inputs
        rainfall_mm = min(200, max(0, rainfall_mm))
        soil_saturation = min(1.0, max(0.0, soil_saturation))
        drainage_capacity = min(1.0, max(0.0, drainage_capacity))
        
        # Get membership values
        rainfall_mem = self._get_rainfall_membership(rainfall_mm)
        soil_mem = self._get_soil_membership(soil_saturation)
        drainage_mem = self._get_drainage_membership(drainage_capacity)
        
        # Apply fuzzy rules
        risk_memberships = self._apply_fuzzy_rules(rainfall_mem, soil_mem, drainage_mem)
        
        # Defuzzify to get risk score
        risk_score = self._defuzzify(risk_memberships)
        
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