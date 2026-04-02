#!/usr/bin/env python
"""Quick test of Enhanced Test Generator"""

from requirement_analyzer.task_gen.enhanced_test_generator import EnhancedTestGenerator

generator = EnhancedTestGenerator()
requirements = [
    'Patient can book appointments up to 30 days in advance',
    'System must prevent unauthorized access to medical records'
]

results = generator.generate(requirements, max_tests=10)
print(f'✅ Generated {results["summary"]["total_test_cases"]} test cases')
print(f'Quality: {results["summary"]["avg_quality_score"]:.2%}')
print(f'Distribution: {results["summary"]["test_type_distribution"]}')

if results['test_cases']:
    print(f'\n--- FIRST TEST CASE ---')
    tc = results['test_cases'][0]
    print(f'ID: {tc["test_id"]}')
    print(f'Title: {tc["title"]}')
    print(f'Type: {tc["test_type"]}')
    print(f'Priority: {tc["priority"]}')
    print(f'Quality Score: {tc["ml_quality_score"]:.2%}')
    print(f'Effort: {tc["effort_hours"]:.1f}h')
    print(f'\nPreconditions:')
    for pc in tc["preconditions"]:
        print(f'  • {pc}')
    print(f'\nTest Data:')
    for key, val in tc["test_data"].items():
        print(f'  {key}: {val}')
    print(f'\nSteps:')
    for step in tc["steps"]:
        print(f'  {step["order"]}. {step["action"]}')
        print(f'     Expected: {step["expected_result"]}')
    print(f'\nExpected Result: {tc["expected_result"]}')
