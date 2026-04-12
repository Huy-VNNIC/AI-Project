#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test decomposition logic"""

import sys
sys.path.insert(0, "requirement_analyzer")

from task_Invest_text import InvestAnalyzer

# Test the decomposition
analyzer = InvestAnalyzer()

test_text = "Xây dựng toàn bộ hệ thống quản lý dự án Agile"
print(f"Input: {test_text}")
print(f"Input length: {len(test_text)}")
print()

results = analyzer.analyze_many(test_text)
print(f"Number of results: {len(results)}")
print()

for i, result in enumerate(results, 1):
    print(f"Result {i}:")
    print(f"  Title: {result.get('title', 'N/A')}")
    print(f"  Score: {result.get('score', 0)}")
    print(f"  Original: {result.get('original', 'N/A')[:50]}...")
    print(f"  Criteria: {result.get('criteria', {})}")
    print(f"  Issues: {result.get('issues', [])}")
    print()

if len(results) == 3:
    print("✅ Decomposition successful! 3 tasks generated.")
else:
    print(f"❌ Expected 3 results, got {len(results)}")
