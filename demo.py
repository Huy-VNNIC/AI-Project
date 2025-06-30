#!/usr/bin/env python3
"""
COCOMO II Simple Demo

This script demonstrates how to use the COCOMO II model for software project estimation.
Since we don't have the trained models yet, this script will use the traditional COCOMO II
formulas to provide estimations.
"""

import os
import sys
import math

def cocomo_ii_basic_estimate(size, size_type='kloc'):
    """
    Basic COCOMO II estimate using the Post-Architecture model with default values.
    This is a simplified version until our machine learning models are trained.
    
    Args:
        size: The size of the project (KLOC, FP, or UCP)
        size_type: The type of size measure ('kloc', 'fp', or 'ucp')
        
    Returns:
        Dictionary with estimation results
    """
    # Convert FP and UCP to KLOC if needed
    if size_type == 'fp':
        # A rough conversion factor, usually between 100-130 LOC per function point
        size_in_kloc = size * 0.12  # Assuming 120 LOC per FP, divided by 1000 for KLOC
    elif size_type == 'ucp':
        # A rough conversion factor, usually between 15-30 LOC per UCP
        size_in_kloc = size * 0.02  # Assuming 20 LOC per UCP, divided by 1000 for KLOC
    else:
        size_in_kloc = size
    
    # Constants for the Post-Architecture model with default values
    A = 2.94  # Multiplicative constant
    B = 0.91  # Scale factor exponent
    
    # Calculate effort in person-months
    effort_pm = A * (size_in_kloc ** B)
    
    # Calculate development time in months (TDEV = C * (PM)^D)
    time_months = 3.67 * (effort_pm ** 0.28)
    
    # Calculate average number of personnel required
    developers = math.ceil(effort_pm / time_months)
    
    return {
        'size_type': size_type,
        'input_size': size,
        'size_in_kloc': size_in_kloc,
        'effort_pm': effort_pm,
        'time_months': time_months,
        'developers': developers
    }

def display_results(results):
    """
    Display the estimation results in a formatted way
    
    Args:
        results: Dictionary with estimation results
    """
    print("\n===== COCOMO II Estimation Results =====")
    print(f"Input: {results['input_size']} {results['size_type'].upper()}")
    print(f"Converted to: {results['size_in_kloc']:.2f} KLOC")
    print("\nEstimation Results:")
    print(f"  - Effort: {results['effort_pm']:.2f} person-months")
    print(f"  - Duration: {results['time_months']:.2f} months")
    print(f"  - Team Size: {results['developers']} developers")
    
    # Calculate cost (assuming $5000 per person-month)
    rate_per_month = 5000
    cost = results['effort_pm'] * rate_per_month
    print(f"\nEstimated Cost (at ${rate_per_month}/person-month): ${cost:.2f}")

def main():
    """
    Main function to demonstrate COCOMO II functionality
    """
    print("\n" + "="*50)
    print("COCOMO II Simple Estimation Demo")
    print("="*50)
    print("Note: This is using simplified formulas until ML models are trained")
    
    # Demo examples
    print("\nExample 1: Small Web Application")
    print("-" * 30)
    print("Input: 5 KLOC (5,000 lines of code)")
    results = cocomo_ii_basic_estimate(5, 'kloc')
    display_results(results)
    
    print("\nExample 2: Medium Business Application")
    print("-" * 30)
    print("Input: 250 Function Points")
    results = cocomo_ii_basic_estimate(250, 'fp')
    display_results(results)
    
    print("\nExample 3: Large Enterprise System")
    print("-" * 30)
    print("Input: 350 Use Case Points")
    results = cocomo_ii_basic_estimate(350, 'ucp')
    display_results(results)
    
    print("\nExample 4: Complex Real-time System")
    print("-" * 30)
    print("Input: 25 KLOC (25,000 lines of code)")
    results = cocomo_ii_basic_estimate(25, 'kloc')
    display_results(results)
    
    print("\nNote: This is using traditional COCOMO II formulas.")
    print("When trained ML models are available, they will provide more accurate estimates.")
    print("\n" + "="*50)
    
    # Interactive mode
    try:
        choice = input("\nWould you like to try your own estimation? (y/n): ").lower()
        if choice == 'y' or choice == 'yes':
            print("\nSelect size metric:")
            print("1. KLOC (Kilo Lines of Code)")
            print("2. FP (Function Points)")
            print("3. UCP (Use Case Points)")
            
            choice = input("Enter your choice (1-3): ")
            size_types = {
                '1': 'kloc',
                '2': 'fp',
                '3': 'ucp'
            }
            
            size_type = size_types.get(choice, 'kloc')
            size = float(input(f"\nEnter project size ({size_type.upper()}): "))
            
            results = cocomo_ii_basic_estimate(size, size_type)
            display_results(results)
    except ValueError:
        print("Error: Please enter a valid number for the size.")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
    print("For interactive mode, run: python cocomo_ii_predictor.py")
    print("="*50)

if __name__ == "__main__":
    main()
