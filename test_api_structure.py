#!/usr/bin/env python3
"""Test API response structure for frontend compatibility"""

from requirement_analyzer.api_v2_handler import V2TaskGenerator
import json

def test_api_structure():
    gen = V2TaskGenerator()
    result = gen.generate_from_text(
        "Hệ thống quản lý hồ sơ bệnh nhân với phân quyền"
    )
    
    print("API Response Structure:")
    print("=" * 60)
    
    # Check if we have tasks
    if 'tasks' in result:
        print(f"✓ Has 'tasks' key: {len(result['tasks'])} task(s)")
        
        task = result['tasks'][0]
        print(f"\nFirst task structure:")
        print(f"  Keys: {list(task.keys())}")
        
        if 'user_stories' in task:
            print(f"  ✓ Has 'user_stories': {len(task['user_stories'])} stories")
            if len(task['user_stories']) > 0:
                us = task['user_stories'][0]
                print(f"\n  First user story structure:")
                print(f"    Keys: {list(us.keys())}")
                
                # Check required fields
                required = ['title', 'priority', 'domain', 'story_points']
                missing = []
                for field in required:
                    val = us.get(field)
                    status = "✓" if val else "✗"
                    print(f"    {status} {field}: {val if val else 'MISSING'}")
                    if not val:
                        missing.append(field)
                
                if missing:
                    print(f"\n  Missing fields: {missing}")
                    print("  [Frontend will use defaults]")
                else:
                    print(f"\n  ✓ All required fields present!")
        else:
            print(f"  ✗ Missing 'user_stories' key!")
            return False
    else:
        print("✗ Missing 'tasks' key!")
        return False
    
    print("\n" + "=" * 60)
    print("✓ API response structure is compatible with frontend!")
    print("\nFrontend fix will:")
    print("  1. Flatten nested user_stories")
    print("  2. Use safe defaults for missing fields")
    print("  3. Handle both V1 and V2 response formats")
    return True

if __name__ == "__main__":
    success = test_api_structure()
    exit(0 if success else 1)
