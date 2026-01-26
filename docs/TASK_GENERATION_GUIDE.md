# AI Task Generation Feature

## Overview

The AI Task Generation feature automatically converts software requirements into structured user stories and tasks using trained machine learning models. This feature uses a **hybrid approach** combining ML-based classification with pattern-based natural language generation.

## Architecture

### System Components

```
Input Requirements
    ↓
┌─────────────────────────────────────────┐
│  1. Segmentation (spaCy)                │
│     - Split into sentences              │
│     - Clean and normalize               │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  2. Requirement Detection (ML)          │
│     - TF-IDF + Linear Classifier        │
│     - Filter non-requirements           │
│     - Threshold: 0.5 (configurable)     │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  3. Enrichment (ML Classifiers)         │
│     - Type: functional, security, etc.  │
│     - Priority: high, medium, low       │
│     - Domain: finance, healthcare, etc. │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  4. Task Generation (Pattern-based)     │
│     - Entity extraction (spaCy)         │
│     - Title generation (verb + object)  │
│     - Description composition           │
│     - Acceptance criteria generation    │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  5. Post-processing                     │
│     - Deduplication                     │
│     - Quality filtering                 │
│     - Story point estimation            │
└─────────────────────────────────────────┘
    ↓
Structured User Stories (JSON/CSV)
```

## Features

### ✅ What This System Does

1. **Automatic Requirements Detection**
   - Filters out non-requirement sentences (descriptions, notes, etc.)
   - Uses trained ML classifier with 85%+ accuracy

2. **Intelligent Classification**
   - **Type**: functional, security, performance, interface, data, integration
   - **Priority**: high, medium, low (based on keywords and patterns)
   - **Domain**: finance, healthcare, ecommerce, etc.

3. **Natural Task Generation**
   - Extracts entities (actions, objects) from requirements
   - Generates descriptive titles (not generic)
   - Creates user stories in standard format: "As a [role], I want to [action], so that [benefit]"
   - Generates 3-6 acceptance criteria per task

4. **Quality Controls**
   - Generic title detection (flags "capability", "functionality", etc.)
   - Duplicate acceptance criteria removal
   - Intent verification (keywords must match)
   - Story point estimation (1-13 scale)

### ⚠️ Current Limitations

1. **Generic Titles**: ~60% of titles contain generic terms (e.g., "Build user login capability")
   - **Fix in progress**: Use spaCy ROOT verb + direct object instead of fallback patterns
   - **Target**: Reduce to 25-30%

2. **Coverage**: 73.6% of requirements generate tasks
   - **Reason**: Strict requirement detector threshold (0.5)
   - **Improvement**: Lower threshold to 0.3 or add regex fallback

3. **Pattern-based Generation**: Not fully natural language
   - Uses rule-based templates with entity slots
   - Alternative: LLM mode (requires API key) or fine-tuned seq2seq model

## Usage

### 1. Web UI

Access the task generation interface at: **http://localhost:8000/task-generation**

#### Features:
- **Text Input**: Paste requirements (one per line)
- **File Upload**: Upload .txt, .md, .docx, .pdf files
- **Live Preview**: See generated tasks with expandable cards
- **Filters**: Filter by type (functional, security, etc.)
- **Export**: Download as JSON or CSV
- **Quick Examples**: Pre-loaded examples for e-commerce, auth, healthcare

### 2. API Endpoints

#### Generate Tasks from Text
```bash
POST /api/task-generation/generate
Content-Type: application/json

{
  "text": "The system must allow users to login with email and password.\nThe application shall send password reset emails.",
  "max_tasks": 50,
  "requirement_threshold": 0.5,
  "epic_name": "Authentication Module",
  "domain_hint": "security"
}
```

**Response:**
```json
{
  "tasks": [
    {
      "title": "Implement user login authentication",
      "description": "The system needs to implement user authentication using email and password credentials...",
      "type": "security",
      "priority": "high",
      "domain": "authentication",
      "role": "user",
      "story_points": 5,
      "acceptance_criteria": [
        "User can enter email and password",
        "System validates credentials against database",
        "Invalid credentials show error message",
        "Successful login redirects to dashboard"
      ]
    }
  ],
  "total_sentences": 2,
  "requirements_detected": 2,
  "filtered_count": 0,
  "processing_time": 0.45
}
```

#### Generate from File
```bash
POST /api/task-generation/generate-from-file
Content-Type: multipart/form-data

file: <requirements.txt>
max_tasks: 50
```

#### Check Status
```bash
GET /api/task-generation/status
```

**Response:**
```json
{
  "available": true,
  "mode": "model",
  "generator_class": "ModelBasedTaskGenerator",
  "message": "Task generation ready (mode: model)"
}
```

### 3. Python API

