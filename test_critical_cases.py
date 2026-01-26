#!/usr/bin/env python3
"""
Test 3 critical cases after quality fixes
"""
import requests
import json

API_BASE = "http://localhost:8000"

def test_case(name: str, text: str, expectations: dict):
    """Test a single case"""
    print(f"\n{'='*70}")
    print(f"TEST: {name}")
    print(f"{'='*70}")
    print(f"Input: '{text}'")
    print()
    
    try:
        response = requests.post(
            f"{API_BASE}/api/task-generation/generate",
            json={
                "text": text,
                "max_tasks": 5,
                "requirement_threshold": 0.3
            },
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ API Error {response.status_code}: {response.text}")
            return False
        
        data = response.json()
        tasks = data.get('tasks', [])
        
        # Check expectations
        if 'should_generate' in expectations:
            if expectations['should_generate']:
                if len(tasks) == 0:
                    print(f"❌ FAIL: Expected tasks but got none")
                    return False
                print(f"✅ Generated {len(tasks)} task(s)")
            else:
                if len(tasks) > 0:
                    print(f"❌ FAIL: Should NOT generate tasks, but got: {tasks[0].get('title')}")
                    return False
                print(f"✅ PASS: Correctly filtered (no tasks)")
                return True
        
        if len(tasks) == 0:
            print(f"❌ No tasks generated")
            return False
        
        task = tasks[0]
        title = task.get('title', '')
        task_type = task.get('type', '')
        domain = task.get('domain', '')
        
        print(f"Generated Task:")
        print(f"  Title: {title}")
        print(f"  Type: {task_type}")
        print(f"  Domain: {domain}")
        print()
        
        # Check title expectations
        passed = True
        if 'title_must_contain' in expectations:
            for keyword in expectations['title_must_contain']:
                if keyword.lower() not in title.lower():
                    print(f"  ❌ Title missing expected keyword: '{keyword}'")
                    passed = False
                else:
                    print(f"  ✅ Title contains: '{keyword}'")
        
        if 'title_must_not_contain' in expectations:
            for keyword in expectations['title_must_not_contain']:
                if keyword.lower() in title.lower():
                    print(f"  ❌ Title should NOT contain: '{keyword}'")
                    passed = False
                else:
                    print(f"  ✅ Title does not contain: '{keyword}'")
        
        if 'expected_type' in expectations:
            if task_type == expectations['expected_type']:
                print(f"  ✅ Type correct: {task_type}")
            else:
                print(f"  ❌ Type incorrect: got '{task_type}', expected '{expectations['expected_type']}'")
                passed = False
        
        if 'expected_domain' in expectations:
            if domain == expectations['expected_domain']:
                print(f"  ✅ Domain correct: {domain}")
            else:
                print(f"  ⚠️  Domain: got '{domain}', expected '{expectations['expected_domain']}'")
                # Don't fail on domain - it's harder to predict
        
        if passed:
            print(f"\n✅ TEST PASSED")
        else:
            print(f"\n❌ TEST FAILED")
        
        return passed
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def main():
    import time
    print("\n" + "="*70)
    print("CRITICAL QUALITY TESTS (After Fixes)")
    print("="*70)
    
    # Wait for API
    print("\nWaiting for API to start...")
    for i in range(10):
        try:
            r = requests.get(f"{API_BASE}/", timeout=2)
            if r.status_code == 200:
                print("✅ API is ready\n")
                break
        except:
            pass
        time.sleep(1)
    else:
        print("❌ API not ready after 10s")
        return
    
    results = []
    
    # TEST 1: Notes + Requirement (should filter notes)
    results.append(test_case(
        "Test 1: Notes + Requirement",
        "We discussed authentication in the last meeting. The system must support OAuth2 login.",
        {
            'should_generate': True,
            'title_must_contain': ['OAuth2', 'login'],
            'title_must_not_contain': ['discussed', 'meeting'],
            'expected_type': 'security',
            'expected_domain': 'general'
        }
    ))
    
    # TEST 2: Helper verb
    results.append(test_case(
        "Test 2: Helper Verb (allow → reset)",
        "The system must allow users to reset their password via email.",
        {
            'title_must_contain': ['reset', 'password'],
            'title_must_not_contain': ['allow', 'capability', 'functionality'],
            'expected_type': 'security',
            'expected_domain': 'general'
        }
    ))
    
    # TEST 3: Object + Format
    results.append(test_case(
        "Test 3: Object + Format Extraction",
        "The system shall be able to export audit logs to CSV.",
        {
            'title_must_contain': ['export', 'audit', 'CSV'],
            'title_must_not_contain': ['capability', 'feature'],
            'expected_type': 'security'
        }
    ))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"❌ {total - passed} test(s) failed")
    
    print("="*70)


if __name__ == "__main__":
    main()
