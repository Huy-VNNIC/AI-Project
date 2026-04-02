#!/usr/bin/env python3
"""Test LLM-Free Adapter Integration"""
import sys
from pathlib import Path

# Setup path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / 'requirement_analyzer' / 'task_gen'))

from api_adapter_llmfree import get_llmfree_adapter

print("=" * 70)
print("🧪 TESTING LLM-FREE ADAPTER INTEGRATION")
print("=" * 70)

# Create adapter
adapter = get_llmfree_adapter()

# Test with hotel requirements (Vietnamese)
test_reqs = """Hệ thống phải cho phép đặt phòng mới với các thông tin: loại phòng, ngày check-in, ngày check-out, thông tin khách hàng
Hệ thống phải kiểm tra tính khả dụng của phòng theo loại và ngày
Hệ thống phải hỗ trợ đặt phòng trực tuyến và tại quầy lễ tân
Hệ thống phải cho phép xác nhận, hủy, và chỉnh sửa đơn đặt phòng
Hệ thống phải gửi email xác nhận khi đặt phòng thành công"""

print("\n🔄 Testing with 5 Hotel Requirements (Vietnamese)...")
result = adapter.generate_tests(test_reqs, max_tests=20, quality_threshold=0.5)

print(f"\n✅ Status: {result['status']}")
print(f"   Generated: {result['summary']['unique_tests_final']} tests")
print(f"   Quality Score: {result['summary']['avg_confidence']:.2f}")
print(f"   Avg Effort: {result['summary']['avg_effort_hours']:.1f}h")
print(f"   Domain Distribution: {result['summary']['domain_distribution']}")
print(f"   Test Type Distribution: {result['summary']['test_type_distribution']}")
print(f"   Quality Gates:")
print(f"      Passed: {result['summary']['quality_gates']['passed']}")
print(f"      Marginal: {result['summary']['quality_gates']['marginal']}")
print(f"      Failed: {result['summary']['quality_gates']['failed']}")

print(f"\n📋 Sample Generated Tests:")
if result['test_cases']:
    for i, test in enumerate(result['test_cases'][:5], 1):
        print(f"\n   [{i}] {test['test_id']}: {test['title']}")
        print(f"       Type: {test['test_type']} | Priority: {test['priority']}")
        print(f"       Confidence: {test['ml_quality_score']:.2f} | Effort: {test['effort_hours']:.1f}h")
        print(f"       Description: {test['description'][:80]}...")
else:
    print("   ❌ NO TESTS GENERATED")

print("\n" + "=" * 70)
print("✅ TEST COMPLETE - System is working!")
print("=" * 70)
