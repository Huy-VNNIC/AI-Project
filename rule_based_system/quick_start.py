"""
Quick start script for Rule-Based Test Case Generator.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from rule_based_system.core.pipeline import run_pipeline_from_text
from rule_based_system.exports.export_handler import export_all_formats


def quick_start():
    """Quick demonstration of the system."""
    
    print("\n" + "="*70)
    print("🚀 RULE-BASED TEST CASE GENERATOR - QUICK START")
    print("="*70 + "\n")
    
    # Sample requirements
    sample_requirements = """
    System Requirements:
    
    1. User can login with email and password
    2. System must validate email format
    3. If login fails, display error message
    4. Admin can create new product listing
    5. System must check inventory before confirming order
    6. When checkout is complete, send confirmation email
    7. Password must be encrypted before storing
    """
    
    print("📝 Input Requirements:")
    print(sample_requirements)
    print("\n" + "="*70)
    print("Processing...")
    print("="*70 + "\n")
    
    # Run pipeline
    result = run_pipeline_from_text(sample_requirements, force_format="free_text")
    
    # Display summary
    summary = result["summary"]
    print(f"✅ Processing Complete!\n")
    print(f"📊 Summary:")
    print(f"  - Format Detected: {result['format_detected']}")
    print(f"  - Total Requirements: {summary['total_requirements']}")
    print(f"  - Total Test Cases: {summary['total_test_cases']}")
    print(f"  - Avg Tests per Requirement: {summary['avg_tests_per_req']}")
    print(f"\n📋 Test Cases by Type:")
    for test_type, count in summary['test_cases_by_type'].items():
        print(f"  - {test_type.capitalize()}: {count}")
    
    # Show first 3 test cases
    print("\n📚 First 3 Test Cases:")
    for i, tc in enumerate(result["test_cases"][:3], 1):
        print(f"\n  {i}. {tc['title']}")
        print(f"     Type: {tc['test_type']} | Priority: {tc['priority']}")
        print(f"     Expected: {tc['expected_result'][:60]}...")
    
    # Export to file
    print("\n" + "="*70)
    print("💾 Exporting to files...")
    print("="*70)
    
    test_cases = result["_objects"]["test_cases"]
    output_dir = os.path.join(os.path.dirname(__file__), "sample_output")
    base_path = os.path.join(output_dir, "test_cases")
    
    # Create directory if needed
    os.makedirs(output_dir, exist_ok=True)
    
    # Export all formats
    export_all_formats(test_cases, base_path)
    
    print(f"✅ Files exported to: {output_dir}")
    print(f"  - test_cases.json")
    print(f"  - test_cases.csv")
    print(f"  - test_cases.xlsx")
    print(f"  - test_cases.md")
    
    print("\n" + "="*70)
    print("✨ Quick Start Complete!")
    print("="*70)
    print("\nNext steps:")
    print("  1. Check generated files in sample_output/")
    print("  2. Run: python main.py (to start API server)")
    print("  3. Open: http://localhost:8001/docs")


if __name__ == "__main__":
    quick_start()
