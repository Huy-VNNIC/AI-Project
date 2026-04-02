# 🚀 Quick Start Guide - Rule-Based Test Case Generator

## ⚡ One-Command Setup

Choose **ONE** of these options to install and run the system:

### Option 1: Python (Recommended)
```bash
cd rule_based_system
python3 setup.py
```

### Option 2: Bash Script
```bash
cd rule_based_system
bash setup_and_run.sh
```

### Option 3: Manual Commands
```bash
cd rule_based_system
pip install -r requirements.txt
python3 -m spacy download en_core_web_sm
python3 quick_start.py
```

---

## 📊 What Happens on First Run

✅ **Step 1:** Installs all dependencies (FastAPI, spaCy, pandas, etc.)
✅ **Step 2:** Downloads spaCy NLP model
✅ **Step 3:** Runs demo with sample requirements
✅ **Step 4:** Generates 50+ test cases
✅ **Step 5:** Exports to 4 formats (JSON, CSV, Excel, Markdown)

**Result:** Sample test cases in `sample_output/`
- `test_cases.json` (JSON format)
- `test_cases.csv` (CSV format)
- `test_cases.xlsx` (Excel format)
- `test_cases.md` (Markdown format)

---

## 📂 File Structure

```
rule_based_system/
├── setup.py ................ One-command setup script
├── setup_and_run.sh ........ Bash setup script
├── quick_start.py .......... Demo script
├── main.py ................ REST API server
├── requirements.txt ........ Dependencies
├── models/
│   └── canonical.py ....... Data schemas
├── core/
│   ├── input_processor.py .. File extraction (PDF, DOCX, TXT, Excel)
│   ├── format_detector.py .. Auto-detect format
│   ├── text_preprocessor.py Code cleanup
│   ├── normalizer.py ...... Synonym mapping
│   ├── test_generator.py .. Rule engine
│   └── pipeline.py ........ Orchestrator
├── parsers/
│   ├── free_text_parser.py . NLP parsing
│   ├── user_story_parser.py User story "As a..."
│   ├── use_case_parser.py .. Structured use cases
│   └── excel_parser.py .... Excel/CSV table parsing
├── exports/
│   └── export_handler.py .. Multi-format export
└── sample_output/ ........ Generated test cases
```

---

## 🎯 Usage Examples

### 1. Run Demo (After Setup)
```bash
cd rule_based_system
python3 quick_start.py
```

### 2. Start REST API Server
```bash
cd rule_based_system
python3 main.py
# Open: http://localhost:8001/docs
```

### 3. Use as Python Library
```python
from rule_based_system import run_pipeline_from_text

result = run_pipeline_from_text("""
    User can login with email and password.
    System must validate email format.
""")

print(f"Generated {result['summary']['total_test_cases']} test cases")
for tc in result['test_cases'][:5]:
    print(f"  - {tc['title']}")
```

### 4. Process a File
```python
from rule_based_system import run_pipeline

result = run_pipeline("requirements.pdf")
print(f"Format: {result['format_detected']}")
print(f"Test cases: {result['summary']['total_test_cases']}")
```

### 5. Export to Different Formats
```python
from rule_based_system.exports.export_handler import export_all_formats

# Export to all 4 formats at once
export_all_formats(test_cases, "output/test_cases")
```

---

## 📊 System Output

### Quick Start Result (7 requirements)
```
✅ Processing Complete!
📊 Summary:
  - Format Detected: free_text
  - Total Requirements: 7
  - Total Test Cases: 53
  - Avg Tests per Requirement: 7.6

📋 Test Cases by Type:
  - Positive: 9
  - Negative: 15
  - Edge: 22
  - Security: 7
```

### Generated Test Example
```
[Positive] User logins email with valid inputs
  Type: positive | Priority: high
  Expected: can login with email and password

[Negative] User logins email - invalid email
  Type: negative | Priority: high
  Expected: System shows error: invalid email

[Edge] User logins email with maximum length email
  Type: edge | Priority: medium
  Expected: System handles long email gracefully
```

