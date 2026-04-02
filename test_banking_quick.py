#!/usr/bin/env python
"""Test enhanced banking generator"""
from requirement_analyzer.task_gen.enhanced_test_generator import EnhancedTestGenerator

generator = EnhancedTestGenerator()
requirements = [
    "Hệ thống phải cho phép mở tài khoản trực tuyến với xác thực eKYC",
    "Hệ thống phải hỗ trợ chuyển khoản nội bộ giữa các tài khoản",
    "Hệ thống phải xác thực giao dịch bằng OTP hoặc sinh trắc học"
]

results = generator.generate(requirements, max_tests=9)
print(f"✅ Generated {results['summary']['total_test_cases']} test cases")
print(f"Quality: {results['summary']['avg_quality_score']:.1%}")

tc = results["test_cases"][0]
print(f"\nFirst Test Case:")
print(f"  ID: {tc['test_id']} ✓")
print(f"  Title: {tc['title'][:50]}...")
print(f"  Domain: {tc['domain']} ✓ (banking)")
print(f"  Quality: {tc['ml_quality_score']:.0%}")
print(f"  Test Data: {list(tc['test_data'].keys())}")
print(f"\nSample Precondition: {tc['preconditions'][0]}")

# Show test distribution
print(f"\nTest Type Distribution: {results['summary']['test_type_distribution']}")
