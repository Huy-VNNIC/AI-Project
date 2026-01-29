# Task Generation System - Quick Reference Card

## 🚀 One-Command Training (Recommended)

```bash
# Train on medium dataset (100k samples) - ~10-15 minutes
bash scripts/task_generation/train_all.sh medium

# Or train on small dataset for quick test (~2-3 minutes)
bash scripts/task_generation/train_all.sh small

# Or full production dataset (~1-2 hours)
bash scripts/task_generation/train_all.sh large
```

This single command will:
1. ✅ Scan and analyze data quality
2. ✅ Clean and convert to Parquet
3. ✅ Create stratified train/val/test splits
4. ✅ Train requirement detector (binary classifier)
5. ✅ Train enrichers (type/priority/domain)
6. ✅ Save all models and metrics

---

## 🧪 Test After Training

```bash
# Run demo script
python demo_task_generation.py

# Start API server
python requirement_analyzer/api.py
```

Then test API:
```bash
curl -X POST http://localhost:8000/generate-tasks \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The system must support user authentication with email and password.",
    "max_tasks": 10
  }'
```

---

## 📡 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/generate-tasks` | POST | Generate tasks from text |
| `/generate-tasks-estimate` | POST | Generate + estimate effort |
| `/upload-requirements-generate-tasks` | POST | Upload doc + generate |
| `/tasks/feedback` | POST | Submit user feedback |

---

## 📂 Project Structure

```
requirement_analyzer/
  task_gen/                    # Main module
    __init__.py
    schemas.py                 # Pydantic models
    segmenter.py               # Document → sentences
    req_detector.py            # Requirement detector (ML)
    enrichers.py               # Type/priority/domain (ML) + role (rules)
    generator_templates.py     # Template-based generation
    postprocess.py             # Dedupe + filter
    pipeline.py                # Main orchestrator

scripts/task_generation/
  01_scan_dataset.py          # Data quality analysis
  02_build_parquet.py         # Data cleaning
  03_build_splits.py          # Train/val/test split
  04_train_requirement_detector.py
  05_train_enrichers.py
  train_all.sh                # Master training script

models/task_gen/              # Trained models
  requirement_detector_model.joblib
  type_model.joblib
  priority_model.joblib
  domain_model.joblib
  *_metrics.json

data/
  processed/                  # Cleaned parquet files
  splits/                     # Train/val/test splits
```

---

## 🎯 Common Tasks

### Generate tasks from Python code:

```python
from requirement_analyzer.task_gen import get_pipeline

pipeline = get_pipeline()

response = pipeline.generate_tasks(
    text=your_requirements_doc,
    max_tasks=50,
    epic_name="My Epic",
    domain_hint="ecommerce"
)

for task in response.tasks:
    print(f"{task.title} - {task.priority} - {task.story_points} pts")
```

### Check model metrics:

```bash
cat models/task_gen/requirement_detector_metrics.json
cat models/task_gen/enrichers_summary.json
```

### Retrain with more data:

```bash
# Just run training script again with larger dataset
bash scripts/task_generation/train_all.sh large
```

---

## 🔧 Configuration

### Tune requirement detection threshold:

```python
response = pipeline.generate_tasks(
    text=doc,
    requirement_threshold=0.6  # Higher = more strict
)
```

### Tune deduplication:

```python
from requirement_analyzer.task_gen import get_postprocessor

postprocessor = get_postprocessor(
    similarity_threshold=0.90,  # Higher = less deduplication
    min_task_length=15
)
```

### Add custom templates:

Edit `requirement_analyzer/task_gen/generator_templates.py`:

```python
self.templates['your_type'] = {
    'title_template': 'Custom {action} {object}',
    'description_template': '...',
    'ac_templates': ['...']
}
```

---

## 📊 Expected Performance

**Medium Dataset (100k samples):**

| Model | Metric | Score |
|-------|--------|-------|
| Requirement Detector | F1 | 0.85+ |
| Requirement Detector | PR-AUC | 0.90+ |
| Type Classifier | Macro-F1 | 0.75+ |
| Priority Classifier | Macro-F1 | 0.70+ |
| Domain Classifier | Macro-F1 | 0.80+ |

**Task Generation:**
- Speed: ~100-200 tasks/minute
- Avg Confidence: 0.75-0.85
- Valid JSON: 100%

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `Pipeline not available` | Run training first: `bash scripts/task_generation/train_all.sh medium` |
| `spaCy model error` | `python -m spacy download en_core_web_sm` |
| `Memory error` | Use smaller dataset or reduce chunksize |
| Low task quality | Check data quality report, increase training data |

---

## 💡 Tips

1. **Start with `medium` dataset** - good balance of quality and speed
2. **Check data quality report** before training to understand your data
3. **Use domain hints** when you know the domain for better accuracy
4. **Collect user feedback** via `/tasks/feedback` endpoint for future improvements
5. **Monitor confidence scores** - tasks with <0.5 confidence may need review

---

## 📚 Full Documentation

See [TASK_GENERATION_README.md](TASK_GENERATION_README.md) for complete documentation.

---

**Version**: 1.0.0  
**Quick Start Time**: ~15 minutes (medium dataset)  
**Ready for Production**: Yes ✅
