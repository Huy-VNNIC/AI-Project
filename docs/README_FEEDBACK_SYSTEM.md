# AI Estimation Tool Feedback System

This document provides an overview of the self-improving feedback loop system implemented for the software effort estimation tool.

## Overview

The feedback system enables users to submit actual project effort data after completion, which is collected, analyzed, and used to retrain the estimation models periodically, creating a continuous improvement cycle.

## Architecture

### Backend Components

1. **Feedback API (`feedback_api.py`)**
   - Provides RESTful endpoints for feedback submission and statistics
   - Endpoints: `/api/feedback`, `/api/feedback/stats`, `/api/feedback-overview`
   - Blueprint-based design for modular integration

2. **Feedback Collector (`feedback_collector.py`)**
   - Manages persistent storage of feedback data
   - Performs statistics calculations and data aggregation
   - Maintains project history and estimation accuracy metrics

3. **Feature Extractor (`feedback_feature_extractor.py`)**
   - Converts feedback data into compatible feature vectors for model retraining
   - Ensures consistency between original training data and feedback data

4. **Model Retrainer (`model_retrainer.py`)**
   - Combines original training data with feedback data
   - Retrains estimation models using scikit-learn
   - Evaluates and persists improved models
   - Tracks model version history and performance improvements

5. **Scheduled Retraining (`scheduled_retraining.py`, `retrain_models_with_feedback.sh`)**
   - Provides automated retraining on a schedule via cron jobs
   - Implements thresholds for minimum feedback quantity before retraining

### Frontend Components

1. **Feedback Page (`/app/feedback/page.tsx`)**
   - Three-tab interface: Overview, Statistics, Model Improvement
   - Visualizations of feedback data and model performance
   - Form for submitting actual effort data

2. **API Integration**
   - React hooks (`use-feedback.ts`) for data fetching and submission
   - API route for proxying requests to the backend service

3. **UI Components**
   - Statistics display (`feedback-stats.tsx`)
   - Submission dialog (`actual-effort-dialog.tsx`)

## Deployment

### Starting the Production Service

To run the production-ready estimation service with feedback:

```bash
./run_estimation_service.sh
```

#### Command-line options:

- `--host HOST`: Host to run the server on (default: 0.0.0.0)
- `--port PORT`: Port to run the server on (default: 8001)
- `--debug`: Run in debug mode
- `--no-production`: Run in development mode without Waitress

Example:
```bash
./run_estimation_service.sh --port 8080 --debug
```

### Scheduled Retraining

To enable automatic retraining with cron:

1. Edit your crontab:
```bash
crontab -e
```

2. Add this line to run retraining daily at midnight:
```
0 0 * * * /path/to/retrain_models_with_feedback.sh
```

## API Documentation

### Feedback Submission

**Endpoint:** `/api/feedback`

**Method:** POST

**Request Body:**
```json
{
  "project_id": "string",
  "project_name": "string",
  "predicted_effort": 120.5,
  "actual_effort": 130.2,
  "estimation_method": "UCP",
  "project_features": {
    "feature1": "value1",
    "feature2": "value2"
  },
  "completion_date": "2023-07-15",
  "team_size": 5
}
```

### Feedback Statistics

**Endpoint:** `/api/feedback/stats`

**Method:** GET

**Response:**
```json
{
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

### Feedback Overview

**Endpoint:** `/api/feedback-overview`

**Method:** GET

**Response:**
```json
{
  "recent_feedback": [...],
  "model_improvements": [...],
  "retraining_history": [...],
  "accuracy_trends": [...]
}
```

## Development

To extend the feedback system:

1. Add new metrics in `feedback_collector.py`
2. Update frontend visualization in `feedback-stats.tsx`
3. Modify retraining parameters in `model_retrainer.py`
