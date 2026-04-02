#!/usr/bin/env python3
"""Test all imports to ensure no errors"""

import sys

print("=" * 80)
print("IMPORT VERIFICATION TEST")
print("=" * 80)

failed = []

# Test each import
tests = [
    ("FastAPI app", "from app.main import app, PURE_ML_ROUTER_AVAILABLE; assert PURE_ML_ROUTER_AVAILABLE"),
    ("Pure ML API Adapter", "from requirement_analyzer.pure_ml_api_adapter import PureMLAPIAdapter"),
    ("Pure ML Parser", "from requirement_analyzer.task_gen.llm_parser_pure import PureMLParser"),
    ("Pure ML Generator", "from requirement_analyzer.task_gen.llm_test_generator_pure import PureMLTestGenerator"),
    ("Feedback System", "from requirement_analyzer.task_gen.feedback_system import FeedbackCollector"),
    ("Orchestrator", "from requirement_analyzer.task_gen.pure_ml_test_generator_v3 import PureMLTestCaseGeneratorV3"),
]

for name, import_stmt in tests:
    try:
        exec(import_stmt)
        print(f"✅ {name:40} - OK")
    except Exception as e:
        error_msg = str(e)[:80]
        print(f"❌ {name:40} - FAIL: {error_msg}")
        failed.append(name)

print("=" * 80)
if failed:
    print(f"❌ {len(failed)} import(s) failed:")
    for f in failed:
        print(f"   - {f}")
    sys.exit(1)
else:
    print(f"✅ All {len(tests)} imports successful!")
    sys.exit(0)
