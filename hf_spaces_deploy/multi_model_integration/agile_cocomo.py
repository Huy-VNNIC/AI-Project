#!/usr/bin/env python3
"""
Agile-Adaptive COCOMO II Model - A COCOMO variant that adapts to Agile development
processes and incorporates sprint velocity and Agile metrics.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
try:
    # When imported as a package
    from .estimation_models import EstimationModel, COCOMOII
except ImportError:
    # When run directly
    from estimation_models import EstimationModel, COCOMOII

class AgileCOCOMO(EstimationModel):
    """
    Agile-Adaptive COCOMO II Model
    
    This model extends COCOMO II by incorporating Agile development practices:
    - Uses sprint velocity for effort calibration
    - Adapts estimates based on completed sprints
    - Provides sprint-by-sprint effort predictions
    - Incorporates Agile-specific scaling factors
    """
    
    def __init__(self, base_cocomo_model=None):
        """
        Initialize the Agile COCOMO model
        
        Args:
            base_cocomo_model (COCOMOII, optional): Base COCOMO II model
        """
        self._model_name = "Agile COCOMO"
        self._input_features = [
            "size",                    # Kích thước (story points hoặc KLOC)
            "sprint_length",           # Độ dài sprint (tuần)
            "team_velocity",           # Vận tốc team (story points/sprint)
            "completed_sprints",       # Số sprint đã hoàn thành
            "velocity_history",        # Lịch sử vận tốc team
            "methodology",             # Phương pháp Agile cụ thể (Scrum, Kanban, XP)
            "team_experience",         # Kinh nghiệm team với Agile
            "technical_debt",          # Nợ kỹ thuật (thấp, trung bình, cao)
            "automation_level"         # Mức độ tự động hóa (CI/CD, testing)
        ]
        
        # Sử dụng mô hình COCOMO II làm nền tảng hoặc tạo mới
        self.base_cocomo = base_cocomo_model if base_cocomo_model else COCOMOII()
        
        # Agile adjustment factors
        self.agile_factors = {
            "methodology": {
                "scrum": 0.90,         # Scrum thường tốt hơn
                "kanban": 0.95,        # Kanban linh hoạt nhưng ít cấu trúc hơn
                "xp": 0.85,            # XP có testing liên tục, pair programming
                "hybrid": 0.92,        # Hybrid approach
                "default": 1.0         # Mặc định
            },
            "technical_debt": {
                "low": 0.90,           # Ít nợ kỹ thuật
                "medium": 1.0,         # Trung bình
                "high": 1.15           # Nhiều nợ kỹ thuật
            },
            "automation_level": {
                "high": 0.85,          # CI/CD đầy đủ, test tự động cao
                "medium": 0.95,        # Một số tự động hóa
                "low": 1.05            # Ít hoặc không có tự động hóa
            }
        }
        
        # Sprint history tracking
        self.sprint_history = []
    
    @property
    def model_name(self):
        return self._model_name
    
    @property
    def input_features(self):
        return self._input_features
    
    def estimate_effort(self, project_data):
        """
        Estimate effort using Agile COCOMO
        
        Args:
            project_data (dict): Project information including Agile metrics
            
        Returns:
            dict: Estimation results
        """
        # Check input data
        if "size" not in project_data:
            raise ValueError("Size information (story points or KLOC) is required for Agile COCOMO")
        
        # Extract Agile-specific parameters
        size = project_data.get("size", 0)  # Story points or KLOC
        sprint_length = project_data.get("sprint_length", 2)  # weeks
        team_velocity = project_data.get("team_velocity", 0)  # SP/sprint
        completed_sprints = project_data.get("completed_sprints", 0)
        velocity_history = project_data.get("velocity_history", [])
        
        # Get base COCOMO II estimate
        base_estimate = self.base_cocomo.estimate_effort(project_data)
        base_effort = base_estimate["effort_pm"]
        
        # Calculate Agile adjustment factors
        agile_adjustment = self._calculate_agile_adjustment(project_data)
        
        # Apply velocity-based calibration if we have velocity data
        if team_velocity > 0:
            # Convert effort to sprints
            sprints_total = size / team_velocity if team_velocity > 0 else 0
            
            # Convert sprints to person-months
            # Each sprint is sprint_length weeks, and 1 month is ~4.3 weeks
            effort_pm = (sprints_total * sprint_length / 4.3) * project_data.get("team_size", 1)
            
            # Blend traditional COCOMO with velocity-based estimate
            # More completed sprints means more weight on velocity-based estimate
            velocity_weight = min(0.8, completed_sprints * 0.1)  # Max 80% weight on velocity
            cocomo_weight = 1 - velocity_weight
            
            effort_pm = (effort_pm * velocity_weight) + (base_effort * agile_adjustment * cocomo_weight)
            confidence = 0.6 + (velocity_weight * 0.3)  # Higher confidence with more sprints
        else:
            # Without velocity data, just adjust base COCOMO
            effort_pm = base_effort * agile_adjustment
            confidence = 0.6  # Lower confidence without velocity data
        
        # Calculate remaining effort if we have completed some sprints
        remaining_effort = effort_pm
        if completed_sprints > 0 and team_velocity > 0:
            # Estimate completed effort based on sprints
            completed_effort = (completed_sprints * sprint_length / 4.3) * project_data.get("team_size", 1)
            remaining_effort = max(0, effort_pm - completed_effort)
        
        # Calculate time and team size
        team_size = project_data.get("team_size", 1)
        if team_size <= 0:
            team_size = 1  # Ensure team size is at least 1
            
        sprints_remaining = remaining_effort * 4.3 / (sprint_length * team_size) if sprint_length > 0 and team_size > 0 else 0
        time_months = sprints_remaining * sprint_length / 4.3 if sprint_length > 0 else 0
        
        # If time is too small, set a reasonable minimum
        if time_months < 0.1 and remaining_effort > 0:
            time_months = 0.1
        
        # Generate sprint-by-sprint forecast
        sprint_forecast = self._generate_sprint_forecast(
            remaining_effort, team_velocity, sprint_length, team_size, completed_sprints
        )
        
        result = {
            "effort_pm": effort_pm,
            "remaining_effort_pm": remaining_effort,
            "time_months": time_months,
            "team_size": team_size,
            "confidence": confidence,
            "model": self.model_name,
            "sprints_remaining": sprints_remaining,
            "sprint_forecast": sprint_forecast,
            "agile_adjustment": agile_adjustment
        }
        
        return result
    
    def _calculate_agile_adjustment(self, project_data):
        """Calculate adjustment factor based on Agile-specific factors"""
        # Extract factors
        methodology = project_data.get("methodology", "default").lower()
        technical_debt = project_data.get("technical_debt", "medium").lower()
        automation_level = project_data.get("automation_level", "medium").lower()
        
        # Get adjustment multipliers
        methodology_factor = self.agile_factors["methodology"].get(
            methodology, self.agile_factors["methodology"]["default"]
        )
        technical_debt_factor = self.agile_factors["technical_debt"].get(
            technical_debt, self.agile_factors["technical_debt"]["medium"]
        )
        automation_factor = self.agile_factors["automation_level"].get(
            automation_level, self.agile_factors["automation_level"]["medium"]
        )
        
        # Team experience bonus (0.85 to 1.1)
        team_exp = project_data.get("team_experience", 0.5)  # 0 to 1 scale
        team_exp_factor = 1.1 - (team_exp * 0.25)  # More experience = lower effort
        
        # Combined adjustment
        adjustment = methodology_factor * technical_debt_factor * automation_factor * team_exp_factor
        
        return adjustment
    
    def _generate_sprint_forecast(self, remaining_effort, velocity, sprint_length, team_size, completed_sprints):
        """Generate sprint-by-sprint effort forecast"""
        forecast = []
        
        # Handle edge case where there's no remaining effort
        if remaining_effort <= 0:
            return [{
                "sprint": completed_sprints + 1,
                "story_points": 0,
                "effort_hours": 0,
                "effort_pm": 0
            }]
        
        # Convert person-months to person-hours
        # Assuming 160 hours per person-month (8 hours * 20 days)
        remaining_hours = remaining_effort * 160
        
        # Calculate hours per sprint for the team
        if team_size <= 0 or sprint_length <= 0:
            hours_per_sprint = 160  # Default value if team_size or sprint_length is invalid
        else:
            hours_per_sprint = team_size * 8 * 5 * sprint_length  # team_size * hours/day * days/week * weeks
        
        # Initial velocity estimation (if not provided)
        if velocity <= 0:
            # Estimate velocity from COCOMO effort and team size
            story_points_per_sprint = 20  # Default assumption
        else:
            story_points_per_sprint = velocity
        
        # Calculate story points remaining
        points_per_hour = story_points_per_sprint / hours_per_sprint if hours_per_sprint > 0 else 0.125  # Default: 1 SP = 8 hours
        points_remaining = remaining_hours * points_per_hour
        
        # Generate sprint forecasts (limit to 10 sprints to avoid infinite loops)
        sprint_num = completed_sprints + 1
        max_sprints = 10  # Limit to 10 sprints to avoid infinite loops
        sprint_count = 0
        
        while points_remaining > 0 and sprint_count < max_sprints:
            # Calculate points for this sprint (with some randomness to simulate real-world variation)
            variation = np.random.normal(1, 0.1)  # 10% standard deviation
            points_this_sprint = min(points_remaining, story_points_per_sprint * variation)
            hours_this_sprint = points_this_sprint / points_per_hour if points_per_hour > 0 else points_this_sprint * 8
            
            # Add to forecast
            forecast.append({
                "sprint": sprint_num,
                "story_points": points_this_sprint,
                "effort_hours": hours_this_sprint,
                "effort_pm": hours_this_sprint / 160  # Convert back to person-months
            })
            
            # Update remaining
            points_remaining -= points_this_sprint
            sprint_num += 1
            sprint_count += 1
        
        return forecast
    
    def update_with_sprint_data(self, sprint_num, actual_velocity, actual_effort, remaining_backlog):
        """
        Update model with actual sprint data
        
        Args:
            sprint_num (int): Sprint number
            actual_velocity (float): Actual velocity achieved
            actual_effort (float): Actual effort expended (person-hours)
            remaining_backlog (float): Remaining backlog size (story points)
            
        Returns:
            None
        """
        # Record in sprint history
        self.sprint_history.append({
            "sprint": sprint_num,
            "actual_velocity": actual_velocity,
            "actual_effort": actual_effort,
            "remaining_backlog": remaining_backlog,
            "date": datetime.now().strftime("%Y-%m-%d")
        })
        
        print(f"Sprint {sprint_num} data recorded. Velocity: {actual_velocity} SP, Effort: {actual_effort} hours")
    
    def plot_sprint_burndown(self, initial_backlog=None):
        """
        Plot sprint burndown chart based on recorded history
        
        Args:
            initial_backlog (float, optional): Initial backlog size
            
        Returns:
            matplotlib.figure.Figure: The generated figure
        """
        if not self.sprint_history:
            print("No sprint history available for burndown chart")
            return None
        
        # Extract data
        sprints = [entry["sprint"] for entry in self.sprint_history]
        remaining = [entry["remaining_backlog"] for entry in self.sprint_history]
        
        # Create burndown chart
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot actual burndown
        ax.plot(sprints, remaining, 'b-o', label='Actual Remaining')
        
        # Plot ideal burndown if we have initial backlog
        if initial_backlog:
            ideal_remaining = [initial_backlog * (1 - i/len(sprints)) for i in range(len(sprints) + 1)]
            ideal_sprints = [0] + sprints
            ax.plot(ideal_sprints, ideal_remaining, 'r--', label='Ideal Burndown')
        
        # Add labels and title
        ax.set_xlabel('Sprint')
        ax.set_ylabel('Remaining Story Points')
        ax.set_title('Sprint Burndown Chart')
        ax.grid(True)
        ax.legend()
        
        return fig
    
    def suitability_score(self, project_data):
        """
        Calculate suitability score for Agile COCOMO
        
        Args:
            project_data (dict): Project information
            
        Returns:
            float: Suitability score (0-1)
        """
        methodology = project_data.get("methodology", "").lower()
        
        # Agile COCOMO is more suitable for agile projects
        methodology_score = 0.9 if methodology in ["agile", "scrum", "kanban", "xp"] else 0.4
        
        # Team velocity data increases suitability
        velocity_score = 0.8 if project_data.get("team_velocity", 0) > 0 else 0.3
        
        # Completed sprints increase suitability
        completed_sprints = project_data.get("completed_sprints", 0)
        sprint_score = min(1.0, 0.3 + (completed_sprints * 0.1))  # Max 1.0
        
        # Combined score
        return 0.4 * methodology_score + 0.3 * velocity_score + 0.3 * sprint_score
