#!/usr/bin/env python3
"""
Tests for Multi-Model Integration and Agile-Adaptive COCOMO
"""

import unittest
import os
import sys
from pathlib import Path

# Import modules to test
from multi_model_integration.estimation_models import COCOMOII, FunctionPoints, UseCasePoints, PlanningPoker
from multi_model_integration.multi_model_integration import MultiModelIntegration
from multi_model_integration.agile_cocomo import AgileCOCOMO

class TestMultiModelIntegration(unittest.TestCase):
    """Test cases for Multi-Model Integration"""
    
    def setUp(self):
        """Set up test data"""
        self.project_data = {
            # Basic project data
            "size": 10,  # KLOC
            "reliability": 1.1,
            "complexity": 1.2,
            "reuse": 0.9,
            "documentation": 1.0,
            "team_experience": 0.8,
            
            # Function Points data
            "external_inputs": 20,
            "external_outputs": 15,
            "external_inquiries": 10,
            "internal_files": 5,
            "external_files": 3,
            "complexity_adjustment": 1.0,
            
            # Use Case Points data
            "simple_actors": 2,
            "average_actors": 1,
            "complex_actors": 1,
            "simple_use_cases": 5,
            "average_use_cases": 4,
            "complex_use_cases": 3,
            "technical_factors": {
                "distributed_system": 2,
                "response_time": 3,
                "end_user_efficiency": 3
            },
            "environmental_factors": {
                "familiar_with_process": 3,
                "application_experience": 3,
                "lead_analyst_capability": 4
            },
            "productivity_factor": 20,
            
            # Planning Poker data
            "user_stories": [
                {"name": "Login", "points": 3},
                {"name": "Dashboard", "points": 5},
                {"name": "Reports", "points": 8}
            ],
            "velocity": 20,
            "sprint_length": 2,
            "hours_per_point": 6,
            
            # General project info
            "methodology": "hybrid",
            "team_size": 4
        }
        
        # Create integrator
        self.integrator = MultiModelIntegration()
        
        # Create Agile COCOMO
        self.agile_cocomo = AgileCOCOMO()
    
    def test_cocomo_ii(self):
        """Test COCOMO II model"""
        model = COCOMOII()
        result = model.estimate_effort(self.project_data)
        
        # Basic validation
        self.assertIn("effort_pm", result)
        self.assertIn("time_months", result)
        self.assertIn("team_size", result)
        self.assertGreater(result["effort_pm"], 0)
        self.assertEqual(result["model"], "COCOMO II")
    
    def test_function_points(self):
        """Test Function Points model"""
        model = FunctionPoints()
        result = model.estimate_effort(self.project_data)
        
        # Basic validation
        self.assertIn("effort_pm", result)
        self.assertGreater(result["effort_pm"], 0)
        self.assertEqual(result["model"], "Function Points")
    
    def test_use_case_points(self):
        """Test Use Case Points model"""
        model = UseCasePoints()
        result = model.estimate_effort(self.project_data)
        
        # Basic validation
        self.assertIn("effort_pm", result)
        self.assertGreater(result["effort_pm"], 0)
        self.assertEqual(result["model"], "Use Case Points")
    
    def test_planning_poker(self):
        """Test Planning Poker model"""
        model = PlanningPoker()
        result = model.estimate_effort(self.project_data)
        
        # Basic validation
        self.assertIn("effort_pm", result)
        self.assertGreater(result["effort_pm"], 0)
        self.assertEqual(result["model"], "Planning Poker")
    
    def test_multi_model_integration(self):
        """Test multi-model integration"""
        for method in ["weighted_average", "best_model", "bayesian_average"]:
            result = self.integrator.estimate(self.project_data, method=method)
            
            # Basic validation
            self.assertIn("effort_pm", result)
            self.assertIn("time_months", result)
            self.assertIn("team_size", result)
            self.assertIn("confidence", result)
            self.assertIn("integration_method", result)
            self.assertIn("model_results", result)
            self.assertGreater(result["effort_pm"], 0)
            self.assertEqual(result["integration_method"], method)
            
            # At least one model result
            self.assertGreater(len(result["model_results"]), 0)
    
    def test_agile_cocomo(self):
        """Test Agile-Adaptive COCOMO"""
        # Add Agile-specific data
        agile_data = self.project_data.copy()
        agile_data.update({
            "size": 100,  # Story points
            "sprint_length": 2,
            "team_velocity": 25,
            "completed_sprints": 2,
            "methodology": "scrum",
            "technical_debt": "low",
            "automation_level": "high"
        })
        
        result = self.agile_cocomo.estimate_effort(agile_data)
        
        # Basic validation
        self.assertIn("effort_pm", result)
        self.assertIn("time_months", result)
        self.assertIn("team_size", result)
        self.assertIn("confidence", result)
        self.assertIn("sprint_forecast", result)
        self.assertIn("sprints_remaining", result)
        self.assertIn("agile_adjustment", result)
        self.assertGreater(result["effort_pm"], 0)
        self.assertEqual(result["model"], "Agile COCOMO")
        
        # Sprint forecast validation
        self.assertGreater(len(result["sprint_forecast"]), 0)
        for sprint in result["sprint_forecast"]:
            self.assertIn("sprint", sprint)
            self.assertIn("story_points", sprint)
            self.assertIn("effort_hours", sprint)
            self.assertIn("effort_pm", sprint)
    
    def test_agile_cocomo_sprint_updates(self):
        """Test Agile-Adaptive COCOMO sprint updates"""
        # Add sprint data
        self.agile_cocomo.update_with_sprint_data(
            sprint_num=1,
            actual_velocity=26,
            actual_effort=156,
            remaining_backlog=74
        )
        
        self.agile_cocomo.update_with_sprint_data(
            sprint_num=2,
            actual_velocity=28,
            actual_effort=168,
            remaining_backlog=46
        )
        
        # Verify sprint history
        self.assertEqual(len(self.agile_cocomo.sprint_history), 2)
        self.assertEqual(self.agile_cocomo.sprint_history[0]["sprint"], 1)
        self.assertEqual(self.agile_cocomo.sprint_history[1]["sprint"], 2)

if __name__ == "__main__":
    unittest.main()
