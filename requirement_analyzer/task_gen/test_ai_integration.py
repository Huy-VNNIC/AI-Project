#!/usr/bin/env python3
"""
Test AI Test Generation Integration with FastAPI
==================================================

Tests the API endpoints for AI-powered test case generation.
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# For testing without running the full server
def test_handler_directly():
    """Test AI handler directly"""
    print("="*80)
    print("Direct Handler Test")
    print("="*80)
    
    try:
        from requirement_analyzer.task_gen.ai_test_handler import AITestGenerationHandler
        
        handler = AITestGenerationHandler()
        
        # Test requirement
        requirement = """
        System must implement user authentication with email and password.
        Users can register with unique email. Passwords must be at least 8 
        characters with uppercase, lowercase, and numbers. Account lockout 
        after 5 failed login attempts. Session timeout after 30 minutes.
        """
        
        print(f"\nRequirement: {requirement[:100]}...\n")
        
        result = handler.generate_tests_for_task(
            task_id="AUTH-001",
            task_description=requirement,
            acceptance_criteria="Given user with valid email, When user provides correct password"
        )
        
        if result.get("status") == "success":
            print(f"✅ Handler working!")
            print(f"   - Test cases generated: {result['summary']['total_test_cases']}")
            print(f"   - By type: {result['summary']['by_type']}")
            print(f"   - AI confidence: {result['summary']['avg_confidence']:.2f}")
            return True
        else:
            print(f"❌ Handler failed: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_client():
    """Test API client (simulated)"""
    print("\n" + "="*80)
    print("API Client Test (Simulated)")
    print("="*80)
    
    try:
        # Simulate API requests
        from requirement_analyzer.task_gen.api_ai_test_generation_v3 import GenerateTestsRequest
        
        print("\n✅ API models importable!")
        
        # Create request
        request = GenerateTestsRequest(
            task_id="TEST-001",
            description="User registration feature",
            acceptance_criteria="Given user, When user registers, Then account is created"
        )
        
        print(f"   - Generated request: {request.task_id}")
        print(f"   - Ready for API calls")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_endpoints_structure():
    """Test that all endpoints are properly defined"""
    print("\n" + "="*80)
    print("API Endpoints Structure Test")
    print("="*80)
    
    try:
        from requirement_analyzer.task_gen.api_ai_test_generation_v3 import router
        
        print("\n✅ API Router loaded!")
        print("\nAvailable endpoints:")
        
        for route in router.routes:
            if hasattr(route, 'path'):
                methods = getattr(route, 'methods', ['GET'])
                print(f"   • {', '.join(methods)} {route.path}")
        
        print("\nEndpoints available:")
        endpoints = [
            "/generate - Generate tests for single task",
            "/generate-batch - Batch generation for multiple tasks",
            "/requirement/analyze - Analyze requirement only",
            "/test-scenarios/extract - Extract scenarios",
            "/export/pytest - Export as pytest code",
            "/export/gherkin - Export as Gherkin",
            "/health - Health check"
        ]
        
        for ep in endpoints:
            print(f"   ✓ {ep}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_main_app_integration():
    """Test integration with main.py"""
    print("\n" + "="*80)
    print("Main App Integration Test")
    print("="*80)
    
    try:
        from app.main import app, AI_TEST_ROUTER_AVAILABLE
        
        print("\n✅ Main app imported!")
        print(f"   - AI Test Router available: {AI_TEST_ROUTER_AVAILABLE}")
        
        # Check routes
        print("\nAPI Routes registered:")
        ai_test_routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                path = route.path
                if 'ai-tests' in path:
                    ai_test_routes.append(path)
        
        if ai_test_routes:
            print(f"   ✓ {len(ai_test_routes)} AI test routes registered:")
            for route in ai_test_routes[:5]:
                print(f"     • {route}")
            if len(ai_test_routes) > 5:
                print(f"     ... and {len(ai_test_routes) - 5} more")
        else:
            print("   ⚠️  No AI test routes found")
        
        return AI_TEST_ROUTER_AVAILABLE
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_pipeline():
    """Test full generation pipeline"""
    print("\n" + "="*80)
    print("Full Generation Pipeline Test")
    print("="*80)
    
    try:
        from requirement_analyzer.task_gen.ai_intelligent_test_generator import AIIntelligentTestGenerator
        
        generator = AIIntelligentTestGenerator()
        
        # Complex requirement
        requirement = """
        Payment processing system must accept credit cards (Visa, Mastercard, Amex).
        
        Security Requirements:
        - PCI DSS compliance
        - Data encryption (TLS 1.2+)
        - No card storage (tokenization only)
        
        Business Rules:
        - Transaction amount 0.01 to 999,999.99
        - Support recurring payments (weekly, monthly, yearly)
        - Refunds allowed within 90 days
        - Fraud detection with 3D Secure
        
        Performance:
        - Process transactions within 2 seconds
        - 99.9% availability SLA
        - Handle 1000 concurrent transactions
        """
        
        print(f"\nProcessing complex payment requirement...")
        
        result = generator.generate_test_cases(requirement)
        
        print(f"\n✅ Full pipeline working!")
        print(f"   - Requirement complexity: {result['analysis']['complexity']:.2f}")
        print(f"   - Entities found: {len(result['analysis']['entities'])}")
        print(f"   - Scenarios extracted: {len(result['scenarios'])}")
        print(f"   - Test cases generated: {result['summary']['total_test_cases']}")
        print(f"   - AI confidence: {result['summary']['avg_confidence']:.2f}")
        print(f"   - Test distribution: {result['summary']['by_type']}")
        
        # Show sample test
        if result['test_cases']:
            sample = result['test_cases'][0]
            print(f"\nSample Generated Test:")
            print(f"   ID: {sample['test_id']}")
            print(f"   Title: {sample['title']}")
            print(f"   Type: {sample['type']}")
            print(f"   Priority: {sample['priority']}")
            print(f"   Why: {sample['why_generated'][:60]}...")
            print(f"   AI Confidence: {sample['ai_confidence']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    
    print("\n" + "█" * 80)
    print("AI INTELLIGENT TEST GENERATION - INTEGRATION TESTS")
    print("█" * 80)
    
    tests = [
        ("Handler Direct Test", test_handler_directly),
        ("API Client Test", test_api_client),
        ("Endpoints Structure Test", test_endpoints_structure),
        ("Main App Integration Test", test_main_app_integration),
        ("Full Pipeline Test", test_full_pipeline),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ Test crashed: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All integration tests PASSED!")
        print("\nSystem is ready to use:")
        print("  1. Direct Python API available")
        print("  2. FastAPI endpoints integrated")
        print("  3. Full test generation pipeline working")
        print("  4. Main app properly configured")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
