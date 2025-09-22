# Feedback Loop & Model Improvement System

This production-ready component enables the AI Prediction Platform to continuously improve its effort estimation accuracy through a self-improving feedback loop system.

## Overview

The feedback system collects actual effort data after project completion, processes this information, and uses it to retrain the estimation models periodically, resulting in progressively better accuracy over time. The entire pipeline is automated, from data collection through the frontend to model retraining via scheduled jobs.

## Key Features

- **Feedback Collection**: API endpoints and UI for submitting actual effort after project completion
- **Feature Extraction**: Automatically extracts and normalizes features from feedback data for model compatibility
- **Automatic Model Retraining**: Scheduled process to retrain models with new feedback data
- **Performance Monitoring**: Comprehensive dashboards to track estimation errors and model improvements
- **Production-Ready API**: Robust, integrated API service with proper error handling and logging

## Components

### 1. Feedback Collector (`feedback_collector.py`)

Manages the persistent storage and retrieval of feedback data:
- Adds new feedback entries with validation and preprocessing
- Loads and filters existing feedback data
- Generates comprehensive statistics about collected feedback
- Tracks error metrics across different estimation methods
- Persists data in JSON format with backup mechanisms

### 2. Feature Extractor (`feedback_feature_extractor.py`)

Processes feedback data to ensure compatibility with model training:
- Extracts numerical features from textual descriptions
- Normalizes features for consistency across different data sources
- Validates feature completeness and handles missing data
- Supports multiple estimation methods (UCP, COCOMO, Function Points)

### 3. Model Retrainer (`model_retrainer.py`)

Handles the production retraining pipeline:
- Combines original training data with feedback data with configurable weights
- Trains new models using scikit-learn with optimized hyperparameters
- Evaluates model performance using multiple metrics (MMRE, PRED25, etc.)
- Manages model versioning and maintains performance history
- Saves retrained models with metadata for tracking improvement

### 4. Scheduled Retraining (`scheduled_retraining.py`)

Provides robust automation for the retraining process:
- Runs as a scheduled job via cron (configurable frequency)
- Implements threshold checks for minimum feedback quantity
- Handles errors gracefully with detailed logging
- Sends email notifications about training results and improvements
- Includes command-line options for manual triggering and testing

### 5. Production API Integration (`feedback_api.py`, `run_estimation_service.py`)

Enterprise-grade API implementation:
- RESTful endpoints for feedback submission, statistics, and insights
- Blueprint-based modular design for maintainability
- Authentication and validation for secure data submission
- Comprehensive error handling and logging
- Production deployment with Waitress WSGI server
- `/api/feedback` - Submit new feedback data
- `/api/feedback/stats` - Get statistics about collected feedback
- `/api/feedback-overview` - Get insights about model performance

## Usage

### Submitting Feedback

After a project is completed, users can submit actual effort data via the API:

```json
POST /api/feedback
{
    "project_id": "project123",
    "task_id": "task456",
    "requirement_text": "Implement user authentication system...",
    "estimated_effort": 2.5,
    "actual_effort": 3.0,
    "effort_unit": "PERSON_MONTH"
}
```

### Viewing Feedback Statistics

```
GET /api/feedback/stats
```

Response:
```json
{
    "success": true,
    "stats": {
        "total_feedback": 42,
        "avg_estimation_error": 18.5,
        "median_error": 15.2,
        "last_feedback": "2025-08-10T14:32:45.123Z"
    }
}
```

## API Endpoints

The feedback system provides the following production-ready API endpoints:

### 1. Submit Feedback

**Endpoint:** `/api/feedback`

**Method:** POST

**Request Body:**
```json
{
  "project_id": "12345",
  "project_name": "ERP System Implementation",
  "predicted_effort": 320.5,
  "actual_effort": 345.2,
  "estimation_method": "UCP",
  "project_features": {
    "uaw": 12,
    "ucw": 15,
    "tcf": 0.85,
    "ecf": 0.78,
    "requirements": "The system should allow users to manage inventory..."
  },
  "completion_date": "2023-09-15",
  "team_size": 7
}
```

**Response:**
```json
{
  "success": true,
  "message": "Feedback recorded successfully",
  "feedback_id": "fb-12345"
}
```

### 2. Get Feedback Statistics

**Endpoint:** `/api/feedback/stats`

**Method:** GET

**Response:**
```json
{
  "success": true,
  "total_feedback": 42,
  "average_error": 18.5,
  "pred25": 76.2,
  "models": {
    "UCP": {
      "feedback_count": 15,
      "average_error": 17.2,
      "improvement": 3.5
    },
    "COCOMO": {
      "feedback_count": 27,
      "average_error": 19.3,
      "improvement": 2.8
    }
  }
}
```

### 3. Get Feedback Overview

**Endpoint:** `/api/feedback-overview`

**Method:** GET

**Response:**
```json
{
  "success": true,
  "recent_feedback": [
    {
      "project_name": "ERP System",
      "completion_date": "2023-09-15",
      "error_percentage": 7.7
    },
    {
      "project_name": "Mobile App",
      "completion_date": "2023-08-22",
      "error_percentage": 12.3
    }
  ],
  "model_improvements": {
    "UCP": 8.5,
    "COCOMO": 6.2,
    "FP": 9.1
  },
  "retraining_history": [
    {
      "date": "2023-09-01",
      "models_retrained": ["UCP", "COCOMO"],
      "improvement": 7.2
    }
  ]
}
```

## Frontend Integration

The feedback system is fully integrated with the Next.js frontend:

### 1. Feedback Page
- Path: `/feedback`
- Components: 
  - Overview tab with summary statistics
  - Detailed statistics with charts and tables
  - Model improvement history
  - Form for submitting actual effort data

### 2. API Integration
- React hooks for data fetching and submission
- API routes for proxying requests to the backend service

### 3. Navigation
- Direct access from main navigation menu
- Integration with the main dashboard layout

## Production Deployment

### Starting the Service

To run the production-ready estimation service with the feedback system:

```bash
./run_estimation_service.sh
```

#### Command-line options:

- `--host HOST`: Host to run the server on (default: 0.0.0.0)
- `--port PORT`: Port to run the server on (default: 8001)
- `--debug`: Run in debug mode
- `--no-production`: Run in development mode without Waitress

### Manual Retraining

To manually trigger model retraining:

```bash
python scheduled_retraining.py --force --notify
```

## Scheduled Operation

The system is designed to automatically retrain models on a monthly basis:

1. Set up a cron job to run the retraining script:

```
0 0 1 * * /path/to/AI-Project/retrain_models_with_feedback.sh
```

## Implementation Details

### Data Storage

Feedback data is stored in JSON format at `datasets/feedback/feedback_data.json` with the following structure:
- project_id
- project_name
- predicted_effort
- actual_effort
- estimation_method
- project_features (JSON object)
- completion_date
- team_size
- timestamp
- error_percentage

### Model Storage

Retrained models are stored in `models/retrained/` with version history and performance metrics tracked in `training_history.json`.

## Benefits

- **Increasing Accuracy**: Models improve over time as they learn from real-world outcomes
- **Organizational Learning**: System adapts to the specific estimation patterns of your organization
- **Continuous Feedback**: Provides insights about estimation accuracy and areas for improvement
- **Production-Ready**: Robust implementation ready for enterprise use
- **Fully Integrated**: Seamless integration between frontend and backend

## Next Steps

1. **Analytics Dashboard**: Add more advanced visualizations for feedback trends
2. **A/B Testing**: Test different model versions side by side
3. **Anomaly Detection**: Flag suspicious feedback data automatically
4. **Email Notifications**: Send regular reports about model performance
