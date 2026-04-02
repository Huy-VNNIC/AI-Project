#!/usr/bin/env python
"""Test Enhanced Generator via API"""

import requests
import json

api_url = "http://localhost:8000/api/v3/test-generation/generate"

requirements = """Patient can book appointments up to 30 days in advance
System must prevent unauthorized access to medical records
Doctor can view patient medication history"""

payload = {
    "requirements": requirements,
    "max_tests": 15,
    "confidence_threshold": 0.5
}

print("🚀 Testing Enhanced Test Generator via API\n")
print("="*80)

try:
    response = requests.post(api_url, json=payload, timeout=30)
    data = response.json()
    
    print(f"✅ API Response: {response.status_code}")
    print(f"Total Test Cases: {data['summary']['total_test_cases']}")
    print(f"Avg Quality: {data['summary']['avg_quality_score']:.2%}")
    print(f"Avg Effort: {data['summary']['avg_effort_hours']:.2f}h")
    print(f"Test Distribution: {data['summary'].get('test_types', {})}")
    
    if data['test_cases']:
        print("\n" + "="*80)
        print("SAMPLE TEST CASES:\n")
        
        for i, tc in enumerate(data['test_cases'][:3], 1):
            print(f"\n#{i} - {tc['test_id']} ({tc['test_type']})")
            print(f"   Title: {tc['title']}")
            print(f"   Quality: {tc['ml_quality_score']:.0%}")
            print(f"   Steps: {len(tc['steps'])}")
            print(f"   Preconditions: {len(tc['preconditions'])}")
            print(f"   Test Data Fields: {len(tc['test_data'])}")
    
    print("\n" + "="*80)
    print(f"\n✅ SUCCESS! Generated {data['summary']['total_test_cases']} high-quality test cases")
    print(f"\nFeatures enabled:")
    for feature in data['summary'].get('features', []):
        print(f"  ✓ {feature}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
