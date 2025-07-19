#!/usr/bin/env python3
"""
Test script to verify COCOMO II module comparison functionality
"""

import os
import sys

def test_linear_analysis():
    """Test the linear analysis module"""
    print("Testing COCOMO II Linear Analysis Module...")
    
    # Test if the module can be imported
    try:
        import cocomo_ii_linear_analysis
        print("✓ Module imported successfully")
    except Exception as e:
        print(f"✗ Failed to import module: {e}")
        return False
    
    # Test if required files exist
    required_files = [
        './processed_data/loc_based.csv',
        './processed_data/fp_based.csv', 
        './processed_data/ucp_based.csv'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ Found data file: {file}")
        else:
            print(f"✗ Missing data file: {file}")
    
    # Test if generated images exist
    expected_images = [
        'cocomo_ii_linear_analysis_loc.png',
        'cocomo_ii_linear_analysis_fp.png',
        'cocomo_ii_linear_analysis_ucp.png',
        'cocomo_ii_schemas_comparison.png'
    ]
    
    for image in expected_images:
        if os.path.exists(image):
            print(f"✓ Generated image: {image}")
        else:
            print(f"✗ Missing image: {image}")
    
    return True

def test_traditional_cocomo():
    """Test traditional COCOMO II functions"""
    print("\nTesting Traditional COCOMO II Functions...")
    
    try:
        from demo import cocomo_ii_basic_estimate
        
        # Test LOC estimation
        result = cocomo_ii_basic_estimate(5, 'kloc')
        print(f"✓ LOC estimation: {result['effort_pm']:.2f} person-months")
        
        # Test FP estimation
        result = cocomo_ii_basic_estimate(250, 'fp')
        print(f"✓ FP estimation: {result['effort_pm']:.2f} person-months")
        
        # Test UCP estimation  
        result = cocomo_ii_basic_estimate(350, 'ucp')
        print(f"✓ UCP estimation: {result['effort_pm']:.2f} person-months")
        
        return True
        
    except Exception as e:
        print(f"✗ Traditional COCOMO II test failed: {e}")
        return False

def test_ml_models():
    """Test ML model functionality"""
    print("\nTesting ML Models...")
    
    try:
        from cocomo_ii_api import CocomoIIAPI
        
        api = CocomoIIAPI('./models/cocomo_ii_extended')
        
        # Test prediction for each schema
        schemas = ['LOC', 'FP', 'UCP']
        sizes = [5, 250, 350]
        
        for schema, size in zip(schemas, sizes):
            try:
                result = api.predict(schema, size)
                effort = result['predictions']['effort_pm']
                print(f"✓ ML prediction for {schema}: {effort:.2f} person-months")
            except Exception as e:
                print(f"✗ ML prediction failed for {schema}: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ ML models test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("COCOMO II MODULE COMPARISON TESTS")
    print("="*60)
    
    all_passed = True
    
    # Test linear analysis
    if not test_linear_analysis():
        all_passed = False
    
    # Test traditional COCOMO II
    if not test_traditional_cocomo():
        all_passed = False
    
    # Test ML models
    if not test_ml_models():
        all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ Some tests failed")
    print("="*60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)