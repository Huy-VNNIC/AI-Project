"""
Module implementing COCOMO II effort estimation model
"""

import math
from typing import Dict, Any

class CocomoIIPredictor:
    """
    Implements the Constructive Cost Model II (COCOMO II) for software effort estimation
    """
    
    def __init__(self):
        """Initialize the COCOMO II predictor with default parameters"""
        self.a = 2.94  # Constant factor
        self.b = 1.1   # Scale factor exponent
        
        # Effort Multipliers with default values
        self.effort_multipliers = {
            'reliability': 1.0,      # Required software reliability
            'data_size': 1.0,        # Size of application database
            'complexity': 1.0,       # Product complexity
            'reuse': 1.0,            # Required reusability
            'documentation': 1.0,    # Documentation match to life-cycle needs
            'time_constraint': 1.0,  # Execution time constraint
            'storage_constraint': 1.0,  # Main storage constraint
            'platform_volatility': 1.0,  # Platform volatility
            'analyst_capability': 1.0,   # Analyst capability
            'programmer_capability': 1.0, # Programmer capability
            'personnel_continuity': 1.0,  # Personnel continuity
            'language_experience': 1.0,   # Programming language experience
            'tool_experience': 1.0,       # Use of software tools
            'schedule_constraint': 1.0,   # Required development schedule
        }
        
        # Scale Factors with default values
        self.scale_factors = {
            'precedentedness': 1.0,       # Precedentedness
            'development_flexibility': 1.0, # Development flexibility
            'architecture_risk': 1.0,      # Architecture/risk resolution
            'team_cohesion': 1.0,          # Team cohesion
            'process_maturity': 1.0,       # Process maturity
        }
    
    def estimate_effort(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate effort using COCOMO II model
        
        Args:
            features (dict): Features extracted from requirements
            
        Returns:
            dict: Estimation results with effort in person-months
        """
        # Extract KLOC (thousands of lines of code) from features
        size = features.get('size', 0)
        if not size:
            size = features.get('size_kloc', 0)
        
        if not size or size < 0.1:
            # Use rule of thumb for very small projects
            if 'num_requirements' in features:
                num_req = features['num_requirements']
                size = max(0.1, num_req * 0.5)  # 0.5 KLOC per requirement as baseline
            else:
                size = 1.0  # Default to 1 KLOC
        
        # Complexity adjustment (1.0 is nominal, higher is more complex)
        complexity = features.get('complexity', 1.0)
        
        # Calculate Effort Adjustment Factor (EAF)
        eaf = 1.0
        eaf *= self._get_reliability_factor(features)
        eaf *= self._get_complexity_factor(complexity)
        
        # Calculate exponent
        exponent = self.b
        
        # Calculate effort in person-months
        effort = self.a * (size ** exponent) * eaf
        
        # Calculate duration in months (using standard COCOMO formula)
        duration = 3.0 * (effort ** 0.33)
        
        # Calculate average staffing
        staffing = effort / duration if duration > 0 else 1
        
        # Calculate confidence based on the input quality
        confidence = self._calculate_confidence(features)
        
        return {
            'effort_months': effort,
            'duration': duration,
            'team_size': staffing,
            'confidence': confidence
        }
    
    def _get_reliability_factor(self, features):
        """Get reliability factor from features"""
        reliability = features.get('reliability', 1.0)
        
        if reliability <= 0.8:
            return 0.82  # Very low (positive effect)
        elif reliability <= 0.9:
            return 0.92  # Low
        elif reliability <= 1.1:
            return 1.00  # Nominal
        elif reliability <= 1.3:
            return 1.10  # High
        else:
            return 1.26  # Very high (negative effect)
    
    def _get_complexity_factor(self, complexity):
        """Get complexity factor"""
        if complexity <= 0.8:
            return 0.73  # Very low
        elif complexity <= 0.9:
            return 0.87  # Low
        elif complexity <= 1.1:
            return 1.00  # Nominal
        elif complexity <= 1.3:
            return 1.17  # High
        else:
            return 1.34  # Very high
    
    def _calculate_confidence(self, features):
        """Calculate confidence level based on input features"""
        # Simple confidence calculation (0.0 to 1.0)
        base_confidence = 0.7  # Base confidence
        
        # Adjust based on size - lower confidence for very small or very large
        size = features.get('size', 0)
        if size < 1:
            size_factor = 0.9
        elif size > 100:
            size_factor = 0.8
        else:
            size_factor = 1.0
            
        # Adjust based on complexity
        complexity = features.get('complexity', 1.0)
        if complexity > 1.2:
            complexity_factor = 0.9
        else:
            complexity_factor = 1.0
            
        final_confidence = base_confidence * size_factor * complexity_factor
        
        return round(final_confidence, 2)