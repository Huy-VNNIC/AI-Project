"""
Test script to validate ML model preprocessor fixes
"""

import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.append(str(PROJECT_ROOT))

from requirement_analyzer.estimator import EffortEstimator
from requirement_analyzer.analyzer import RequirementAnalyzer

def test_model_prediction():
    """Test direct prediction with the ML models"""
    print("Testing ML model prediction...")
    estimator = EffortEstimator()
    
    # Test with manual features
    test_features = {
        'developers': 3, 
        'team_exp': 3, 
        'manager_exp': 3, 
        'size': 1.5, 
        'kloc_per_dev': 0.5, 
        'time_months': 6, 
        'kloc_per_month': 0.25, 
        'points_non_adjust': 20, 
        'adjustment': 1.0, 
        'transactions': 5, 
        'entities': 3, 
        'fp_per_month': 3.3, 
        'fp_per_dev': 6.7, 
        'schema': 1
    }
    
    print(f"Test features: {test_features}")
    
    # Try all models
    for model_name in estimator.ml_models.keys():
        try:
            result = estimator.estimate_from_ml_model(test_features, model_name)
            print(f"Model {model_name}: Effort prediction = {result:.2f} person-months")
        except Exception as e:
            print(f"Error with model {model_name}: {e}")
    
    print("Done testing ML model prediction.\n")

def test_requirement_analysis_and_prediction():
    """Test full workflow from requirements to prediction"""
    print("Testing requirement analysis and prediction...")
    
    # Sample requirements
    test_requirement = """
    Project Requirements:
    1. Develop a web application for customer relationship management.
    2. The application should include user authentication, customer database, 
       reporting dashboard, and email notification system.
    3. The system should handle up to 1000 concurrent users.
    4. The development team has 5 developers with high experience.
    5. The project timeline is 8 months.
    """
    
    print(f"Test requirement document: {test_requirement[:100]}...")
    
    # Create analyzer and estimator
    analyzer = RequirementAnalyzer()
    estimator = EffortEstimator()
    
    # Analyze requirements
    params = analyzer.analyze_requirements_document(test_requirement)
    
    # Print ML features
    print(f"Extracted ML features: {params['ml_features']}")
    
    # Estimate with all integration methods
    for method in ["weighted_average", "best_model", "stacking", "bayesian_average"]:
        try:
            result = estimator.integrated_estimate(params, method)
            print(f"Method {method}: Total effort = {result['total_effort']:.2f} person-months")
        except Exception as e:
            print(f"Error with method {method}: {e}")
    
    print("Done testing requirement analysis and prediction.")

if __name__ == "__main__":
    test_model_prediction()
    test_requirement_analysis_and_prediction()
