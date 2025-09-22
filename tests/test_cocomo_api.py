#!/usr/bin/env python3
"""
Test script cho COCOMO II API
"""

from cocomo_ii_api import CocomoIIAPI

def test_api():
    # Khởi tạo API
    api = CocomoIIAPI()
    
    # In thông tin mô hình
    print("\n=== THÔNG TIN MÔ HÌNH ===")
    model_info = api.get_model_info()
    print(f"Các mô hình có sẵn: {', '.join(model_info['models'])}")
    print(f"Các đặc trưng được sử dụng: {', '.join(model_info['features'])}")
    
    # Test với dữ liệu LOC
    print("\n=== DỰ ĐOÁN VỚI KLOC ===")
    sizes = [5, 10, 20, 50, 100]
    for size in sizes:
        result = api.predict('LOC', size)
        print(f"\nDự đoán cho {size} KLOC:")
        print(f"  - Effort: {result['predictions']['effort_pm']:.2f} người-tháng")
        print(f"  - Thời gian: {result['predictions']['time_months']:.2f} tháng")
        print(f"  - Số nhà phát triển: {result['predictions']['developers']} người")
    
    # Test với dữ liệu FP
    print("\n=== DỰ ĐOÁN VỚI FUNCTION POINTS ===")
    sizes = [100, 200, 500, 1000, 2000]
    for size in sizes:
        result = api.predict('FP', size)
        print(f"\nDự đoán cho {size} Function Points:")
        print(f"  - Effort: {result['predictions']['effort_pm']:.2f} người-tháng")
        print(f"  - Thời gian: {result['predictions']['time_months']:.2f} tháng")
        print(f"  - Số nhà phát triển: {result['predictions']['developers']} người")
    
    # Test với dữ liệu UCP
    print("\n=== DỰ ĐOÁN VỚI USE CASE POINTS ===")
    sizes = [50, 100, 200, 300, 500]
    for size in sizes:
        result = api.predict('UCP', size)
        print(f"\nDự đoán cho {size} Use Case Points:")
        print(f"  - Effort: {result['predictions']['effort_pm']:.2f} người-tháng")
        print(f"  - Thời gian: {result['predictions']['time_months']:.2f} tháng")
        print(f"  - Số nhà phát triển: {result['predictions']['developers']} người")
    
    # So sánh các mô hình
    print("\n=== SO SÁNH CÁC MÔ HÌNH ===")
    size = 20  # KLOC
    print(f"\nDự đoán cho {size} KLOC:")
    for model_name in api.get_available_models():
        result = api.predict('LOC', size, model_name)
        print(f"  - {model_name}: {result['predictions']['effort_pm']:.2f} người-tháng")
    
    # Test với đặc trưng bổ sung
    print("\n=== DỰ ĐOÁN VỚI ĐẶC TRƯNG BỔ SUNG ===")
    extra_features = {
        'manager_exp': 10,       # Kinh nghiệm quản lý (năm)
        'team_exp': 5,           # Kinh nghiệm của team (năm)
        'adjustment': 1.2        # Hệ số điều chỉnh
    }
    result = api.predict('LOC', 20, extra_features=extra_features)
    print(f"\nDự đoán cho 20 KLOC với đặc trưng bổ sung:")
    print(f"  - Effort: {result['predictions']['effort_pm']:.2f} người-tháng")
    print(f"  - Thời gian: {result['predictions']['time_months']:.2f} tháng")
    print(f"  - Số nhà phát triển: {result['predictions']['developers']} người")

if __name__ == "__main__":
    test_api()
