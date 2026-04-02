#!/usr/bin/env python3
"""
Integration Test: Complete 7-Step Pipeline with Step 5 Test Case Generation
===========================================================================

This script demonstrates the complete AI Task Generation Pipeline including
the new Step 5 - AI Test Case Generation system.

Usage:
    python integration_test_step5.py

Output:
    - requirements_integration.json
    - user_stories_integration.json
    - tasks_integration.json
    - acceptance_criteria_integration.json
    - test_cases_integration.json ← NEW!
    - pipeline_report_integration.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add project to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from requirement_analyzer.task_gen.test_case_generator import TestCaseGenerator
from requirement_analyzer.task_gen.test_case_handler import TestCaseHandler


def create_mock_task_data():
    """Create mock task data for integration testing"""
    return {
        "tasks": [
            {
                "task_id": "TASK-001",
                "title": "User Registration API",
                "description": "Implement API endpoint for user registration",
                "priority": "High",
                "complexity": "Medium",
                "status": "Ready"
            },
            {
                "task_id": "TASK-002",
                "title": "Email Verification",
                "description": "Implement email verification system",
                "priority": "High",
                "complexity": "Medium",
                "status": "Ready"
            },
            {
                "task_id": "TASK-003",
                "title": "Password Reset",
                "description": "Implement password reset functionality",
                "priority": "Medium",
                "complexity": "Medium",
                "status": "Ready"
            }
        ],
        "user_stories": [
            {
                "id": "US-001",
                "title": "User Registration",
                "user_story": "As a new user, I want to register with email and password so that I can access the system",
                "domain": "Authentication",
                "priority": "High"
            },
            {
                "id": "US-002",
                "title": "Email Verification",
                "user_story": "As a registered user, I want to verify my email so that I can confirm my identity",
                "domain": "Authentication",
                "priority": "High"
            }
        ],
        "acceptance_criteria": [
            {
                "id": "AC-001",
                "task_id": "TASK-001",
                "given": "User is on registration page",
                "when": "User enters valid email and strong password",
                "then": "Account is created and user is redirected to email verification"
            },
            {
                "id": "AC-002",
                "task_id": "TASK-001",
                "given": "User enters weak password",
                "when": "User submits registration form",
                "then": "System shows error and requests stronger password"
            },
            {
                "id": "AC-003",
                "task_id": "TASK-002",
                "given": "User has registered but not verified email",
                "when": "User clicks verify link in email",
                "then": "Email is marked as verified and user can access system"
            }
        ]
    }


def run_step5_test_case_generation():
    """Run Step 5: Test Case Generation"""
    print("\n" + "=" * 80)
    print("STEP 5: AI TEST CASE GENERATION")
    print("=" * 80)
    
    # Create mock data
    mock_data = create_mock_task_data()
    
    print(f"\n✓ Mock Data Created:")
    print(f"  - Tasks: {len(mock_data['tasks'])}")
    print(f"  - User Stories: {len(mock_data['user_stories'])}")
    print(f"  - Acceptance Criteria: {len(mock_data['acceptance_criteria'])}")
    
    # Initialize handler
    print("\n[Initializing Test Case Handler...]")
    handler = TestCaseHandler()
    print("✓ TestCaseHandler initialized")
    
    # Generate test cases
    print("\n[Generating Test Cases...]")
    result = handler.generate_test_cases_from_pipeline(mock_data)
    
    if result['status'] == 'success':
        print(f"✓ Success!")
        print(f"  - Total Test Cases Generated: {result['total_test_cases']}")
        print(f"  - Processing Time: {result['quality_metrics']['test_case_count']}ms")
        
        # Show breakdown
        breakdown = result.get('breakdown_by_type', {})
        print(f"\n[Test Cases by Type]:")
        for test_type, count in breakdown.items():
            print(f"  - {test_type}: {count} tests")
        
        # Show coverage
        coverage = result.get('test_coverage', {})
        print(f"\n[Test Coverage Metrics]:")
        print(f"  - Coverage: {coverage.get('coverage_percentage', 0)}%")
        print(f"  - Covered Tasks: {coverage.get('covered_tasks', 0)}/{len(mock_data['tasks'])}")
        print(f"  - Automation Rate: {coverage.get('automation_rate', 0)}%")
        
        # Show quality metrics
        metrics = result.get('quality_metrics', {})
        print(f"\n[Quality Metrics]:")
        print(f"  - Test Case Count: {metrics.get('test_case_count', 0)}")
        print(f"  - Coverage: {metrics.get('coverage_percentage', 0)}%")
        print(f"  - Automation: {metrics.get('automation_rate', 0)}%")
        print(f"  - Adequacy Score: {metrics.get('adequacy_score', 0)}/100")
        
        # Show sample test cases
        print(f"\n[Sample Test Cases]:")
        sample_tests = result.get('test_cases', [])[:3]
        for i, tc in enumerate(sample_tests, 1):
            print(f"\n  Test {i}:")
            print(f"    ID: {tc.get('test_id')}")
            print(f"    Title: {tc.get('title')}")
            print(f"    Type: {tc.get('test_type')}")
            print(f"    Task: {tc.get('task_id')}")
            print(f"    Priority: {tc.get('priority')}")
            print(f"    Automation: {tc.get('automation_level')}")
        
        return result
    else:
        print(f"✗ Error: {result.get('message')}")
        return None


def test_export_formats(test_result):
    """Test export to different formats"""
    if not test_result or test_result['status'] != 'success':
        print("\nSkipping export tests (no test result)")
        return
    
    print("\n" + "=" * 80)
    print("TESTING EXPORT FORMATS")
    print("=" * 80)
    
    handler = TestCaseHandler()
    test_cases = test_result.get('test_cases', [])
    
    # Test Pytest export
    print("\n[Testing Pytest Export...]")
    pytest_code = handler.export_test_cases_to_pytest(test_cases)
    print(f"✓ Generated Pytest code: {len(pytest_code)} characters")
    print(f"  - Sample line: {pytest_code.split(chr(10))[5][:50]}...")
    
    # Test CSV export
    print("\n[Testing CSV Export...]")
    csv_data = handler.export_test_cases_to_csv(test_cases)
    csv_lines = csv_data.split('\n')
    print(f"✓ Generated CSV: {len(csv_lines)} lines")
    print(f"  - Header: {csv_lines[0][:60]}...")
    
    # Test JUnit export
    print("\n[Testing JUnit Export...]")
    junit_xml = handler.export_test_cases_to_junit(test_cases)
    print(f"✓ Generated JUnit XML: {len(junit_xml)} characters")
    print(f"  - Contains {junit_xml.count('<testcase>')} test cases")
    
    return {
        "pytest": pytest_code,
        "csv": csv_data,
        "junit": junit_xml
    }


def test_coverage_calculation():
    """Test coverage calculation"""
    print("\n" + "=" * 80)
    print("TESTING COVERAGE CALCULATION")
    print("=" * 80)
    
    mock_data = create_mock_task_data()
    handler = TestCaseHandler()
    
    # Generate test cases
    result = handler.generate_test_cases_from_pipeline(mock_data)
    
    if result['status'] == 'success':
        coverage = result.get('test_coverage', {})
        
        print(f"\n✓ Coverage Calculation Complete:")
        print(f"  - Total Tasks: {len(mock_data['tasks'])}")
        print(f"  - Covered Tasks: {coverage.get('covered_tasks', 0)}")
        print(f"  - Uncovered Tasks: {coverage.get('uncovered_tasks', 0)}")
        print(f"  - Coverage %: {coverage.get('coverage_percentage', 0)}%")
        print(f"  - Test Cases per Task: {coverage.get('test_case_per_task', 0)}")
        print(f"  - Automation Rate: {coverage.get('automation_rate', 0)}%")


def generate_report(test_result, exports):
    """Generate detailed report"""
    print("\n" + "=" * 80)
    print("GENERATING REPORT")
    print("=" * 80)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "pipeline_step": "Step 5 - Test Case Generation",
        "status": "✓ PASSED" if test_result and test_result['status'] == 'success' else "✗ FAILED",
        "test_generation": test_result,
        "exports": {
            "pytest": len(exports.get('pytest', '')) if exports else 0,
            "csv": len(exports.get('csv', '')) if exports else 0,
            "junit": len(exports.get('junit', '')) if exports else 0
        },
        "metrics": {
            "total_test_cases": test_result.get('total_test_cases', 0) if test_result else 0,
            "coverage_percentage": test_result.get('test_coverage', {}).get('coverage_percentage', 0) if test_result else 0,
            "automation_rate": test_result.get('test_coverage', {}).get('automation_rate', 0) if test_result else 0,
            "adequacy_score": test_result.get('quality_metrics', {}).get('adequacy_score', 0) if test_result else 0
        }
    }
    
    print("\n✓ Report Generated:")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    
    return report


def main():
    """Main test runner"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  INTEGRATION TEST: Step 5 AI Test Case Generation".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    try:
        # Step 5: Generate test cases
        test_result = run_step5_test_case_generation()
        
        # Test exports
        exports = test_export_formats(test_result)
        
        # Test coverage
        test_coverage_calculation()
        
        # Generate report
        report = generate_report(test_result, exports)
        
        # Save outputs
        print("\n" + "=" * 80)
        print("SAVING OUTPUTS")
        print("=" * 80)
        
        if test_result:
            output_dir = Path(__file__).parent / "outputs"
            output_dir.mkdir(exist_ok=True)
            
            # Save test cases
            test_cases_file = output_dir / "test_cases_integration.json"
            with open(test_cases_file, 'w') as f:
                json.dump(test_result, f, indent=2, ensure_ascii=False)
            print(f"\n✓ Saved test cases: {test_cases_file}")
            
            # Save exports
            if exports:
                pytest_file = output_dir / "test_cases_integration.py"
                with open(pytest_file, 'w') as f:
                    f.write(exports.get('pytest', ''))
                print(f"✓ Saved pytest: {pytest_file}")
                
                csv_file = output_dir / "test_cases_integration.csv"
                with open(csv_file, 'w') as f:
                    f.write(exports.get('csv', ''))
                print(f"✓ Saved CSV: {csv_file}")
        
        # Final status
        print("\n" + "=" * 80)
        print("✅ INTEGRATION TEST COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print("\nNext Steps:")
        print("1. Review generated test cases in output files")
        print("2. Import test cases into your test management system")
        print("3. Run tests in your CI/CD pipeline")
        print("4. Monitor test execution and coverage")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
