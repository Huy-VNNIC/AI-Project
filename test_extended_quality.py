#!/usr/bin/env python3
"""
Extended test suite - 7 critical cases total
"""
import requests
import json

API_BASE = "http://localhost:8000"

def test_case(name: str, text: str, expectations: dict):
    """Test a single case"""
    print(f"\n{'='*70}")
    print(f"{name}")
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
                    print(f"❌ FAIL: Should NOT generate, but got: {tasks[0].get('title')}")
                    return False
                print(f"✅ PASS: Correctly filtered")
                return True
        
        if len(tasks) == 0:
            print(f"❌ No tasks generated")
            return False
        
        task = tasks[0]
        title = task.get('title', '')
        task_type = task.get('type', '')
        domain = task.get('domain', '')
        ac = task.get('acceptance_criteria', [])
        
        print(f"Generated Task:")
        print(f"  Title: {title}")
        print(f"  Type: {task_type}, Domain: {domain}")
        print(f"  AC ({len(ac)} items):")
        for i, criteria in enumerate(ac[:3], 1):
            print(f"    {i}. {criteria[:70]}...")
        print()
        
        # Check expectations
        passed = True
        
        if 'title_must_contain' in expectations:
            for keyword in expectations['title_must_contain']:
                if keyword.lower() not in title.lower():
                    print(f"  ❌ Title missing: '{keyword}'")
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
                print(f"  ✅ Type: {task_type}")
            else:
                print(f"  ⚠️  Type: got '{task_type}', expected '{expectations['expected_type']}'")
        
        if 'expected_domain' in expectations:
            if domain == expectations['expected_domain']:
                print(f"  ✅ Domain: {domain}")
            else:
                print(f"  ⚠️  Domain: got '{domain}', expected '{expectations['expected_domain']}'")
        
        if 'ac_must_contain' in expectations:
            ac_text = ' '.join(ac).lower()
            for keyword in expectations['ac_must_contain']:
                if keyword.lower() in ac_text:
                    print(f"  ✅ AC contains keyword: '{keyword}'")
                else:
                    print(f"  ⚠️  AC missing keyword: '{keyword}'")
        
        if passed:
            print(f"\n✅ TEST PASSED")
        else:
            print(f"\n⚠️  TEST PARTIAL")
        
        return passed
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    import time
    print("\n" + "="*70)
    print("EXTENDED QUALITY TEST SUITE (7 Critical Cases)")
    print("="*70)
    
    # Wait for API
    print("\nWaiting for API...")
    for i in range(10):
        try:
            r = requests.get(f"{API_BASE}/", timeout=2)
            if r.status_code == 200:
                print("✅ API ready\n")
                break
        except:
            pass
        time.sleep(1)
    else:
        print("❌ API not ready")
        return
    
    results = []
    
    # Original 3 tests
    results.append(test_case(
        "Test 1: Notes + Requirement",
        "We discussed authentication in the last meeting. The system must support OAuth2 login.",
        {
            'title_must_contain': ['OAuth2', 'login'],
            'title_must_not_contain': ['discussed', 'meeting'],
            'expected_type': 'security',
            'expected_domain': 'general'
        }
    ))
    
    results.append(test_case(
        "Test 2: Helper Verb (allow → reset)",
        "The system must allow users to reset their password via email.",
        {
            'title_must_contain': ['reset', 'password'],
            'title_must_not_contain': ['allow', 'capability', 'functionality'],
            'expected_type': 'security',
            'ac_must_contain': ['reset link', 'expires', 'password policy']
        }
    ))
    
    results.append(test_case(
        "Test 3: Object + Format (be able to)",
        "The system shall be able to export audit logs to CSV.",
        {
            'title_must_contain': ['export', 'audit', 'CSV'],
            'title_must_not_contain': ['capability', 'feature'],
            'expected_type': 'security',
            'ac_must_contain': ['CSV', 'fields', 'authorized']
        }
    ))
    
    # New 4 tests
    results.append(test_case(
        "Test 4: Login using method",
        "Users must log in using email and password.",
        {
            'title_must_contain': ['log in', 'email', 'password'],
            'title_must_not_contain': ['capability', 'functionality'],
            'expected_type': 'security',
            'ac_must_contain': ['credentials', 'lockout']
        }
    ))
    
    results.append(test_case(
        "Test 5: Send verification email",
        "The system must send verification emails after registration.",
        {
            'title_must_contain': ['send', 'verification', 'email'],
            'title_must_not_contain': ['capability'],
            'expected_type': 'security',
            'ac_must_contain': ['verification', 'link', 'activated']
        }
    ))
    
    results.append(test_case(
        "Test 6: Reset password via email link",
        "Users must be able to reset passwords via an email link.",
        {
            'title_must_contain': ['reset', 'password', 'email'],
            'title_must_not_contain': ['capability', 'able'],
            'expected_type': 'security',
            'ac_must_contain': ['reset link', 'expires']
        }
    ))
    
    results.append(test_case(
        "Test 7: Session expiry",
        "Sessions must expire after 30 minutes of inactivity.",
        {
            'title_must_contain': ['expire', 'session', '30', 'minutes'],
            'title_must_not_contain': ['capability'],
            'expected_type': 'security',
            'ac_must_contain': ['inactivity', 're-authenticate', 'warning']
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
    elif passed >= total * 0.8:
        print(f"⚠️  Most tests passed ({passed}/{total})")
    else:
        print(f"❌ {total - passed} test(s) failed")
    
    print("="*70)


if __name__ == "__main__":
    main()
