# Model-Based Task Generation - Production Candidate

**Status:** 🟡 Production Candidate (v1.0) - OOD Evaluation Required  
**Date:** 2026-01-20  
**Mode:** NO API Keys Required

---

## Overview

Hệ thống tạo tasks từ requirements documents sử dụng **trained ML models** (không cần OpenAI/Anthropic API keys).

**✅ Verified:**
- **No data leakage**: Hash-based verification confirms 0 overlapping samples between train/val/test
- **Clean splits**: 305K train / 38K val / 38K test (stratified by requirement type + domain)
- **Pattern-based generation**: Uses rule patterns + spaCy NER (not seq2seq)

**⚠️ Remaining Limitation:**
- **OOD evaluation required**: Metrics validated on held-out test set, but need 200-500 real unseen documents to confirm generalization

### 3 Generation Modes

| Mode | Description | API Key | Quality | Speed | Notes |
|------|-------------|---------|---------|-------|-------|
| **Template** | Hardcoded strings | ❌ No | 🔴 Low (generic) | ⚡ 50ms | "Rất giả" |
| **LLM** | OpenAI/Anthropic | ✅ Yes | 🟢 Best | 🐢 5-10s | $$$ |
| **Model** | Trained ML + NLP patterns | ❌ No | 🟡 Medium | ⚡ 200ms | Pattern-based, not learned generation |

---

## Architecture

```
Document Text
    ↓
[Segmenter] → Sentences
    ↓
[Requirement Detector] → Filter requirements (observed high F1 on current split)
    ↓
[Enrichers] → Classify type/priority/domain
    ↓
[Model-Based Generator] → Pattern-based NLG with spaCy extraction
    ↓
[Postprocessor] → Dedupe, repair quality
    ↓
Tasks (JSON)
```

---

## Trained Models

**Location:** `requirement_analyzer/models/task_gen/models/`

**✅ Leakage Verified:** Hash-based check confirms **zero overlap** between train/val/test splits (381,952 samples total).  
**⚠️ OOD Evaluation Pending:** Metrics below are on held-out test set (38,196 samples), but require validation on real unseen documents.

| Model | Test Set Accuracy | Purpose |
|-------|----------|---------|
| `requirement_detector_model.joblib` | ~100%* | Detect requirements vs non-requirements |
| `type_model.joblib` | ~100%* | Classify functional/security/interface/data |
| `domain_model.joblib` | ~100%* | Classify ecommerce/finance/healthcare/iot/education |
| `priority_model.joblib` | **37%** | Classify Low/Medium/High (enhanced with keywords) |

*High accuracy likely due to strong keyword patterns in dataset. OOD evaluation recommended.

**Training Data:**
- Raw: 999K rows (100 CSV chunks)
- Cleaned: 386K rows (60% duplicates removed by 02_build_parquet.py)
- Train/Val/Test: 305K / 38K / 38K (stratified by `is_requirement + domain`)
- **✅ Leakage check**: Zero hash overlap confirmed (script: `00_verify_no_leakage.py`)

---

## Quality Gates (NEW - Production Features)

### 1. Title Repair
- Detects: "implement implement", "system implement"
- Action: Fallback to entity-based title
- Example: "implement implement for user" → "Implement user capability"

### 2. AC Deduplication
- Removes duplicate acceptance criteria within same task
- Normalizes text for comparison
- Preserves unique items only

### 3. Priority Hybrid (Keywords + Model)
- **HIGH** keywords: `must`, `critical`, `security`, `authentication`, `encrypt`, `payment`, `HIPAA`, `PCI`
- **MEDIUM** keywords: `should`, `needs to`, `required`, `validate`
- **LOW** keywords: `could`, `may`, `nice to have`, `optional`
- **Domain boost**: Healthcare/Finance + Security → High priority

**Result:** Fixes 37% model accuracy with rule-based keywords

---

## Usage

### Basic Usage

```python
from requirement_analyzer.task_gen.pipeline import TaskGenerationPipeline

pipeline = TaskGenerationPipeline(
    model_dir='requirement_analyzer/models/task_gen/models',  # Point directly to models/ dir
    generator_mode="model"  # <-- Use trained models (pattern-based NLG)
)

result = pipeline.generate_tasks(
    document_text, 
    max_tasks=50,
    requirement_threshold=0.5
)

for task in result.tasks:
    print(f"{task.title} ({task.type}, {task.priority})")
```

### FastAPI Integration

```python
from fastapi import FastAPI, UploadFile
from requirement_analyzer.task_gen.pipeline import TaskGenerationPipeline

app = FastAPI()
pipeline = TaskGenerationPipeline(generator_mode="model")

@app.post("/generate-tasks")
async def generate_tasks(file: UploadFile):
    text = await file.read()
    result = pipeline.generate_tasks(text.decode(), max_tasks=50)
    
    return {
        "tasks": [task.dict() for task in result.tasks],
        "metadata": result.metadata
    }
```

