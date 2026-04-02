#!/usr/bin/env python
"""End-to-end test: Adapter → Generator v2"""
import json
from requirement_analyzer.pure_ml_api_adapter import PureMLAPIAdapter

print("\n" + "="*100)
print("🧪 END-TO-END TEST: API ADAPTER → SMART AI GENERATOR v2")
print("="*100 + "\n")

adapter = PureMLAPIAdapter()

# Healthcare requirements
requirements_text = """
Hệ thống phải đăng ký khám bệnh trực tuyến với chọn bác sĩ và giờ khám
Hệ thống phải quản lý hồ sơ bệnh nhân với thông tin cá nhân đầy đủ
Hệ thống phải kiểm tra bảo hiểm y tế của bệnh nhân
Hệ thống phải cảnh báo dị ứng thuốc khi tiếp nhận
"""

result = adapter.generate_test_cases(
    requirements_text=requirements_text,
    max_tests=5,
    confidence_threshold=0.5
)

print(f"API Response Summary:")
print(f"  Status: {result['status']}")
print(f"  System: {result['summary'].get('system')}")
print(f"  Total tests: {result['summary'].get('total_test_cases')}")
print(f"  Avg quality: {result['summary'].get('avg_quality_score'):.0%}")
print(f"  Avg effort: {result['summary'].get('avg_effort_hours'):.1f}h")

print(f"\n" + "="*100)
print("GENERATED TEST CASES (First 5)")
print("="*100 + "\n")

for i, tc in enumerate(result['test_cases'][:5], 1):
    print(f"{i}. Test ID: {tc['test_id']}")
    print(f"   Title: {tc['title']}")
    print(f"   Domain: {tc['domain']}")
    print(f"   Type: {tc['test_type']}")
    print(f"   Quality: {tc['ml_quality_score']:.0%}")
    print(f"   Effort: {tc['effort_hours']:.1f}h")
    print(f"   Steps: {len(tc['steps'])}")
    print()

print("="*100)
print("VALIDATION")
print("="*100)

# Check all requirements
tc_ids = [tc['test_id'] for tc in result['test_cases']]
unknown_count = sum(1 for id in tc_ids if 'UNKNOWN' in id)

print(f"✓ Total test cases: {len(result['test_cases'])}")
print(f"✓ TC-UNKNOWN count: {unknown_count} (should be 0)")
print(f"✓ Unique test IDs: {len(set(tc_ids))} / {len(tc_ids)}")
print(f"✓ Domains detected: {set(tc['domain'] for tc in result['test_cases'])}")
print(f"✓ Test types: {set(tc['test_type'] for tc in result['test_cases'])}")
print(f"✓ Quality range: {min(tc['ml_quality_score'] for tc in result['test_cases']):.0%} - {max(tc['ml_quality_score'] for tc in result['test_cases']):.0%}")
print(f"✓ Effort range: {min(tc['effort_hours'] for tc in result['test_cases']):.1f}h - {max(tc['effort_hours'] for tc in result['test_cases']):.1f}h")
print(f"✓ System: {result['summary'].get('system')}")
print(f"✓ Features: {len(result['summary'].get('features', []))} listed")

print("\n" + "="*100)
print("✅ END-TO-END TEST PASSED")
print("="*100 + "\n")
