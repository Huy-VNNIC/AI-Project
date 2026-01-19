# Task Generation Module

AI-powered task generation from requirement documents.

## Quick Start

```python
from requirement_analyzer.task_gen import get_pipeline

# Initialize pipeline
pipeline = get_pipeline(mode='template')

# Generate tasks
document = """
User must be able to login with email and password.
System should validate credentials and issue JWT token.
"""

result = pipeline.generate_tasks(document, max_tasks=10)

# Access tasks
for task in result.tasks:
    print(f"{task.title} [{task.priority}]")
    print(f"  Story Points: {task.story_points}")
    print(f"  AC: {len(task.acceptance_criteria)} criteria\n")
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Verify installation
python scripts/task_generation/test_install.py
```

## Training

```bash
# One-command training (15 min)
bash scripts/task_generation/run_full_pipeline.sh

# Or step-by-step:
python scripts/task_generation/01_scan_dataset.py
python scripts/task_generation/02_build_parquet.py
python scripts/task_generation/03_build_splits.py
python scripts/task_generation/04_train_requirement_detector.py
python scripts/task_generation/05_train_enrichers.py
```

## API Usage

```bash
# Start server
cd requirement_analyzer
uvicorn api:app --reload

# Test endpoint
curl -X POST http://localhost:8000/generate-tasks \
  -H "Content-Type: application/json" \
  -d '{"text": "User must login", "max_tasks": 5}'
```

## Modes

### Template Mode (Current)
- Fast (~1000 tasks/sec)
- Deterministic output
- Generic but consistent

### LLM Mode (To Implement)
- Natural output
- Context-aware
- See `LLM_MODE_QUICKSTART.md`

## Module Structure

```
task_gen/
├── schemas.py          # Pydantic models
├── segmenter.py        # Document → sentences
├── req_detector.py     # ML: is requirement?
├── enrichers.py        # ML: type/priority/domain
├── generator_templates.py  # Template-based
├── postprocess.py      # Dedupe, filter
└── pipeline.py         # Main orchestrator
```

## Output Schema

```json
{
  "title": "Implement User Authentication",
  "description": "Build secure login with JWT tokens...",
  "acceptance_criteria": [
    "User can login with email/password",
    "System validates credentials",
    "JWT token is issued on success"
  ],
  "type": "security",
  "priority": "High",
  "domain": "ecommerce",
  "role": "Backend",
  "story_points": 5,
  "confidence": 0.87
}
```

## Performance

- **Training**: 15 min (1M dataset)
- **Inference**: 1-2s per document (50 tasks)
- **Accuracy**: F1 0.88-0.92 (requirement detection)

## Documentation

- **Architecture**: `ARCHITECTURE.md`
- **Comparison**: `GENERATION_MODES.md`
- **LLM Guide**: `LLM_MODE_QUICKSTART.md`
- **Summary**: `IMPLEMENTATION_SUMMARY.md`
- **Quick Ref**: `TASK_GENERATION_QUICK_REF.md`

## License

See project root LICENSE file.
