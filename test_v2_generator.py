#!/usr/bin/env python3
"""Test V2 Task Generator"""

from requirement_analyzer.api_v2_handler import V2TaskGenerator

# Create generator
generator = V2TaskGenerator()

# Test with a simple requirement
test_req = """
1. Hệ thống phải quản lý hồ sơ bệnh nhân với thông tin chi tiết
2. Hệ thống phải xử lý 500 lượt khám đồng thời
3. Admin phải có khả năng tạo và chỉnh sửa tài khoản nhân viên
"""

print("Testing V2 Task Generator...")
print("=" * 60)

result = generator.generate_from_text(test_req, language="vi")

# Print summary
print(f"✓ Status: {result.get('status')}")
print(f"  Total Requirements: {result.get('total_tasks')}")
print(f"  Functional: {result.get('functional_requirements')}")
print(f"  Non-Functional: {result.get('non_functional_requirements')}")
print(f"  Total User Stories: {result.get('summary', {}).get('total_user_stories')}")
print(f"  Total Subtasks: {result.get('summary', {}).get('total_subtasks')}")

# Show first task
if result.get('tasks'):
    task = result['tasks'][0]
    print(f"\n[Requirement 1]:")
    print(f"  Original: {task.get('original_requirement')[:70]}...")
    if task.get('user_stories'):
        story = task['user_stories'][0]
        print(f"  User Story: {story.get('user_story')}")
        print(f"  Story Points: {story.get('story_points')}")
        print(f"  Acceptance Criteria: {len(story.get('acceptance_criteria', []))} items")
        if story.get('acceptance_criteria'):
            ac = story['acceptance_criteria'][0]
            print(f"    1. Given: {ac.get('given', 'N/A')}")
            print(f"       When: {ac.get('when', 'N/A')}")
            print(f"       Then: {ac.get('then', 'N/A')}")

print("\n" + "=" * 60)
print("✓ V2 Generator Test Complete!")
