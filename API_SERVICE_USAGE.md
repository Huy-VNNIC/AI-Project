# Requirement Analyzer API Service

This document describes how to run and use the Requirement Analyzer API service, which provides endpoints for analyzing software requirements and estimating development effort.

## Running the API Service

To run the API service:

```bash
# Option 1: Use the run_api_service.sh script
./run_api_service.sh

# Option 2: Manually activate the virtual environment and run the service
source venv/bin/activate
python -m requirement_analyzer.api
```

The service will start on http://0.0.0.0:8000 by default.

## API Endpoints

### Main UI
- `GET /`: Main HTML interface for the service
- `GET /debug`: Debug page with additional functionality

### Requirement Analysis and Estimation
- `POST /analyze`: Analyze a requirements document
- `POST /estimate`: Estimate effort from a requirements document
- `POST /upload-requirements`: Upload and analyze a requirements file
- `POST /estimate-from-tasks`: Estimate effort from a list of tasks

### Feedback and Model Improvement
- `POST /api/feedback`: Submit feedback about actual effort after project completion
- `GET /api/feedback/stats`: Get statistics about collected feedback data
- `GET /api/feedback-overview`: Get overview and insights about model performance
- `POST /trello-import`: Import and estimate from Trello boards
- `POST /jira-import`: Import and estimate from Jira issues

## Example API Usage

### Analyze Requirements

```bash
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"text": "The system should allow users to register and login. Users should be able to create and edit their profiles."}'
```

### Estimate Effort

```bash
curl -X POST "http://localhost:8000/estimate" \
     -H "Content-Type: application/json" \
     -d '{"text": "The system should allow users to register and login. Users should be able to create and edit their profiles.", "method": "weighted_average"}'
```

### Estimate from Tasks

```bash
curl -X POST "http://localhost:8000/estimate-from-tasks" \
     -H "Content-Type: application/json" \
     -d '{
        "tasks": [
            {
                "title": "User Registration",
                "description": "Implement user registration functionality",
                "priority": "High",
                "complexity": "Medium"
            },
            {
                "title": "User Login",
                "description": "Implement secure user login",
                "priority": "High",
                "complexity": "Medium"
            }
        ],
        "method": "weighted_average"
     }'
```

## Available Estimation Methods

The following estimation methods are available:

- `weighted_average` (default): Weighted average of multiple estimation models
- `cocomo`: COCOMO II model
- `function_points`: Function Point Analysis
- `use_case_points`: Use Case Points
- `neural_network`: Neural Network model

## Feedback System

The API includes a feedback loop system that allows continuous improvement of estimation models based on actual project outcomes.

### Submitting Feedback

After a project is completed, submit the actual effort to improve future estimations:

```bash
curl -X POST http://localhost:5000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "project123",
    "task_id": "task456",
    "requirement_text": "Implement user authentication system with login, registration, and password reset functionality.",
    "estimated_effort": 2.5,
    "actual_effort": 3.0,
    "effort_unit": "PERSON_MONTH"
  }'
```

### Viewing Feedback Statistics

To get statistics about collected feedback:

```bash
curl -X GET http://localhost:5000/api/feedback/stats
```

### Feedback Overview and Insights

To get an overview of model performance and insights:

```bash
curl -X GET http://localhost:5000/api/feedback-overview
```

### Model Retraining

Models are automatically retrained monthly with collected feedback. To manually trigger retraining:

```bash
python scheduled_retraining.py --force
```

For more details, see [FEEDBACK_SYSTEM.md](FEEDBACK_SYSTEM.md).

## Troubleshooting

If you encounter any issues:

1. Check that all dependencies are installed properly
2. Ensure that models are properly trained and available
3. Check the logs for detailed error messages
4. Retrain models if necessary using the retrain scripts

For model or feature mismatch issues, run:

```bash
./fix_sklearn_version.sh
./retrain_with_current_features.sh
```
