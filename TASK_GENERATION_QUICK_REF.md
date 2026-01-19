# AI Task Generation System - Quick Reference

## 🎯 Overview
End-to-end AI system that automatically generates software tasks from requirement documents.

**Pipeline**: Document → Requirements → Labels (type/priority/domain/role) → Tasks (JSON)

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements-task-generation.txt
python -m spacy download en_core_web_sm
```

### 2. Test Installation
```bash
python scripts/task_generation/test_install.py
```

### 3. Run Full Training Pipeline
```bash
./scripts/task_generation/run_full_pipeline.sh
```
This will:
- Scan & analyze dataset
- Clean & convert to parquet
- Create train/val/test splits
- Train requirement detector
- Train enrichment classifiers (type/priority/domain)
- Run demo

### 4. Start API Server
```bash
python requirement_analyzer/api.py
```

### 5. Test API
```bash
curl -X POST http://localhost:8000/generate-tasks \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The system must allow users to register and login.",
    "max_tasks": 10
  }'
```

---

## 📁 Project Structure

```
requirement_analyzer/
  task_gen/                    # Main task generation module
    __init__.py
    schemas.py                 # Pydantic models (GeneratedTask, etc.)
    segmenter.py               # Document → sentences
    req_detector.py            # ML: is_requirement classifier
    enrichers.py               # ML: type/priority/domain classifiers + role rules
    generator_templates.py     # Template-based task generator
    postprocess.py             # Dedupe, filter, split/merge
    pipeline.py                # Main orchestrator
  
  dataset_large_1m/            # Training data (1M rows)
  dataset_small_10k/           # Training data (10K rows)

scripts/task_generation/       # Training & utility scripts
  01_scan_dataset.py           # Data quality analysis
  02_build_parquet.py          # Clean & convert to parquet
  03_build_splits.py           # Stratified train/val/test split
  04_train_requirement_detector.py
  05_train_enrichers.py
  demo_task_generation.py
  run_full_pipeline.sh
  test_install.py

models/task_gen/               # Trained models (created after training)
  requirement_detector_*.joblib
  type_*.joblib
  priority_*.joblib
  domain_*.joblib

data/
  processed/                   # Cleaned parquet files
  splits/                      # train.parquet, val.parquet, test.parquet

report/                        # Training reports & metrics
  data_quality_report.md
```

---

## 🔧 Training Pipeline Details

### Step 1: Scan Dataset
```bash
python scripts/task_generation/01_scan_dataset.py \
  --dataset requirement_analyzer/dataset_large_1m \
  --output report/data_quality_report
```
**Output**: JSON + Markdown report with statistics

### Step 2: Clean & Convert
```bash
python scripts/task_generation/02_build_parquet.py \
  --input requirement_analyzer/dataset_large_1m \
  --output data/processed \
  --min-length 10 \
  --max-length 1000
```
**Output**: `clean_full.parquet`, `clean_requirements.parquet`, `label_maps.json`

### Step 3: Create Splits
```bash
python scripts/task_generation/03_build_splits.py \
  --input data/processed \
  --output data/splits \
  --train-size 0.8 \
  --val-size 0.1 \
  --test-size 0.1
```
**Output**: `train.parquet`, `val.parquet`, `test.parquet`

### Step 4: Train Requirement Detector
```bash
python scripts/task_generation/04_train_requirement_detector.py \
  --data-dir data/splits \
  --output-dir models/task_gen \
  --model-type sgd
```
**Output**: Binary classifier (is_requirement), metrics, confusion matrix

### Step 5: Train Enrichers
```bash
python scripts/task_generation/05_train_enrichers.py \
  --data-dir data/splits \
  --output-dir models/task_gen \
  --labels type priority domain
