# AI Effort Estimation System for Hugging Face

This application provides intelligent software effort estimation using machine learning models trained on historical project data. It allows users to get accurate effort estimates based on natural language requirement descriptions.

## Features

- **AI-Powered Estimation**: Get accurate software development effort estimates using multiple ML models
- **Requirement Analysis**: Extract key features from natural language requirement descriptions
- **Continuous Learning**: The system improves over time through user feedback
- **API Access**: Integrate effort estimation into your project management tools
- **Requirement Analyzer Module**: Added support for detailed requirement text analysis with NLP features

## How to Use

### Web Interface

1. Enter your requirement text in the provided text area
2. Click "Get Estimation"
3. View the estimated effort from different models

### API Usage

To get an effort estimation:

```python
import requests

response = requests.post(
    "https://your-huggingface-space-url/api/estimate",
    json={"requirement_text": "Implement a user authentication system with login, registration, password reset, and OAuth integration"}
)

print(response.json())
```

Example response:
```json
{
  "success": true,
  "predictions": {
    "linear_regression": {
      "effort": 3.5,
      "unit": "PERSON_MONTH"
    },
    "random_forest": {
      "effort": 4.2,
      "unit": "PERSON_MONTH"
    }
  },
  "requirement_text": "Implement a user authentication system with login, registration, password reset, and OAuth integration"
}
```

## About the Models

This system uses multiple machine learning models including:

- **COCOMO II-based Linear Regression**: Classical approach enhanced with NLP
- **Random Forest**: More robust to outliers and complex relationships
- **XGBoost**: High-performance gradient boosting for accurate estimates
- **Neural Network**: Deep learning approach for complex requirement understanding

## Feedback System

The system includes a feedback mechanism that collects actual effort data once projects are completed, allowing the models to continuously improve over time.

## Technical Details

Built with:
- Flask web framework
- Scikit-learn for traditional ML models
- NLTK and spaCy for NLP processing
- TensorFlow and PyTorch for deep learning models
