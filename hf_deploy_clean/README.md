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

## Features

🔍 **Text Analysis**: Analyze project requirements from plain text
📄 **File Upload**: Upload requirement documents (.txt, .md)
📊 **Multiple Models**: Traditional and ML-based estimation approaches
🎯 **Confidence Scoring**: Reliability metrics for estimations

## API Endpoints

- **POST /estimate**: Estimate effort from requirements text
- **POST /upload-requirements**: Process uploaded documents
- **GET /docs**: Interactive API documentation

## Usage

1. **Text Analysis**: Enter your project requirements in the text area
2. **File Upload**: Upload a requirements document
3. **API Access**: Use the REST endpoints for integration

## Models

- **COCOMO II**: Industry-standard parametric estimation
- **Function Points**: Functional size measurement
- **Use Case Points**: Use case driven estimation
- **Machine Learning**: Historical data-based predictions

Built with ❤️ using Gradio and FastAPI