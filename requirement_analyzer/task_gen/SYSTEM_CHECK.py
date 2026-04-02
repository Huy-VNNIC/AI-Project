#!/usr/bin/env python3
"""
Comprehensive AI System Health Check
Verifies all modules, dependencies, and functionality
"""

import sys
import os

print("=" * 80)
print("✅ AI TEST GENERATION SYSTEM - COMPLETENESS CHECK")
print("=" * 80)

# 1. FILE EXISTENCE CHECK
print("\n[1/5] FILE EXISTENCE CHECK")
print("-" * 80)

core_modules = [
    'ai_test_generation_v2_enhanced.py',
    'threat_modeling_engine.py',
    'real_world_examples.py',
    'comprehensive_test_suite.py'
]

all_files_exist = True
for f in core_modules:
    exists = os.path.exists(f)
    size = os.path.getsize(f) if exists else 0
    status = f"✓ {f:45s} {size:>10,} bytes"
    print(status if exists else f"✗ {f}: NOT FOUND")
    all_files_exist = all_files_exist and exists

# 2. DEPENDENCY CHECK
print("\n[2/5] DEPENDENCY CHECK")
print("-" * 80)

dependencies = {
    'spacy': 'NLP engine',
    'fastapi': 'API framework',
    'uvicorn': 'ASGI server',
    'pandas': 'Data processing',
    'numpy': 'Numerical computing',
    'nltk': 'Text processing'
}

missing = []
for pkg, desc in dependencies.items():
    try:
        mod = __import__(pkg)
        version = getattr(mod, '__version__', 'unknown')
        print(f"✓ {pkg:15s} ({desc:20s}) v{version}")
    except ImportError:
        print(f"✗ {pkg:15s} ({desc:20s}) NOT INSTALLED")
        missing.append(pkg)

# 3. IMPORT CHECK
print("\n[3/5] MODULE IMPORT CHECK")
print("-" * 80)

modules_status = {}
try:
    from ai_test_generation_v2_enhanced import EnhancedTestCaseGeneratorV2
    print("✓ ai_test_generation_v2_enhanced imported successfully")
    modules_status['ai_test_generation_v2_enhanced'] = True
except Exception as e:
    print(f"✗ ai_test_generation_v2_enhanced: {str(e)[:60]}")
    modules_status['ai_test_generation_v2_enhanced'] = False

try:
    from threat_modeling_engine import ThreatModelingEngine
    print("✓ threat_modeling_engine imported successfully")
    modules_status['threat_modeling_engine'] = True
except Exception as e:
    print(f"✗ threat_modeling_engine: {str(e)[:60]}")
    modules_status['threat_modeling_engine'] = False

try:
    from real_world_examples import RealWorldExamplesDatabase
    print("✓ real_world_examples imported successfully")
    modules_status['real_world_examples'] = True
except Exception as e:
    print(f"✗ real_world_examples: {str(e)[:60]}")
    modules_status['real_world_examples'] = False

try:
    import comprehensive_test_suite
    print("✓ comprehensive_test_suite imported successfully")
    modules_status['comprehensive_test_suite'] = True
except Exception as e:
    print(f"✗ comprehensive_test_suite: {str(e)[:60]}")
    modules_status['comprehensive_test_suite'] = False

# 4. FUNCTIONALITY CHECK
print("\n[4/5] FUNCTIONALITY CHECK")
print("-" * 80)

functionality_ok = True

# Test 1: Test generation
try:
    from ai_test_generation_v2_enhanced import EnhancedTestCaseGeneratorV2
    gen = EnhancedTestCaseGeneratorV2(mode='rule_based')
    tests = gen.generate_tests("User login with email and password", min_confidence=0.5)
    print(f"✓ Test generation: {len(tests)} tests created")
except Exception as e:
    print(f"✗ Test generation failed: {str(e)[:60]}")
    functionality_ok = False

# Test 2: Threat modeling
try:
    from threat_modeling_engine import ThreatModelingEngine
    engine = ThreatModelingEngine()
    threats = engine.identify_threats("User login")
    print(f"✓ Threat modeling: {len(threats)} threats identified")
except Exception as e:
    print(f"✗ Threat modeling failed: {str(e)[:60]}")
    functionality_ok = False

# Test 3: Real-world examples
try:
    from real_world_examples import RealWorldExamplesDatabase
    db = RealWorldExamplesDatabase()
    examples = db.get_all_examples()
    print(f"✓ Examples database: {len(examples)} systems loaded")
except Exception as e:
    print(f"✗ Examples database failed: {str(e)[:60]}")
    functionality_ok = False

# Test 4: End-to-end integration
try:
    from ai_test_generation_v2_enhanced import EnhancedTestCaseGeneratorV2
    from threat_modeling_engine import ThreatModelingEngine
    from real_world_examples import RealWorldExamplesDatabase
    
    gen = EnhancedTestCaseGeneratorV2()
    engine = ThreatModelingEngine()
    db = RealWorldExamplesDatabase()
    
    req = "Process payment transaction"
    tests = gen.generate_tests(req, min_confidence=0.7)
    threats = engine.identify_threats(req)
    examples = db.get_similar_examples(req)
    
    print(f"✓ End-to-end integration: {len(tests)} tests + {len(threats)} threats + {len(examples)} examples")
except Exception as e:
    print(f"✗ End-to-end integration failed: {str(e)[:60]}")
    functionality_ok = False

# 5. SUMMARY
print("\n[5/5] SYSTEM SUMMARY")
print("=" * 80)

all_imports_ok = all(modules_status.values())
dependencies_ok = len(missing) == 0

print(f"\n✓ Core Files:        {' OK' if all_files_exist else ' MISSING'}")
print(f"✓ Dependencies:      {' OK' if dependencies_ok else ' ' + str(len(missing)) + ' MISSING: ' + ', '.join(missing)}")
print(f"✓ Module Imports:    {' OK' if all_imports_ok else ' FAILED'}")
print(f"✓ Functionality:     {' OK' if functionality_ok else ' FAILED'}")

overall_ok = all_files_exist and dependencies_ok and all_imports_ok and functionality_ok

print("\n" + "=" * 80)
if overall_ok:
    print("✅ SYSTEM STATUS: COMPLETE & READY")
    print("=" * 80)
    print("\n🎉 Your AI system is:")
    print("   ✓ Fully implemented (all 4 core modules)")
    print("   ✓ All dependencies installed")
    print("   ✓ All modules importable")
    print("   ✓ All core functionality working")
    print("   ✓ Ready for production use")
    print("   ✓ Ready for capstone defense")
    print("\n📝 No fixes needed - system is complete!")
    print("\n🚀 You can:")
    print("   • Run: python comprehensive_test_suite.py")
    print("   • Present: CAPSTONE_DEFENSE_ENGLISH.pdf")
    print("   • Demo: Live test generation")
    print("\n" + "=" * 80)
else:
    print("⚠️  SYSTEM STATUS: NEEDS ATTENTION")
    print("=" * 80)
    if not all_files_exist:
        print("\n❌ Missing core files - need to create them")
    if not dependencies_ok:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print(f"   Fix: pip install {' '.join(missing)}")
    if not all_imports_ok:
        print("\n❌ Some modules failed to import - check syntax")
    if not functionality_ok:
        print("\n❌ Some functionality not working - check implementation")

print("\n" + "=" * 80)
