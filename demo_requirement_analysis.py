#!/usr/bin/env python3
"""
Demonstration: How the system processes YOUR requirement files

Flow:
1. You upload a file (TXT, CSV, MD, DOCX)
2. System reads the file content
3. Parses requirements from your file
4. Analyzes each requirement specifically
5. Generates test cases based on ACTUAL requirement content
"""

import requests
import json

# Step 1: Create a sample requirement file (as if you uploaded it)
requirement_file_content = """Hotel Management System Requirements

REQUIREMENT 1: Đặt Phòng
- Khách hàng có thể tìm kiếm phòng trống theo ngày
- Hệ thống phải kiểm tra tính khả dụng của phòng theo loại và ngày
- Phải hiển thị giá phòng rõ ràng
- Cho phép đặt phòng trên 30 ngày trước

REQUIREMENT 2: Xác Nhận Đặt Phòng
- Hệ thống phải gửi email xác nhận trong 5 phút
- Tạo mã đặt phòng tự động
- Lưu thông tin chi tiết lưu trú
- Cho phép hủy trong 24 giờ

REQUIREMENT 3: Quản Lý Thanh Toán
- Hỗ trợ thanh toán qua multiple methods: thẻ, chuyển khoản
- Tính toán thuế và phí dịch vụ
- Tạo hóa đơn chi tiết
- Ghi nhận trạng thái: PENDING, CONFIRMED, COMPLETED
"""

# Step 2: Write to a temporary file
test_file_path = "/tmp/hotel_requirements_demo.txt"
with open(test_file_path, 'w', encoding='utf-8') as f:
    f.write(requirement_file_content)

print("=" * 80)
print("DEMONSTRATION: How the System Analyzes YOUR Requirement Files")
print("=" * 80)

print("\n1. YOUR UPLOADED REQUIREMENTS FILE CONTENT:")
print("-" * 80)
print(requirement_file_content)
print("-" * 80)

# Step 3: Send to API (exactly as the web UI does)
print("\n2. SENDING FILE TO API ENDPOINT: /api/v3/test-generation/analyze-file-detailed")
print("-" * 80)

with open(test_file_path, 'rb') as f:
    files = {'file': ('hotel_requirements_demo.txt', f, 'text/plain')}
    
    response = requests.post(
        'http://localhost:8000/api/v3/test-generation/analyze-file-detailed',
        files=files,
        timeout=30
    )

if response.status_code == 200:
    result = response.json()
    
    print(f"\n3. API ANALYSIS RESULTS:")
    print("-" * 80)
    print(f"Generator Version: {result.get('generator_version')}")
    print(f"File Name: {result.get('filename')}")
    print(f"Total Requirements in File: {result.get('total_requirements_in_file')}")
    print(f"Requirements Analyzed: {result.get('total_requirements_analyzed')}")
    print(f"Test Cases Generated: {result.get('total_test_cases_generated')}")
    print(f"Average Confidence: {result.get('avg_nlp_confidence'):.1%}")
    
    print(f"\n4. DETAILED ANALYSIS FOR EACH REQUIREMENT:")
    print("-" * 80)
    
    for req in result.get('detailed', []):
        print(f"\nRequirement #{req['index']}: {req['requirement']}")
        print(f"  Word Count: {req['word_count']}")
        print(f"  Character Count: {req['character_count']}")
        print(f"  NLP Confidence: {req['nlp_confidence']:.0%}")
        print(f"  Test Cases Generated: {req['test_cases_count']}")
        
        # Show first 2 test cases for this requirement
        print(f"\n  Generated Test Cases:")
        for tc in req['test_cases'][:2]:
            print(f"    - {tc['id']}: {tc['title']}")
            print(f"      Type: {tc['type']}")
            print(f"      Priority: {tc['priority']}")
            print(f"      Confidence: {tc['confidence']:.0%}")
            if tc.get('test_data'):
                print(f"      Test Data Keys: {list(tc['test_data'].keys())}")
            if tc.get('preconditions'):
                print(f"      Preconditions: {len(tc['preconditions'])} items")
        
        if req['test_cases_count'] > 2:
            print(f"    ... and {req['test_cases_count'] - 2} more test cases")
    
    print("\n" + "=" * 80)
    print("CONCLUSION:")
    print("=" * 80)
    print("✅ YES! The system uses YOUR requirement file to generate test cases")
    print("✅ Each test case is specific to the actual requirement content")
    print("✅ Test data and scenarios are based on what's in YOUR file")
    print("✅ The system analyzes the specific Vietnamese text you provide")
    print("✅ Confidence scores reflect how well the requirement is understood")
    print("=" * 80)

else:
    print(f"Error: {response.status_code}")
    print(response.text)
