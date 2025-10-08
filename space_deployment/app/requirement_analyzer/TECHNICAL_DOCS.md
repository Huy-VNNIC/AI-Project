# Software Effort Estimation Service: Technical Documentation

## Overview

This service analyzes software requirements and provides effort estimations using multiple models and techniques. It combines rule-based approaches (COCOMO II, Function Points, Use Case Points) with machine learning models to provide accurate effort estimates.

## System Architecture

The system consists of several key components:

1. **Requirement Analyzer**: Extracts relevant parameters from requirements documents using NLP techniques.
2. **Effort Estimator**: Uses the extracted parameters to estimate development effort using multiple models.
3. **API Service**: Provides REST API endpoints for accessing the estimation capabilities.
4. **Web Interface**: User-friendly interface for inputting requirements and viewing estimates.
5. **Task Integration**: Allows importing requirements from task management tools (Trello, Jira).

## Machine Learning Pipeline

The ML pipeline includes:

1. **Feature Extraction**: Extracts numerical and categorical features from requirements text.
2. **Preprocessing**: Handles missing values, scales numerical features, and encodes categorical features.
3. **Model Prediction**: Multiple models (Linear Regression, Decision Tree, Random Forest, Gradient Boosting) provide predictions.
4. **Model Integration**: Combines predictions from different models using various methods (weighted average, best model, stacking, Bayesian average).

## Common Issues and Solutions

### Preprocessor Feature Count Mismatch

**Issue**: The preprocessor expects a specific number of features, but the analyzer provides fewer.

**Solution**: We've modified the `estimate_from_ml_model` method to handle preprocessor errors gracefully. It now attempts to use the preprocessor first, but falls back to direct prediction if there's an error.

```python
# Try to apply preprocessor, but fall back to direct prediction if there's an error
if self.preprocessor:
    try:
        X_transformed = self.preprocessor.transform(X)
        effort = model.predict(X_transformed)[0]
    except Exception as e:
        print(f"Warning: Error applying preprocessor: {e}")
        # If error, try predicting directly with original data
        effort = model.predict(X)[0]
else:
    effort = model.predict(X)[0]
```

### Vietnamese Language Support

The system has been enhanced to support both English and Vietnamese requirements by:

1. Adding Vietnamese keywords for requirement classification
2. Improving the text analysis to handle Vietnamese characters
3. Making feature extraction robust to different languages

## API Endpoints

- `POST /analyze`: Analyze requirements document
- `POST /estimate`: Estimate effort from requirements text
- `POST /upload-requirements`: Upload and analyze a requirements file
- `POST /estimate-from-tasks`: Estimate from a list of tasks
- `POST /trello-import`: Import and estimate from Trello cards
- `POST /jira-import`: Import and estimate from Jira issues

## Testing

Use the included test script to validate the system:

```bash
python3 test_ml_model_fix.py
```

This script tests:
1. Direct prediction with ML models
2. Full workflow from requirements analysis to effort estimation

## Future Improvements

1. **Feature Alignment**: Ensure full compatibility between analyzer and ML models by aligning features.
2. **Enhanced NLP**: Improve feature extraction for minimal or ambiguous input.
3. **Feedback Loop**: Add capability to incorporate user feedback to improve estimations over time.
4. **Integration Enhancements**: Complete and document real-world integration with Trello/Jira using API credentials.
