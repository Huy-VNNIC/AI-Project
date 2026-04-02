#!/usr/bin/env python3
"""
Integration Test: Pure ML API End-to-End
Tests that the API is correctly set up without actually running the server
"""

import sys
import os
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_imports():
    """Test that all modules can be imported"""
    print("=" * 70)
    print("INTEGRATION TEST: Module Imports")
    print("=" * 70)
    
    tests = [
        ("FastAPI router", "from requirement_analyzer.api_v2_test_generation import pure_ml_router"),
        ("Pure ML adapter", "from requirement_analyzer.pure_ml_api_adapter import PureMLAPIAdapter"),
        ("App main", "from app.main import app, PURE_ML_ROUTER_AVAILABLE"),
    ]
    
    results = []
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            results.append((name, "✅ PASS"))
            print(f"  ✅ {name:30} - Imported successfully")
        except Exception as e:
            results.append((name, f"❌ FAIL: {str(e)[:50]}"))
            print(f"  ❌ {name:30} - {str(e)[:50]}")
    
    print()
    return all("✅" in r[1] for r in results)


def test_router_configuration():
    """Test that the router is properly configured"""
    print("=" * 70)
    print("INTEGRATION TEST: Router Configuration")
    print("=" * 70)
    
    try:
        from requirement_analyzer.api_v2_test_generation import pure_ml_router
        
        print(f"  Router Prefix: {pure_ml_router.prefix}")
        print(f"  Router Tags: {pure_ml_router.tags}")
        
        # Check routes
        routes_info = []
        for route in pure_ml_router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                routes_info.append(f"{', '.join(sorted(route.methods))} {route.path}")
        
        print(f"  Total Routes: {len(routes_info)}")
        for route in sorted(routes_info):
            print(f"    • {route}")
        
        required_routes = [
            "/api/v3/test-generation/generate",
            "/api/v3/test-generation/feedback",
            "/api/v3/test-generation/stats",
            "/api/v3/test-generation/insights"
        ]
        
        found_routes = [r.split()[-1] for r in routes_info]
        missing = [r for r in required_routes if r not in found_routes]
        
        if missing:
            print(f"\n  ❌ Missing routes: {missing}")
            return False
        else:
            print(f"\n  ✅ All required routes present")
            return True
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def test_app_configuration():
    """Test that the app has the Pure ML router registered"""
    print("\n" + "=" * 70)
    print("INTEGRATION TEST: App Configuration")
    print("=" * 70)
    
    try:
        from app.main import app, PURE_ML_ROUTER_AVAILABLE
        
        print(f"  PURE_ML_ROUTER_AVAILABLE: {PURE_ML_ROUTER_AVAILABLE}")
        
        if not PURE_ML_ROUTER_AVAILABLE:
            print("  ⚠️  Pure ML router not available (check imports)")
            return False
        
        # Check that the app has routes
        app_routes = [r.path for r in app.routes]
        v3_routes = [r for r in app_routes if "/api/v3/" in r]
        
        print(f"  App Total Routes: {len(app_routes)}")
        print(f"  V3 Routes: {len(v3_routes)}")
        
        if v3_routes:
            print(f"  ✅ V3 routes registered in app")
            for route in sorted(v3_routes):
                print(f"      • {route}")
            return True
        else:
            print(f"  ❌ No V3 routes found in app")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_file_syntax():
    """Test that modified files have correct Python syntax"""
    print("\n" + "=" * 70)
    print("INTEGRATION TEST: File Syntax")
    print("=" * 70)
    
    files = [
        "requirement_analyzer/api_v2_test_generation.py",
        "app/main.py",
    ]
    
    results = []
    for file in files:
        filepath = PROJECT_ROOT / file
        try:
            with open(filepath, 'r') as f:
                compile(f.read(), file, 'exec')
            print(f"  ✅ {file:45} - Valid Python syntax")
            results.append(True)
        except SyntaxError as e:
            print(f"  ❌ {file:45} - {e}")
            results.append(False)
    
    return all(results)


def test_endpoint_documentation():
    """Verify endpoint documentation is present"""
    print("\n" + "=" * 70)
    print("INTEGRATION TEST: Endpoint Documentation")
    print("=" * 70)
    
    try:
        from requirement_analyzer.api_v2_test_generation import (
            generate_test_cases_pure_ml,
            submit_test_feedback,
            get_pure_ml_stats,
            get_pure_ml_insights
        )
        
        endpoints = [
            ("generate_test_cases_pure_ml", generate_test_cases_pure_ml),
            ("submit_test_feedback", submit_test_feedback),
            ("get_pure_ml_stats", get_pure_ml_stats),
            ("get_pure_ml_insights", get_pure_ml_insights),
        ]
        
        for name, func in endpoints:
            has_docstring = bool(func.__doc__)
            status = "✅" if has_docstring else "⚠️"
            print(f"  {status} {name:30} - {'Has docstring' if has_docstring else 'No docstring'}")
        
        return all(bool(f.__doc__) for _, f in endpoints)
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def main():
    """Run all integration tests"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + "PURE ML API - INTEGRATION TEST SUITE".center(68) + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Router Config", test_router_configuration()))
    results.append(("App Config", test_app_configuration()))
    results.append(("File Syntax", test_file_syntax()))
    results.append(("Documentation", test_endpoint_documentation()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status:10} - {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Pure ML API is ready!")
        print("\nTo start the server:")
        print("  cd /home/dtu/AI-Project/AI-Project")
        print("  uvicorn app.main:app --reload")
        print("\nThen test endpoints:")
        print("  curl http://localhost:8000/api/v3/test-generation/stats")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - review errors above")
        return 1


if __name__ == "__main__":
    exit(main())
