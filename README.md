# AI Project - Software Effort Estimation

This project provides tools for software effort estimation using various models including COCOMO II and machine learning approaches.

## Project Structure

The project is organized as follows:

- **app/**: Main application code
  - Flask/FastAPI web application
  - API routes and endpoints
  
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

- **docs/**: Documentation
  - API documentation, user guides, research papers
  - Detailed guides for features and deployment
  
- **scripts/**: Shell scripts (`.sh` files)
  - Deployment, testing, and management scripts
  - See [scripts/README.md](scripts/README.md) for details

- **docker/**: Docker configuration
  - Dockerfiles and docker-compose files
  - Nginx configuration
  - See [docker/README.md](docker/README.md) for details

- **tools/**: Utility Python scripts
  - Demo scripts, testing tools, model trainers
  - See [tools/README.md](tools/README.md) for details

- **config/**: Configuration files
  - Requirements files, CSV data, patches
  - See [config/README.md](config/README.md) for details

- **notebooks/**: Jupyter notebooks for analysis and demonstrations

- **tests/**: Test files

- **data/**: Data files
  - **raw/**: Raw data
  - **processed/**: Processed data
  
- **static/**: Static resources (CSS, JS, images)

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
