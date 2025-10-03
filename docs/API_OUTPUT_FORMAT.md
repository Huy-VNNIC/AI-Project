# API Output Format Documentation

## Estimation Service API Output

The Estimation Service API returns estimation results in a standardized format for consistent UI display and integration with other systems. The output includes both the overall estimation and detailed model-specific results.

### Example Output

```json
{
  "estimation": {
    "total_effort": 42.75,
    "duration": 8.2,
    "team_size": 5.2,
    "confidence_level": "Medium",
    "model_estimates": {
      "cocomo": {
        "effort": 45.30,
        "name": "COCOMO II (cocomo)",
        "confidence": 0.70,
        "description": "Constructive Cost Model II estimation"
      },
      "function_points": {
        "effort": 38.45,
        "name": "Function Points (function_points)",
        "confidence": 0.75,
        "description": "Function Point Analysis based estimation"
      },
      "ml_rf": {
        "effort": 41.90,
        "name": "ML Random Forest (ml_rf)",
        "confidence": 0.80,
        "description": "Machine Learning Random Forest model"
      }
    }
  },
  "analysis": {
    // Analysis details (features, extracted parameters, etc.)
  }
}
```

### Output Fields

#### Top-Level Structure

| Field | Type | Description |
|-------|------|-------------|
| `estimation` | Object | Contains all estimation results including the final integrated estimate and individual model estimates |
| `analysis` | Object | Contains details of the analysis performed on the requirements, including extracted features |

#### Estimation Object

| Field | Type | Description |
|-------|------|-------------|
| `total_effort` | Number | Final effort estimation in person-months, calculated by integrating multiple model estimates |
| `duration` | Number | Estimated project duration in months |
| `team_size` | Number | Recommended team size for the project |
| `confidence_level` | String | Confidence level of the estimate (`"High"`, `"Medium"`, or `"Low"`) |
| `model_estimates` | Object | Individual estimates from each model used in the integration |

#### Model Estimates Object

Each key in the `model_estimates` object represents a different estimation model. The structure of each model estimate is:

| Field | Type | Description |
|-------|------|-------------|
| `effort` | Number | Effort estimation in person-months from this specific model |
| `name` | String | User-friendly name of the model with its identifier |
| `confidence` | Number | Confidence score for this estimate, from 0.0 to 1.0 |
| `description` | String | Description of the model and how it produces estimates |

### Available Models

1. **COCOMO II** (`cocomo`) - Constructive Cost Model II, suitable for medium to large traditional projects
2. **Function Points** (`function_points`) - Based on function point analysis, suitable for business applications
3. **Use Case Points** (`use_case`) - Based on use case analysis, suitable for object-oriented projects
4. **ML Random Forest** (`ml_rf`) - Machine learning model using Random Forest algorithm
5. **ML Gradient Boosting** (`ml_gb`) - Machine learning model using Gradient Boosting algorithm
6. **ML Decision Tree** (`ml_dt`) - Machine learning model using Decision Tree algorithm
7. **ML Linear Regression** (`ml_lr`) - Machine learning model using Linear Regression algorithm

### Error Response

When an error occurs during estimation, the API will return a default estimation with an error message:

```json
{
  "estimation": {
    "total_effort": 10.0,
    "duration": 6.0,
    "team_size": 2.0,
    "confidence_level": "Low",
    "model_estimates": {
      "default": {
        "effort": 10.0,
        "confidence": 0.3,
        "description": "Default estimation due to error"
      }
    },
    "error": "Error details will be provided here"
  },
  "analysis": {
    // Default analysis or partial analysis if available
  }
}
```

## Integration with Frontend

The standardized format enables consistent display in the frontend UI, including:

1. **Summary cards** showing total effort, duration, team size, and confidence level
2. **Model comparison charts** displaying estimates from different models
3. **Detailed model information** showing the name, confidence, and description of each model
4. **Analysis explorer** displaying the features extracted from requirements

The frontend automatically handles both the new standardized format and the legacy format for backward compatibility.