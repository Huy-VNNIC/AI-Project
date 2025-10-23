#!/usr/bin/env python3
"""
Test script to check if the LOC model provides realistic estimates for large projects
"""

from requirement_analyzer.loc_model import LOCModel
import os
import sys

def test_loc_model_large_projects():
    """Test if LOC models provide realistic estimates for large projects"""
    print("Testing LOC models for large projects...")
    
    # Create LOC models
    linear_model = LOCModel(model_type="linear")
    rf_model = LOCModel(model_type="random_forest")
    
    # Test parameters for different project sizes
    test_sizes = [
        {'kloc': 5, 'complexity': 1.0, 'developers': 3, 'experience': 1.0, 'name': 'Small project (5K LOC)'},
        {'kloc': 20, 'complexity': 1.2, 'developers': 4, 'experience': 1.0, 'name': 'Medium project (20K LOC)'},
        {'kloc': 50, 'complexity': 1.5, 'developers': 5, 'experience': 1.0, 'name': 'Large project (50K LOC)'},
        {'kloc': 100, 'complexity': 1.8, 'developers': 8, 'experience': 1.0, 'name': 'Very large project (100K LOC)'}
    ]
    
    print("\nLOC Linear Model Results:")
    print("-" * 80)
    print(f"{'Project':<25} {'KLOC':<10} {'Complexity':<15} {'Effort (PM)':<15} {'PM/KLOC':<10}")
    print("-" * 80)
    
    for params in test_sizes:
        result = linear_model.estimate(params)
        effort = result['estimate']
        effort_per_kloc = effort / params['kloc']
        print(f"{params['name']:<25} {params['kloc']:<10.1f} {params['complexity']:<15.1f} {effort:<15.2f} {effort_per_kloc:<10.2f}")
    
    print("\nLOC Random Forest Model Results:")
    print("-" * 80)
    print(f"{'Project':<25} {'KLOC':<10} {'Complexity':<15} {'Effort (PM)':<15} {'PM/KLOC':<10}")
    print("-" * 80)
    
    for params in test_sizes:
        result = rf_model.estimate(params)
        effort = result['estimate']
        effort_per_kloc = effort / params['kloc']
        print(f"{params['name']:<25} {params['kloc']:<10.1f} {params['complexity']:<15.1f} {effort:<15.2f} {effort_per_kloc:<10.2f}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    # Add project root to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    test_loc_model_large_projects()
