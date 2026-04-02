#!/usr/bin/env python3
"""
🧪 Test Script for Custom AI Test Generation
=============================================

Tests:
1. Custom AI Mode (/api/v2/test-generation/generate-ai)
2. Template Mode (/api/v2/test-generation/generate-test-cases)
3. Comparison between both
4. Edge cases and error handling

Usage:
    python3 test_custom_ai.py
"""

import requests
import json
import time
from typing import Dict, Any, List

BASE_URL = "http://localhost:8000"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_header(text: str):
    print(f"\n{BLUE}{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}{RESET}\n")

def print_success(text: str):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text: str):
    print(f"{RED}❌ {text}{RESET}")

def print_info(text: str):
    print(f"{BLUE}ℹ️  {text}{RESET}")

def print_warning(text: str):
    print(f"{YELLOW}⚠️  {text}{RESET}")

# ============================================================================
# TEST 1: Custom AI Mode
# ============================================================================

def test_custom_ai_basic():
    """Test Custom AI with simple requirement"""
    print_header("TEST 1: Custom AI - Basic Requirement")
    
    payload = {
        "requirements": "User should be able to login with email and password",
        "max_tests": 10,
        "threshold": 0.6
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/v2/test-generation/generate-ai",
            json=payload,
            timeout=30
        )
        elapsed = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {elapsed:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check status
            if data.get("status") == "success":
                print_success(f"Generated {len(data.get('test_cases', []))} test cases")
            else:
                print_error(f"Status: {data.get('status')}")
                return False
            
            # Check test cases
            test_cases = data.get("test_cases", [])
            if not test_cases:
                print_error("No test cases generated")
                return False
            
            print(f"\n📋 Test Cases:")
            for i, tc in enumerate(test_cases[:3], 1):
                print(f"\n  Test {i}:")
                print(f"  - Title: {tc.get('title')}")
                print(f"  - Type: {tc.get('test_type', tc.get('type'))}")
                print(f"  - Priority: {tc.get('priority')}")
                print(f"  - AI Confidence: {tc.get('ai_confidence')}")
                print(f"  - Reason: {tc.get('why_generated', 'N/A')[:70]}")
            
            if len(test_cases) > 3:
                print(f"\n  ... and {len(test_cases) - 3} more test cases")
            
            # Check analysis
            if "analysis" in data:
                analysis = data["analysis"]
                print(f"\n🔍 AI Analysis:")
                print(f"  - Entities: {len(analysis.get('entities', []))}")
                print(f"  - Relationships: {len(analysis.get('relationships', []))}")
                print(f"  - Edge Cases: {len(analysis.get('edge_cases', []))}")
                print(f"  - Conditions: {len(analysis.get('conditions', []))}")
                print(f"  - Complexity: {analysis.get('complexity', 'N/A')}")
            
            # Check summary
            if "summary" in data:
                summary = data["summary"]
                print(f"\n📊 Summary:")
                print(f"  - Total: {summary.get('total_test_cases')}")
                print(f"  - Avg Confidence: {summary.get('avg_confidence')}")
                if "by_type" in summary:
                    print(f"  - By Type: {summary['by_type']}")
            
            return True
        else:
            print_error(f"API Error: {response.status_code}")
            print(response.text[:300])
            return False
            
    except requests.exceptions.Timeout:
        print_error("Request timeout (30s)")
        return False
    except Exception as e:
        print_error(f"Exception: {e}")
        return False

# ============================================================================
# TEST 2: Complex Requirement
# ============================================================================

def test_custom_ai_complex():
    """Test Custom AI with complex requirement involving security"""
    print_header("TEST 2: Custom AI - Complex Requirement (Security)")
    
    payload = {
        "requirements": """
        User Authentication System:
        - Users must login with email and password
        - System must validate email format (RFC 5322)
        - Password must be at least 8 characters with uppercase, lowercase, and numbers
        - System should prevent SQL injection attacks
        - After 3 failed login attempts, account should be locked for 15 minutes
        - Session should expire after 30 minutes of inactivity
        - All passwords must be hashed using bcrypt
        - System must support two-factor authentication (2FA)
        """,
        "max_tests": 15,
        "threshold": 0.5
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v2/test-generation/generate-ai",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            test_cases = data.get("test_cases", [])
            
            print_success(f"Generated {len(test_cases)} test cases for complex requirement")
            
            # Analyze by type
            by_type = {}
            for tc in test_cases:
                t = tc.get("test_type", tc.get("type", "Unknown"))
                by_type[t] = by_type.get(t, 0) + 1
            
            print(f"\n📊 Test Distribution:")
            for test_type, count in sorted(by_type.items()):
                print(f"  - {test_type}: {count}")
            
            # Check for security tests
            security_tests = [tc for tc in test_cases if "security" in tc.get("title", "").lower() or "injection" in tc.get("title", "").lower()]
            print(f"\n🔒 Security Tests Found: {len(security_tests)}")
            
            # Check AI analysis
            if "analysis" in data:
                edge_cases = data["analysis"].get("edge_cases", [])
                print(f"\n🎯 Edge Cases Detected by AI ({len(edge_cases)}):")
                for ec in edge_cases[:5]:
                    print(f"  - {ec}")
            
            return len(test_cases) > 0
        else:
            print_error(f"API Error: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Exception: {e}")
        return False

# ============================================================================
# TEST 3: Compare AI vs Template
# ============================================================================

def test_comparison():
    """Compare Custom AI vs Template-Based Generation"""
    print_header("TEST 3: Custom AI vs Template-Based Comparison")
    
    requirement = "User should login with email and password"
    
    print("Testing both modes with same requirement...")
    print(f"Requirement: {requirement}\n")
    
    # Test Custom AI
    print(f"{YELLOW}[1/2] Testing Custom AI...{RESET}")
    ai_payload = {
        "requirements": requirement,
        "max_tests": 10,
        "threshold": 0.6
    }
    
    try:
        ai_start = time.time()
        ai_response = requests.post(
            f"{BASE_URL}/api/v2/test-generation/generate-ai",
            json=ai_payload,
            timeout=30
        )
        ai_time = time.time() - ai_start
        ai_data = ai_response.json() if ai_response.status_code == 200 else {}
    except Exception as e:
        print_error(f"Custom AI failed: {e}")
        ai_data = {}
        ai_time = None
    
    # Test Template
    print(f"{YELLOW}[2/2] Testing Template...{RESET}")
    template_payload = {
        "max_tests": 10,
        "threshold": 0.6
    }
    
    try:
        template_start = time.time()
        template_response = requests.post(
            f"{BASE_URL}/api/v2/test-generation/generate-test-cases",
            json=template_payload,
            timeout=30
        )
        template_time = time.time() - template_start
        template_data = template_response.json() if template_response.status_code == 200 else {}
    except Exception as e:
        print_error(f"Template generation failed: {e}")
        template_data = {}
        template_time = None
    
    # Compare
    print("\n📊 COMPARISON RESULTS:")
    print(f"\n{'Metric':<30} {'Custom AI':<25} {'Template':<25}")
    print("-" * 80)
    
    ai_count = len(ai_data.get("test_cases", []))
    template_count = len(template_data.get("test_cases", []))
    print(f"{'Test Cases Generated':<30} {ai_count:<25} {template_count:<25}")
    
    ai_conf = ai_data.get("summary", {}).get("avg_confidence", "N/A")
    print(f"{'Avg Confidence':<30} {str(ai_conf):<25} {'N/A':<25}")
    
    ai_time_str = f"{ai_time:.2f}s" if ai_time else "Error"
    template_time_str = f"{template_time:.2f}s" if template_time else "Error"
    print(f"{'Response Time':<30} {ai_time_str:<25} {template_time_str:<25}")
    
    ai_has_analysis = "analysis" in ai_data
    print(f"{'AI Analysis':<30} {'Yes' if ai_has_analysis else 'No':<25} {'No':<25}")
    
    print("\n" + "-" * 80)
    print(f"{GREEN}✅ Custom AI provides:{RESET}")
    print(f"   - AI Confidence scores")
    print(f"   - Full requirement analysis")
    print(f"   - Entity extraction")
    print(f"   - Edge case detection")
    
    return ai_count > 0 and template_count > 0

# ============================================================================
# TEST 4: Error Handling
# ============================================================================

def test_error_handling():
    """Test error cases"""
    print_header("TEST 4: Error Handling")
    
    test_cases = [
        {
            "name": "Empty requirement",
            "payload": {"requirements": "", "max_tests": 10},
            "expect_error": True
        },
        {
            "name": "Invalid threshold (>1.0)",
            "payload": {"requirements": "Test", "threshold": 1.5},
            "expect_error": True
        },
        {
            "name": "Valid request",
            "payload": {"requirements": "Test requirement", "max_tests": 5},
            "expect_error": False
        }
    ]
    
    passed = 0
    for test in test_cases:
        print(f"\nTest: {test['name']}")
        try:
            response = requests.post(
                f"{BASE_URL}/api/v2/test-generation/generate-ai",
                json=test["payload"],
                timeout=10
            )
            
            is_error = response.status_code >= 400
            
            if test["expect_error"] == is_error:
                print_success(f"Status: {response.status_code} (as expected)")
                passed += 1
            else:
                print_warning(f"Status: {response.status_code} (unexpected)")
        except Exception as e:
            print_error(f"Exception: {e}")
    
    return passed == len(test_cases)

# ============================================================================
# TEST 5: Endpoint Check
# ============================================================================

def test_endpoints():
    """Verify all endpoints are available"""
    print_header("TEST 5: API Endpoints Check")
    
    endpoints = [
        ("GET", "/health", {}),
        ("GET", "/api/v2/test-generation/health", {}),
        ("POST", "/api/v2/test-generation/generate-ai", {"requirements": "test"}),
        ("POST", "/api/v2/test-generation/generate-test-cases", {"max_tests": 5}),
    ]
    
    available = 0
    
    for method, endpoint, payload in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", json=payload, timeout=5)
            
            status = "✅" if response.status_code < 400 else "⚠️"
            print(f"{status} {method:6} {endpoint:<50} → {response.status_code}")
            
            if response.status_code < 400:
                available += 1
        except Exception as e:
            print(f"❌ {method:6} {endpoint:<50} → Error: {str(e)[:40]}")
    
    return available == len(endpoints)

# ============================================================================
# MAIN
# ============================================================================

def main():
    print(f"\n{BLUE}{'='*80}")
    print("  🧪 CUSTOM AI TEST GENERATION - TEST SUITE")
    print(f"{'='*80}{RESET}")
    print(f"Base URL: {BASE_URL}\n")
    
    results = {}
    
    # Run tests
    results["1. Custom AI Basic"] = test_custom_ai_basic()
    results["2. Custom AI Complex"] = test_custom_ai_complex()
    results["3. AI vs Template"] = test_comparison()
    results["4. Error Handling"] = test_error_handling()
    results["5. Endpoints"] = test_endpoints()
    
    # Summary
    print_header("📋 TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:12} {test_name}")
    
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("All tests passed! Custom AI is working perfectly! 🎉")
    else:
        print_warning(f"{total - passed} tests failed. Please check the errors above.")
    
    print(f"{BLUE}{'='*80}{RESET}\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
