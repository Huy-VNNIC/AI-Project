#!/usr/bin/env python3
"""
🧪 Simple Test Guide for Custom AI
===================================

Just copy and paste these commands to test!
"""

import subprocess
import json
import sys

def run_test(name, curl_cmd):
    """Run a single test"""
    print(f"\n{'='*80}")
    print(f"  🧪 {name}")
    print(f"{'='*80}")
    print(f"Command:\n{curl_cmd}\n")
    
    # Execute curl command
    result = subprocess.run(curl_cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            print(f"✅ Status: {data.get('status')}")
            print(f"✅ Test Cases: {len(data.get('test_cases', []))}")
            if data.get('test_cases'):
                print(f"\nFirst test:")
                tc = data['test_cases'][0]
                print(f"  - Title: {tc.get('title')}")
                print(f"  - Type: {tc.get('test_type', tc.get('type'))}")
                print(f"  - Confidence: {tc.get('ai_confidence')}")
            if 'summary' in data:
                print(f"\nSummary:")
                print(f"  - Total: {data['summary'].get('total_test_cases')}")
                print(f"  - Avg Confidence: {data['summary'].get('avg_confidence')}")
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON response:\n{result.stdout[:200]}")
    else:
        print(f"❌ Error:\n{result.stderr[:300]}")

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                   🤖 CUSTOM AI TEST GUIDE                                  ║
║                                                                            ║
║  Choose one of these tests to run:                                         ║
║  (Copy the curl command and paste in terminal)                             ║
╚════════════════════════════════════════════════════════════════════════════╝
""")

tests = [
    (
        "TEST 1: Simple Login Requirement",
        """curl -s -X POST http://localhost:8000/api/v2/test-generation/generate-ai \\
  -H "Content-Type: application/json" \\
  -d '{
    "requirements": "User should be able to login with email and password",
    "max_tests": 10,
    "threshold": 0.6
  }' | python3 -m json.tool"""
    ),
    (
        "TEST 2: Complex Security Requirement",
        """curl -s -X POST http://localhost:8000/api/v2/test-generation/generate-ai \\
  -H "Content-Type: application/json" \\
  -d '{
    "requirements": "User authentication with email and password. Password must be 8+ chars. Prevent SQL injection. Lock after 3 failed attempts.",
    "max_tests": 15,
    "threshold": 0.5
  }' | python3 -m json.tool"""
    ),
    (
        "TEST 3: Multi-line Requirements",
        """curl -s -X POST http://localhost:8000/api/v2/test-generation/generate-ai \\
  -H "Content-Type: application/json" \\
  -d '{
    "requirements": "REQUIREMENT 1: Users must login with email and password\\nREQUIREMENT 2: Validate email format\\nREQUIREMENT 3: Password minimum 8 characters\\nREQUIREMENT 4: Prevent brute force attacks",
    "max_tests": 12,
    "threshold": 0.6
  }' | python3 -m json.tool"""
    ),
]

for i, (name, cmd) in enumerate(tests, 1):
    print(f"\n{i}. {name}")
    print(f"\n   Command:")
    for line in cmd.split('\n'):
        print(f"   {line}")

print(f"""

{'='*80}
INSTRUCTIONS: Copy one command above and paste in terminal

Example:
---------
$ curl -s -X POST http://localhost:8000/api/v2/test-generation/generate-ai \\
  -H "Content-Type: application/json" \\
  -d '{{"requirements": "User login", ...}}' | python3 -m json.tool

You should see:
  "status": "success"
  "test_cases": [ ... ]
  "summary": {{ "avg_confidence": 0.96, ... }}

{'='*80}
""")

# Offer to run tests
print("\n🔥 Want me to run these tests for you?")
response = input("Run all tests? (y/n): ").lower()

if response == 'y':
    print("\n⏳ Running tests...")
    for name, cmd in tests:
        run_test(name, cmd)
    print("\n" + "="*80)
    print("✅ All tests completed!")
else:
    print("\nOK! Copy and paste any command above to test manually.")
