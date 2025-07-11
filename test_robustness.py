"""
Script to test and enhance robustness of feature extraction for minimal or ambiguous input
"""

import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.append(str(PROJECT_ROOT))

from requirement_analyzer.analyzer import RequirementAnalyzer
from requirement_analyzer.estimator import EffortEstimator

def test_minimal_input():
    """Test with very minimal input"""
    print("\n=== Testing with minimal input ===")
    
    minimal_inputs = [
        "Build a website",
        "Create a mobile app",
        "Develop a backend API",
        "Design a database system",
        "Make a simple game",
    ]
    
    analyzer = RequirementAnalyzer()
    estimator = EffortEstimator()
    
    for input_text in minimal_inputs:
        print(f"\nInput: '{input_text}'")
        try:
            params = analyzer.analyze_requirements_document(input_text)
            print(f"Extracted size: {params['ml_features']['size']} KLOC")
            
            result = estimator.integrated_estimate(params)
            print(f"Estimated effort: {result['total_effort']:.2f} person-months")
            print(f"Confidence level: {result['confidence_level']}")
        except Exception as e:
            print(f"Error: {e}")

def test_ambiguous_input():
    """Test with ambiguous input"""
    print("\n=== Testing with ambiguous input ===")
    
    ambiguous_inputs = [
        "We need something for customer management",
        "The system should be fast and reliable",
        "Users should be able to do things",
        "Maybe an app or website, not sure yet",
        "It needs to work well on all devices",
    ]
    
    analyzer = RequirementAnalyzer()
    estimator = EffortEstimator()
    
    for input_text in ambiguous_inputs:
        print(f"\nInput: '{input_text}'")
        try:
            params = analyzer.analyze_requirements_document(input_text)
            print(f"Extracted size: {params['ml_features']['size']} KLOC")
            
            result = estimator.integrated_estimate(params)
            print(f"Estimated effort: {result['total_effort']:.2f} person-months")
            print(f"Confidence level: {result['confidence_level']}")
        except Exception as e:
            print(f"Error: {e}")

def test_vietnamese_input():
    """Test with Vietnamese input"""
    print("\n=== Testing with Vietnamese input ===")
    
    vietnamese_inputs = [
        "Xây dựng một trang web thương mại điện tử",
        "Phát triển ứng dụng di động với xác thực người dùng",
        "Hệ thống cần có tính bảo mật cao và hiệu suất tốt",
        "Dự án sẽ có 5 lập trình viên với kinh nghiệm cao",
        "Thiết kế cơ sở dữ liệu cho hệ thống quản lý khách hàng",
    ]
    
    analyzer = RequirementAnalyzer()
    estimator = EffortEstimator()
    
    for input_text in vietnamese_inputs:
        print(f"\nInput: '{input_text}'")
        try:
            params = analyzer.analyze_requirements_document(input_text)
            print(f"Extracted size: {params['ml_features']['size']} KLOC")
            
            result = estimator.integrated_estimate(params)
            print(f"Estimated effort: {result['total_effort']:.2f} person-months")
            print(f"Confidence level: {result['confidence_level']}")
        except Exception as e:
            print(f"Error: {e}")

def test_complex_input():
    """Test with complex input with explicit and implicit parameters"""
    print("\n=== Testing with complex input ===")
    
    complex_inputs = [
        """
        Develop an enterprise resource planning system with modules for:
        - Human resources management
        - Financial accounting
        - Inventory management
        - Customer relationship management
        - Supply chain management
        The system will be used by 500+ users and should handle high volumes of transactions.
        We need strong security and performance. Development team has 15 engineers.
        """,
        
        """
        Create a mobile app for both iOS and Android with following features:
        - Realtime geolocation tracking
        - Push notifications
        - Offline mode with data synchronization
        - Secure payment processing
        - Social media integration
        - User-generated content management
        The app will be used by thousands of users daily. Timeline is tight: only 6 months.
        """,
    ]
    
    analyzer = RequirementAnalyzer()
    estimator = EffortEstimator()
    
    for input_text in complex_inputs:
        print(f"\nInput: '{input_text[:100]}...'")
        try:
            params = analyzer.analyze_requirements_document(input_text)
            print(f"Extracted size: {params['ml_features']['size']} KLOC")
            print(f"Extracted developers: {params['ml_features']['developers']}")
            print(f"Extracted time: {params['ml_features']['time_months']} months")
            
            result = estimator.integrated_estimate(params)
            print(f"Estimated effort: {result['total_effort']:.2f} person-months")
            print(f"Duration: {result['duration']:.2f} months")
            print(f"Team size: {result['team_size']:.2f} people")
            print(f"Confidence level: {result['confidence_level']}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_minimal_input()
    test_ambiguous_input()
    test_vietnamese_input()
    test_complex_input()
