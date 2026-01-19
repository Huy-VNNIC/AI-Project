"""
Quick test to verify task generation system is properly installed
"""
import sys
from pathlib import Path

def test_imports():
    """Test all required imports"""
    print("🔍 Testing imports...")
    
    try:
        import pandas as pd
        print("  ✓ pandas")
    except ImportError as e:
        print(f"  ❌ pandas: {e}")
        return False
    
    try:
        import numpy as np
        print("  ✓ numpy")
    except ImportError as e:
        print(f"  ❌ numpy: {e}")
        return False
    
    try:
        import sklearn
        print("  ✓ scikit-learn")
    except ImportError as e:
        print(f"  ❌ scikit-learn: {e}")
        return False
    
    try:
        import spacy
        print("  ✓ spacy")
    except ImportError as e:
        print(f"  ❌ spacy: {e}")
        return False
    
    try:
        import joblib
        print("  ✓ joblib")
    except ImportError as e:
        print(f"  ❌ joblib: {e}")
        return False
    
    try:
        import pyarrow
        print("  ✓ pyarrow")
    except ImportError as e:
        print(f"  ❌ pyarrow: {e}")
        return False
    
    return True


def test_spacy_model():
    """Test spaCy model is downloaded"""
    print("\n🔍 Testing spaCy model...")
    
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("  ✓ en_core_web_sm loaded")
        return True
    except OSError:
        print("  ⚠️  en_core_web_sm not found")
        print("     Run: python -m spacy download en_core_web_sm")
        return False


def test_modules():
    """Test task_gen modules can be imported"""
    print("\n🔍 Testing task_gen modules...")
    
    try:
        from requirement_analyzer.task_gen import schemas
        print("  ✓ schemas")
    except ImportError as e:
        print(f"  ❌ schemas: {e}")
        return False
    
    try:
        from requirement_analyzer.task_gen import segmenter
        print("  ✓ segmenter")
    except ImportError as e:
        print(f"  ❌ segmenter: {e}")
        return False
    
    try:
        from requirement_analyzer.task_gen import req_detector
        print("  ✓ req_detector")
    except ImportError as e:
        print(f"  ❌ req_detector: {e}")
        return False
    
    try:
        from requirement_analyzer.task_gen import enrichers
        print("  ✓ enrichers")
    except ImportError as e:
        print(f"  ❌ enrichers: {e}")
        return False
    
    try:
        from requirement_analyzer.task_gen import generator_templates
        print("  ✓ generator_templates")
    except ImportError as e:
        print(f"  ❌ generator_templates: {e}")
        return False
    
    try:
        from requirement_analyzer.task_gen import postprocess
        print("  ✓ postprocess")
    except ImportError as e:
        print(f"  ❌ postprocess: {e}")
        return False
    
    try:
        from requirement_analyzer.task_gen import pipeline
        print("  ✓ pipeline")
    except ImportError as e:
        print(f"  ❌ pipeline: {e}")
        return False
    
    return True


def test_dataset_exists():
    """Check if dataset exists"""
    print("\n🔍 Checking datasets...")
    
    datasets = [
        "requirement_analyzer/dataset_large_1m",
        "requirement_analyzer/dataset_medium_100k",
        "requirement_analyzer/dataset_small_10k"
    ]
    
    found = False
    for ds in datasets:
        path = Path(ds)
        if path.exists():
            csv_files = list(path.glob("chunk_*.csv"))
            print(f"  ✓ {ds} ({len(csv_files)} files)")
            found = True
        else:
            print(f"  ⚠️  {ds} not found")
    
    if not found:
        print("\n  ⚠️  No datasets found! Task generation training requires dataset.")
        print("     The system will still work with pre-trained models.")
    
    return True  # Not critical


def test_basic_functionality():
    """Test basic pipeline initialization"""
    print("\n🔍 Testing basic functionality...")
    
    try:
        from requirement_analyzer.task_gen import get_segmenter
        segmenter = get_segmenter()
        
        test_text = "The system must allow users to register. Users can update their profile."
        sections, sentences = segmenter.segment(test_text)
        
        if len(sentences) >= 2:
            print(f"  ✓ Segmenter works ({len(sentences)} sentences extracted)")
        else:
            print(f"  ⚠️  Segmenter might not be working correctly")
            return False
        
        return True
    except Exception as e:
        print(f"  ❌ Error testing segmenter: {e}")
        return False


def main():
    """Run all tests"""
    print("="*80)
    print("🧪 TASK GENERATION SYSTEM - INSTALLATION TEST")
    print("="*80)
    
    results = []
    
    # Test 1: Imports
    results.append(("Core imports", test_imports()))
    
    # Test 2: spaCy model
    results.append(("spaCy model", test_spacy_model()))
    
    # Test 3: Modules
    results.append(("Task gen modules", test_modules()))
    
    # Test 4: Dataset
    results.append(("Dataset availability", test_dataset_exists()))
    
    # Test 5: Basic functionality
    results.append(("Basic functionality", test_basic_functionality()))
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10s} {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed! System is ready.")
        print("\nNext steps:")
        print("  1. Train models: ./scripts/task_generation/run_full_pipeline.sh")
        print("  2. Or run demo: python scripts/task_generation/demo_task_generation.py")
        print("  3. Start API: python requirement_analyzer/api.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\nTo install missing packages:")
        print("  pip install -r requirements-task-generation.txt")
        print("  python -m spacy download en_core_web_sm")
        return 1


if __name__ == "__main__":
    sys.exit(main())
