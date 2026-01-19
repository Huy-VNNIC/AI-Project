#!/usr/bin/env python3
"""
Quick test to verify task generation installation
"""
import sys
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    required_modules = [
        ('sklearn', 'scikit-learn'),
        ('spacy', 'spacy'),
        ('nltk', 'nltk'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('pydantic', 'pydantic'),
        ('fastapi', 'fastapi'),
    ]
    
    failed = []
    
    for module_name, package_name in required_modules:
        try:
            __import__(module_name)
            print(f"  ✓ {package_name}")
        except ImportError:
            print(f"  ✗ {package_name} - NOT FOUND")
            failed.append(package_name)
    
    if failed:
        print(f"\n❌ Missing packages: {', '.join(failed)}")
        print("\nInstall with:")
        print(f"  pip install {' '.join(failed)}")
        return False
    
    print("\n✅ All required packages installed")
    return True


def test_spacy_model():
    """Test if spaCy model is downloaded"""
    print("\n🔍 Testing spaCy model...")
    
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("  ✓ en_core_web_sm loaded")
        return True
    except OSError:
        print("  ✗ en_core_web_sm - NOT FOUND")
        print("\nDownload with:")
        print("  python -m spacy download en_core_web_sm")
        return False


def test_nltk_data():
    """Test if NLTK data is downloaded"""
    print("\n🔍 Testing NLTK data...")
    
    try:
        import nltk
        
        required_data = [
            ('tokenizers/punkt', 'punkt'),
            ('corpora/stopwords', 'stopwords'),
            ('corpora/wordnet', 'wordnet'),
        ]
        
        failed = []
        for resource, name in required_data:
            try:
                nltk.data.find(resource)
                print(f"  ✓ {name}")
            except LookupError:
                print(f"  ✗ {name} - NOT FOUND")
                failed.append(name)
        
        if failed:
            print(f"\nDownload missing data:")
            print(f"  python -c \"import nltk; nltk.download({failed})\"")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_project_structure():
    """Test if project structure is correct"""
    print("\n🔍 Testing project structure...")
    
    project_root = Path(__file__).parent
    
    required_dirs = [
        'requirement_analyzer/task_gen',
        'scripts/task_generation',
        'data',
        'models',
    ]
    
    required_files = [
        'requirement_analyzer/task_gen/__init__.py',
        'requirement_analyzer/task_gen/pipeline.py',
        'requirement_analyzer/task_gen/schemas.py',
        'scripts/task_generation/train_all.sh',
    ]
    
    all_good = True
    
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"  ✓ {dir_path}/")
        else:
            print(f"  ✗ {dir_path}/ - NOT FOUND")
            all_good = False
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} - NOT FOUND")
            all_good = False
    
    return all_good


def test_dataset():
    """Test if dataset exists"""
    print("\n🔍 Testing dataset...")
    
    project_root = Path(__file__).parent
    
    datasets = [
        'requirement_analyzer/dataset_small_10k',
        'requirement_analyzer/dataset_medium_100k',
        'requirement_analyzer/dataset_large_1m',
    ]
    
    found = []
    for dataset in datasets:
        dataset_path = project_root / dataset
        if dataset_path.exists():
            csv_files = list(dataset_path.glob('chunk_*.csv'))
            print(f"  ✓ {dataset} ({len(csv_files)} files)")
            found.append(dataset)
        else:
            print(f"  ✗ {dataset} - NOT FOUND")
    
    if not found:
        print("\n⚠️  No datasets found!")
        print("Please ensure dataset files are in place")
        return False
    
    return True


def test_api_import():
    """Test if API can import task_gen module"""
    print("\n🔍 Testing API integration...")
    
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    try:
        from requirement_analyzer.task_gen import (
            get_pipeline,
            GeneratedTask,
            TaskGenerationRequest
        )
        print("  ✓ task_gen module imports successfully")
        print("  ✓ Pipeline available")
        print("  ✓ Schemas available")
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False


def main():
    """Run all tests"""
    print("="*70)
    print("🧪 TASK GENERATION INSTALLATION TEST")
    print("="*70)
    
    results = []
    
    # Run tests
    results.append(("Package imports", test_imports()))
    results.append(("spaCy model", test_spacy_model()))
    results.append(("NLTK data", test_nltk_data()))
    results.append(("Project structure", test_project_structure()))
    results.append(("Dataset", test_dataset()))
    results.append(("API integration", test_api_import()))
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready.")
        print("\n🚀 Next steps:")
        print("  1. Train models: cd scripts/task_generation && ./train_all.sh")
        print("  2. Run demo: python scripts/task_generation/demo.py")
        print("  3. Start API: cd requirement_analyzer && python api.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
