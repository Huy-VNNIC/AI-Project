# Production Infrastructure - Complete Guide

## 🎯 Overview

Complete production infrastructure for task generation system including:
- ✅ FastAPI REST endpoints
- ✅ Structured JSON logging
- ✅ Feedback collection database
- ✅ Jira/Trello data crawling
- ✅ OOD evaluation framework

---

## 📁 Structure

```
AI-Project/
├── app/
│   ├── main.py                    # FastAPI application
│   ├── routers/
│   │   └── tasks.py               # Task generation endpoints
│   └── middleware/
│       └── logging.py             # Structured logging
├── scripts/
│   ├── data_pull/
│   │   ├── pull_jira.py          # Jira API integration
│   │   ├── pull_trello.py        # Trello API integration
│   │   └── clean_and_merge.py    # Data cleaning pipeline
│   └── eval/
│       ├── ood_requirements_template.csv
│       ├── 01_generate_ood_outputs.py
│       └── 02_summarize_ood_scores.py
├── data/
│   ├── external/                  # Crawled data (Jira/Trello)
│   └── feedback.db                # Feedback database
├── logs/                          # Structured logs
└── .env                           # Configuration (copy from .env.example)
```

---

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Required variables:**
```env
# Jira
JIRA_BASE_URL=https://your-company.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your-api-token

# Trello
TRELLO_API_KEY=your-api-key
TRELLO_TOKEN=your-token
TRELLO_BOARD_IDS=board1,board2

# API
API_HOST=0.0.0.0
API_PORT=8000
MODEL_DIR=requirement_analyzer/models/task_gen/models
```

### 2. Run API Server

```bash
# Start FastAPI server
cd /home/dtu/AI-Project/AI-Project
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**API will be available at:**
- http://localhost:8000 - Health check
- http://localhost:8000/docs - Interactive API docs (Swagger)
- http://localhost:8000/redoc - Alternative API docs

### 3. Test API

```bash
# Health check
curl http://localhost:8000/health

# Generate tasks
curl -X POST http://localhost:8000/api/tasks/generate \
  -H "Content-Type: application/json" \
  -d '{
    "document_text": "The system must authenticate users through email and password. Users should be able to reset their passwords.",
    "mode": "model",
    "max_tasks": 10
  }'

# Get statistics
curl http://localhost:8000/api/tasks/stats?days=7
```

---

## 📡 API Endpoints

### POST `/api/tasks/generate`

Generate tasks from requirement document.

**Request:**
```json
{
  "document_text": "The system must...",
  "mode": "model",  // or "template", "llm"
  "max_tasks": 50,
  "requirement_threshold": 0.5,
  "dedupe": true,
  "epic_name": "Sprint 23"
}
```

**Response:**
```json
{
  "tasks": [
    {
      "title": "Implement User Authentication",
      "description": "As a user, I want to...",
      "type": "Story",
      "priority": "High",
      "domain": "Security",
      "acceptance_criteria": [
        "User can log in with email/password",
        "System validates credentials",
        "Failed attempts are logged"
      ],
      "confidence": 0.98
    }
  ],
  "metadata": {
    "mode": "model",
    "num_sentences": 10,
    "num_requirements": 5,
    "num_tasks": 3,
    "latency_ms": 1250,
    "avg_confidence": 0.95,
    "quality_gates": {
      "title_repairs": 2,
      "ac_dedupes": 1,
      "priority_boosts": 0
    }
  }
}
```

### POST `/api/tasks/feedback`

Submit user feedback on generated tasks.

**Request:**
```json
{
  "task_id": "task_123",
  "generated_task": { /* original task */ },
  "final_task": { /* user-edited task */ },
  "rating": 4,
  "comment": "Good but priority was wrong",
  "session_id": "session_xyz"
}
```

**Response:**
```json
{
  "status": "success",
  "feedback_id": 42,
  "message": "Thank you for your feedback!"
}
```

### GET `/api/tasks/stats?days=7`

Get generation statistics.

**Response:**
```json
{
  "total_requests": 150,
  "avg_latency_ms": 1234.5,
  "avg_confidence": 0.89,
  "mode_distribution": {
    "model": 120,
    "template": 30
  },
  "quality_gates_summary": {
    "title_repairs": 45,
    "ac_dedupes": 12,
    "priority_boosts": 8
  }
}
```

### GET `/api/tasks/feedback/export?limit=1000`

Export feedback data for analysis.

**Response:**
```json
{
  "count": 150,
  "feedbacks": [
    {
      "id": 1,
      "timestamp": "2024-01-15T10:30:00",
      "task_id": "task_123",
      "generated_task": { /* ... */ },
      "final_task": { /* ... */ },
      "rating": 4,
      "comment": "...",
      "session_id": "..."
    }
  ]
}
```

---

## 🗄️ Data Crawling

### Pull from Jira

```bash
# Edit .env with Jira credentials
python scripts/data_pull/pull_jira.py
```

**Output:** `data/external/jira_issues_YYYYMMDD_HHMMSS.jsonl`

**Features:**
- Paginated search (handles large result sets)
- ADF (Atlassian Document Format) → plain text conversion
- Acceptance criteria extraction
- PII handling
- Standardized schema

**Example JQL queries (.env):**
```env
JIRA_JQL=project = ABC AND type IN (Story, Task) AND created >= -90d
```

### Pull from Trello

```bash
# Edit .env with Trello credentials
python scripts/data_pull/pull_trello.py
```

**Output:** `data/external/trello_cards_YYYYMMDD_HHMMSS.jsonl`

**Features:**
- Board card fetching
- Label/list/due date extraction
- Checklist parsing (acceptance criteria)
- Priority inference from labels
- Comment retrieval (optional)

### Clean and Merge

```bash
# Clean + deduplicate + merge Jira and Trello data
python scripts/data_pull/clean_and_merge.py \
  data/external/jira_issues_*.jsonl \
  data/external/trello_cards_*.jsonl
