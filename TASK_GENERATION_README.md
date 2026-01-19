# AI Task Generation System - Complete Guide

## 📋 Tổng Quan

Hệ thống **AI Task Generation** tự động sinh task từ tài liệu requirements, sử dụng kết hợp **Machine Learning** và **Template-based Generation** để đảm bảo chất lượng cao và ổn định.

### Kiến Trúc

```
Input (Requirements Doc)
    ↓
[1] Segmentation → sections + sentences
    ↓
[2] Requirement Detection → ML classifier (binary)
    ↓
[3] Enrichment → type/priority/domain (ML) + role (rule-based)
    ↓
[4] Task Generation → Template + NLP parsing
    ↓
[5] Post-processing → dedupe + filter
    ↓
Output (Tasks JSON) → [Optional] Effort Estimation
```

---

## 🚀 Quick Start

### Bước 1: Chuẩn Bị Dataset

Bạn đã có 3 datasets sẵn:
- `dataset_small_10k/` - Để test nhanh
- `dataset_medium_100k/` - Để training baseline
- `dataset_large_1m/` - Để training production model

### Bước 2: Chạy Data Pipeline

```bash
cd /home/dtu/AI-Project/AI-Project

# Activate virtual environment
source venv/bin/activate

# Bước 2.1: Scan dataset (xem chất lượng dữ liệu)
python scripts/task_generation/01_scan_dataset.py \
    --dataset requirement_analyzer/dataset_medium_100k \
    --output report/data_quality_report

# Bước 2.2: Clean và convert sang Parquet (để training nhanh)
python scripts/task_generation/02_build_parquet.py \
    --input requirement_analyzer/dataset_medium_100k \
    --output data/processed \
    --min-length 10 \
    --max-length 1000

# Bước 2.3: Tạo train/val/test splits (stratified)
python scripts/task_generation/03_build_splits.py \
    --input data/processed \
    --output data/splits \
    --train-size 0.8 \
    --val-size 0.1 \
    --test-size 0.1
```

### Bước 3: Train ML Models

```bash
# Bước 3.1: Train Requirement Detector (binary classifier)
python scripts/task_generation/04_train_requirement_detector.py \
    --data-dir data/splits \
    --output-dir models/task_gen \
    --model-type sgd

# Bước 3.2: Train Enrichers (type/priority/domain classifiers)
python scripts/task_generation/05_train_enrichers.py \
    --data-dir data/splits \
    --output-dir models/task_gen \
    --labels type priority domain
```

Kết quả models sẽ được lưu trong `models/task_gen/`:
```
models/task_gen/
├── requirement_detector_vectorizer.joblib
├── requirement_detector_model.joblib
├── requirement_detector_metrics.json
├── type_vectorizer.joblib
├── type_model.joblib
├── type_classes.json
├── priority_vectorizer.joblib
├── priority_model.joblib
├── priority_classes.json
├── domain_vectorizer.joblib
├── domain_model.joblib
├── domain_classes.json
└── enrichers_summary.json
```

### Bước 4: Khởi Động API

```bash
# Cài dependencies nếu chưa có
pip install spacy
python -m spacy download en_core_web_sm

# Start API server
cd requirement_analyzer
python api.py
```

Hoặc sử dụng uvicorn:
```bash
uvicorn requirement_analyzer.api:app --host 0.0.0.0 --port 8000 --reload
```

API sẽ chạy tại: http://localhost:8000

---

## 📡 API Endpoints

### 1. Generate Tasks from Text

**POST** `/generate-tasks`

```json
{
  "text": "The system shall support user authentication...",
  "max_tasks": 50,
  "mode": "template",
  "include_story_points": true,
  "domain_hint": "healthcare",
  "epic_name": "User Management"
}
```

**Response:**
```json
{
  "tasks": [
    {
      "task_id": "uuid",
      "title": "Implement user authentication",
      "description": "...",
      "acceptance_criteria": ["...", "..."],
      "type": "security",
      "priority": "High",
      "domain": "healthcare",
      "role": "Backend",
      "story_points": 5,
      "confidence": 0.87,
      "source": {
        "sentence": "The system shall support user authentication...",
        "section": "Security Requirements"
      }
    }
  ],
  "total_tasks": 15,
  "stats": {
    "type_distribution": {"functional": 8, "security": 5, "interface": 2},
    "avg_confidence": 0.82
  },
  "processing_time": 2.3
}
```

### 2. Generate Tasks + Estimate Effort

**POST** `/generate-tasks-estimate`

Tự động tính story points và effort cho từng task.

### 3. Upload Document and Generate Tasks

**POST** `/upload-requirements-generate-tasks`

- Upload file: `.txt`, `.pdf`, `.docx`, `.md`
- Tự động parse + generate tasks

### 4. Submit Feedback (Learning Loop)

**POST** `/tasks/feedback`

```json
{
  "task_id": "uuid",
  "accepted": true,
  "edited_task": {...},
  "comment": "Need more specific AC"
}
```

---

## 🧪 Testing

### Test thử với sample text:

```python
import requests

text = """
The system must support user registration with email verification.
Users shall be able to login using email and password.
The application should display a dashboard after successful login.
All user data must be encrypted at rest and in transit.
The system needs to support role-based access control.
"""

response = requests.post(
    "http://localhost:8000/generate-tasks",
    json={
        "text": text,
        "max_tasks": 10,
        "domain_hint": "general"
    }
)

tasks = response.json()
print(f"Generated {tasks['total_tasks']} tasks")
for task in tasks['tasks']:
    print(f"- [{task['type']}] {task['title']} (Priority: {task['priority']})")
```

