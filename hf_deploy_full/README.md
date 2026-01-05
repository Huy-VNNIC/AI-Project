---
title: Software Effort Estimation Full API
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# 🚀 Software Effort Estimation API

Advanced software project effort estimation API with multiple models including COCOMO II, Function Points, Use Case Points, and Machine Learning models.

## 📋 API Endpoints

### 1. POST `/analyze`
Analyze requirements text and extract parameters
- **Input**: `{"text": "Your requirements here"}`
- **Output**: Extracted parameters and initial analysis

### 2. POST `/upload-requirements` 
Upload and process requirement documents
- **Input**: File upload (PDF, DOCX, TXT)
- **Output**: Processed requirements and analysis

### 3. POST `/estimate-from-tasks`
Estimate effort from task list
- **Input**: `{"tasks": ["task1", "task2", ...]}`
- **Output**: Effort estimation based on task breakdown

### 4. POST `/estimate-cocomo`
Detailed COCOMO II estimation with parameters
- **Input**: COCOMO parameters object
- **Output**: Comprehensive effort estimation

## 🛠️ Estimation Models

- **COCOMO II**: Industry-standard parametric estimation
- **Function Points**: Functional size measurement
- **Use Case Points**: Use case driven estimation  
- **Machine Learning**: Historical data-based predictions
- **Hybrid Approach**: Combines multiple models for accuracy

## 📊 Features

✅ **Multi-Model Integration**: Combines traditional and ML approaches  
✅ **Priority Analysis**: Categorizes requirements by importance  
✅ **Document Processing**: Supports PDF, DOCX, TXT formats  
✅ **Confidence Scoring**: Provides reliability metrics  
✅ **Parameter Extraction**: Automatically identifies project characteristics  
✅ **Task Breakdown**: Analyzes individual tasks for estimation

## 🚀 Usage

Access the API documentation at `/docs` for interactive testing.

### Example Request:
```bash
curl -X POST "https://your-space-url/analyze" \
     -H "Content-Type: application/json" \
     -d '{"text": "Build a web application with user authentication and reporting"}'
```

Built with ❤️ using FastAPI, Scikit-learn, and Spacy