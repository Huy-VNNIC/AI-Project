# 📚 RULE-BASED TEST CASE GENERATOR - DOCUMENTATION INDEX

**Last Updated:** April 2, 2026  
**System Status:** 🟢 **FULLY OPERATIONAL**  
**Start Command:** `python3 setup.py`

---

## 🎯 QUICK NAVIGATION

### ⚡ I Want to...

**Start Using the System NOW** → [QUICKSTART.md](./QUICKSTART.md)
- One-command setup
- Basic usage examples
- REST API tutorial

**Understand How It Works** → [README.md](./README.md)
- Complete architecture
- Module documentation
- Data models
- API reference

**Check System Status** → [STATUS_CHECKLIST.md](./STATUS_CHECKLIST.md)
- What's been implemented
- Test results
- Feature checklist

**See Test Results** → [TEST_REPORT.md](./TEST_REPORT.md)
- Execution results
- Performance metrics
- Verification details

**See What Was Built** → [IMPLEMENTATION_COMPLETE.md](./IMPLEMENTATION_COMPLETE.md)
- File manifest
- Code statistics
- Architecture overview

---

## 📁 DOCUMENTATION FILES

### 1. **QUICKSTART.md** ⚡ START HERE
- **For:** Users who want to start immediately
- **Contains:** 
  - One-command setup (3 options)
  - Usage examples
  - REST API examples
  - Troubleshooting
  - Quick reference

**Read Time:** 5 minutes
**Location:** [QUICKSTART.md](./QUICKSTART.md)

---

### 2. **README.md** 📖 COMPREHENSIVE GUIDE
- **For:** Users understanding the system deeply
- **Contains:**
  - System architecture diagram
  - Module-by-module reference
  - Data models explained
  - Test generation rules
  - API endpoint documentation
  - Example workflows
  - Integration guide

**Read Time:** 15 minutes
**Location:** [README.md](./README.md)

---

### 3. **STATUS_CHECKLIST.md** ✅ VERIFICATION
- **For:** Understanding what's been completed
- **Contains:**
  - Feature checklist
  - Test results summary
  - Directory structure
  - Statistics
  - One-command options

**Read Time:** 10 minutes
**Location:** [STATUS_CHECKLIST.md](./STATUS_CHECKLIST.md)

---

### 4. **TEST_REPORT.md** 🧪 DETAILED TESTING
- **For:** Understanding test coverage
- **Contains:**
  - Test execution results
  - Component test results
  - Performance metrics
  - Quality assurance report
  - Verification checklist

**Read Time:** 10 minutes
**Location:** [TEST_REPORT.md](./TEST_REPORT.md)

---

### 5. **IMPLEMENTATION_COMPLETE.md** 🏗️ BUILD DETAILS
- **For:** Understanding what was built
- **Contains:**
  - File manifest
  - Code statistics
  - Architecture details
  - Features overview

**Read Time:** 5 minutes
**Location:** [IMPLEMENTATION_COMPLETE.md](./IMPLEMENTATION_COMPLETE.md)

---

## 🚀 GETTING STARTED - 3 EASY OPTIONS

### Option 1: Python Setup Script (Recommended)
```bash
cd /home/dtu/AI-Project/AI-Project/rule_based_system
python3 setup.py
```
**What It Does:**
- Installs all dependencies
- Downloads spaCy model
- Runs quick start demo
- Generates sample test cases

**Time:** ~60 seconds

---

### Option 2: Bash Setup Script
```bash
cd /home/dtu/AI-Project/AI-Project/rule_based_system
bash setup_and_run.sh
```

---

### Option 3: Manual Steps
```bash
cd /home/dtu/AI-Project/AI-Project/rule_based_system
pip install -r requirements.txt
python3 -m spacy download en_core_web_sm
python3 quick_start.py
```

---

## 📚 CODE REFERENCE

### Core Modules

#### 1. **models/canonical.py**
- Data schemas (CanonicalRequirement, TestCase)
- Universal representation
- Serialization methods

#### 2. **core/input_processor.py**
- Extract from PDF, DOCX, TXT, Excel, CSV
- Handle multiple file types
- Error handling

#### 3. **core/format_detector.py**
- Auto-detect format type
- Free text, user story, use case, Excel
- Fallback to default

#### 4. **core/text_preprocessor.py**
- Clean and normalize text
- Remove artifacts
- Preserve structure

#### 5. **core/normalizer.py**
- Synonym mapping (70+ rules)
- Lemmatization
- Type re-classification
- Security/performance signals

#### 6. **parsers/free_text_parser.py**
- spaCy NLP dependency parsing
- Extract actor, action, objects, conditions
- Expected result detection

#### 7. **parsers/user_story_parser.py**
- Parse "As a... I want... so that..." format
- Acceptance criteria extraction
- Regex-based parsing