```

**Output:** `data/external/tasks_corpus.jsonl`

**Quality filters:**
- Minimum title length: 5 characters
- Minimum description length: 20 characters
- PII removal: emails → `[EMAIL]`, phones → `[PHONE]`
- Bot detection: Skip automated messages
- Hash-based deduplication

**Statistics reported:**
- Total raw, invalid, duplicates, cleaned
- Retention rate
- Breakdown by source, type, priority
- Quality metrics (with description %, with AC %, avg AC count)

---

## 📊 OOD Evaluation

**Purpose:** Validate model performance on real-world requirements from different domains.

### Step 1: Prepare Requirements

1. Open `scripts/eval/ood_requirements_template.csv`
2. Fill 200-500 rows with **real requirements**:
   ```csv
   id,domain_expected,requirement_sentence
   1,banking,"The system must verify user identity through 2FA"
   2,ecommerce,"Users should be able to add items to cart"
   3,healthcare,"Patient records must be encrypted at rest"
   ```

### Step 2: Generate Outputs

```bash
python scripts/eval/01_generate_ood_outputs.py \
  scripts/eval/ood_requirements_template.csv \
  scripts/eval/ood_generated.csv \
  --mode model
```

This will populate `generated_*` columns (title, description, type, priority, etc.)

### Step 3: Manual Scoring

Open `scripts/eval/ood_generated.csv` and score each row:

**Quality scores (1-5):**
- `score_title_clarity`: Is title clear and concise?
- `score_desc_correctness`: Does description match requirement?
- `score_ac_testability`: Are acceptance criteria testable?

**Label accuracy (0/1):**
- `score_label_type`: Is type label correct?
- `score_label_domain`: Is domain label correct?
- `score_priority_reasonable`: Is priority reasonable?

**Quality flags:**
- `has_duplicates`: Are there duplicate/redundant ACs? (0/1)
- `notes`: Free text comments

### Step 4: Generate Report

```bash
python scripts/eval/02_summarize_ood_scores.py \
  scripts/eval/ood_generated.csv \
  --output docs/OOD_REPORT.md
```

**Report includes:**
- Overall quality score (avg of title/desc/AC)
- Label accuracy (type, domain, priority)
- Duplicate rate
- Breakdown by domain
- Top 20 worst examples
- Pass/fail status
- Recommendations

**Pass criteria:**
- Overall quality ≥ 3.5/5
- Duplicate rate ≤ 10%
- Type accuracy ≥ 80%
- Domain accuracy ≥ 80%

---

## 📝 Logging

All requests are logged to `logs/api_YYYYMMDD.log` in structured JSON format.

**Example log entry:**
```json
{
  "timestamp": "2024-01-15T10:30:15.123456",
  "level": "INFO",
  "message": "Request completed: POST /api/tasks/generate - 200",
  "request_id": "1705315815123",
  "method": "POST",
  "path": "/api/tasks/generate",
  "status_code": 200,
  "duration_ms": 1234,
  "user_agent": "curl/7.68.0"
}
```

**Log fields:**
- `timestamp`: ISO 8601 timestamp
- `level`: INFO, WARNING, ERROR
- `request_id`: Unique request identifier
- `method`: HTTP method
- `path`: Request path
- `status_code`: HTTP status code
- `duration_ms`: Request duration
- `user_agent`: Client user agent

**Generation event logs:**
```json
{
  "timestamp": "2024-01-15T10:30:16",
  "level": "INFO",
  "message": "Task generation completed",
  "request_id": "1705315815123",
  "mode": "model",
  "num_sentences": 10,
  "num_requirements": 5,
  "num_tasks": 3,
  "latency_ms": 1200,
  "avg_confidence": 0.95,
  "quality_gates": {
    "title_repairs": 2,
    "ac_dedupes": 1,
    "priority_boosts": 0
  }
}
```

---

## 🔒 Security

### API Tokens

**Jira:**
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Create API token
3. Use email + token for authentication

**Trello:**
1. Get API key: https://trello.com/app-key
2. Generate token: Click "Token" link on API key page
3. Use API key + token for authentication

### Environment Variables

**Never commit `.env` to version control!**

```bash
# Add to .gitignore
echo ".env" >> .gitignore
```

### Rate Limiting

Configure in `.env`:
```env
RATE_LIMIT_PER_MINUTE=60
```

---

## 🧪 Testing

### Test API locally

```bash
# Test health
curl http://localhost:8000/health

