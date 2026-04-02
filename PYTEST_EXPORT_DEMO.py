"""
Pytest Export Generator - Demo & Usage Guide
Shows how to use the new pytest/gherkin/rtm export features
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

# ===== 1. DEMO: Pytest Export =====
def demo_pytest_export():
    """
    Export test cases as executable pytest code
    This generates a complete Python file with all test classes ready to run
    """
    print("\n" + "="*60)
    print("📝 PYTEST EXPORT DEMO")
    print("="*60)
    
    # Upload sample requirements file
    with open('sample_requirements.txt', 'rb') as f:
        files = {'file': f}
        data = {'max_tests': 8}
        response = requests.post(
            f"{BASE_URL}/api/v3/test-generation/export-pytest",
            files=files,
            data=data
        )
    
    if response.status_code == 200:
        # Save pytest file
        with open('test_hotel_booking_generated.py', 'wb') as f:
            f.write(response.content)
        print("✓ Pytest file exported: test_hotel_booking_generated.py")
        print(f"  Size: {len(response.content)} bytes")
        print("\n  To run tests:")
        print("  - pytest test_hotel_booking_generated.py -v")
        print("  - pytest test_hotel_booking_generated.py::TestREQ_HOT_001 -v")
        print("  - pytest test_hotel_booking_generated.py -m critical")
    else:
        print(f"✗ Export failed: {response.status_code}")
        print(response.text)

# ===== 2. DEMO: Gherkin Export =====
def demo_gherkin_export():
    """
    Export test cases as Gherkin/BDD feature files
    Perfect for stakeholder communication and Cucumber/Behave frameworks
    """
    print("\n" + "="*60)
    print("📋 GHERKIN/BDD EXPORT DEMO")
    print("="*60)
    
    with open('sample_requirements.txt', 'rb') as f:
        files = {'file': f}
        data = {'max_tests': 8}
        response = requests.post(
            f"{BASE_URL}/api/v3/test-generation/export-gherkin",
            files=files,
            data=data
        )
    
    if response.status_code == 200:
        with open('hotel_booking_generated.feature', 'wb') as f:
            f.write(response.content)
        print("✓ Gherkin file exported: hotel_booking_generated.feature")
        print(f"  Size: {len(response.content)} bytes")
        print("\n  To run with Cucumber:")
        print("  - cucumber hotel_booking_generated.feature")
        print("  - behave hotel_booking_generated.feature")
        
        # Preview content
        content = response.content.decode('utf-8')
        lines = content.split('\n')[:20]
        print("\n  Preview (first 20 lines):")
        for line in lines:
            print(f"  {line}")
    else:
        print(f"✗ Export failed: {response.status_code}")
        print(response.text)

# ===== 3. DEMO: RTM (Requirements Traceability Matrix) =====
def demo_rtm_export():
    """
    Export Requirements Traceability Matrix
    Shows requirement-to-test mapping for audit and compliance
    """
    print("\n" + "="*60)
    print("📊 REQUIREMENTS TRACEABILITY MATRIX (RTM) EXPORT")
    print("="*60)
    
    with open('sample_requirements.txt', 'rb') as f:
        files = {'file': f}
        data = {'max_tests': 8}
        response = requests.post(
            f"{BASE_URL}/api/v3/test-generation/export-rtm",
            files=files,
            data=data
        )
    
    if response.status_code == 200:
        with open('requirements_traceability_matrix_generated.csv', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("✓ RTM CSV file exported: requirements_traceability_matrix_generated.csv")
        print(f"  Size: {len(response.text)} bytes")
        
        # Preview content
        lines = response.text.split('\n')
        print("\n  Preview (first 5 rows):")
        for line in lines[:5]:
            print(f"  {line}")
        
        print("\n  Use in Excel/Sheets for:")
        print("  - Audit trail verification")
        print("  - Coverage analysis")
        print("  - Test case traceability")
    else:
        print(f"✗ Export failed: {response.status_code}")
        print(response.text)

# ===== 4. DEMO: Detailed JSON Export =====
def demo_json_export():
    """
    Export complete test data as JSON
    Useful for CI/CD pipeline integration and programmatic processing
    """
    print("\n" + "="*60)
    print("⚙️ JSON EXPORT DEMO")
    print("="*60)
    
    with open('sample_requirements.txt', 'rb') as f:
        files = {'file': f}
        data = {'max_tests': 8}
        response = requests.post(
            f"{BASE_URL}/api/v3/test-generation/export-json",
            files=files,
            data=data
        )
    
    if response.status_code == 200:
        with open('test_cases_detailed_generated.json', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        test_data = json.loads(response.text)
        print("✓ JSON file exported: test_cases_detailed_generated.json")
        print(f"  Size: {len(response.text)} bytes")
        print(f"  Requirements: {test_data.get('total_requirements_analyzed', 0)}")
        print(f"  Test Cases: {test_data.get('total_test_cases_generated', 0)}")
        print(f"  Average Confidence: {test_data.get('avg_nlp_confidence', 0):.1%}")
    else:
        print(f"✗ Export failed: {response.status_code}")
        print(response.text)

# ===== 5. DEMO: Get Statistics =====
def demo_statistics():
    """
    Get test generation statistics
    Useful for monitoring and planning
    """
    print("\n" + "="*60)
    print("📊 TEST STATISTICS DEMO")
    print("="*60)
    
    with open('sample_requirements.txt', 'rb') as f:
        files = {'file': f}
        data = {'max_tests': 8}
        response = requests.post(
            f"{BASE_URL}/api/v3/test-generation/get-statistics",
            files=files,
            data=data
        )
    
    if response.status_code == 200:
        stats = response.json()
        print("✓ Statistics gathered:")
        print(f"  Total Requirements: {stats['statistics']['total_requirements']}")
        print(f"  Total Test Cases: {stats['statistics']['total_test_cases']}")
        print(f"  Average Confidence: {stats['statistics']['average_confidence']:.1%}")
        print(f"\n  Test Type Distribution:")
        for test_type, count in stats['statistics']['test_type_distribution'].items():
            print(f"    - {test_type}: {count}")
        print(f"\n  Priority Distribution:")
        for priority, count in stats['statistics']['priority_distribution'].items():
            print(f"    - {priority}: {count}")
        print(f"\n  Export Formats Available: {', '.join(stats['export_formats_available'])}")
    else:
        print(f"✗ Statistics failed: {response.status_code}")
        print(response.text)

# ===== BATCH EXPORT ALL FORMATS =====
def batch_export_all_formats():
    """
    Export test cases in all available formats at once
    """
    print("\n" + "="*60)
    print("🚀 BATCH EXPORT - ALL FORMATS")
    print("="*60)
    
    formats = [
        ('pytest', 'test_hotel_booking_generated.py'),
        ('gherkin', 'hotel_booking_generated.feature'),
        ('rtm', 'requirements_traceability_matrix_generated.csv'),
        ('json', 'test_cases_detailed_generated.json')
    ]
    
    success_count = 0
    
    for format_name, filename in formats:
        try:
            print(f"\n⏳ Exporting {format_name.upper()}...", end=" ")
            
            with open('sample_requirements.txt', 'rb') as f:
                files = {'file': f}
                data = {'max_tests': 8}
                endpoint = f"{BASE_URL}/api/v3/test-generation/export-{format_name}"
                response = requests.post(endpoint, files=files, data=data)
            
            if response.status_code == 200:
                with open(filename, 'wb' if format_name != 'json' else 'w', encoding='utf-8' if format_name == 'json' else None) as f:
                    if format_name == 'json':
                        f.write(response.text)
                    else:
                        f.write(response.content)
                print(f"✓ ({len(response.content)} bytes)")
                success_count += 1
            else:
                print(f"✗ Error {response.status_code}")
        except Exception as e:
            print(f"✗ Exception: {str(e)}")
    
    print(f"\n✓ Batch export complete: {success_count}/{len(formats)} formats exported")

# ===== USAGE EXAMPLES =====
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎯 PYTEST EXPORT GENERATOR - USAGE DEMO")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API Base URL: {BASE_URL}")
    
    # Run all demos
    try:
        print("\n[1/5] Pytest Export...", end="")
        demo_pytest_export()
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
    
    try:
        print("\n[2/5] Gherkin Export...", end="")
        demo_gherkin_export()
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
    
    try:
        print("\n[3/5] RTM Export...", end="")
        demo_rtm_export()
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
    
    try:
        print("\n[4/5] JSON Export...", end="")
        demo_json_export()
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
    
    try:
        print("\n[5/5] Statistics...", end="")
        demo_statistics()
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
    
    try:
        batch_export_all_formats()
    except Exception as e:
        print(f"\n✗ Batch export error: {str(e)}")
    
    print("\n" + "="*60)
    print("✓ DEMO COMPLETE")
    print("="*60)
    
    print("\n📁 Generated Files:")
    import os
    files_to_check = [
        'test_hotel_booking_generated.py',
        'hotel_booking_generated.feature',
        'requirements_traceability_matrix_generated.csv',
        'test_cases_detailed_generated.json'
    ]
    for f in files_to_check:
        if os.path.exists(f):
            size = os.path.getsize(f)
            print(f"  ✓ {f} ({size} bytes)")
        else:
            print(f"  ✗ {f} (not generated)")
