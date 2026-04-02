#!/usr/bin/env python3
"""Test new AI test case generation endpoint"""

import json
import time
import sys
import urllib.request
import urllib.error

def test_endpoint():
    # Wait for API to fully start
    print("⏳ Waiting for API to fully start...")
    time.sleep(3)
    
    try:
        # Test the new endpoint
        url = "http://localhost:8000/api/v2/test-generation/generate-test-cases"
        
        payload = {
            "requirements": "The system shall allow users to login with email and password.\nThe application must prevent SQL injection attacks.",
            "max_tests": 20,
            "threshold": 0.5
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        print("🚀 Testing endpoint: POST /api/v2/test-generation/generate-test-cases")
        print(f"\n📝 Requirements:")
        for req_text in payload['requirements'].split('\n'):
            print(f"  - {req_text}")
        
        print("\n⏳ Calling API...")
        
        response = urllib.request.urlopen(req, timeout=30)
        data = json.loads(response.read().decode('utf-8'))
        
        print("\n" + "="*60)
        print("✅ SUCCESS! API Working!")
        print("="*60)
        print(f"\nStatus: {data.get('status')}")
        print(f"Generated: {data.get('summary', {}).get('total_tests')} test cases")
        print(f"Generation time: {data.get('generation_time')} ms")
        print(f"Average confidence: {data.get('summary', {}).get('avg_confidence')}%")
        print(f"Average effort: {data.get('summary', {}).get('avg_effort_hours')} hours")
        
        print(f"\n📊 Test Cases by Category:")
        for cat, count in data.get('summary', {}).get('by_category', {}).items():
            print(f"  - {cat}: {count}")
        
        print(f"\n🧪 Sample Test Cases:")
        for i, tc in enumerate(data.get('test_cases', [])[:3], 1):
            print(f"\n  Test {i}:")
            print(f"    ID: {tc['test_id']}")
            print(f"    Category: {tc['category']}")
            print(f"    Severity: {tc['severity']}")
            print(f"    Description: {tc['description']}")
            print(f"    Confidence: {tc['confidence']*100:.0f}%")
            print(f"    Effort: {tc['estimated_effort_hours']}h")
            print(f"    Automation: {tc['automation_feasibility']*100:.0f}%")
            if tc.get('security_threats'):
                print(f"    Security Threats: {len(tc['security_threats'])}")
        
        return 0
        
    except urllib.error.HTTPError as e:
        print(f"\n❌ HTTP Error {e.code}")
        try:
            error_data = json.loads(e.read().decode('utf-8'))
            print(f"Detail: {error_data.get('detail')}")
        except:
            pass
        return 1
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(test_endpoint())