---

## 📊 Model Performance

Sau khi training, check metrics:

```bash
cat models/task_gen/requirement_detector_metrics.json
cat models/task_gen/enrichers_summary.json
```

Expected performance (medium dataset):
- **Requirement Detector**: F1 > 0.85, PR-AUC > 0.90
- **Type Classifier**: Macro-F1 > 0.75
- **Priority Classifier**: Macro-F1 > 0.70
- **Domain Classifier**: Macro-F1 > 0.80

---

## 🔧 Customization

### Thêm Type Mới

Edit `requirement_analyzer/task_gen/generator_templates.py`:

```python
self.templates['custom_type'] = {
    'title_template': 'Your template here',
    'description_template': '...',
    'ac_templates': ['...']
}
```

### Thêm Role Mapping Rules

Edit `requirement_analyzer/task_gen/enrichers.py` → `RoleAssigner`:

```python
self.role_patterns['NewRole'] = [
    r'\bnew_keyword\b',
    r'\banother_pattern\b'
]
```

### Tune Deduplication Threshold

```python
from requirement_analyzer.task_gen import get_postprocessor

postprocessor = get_postprocessor(
    similarity_threshold=0.90,  # higher = less aggressive
    min_task_length=15
)
```

---

## 🎯 Use Cases

### 1. Jira/Trello Integration

```python
from requirement_analyzer.task_gen import get_pipeline

pipeline = get_pipeline()
response = pipeline.generate_tasks(requirement_doc)

# Export to Jira format
for task in response.tasks:
    jira_issue = {
        "summary": task.title,
        "description": task.description,
        "issuetype": {"name": "Story"},
        "priority": {"name": task.priority},
        "labels": [task.type, task.domain],
        "customfield_storypoints": task.story_points
    }
    # POST to Jira API...
```

### 2. Sprint Planning

```python
# Generate tasks
tasks = pipeline.generate_tasks(sprint_requirements)

# Group by priority and story points
high_priority = [t for t in tasks if t.priority == 'High']
total_points = sum(t.story_points for t in high_priority)

print(f"High priority: {len(high_priority)} tasks, {total_points} points")
```

### 3. Requirements Quality Check

```python
# Check requirement coverage
response = pipeline.generate_tasks(requirements_doc)

if response.total_tasks < 5:
    print("⚠️  Too few requirements detected. Document may be incomplete.")

low_confidence = [t for t in response.tasks if t.confidence < 0.5]
if low_confidence:
    print(f"⚠️  {len(low_confidence)} tasks have low confidence")
```

---

## 🐛 Troubleshooting

### Models not loading
```
⚠️  Task generation pipeline not available
```
**Fix**: Train models first using scripts 04 and 05.

### spaCy model error
```
OSError: Can't find model 'en_core_web_sm'
```
**Fix**: 
```bash
python -m spacy download en_core_web_sm
```

### Memory issues with large dataset
```
MemoryError during training
```
**Fix**: Use smaller chunksize or switch to `dataset_medium_100k`.

### Low task generation quality
**Fix**: 
1. Check data quality report
2. Increase training data size
3. Adjust confidence threshold in detection

---

## 📈 Roadmap

### Current (v1.0 - Template Mode)
- ✅ ML-based requirement detection
- ✅ Multi-class enrichment (type/priority/domain)
- ✅ Template-based generation
- ✅ Rule-based role assignment
- ✅ Deduplication & filtering

### Next (v1.1)
- [ ] RAG mode with LLM (optional)
- [ ] Fine-tuned role classifier
- [ ] Feedback loop with retraining
- [ ] Dependency detection between tasks

### Future (v2.0)
- [ ] Fine-tune T5 for text→JSON generation
- [ ] Multi-language support (Vietnamese)
- [ ] Integration with GitHub Issues, Azure DevOps
- [ ] Automated sprint planning

---

## 📚 Architecture Details

### Why Template-based First?

1. **Ổn định**: JSON luôn valid, không hallucinate
2. **Giải thích được**: Rule-based, dễ debug
3. **Nhanh**: Không cần LLM API calls
4. **Production-ready**: Chạy offline, không phụ thuộc external services

### Dataset Schema

```
text,is_requirement,type,priority,domain
"System shall...",1,functional,High,ecommerce
"Figure 3 shows...",0,non_requirement,none,general
```

- `is_requirement`: Binary (0/1)
- `type`: functional, security, interface, data, performance, etc.
- `priority`: Low, Medium, High, none
- `domain`: ecommerce, iot, healthcare, education, finance, general

---

## 🤝 Contributing

Cấu trúc code:

```
requirement_analyzer/
  task_gen/
    __init__.py           # Public API
    schemas.py            # Pydantic models
    segmenter.py          # Document → sentences
    req_detector.py       # Binary classifier
    enrichers.py          # Multi-class classifiers + role
    generator_templates.py # Template-based generation
    postprocess.py        # Dedupe + filter
    pipeline.py           # Orchestrator
```

Để thêm feature mới:
1. Tạo module trong `task_gen/`
2. Update `pipeline.py` để integrate
3. Thêm endpoint trong `api.py`
4. Viết test

---

## 📞 Support

Nếu gặp issue:
1. Check logs: `requirement_analyzer.api` logger
2. Verify models loaded: `GET /health`
3. Test với small document trước

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-20  
**Maintained by**: AI-Project Team
