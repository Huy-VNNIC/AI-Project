#!/usr/bin/env python3
"""
Demo thực tế cho cả tích hợp đa mô hình và Agile COCOMO
"""

import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Add parent directory to path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

# Import from relative modules
from estimation_models import COCOMOII, FunctionPoints, UseCasePoints, PlanningPoker
from multi_model_integration import MultiModelIntegration
from agile_cocomo import AgileCOCOMO

def format_result(result, title=None):
    """Format result dictionary for display"""
    if title:
        print(f"\n===== {title} =====")
    
    print(f"Effort: {result['effort_pm']:.2f} person-months")
    print(f"Time: {result['time_months']:.2f} months")
    print(f"Team Size: {result['team_size']:.2f} people")
    print(f"Confidence: {result['confidence']:.2f}")
    
    if "model" in result:
        print(f"Model: {result['model']}")
    
    if "integration_method" in result:
        print(f"Integration Method: {result['integration_method']}")
        print("\nIndividual Model Results:")
        for model_result in result.get("model_results", []):
            print(f"- {model_result['model']}: {model_result['effort_pm']:.2f} PM " +
                  f"(Confidence: {model_result['confidence']:.2f}, Suitability: {model_result.get('suitability', 0):.2f})")
    
    # Agile-specific information
    if "sprints_remaining" in result:
        print(f"\nAgile Metrics:")
        print(f"Sprints Remaining: {result['sprints_remaining']:.1f}")
        print(f"Agile Adjustment Factor: {result['agile_adjustment']:.2f}")
        
        print("\nSprint Forecast:")
        for sprint in result.get("sprint_forecast", [])[:5]:  # Show first 5 sprints
            print(f"Sprint {sprint['sprint']}: {sprint['story_points']:.1f} SP, " +
                  f"{sprint['effort_hours']:.1f} hours ({sprint['effort_pm']:.2f} PM)")
        
        if len(result.get("sprint_forecast", [])) > 5:
            print(f"... and {len(result['sprint_forecast']) - 5} more sprints")

def demo_multi_model_integration():
    """Demonstrate multi-model integration"""
    print("\n" + "="*50)
    print("DEMO: MULTI-MODEL INTEGRATION")
    print("="*50)
    
    # Create project data that has inputs for all models
    project_data = {
        # COCOMO II inputs
        "size": 25,  # KLOC
        "reliability": 1.15,  # Slightly higher than normal
        "complexity": 1.3,    # Complex project
        "reuse": 0.9,         # Some reuse
        "documentation": 1.0,  # Normal documentation
        "team_experience": 0.85,  # Experienced team
        "language_experience": 0.9,
        "tool_experience": 0.9,
        "schedule_constraint": 1.1,  # Slight schedule pressure
        
        # Function Points inputs
        "external_inputs": 30,
        "external_outputs": 25,
        "external_inquiries": 20,
        "internal_files": 8,
        "external_files": 5,
        "complexity_adjustment": 1.05,
        
        # Use Case Points inputs
        "simple_actors": 3,
        "average_actors": 2,
        "complex_actors": 1,
        "simple_use_cases": 10,
        "average_use_cases": 8,
        "complex_use_cases": 5,
        "technical_factors": {
            "distributed_system": 2,  # 0-5 scale
            "response_time": 3,
            "end_user_efficiency": 4,
            "complex_processing": 3,
            "reusable_code": 4,
            "easy_to_install": 2,
            "easy_to_use": 3,
            "portable": 4,
            "easy_to_change": 3,
            "concurrent": 3,
            "security_features": 5,
            "third_party_access": 2,
            "special_training": 1
        },
        "environmental_factors": {
            "familiar_with_process": 4,  # 0-5 scale
            "application_experience": 3,
            "object_oriented_experience": 3,
            "lead_analyst_capability": 4,
            "motivation": 5,
            "stable_requirements": 2,
            "part_time_workers": 3,
            "difficult_language": 2
        },
        "productivity_factor": 20,  # Hours per Use Case Point
        
        # Planning Poker inputs
        "user_stories": [
            {"name": "Login System", "points": 5},
            {"name": "User Profile", "points": 8},
            {"name": "Search Functionality", "points": 13},
            {"name": "Payment Processing", "points": 20},
            {"name": "Reporting", "points": 13},
            {"name": "Admin Dashboard", "points": 8},
            {"name": "Notifications", "points": 5},
            {"name": "API Integration", "points": 13}
        ],
        "velocity": 25,  # SP/sprint
        "sprint_length": 2,  # weeks
        "hours_per_point": 6,
        
        # General project info
        "methodology": "hybrid",  # Mix of agile and traditional
        "team_size": 5,
        "hourly_rate": 50  # USD
    }
    
    # Create multi-model integration
    integrator = MultiModelIntegration()
    
    # Try all integration methods
    integration_methods = ["weighted_average", "best_model", "stacking", "bayesian_average"]
    
    for method in integration_methods:
        try:
            result = integrator.estimate(project_data, method=method)
            format_result(result, f"Integration Method: {method}")
        except Exception as e:
            print(f"\nError with {method}: {str(e)}")
    
    # Return the weighted average result for comparison
    return integrator.estimate(project_data, method="weighted_average")