# Test generation
curl -X POST http://localhost:8000/api/tasks/generate \
  -H "Content-Type: application/json" \
  -d @test_request.json

# Test feedback
curl -X POST http://localhost:8000/api/tasks/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "generated_task": {"title": "Test"},
    "rating": 5,
    "comment": "Excellent"
  }'

# Test stats
curl http://localhost:8000/api/tasks/stats
```

### Test data crawling

```bash
# Test Jira (dry run)
python scripts/data_pull/pull_jira.py --max-results 10

# Test Trello (dry run)
python scripts/data_pull/pull_trello.py --max-cards 10

# Test cleaning
python scripts/data_pull/clean_and_merge.py \
  data/external/jira_issues_test.jsonl
```

---

## 🚦 Production Checklist

### Before deploying:

- [ ] Configure `.env` with production credentials
- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Configure CORS for production origins
- [ ] Set up log rotation
- [ ] Run OOD evaluation (≥ 200 requirements)
- [ ] Pass OOD criteria (quality ≥ 3.5, accuracy ≥ 80%)
- [ ] Test API with production load
- [ ] Set up monitoring/alerting
- [ ] Document API for users
- [ ] Train team on feedback collection

### After deploying:

- [ ] Monitor logs for errors
- [ ] Track generation statistics
- [ ] Collect user feedback
- [ ] Analyze worst examples
- [ ] Retrain models with feedback data
- [ ] Re-run OOD evaluation quarterly

---

## 📊 Data Improvement Workflow

### 1. Crawl external data

```bash
python scripts/data_pull/pull_jira.py
python scripts/data_pull/pull_trello.py
python scripts/data_pull/clean_and_merge.py data/external/*.jsonl
```

Output: `data/external/tasks_corpus.jsonl` (clean, deduplicated tasks)

### 2. Use for model improvement

**Option A: Retrain priority model**
- Priority labels from real PM-tagged tasks
- Stronger signal than synthetic data
- Use `task_corpus.jsonl` as additional training data

**Option B: Fine-tune generator**
- Requirement → task pairs
- Learn BA writing style
- Use for RAG examples

**Option C: RAG at inference**
- Retrieve similar tasks
- Use as style examples
- Improve generation quality

### 3. Collect feedback

- Users submit corrections via `/api/tasks/feedback`
- Export feedback: `GET /api/tasks/feedback/export`
- Analyze common errors
- Retrain models with corrected data

### 4. Re-evaluate

- Run OOD evaluation with new data
- Compare metrics before/after
- Update production status if passed

---

## 🛠️ Troubleshooting

### API won't start

```bash
# Check models exist
ls requirement_analyzer/models/task_gen/models/

# Check dependencies
pip install -r requirements.txt

# Check port availability
lsof -i :8000
```

### Jira API errors

```bash
# Test credentials
curl -u your-email@company.com:your-token \
  https://your-company.atlassian.net/rest/api/3/myself

# Check JQL syntax
# In Jira UI: Filters → Advanced search → Test query
```

### Trello API errors

```bash
# Test credentials
curl "https://api.trello.com/1/members/me?key=YOUR_KEY&token=YOUR_TOKEN"

# Check board IDs
# In Trello: Open board → URL has board ID
```

### Low quality scores

1. Analyze worst examples in OOD report
2. Check common patterns (domain, type, etc.)
3. Retrain specific classifier
4. Improve generation prompts
5. Add more training data for weak categories

---

## 📞 Next Steps

1. **Fill `.env` with credentials**
2. **Start API:** `uvicorn app.main:app --reload`
3. **Test endpoints** (see Testing section)
4. **Pull data from Jira/Trello** (if available)
5. **Run OOD evaluation** (200-500 requirements)
6. **Review OOD report** (`docs/OOD_REPORT.md`)
7. **Deploy to production** (if passed OOD)

**For questions or issues:**
- Check logs: `logs/api_YYYYMMDD.log`
- Review API docs: http://localhost:8000/docs
- See examples: This guide

Good luck! 🚀
