# 🚀 Getting Started - Rule-Based Test Case Generator

> **Quick start guide to run your system in 5 minutes**

## ⚡ Super Quick Start (Recommended)

```bash
# 1. Install dependencies (one time)
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 2. Run the test suite (verify everything works)
cd rule_based_testgen
python test_system.py

# 3. Start the API server
python main.py

# 4. Open in browser: http://localhost:8000/docs
```

That's it! Your system is running.

---

## 📋 Step-by-Step Setup

### Step 1: Install Dependencies

```bash
cd rule_based_testgen

# Install Python packages
pip install -r requirements.txt

# Download spaCy English model (required for NLP)
python -m spacy download en_core_web_sm
```

**What gets installed:**
- FastAPI (web API framework)
- spaCy (natural language processing)
- pdfplumber (PDF extraction)
- python-docx (Word document parsing)
- openpyxl (Excel export)

### Step 2: Verify Installation

```bash
python test_system.py
```

Expected output:
```
==============================================================================
🧪 TESTING RULE-BASED TEST CASE GENERATOR
==============================================================================

✓ Testing imports...
  ✓ Pipeline imported

✓ Initializing pipeline...
  ✓ Pipeline initialized

✓ Processing requirements...
  ✓ Processing complete
  - Requirements found: 7
  - Test cases generated: 28

✅ ALL TESTS PASSED!
```

If you see errors, check:
- Python 3.8+ installed: `python --version`
- All dependencies installed: `pip list | grep -i fastapi`
- spaCy model downloaded: `python -c "import spacy; spacy.load('en_core_web_sm')"`

### Step 3: Start the API Server

```bash
python main.py
```

Expected output:
```
Uvicorn running on http://127.0.0.1:8000
Press CTRL+C to quit
```

### Step 4: Access the API

**Interactive API docs:**
- Open browser: http://localhost:8000/docs
- Or: http://localhost:8000/redoc

**Try it out:**
1. Click on a green endpoint (e.g., `POST /api/generate`)
2. Click **Try it out**
3. Paste sample requirements in the text box
4. Click **Execute**

---

## 🧪 Test APIs Without Browser

### Test 1: Generate from Text

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "requirements_text": "User can login with email and password. System must validate email format.",
    "export_format": "json"
  }' | jq .
```

### Test 2: Generate from File

```bash
# With sample requirements
curl -X POST http://localhost:8000/api/generate-file \
  -F "file=@sample_requirements.txt" \
  -F "export_format=excel" \
  -o test_output.xlsx

# Check file was created
ls -lh test_output.xlsx
```

### Test 3: Health Check

```bash
curl http://localhost:8000/health
# Returns: {"status": "healthy"}
```

### Test 4: System Stats

```bash
curl http://localhost:8000/api/stats | jq .
```

---

## 📝 Using with Your Own Requirements

### Option 1: Text Input

Create a text file `my_requirements.txt`:
```
# Login Requirements
- User can sign in with email and password
- System must validate email format
- If login fails, show error message
- Password must be at least 8 characters

# Product Management
- Admin can create product
- System must check inventory
- When product is unavailable, show "out of stock"
```

Then use the API:
```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "requirements_text": "'"$(cat my_requirements.txt)"'",
    "export_format": "excel"
  }' -o my_tests.xlsx
```

### Option 2: File Upload

```bash
# Upload file and get Excel output
curl -X POST http://localhost:8000/api/generate-file \
  -F "file=@my_requirements.txt" \
  -F "export_format=excel" \
  -o results.xlsx

# Or get JSON output
curl -X POST http://localhost:8000/api/generate-file \
  -F "file=@my_requirements.txt" \
  -F "export_format=json" | jq .
```

### Option 3: Python Script

```python
from pipeline import TestGenerationPipeline

# Create pipeline
pipeline = TestGenerationPipeline()

# Process file
results = pipeline.process_file(
    filepath="my_requirements.txt",
    output_format="excel",
    export_path="tests.xlsx"
)

print(f"Generated {results['summary']['total_test_cases']} test cases")
print(f"Export: {results['export_file']}")
```

---

## 📊 Output Formats

The system can export to:

### JSON Output
```json
{
  "requirements": [{
    "requirement_id": "REQ-001",
    "actor": "user",
    "action": "login",
    "type": "functional",
    "domain": "general"
  }],
  "test_cases": [{
    "test_id": "REQ-001-POS-001",
    "title": "User successfully logs in with valid credentials",
    "test_type": "positive",
    "steps": ["Enter email", "Enter password", "Click login"],
    "expected_result": "User is logged in"
  }],
  "summary": {
    "total_requirements": 1,
    "total_test_cases": 4
  }
}
```

### Excel Output
- **Requirements sheet:** All structured requirements
- **Test Cases sheet:** All generated test cases with formatting
- **Summary sheet:** Statistics and metrics

### CSV Output
```
test_id,requirement_id,title,test_type,priority,steps,expected_result
REQ-001-POS-001,REQ-001,User successfully logs in,positive,high,"Enter email|Enter password|Click login",User is logged in
REQ-001-NEG-001,REQ-001,Login fails with empty email,negative,high,"Leave email empty|Enter password|Click login",Error message displayed
```

### Markdown Output
```markdown
# Test Cases Report