def demo_agile_cocomo():
    """Demonstrate Agile COCOMO model"""
    print("\n" + "="*50)
    print("DEMO: AGILE-ADAPTIVE COCOMO")
    print("="*50)
    
    # Create Agile COCOMO model
    agile_cocomo = AgileCOCOMO()
    
    # Project data for a new Agile project (no sprints completed yet)
    new_project_data = {
        "size": 300,  # Story points
        "sprint_length": 2,  # weeks
        "team_size": 5,
        "methodology": "scrum",
        "team_experience": 0.7,  # 0-1 scale, higher is more experienced
        "technical_debt": "low",
        "automation_level": "high",
        # COCOMO II factors
        "reliability": 1.1,
        "complexity": 1.2,
        "reuse": 0.9,
        "documentation": 0.9  # Less documentation in Agile
    }
    
    # Get estimate for new project
    new_result = agile_cocomo.estimate_effort(new_project_data)
    format_result(new_result, "New Agile Project (No Velocity Data)")
    
    # Project data for an ongoing Agile project
    ongoing_project_data = {
        "size": 180,  # Remaining story points
        "sprint_length": 2,  # weeks
        "team_velocity": 30,  # SP/sprint
        "completed_sprints": 4,
        "velocity_history": [25, 28, 32, 30],  # Previous velocities
        "team_size": 5,
        "methodology": "scrum",
        "team_experience": 0.7,
        "technical_debt": "low",
        "automation_level": "high",
        # COCOMO II factors
        "reliability": 1.1,
        "complexity": 1.2,
        "reuse": 0.9,
        "documentation": 0.9
    }
    
    # Get estimate for ongoing project
    ongoing_result = agile_cocomo.estimate_effort(ongoing_project_data)
    format_result(ongoing_result, "Ongoing Agile Project (With Velocity Data)")
    
    # Simulate sprint updates
    print("\n===== Sprint Updates Simulation =====")
    
    # Initial backlog
    initial_backlog = 300
    remaining_backlog = 300
    
    # Simulate 6 sprints
    for sprint in range(1, 7):
        # Simulate some variation in velocity (normal distribution around 30 SP)
        actual_velocity = max(20, min(40, np.random.normal(30, 5)))
        
        # Calculate story points completed and remaining
        points_completed = min(remaining_backlog, actual_velocity)
        remaining_backlog -= points_completed
        
        # Calculate actual effort (with some randomness)
        hours_per_point = np.random.normal(6, 1)  # 6 hours per point on average
        actual_effort = points_completed * hours_per_point
        
        # Update model with actual data
        agile_cocomo.update_with_sprint_data(
            sprint_num=sprint,
            actual_velocity=actual_velocity,
            actual_effort=actual_effort,
            remaining_backlog=remaining_backlog
        )
        
        # Re-estimate after every 2 sprints
        if sprint % 2 == 0:
            # Update project data with new information
            updated_data = ongoing_project_data.copy()
            updated_data["size"] = remaining_backlog
            updated_data["completed_sprints"] = sprint
            updated_data["team_velocity"] = sum(entry["actual_velocity"] for entry in agile_cocomo.sprint_history[-2:]) / 2
            
            # Get updated estimate
            updated_result = agile_cocomo.estimate_effort(updated_data)
            format_result(updated_result, f"Re-estimate After Sprint {sprint}")
    
    # Generate burndown chart
    try:
        fig = agile_cocomo.plot_sprint_burndown(initial_backlog)
        if fig:
            # Save to file
            chart_path = os.path.join(parent_dir, "comparison_results", "agile_burndown.png")
            os.makedirs(os.path.dirname(chart_path), exist_ok=True)
            fig.savefig(chart_path)
            print(f"\nBurndown chart saved to: {chart_path}")
    except Exception as e:
        print(f"Could not generate burndown chart: {str(e)}")
    
    return ongoing_result

def compare_approaches(multi_model_result, agile_result):
    """Compare multi-model integration with Agile COCOMO"""
    print("\n" + "="*50)
    print("COMPARISON: MULTI-MODEL VS. AGILE COCOMO")
    print("="*50)
    
    print(f"Multi-Model Integration: {multi_model_result['effort_pm']:.2f} person-months")
    print(f"Agile COCOMO: {agile_result['effort_pm']:.2f} person-months")
    
    difference = abs(multi_model_result['effort_pm'] - agile_result['effort_pm'])
    percentage = (difference / multi_model_result['effort_pm']) * 100
    
    print(f"\nDifference: {difference:.2f} person-months ({percentage:.1f}%)")
    
    print("\nInsights:")
    print("- Multi-model integration leverages strengths of various models")
    print("- Agile COCOMO adapts better to iterative development with velocity data")
    print("- Each approach has different confidence levels and assumptions")
    print("- Recommendation: Use multi-model for initial estimates, Agile COCOMO for ongoing projects")

def main():
    """Main function to run the demo"""
    print("="*50)
    print("SOFTWARE EFFORT ESTIMATION - RESEARCH DEMONSTRATION")
    print("="*50)
    
    # Run multi-model integration demo
    multi_model_result = demo_multi_model_integration()
    
    # Run Agile COCOMO demo
    agile_result = demo_agile_cocomo()
    
    # Compare approaches
    compare_approaches(multi_model_result, agile_result)
    
    print("\n" + "="*50)
    print("DEMO COMPLETED")
    print("="*50)

if __name__ == "__main__":
    main()
