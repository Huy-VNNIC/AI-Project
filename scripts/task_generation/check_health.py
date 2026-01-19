#!/usr/bin/env python3
"""
System Health Check for Task Generation

Verifies all components are working correctly.
Run before deploying to production.
"""

import sys
import os
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# ==============================================================================
# Health Checks
# ==============================================================================

def check_dependencies():
    """Check if all required packages are installed."""
    logger.info("🔍 Checking dependencies...")
    
    required = {
        'sklearn': 'scikit-learn',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'spacy': 'spacy',
        'pydantic': 'pydantic',
        'fastapi': 'fastapi',
        'pyarrow': 'pyarrow'
    }
    
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
            logger.info(f"  ✅ {package}")
        except ImportError:
            logger.error(f"  ❌ {package} - NOT FOUND")
            missing.append(package)
    
    return len(missing) == 0, missing


def check_spacy_model():
    """Check if spaCy model is downloaded."""
    logger.info("🔍 Checking spaCy model...")
    
    try:
        import spacy
        nlp = spacy.load('en_core_web_sm')
        logger.info(f"  ✅ en_core_web_sm (version {nlp.meta['version']})")
        return True
    except OSError:
        logger.error("  ❌ en_core_web_sm - NOT FOUND")
        logger.info("     Run: python -m spacy download en_core_web_sm")
        return False


def check_dataset():
    """Check if dataset exists."""
    logger.info("🔍 Checking dataset...")
    
    paths = [
        'datasets/dataset_large_1m',
        'datasets/dataset_small_10k'
    ]
    
    for path in paths:
        if Path(path).exists():
            chunks = list(Path(path).glob('chunk_*.csv'))
            if chunks:
                logger.info(f"  ✅ {path} ({len(chunks)} chunks)")
                return True
    
    logger.error("  ❌ Dataset not found")
    logger.info("     Expected: datasets/dataset_large_1m/ or dataset_small_10k/")
    return False


def check_trained_models():
    """Check if models are trained."""
    logger.info("🔍 Checking trained models...")
    
    model_path = Path('models/task_gen')
    if not model_path.exists():
        logger.warning("  ⚠️  models/task_gen/ directory not found")
        return False
    
    expected_models = [
        'requirement_detector_*.joblib',
        'type_classifier_*.joblib',
        'priority_classifier_*.joblib',
        'domain_classifier_*.joblib'
    ]
    
    found = []
    for pattern in expected_models:
        matches = list(model_path.glob(pattern))
        if matches:
            logger.info(f"  ✅ {pattern.replace('_*.joblib', '')} ({len(matches)} versions)")
            found.append(True)
        else:
            logger.warning(f"  ⚠️  {pattern} - NOT FOUND")
            found.append(False)
    
    if not all(found):
        logger.info("     Run: bash scripts/task_generation/run_full_pipeline.sh")
        return False
    
    return True


def check_module_import():
    """Check if task_gen module can be imported."""
    logger.info("🔍 Checking task_gen module...")
    
    try:
        from requirement_analyzer.task_gen import (
            get_pipeline,
            GeneratedTask,
            TaskGenerationRequest,
            TaskGenerationResponse
        )
        logger.info("  ✅ Module imports successfully")
        return True
    except ImportError as e:
        logger.error(f"  ❌ Import failed: {e}")
        return False


def check_pipeline_initialization():
    """Check if pipeline can be initialized."""
    logger.info("🔍 Checking pipeline initialization...")
    
    try:
        from requirement_analyzer.task_gen import get_pipeline
        
        # Try template mode
        pipeline = get_pipeline(mode='template')
        logger.info("  ✅ Template mode pipeline initialized")
        return True
    except Exception as e:
        logger.error(f"  ❌ Pipeline initialization failed: {e}")
        return False


def check_basic_generation():
    """Test basic task generation."""
    logger.info("🔍 Testing basic task generation...")
    
    try:
        from requirement_analyzer.task_gen import get_pipeline
        
        pipeline = get_pipeline(mode='template')
        
        # Simple test
        test_doc = """
        Users must be able to login with email and password.
        System should validate credentials against database.
        """
        
        result = pipeline.generate_tasks(test_doc, max_tasks=5)
        
        if result.total_tasks > 0:
            logger.info(f"  ✅ Generated {result.total_tasks} tasks")
            logger.info(f"     First task: {result.tasks[0].title}")
            return True
        else:
            logger.warning("  ⚠️  No tasks generated")
            return False
            
    except Exception as e:
        logger.error(f"  ❌ Generation failed: {e}")
        return False


