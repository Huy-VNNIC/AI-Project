#!/usr/bin/env python3
"""
Test AI Test Case Generation endpoint
"""
import requests
import json
import time

API_URL = "http://localhost:8000/api/v2/test-generation/generate-test-cases"

print("=" * 60)
print("🧪 Testing AI Test Case Generation Endpoint")
print("=" * 60)

# Test 1: Check if API is running
print("\n1️⃣ Checking if API is running...")
try:
    health_response = requests.get("http://localhost:8000/health", timeout=5)
    if health_response.status_code == 200:
        print("   ✅ API is running!")
    else:
        print(f"   ❌ API returned: {health_response.status_code}")
except Exception as e:
    print(f"   ❌ API not responding: {e}")
    exit(1)

# Test 2: Test the endpoint
print("\n2️⃣ Testing generate-test-cases endpoint...")
test_payload = {
    "requirements": "The system shall allow users to login with email and password.\nThe system must prevent SQL injection attacks.",
    "max_tests": 5,
    "threshold": 0.5
}

print(f"   Request URL: {API_URL}")
print(f"   Payload: {json.dumps(test_payload, indent=2)}")

try:
    response = requests.post(API_URL, json=test_payload, timeout=30)
    print(f"\n   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n   ✅ SUCCESS! Response:")
        print(f"   - Total test cases: {len(data.get('test_cases', []))}")
        print(f"   - Generation time: {data.get('generation_time', 'N/A')}ms")
        print(f"\n   First test case:")
        if data.get('test_cases'):
            tc = data['test_cases'][0]
            print(f"   - ID: {tc.get('test_id')}")
            print(f"   - Category: {tc.get('category')}")
            print(f"   - Description: {tc.get('description', '')[:80]}...")
            print(f"   - Confidence: {tc.get('confidence', 0)*100:.0f}%")
    else:
        print(f"\n   ❌ ERROR! Response:")
        print(f"   {response.text}")
        
except Exception as e:
    print(f"\n   ❌ Request failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