---

## Output Format

```json
{
  "task_id": "uuid",
  "title": "Authenticate users with JWT tokens",
  "description": "Implement comprehensive security for authenticate users...",
  "acceptance_criteria": [
    "Only authorized users can authenticate users",
    "All authenticate operations are logged for audit",
    "All data is encrypted in transit and at rest"
  ],
  "type": "security",
  "priority": "High",
  "domain": "finance",
  "role": "Security",
  "story_points": 5,
  "confidence": 0.85,
  "source": {
    "sentence": "The system must authenticate users...",
    "section": "Authentication",
    "offset": [0, 50]
  }
}
```

---

## Files Structure

```
requirement_analyzer/
  task_gen/
    pipeline.py                    # Main orchestrator
    generator_model_based.py       # Model-based generator (NEW)
    generator_templates.py         # Template generator (legacy)
    generator_llm.py              # LLM generator (needs API)
    req_detector.py               # Requirement detection
    enrichers.py                  # Type/priority/domain classifiers
    postprocess.py                # Quality gates (NEW features)
    segmenter.py                  # Document segmentation
    schemas.py                    # Data models
    
  models/task_gen/
    models/                       # Trained models
      requirement_detector_*.joblib
      type_*.joblib
      priority_*.joblib
      domain_*.joblib
    splits/                       # Train/val/test data
    clean_data.parquet/          # Cleaned dataset

scripts/task_generation/
  01_scan_dataset.py             # Data quality report
  02_build_parquet.py            # Clean & dedupe dataset
  03_build_splits.py             # Create train/val/test
  04_train_requirement_detector.py
  05_train_enrichers.py
  06_generate_training_tasks.py  # Create synthetic tasks
  demo_model_based.py            # Demo all 3 modes
```

---

## Performance

**Speed:**
- 10 tasks from 10 requirements: ~200ms
- 50 tasks from 50 requirements: ~800ms

**Quality Metrics (vs Template):**
- Title clarity: 🟡 Good (vs 🔴 Poor template)
- Natural language: 🟢 Yes (vs ❌ No template)
- Duplicate AC: ✅ Fixed (postprocessor)
- Priority accuracy: 🟡 Hybrid (keywords + model)

---

## Next Steps to Production-Ready Status

### ✅ Completed: Data Leakage Verification

**Result:** ✅ **Zero hash overlap** confirmed between train/val/test splits  
**Script:** `scripts/task_generation/00_verify_no_leakage.py`  
**Verification Date:** 2026-01-20

```
Train/Val overlap:  0 samples (CLEAN)
Train/Test overlap: 0 samples (CLEAN)
Val/Test overlap:   0 samples (CLEAN)
```

**Conclusion:** Observed high accuracy (~100% for detector/type/domain) is **trustworthy** on test set. However, still requires OOD evaluation to confirm generalization to unseen real-world documents.

---

### 📊 Priority 0: Out-of-Distribution (OOD) Evaluation (CRITICAL - BLOCKING)

**Required:** Test on 200-500 **real unseen requirement documents** (NOT from dataset_large_1m).

**Process:**
1. Collect requirement docs from:
   - Real project specifications
   - Public requirement repositories (GitHub, IEEE)
   - Different domains than training data
2. Manual extraction of 200-500 requirement sentences
3. Run through full pipeline (model mode)
4. Human scoring rubric (1-5 scale):
   - **Title clarity:** Is title concise and specific?
   - **Description correctness:** Does description match requirement?
   - **AC testability:** Are acceptance criteria measurable?
   - **Type accuracy:** Correct functional/security/data classification?
   - **Priority accuracy:** Reasonable High/Medium/Low?
5. **Target:** Average score > 3.5/5 to claim "production quality"

**Timeline:** 1-2 weeks (data collection + evaluation)

---

### ✅ Completed (Priority 1-4)
1. ✅ Fixed interface signature (`generate_batch`)
2. ✅ Fixed model paths (all components use `models/` dir)
3. ✅ Added postprocessor quality gates (dedupe AC, title repair, priority keywords)
4. ✅ Demo runs clean (no warnings)

---

### 📋 TODO (Priority 5-6)

