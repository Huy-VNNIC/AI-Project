#!/usr/bin/env python3
"""
Test script to verify the standardized API output format
"""

import sys
import requests
import json
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

try:
    # Try to import directly (when run in the codebase)
    from requirement_analyzer.estimator import EffortEstimator
except ImportError:
    print("Cannot import EffortEstimator directly, will test via API")

def test_direct_estimation():
    """Test the estimator directly to verify output format"""
    try:
        estimator = EffortEstimator()
        
        # Sample requirement text
        sample_text = """
        The system shall allow users to register accounts with email verification.
        Users should be able to login using their credentials.
        The system needs to support password reset functionality.
        Administrators should be able to manage user accounts.
        """
        
        # Get estimation
        result = estimator.estimate_from_requirements(sample_text)
        
        # Print formatted result
        print("\n=== DIRECT ESTIMATION RESULT ===")
        print(json.dumps(result, indent=2))
        
        # Verify the model_estimates format
        if 'estimation' in result and 'model_estimates' in result['estimation']:
            print("\n=== MODEL ESTIMATES FORMAT VERIFICATION ===")
            for model, details in result['estimation']['model_estimates'].items():
                print(f"\nModel: {model}")
                if isinstance(details, dict) and 'effort' in details:
                    print(f"✅ Format OK: {details}")
                else:
                    print(f"❌ Format ERROR: {details}")
        
    except Exception as e:
        print(f"Error testing direct estimation: {e}")

def test_api_estimation(url="http://localhost:8001/api/estimate"):
    """Test the API endpoint to verify output format"""
    try:
        # Sample request data
        data = {
            "text": """
            The system shall allow users to register accounts with email verification.
            Users should be able to login using their credentials.
            The system needs to support password reset functionality.
            Administrators should be able to manage user accounts.
            """
        }
        
        # Send request
        print(f"\n=== SENDING API REQUEST TO {url} ===")
        response = requests.post(url, json=data)
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            print("\n=== API ESTIMATION RESULT ===")
            print(json.dumps(result, indent=2))
            
            # Verify the model_estimates format
            if 'estimation' in result and 'model_estimates' in result['estimation']:
                print("\n=== MODEL ESTIMATES FORMAT VERIFICATION ===")
                for model, details in result['estimation']['model_estimates'].items():
                    print(f"\nModel: {model}")
                    if isinstance(details, dict) and 'effort' in details:
                        print(f"✅ Format OK: {details}")
                    else:
                        print(f"❌ Format ERROR: {details}")
        else:
            print(f"API Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error testing API: {e}")
        
if __name__ == "__main__":
    # Run both tests
    test_direct_estimation()
    
    # Only test API if the service is running
    api_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8001/api/estimate"
    print(f"\nTo test the API endpoint, make sure the API service is running.")
    test_input = input(f"Do you want to test the API at {api_url}? (y/N): ")
    
    if test_input.lower() == 'y':
        test_api_estimation(api_url)