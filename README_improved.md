# Advanced Software Effort Estimation System

This project is a comprehensive software effort estimation system that combines machine learning, natural language processing, and traditional estimation techniques to provide accurate software development effort predictions based on requirements documents.

## Project Components

The system consists of the following components:

1. **ML-Based Requirements Analyzer**: Analyzes requirements documents using advanced NLP and machine learning techniques to extract key features for effort estimation.

2. **Multi-Model Estimation Engine**: Implements various estimation methods including COCOMO II, Function Points Analysis, Use Case Points, and several machine learning models (Random Forest, XGBoost, Neural Networks, etc.).

3. **Model Selection System**: Intelligently selects the most appropriate estimation model based on project characteristics.

4. **Comprehensive Estimation Service**: Provides detailed effort estimates, team composition suggestions, effort breakdowns, and project reports.

5. **REST API**: Exposes the estimation capabilities through a clean REST API that can be integrated with other systems.

6. **Task Management Integration**: Connects with task management systems (like Trello or Kanban) to update effort estimates based on actual task completions.

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd AI-Project
   ```

2. Set up the environment:
   ```
   chmod +x setup_requirement_analyzer.sh
   ./setup_requirement_analyzer.sh
   ```

This script will:
- Install required Python packages
- Download necessary NLP resources
- Train requirement classifier models

### Running the Service

To start the estimation service:

```
chmod +x run_estimation_service.sh
./run_estimation_service.sh
```

Optional parameters:
- `--port <port>`: Specify the port to run the API server (default: 5000)
- `--task-service-url <url>`: URL of the task management service (default: http://localhost:8000)
- `--skip-integration`: Skip integration with task management service

## API Endpoints

The system provides the following API endpoints:

- `GET /api/health`: Health check endpoint
- `POST /api/estimate`: Estimate effort based on requirements text
- `POST /api/team`: Suggest team composition
- `POST /api/breakdown`: Get effort breakdown by phase and component
- `POST /api/report`: Generate comprehensive estimation report
- `POST /api/analyze`: Analyze requirements text

### Example API Usage

#### Estimate Effort

```bash
curl -X POST http://localhost:5000/api/estimate \
  -H "Content-Type: application/json" \
  -d '{"requirements": "The system shall allow users to login and manage their profiles. Users can create, update, and delete tasks. The system should provide notification capabilities.", "method": "auto", "unit": "person_months"}'
```

#### Get Estimation Report

```bash
curl -X POST http://localhost:5000/api/report \
  -H "Content-Type: application/json" \
  -d '{"requirements": "The system shall allow users to login and manage their profiles. Users can create, update, and delete tasks. The system should provide notification capabilities.", "project_name": "Task Management System"}'
```

## Advanced Usage

### Training Models with Custom Datasets

To train estimation models with your own datasets:

```bash
python requirement_analyzer/train_models.py --effort-datasets /path/to/your/dataset.csv
```

### Integrating with Task Management Systems

The system can be integrated with task management systems to update effort estimates based on actual task completions. See the `service_integration.py` script for details.

## Architecture Diagram

```
┌───────────────────┐      ┌───────────────────┐      ┌───────────────────┐
│                   │      │                   │      │                   │
│  Requirements     │──────▶  ML Requirements  │──────▶  Model Selection  │
│  Document         │      │  Analyzer         │      │  System           │
│                   │      │                   │      │                   │
└───────────────────┘      └───────────────────┘      └─────────┬─────────┘
                                                                │
                                                                │
┌───────────────────┐      ┌───────────────────┐      ┌─────────▼─────────┐
│                   │      │                   │      │                   │
│  Task Management  │◀─────│  REST API         │◀─────│  Effort           │
│  Integration      │      │  Server           │      │  Estimation       │
│                   │      │                   │      │  Service          │
└───────────────────┘      └───────────────────┘      └───────────────────┘
```

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
