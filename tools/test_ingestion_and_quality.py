#!/usr/bin/env python3
"""
Test script for task generation quality improvements and file ingestion
"""
import requests
import json
from pathlib import Path

API_BASE = "http://localhost:8000"

def test_quality_improvements():
    """Test core quality improvements (pre-filter, helper verbs, etc.)"""
    print("\n" + "="*70)
    print("TEST 1: Quality Improvements (Single Text Input)")
    print("="*70)
    
    test_cases = [
        {
            "name": "Helper verb + auth (should fix 'allow' → 'login')",
            "text": "Users must be allowed to log in with email and password",
            "expected_action": "login",
            "expected_domain": "general"
        },
        {
            "name": "Object + format extraction",
            "text": "System must export audit logs to CSV format",
            "expected_in_title": "audit logs",
            "expected_format": "CSV"
        },
        {
            "name": "Meeting note (should be filtered out)",
            "text": "We discussed authentication requirements in last meeting",
            "should_generate": False
        },
        {
            "name": "Heading-like (should be filtered out)",
            "text": "Authentication Module",
            "should_generate": False
        },
        {
            "name": "Security keyword override",
            "text": "Users must reset password via email verification",
            "expected_type": "security",
            "expected_domain": "general"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test['name']} ---")
        print(f"Input: '{test['text']}'")
        
        try:
            response = requests.post(
                f"{API_BASE}/api/task-generation/generate",
                json={
                    "text": test['text'],
                    "max_tasks": 5,
                    "requirement_threshold": 0.3
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                tasks = data.get('tasks', [])
                
                if test.get('should_generate') is False:
                    if len(tasks) == 0:
                        print(f"✅ PASS: Correctly filtered out (no tasks generated)")
                    else:
                        print(f"❌ FAIL: Should have been filtered, but generated {len(tasks)} tasks")
                        print(f"   Generated: {tasks[0].get('title', 'N/A')}")
                else:
                    if len(tasks) > 0:
                        task = tasks[0]
                        title = task.get('title', '')
                        task_type = task.get('type', '')
                        domain = task.get('domain', '')
                        
                        print(f"✅ Generated: {title}")
                        print(f"   Type: {task_type}, Domain: {domain}")
                        
                        # Check expectations
                        passed = True
                        if 'expected_action' in test:
                            action_in_title = test['expected_action'].lower() in title.lower()
                            if action_in_title:
                                print(f"   ✅ Action '{test['expected_action']}' found in title")
                            else:
                                print(f"   ❌ Action '{test['expected_action']}' NOT in title")
                                passed = False
                        
                        if 'expected_in_title' in test:
                            obj_in_title = test['expected_in_title'].lower() in title.lower()
                            if obj_in_title:
                                print(f"   ✅ Object '{test['expected_in_title']}' found in title")
                            else:
                                print(f"   ❌ Object '{test['expected_in_title']}' NOT in title")
                                passed = False
                        
                        if 'expected_type' in test:
                            if task_type == test['expected_type']:
                                print(f"   ✅ Type matches: {task_type}")
                            else:
                                print(f"   ❌ Type mismatch: got '{task_type}', expected '{test['expected_type']}'")
                                passed = False
                        
                        if 'expected_domain' in test:
                            if domain == test['expected_domain']:
                                print(f"   ✅ Domain matches: {domain}")
                            else:
                                print(f"   ❌ Domain mismatch: got '{domain}', expected '{test['expected_domain']}'")
                                passed = False
                        
                        if passed:
                            print(f"   ✅ PASS: All checks passed")
                        else:
                            print(f"   ⚠️  PARTIAL: Some checks failed")
                    else:
                        print(f"❌ FAIL: No tasks generated (expected at least 1)")
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"   {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")


def test_file_ingestion():
    """Test file ingestion endpoint"""
    print("\n" + "="*70)
    print("TEST 2: File Ingestion Pipeline")
    print("="*70)
    
    # Create test file
    test_file_path = Path("/tmp/test_requirements.txt")
    test_content = """User Authentication Requirements

Users must log in with email and password to access the system.
The system must allow users to reset their password via email verification.
System must export audit logs to CSV format for compliance reporting.

Meeting Notes (Jan 26, 2026)
We discussed the authentication module in yesterday's meeting.
The team agreed to use OAuth 2.0 for third-party integrations.

Additional Requirements:
- Users must enable two-factor authentication for enhanced security
- Admin users must be able to view login history in real-time dashboard
"""
    
    test_file_path.write_text(test_content, encoding='utf-8')
    
    print(f"\nCreated test file: {test_file_path}")
    print(f"Content ({len(test_content)} chars):\n{test_content[:200]}...\n")
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_requirements.txt', f, 'text/plain')}
            data = {
                'max_tasks': '200',
                'requirement_threshold': '0.3'
            }
            
            print("Sending file to API...")
            response = requests.post(
                f"{API_BASE}/api/task-generation/generate-from-file",
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ API Response Success")
            print(f"   Source File: {result.get('source_file', 'N/A')}")
            
            # Check ingestion metadata
            ingestion = result.get('ingestion', {})
            print(f"\n📊 Ingestion Metadata:")
            print(f"   Total Characters: {ingestion.get('total_chars', 0)}")
            print(f"   Requirements Extracted: {ingestion.get('requirements_extracted', 0)}")
            print(f"   Threshold: {ingestion.get('threshold', 0)}")
            
            # Check tasks
            tasks = result.get('tasks', [])
            total_tasks = result.get('total_tasks', 0)
            print(f"\n📋 Generated Tasks: {total_tasks}")
            
            if total_tasks > 0:
                print("\n   Top tasks:")
                for i, task in enumerate(tasks[:5], 1):
                    print(f"   {i}. {task.get('title', 'N/A')}")
                    print(f"      Type: {task.get('type', 'N/A')}, Domain: {task.get('domain', 'N/A')}")
                
                # Check if meeting notes were filtered
                meeting_note_titles = [t for t in tasks if 'discussed' in t.get('title', '').lower() or 'meeting' in t.get('title', '').lower()]
                if len(meeting_note_titles) == 0:
                    print(f"\n   ✅ Meeting notes correctly filtered out")
                else:
                    print(f"\n   ❌ WARNING: {len(meeting_note_titles)} meeting note(s) not filtered")
                
                # Check for auth-related tasks
                auth_tasks = [t for t in tasks if any(kw in t.get('title', '').lower() for kw in ['login', 'password', 'authentication', 'oauth', '2fa'])]
                print(f"\n   Auth-related tasks: {len(auth_tasks)}")
                for task in auth_tasks:
                    domain = task.get('domain', 'N/A')
                    task_type = task.get('type', 'N/A')
                    if domain in ['general', 'security']:
                        print(f"      ✅ {task.get('title')} → domain={domain}, type={task_type}")
                    else:
                        print(f"      ⚠️  {task.get('title')} → domain={domain} (expected: general/security)")
            else:
                print("   ⚠️  No tasks generated")
            
            print(f"\n✅ File ingestion test completed")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"   {response.text}")
    
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        if test_file_path.exists():
            test_file_path.unlink()
            print(f"\nCleaned up test file")


def main():
    print("\n" + "="*70)
    print("TASK GENERATION QUALITY & INGESTION TEST SUITE")
    print("="*70)
    print("\nChecking API availability...")
    
    try:
        response = requests.get(f"{API_BASE}/", timeout=5)
        if response.status_code == 200:
            print("✅ API is running")
        else:
            print(f"⚠️  API returned status {response.status_code}")
    except Exception as e:
        print(f"❌ API not reachable: {e}")
        print("\nPlease start the API first:")
        print("  cd /home/dtu/AI-Project/AI-Project")
        print("  source /home/dtu/AI-Project/.venv/bin/activate")
        print("  python -m requirement_analyzer.api")
        return
    
    # Run tests
    test_quality_improvements()
    test_file_ingestion()
    
    print("\n" + "="*70)
    print("TEST SUITE COMPLETED")
    print("="*70)


if __name__ == "__main__":
    main()
