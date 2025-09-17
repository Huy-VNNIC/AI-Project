# AI Effort Estimation System - Production Setup

This document provides instructions for running the production-ready AI Effort Estimation System with the integrated feedback loop.

## System Architecture

The system consists of two main components:

1. **AI Service (Backend)**
   - Python Flask API service
   - ML models for effort estimation
   - Feedback collection and processing
   - Automated model retraining

2. **Web Application (Frontend)**
   - Next.js application
   - React components
   - API integration with the AI service

## Starting the System

### 1. Start the AI Service

To start the AI service in production mode:

```bash
cd /path/to/AI-Project
./run_estimation_service.sh --port 8001 --production
```

Options:
- `--host HOST`: Host to run the server on (default: 0.0.0.0)
- `--port PORT`: Port to run the server on (default: 8001)
- `--debug`: Run in debug mode
- `--no-production`: Run in development mode without Waitress

The service will start with the following endpoints:
- `/api/health` - Health check
- `/api/analyze` - Analyze requirements
- `/api/estimate` - Estimate effort
- `/api/team` - Suggest team composition
- `/api/feedback` - Submit feedback on actual effort
- `/api/feedback/stats` - Get feedback statistics
- `/api/feedback-overview` - Get feedback overview and insights

### 2. Start the Web Application

```bash
cd /path/to/AI-Prediction-Platform
npm run dev
```

Make sure your `.env.local` file has the correct AI_SERVICE_URL setting:
```
AI_SERVICE_URL=http://localhost:8001
```

## Using the System

### 1. Estimate Effort for a Project

1. Navigate to the AI Estimation Tool in the web application
2. Enter project requirements
3. Select estimation method
4. Submit for analysis and estimation

### 2. Submit Feedback

After a project is completed:

1. Navigate to the Feedback page
2. Fill in the actual effort data
3. Submit to improve future estimations

### 3. View Feedback Statistics

1. Navigate to the Feedback page
2. Check the Statistics tab to see estimation accuracy
3. View the Model Improvement tab to see how models have improved

## Scheduled Retraining

To set up automatic model retraining:

1. Edit your crontab:
   ```bash
   crontab -e
   ```

2. Add a monthly retraining job (runs at midnight on the 1st of each month):
   ```
   0 0 1 * * /path/to/AI-Project/retrain_models_with_feedback.sh
   ```

## API Documentation

### Analyze Requirements

**Endpoint:** `/api/analyze`

**Method:** POST

**Request:**
```json
{
  "requirements": "User authentication system with login and signup..."
}
```

### Estimate Effort

**Endpoint:** `/api/estimate`

**Method:** POST

**Request:**
```json
{
  "requirements": "User authentication system with login and signup...",
  "method": "UCP",
  "additional_features": {
    "uaw": 10,
    "ucw": 15
  }
}
```

### Submit Feedback

**Endpoint:** `/api/feedback`

**Method:** POST

**Request:**
```json
{
  "project_id": "project123",
  "task_id": "task456",
  "requirement_text": "User authentication system with login and signup...",
  "estimated_effort": 120,
  "actual_effort": 135,
  "effort_unit": "HOUR",
  "model_used": "UCP"
}
```

## Troubleshooting

### AI Service Not Starting

- Check if the virtual environment is activated
- Ensure all required packages are installed: `pip install -r requirements.txt`
- Check log files in the AI-Project directory

### Frontend Not Connecting to Backend

- Verify the `AI_SERVICE_URL` in `.env.local` matches the running AI service
- Check browser console for network errors
- Ensure CORS is properly configured in the AI service

### Feedback Not Being Processed

- Check `feedback_api.log` for errors
- Verify that the feedback data contains all required fields
- Ensure the feedback directory is writable by the service
