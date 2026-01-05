#!/usr/bin/env python3
"""
Simple demo script to test the effort estimation functionality
"""

import os
import sys
import json

# Add the project directory to the path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    from requirement_analyzer.ml_requirement_analyzer import MLRequirementAnalyzer
    from requirement_analyzer.model_integration import ModelSelector
    print("Successfully imported required modules")
except Exception as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def test_requirement_analyzer():
    """Test the requirement analyzer component"""
    print("\n--- Testing ML Requirement Analyzer ---")
    try:
        analyzer = MLRequirementAnalyzer()
        print("MLRequirementAnalyzer initialized successfully")
        
        # Test with a simple requirement
        simple_req = """
        The system shall provide user authentication functionality including login and registration.
        Users should be able to reset their passwords via email.
        The system must support role-based access control with at least three roles: admin, manager, and regular user.
        """
        
        analysis = analyzer.analyze_requirements_document(simple_req)
        print(f"Analysis completed. Found {len(analysis['requirements'])} requirements")
        
        # Display extracted features
        print("\nExtracted features:")
        for feature, value in analysis['ml_features'].items():
            print(f"  {feature}: {value}")
            
        return True
    except Exception as e:
        print(f"Error in requirement analyzer test: {e}")
        return False

def main():
    print("=== Software Effort Estimation System Demo ===")
    
    # Test requirement analyzer
    if not test_requirement_analyzer():
        print("Requirement analyzer test failed")
        return
        
    print("\nDemo completed successfully!")

if __name__ == "__main__":
    main()
