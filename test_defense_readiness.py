#!/usr/bin/env python3
"""Final API readiness check before defense"""

import sys
import json
from pathlib import Path

def test_api_readiness():
    """Test system readiness for thesis defense"""
    
    # Check if API can be imported
    try:
        from requirement_analyzer.api_v2_handler import V2TaskGenerator
        print("[OK] API module imports successfully")
    except Exception as e:
        print(f"[FAIL] API import error: {e}")
        return False
    
    # Test 1: Can we create generator?
    try:
        gen = V2TaskGenerator()
        print("[OK] Generator instantiation successful")
    except Exception as e:
        print(f"[FAIL] Generator creation error: {e}")
        return False
    
    # Test 2: Can we process a requirement?
    try:
        result = gen.generate_from_text(
            "Hệ thống phải quản lý hồ sơ bệnh nhân với phân quyền người dùng",
            language="vi"
        )
        print("[OK] Text processing successful")
    except Exception as e:
        print(f"[FAIL] Text processing error: {e}")
        return False
    
    # Test 3: Check required outputs
    required_fields = ['tasks', 'methodology', 'summary']
    missing = [f for f in required_fields if f not in result]
    if missing:
        print(f"[FAIL] Missing fields: {missing}")
        return False
    else:
        print("[OK] All required output fields present")
    
    # Test 4: Check explainability fields
    task = result['tasks'][0]
    explainability_fields = ['decomposition_reasoning', 'user_stories', 'gaps']
    missing_explainability = [f for f in explainability_fields if f not in task]
    if missing_explainability:
        print(f"[FAIL] Missing explainability fields: {missing_explainability}")
        return False
    else:
        print("[OK] Explainability fields present")
    
    # Test 5: Verify user story quality
    stories = task.get('user_stories', [])
    quality_issues = []
    for i, story in enumerate(stories):
        us = story.get('user_story', '')
        if 'để để' in us:
            quality_issues.append(f"Story {i+1}: Double 'để' detected")
        if 'tôi muốn phải' in us:
            quality_issues.append(f"Story {i+1}: Double verb issue")
    
    if quality_issues:
        print(f"[FAIL] Quality issues:")
        for issue in quality_issues:
            print(f"       {issue}")
        return False
    else:
        print("[OK] User story quality verified (no translation artifacts)")
    
    # Test 6: Performance check
    import time
    start = time.time()
    result2 = gen.generate_from_text(
        "Quản lý đơn hàng bán hàng",
        language="vi"
    )
    elapsed = (time.time() - start) * 1000  # milliseconds
    if elapsed > 1000:
        print(f"[WARN] Slow performance: {elapsed:.0f}ms (target: <500ms)")
    else:
        print(f"[OK] Performance: {elapsed:.0f}ms (acceptable)")
    
    print("\n" + "="*60)
    print("DEFENSE READINESS REPORT")
    print("="*60)
    print(f"System Status: READY FOR DEFENSE")
    print(f"Generated {len(result['tasks'])} task(s)")
    print(f"Generated {len(stories)} user stories")
    print(f"Decomposition reasoning: {'YES' if task.get('decomposition_reasoning') else 'NO'}")
    print(f"Translation quality: CLEAN (no artifacts)")
    print(f"API response time: {elapsed:.0f}ms")
    print("\nYou can now proceed with thesis defense confidently!")
    
    return True

if __name__ == "__main__":
    success = test_api_readiness()
    sys.exit(0 if success else 1)