---

## 🌐 REST API (After `python3 main.py`)

### Health Check
```bash
curl http://localhost:8001/health
```

### Generate Test Cases from Text
```bash
curl -X POST http://localhost:8001/generate/text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "User can login with email and password",
    "format": "free_text"
  }'
```

### Upload File and Generate Tests
```bash
curl -X POST http://localhost:8001/generate \
  -F "file=@requirements.pdf"
```

### Download as Excel
```bash
curl -X POST http://localhost:8001/export/excel \
  -F "file=@requirements.pdf" \
  --output test_cases.xlsx
```

### View API Docs
Open browser: **http://localhost:8001/docs**

---

## 📋 Supported Input Formats

| Format | File Type | Parser |
|--------|-----------|--------|
| Free Text | TXT, PDF, DOCX | spaCy NLP |
| User Story | TXT, PDF, DOCX | Regex pattern |
| Use Case | TXT, PDF, DOCX | Header-based |
| Excel | XLSX, CSV | Fuzzy column matching |

---

## 🧪 Supported Test Types

| Test Type | Count | Purpose |
|-----------|-------|---------|
| **Positive** | 1 per req | Happy path validation |
| **Negative** | 2-3 per field | Error handling |
| **Edge** | Boundary values | Limit testing |
| **Security** | SQL, XSS, etc. | Security validation |
| **Performance** | Load testing | Performance validation |
| **Condition** | Per IF/WHEN | Condition coverage |

---

## 💾 Export Formats

| Format | Extension | Best For |
|--------|-----------|----------|
| **JSON** | .json | Programmatic use |
| **CSV** | .csv | Spreadsheet tools |
| **Excel** | .xlsx | Professional reports |
| **Markdown** | .md | Documentation |

---

## ⚙️ Configuration

### Change API Port
Edit `main.py` line 2:
```python
PORT = 8001  # Change this to 8002, 8003, etc.
```

### Add Custom Synonyms
Edit `core/normalizer.py`:
```python
ACTION_SYNONYMS["new_action"] = "canonical_form"
SECURITY_SIGNALS.add("new_keyword")
```

---

## 🐛 Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'spacy'`
**Solution:**
```bash
pip install -r requirements.txt
python3 -m spacy download en_core_web_sm
```

### Issue: Port 8001 already in use
**Solution:** Change port in `main.py` (line 2), then restart

### Issue: "No such file or directory"
**Solution:** Make sure you're in the `rule_based_system/` directory

### Issue: spaCy model not found
**Solution:**
```bash
python3 -m spacy download en_core_web_sm
```

---

## 📚 Full Documentation

See **README.md** for:
- Complete architecture explanation
- Module-by-module reference
- Data model definitions
- Test generation rules table
- Integration examples
- Advanced usage

---

## ✨ Key Features

✅ **No External APIs** - Completely offline
✅ **Deterministic** - Same input = same output
✅ **Rule-Based** - Transparent, explainable
✅ **Fast** - Instant test generation
✅ **Comprehensive** - 5 test types per requirement
✅ **Multi-Format** - 4 export formats
✅ **REST API** - Easy integration
✅ **Production-Ready** - Full error handling

---

## 🎓 Learning Path

**Beginner:** Run `python3 setup.py` to see it work
**Intermediate:** Modify `quick_start.py` with your requirements
**Advanced:** Build REST API wrapper or database backend

---

## 💡 Tips

- Use `quick_start.py` to test with sample data
- Use REST API (port 8001) for production
- Export to Excel for stakeholder reports
- Export to CSV for test management tools
- Export to JSON for programmatic access

---

## 🆘 Need Help?

1. **Check output:** `sample_output/` folder after running
2. **Check logs:** Look at terminal output for errors
3. **Read docs:** See `README.md` for detailed information
4. **Test API:** Visit http://localhost:8001/docs

---

**Ready? Just run one command and you're done! 🚀**

```bash
python3 setup.py
```
