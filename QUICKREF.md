# Quick Reference - Production Infrastructure

## 🚀 Start API Server

```bash
cd /home/dtu/AI-Project/AI-Project
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit: http://localhost:8000/docs

## 📡 API Endpoints

### Generate Tasks
```bash
curl -X POST http://localhost:8000/api/tasks/generate \
  -H "Content-Type: application/json" \
  -d '{"document_text": "Your requirement text...", "mode": "model"}'
```

### Submit Feedback
```bash
curl -X POST http://localhost:8000/api/tasks/feedback \
  -H "Content-Type: application/json" \
  -d '{"generated_task": {...}, "rating": 5}'
```

### Get Statistics
```bash
curl http://localhost:8000/api/tasks/stats?days=7
```

## 🗄️ Data Crawling

### Jira
```bash
python scripts/data_pull/pull_jira.py
# Output: data/external/jira_issues_YYYYMMDD_HHMMSS.jsonl
```

### Trello
```bash
python scripts/data_pull/pull_trello.py
# Output: data/external/trello_cards_YYYYMMDD_HHMMSS.jsonl
```

### Clean & Merge
```bash
python scripts/data_pull/clean_and_merge.py \
  data/external/jira_*.jsonl \
  data/external/trello_*.jsonl
# Output: data/external/tasks_corpus.jsonl
```

## 📊 OOD Evaluation

### Step 1: Generate
```bash
python scripts/eval/01_generate_ood_outputs.py \
  scripts/eval/ood_requirements_template.csv \
  scripts/eval/ood_generated.csv
```

### Step 2: Manual Scoring
Open `ood_generated.csv` and fill `score_*` columns

### Step 3: Report
```bash
python scripts/eval/02_summarize_ood_scores.py \
  scripts/eval/ood_generated.csv
# Output: docs/OOD_REPORT.md
```

## 🧪 Test Infrastructure
```bash
./test_infrastructure.sh
```

## 📝 Check Logs
```bash
tail -f logs/api_$(date +%Y%m%d).log
```

## 📚 Documentation

- [docs/PRODUCTION_INFRASTRUCTURE.md](docs/PRODUCTION_INFRASTRUCTURE.md) - Complete guide
- [docs/IMPLEMENTATION_SUMMARY_VI.md](docs/IMPLEMENTATION_SUMMARY_VI.md) - Vietnamese summary
- http://localhost:8000/docs - API docs (when running)

## 🔧 Configuration

1. Copy: `cp .env.example .env`
2. Edit: `nano .env`
3. Fill credentials for Jira/Trello (optional)

## ⚠️ Known Issues

**Numpy version conflict:** If API won't start, run:
```bash
pip install --upgrade numpy scipy scikit-learn
```

## 📊 Files Created

- `app/routers/tasks.py` - 4 endpoints
- `app/middleware/logging.py` - JSON logging
- `scripts/data_pull/pull_jira.py` - Jira crawler
- `scripts/data_pull/pull_trello.py` - Trello crawler
- `scripts/data_pull/clean_and_merge.py` - Data cleaner
- `scripts/eval/01_generate_ood_outputs.py` - OOD generation
- `scripts/eval/02_summarize_ood_scores.py` - OOD reporting
- `.env.example` - Config template
- `test_infrastructure.sh` - Test script

Total: ~2600 lines of production code
