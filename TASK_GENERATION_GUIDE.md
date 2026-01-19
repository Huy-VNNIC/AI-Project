# Task Generation System - Quick Reference Guide

## 🚀 Quick Start

### 1. Train Models (First Time Setup)

```bash
# Make script executable
chmod +x scripts/task_generation/train_all.sh

# Run training pipeline (uses dataset_small_10k by default)
cd scripts/task_generation
./train_all.sh

# Or train with larger dataset
python 01_scan_dataset.py --dataset requirement_analyzer/dataset_large_1m
python 02_build_parquet.py --input requirement_analyzer/dataset_large_1m
python 03_build_splits.py
python 04_train_requirement_detector.py
python 05_train_enrichers.py
```

### 2. Run Demo

```bash
python scripts/task_generation/demo.py
```

### 3. Start API Server

```bash
cd requirement_analyzer
python api.py
```

### 4. Test API

```bash
# Generate tasks from text
curl -X POST http://localhost:8000/generate-tasks \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The system shall support user authentication with email and password. Users must be able to reset passwords.",
    "max_tasks": 10,
    "epic_name": "User Management"
  }'

# Upload document and generate tasks
curl -X POST http://localhost:8000/upload-requirements-generate-tasks \
  -F "file=@requirements.pdf" \
  -F "max_tasks=50" \
  -F "epic_name=Project Alpha"
```

---

## 📁 Directory Structure

```
AI-Project/
├── requirement_analyzer/
│   ├── task_gen/                    # Task generation module
│   │   ├── __init__.py
│   │   ├── schemas.py               # Pydantic models
│   │   ├── segmenter.py             # Document segmentation
│   │   ├── req_detector.py          # Requirement detection
│   │   ├── enrichers.py             # Type/Priority/Domain classifiers
│   │   ├── generator_templates.py   # Template-based generator
│   │   ├── generator_llm.py         # LLM generator (optional)
│   │   ├── postprocess.py           # Dedupe, merge, split
│   │   └── pipeline.py              # Main orchestrator
│   └── api.py                       # FastAPI with new endpoints
├── scripts/task_generation/
│   ├── 01_scan_dataset.py           # Scan & analyze dataset
│   ├── 02_build_parquet.py          # Clean & convert to parquet
│   ├── 03_build_splits.py           # Train/val/test split
│   ├── 04_train_requirement_detector.py
│   ├── 05_train_enrichers.py
│   ├── train_all.sh                 # Master training script
│   └── demo.py                      # Demo script
├── data/
│   ├── processed/                   # Cleaned parquet files
│   └── splits/                      # train.parquet, val.parquet, test.parquet
├── models/task_gen/                 # Trained models
└── report/                          # Quality reports
```

---

## 🔧 Key Components

### Pipeline Stages

1. **Segmentation**: Split document into sections & sentences
2. **Detection**: Filter requirement sentences (binary classifier)
3. **Enrichment**: Predict type/priority/domain (multi-class classifiers)
4. **Generation**: Create task JSON (template or LLM)
5. **Post-processing**: Dedupe, filter, quality control

### Models

- **RequirementDetector**: SGDClassifier (binary) - is_requirement
- **TypeClassifier**: LogisticRegression (multi-class)
- **PriorityClassifier**: LogisticRegression (multi-class)
- **DomainClassifier**: LogisticRegression (multi-class)
- **RoleAssigner**: Rule-based (can upgrade to ML later)

---

## 📊 API Endpoints

### New Task Generation Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/generate-tasks` | POST | Generate tasks from text |
| `/generate-tasks-estimate` | POST | Generate tasks + effort estimation |
| `/upload-requirements-generate-tasks` | POST | Upload file + generate tasks |
| `/tasks/feedback` | POST | Submit task feedback (learning loop) |

### Existing Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/estimate` | POST | Effort estimation from text |
| `/upload-requirements` | POST | Upload & estimate |
| `/estimate-cocomo` | POST | COCOMO II estimation |

---

## 🎯 Task Schema

```json
{
  "task_id": "uuid",
  "title": "Implement user authentication",
  "description": "Setup JWT-based authentication...",
  "acceptance_criteria": [
    "User can login with email/password",
    "JWT tokens are properly validated",
    "Session expires after 24 hours"
  ],
  "type": "security",
  "priority": "High",
  "domain": "general",
  "role": "Backend",
  "labels": ["auth", "security", "api"],
  "story_points": 5,
  "estimated_hours": 20.5,
  "confidence": 0.85,
  "source": {
    "sentence": "Original requirement sentence...",
    "section": "Security Requirements",
    "doc_offset": [1234, 1456]
  }
}
```

---

## 🔍 Training Data Format

Input CSV schema:
```csv
text,is_requirement,type,priority,domain
"The system shall...",1,functional,High,ecommerce
"Figure 1 shows...",0,non_requirement,none,general
```

---

## ⚙️ Configuration

### Training Parameters

```python
# Requirement Detector
model_type = 'sgd'  # or 'logistic'
calibrate = True    # probability calibration

# Enrichers
max_features = 5000
ngram_range = (1, 2)

# Task Generation
max_tasks = 50
requirement_threshold = 0.5
similarity_threshold = 0.85  # for deduplication
```

### Inference Parameters

```python
# Pipeline
requirement_threshold = 0.5  # confidence threshold
max_tasks = 50               # limit output

# Post-processing
min_task_length = 10
similarity_threshold = 0.85  # dedupe
```

---

## 📈 Performance Metrics

Models report:
- **Requirement Detector**: Precision, Recall, F1, ROC-AUC, PR-AUC
- **Enrichers**: Accuracy, Macro-F1, Weighted-F1 per class
- **Generation**: Avg confidence, task count, processing time

---

## 🐛 Troubleshooting

### Models not found
```bash
# Train models first
cd scripts/task_generation
./train_all.sh
```

### spaCy model missing
```bash
python -m spacy download en_core_web_sm
```

### Low quality tasks
- Increase `requirement_threshold` (0.5 → 0.7)
- Check `confidence` scores in output
- Review training data quality

### Too many/few tasks
- Adjust `max_tasks` parameter
- Tune `requirement_threshold`
- Check segmentation (sentence splitting)

---

## 🔄 Retraining

When to retrain:
- New domain data available
- User feedback accumulated
- Model drift detected

```bash
# Incremental retraining with new data
# 1. Add new data to dataset folder
# 2. Re-run pipeline
cd scripts/task_generation
./train_all.sh
```

---

## 📚 Further Reading

- See `TECHNICAL_DOCS.md` for detailed architecture
- See `api_documentation.md` for API specs
- See training scripts for hyperparameter details

---

## 🤝 Contributing

To add new features:

1. **New label classifier**: Add to `enrichers.py`
2. **Custom generator**: Implement `TaskGeneratorBase` interface
3. **New post-processor**: Extend `TaskPostProcessor`
4. **Feedback loop**: Use `/tasks/feedback` endpoint data

---

## 📊 Metrics & Monitoring

Key metrics to track:
- Task generation success rate
- Average confidence scores
- User acceptance rate (via feedback)
- Processing time per document
- Model performance on validation set

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-20