```
**Output**: 3 multi-class classifiers, metrics, confusion matrices

---

## 📡 API Endpoints

### POST /generate-tasks
Generate tasks from requirement document

**Request**:
```json
{
  "text": "The system must...",
  "max_tasks": 50,
  "mode": "template",
  "include_story_points": true,
  "domain_hint": "ecommerce",
  "epic_name": "MVP Sprint 1"
}
```

**Response**:
```json
{
  "tasks": [
    {
      "task_id": "uuid",
      "title": "Implement user registration",
      "description": "...",
      "acceptance_criteria": ["...", "..."],
      "type": "functional",
      "priority": "High",
      "domain": "ecommerce",
      "role": "Backend",
      "story_points": 5,
      "confidence": 0.87
    }
  ],
  "total_tasks": 12,
  "stats": {...},
  "processing_time": 2.3
}
```

### POST /generate-tasks-estimate
Generate tasks + effort estimation

### POST /upload-requirements-generate-tasks
Upload file (PDF/DOCX/TXT) and generate tasks

### POST /tasks/feedback
Submit feedback for learning loop

---

## 🧠 Architecture

### Inference Pipeline (Online)
```
Document Text
    ↓
[Segmenter] → Sentences
    ↓
[RequirementDetector] → Filter requirements (threshold=0.5)
    ↓
[Enrichers] → type/priority/domain/role + confidence
    ↓
[TaskGenerator] → Generate task JSON (title/desc/AC)
    ↓
[PostProcessor] → Dedupe, filter, validate
    ↓
Generated Tasks (JSON)
```

### Task Schema
```python
{
  "task_id": str,
  "title": str,
  "description": str,
  "acceptance_criteria": [str],
  "type": str,          # functional, security, interface, data, etc.
  "priority": str,      # Low, Medium, High
  "domain": str,        # ecommerce, iot, healthcare, etc.
  "role": str,          # Backend, Frontend, QA, DevOps, Security
  "labels": [str],
  "story_points": int,  # Fibonacci: 1,2,3,5,8,13,21
  "confidence": float,
  "source": {
    "sentence": str,
    "section": str,
    "doc_offset": [int, int]
  }
}
```

---

## 🎛️ Configuration

### Model Thresholds
- **Requirement detection**: 0.5 (adjustable)
- **Similarity dedupe**: 0.85
- **Min confidence**: 0.3

### Story Points Allocation
Based on:
- Priority: High=1.3x, Medium=1.0x, Low=0.8x
- Type: security=1.2x, data=1.1x, functional=1.0x
- Role: Security=1.2x, DevOps=1.1x, Backend=1.0x

Mapped to Fibonacci: 1,2,3,5,8,13,21

---

## 📊 Model Performance (Expected)

### Requirement Detector
- **F1 Score**: 0.85-0.92
- **PR-AUC**: 0.88-0.95
- Target: High recall (don't miss requirements)

### Type Classifier
- **Macro F1**: 0.75-0.85
- Classes: functional, security, interface, data, performance, etc.

### Priority Classifier
- **Macro F1**: 0.70-0.80
- Classes: Low, Medium, High

### Domain Classifier
- **Macro F1**: 0.78-0.88
- Classes: ecommerce, iot, healthcare, education, finance, general

---

## 🐛 Troubleshooting

### Models not found
```bash
# Train models first
./scripts/task_generation/run_full_pipeline.sh
```

### spaCy model missing
```bash
python -m spacy download en_core_web_sm
```

### API returns 503
Check that models exist in `models/task_gen/`

### Low quality tasks
- Increase requirement detection threshold
- Train on more diverse data
- Adjust postprocessing filters

---

## 🔄 Continuous Improvement

### Feedback Loop
1. Users edit generated tasks in UI
2. Submit feedback via `/tasks/feedback`
3. Store edits in database
4. Periodically retrain with user corrections

### Future Enhancements
- Fine-tune T5/BART for text→JSON generation
- Add LLM mode for more natural output
- Multi-language support
- Integration with Jira/Trello APIs

---

## 📚 Key Files

- `requirement_analyzer/api.py` - FastAPI endpoints
- `requirement_analyzer/task_gen/pipeline.py` - Main orchestrator
- `requirement_analyzer/task_gen/schemas.py` - Data models
- `scripts/task_generation/run_full_pipeline.sh` - One-command training

---

## ✅ Success Criteria

✓ Dataset scanned and cleaned
✓ 4 ML models trained (req detector + 3 enrichers)
✓ API returns tasks in < 5 seconds
✓ Task confidence > 0.7 average
✓ Story points allocated
✓ JSON schema validated

---

## 🆘 Support

For issues, check:
1. `report/data_quality_report.md` - Data stats
2. `models/task_gen/*_metrics.json` - Model performance
3. API logs - `logger.info()` messages

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-20
