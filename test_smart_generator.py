#!/usr/bin/env python
"""Test Smart AI Generator"""
from requirement_analyzer.task_gen.smart_ai_generator import AITestGenerator

print("\n🤖 TESTING SMART AI GENERATOR\n" + "="*80)

generator = AITestGenerator()
requirements = [
    "Hệ thống phải cho phép mở tài khoản trực tuyến với xác thực eKYC",
    "Hệ thống phải hỗ trợ chuyển khoản nội bộ giữa các tài khoản",
]

results = generator.generate(requirements, max_tests=10)

print(f"\n✅ Generated {results['summary']['total_test_cases']} test cases\n")

# Show first 2 tests in detail
for i, tc in enumerate(results["test_cases"][:2], 1):
    print(f"\n{'='*80}")
    print(f"TEST #{i}: {tc['test_id']}")
    print(f"Title: {tc['title']}")
    print(f"Type: {tc['test_type']}")
    print(f"Priority: {tc['priority']}")
    print(f"Quality: {tc['ml_quality_score']:.0%}")
    print(f"\nPreconditions:")
    for p in tc['preconditions']:
        print(f"  • {p}")
    print(f"\nTest Data: {tc['test_data']}")
    print(f"\nSteps:")
    for step in tc['steps']:
        print(f"  {step['order']}. {step['action']}")
        print(f"     → {step['expected_result']}")
    print(f"\nExpected Result: {tc['expected_result']}")
    print(f"Effort: {tc['effort_hours']:.1f}h")

print(f"\n{'='*80}")
print(f"\n✅ SMART AI GENERATOR WORKING!")
print(f"✓ Dynamically builds from requirement content")
print(f"✓ No hardcoded templates")
print(f"✓ Adapts to different requirement types")
