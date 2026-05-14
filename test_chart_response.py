#!/usr/bin/env python3
"""
Test script to check API response format for chart display
"""
import json
import requests

def test_upload_endpoint():
    """Test the upload-requirements endpoint"""
    
    # Sample requirements text
    test_text = """
# Tài liệu Yêu cầu: Hệ thống Ngân hàng Số
## 1. Giới thiệu
Tài liệu này mô tả các yêu cầu cho Hệ thống Ngân hàng Số

## 2. Yêu cầu chức năng
### 2.1 Module Quản lý Tài khoản
1. Hệ thống phải cho phép mở tài khoản trực tuyến
2. Hệ thống phải hỗ trợ nhiều loại tài khoản
3. Hệ thống phải hiển thị số dư tài khoản thời gian thực
    """
    
    # Write to temp file
    with open('/tmp/test_requirements.txt', 'w', encoding='utf-8') as f:
        f.write(test_text)
    
    # Upload file
    print("📤 Uploading test requirements file...")
    with open('/tmp/test_requirements.txt', 'rb') as f:
        files = {'file': ('test_requirements.txt', f, 'text/plain')}
        data = {'method': 'weighted_average'}
        
        try:
            response = requests.post('http://localhost:8000/upload-requirements', files=files, data=data)
            
            print(f"\n📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                print("\n✅ Response received successfully!")
                print("\n" + "="*60)
                print("RESPONSE STRUCTURE:")
                print("="*60)
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
                print("\n" + "="*60)
                print("CHECKING FOR CHART DATA:")
                print("="*60)
                
                # Check for model_estimates
                estimation = result.get('estimation', result)
                model_estimates = estimation.get('model_estimates') or result.get('model_estimates')
                
                if model_estimates:
                    print("✅ model_estimates found!")
                    print(f"   Number of models: {len(model_estimates)}")
                    print(f"   Models: {list(model_estimates.keys())}")
                    
                    print("\n📊 Individual Model Data:")
                    for model_key, model_data in model_estimates.items():
                        if isinstance(model_data, dict):
                            name = model_data.get('name', model_key)
                            effort = model_data.get('effort', 'N/A')
                            confidence = model_data.get('confidence', 'N/A')
                            print(f"   - {name}: effort={effort}, confidence={confidence}")
                        else:
                            print(f"   - {model_key}: {type(model_data)} (unexpected format)")
                else:
                    print("❌ model_estimates NOT found!")
                    print("   Available keys in estimation:", list(estimation.keys()))
                    print("   Available keys in root:", list(result.keys()))
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_upload_endpoint()
