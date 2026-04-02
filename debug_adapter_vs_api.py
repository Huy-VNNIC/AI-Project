#!/usr/bin/env python
"""Debug: Compare adapter output vs API output"""
import json
import requests
from requirement_analyzer.pure_ml_api_adapter import PureMLAPIAdapter

# Test requirement
req = "Hệ thống phải mở tài khoản trực tuyến"

print("\n" + "="*80)
print("1. TESTING ADAPTER DIRECTLY")
print("="*80)
adapter = PureMLAPIAdapter()
adapter_result = adapter.generate_test_cases(
    requirements_text=req,
    max_tests=1
)
print(f"Adapter System: {adapter_result['summary'].get('system')}")
print(f"Adapter Features: {adapter_result['summary'].get('features', [])[:2]}")

print("\n" + "="*80)
print("2. TESTING API ENDPOINT")
print("="*80)
try:
    api_result = requests.post(
        "http://localhost:8000/api/v3/test-generation/generate",
        json={"requirements": req, "max_tests": 1},
        timeout=10
    ).json()
    print(f"API System: {api_result['summary'].get('system')}")
    print(f"API Features: {api_result['summary'].get('features', [])[:2]}")
except Exception as e:
    print(f"API Error: {e}")

print("\n" + "="*80)
print("COMPARISON")
print("="*80)
adapter_system = adapter_result['summary'].get('system')
api_system = api_result['summary'].get('system') if 'api_result' in locals() else "ERROR"
print(f"Match: {adapter_system == api_system} (✓ if True)")
print(f"Adapter: {adapter_system}")
print(f"API:     {api_system}")