```python
from requirement_analyzer.task_gen import get_pipeline

# Initialize pipeline (uses model mode by default)
pipeline = get_pipeline()

# Generate tasks
result = pipeline.generate_tasks(
    text="""
    The system must verify user identity through two-factor authentication.
    Users should be able to reset their password via email link.
    The application shall log all authentication attempts.
    """,
    max_tasks=50,
    requirement_threshold=0.5
)

# Access results
for task in result.tasks:
    print(f"Title: {task.title}")
    print(f"Type: {task.type}, Priority: {task.priority}")
    print(f"Description: {task.description}")
    print(f"Acceptance Criteria: {task.acceptance_criteria}")
    print(f"Story Points: {task.story_points}")
    print("---")
```

## Configuration

### Generator Modes

Set via environment variable `TASK_GEN_MODE`:

1. **model** (default) - Uses trained ML models
   - No API key required
   - Fast (100ms per requirement)
   - Deterministic output
   - Pattern-based generation

2. **template** - Simple rule-based templates
   - Fastest option
   - Most generic output
   - Fallback if models not available

3. **llm** - LLM-based generation (OpenAI/Anthropic)
   - Requires API key
   - Most natural language
   - Higher cost (~$0.001 per task)
   - Variable output

```bash
# Use model mode (default)
python -m requirement_analyzer.api

# Use LLM mode
export TASK_GEN_MODE=llm
export OPENAI_API_KEY=sk-...
python -m requirement_analyzer.api
```

### Detection Threshold

Control how strict requirement detection is:

```python
# Strict (default): only clear requirements pass
result = pipeline.generate_tasks(text=..., requirement_threshold=0.5)

# Lenient: catches more potential requirements
result = pipeline.generate_tasks(text=..., requirement_threshold=0.3)
```

## Model Files

Required model files (located in `requirement_analyzer/models/task_gen/models/`):

```
requirement_detector_model.joblib        # Requirement vs non-requirement classifier
requirement_detector_vectorizer.joblib   # TF-IDF vectorizer for detector

type_model.joblib                        # Type classifier (functional, security, etc.)
type_vectorizer.joblib                   # TF-IDF vectorizer for type

priority_model.joblib                    # Priority classifier (high, medium, low)
priority_vectorizer.joblib               # TF-IDF vectorizer for priority

domain_model.joblib                      # Domain classifier (finance, healthcare, etc.)
domain_vectorizer.joblib                 # TF-IDF vectorizer for domain
```

All models are **trained** (not rule-based) using TF-IDF + LinearSVC on 1M+ sentences from multiple datasets.

## Production Status

### ✅ Production-Grade Infrastructure

- API endpoints with proper error handling
- Logging and telemetry
- File upload support
- Export to JSON/CSV
- Configurable thresholds
- OOD evaluation framework
- Manual scoring rubric

### ⚠️ Quality Improvements Needed

- **Generic titles**: 60% → target 25-30%
- **Coverage**: 73.6% → target 80-85%
- **Manual pilot scoring**: Required before full deployment

### Recommendation

**Current Status**: **Production Candidate** (not yet "Production Ready")

**Gate**: Complete manual pilot scoring (50 rows) using OOD_SCORING_RUBRIC.md
- If avg_quality ≥ 3.5 → proceed to full evaluation
- If avg_quality < 3.2 → fix generic titles first

## Roadmap

### Phase 1: Current (Model-based)
- ✅ ML classifiers for detection + enrichment
- ✅ Pattern-based NLG for generation
- ✅ Web UI + API
- ⏳ Manual pilot scoring
- ⏳ Title quality fixes

### Phase 2: Quality Improvements
- [ ] Fix generic titles (spaCy ROOT verb + dobj)
- [ ] Improve coverage (lower threshold + regex fallback)
- [ ] Add pre-scoring automation
- [ ] Full OOD evaluation (250 rows)

### Phase 3: LLM Integration (Optional)
- [ ] LLM mode with schema guardrails
- [ ] Fine-tune seq2seq model on gold dataset
- [ ] Hybrid mode (ML + LLM for refinement)

## Testing

Run the test script to verify configuration:

```bash
./test_task_generation.sh
```

Expected output:
```
✓ Model directory exists
✓ Found 8 .joblib files
✓ Pipeline initialized
✓ Generator mode: model
✓ Generated 1 task(s)
```

## Examples

See the web UI for interactive examples:
- E-commerce System
- Authentication Module
- Healthcare Application

## Support

For issues or questions:
1. Check API logs: `/tmp/api_log.txt`
2. Verify models exist: `ls requirement_analyzer/models/task_gen/models/*.joblib`
3. Test configuration: `./test_task_generation.sh`
4. Review OOD evaluation results: `docs/OOD_EVALUATION_REPORT.pdf`

## Credits

Developed as part of AI-powered Software Effort Estimation system.
Uses spaCy for NLP, scikit-learn for ML, and FastAPI for serving.