#### 8. **parsers/use_case_parser.py**
- Header-based section extraction
- Main flow analysis
- Multiple use cases support

#### 9. **parsers/excel_parser.py**
- Fuzzy column matching
- Flexible schema mapping
- Row-to-requirement conversion

#### 10. **core/test_generator.py**
- Rule-based test generation
- 5 test types (positive, negative, edge, security, performance)
- Test data mapping
- Priority assignment

#### 11. **core/pipeline.py**
- Orchestrate all components
- File and text input support
- Summary generation

#### 12. **exports/export_handler.py**
- JSON export
- CSV export (RFC 4180)
- Excel XLSX (formatted)
- Markdown export
- Batch export

#### 13. **main.py**
- FastAPI REST API
- 5+ endpoints
- Swagger UI auto-documentation
- CORS support

---

## 🎯 TYPICAL WORKFLOWS

### Workflow 1: Quick Demo (5 minutes)
```
1. Run: python3 setup.py
2. Check: sample_output/ folder
3. View: Generated test cases
4. Done!
```

### Workflow 2: Process Your Requirements (10 minutes)
```
1. Prepare requirements file (PDF, Excel, TXT)
2. Run API: python3 main.py
3. Upload file: http://localhost:8001/docs
4. Download results
```

### Workflow 3: Python Library (Programmatic)
```python
from rule_based_system import run_pipeline, export_excel

# Process file
result = run_pipeline("my_requirements.pdf")

# Use test cases
test_cases = result["_objects"]["test_cases"]

# Export
export_excel(test_cases, "my_tests.xlsx")
```

### Workflow 4: REST API Integration
```bash
# Upload and get JSON
curl -X POST http://localhost:8001/generate \
  -F "file=@requirements.pdf"

# Or send text
curl -X POST http://localhost:8001/generate/text \
  -H "Content-Type: application/json" \
  -d '{"text":"User can login","format":"free_text"}'
```

---

## 📊 KEY STATISTICS

| Metric | Value |
|--------|-------|
| **Total Files** | 24 |
| **Total Code Lines** | ~3,700 |
| **Core Modules** | 10 |
| **Parser Types** | 4 |
| **Export Formats** | 4 |
| **API Endpoints** | 5+ |
| **Test Cases Generated (Demo)** | 53 |
| **Normalization Rules** | 70+ |
| **Installation Time** | ~60 seconds |
| **First Run Time** | < 5 seconds |

---

## 🔧 CONFIGURATION

### Change API Port
Edit **main.py** line 2:
```python
PORT = 8001  # Change to 8002, 8003, etc.
```

### Add Custom Synonyms
Edit **core/normalizer.py**:
```python
ACTION_SYNONYMS["new_verb"] = "canonical_verb"
SECURITY_SIGNALS.add("new_keyword")
```

### Customize Test Rules
Edit **core/test_generator.py**:
```python
# Add new test data
FIELD_TEST_DATA["custom_field"] = {...}

# Add new action
ACTION_INPUT_MAP["new_action"] = [...]
```

---

## 🛠️ TROUBLESHOOTING

