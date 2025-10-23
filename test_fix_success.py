#!/usr/bin/env python3
"""
Test client for the requirement analyzer API - check for specific fixes
"""

import requests
import json
import sys
from pprint import pprint

def test_estimation_endpoint():
    """Test the estimation endpoint"""
    print("Testing estimation endpoint...")
    
    # Simple requirement text
    requirement_text = """
    Phát triển hệ thống quản lý khách hàng cho ngân hàng. 
    Hệ thống sẽ có các chức năng: quản lý thông tin khách hàng, 
    lịch sử giao dịch, phân tích hành vi, gửi thông báo tự động. 
    Dự án có quy mô trung bình, khoảng 30.000 dòng mã, 
    độ phức tạp trung bình. Team phát triển gồm 4 người với 2 năm kinh nghiệm.
    """
    
    # API endpoint
    url = "http://localhost:8000/estimate"
    
    # Request data
    data = {
        "requirements": requirement_text,
        "additional_params": {
            "complexity": 1.3,
            "team_size": 4,
            "experience": 2.0
        }
    }
    
    # Make POST request
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        
        print("API Response:")
        print("-" * 50)
        pprint(result)
        
        # Check if the ML models were used
        print("\nChecking if ML models were used correctly...")
        model_estimates = result.get("model_estimates", {})
        ml_models_used = False
        
        for model_name, model_data in model_estimates.items():
            if model_name.startswith("ml_"):
                ml_models_used = True
                print(f"✅ ML model {model_name} was used: {model_data}")
        
        if ml_models_used:
            print("✅ SUCCESS: ML models were used in the estimation!")
        else:
            print("❌ ERROR: No ML models were used in the estimation!")
            
        return ml_models_used
        
    except Exception as e:
        print(f"Error testing API: {e}")
        return False

def main():
    """Main function"""
    print("Testing if fixes for ML models and preprocessor worked...\n")
    
    success = test_estimation_endpoint()
    
    if success:
        print("\n🎉 All fixes were successful! The system is now working properly.")
    else:
        print("\n❌ Some issues remain. The system is not fully fixed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
