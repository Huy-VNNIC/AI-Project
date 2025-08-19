## API Endpoints

The feedback system provides the following API endpoints:

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

### Scheduled Retraining

The system automatically retrains models using the feedback data through a scheduled job:

1. Set up a cron job to run the retraining script:

```
0 0 1 * * /path/to/AI-Project/retrain_models_with_feedback.sh
```

## Next Steps

1. **Analytics Dashboard**: Add more advanced visualizations for feedback trends
2. **A/B Testing**: Test different model versions side by side
3. **Anomaly Detection**: Flag suspicious feedback data automatically
4. **Email Notifications**: Send regular reports about model performance