def check_api_imports():
    """Check if API can import task_gen."""
    logger.info("🔍 Checking API integration...")
    
    try:
        sys.path.insert(0, str(Path('requirement_analyzer')))
        
        # Check if api.py exists
        if not Path('requirement_analyzer/api.py').exists():
            logger.error("  ❌ api.py not found")
            return False
        
        # Try to import (without starting server)
        import api
        logger.info("  ✅ API module imports successfully")
        return True
    except ImportError as e:
        logger.error(f"  ❌ API import failed: {e}")
        return False
    except Exception as e:
        logger.warning(f"  ⚠️  API check skipped: {e}")
        return True  # Don't fail if api has other issues


def check_directories():
    """Check required directory structure."""
    logger.info("🔍 Checking directory structure...")
    
    required = {
        'data/processed': 'Processed data',
        'data/splits': 'Train/val/test splits',
        'models/task_gen': 'Trained models',
        'report': 'Training reports',
        'logs': 'Log files'
    }
    
    all_exist = True
    for path, desc in required.items():
        p = Path(path)
        if p.exists():
            logger.info(f"  ✅ {path}/ ({desc})")
        else:
            logger.warning(f"  ⚠️  {path}/ missing - will be created on first run")
            all_exist = False
    
    return all_exist


def check_disk_space():
    """Check available disk space."""
    logger.info("🔍 Checking disk space...")
    
    try:
        import shutil
        total, used, free = shutil.disk_usage('.')
        
        free_gb = free // (2**30)
        
        if free_gb < 5:
            logger.warning(f"  ⚠️  Low disk space: {free_gb} GB free")
            logger.info("     Training and models require ~5 GB")
            return False
        else:
            logger.info(f"  ✅ Sufficient disk space: {free_gb} GB free")
            return True
    except Exception as e:
        logger.warning(f"  ⚠️  Could not check disk space: {e}")
        return True


# ==============================================================================
# Main Health Check
# ==============================================================================

def run_health_check():
    """Run all health checks."""
    logger.info("=" * 60)
    logger.info("🏥 Task Generation System Health Check")
    logger.info("=" * 60)
    
    checks = [
        ("Dependencies", check_dependencies),
        ("spaCy Model", check_spacy_model),
        ("Dataset", check_dataset),
        ("Directory Structure", check_directories),
        ("Disk Space", check_disk_space),
        ("Trained Models", check_trained_models),
        ("Module Import", check_module_import),
        ("Pipeline Init", check_pipeline_initialization),
        ("Basic Generation", check_basic_generation),
        ("API Integration", check_api_imports)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            logger.info("")
            result = check_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"❌ {name} check failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("📊 Health Check Summary")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status:10s} {name}")
    
    logger.info("")
    logger.info(f"Total: {passed}/{total} checks passed")
    
    if passed == total:
        logger.info("🎉 All checks passed! System is ready.")
        return 0
    elif passed >= total - 2:
        logger.warning("⚠️  System is partially ready. Some optional checks failed.")
        return 1
    else:
        logger.error("❌ System is NOT ready. Fix the issues above.")
        return 2


def quick_fix_suggestions():
    """Print quick fix suggestions for common issues."""
    logger.info("")
    logger.info("=" * 60)
    logger.info("🔧 Quick Fix Guide")
    logger.info("=" * 60)
    logger.info("")
    logger.info("If dependencies are missing:")
    logger.info("  pip install -r requirements.txt")
    logger.info("")
    logger.info("If spaCy model is missing:")
    logger.info("  python -m spacy download en_core_web_sm")
    logger.info("")
    logger.info("If models are not trained:")
    logger.info("  bash scripts/task_generation/run_full_pipeline.sh")
    logger.info("")
    logger.info("If dataset is missing:")
    logger.info("  Check: datasets/dataset_large_1m/ or datasets/dataset_small_10k/")
    logger.info("")
    logger.info("For full documentation:")
    logger.info("  See START_HERE.md or IMPLEMENTATION_SUMMARY.md")
    logger.info("")


# ==============================================================================
# CLI
# ==============================================================================

if __name__ == '__main__':
    exit_code = run_health_check()
    
    if exit_code != 0:
        quick_fix_suggestions()
    
    sys.exit(exit_code)
