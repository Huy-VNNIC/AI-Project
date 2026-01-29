"""
Test script to verify document upload functionality for different file formats
"""

import requests
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Test files
test_files = [
    "test_requirements.txt",
    "test_requirements.md"
]

def test_upload_endpoint():
    """Test the document upload endpoint with different file formats"""
    
    base_url = "http://localhost:8080"
    endpoint = f"{base_url}/upload-requirements"
    
    print("\n===== Testing Document Upload Functionality =====\n")
    
    for test_file in test_files:
        file_path = project_root / test_file
        
        if not file_path.exists():
            print(f"[SKIP] File {test_file} does not exist")
            continue
            
        print(f"Testing file: {test_file}")
        
        # Prepare the form data
        files = {
            'file': (test_file, open(file_path, 'rb'), 'text/plain')
        }
        data = {
            'method': 'weighted_average'
        }
        
        try:
            # Make the request
            response = requests.post(endpoint, files=files, data=data)
            
            # Check response
            if response.status_code == 200:
                result = response.json()
                
                # Check for key fields in the response
                if 'estimation' in result and 'analysis' in result:
                    print(f"[SUCCESS] File format {test_file} works correctly")
                    print(f"  - Total Effort: {result['estimation'].get('total_effort')} person-months")
                    print(f"  - Confidence: {result['estimation'].get('confidence_level')}")
                    print(f"  - Text Length: {result['document'].get('text_length')} characters")
                else:
                    print(f"[WARNING] Response is missing key fields")
            else:
                print(f"[FAIL] Request failed with status {response.status_code}")
                print(f"  - Error: {response.text}")
                
        except Exception as e:
            print(f"[ERROR] An error occurred: {str(e)}")
        
        print("-------------------------------------------")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_upload_endpoint()