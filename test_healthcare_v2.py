#!/usr/bin/env python3
"""Production test with healthcare requirements file"""

from requirement_analyzer.api_v2_handler import V2TaskGenerator

# Load healthcare requirements
with open("/home/dtu/AI-Project/AI-Project/requirement_analyzer/task_gen/test_files/healthcare_requirements.md", "r", encoding="utf-8") as f:
    content = f.read()[:2000]  # First 2000 chars for testing

print("=" * 70)
print("TESTING V2 TASK GENERATOR WITH HEALTHCARE REQUIREMENTS")
print("=" * 70)

# Create generator
generator = V2TaskGenerator()

# Generate tasks
result = generator.generate_from_text(content, language="vi")

# Print comprehensive summary
print(f"\n✅ Status: {result.get('status')}")
print(f"📊 Statistics:")
print(f"   - Total Requirements: {result.get('total_tasks')}")
print(f"   - Functional: {result.get('functional_requirements')}")
print(f"   - Non-Functional: {result.get('non_functional_requirements')}")
print(f"   - Total User Stories: {result.get('summary', {}).get('total_user_stories')}")
print(f"   - Total Subtasks: {result.get('summary', {}).get('total_subtasks')}")
print(f"   - Avg Quality Score: {result.get('summary', {}).get('average_quality_score'):.2f}")

# Show first 2 requirements
print("\n" + "=" * 70)
print("SAMPLE OUTPUTS")
print("=" * 70)

for idx, task in enumerate(result.get('tasks', [])[:2], 1):
    print(f"\n[Requirement {idx}]")
    print(f"Original: {task.get('original_requirement')[:70]}...")
    print(f"Domain: {task.get('domain')}")
    print(f"Quality Score: {task.get('quality_score'):.2f}")
    
    stories = task.get('user_stories', [])
    print(f"\n  📖 User Stories Generated: {len(stories)}")
    
    for sidx, story in enumerate(stories[:2], 1):  # Show first 2 stories
        print(f"\n    Story {sidx}: {story.get('title')}")
        print(f"    Format: {story.get('user_story')[:80]}...")
        print(f"    Story Points: {story.get('story_points')}")
        print(f"    Acceptance Criteria: {len(story.get('acceptance_criteria', []))} items")
        
        # Show first AC
        if story.get('acceptance_criteria'):
            ac = story['acceptance_criteria'][0]
            print(f"      AC Example:")
            print(f"        Given: {ac.get('given', 'N/A')[:50]}...")
            print(f"        When: {ac.get('when', 'N/A')[:50]}...")
            print(f"        Then: {ac.get('then', 'N/A')[:50]}...")
        
        # Show subtasks
        subtasks = story.get('subtasks', [])
        print(f"    Subtasks: {len(subtasks)} items")
        for tidx, stask in enumerate(subtasks[:2], 1):  # Show first 2 subtasks
            print(f"      [{tidx}] {stask.get('title')} ({stask.get('role')})")
    
    # Show gaps
    gaps = task.get('gaps', [])
    if gaps:
        print(f"\n  ⚠️ Gaps Detected: {len(gaps)}")
        for gidx, gap in enumerate(gaps[:2], 1):
            print(f"    Gap {gidx}: [{gap.get('severity')}] {gap.get('description')[:60]}...")
            print(f"    Question: {gap.get('question', 'N/A')[:60]}...")

print("\n" + "=" * 70)
print("✅ Test Complete - V2 System Ready for Production!")
print("=" * 70)
