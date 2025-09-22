# COCOMO II Extended - Usage Guide

This guide explains how to use the COCOMO II Extended models to predict software development effort, schedule, and team size based on project size metrics.

## Prerequisites

- Python 3.6+
- Required packages: pandas, numpy, scikit-learn, joblib

## Quick Start

```python
from cocomo_ii_predictor import cocomo_ii_estimate

# Estimate using Lines of Code
result_loc = cocomo_ii_estimate(10, size_type='kloc')
print(f"Effort: {result_loc['effort_pm'][0]:.2f} person-months")
print(f"Duration: {result_loc['time_months'][0]:.2f} months")
print(f"Team Size: {int(result_loc['developers'][0])} developers")

# Estimate using Function Points
result_fp = cocomo_ii_estimate(500, size_type='fp')
print(f"Effort: {result_fp['effort_pm'][0]:.2f} person-months")

# Estimate using Use Case Points
result_ucp = cocomo_ii_estimate(300, size_type='ucp')
print(f"Effort: {result_ucp['effort_pm'][0]:.2f} person-months")
```

## Detailed Usage

### Load the COCOMO II Predictor

```python
from cocomo_ii_predictor import CocomoIIPredictor

# Load the predictor
model_path = '/path/to/models/cocomo_ii_extended'
predictor = CocomoIIPredictor(model_path)
```

### Create Input Data

```python
import pandas as pd

# Create input data for prediction
input_data = pd.DataFrame({
    'schema': ['LOC'],  # Can be 'LOC', 'FP', or 'UCP'
    'size': [10],       # Size value (KLOC, Function Points, or Use Case Points)
    'kloc': [10],       # Include relevant size metric
    'fp': [None],       # Set others to None
    'ucp': [None]
})
```

### Make Predictions

```python
# Predict using the default model (Random Forest Tuned)
results = predictor.predict_all(input_data)

# Or specify a different model
results = predictor.predict_all(input_data, model_name='Linear Regression')

# Access the results
effort = results['effort_pm'][0]
time = results['time_months'][0]
team_size = results['developers'][0]
```

### Available Models

- Linear Regression
- Decision Tree
- Random Forest
- Decision Tree (Tuned)
- Random Forest (Tuned)

## Utility Functions

### Simple Estimation

```python
from cocomo_ii_predictor import cocomo_ii_estimate

# Simple estimation with KLOC
result = cocomo_ii_estimate(size=10, size_type='kloc')

# Simple estimation with Function Points
result = cocomo_ii_estimate(size=500, size_type='fp')

# Simple estimation with Use Case Points
result = cocomo_ii_estimate(size=300, size_type='ucp')
```

### Display Results

```python
from cocomo_ii_predictor import display_cocomo_ii_results

# Display formatted results
display_cocomo_ii_results(size=10, size_type='kloc')
```

## Example Application

```python
def estimate_project():
    print("COCOMO II Extended Estimation Tool")
    print("----------------------------------")
    
    # Get user input
    size_type = input("Enter size type (kloc, fp, ucp): ").lower()
    size = float(input(f"Enter project size ({size_type}): "))
    
    # Make prediction
    from cocomo_ii_predictor import display_cocomo_ii_results
    result = display_cocomo_ii_results(size, size_type)
    
    return result

if __name__ == "__main__":
    estimate_project()
```

## Further Information

For more details about the models and how they were trained, refer to the Jupyter notebooks:
- `cocomo_ii_data_preprocessing_enhanced.ipynb`: Data preprocessing and normalization
- `cocomo_ii_model_training.ipynb`: Model training and evaluation
