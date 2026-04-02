#!/usr/bin/env python3
"""Test explainability and user story wording improvements"""

from requirement_analyzer.api_v2_handler import V2TaskGenerator
import json

def test_xai_features():
    gen = V2TaskGenerator()
    result = gen.generate_from_text(
        "Hệ thống phải quản lý hồ sơ bệnh nhân với phân quyền người dùng",
        language="vi"
    )
    
    print("=" * 70)
    print("TEST V2 WITH EXPLAINABILITY (XAI)")
    print("=" * 70)
    
    # Show explanation for decomposition
    task = result.get('tasks', [{}])[0]
    print(f"\n[1] REQUIREMENT:")
    print(f"    {task.get('original_requirement')}")
    
    print(f"\n[2] DECOMPOSITION REASONING:")
    decomp = task.get('decomposition_reasoning', {})
    print(f"    Summary: {decomp.get('summary')}")
    print(f"    Aspects addressed:")
    for aspect in decomp.get('aspects', []):
        print(f"      - {aspect}")
    
    print(f"\n[3] USER STORIES (Improved Format):")
    stories = task.get('user_stories', [])[:3]
    for i, story in enumerate(stories, 1):
        print(f"\n    Story {i}:")
        print(f"      Title: {story.get('title')}")
        print(f"      Format: {story.get('user_story')}")
        print(f"      Purpose: {story.get('why_this_story')}")
        print(f"      Points: {story.get('story_points')}")
    
    print(f"\n[4] GAP DETECTION (with Reasoning):")
    gaps = task.get('gaps', [])[:2]
    for i, gap in enumerate(gaps, 1):
        print(f"\n    Gap {i}:")
        print(f"      Type: {gap.get('type')} [{gap.get('severity')}]")
        reasoning = gap.get('reasoning', {})
        print(f"      Why Gap: {reasoning.get('why_its_a_gap')}")
        print(f"      Question: {gap.get('question')}")
    
    print(f"\n[5] METHODOLOGY:")
    meth = result.get('methodology', {})
    print(f"    Approach: {meth.get('approach')}")
    for stage in meth.get('stages', []):
        print(f"      - {stage}")
    
    print("\n" + "=" * 70)
    print("RESULTS:")
    print("=" * 70)
    
    # Validation checks
    checks = {
        "Decomposition reasoning present": bool(decomp),
        "User stories have why_this_story": all(s.get('why_this_story') for s in stories),
        "Gaps have reasoning": all(g.get('reasoning') for g in gaps),
        "Methodology documented": bool(meth),
    }
    
    for check, result in checks.items():
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {check}")
    
    # Check user story format quality
    print("\n[USER STORY QUALITY CHECK]:")
    issue_found = False
    for i, story in enumerate(stories, 1):
        us = story.get('user_story', '')
        # Check for double verb (tôi muốn phải)
        if 'tôi muốn phải' in us:
            print(f"  [FAIL] Story {i} has double verb issue: {us}")
            issue_found = True
        elif 'Là một' in us and ('để') in us:
            print(f"  [PASS] Story {i} has proper format")
        else:
            print(f"  [PASS] Story {i} format acceptable")
    
    if not issue_found:
        print("\n  * No translation artifacts detected")
        print("  * Ready for thesis defense!")
    
    return all(checks.values()) and not issue_found

if __name__ == "__main__":
    success = test_xai_features()
    exit(0 if success else 1)
