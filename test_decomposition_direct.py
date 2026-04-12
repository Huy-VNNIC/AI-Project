#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os

# Set encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add path
sys.path.insert(0, 'requirement_analyzer')

# Import the analyzer directly
from task_Invest_text import InvestAnalyzer

analyzer = InvestAnalyzer()

# Test with Vietnamese text
test_text = "Xây dựng toàn bộ hệ thống quản lý dự án Agile"

print("=" * 60)
print("TEST: Direct Decomposition")
print("=" * 60)
print(f"Input text: {test_text}")
print(f"Input length: {len(test_text)} characters")
print()

# Call analyze_many
results = analyzer.analyze_many(test_text)

print(f"Results count: {len(results)}")
print()

if len(results) == 3:
    print("✓ SUCCESS: Decomposition worked! Got 3 tasks")
    for i, result in enumerate(results, 1):
        title = result.get('title', 'N/A')
        score = result.get('score', 0)
        print(f"  {i}. {title} (score: {score})")
else:
    print(f"✗ FAILED: Expected 3 results, got {len(results)}")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result.get('title', result.get('original', '')[:50])}")
