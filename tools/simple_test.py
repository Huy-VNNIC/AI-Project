#!/usr/bin/env python3
"""
Simple test script for the requirement analyzer API
"""

import requests
import json
import sys

def test_estimate():
    """Test the /estimate endpoint"""
    print("Testing /estimate endpoint...")
    
    url = "http://localhost:8000/estimate"
    data = {
        "text": "Phát triển hệ thống quản lý bệnh viện toàn diện với các mô-đun quản lý bệnh nhân, bác sĩ, lịch hẹn, thanh toán, phòng khám, thuốc và báo cáo thống kê. Hệ thống phải đảm bảo bảo mật dữ liệu y tế tuân thủ các quy định về bảo vệ dữ liệu, có khả năng tích hợp với thiết bị y tế, hỗ trợ nhiều người dùng đồng thời, và có giao diện thân thiện. Dự án dự kiến sẽ được thực hiện bởi 5 lập trình viên trong thời gian 8 tháng, với mức độ phức tạp cao do các yêu cầu nghiêm ngặt về bảo mật và hiệu suất. Kích thước dự kiến khoảng 50.000 dòng mã.",
        "method": "weighted_average",
        "ml_features": {
            "size": 50.0,
            "complexity": 1.5,
            "team_size": 5,
            "experience": 1.0
        }
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Response status code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("\nEstimation result:")
            print(f"Effort: {result.get('effort_pm')} person-months")
            print(f"Duration: {result.get('duration')} months")
            print(f"Team size: {result.get('team_size')} people")
            
            # Check ML models
            ml_models_found = False
            print("\nModel estimates:")
            for model_name, model_data in result.get('model_estimates', {}).items():
                if model_name.startswith('ml_'):
                    ml_models_found = True
                    print(f" ML Model {model_name}: {model_data.get('estimate')} person-months (Confidence: {model_data.get('confidence')}%)")
            
            if ml_models_found:
                print("\n ML models are working correctly!")
                return True
            else:
                print("\n No ML models found in the response.")
                return False
        else:
            print(f"Error response: {response.text}")
            return False
    except Exception as e:
        print(f"Error testing API: {e}")
        return False

def main():
    """Main function"""
    print("Testing if our fixes worked...")
    success = test_estimate()
    
    if success:
        print("\n All fixes were successful!")
    else:
        print("\n Some issues remain.")
        sys.exit(1)

if __name__ == "__main__":
    main()