### Issue: Import Error
```bash
# Solution:
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: spaCy Model Not Found
```bash
# Solution:
python3 -m spacy download en_core_web_sm
```

### Issue: Port Already in Use
```bash
# Solution: Change port in main.py or kill process
lsof -i :8001  # Find process
kill -9 <PID>  # Kill it
```

### Issue: Permission Denied
```bash
# Solution: Make scripts executable
chmod +x setup_and_run.sh
chmod +x setup.py
```

See [QUICKSTART.md](./QUICKSTART.md) for more help.

---

## 📈 LEARNING PATH

### Level 1: Beginner (5 minutes)
- [ ] Read this index
- [ ] Run `python3 setup.py`
- [ ] Check `sample_output/` folder
- [ ] View generated test cases

### Level 2: Intermediate (30 minutes)
- [ ] Read [QUICKSTART.md](./QUICKSTART.md)
- [ ] Try different input formats
- [ ] Experiment with REST API
- [ ] Test with your own requirements

### Level 3: Advanced (2 hours)
- [ ] Read [README.md](./README.md)
- [ ] Study module structure
- [ ] Customize rules
- [ ] Build custom wrappers
- [ ] Integrate with your system

### Level 4: Expert (4+ hours)
- [ ] Understand complete architecture
- [ ] Modify parsers for new formats
- [ ] Add new test generation rules
- [ ] Contribute improvements
- [ ] Deploy as microservice

---

## 🎓 USE CASES

### Academic / Capstone
- [x] Auto-generate test cases for capstone project
- [x] Use as part of thesis/dissertation
- [x] Document approach for paper
- [x] Show in presentation

### Production / Enterprise
- [x] Automate test case generation
- [x] Integrate with CI/CD pipeline
- [x] Batch process requirements
- [x] Support multiple teams

### Learning / Research
- [x] Study NLP + test generation
- [x] Experiment with rules
- [x] Analyze effectiveness
- [x] Publish findings

### Prototyping
- [x] Quick test coverage
- [x] Requirements validation
- [x] Feature documentation
- [x] QA process automation

---

## 📞 SUPPORT RESOURCES

### Documentation
- 📖 [README.md](./README.md) - Complete reference
- ⚡ [QUICKSTART.md](./QUICKSTART.md) - Getting started
- ✅ [STATUS_CHECKLIST.md](./STATUS_CHECKLIST.md) - What's ready
- 🧪 [TEST_REPORT.md](./TEST_REPORT.md) - Test results

### Code Help
- **In Code:** Every function has docstrings
- **Type Hints:** All functions have types
- **Comments:** Complex logic explained
- **API Docs:** Auto-generated at `/docs`

### First Steps
1. Read this index (you are here!)
2. Check [QUICKSTART.md](./QUICKSTART.md)
3. Run `python3 setup.py`
4. Open `sample_output/` to see results

### Troubleshooting
- See [QUICKSTART.md - Troubleshooting](./QUICKSTART.md#troubleshooting)
- Check error messages carefully
- Review terminal output for hints

---

## 🎉 GETTING HELP

### Issue Found?
1. Check [QUICKSTART.md troubleshooting section](./QUICKSTART.md#troubleshooting)
2. Read relevant documentation
3. Check error message for hints
4. Try manual installation steps

### Want to Learn More?
1. Start with [README.md](./README.md)
2. Explore code in relevant modules
3. Read docstrings and comments
4. Experiment with examples

### Want to Customize?
1. Review [core/normalizer.py](./core/normalizer.py) for synonyms
2. Review [core/test_generator.py](./core/test_generator.py) for test rules
3. Review [parsers/](./parsers/) for format support
4. Add your own rules!

---

## 📊 QUICK REFERENCE

### One-Command Start
```bash
python3 setup.py
```

### Quick Demo
```bash
python3 quick_start.py
```

### Start API
```bash
python3 main.py
# Open: http://localhost:8001/docs
```

### Python Library
```python
from rule_based_system import run_pipeline_from_text
result = run_pipeline_from_text("Your requirement")
```

---

## 🔗 FILE STRUCTURE

```
rule_based_system/
├── setup.py ..................... One-command setup
├── quick_start.py ............... Demo script
├── main.py ...................... REST API
├── requirements.txt ............. Dependencies
│
├── models/
│   └── canonical.py ............. Data schemas
│
├── core/
│   ├── input_processor.py ....... File extraction
│   ├── format_detector.py ....... Format detection
│   ├── text_preprocessor.py ..... Text cleaning
│   ├── normalizer.py ............ Normalization
│   ├── test_generator.py ........ Test generation
│   └── pipeline.py .............. Orchestration
│
├── parsers/
│   ├── free_text_parser.py ...... NLP parsing
│   ├── user_story_parser.py ..... User story
│   ├── use_case_parser.py ....... Use case
│   └── excel_parser.py .......... Excel/CSV
│
├── exports/
│   └── export_handler.py ........ Multi-format export
│
├── sample_output/ ............... Generated files
│   ├── test_cases.json
│   ├── test_cases.csv
│   ├── test_cases.xlsx
│   └── test_cases.md
│
└── docs/
    ├── README.md ................ This file
    ├── QUICKSTART.md ............ Getting started
    ├── STATUS_CHECKLIST.md ...... Status
    ├── TEST_REPORT.md ........... Test results
    └── IMPLEMENTATION_COMPLETE.md . Build info
```

---

## ✅ FINAL CHECKLIST

- [ ] Read this index
- [ ] Choose a setup option
- [ ] Run the setup command
- [ ] Check sample output
- [ ] Read [QUICKSTART.md](./QUICKSTART.md)
- [ ] Try with your own requirements
- [ ] Explore [README.md](./README.md) for details
- [ ] (Optional) Read [TEST_REPORT.md](./TEST_REPORT.md)

---

## 🚀 YOU'RE READY!

Everything is prepared and tested. Just run:

```bash
python3 setup.py
```

And see your test cases generated! 🎉

---

**Need help?** → Read [QUICKSTART.md](./QUICKSTART.md)  
**Want details?** → Read [README.md](./README.md)  
**Check status?** → Read [STATUS_CHECKLIST.md](./STATUS_CHECKLIST.md)  
**See tests?** → Read [TEST_REPORT.md](./TEST_REPORT.md)

**Happy Testing! 🧪**
