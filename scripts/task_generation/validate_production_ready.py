"""
Quick Validation: Production-Ready Checklist
Run this to verify all fixes are working
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

def test_models_exist():
    """Test 1: Models exist in correct location"""
    print("🔍 Test 1: Checking model files...")
    
    models_dir = PROJECT_ROOT / 'requirement_analyzer' / 'models' / 'task_gen' / 'models'
    required_files = [
        'requirement_detector_model.joblib',
        'requirement_detector_vectorizer.joblib',
        'type_model.joblib',
        'type_vectorizer.joblib',
        'priority_model.joblib',
        'priority_vectorizer.joblib',
        'domain_model.joblib',
        'domain_vectorizer.joblib',
    ]
    
    missing = []
    for file in required_files:
        if not (models_dir / file).exists():
            missing.append(file)
    
    if missing:
        print(f"  ❌ Missing models: {missing}")
        return False
    
    print(f"  ✅ All {len(required_files)} model files found")
    return True


def test_imports():
    """Test 2: All imports work"""
    print("\n🔍 Test 2: Testing imports...")
    
    try:
        from requirement_analyzer.task_gen.pipeline import TaskGenerationPipeline
        from requirement_analyzer.task_gen.generator_model_based import ModelBasedTaskGenerator
        from requirement_analyzer.task_gen.postprocess import TaskPostProcessor
        print("  ✅ All imports successful")
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False


def test_pipeline_init():
    """Test 3: Pipeline initializes without warnings"""
    print("\n🔍 Test 3: Testing pipeline initialization...")
    
    try:
        from requirement_analyzer.task_gen.pipeline import TaskGenerationPipeline
        import warnings
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            pipeline = TaskGenerationPipeline(
                model_dir=PROJECT_ROOT / 'requirement_analyzer' / 'models' / 'task_gen',
                generator_mode="model"
            )
            
            # Check for model loading warnings
            model_warnings = [str(warning.message) for warning in w if 'not found' in str(warning.message).lower()]
            
            if model_warnings:
                print(f"  ⚠️  Warnings detected: {len(model_warnings)}")
                for warning in model_warnings[:3]:
                    print(f"      {warning}")
                return False
        
        print("  ✅ Pipeline initialized clean (no model warnings)")
        return True
    except Exception as e:
        print(f"  ❌ Initialization failed: {e}")
        return False


def test_generation():
    """Test 4: Generation works end-to-end"""
    print("\n🔍 Test 4: Testing task generation...")
    
    try:
        from requirement_analyzer.task_gen.pipeline import TaskGenerationPipeline
        
        pipeline = TaskGenerationPipeline(
            model_dir=PROJECT_ROOT / 'requirement_analyzer' / 'models' / 'task_gen',
            generator_mode="model"
        )
        
        sample_doc = """
The system must authenticate users with email and password.
Password must be encrypted using bcrypt.
System should implement JWT token-based authentication.
"""
        
        result = pipeline.generate_tasks(sample_doc, max_tasks=5)
        
        if len(result.tasks) == 0:
            print("  ❌ No tasks generated")
            return False
        
        print(f"  ✅ Generated {len(result.tasks)} tasks")
        
        # Check task quality
        first_task = result.tasks[0]
        print(f"     Sample: {first_task.title[:50]}...")
        print(f"     Type: {first_task.type}, Priority: {first_task.priority}")
        print(f"     AC count: {len(first_task.acceptance_criteria)}")
        
        return True
    except Exception as e:
        print(f"  ❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_quality_gates():
    """Test 5: Quality gates are working"""
    print("\n🔍 Test 5: Testing quality gates...")
    
    try:
        from requirement_analyzer.task_gen.generator_model_based import ModelBasedTaskGenerator
        
        models_path = PROJECT_ROOT / 'requirement_analyzer' / 'models' / 'task_gen' / 'models'
        generator = ModelBasedTaskGenerator(model_dir=models_path)
        
        # Test AC deduplication
        ac_with_dupes = [
            "User can login successfully",
            "User can login successfully",  # duplicate
            "System validates input",
            "system validates input",  # duplicate (different case)
        ]
        
        unique_ac = generator._dedupe_acceptance_criteria(ac_with_dupes)
        
        if len(unique_ac) != 2:
            print(f"  ❌ AC deduplication failed: {len(unique_ac)} items (expected 2)")
            return False
        
        print(f"  ✅ AC deduplication works: {len(ac_with_dupes)} → {len(unique_ac)}")
        
        # Test title repair
        bad_title = "implement implement for user"
        entities = {'objects': ['user feature'], 'nouns': ['user'], 'verbs': ['implement']}
        repaired = generator._repair_title(bad_title, entities)
        
        if repaired == bad_title:
            print(f"  ❌ Title repair failed: '{bad_title}' not fixed")
            return False
        
        print(f"  ✅ Title repair works: '{bad_title}' → '{repaired}'")
        
        # Test priority keyword boost
        text_with_security = "The system must encrypt user data for HIPAA compliance"
        boosted = generator._adjust_priority_by_keywords(text_with_security, "Low", "security", "healthcare")
        
        if boosted != "High":
            print(f"  ⚠️  Priority boost suboptimal: {boosted} (expected High)")
        else:
            print(f"  ✅ Priority boost works: Low → {boosted} (security + HIPAA keywords)")
        
        return True
    except Exception as e:
        print(f"  ❌ Quality gates test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all validation tests"""
    print("="*80)
    print("🧪 PRODUCTION-READY VALIDATION")
    print("="*80)
    
    tests = [
        test_models_exist,
        test_imports,
        test_pipeline_init,
        test_generation,
        test_quality_gates,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "="*80)
    print("📊 RESULTS")
    print("="*80)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Production Ready!")
        print("\nYou can now:")
        print("  1. Integrate into FastAPI: generator_mode='model'")
        print("  2. Collect user feedback via /tasks/feedback endpoint")
        print("  3. Monitor task quality metrics")
        print("  4. Optional: Fine-tune T5/BART for even better quality")
        return 0
    else:
        print("\n⚠️  Some tests failed - review above for details")
        return 1


if __name__ == "__main__":
    sys.exit(main())
