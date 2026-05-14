#!/usr/bin/env python3
"""Quick test for the new AI test generator."""
import sys, json
sys.path.insert(0, '.')

# Clear any cached modules
for key in list(sys.modules.keys()):
    if 'smart_ai_generator' in key or 'task_gen' in key:
        del sys.modules[key]

from requirement_analyzer.task_gen.smart_ai_generator_v2_new import AITestGenerator

gen = AITestGenerator()

reqs = [
    'The system shall allow users to browse products by category.',
    'The application must support user registration with email verification.',
    'Users should be able to add products to a shopping cart.',
    'The platform must integrate with payment gateways for secure checkout.',
    'The system shall send confirmation emails for orders.',
    'Patients should be able to schedule appointments up to 30 days in advance.',
    'The system shall prevent unauthorized access to patient medical records.',
]

results = gen.generate(reqs, max_tests=10)

print("=" * 80)
print(f'Total: {results["summary"]["total_test_cases"]}')
print(f'Avg quality: {results["summary"]["avg_quality_score"]:.1%}')
print(f'Types: {json.dumps(results["summary"]["test_type_distribution"])}')
print(f'Domains: {json.dumps(results["summary"].get("domain_distribution", {}))}')
print("=" * 80)

for tc in results['test_cases']:
    print(f'{tc["test_id"]:20s} | {tc["domain"]:15s} | {tc["test_type"]:15s} | {tc["title"][:70]}')

print("=" * 80)
# Show first 2 in detail
for tc in results['test_cases'][:2]:
    print(f'\n--- {tc["test_id"]} ---')
    print(f'Title: {tc["title"]}')
    print(f'Type: {tc["test_type"]} | Priority: {tc["priority"]} | Domain: {tc["domain"]}')
    print(f'Why: {tc["why_generated"]}')
    print(f'Quality: {tc["ml_quality_score"]:.1%} | Effort: {tc["effort_hours"]}h')
    for s in tc["steps"][:3]:
        print(f'  {s["order"]}. {s["action"][:80]}')
        print(f'     -> {s["expected_result"][:80]}')
