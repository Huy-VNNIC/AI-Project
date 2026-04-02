#!/usr/bin/env python3
"""Test the actual API endpoints"""

import json
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# Test 1: Test the v3 endpoint
print("=" * 70)
print("🧪 TEST 1: Testing /api/v3/test-generation/generate endpoint")
print("=" * 70)

test_requirements = "User can login with email and password\nSystem validates email format\nPassword must be encrypted"

payload = {
    "requirements": test_requirements,
    "max_tests": 5,
    "quality_threshold": 0.6
}

print(f"\n📤 Sending request with payload:")
print(f"   requirements: {len(test_requirements)} chars")
print(f"   max_tests: 5")
print(f"   quality_threshold: 0.6")

try:
    response = client.post(
        "/api/v3/test-generation/generate",
        json=payload,
        timeout=30
    )
    
    print(f"\n📥 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ SUCCESS! Generated test cases:")
        print(f"   - Total test cases: {len(data.get('test_cases', []))}")
        
        if data.get('test_cases'):
            print(f"\n📋 Sample test case:")
            tc = data['test_cases'][0]
            print(f"   Title: {tc.get('title', 'N/A')}")
            print(f"   Type: {tc.get('type', 'N/A')}")
            print(f"   Quality Score: {tc.get('quality_score', 'N/A')}")
            
        print(f"\n📊 Response keys: {list(data.keys())}")
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"\n❌ Exception: {e}")


# Test 2: Try the /api/v3/ai-tests/generate endpoint
print("\n" + "=" * 70)
print("🧪 TEST 2: Testing /api/v3/ai-tests/generate endpoint")
print("=" * 70)

ai_payload = {
    "requirements": test_requirements,
    "num_tests": 5
}

print(f"\n📤 Sending request...")

try:
    response = client.post(
        "/api/v3/ai-tests/generate",
        json=ai_payload,
        timeout=30
    )
    
    print(f"\n📥 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ SUCCESS!")
        print(f"📊 Response keys: {list(data.keys())}")
        
        # Pretty print response
        print(f"\n📋 Response structure:")
        print(json.dumps(data, indent=2)[:500])
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"\n❌ Exception: {e}")

print("\n" + "=" * 70)