## REQ-001: User Login

### REQ-001-POS-001: User successfully logs in
- **Type:** Positive
- **Steps:** Enter email, Enter password, Click login
- **Expected Result:** User is logged in

### REQ-001-NEG-001: Login fails with empty email
- **Type:** Negative
- **Steps:** Leave email empty, Enter password, Click login
- **Expected Result:** Error message displayed
```

---

## 🎯 What the System Does

### Input
```
"User can login with email and password. System must validate email."
```

### Processing
1. **Extract:** Find actors (user, system), actions (login, validate), objects
2. **Parse:** Use spaCy to find semantic relationships
3. **Normalize:** Convert "sign in" → "login", "email address" → "email"
4. **Structure:** Build requirement with fields: actor, action, inputs, type
5. **Generate Tests:**
   - 1 positive test (happy path)
   - 2-3 negative tests (invalid inputs, empty fields)
   - 2-3 edge cases (boundary values, special characters)
   - 2-3 security tests (if security-related)

### Output
```
REQ-001-POS-001: User successfully logs in with email and password
REQ-001-NEG-001: Login fails with empty email
REQ-001-NEG-002: Login fails with empty password
REQ-001-NEG-003: Login fails with invalid email format
REQ-001-EDG-001: Login with email at maximum length
REQ-001-EDG-002: Login with special characters in password
REQ-001-SEC-001: Verify password is encrypted
```

---

## 🛠️ Troubleshooting

### Error: "No module named 'spacy'"
```bash
pip install spacy
python -m spacy download en_core_web_sm
```

### Error: "Connection refused at http://localhost:8000"
- Make sure server is running: `python main.py`
- Check port 8000 is not in use: `lsof -i :8000`
- Try different port: `python main.py --port 8001`

### Error: "Requirements.txt not found"
```bash
cd rule_based_testgen
pip install -r requirements.txt
```

### spaCy model not found
```bash
python -m spacy download en_core_web_sm
# Check: python -m spacy validate
```

### Test system.py shows 0 test cases
- Check spaCy is installed: `python -c "import spacy; nlp = spacy.load('en_core_web_sm')"`
- Run in verbose mode: `python test_system.py 2>&1 | head -50`

---

## 📚 Next Steps

### For Testing
1. ✅ Run `python test_system.py`
2. ✅ Start server: `python main.py`
3. ✅ Process requirements using API
4. ✅ Export test cases in your preferred format

### For Capstone Report
1. Document architecture (10 layers)
2. Show example inputs/outputs
3. Compare to ML-based approaches
4. Discuss rule design and extensibility

### For UI Development (Phase 2)
1. Build React/Vue frontend
2. Connect to `/api/generate` and `/api/generate-file` endpoints
3. Add file upload UI
4. Display generated tests in table format
5. Add export buttons (JSON/Excel/CSV)

### For Database Integration (Phase 3)
1. Use FastAPI + SQLAlchemy
2. Store requirements and test cases
3. Add user authentication
4. Track generation history

---

## 🎓 Understanding the Code

**Core Pipeline Flow:**

```
Input Text/File
    ↓
TextPreprocessor → Clean & normalize
    ↓
SentenceSegmenter → Split into atomic units
    ↓
SemanticExtractor → Extract actor/action/objects (spaCy)
    ↓
Normalizer → Apply synonyms & domain rules
    ↓
RequirementStructurer → Build JSON schema
    ↓
TestGenerator → Generate 4 test types (rules)
    ↓
ExportHandler → JSON/Excel/CSV/Markdown
    ↓
Output Files/Response
```

**Key Files:**
- `main.py` - FastAPI server & endpoints
- `pipeline.py` - Orchestrates all modules
- `test_generator.py` - Core rule engine
- `semantic_extractor.py` - spaCy NLP processing
- `config.py` - Domain keywords & synonyms

---

## 💡 Tips

- **Large files?** The system processes files incrementally and prints progress
- **Custom domains?** Add to `DOMAIN_KEYWORDS` in `config.py`
- **New rules?** Add test type rules to `TestGenerator` class
- **Debug issues?** Add `--verbose` flag or check `ExportHandler.to_json()` output

---

## ✅ Success Checklist

- [ ] pip install completed
- [ ] spacy model downloaded: `en_core_web_sm`
- [ ] test_system.py passes
- [ ] main.py starts without errors
- [ ] Can access http://localhost:8000/docs
- [ ] Can POST to /api/generate
- [ ] Can upload file to /api/generate-file
- [ ] Can export to JSON/Excel/CSV
- [ ] Generated at least 4 test cases per requirement

---

## 📞 Quick Command Reference

```bash
# Setup
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Test
cd rule_based_testgen
python test_system.py

# Run Server
python main.py

# Test API (in another terminal)
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"requirements_text":"User can login","export_format":"json"}'

# Stop Server
# Press CTRL+C in the terminal
```

---

**Happy testing! 🎉**

For detailed module documentation, see [README.md](README.md).
