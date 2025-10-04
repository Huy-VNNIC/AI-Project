# AI Project - Software Effort Estimation

This project provides tools for software effort estimation using various models including COCOMO II and machine learning approaches.

## Project Structure

The project is organized as follows:

- **docs/**: Documentation
  - **api_docs/**: API documentation
  - **research/**: Research papers and reports
  - **user_guides/**: User guides
  - **diagrams/**: Diagrams and images

- **src/**: Source code
  - **api/**: API endpoints
  - **models/**: ML models
    - **cocomo/**: COCOMO models
    - **ml_models/**: Machine learning models
    - **multi_model/**: Multi-model integration
  - **analyzer/**: Requirement analyzer
  - **feedback/**: Feedback system
  - **utils/**: Utility functions
  - **data_processing/**: Data processing scripts

- **notebooks/**: Jupyter notebooks for analysis and demonstrations
- **tests/**: Test files
- **scripts/**: Shell scripts for running, deploying, and setting up
- **data/**: Data files
  - **raw/**: Raw data
  - **processed/**: Processed data
- **static/**: Static resources

## Getting Started

To get started with the project:

1. Clone the repository:
```bash
git clone https://github.com/Huy-VNNIC/AI-Project.git
cd AI-Project
```

2. Set up the environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Run the requirement analyzer API:
```bash
python -m requirement_analyzer.api
```

## API Documentation

The API will be available at http://localhost:8000, and the documentation can be accessed at http://localhost:8000/docs.

## License

Copyright (c) 2025 Huy-VNNIC
