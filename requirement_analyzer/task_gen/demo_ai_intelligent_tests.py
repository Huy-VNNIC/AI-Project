#!/usr/bin/env python3
"""
AI Intelligent Test Generation - Comprehensive Test & Demo
===========================================================

Demonstrates the AI-powered test case generation system.
Uses real NLP/ML analysis, NOT templates.

Sample Requirements (Healthcare Domain):
"""

import logging
import sys
import json
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)

logger = logging.getLogger("ai_test_demo")


def print_header(title, char="="):
    """Print formatted header"""
    width = 80
    print("\n" + char * width)
    print(title.center(width))
    print(char * width)


def print_section(title):
    """Print section divider"""
    print(f"\n{'─' * 80}")
    print(f"  {title}")
    print(f"{'─' * 80}")


def print_result(result: dict):
    """Pretty print generation result"""
    
    if result.get("status") == "error":
        print(f"❌ ERROR: {result.get('message')}")
        return
    
    # Header
    print_section("REQUIREMENT ANALYSIS")
    
    requirement = result.get("requirement", "")
    print(f"\nRequirement: {requirement[:100]}...")
    
    analysis = result.get("analysis", {})
    print(f"\n  📊 Entities: {len(analysis.get('entities', []))}")
    print(f"  🔗 Relationships: {len(analysis.get('relationships', []))}")
    print(f"  ⚙️  Conditions: {len(analysis.get('conditions', []))}")
    print(f"  ⚠️  Edge Cases: {len(analysis.get('edge_cases', []))}")
    print(f"  ✓ Validations: {len(analysis.get('validations', []))}")
    print(f"  🔒 Permissions: {len(analysis.get('permissions', []))}")
    print(f"  📈 Complexity: {analysis.get('complexity', 0):.2f}/1.0")
    
    # Test Scenarios
    print_section("EXTRACTED TEST SCENARIOS")
    
    scenarios = result.get("scenarios", [])
    scenario_types = {}
    for scenario in scenarios:
        stype = scenario.get("type", "unknown")
        scenario_types[stype] = scenario_types.get(stype, 0) + 1
    
    print(f"\nTotal Scenarios: {len(scenarios)}")
    print(f"By Type: {scenario_types}")
    
    for i, scenario in enumerate(scenarios[:5], 1):
        print(f"\n  {i}. {scenario.get('name', 'Scenario')}")
        print(f"     Type: {scenario.get('type', 'unknown')}")
        print(f"     Importance: {scenario.get('importance', 0):.2f}")
        print(f"     {scenario.get('description', '')[:60]}...")
    
    if len(scenarios) > 5:
        print(f"\n  ... and {len(scenarios) - 5} more scenarios")
    
    # Test Cases
    print_section("AI-GENERATED TEST CASES")
    
    test_cases = result.get("test_cases", [])
    summary = result.get("summary", {})
    
    print(f"\nTotal Test Cases: {summary.get('total_test_cases', 0)}")
    print(f"By Type: {summary.get('by_type', {})}")
    print(f"By Priority: {summary.get('by_priority', {})}")
    print(f"Average AI Confidence: {summary.get('avg_confidence', 0):.2f}")
    
    for i, tc in enumerate(test_cases[:5], 1):
        print(f"\n  [{i}] {tc.get('test_id', 'TEST')} - {tc.get('title', 'Test')}")
        print(f"      Type: {tc.get('type', 'Unit')} | Priority: {tc.get('priority', 'Medium')}")
        print(f"      Why: {tc.get('why_generated', '')[:60]}...")
        print(f"      AI Confidence: {tc.get('ai_confidence', 0):.2f}")
    
    if len(test_cases) > 5:
        print(f"\n  ... and {len(test_cases) - 5} more test cases")
    
    print()


def main():
    """Main demo function"""
    
    print_header("AI INTELLIGENT TEST CASE GENERATION - COMPREHENSIVE DEMO")
    print("\nThis system uses REAL AI to understand requirements,")
    print("NOT templates. Each test is generated based on actual requirement logic.\n")
    
    # Import handler
    try:
        from requirement_analyzer.task_gen.ai_test_handler import AITestGenerationHandler
        logger.info("✓ Successfully imported AITestGenerationHandler")
    except ImportError as e:
        print_header("IMPORT ERROR", char="!")
        print(f"\nError: {e}")
        print("\nMake sure you're in the correct directory:")
        print("  $ cd /home/dtu/AI-Project/AI-Project")
        print("\nOr install the module properly.")
        return False
    
    # Initialize
    handler = AITestGenerationHandler()
    
    # Sample requirements (healthcare domain)
    requirements = [
        {
            "id": "HEALTHCARE-001",
            "text": """
            The system must allow authorized healthcare providers to upload patient 
            medical records via CSV file. The file must be validated for format compliance 
            (required columns: name, age, diagnosis, date). Files larger than 50MB must be 
            rejected. Upon successful upload, records must be parsed and stored in the database 
            with proper encryption. The system should handle concurrent uploads gracefully.
            """,
            "ac": """
            Given: Healthcare provider has valid CSV file
            When: Provider clicks Upload button
            Then: System validates file format and size
            And: System stores encrypted records in database
            And: System displays success message with record count
            """
        },
        {
            "id": "HEALTHCARE-002",
            "text": """
            Administrators must be able to generate monthly usage reports showing:
            - Number of records processed
            - Average processing time
            - Number of active users
            - Errors encountered
            
            Reports must be generated within 30 seconds even for large datasets.
            Reports should be exportable as PDF or Excel.
            """,
            "ac": """
            Given: Admin is logged in
            When: Admin requests monthly report
            Then: System generates report within 30 seconds
            And: Report displays all required metrics
            And: Admin can export as PDF or Excel
            """
        },
        {
            "id": "HEALTHCARE-003",
            "text": """
            Role-based access control must be implemented. 
            - Doctors can view only their own patients' records
            - Nurses can view records under their department
            - Administrators can access all records
            
            Unauthorized access attempts must be logged and flagged.
            Session timeouts must occur after 30 minutes of inactivity.
            """,
            "ac": """
            Given: User has specific role assigned
            When: User attempts to access patient record
            Then: System checks user's role and permissions
            And: System grants/denies access accordingly
            And: Unauthorized attempts are logged
            """
        }
    ]
    
    all_results = []
    
    # Process each requirement
    for req in requirements:
        print_header(f"PROCESSING: {req['id']}", char="━")
        
        logger.info(f"Processing {req['id']}...")
        
        result = handler.generate_tests_for_task(
            task_id=req['id'],
            task_description=req['text'].strip(),
            acceptance_criteria=req.get('ac', '')
        )
        
        all_results.append(result)
        
        print_result(result)
    
    # Generate overall summary
    print_header("OVERALL SUMMARY", char="═")
    
    summary = handler.get_summary_report(all_results)
    
    print(f"\n  📊 Total Tasks Processed: {summary['total_tasks_processed']}")
    print(f"  🧪 Total Test Cases Generated: {summary['total_test_cases_generated']}")
    print(f"  📈 Distribution by Type: {summary['distribution_by_type']}")
    print(f"  ⭐ Distribution by Priority: {summary['distribution_by_priority']}")
    print(f"  🤖 Average AI Confidence: {summary['average_ai_confidence']:.2f}")
    print(f"  ✅ High Confidence Rate (≥0.8): {summary['high_confidence_rate']:.1%}")
    
    print("\n✓ AI Test Generation Demo Complete!\n")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
