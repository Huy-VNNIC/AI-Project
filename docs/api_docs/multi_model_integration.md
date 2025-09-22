# Multi-Model Integration and Agile-Adaptive COCOMO

This module provides an advanced software effort estimation system that combines multiple estimation models and adapts to Agile development practices.

## Overview

The system includes two main components:

1. **Multi-Model Integration System**: Combines estimates from multiple models (COCOMO II, Function Points, Use Case Points, Planning Poker) using various integration strategies.

2. **Agile-Adaptive COCOMO**: An extension of COCOMO II that adapts to Agile development processes, incorporating sprint velocity, burndown tracking, and Agile-specific factors.

## Features

### Multi-Model Integration

- Integrates estimates from multiple models to provide more robust predictions
- Supports four integration methods:
  - Weighted Average: Combines estimates using confidence and suitability weights
  - Best Model: Selects the most suitable model for the specific project
  - Stacking: Machine learning approach to combine estimates
  - Bayesian Average: Probabilistic integration of estimates

### Agile-Adaptive COCOMO

- Extends COCOMO II with Agile-specific adjustments
- Uses sprint velocity data to calibrate estimates
- Adapts estimates based on completed sprints
- Provides sprint-by-sprint forecasting
- Generates burndown charts
- Accounts for Agile-specific factors like methodology, technical debt, and automation

## Installation

### Prerequisites

The system requires Python 3.6+ and the following dependencies:

```bash
pip install numpy pandas matplotlib scikit-learn
```

### Usage

#### Multi-Model Integration

```python
from multi_model_integration.estimation_models import COCOMOII, FunctionPoints, UseCasePoints, PlanningPoker
from multi_model_integration.multi_model_integration import MultiModelIntegration

# Create project data
project_data = {
    # COCOMO II inputs
    "size": 25,  # KLOC
    "reliability": 1.15,
    # ...more parameters...
    
    # Function Points inputs
    "external_inputs": 30,
    # ...more parameters...
    
    # Use Case Points inputs
    "simple_actors": 3,
    # ...more parameters...
    
    # Planning Poker inputs
    "user_stories": [
        {"name": "Login System", "points": 5},
        # ...more stories...
    ],
    "velocity": 25,  # SP/sprint
}

# Create multi-model integration
integrator = MultiModelIntegration()

# Estimate with desired integration method
result = integrator.estimate(project_data, method="weighted_average")

# Access the results
print(f"Estimated effort: {result['effort_pm']} person-months")
print(f"Estimated time: {result['time_months']} months")
print(f"Estimated team size: {result['team_size']} people")
```

#### Agile-Adaptive COCOMO

```python
from multi_model_integration.agile_cocomo import AgileCOCOMO

# Create Agile COCOMO model
agile_cocomo = AgileCOCOMO()

# Project data for an Agile project
project_data = {
    "size": 300,  # Story points
    "sprint_length": 2,  # weeks
    "team_velocity": 30,  # SP/sprint (optional)
    "completed_sprints": 4,  # Number of completed sprints (optional)
    "team_size": 5,
    "methodology": "scrum",
    "team_experience": 0.7,  # 0-1 scale
    "technical_debt": "low",
    "automation_level": "high",
    # COCOMO II factors still apply
    "reliability": 1.1,
    "complexity": 1.2
}

# Get estimate
result = agile_cocomo.estimate_effort(project_data)

# Update with actual sprint data
agile_cocomo.update_with_sprint_data(
    sprint_num=5,
    actual_velocity=32,
    actual_effort=192,  # hours
    remaining_backlog=150  # story points
)

# Generate burndown chart
fig = agile_cocomo.plot_sprint_burndown(initial_backlog=300)
fig.savefig("burndown.png")
```

## Running the Demo

The demo script demonstrates both the multi-model integration and Agile-Adaptive COCOMO features:

```bash
python multi_model_integration/demo_integration.py
```

## Extending the System

### Adding New Estimation Models

To add a new estimation model:

1. Create a new class that inherits from `EstimationModel`
2. Implement the required methods:
   - `estimate_effort(project_data)`: Calculate effort estimate
   - `model_name`: Return the name of the model
   - `input_features`: Return the list of required input features
   - `suitability_score(project_data)`: Calculate suitability for projects

Example:

```python
class MyNewModel(EstimationModel):
    def __init__(self):
        self._model_name = "My New Model"
        self._input_features = ["feature1", "feature2"]
    
    @property
    def model_name(self):
        return self._model_name
    
    @property
    def input_features(self):
        return self._input_features
    
    def estimate_effort(self, project_data):
        # Implementation here
        return {
            "effort_pm": calculated_effort,
            "time_months": calculated_time,
            "team_size": calculated_team_size,
            "confidence": 0.7,
            "model": self.model_name
        }
    
    def suitability_score(self, project_data):
        # Implementation here
        return 0.5  # 0-1 scale
```

### Adding New Integration Methods

To add a new integration method:

1. Add a new method to the `MultiModelIntegration` class
2. Update the `integration_methods` dictionary in `__init__`

Example:

```python
def __init__(self, models=None):
    # Existing code...
    self.integration_methods = {
        # Existing methods...
        "my_new_method": self._my_new_method
    }

def _my_new_method(self, model_results, project_data):
    # Implementation here
    return integrated_result
```

## Research Applications

This system can be extended for various research purposes:

1. **Comparative Analysis**: Compare different estimation methods across project types
2. **Uncertainty Analysis**: Study confidence intervals and prediction errors
3. **Agile Metrics Research**: Analyze velocity patterns and burndown characteristics
4. **Factor Impact Analysis**: Study how different factors affect estimation accuracy
5. **Custom Integration Methods**: Develop new ways to combine multiple models

## References

- Boehm, B. W. (2000). Software Cost Estimation with COCOMO II. Prentice Hall.
- Cohn, M. (2005). Agile Estimating and Planning. Prentice Hall.
- Karner, G. (1993). Resource Estimation for Objectory Projects. Objective Systems SF AB.
- Albrecht, A. J. (1979). Measuring Application Development Productivity. IBM.

## License

This project is provided for research and educational purposes.
