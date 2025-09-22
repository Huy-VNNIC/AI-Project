#!/usr/bin/env python3
"""
Test script to interact with the effort estimation API
"""

import requests
import json
import sys

def test_api_health():
    """Test the API health endpoint"""
    try:
        response = requests.get('http://localhost:5000/api/health')
        print("Health check response:", response.status_code)
        print(response.json())
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing health endpoint: {e}")
        return False

def test_estimate_effort():
    """Test the effort estimation endpoint"""
    try:
        # Sample requirements text
        requirements = """
        The system shall provide a web-based interface for user authentication.
        Users must be able to register, login, and reset their passwords.
        The system shall store user data securely using encryption.
        The system shall support role-based access control with at least 3 roles.
        Users shall be able to update their profile information.
        The system shall provide a dashboard with project statistics.
        The system shall allow users to create and manage projects.
        Each project shall have tasks that can be assigned to team members.
        The system shall provide real-time notifications for task assignments.
        The system shall generate reports on project progress and team performance.
        """
        
        # Make the API request
        response = requests.post(
            'http://localhost:5000/api/estimate',
            json={'requirements': requirements, 'method': 'auto', 'unit': 'person_months'}
        )
        
        print("Effort estimation response:", response.status_code)
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing estimation endpoint: {e}")
        return False

def test_team_suggestion():
    """Test the team suggestion endpoint"""
    try:
        # Sample requirements text
        requirements = """
        The system shall provide a web-based interface for user authentication.
        The system shall implement a RESTful API for data access.
        The frontend shall be built using React with TypeScript.
        The backend shall be implemented using Django REST Framework.
        The system shall use PostgreSQL for data storage.
        The system shall support deployment via Docker containers.
        The system shall implement automated testing with 80% code coverage.
        """
        
        # Make the API request
        response = requests.post(
            'http://localhost:5000/api/team',
            json={'requirements': requirements}
        )
        
        print("Team suggestion response:", response.status_code)
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing team suggestion endpoint: {e}")
        return False

def main():
    print("=== Testing Effort Estimation API ===")
    
    # Test health endpoint
    if not test_api_health():
        print("Health check failed. Make sure the API server is running.")
        sys.exit(1)
    
    # Test effort estimation
    test_estimate_effort()
    
    # Test team suggestion
    test_team_suggestion()
    
    print("\nAPI tests completed!")

if __name__ == "__main__":
    main()