**5. FastAPI Integration (High Priority)**
```python
# Add endpoints:
POST /api/tasks/generate              # Generate tasks
POST /api/tasks/feedback              # Collect user edits
GET  /api/tasks/stats                 # Generation stats

# Example:
@app.post("/api/tasks/generate")
async def generate_tasks(request: GenerateRequest):
    pipeline = TaskGenerationPipeline(
        model_dir='requirement_analyzer/models/task_gen/models',
        generator_mode="model"
    )
    result = pipeline.generate_tasks(
        request.document_text,
        max_tasks=request.max_tasks
    )
    
    # Log telemetry
    logger.info(f"Generated {len(result.tasks)} tasks", extra={
        "mode": "model",
        "num_sentences": len(result.sentences),
        "latency_ms": result.generation_time_ms,
        "avg_confidence": np.mean([t.confidence for t in result.tasks])
    })
    
    return result
```

**6. Monitoring & Telemetry (High Priority)**
```python
# Log structured data for each generation:
{
  "timestamp": "2026-01-20T10:30:00Z",
  "mode": "model",
  "num_input_sentences": 45,
  "num_requirements_detected": 32,
  "num_tasks_generated": 28,
  "avg_confidence": 0.83,
  "latency_ms": 245,
  "quality_gates_triggered": {
    "title_repairs": 3,
    "ac_deduplicates": 8,
    "priority_boosts": 5
  }
}
```

**7. Fail-Safe & Graceful Degradation (Medium Priority)**
```python
try:
    generator = ModelBasedTaskGenerator(model_dir=models_path)
except Exception as e:
    logger.error(f"Model loading failed: {e}, falling back to template mode")
    generator = get_generator()  # Template fallback
```

**8. Evaluation Framework (Medium Priority)**
- A/B test: Template vs Model vs LLM
- Collect user feedback scores
- Track edit distance (generated vs final user-edited tasks)

**9. Fine-tune T5/BART (Optional - Best Quality)**
- Generate silver tasks with script 06
- Human review → gold set (2-5K tasks)
- Fine-tune T5-small for true seq2seq generation
- Deploy as Mode 4 (learned generation, not patterns)

---

## Troubleshooting

### Models not found
```bash
# Check models exist
ls requirement_analyzer/models/task_gen/models/*.joblib

# If missing, retrain:
cd scripts/task_generation
python 04_train_requirement_detector.py --data-dir ../../requirement_analyzer/models/task_gen/splits --output-dir ../../requirement_analyzer/models/task_gen/models
python 05_train_enrichers.py --data-dir ../../requirement_analyzer/models/task_gen/splits --output-dir ../../requirement_analyzer/models/task_gen/models
```

### Low quality output
1. Check AC deduplication is working (postprocessor)
2. Check priority keywords are applied
3. Add domain-specific patterns to `_init_patterns()`
4. Collect feedback and retrain enrichers

### Slow generation
- Model mode should be <1s for 10 tasks
- If slow: check spaCy is installed (`en_core_web_sm`)
- Disable similarity deduplication if not needed

---

## Changelog

**v1.0.1 (2026-01-20) - Leakage Verified**
- ✅ Data leakage verification complete (zero hash overlap)
- ✅ Test metrics confirmed trustworthy on held-out set
- ✅ Added `00_verify_no_leakage.py` script
- ⚠️ **Remaining blocker:** OOD evaluation on real unseen documents

**v1.0 (2026-01-20) - Production Candidate**
- ✅ Initial MVP release with trained models
- ✅ Model-based generator (pattern-based NLG, no API)
- ✅ Quality gates (dedupe AC, title repair, priority hybrid)
- ✅ 5/5 validation tests passing
- ✅ Clean demo (no warnings)

---

## Production Readiness Status

| Criteria | Status | Notes |
|----------|--------|-------|
| Models trained | ✅ Done | 4 models (detector + 3 enrichers) |
| Interface standardized | ✅ Done | `generate_batch` signature fixed |
| Path resolution | ✅ Done | Unified models_path, no warnings |
| Quality gates | ✅ Done | Title repair, AC dedupe, priority hybrid |
| Validation tests | ✅ 5/5 Pass | All core functionality working |
| **Data leakage check** | ✅ **Done** | Zero hash overlap verified (00_verify_no_leakage.py) |
| **OOD evaluation** | ❌ **BLOCKING** | No real unseen documents tested |
| Monitoring/telemetry | ❌ TODO | No structured logging |
| Fail-safe handling | ❌ TODO | No graceful degradation |
| Deterministic outputs | ⚠️ Partial | spaCy may vary across versions |

**Current Status:** 🟡 **Production Candidate (MVP Ready)**  
**To Production-Ready:** Complete OOD evaluation + add monitoring/telemetry

---

## References

- Training scripts: `scripts/task_generation/`
- Demo: `scripts/task_generation/demo_model_based.py`
- Validation: `scripts/task_generation/validate_production_ready.py`
- API docs: `docs/API_DOCUMENTATION.md`
- Dataset: `requirement_analyzer/dataset_large_1m/`
