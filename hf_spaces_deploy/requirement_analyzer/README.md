# Software Effort Estimation Service

This service analyzes software requirements documents and automatically estimates development effort using trained machine learning models and rule-based approaches.

## Features

- **NLP-based Feature Extraction**: Automatically extracts relevant parameters from requirements documents.
- **Multiple Estimation Models**: Uses COCOMO II, Function Points, Use Case Points, and trained ML models.
- **Integration with Task Management**: Import requirements from Trello/Jira (planned functionality).
- **User-friendly Web Interface**: Simple web UI for entering/uploading requirements and viewing estimates.
- **REST API**: Programmatic access to estimation capabilities.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd AI-Project
   ```

2. Run the setup script:
   ```
   ./start_estimation_service.sh
   ```
   
   This will:
   - Create a virtual environment
   - Install dependencies
   - Start the service

3. Access the web interface at: http://localhost:8000

## Using the Service

### Web Interface

The web interface provides four ways to enter requirements:

1. **Text Input**: Paste your requirements document directly.
2. **Upload Document**: Upload a requirements document (.txt, .doc, .docx, .pdf).
3. **Task List**: Manually enter tasks with details like priority and complexity.
4. **Jira/Trello**: Import tasks from Jira or Trello (requires API credentials).

### API Endpoints

The service provides the following API endpoints:

- `POST /analyze`: Analyze a requirements document
- `POST /estimate`: Estimate effort based on requirements text
- `POST /upload-requirements`: Upload and analyze a requirements file
- `POST /estimate-from-tasks`: Estimate based on a list of tasks
- `POST /trello-import`: Import and estimate from Trello cards
- `POST /jira-import`: Import and estimate from Jira issues

## Integration Methods

When estimating effort, you can choose from several integration methods:

- **Weighted Average**: Combines estimates with weights based on historical accuracy.
- **Best Model**: Uses the estimate from the historically best-performing model.
- **Stacking**: Uses a meta-model that learns how to combine individual estimates.
- **Bayesian Average**: Uses Bayesian statistics to combine estimates with uncertainty.

## Extending the System

### Adding New Models

To add a new estimation model:

1. Create a model class in `multi_model_integration/estimation_models.py`
2. Register the model in `EffortEstimator._init_base_models()`

### Improving Feature Extraction

To enhance the feature extraction:

1. Add new patterns or rules to `RequirementAnalyzer` class
2. Update the `extract_machine_learning_features` method

## License

[License information]
