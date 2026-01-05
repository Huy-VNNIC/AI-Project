---
title: Software Effort Estimation API
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 3.50.2
app_file: app.py
pinned: false
license: mit
---

# Software Effort Estimation API

Advanced software project effort estimation using multiple models including COCOMO II, Function Points, Use Case Points, and Machine Learning models.

## 🔥 Full API Features

### 📍 **Complete FastAPI Backend**
- **POST /estimate**: Analyze requirements text
- **POST /upload-requirements**: Document analysis (.pdf, .doc, .txt, .md)  
- **POST /estimate-from-tasks**: Task-based estimation
- **POST /estimate-cocomo**: Detailed COCOMO II parameters
- **POST /analyze**: Requirements analysis and priority scoring

### 🧠 **Multiple Estimation Models**
- **COCOMO II**: Industry-standard with 17+ parameters
- **Function Points**: Functional complexity analysis
- **Use Case Points**: Actor and use case driven
- **LOC Models**: Linear & Random Forest predictions
- **ML Models**: Historical data-trained models
- **Integrated Approach**: Combines all models for best accuracy

### 📊 **Advanced Features**
- **Priority Analysis**: Smart requirement categorization
- **Confidence Scoring**: Reliability metrics for estimates
- **Phase Distribution**: Inception, Elaboration, Construction, Transition
- **Cost Calculation**: Budget estimation with labor rates
- **Multiple Methods**: Weighted average, median, mean aggregation

### 🔧 **Input Flexibility**
- Plain text requirements
- Uploaded documents (PDF, Word, text files)
- Structured task lists
- Detailed COCOMO II parameters
- Integration with project management tools

Built with FastAPI + Gradio for maximum performance and usability.