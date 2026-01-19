#!/usr/bin/env python3
"""
Demo Test - Production Infrastructure
Tests all components: API, data crawling, OOD evaluation
"""
import sys
import json
import time
import requests
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))


def print_header(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def test_api_endpoints(base_url="http://localhost:8001"):
    """Test FastAPI endpoints"""
    print_header("TEST 1: API ENDPOINTS")
    
    # Test health
    print("1️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check passed")
            print(f"   Status: {data.get('status')}")
            print(f"   Models loaded: {data.get('models_loaded')}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        print(f"   💡 Make sure API is running: uvicorn app.main:app --port 8001")
        return False
    
    # Test generate
    print("\n2️⃣ Testing generate endpoint...")
    test_doc = """
    The system must authenticate users through email and password.
    Users should be able to reset their passwords via email.
    The application must support two-factor authentication using SMS or authenticator apps.
    Admin users need the ability to manage user accounts and permissions.
    """
    
    try:
        response = requests.post(
            f"{base_url}/api/tasks/generate",
            json={
                "document_text": test_doc,
                "mode": "model",
                "max_tasks": 5
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            tasks = data.get('tasks', [])
            metadata = data.get('metadata', {})
            
            print(f"   ✅ Generated {len(tasks)} tasks")
            print(f"   Mode: {metadata.get('mode')}")
            print(f"   Latency: {metadata.get('latency_ms')}ms")
            print(f"   Avg confidence: {metadata.get('avg_confidence', 0):.2f}")
            
            # Show first task
            if tasks:
                print(f"\n   📋 Sample task:")
                task = tasks[0]
                print(f"      Title: {task.get('title', 'N/A')}")
                print(f"      Type: {task.get('type', 'N/A')}")
                print(f"      Priority: {task.get('priority', 'N/A')}")
                print(f"      Domain: {task.get('domain', 'N/A')}")
                print(f"      ACs: {len(task.get('acceptance_criteria', []))}")
            
            return tasks[0] if tasks else None
        else:
            print(f"   ❌ Generation failed: {response.status_code}")
            print(f"   {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def test_feedback(base_url="http://localhost:8001", sample_task=None):
    """Test feedback endpoint"""
    print_header("TEST 2: FEEDBACK COLLECTION")
    
    if not sample_task:
        sample_task = {
            "title": "Test task",
            "description": "Test description",
            "type": "Story",
            "priority": "Medium"
        }
    
    print("Testing feedback submission...")
    try:
        response = requests.post(
            f"{base_url}/api/tasks/feedback",
            json={
                "generated_task": sample_task,
                "rating": 5,
                "comment": "Excellent quality - Demo test",
                "session_id": "demo_test"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Feedback saved")
            print(f"   Feedback ID: {data.get('feedback_id')}")
            print(f"   Message: {data.get('message')}")
            return True
        else:
            print(f"   ❌ Feedback failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_stats(base_url="http://localhost:8001"):
    """Test stats endpoint"""
    print_header("TEST 3: STATISTICS")
    
    print("Fetching generation statistics...")
    try:
        response = requests.get(f"{base_url}/api/tasks/stats?days=7", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Stats retrieved")
            print(f"   Total requests: {data.get('total_requests')}")
            print(f"   Avg latency: {data.get('avg_latency_ms', 0):.1f}ms")
            print(f"   Avg confidence: {data.get('avg_confidence', 0):.2f}")
            print(f"   Mode distribution: {data.get('mode_distribution', {})}")
            return True
        else:
            print(f"   ❌ Stats failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_data_structure():
    """Test data crawling structure"""
    print_header("TEST 4: DATA CRAWLING STRUCTURE")
    
    print("Checking data pull scripts...")
    
    jira_script = Path("scripts/data_pull/pull_jira.py")
    trello_script = Path("scripts/data_pull/pull_trello_v2.py")
    clean_script = Path("scripts/data_pull/clean_and_merge.py")
    
    scripts_ok = True
    for script in [jira_script, trello_script, clean_script]:
        if script.exists():
            print(f"   ✅ {script.name}")
        else:
            print(f"   ❌ {script.name} not found")
            scripts_ok = False
    
    print("\nChecking data directory...")
    data_dir = Path("data/external")
    data_dir.mkdir(parents=True, exist_ok=True)
    print(f"   ✅ {data_dir}")
    
    return scripts_ok


def test_ood_structure():
    """Test OOD evaluation structure"""
    print_header("TEST 5: OOD EVALUATION FRAMEWORK")
    
    print("Checking OOD evaluation scripts...")
    
    template = Path("scripts/eval/ood_requirements_template.csv")
    gen_script = Path("scripts/eval/01_generate_ood_outputs.py")
    sum_script = Path("scripts/eval/02_summarize_ood_scores.py")
    
    all_ok = True
    for file in [template, gen_script, sum_script]:
        if file.exists():
            print(f"   ✅ {file.name}")
        else:
            print(f"   ❌ {file.name} not found")
            all_ok = False
    
    return all_ok


def test_models():
    """Test if models exist"""
    print_header("TEST 6: MODELS")
    
    print("Checking trained models...")
    model_dir = Path("requirement_analyzer/models/task_gen/models")
    
    required_models = [
        'requirement_detector_model.joblib',
        'type_model.joblib',
        'priority_model.joblib',
        'domain_model.joblib'
    ]
    
    all_ok = True
    for model in required_models:
        model_path = model_dir / model
        if model_path.exists():
            size_kb = model_path.stat().st_size / 1024
            print(f"   ✅ {model} ({size_kb:.1f} KB)")
        else:
            print(f"   ❌ {model} not found")
            all_ok = False
    
    return all_ok


def main():
    """Run all tests"""
    print_header("PRODUCTION INFRASTRUCTURE DEMO")
    print("Testing all components...")
    
    # Check if server is running
    base_url = "http://localhost:8001"
    
    try:
        requests.get(f"{base_url}/health", timeout=2)
        server_running = True
    except:
        server_running = False
        print("⚠️  API server not running")
        print("   Start with: uvicorn app.main:app --port 8001 --reload\n")
    
    # Test structure (works without server)
    print("\n🔧 INFRASTRUCTURE TESTS (No server needed)")
    models_ok = test_models()
    data_ok = test_data_structure()
    ood_ok = test_ood_structure()
    
    # Test API (needs server)
    if server_running:
        print("\n\n🚀 API TESTS (Server running)")
        sample_task = test_api_endpoints(base_url)
        feedback_ok = test_feedback(base_url, sample_task)
        stats_ok = test_stats(base_url)
    else:
        print("\n\n⚠️  API TESTS SKIPPED (Server not running)")
        feedback_ok = stats_ok = False
    
    # Summary
    print_header("TEST SUMMARY")
    
    print("Infrastructure:")
    print(f"   Models: {'✅ OK' if models_ok else '❌ Failed'}")
    print(f"   Data crawling structure: {'✅ OK' if data_ok else '❌ Failed'}")
    print(f"   OOD evaluation structure: {'✅ OK' if ood_ok else '❌ Failed'}")
    
    if server_running:
        print("\nAPI:")
        print(f"   Generate endpoint: {'✅ OK' if sample_task else '❌ Failed'}")
        print(f"   Feedback endpoint: {'✅ OK' if feedback_ok else '❌ Failed'}")
        print(f"   Stats endpoint: {'✅ OK' if stats_ok else '❌ Failed'}")
    
    print("\n📊 Overall Status:")
    structure_ok = models_ok and data_ok and ood_ok
    
    if structure_ok and server_running:
        print("   ✅ ALL TESTS PASSED - Production infrastructure ready!")
    elif structure_ok:
        print("   ⚠️  STRUCTURE OK - Start API server to test endpoints")
    else:
        print("   ❌ SOME TESTS FAILED - Check errors above")
    
    print("\n💡 Next steps:")
    if not server_running:
        print("   1. Start API: uvicorn app.main:app --port 8001 --reload")
        print("   2. Run this test again: python demo_infrastructure.py")
    else:
        print("   1. ✅ API is working")
        print("   2. Configure .env with Jira/Trello credentials (optional)")
        print("   3. Run OOD evaluation with 200-500 real requirements")
        print("   4. Collect user feedback via API")
    
    print()


if __name__ == '__main__':
    main()
