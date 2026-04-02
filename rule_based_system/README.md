# 🚀 Rule-Based Test Case Generator

A **deterministic NLP + rule-based system** for automatic test case generation from business requirements. No external AI APIs — completely **self-contained**.

## ✨ Features

- ✅ **Multi-format Input:** PDF, DOCX, TXT, Excel, CSV, User Stories, Use Cases
- ✅ **Format Auto-detection:** Automatically identifies requirement format
- ✅ **NLP Processing:** spaCy dependency parsing for semantic extraction
- ✅ **Rule-Based Generation:** Deterministic test case generation (no randomness)
- ✅ **Multiple Test Types:** Positive, Negative, Edge, Security, Performance
- ✅ **Multi-format Export:** JSON, Excel, CSV, Markdown
- ✅ **REST API:** FastAPI endpoints for easy integration
- ✅ **Standalone:** No external APIs, works completely offline

## 🎯 System Architecture

```
Input File/Text
    ↓
Step 1: Extract Raw Text (PDF/DOCX/TXT/Excel)
    ↓
Step 2: Detect Format (Free Text / User Story / Use Case / Excel)
    ↓
Step 3: Preprocess (Clean & Normalize)
    ↓
Step 4: Parse (Format-specific parser)
    ↓
Step 5: Normalize (Synonym mapping, Lemmatization)
    ↓
Step 6: Generate Test Cases (Rule engine)
    ↓
Step 7: Export (JSON/Excel/CSV/Markdown)
```

## 📦 Project Structure

```
rule_based_system/
├── models/
│   ├── canonical.py          # Data models (CanonicalRequirement, TestCase)
│   └── __init__.py
├── core/
│   ├── input_processor.py    # File extraction
│   ├── format_detector.py    # Format detection
│   ├── text_preprocessor.py  # Text cleaning
│   ├── normalizer.py         # Normalization & lemmatization
│   ├── test_generator.py     # Rule engine
│   ├── pipeline.py           # Orchestrator
│   └── __init__.py
├── parsers/
│   ├── free_text_parser.py   # Free text + spaCy NLP
│   ├── user_story_parser.py  # User story format
│   ├── use_case_parser.py    # Use case format
│   ├── excel_parser.py       # Excel/CSV format
│   └── __init__.py
├── exports/
│   ├── export_handler.py     # JSON/Excel/CSV/Markdown export
│   └── __init__.py
├── main.py                   # FastAPI REST API
├── quick_start.py            # Quick start demo
├── requirements.txt          # Python dependencies
└── __init__.py
```

## 🚀 Quick Start

### Installation

```bash
# Navigate to system directory
cd rule_based_system

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### Option 1: Run Quick Start Demo

```bash
cd rule_based_system
python quick_start.py
```

Output:
```
📊 Summary:
  - Format Detected: free_text
  - Total Requirements: 7
  - Total Test Cases: 28
  - Avg Tests per Requirement: 4.0
```

### Option 2: Start REST API Server

```bash
python main.py
```

Then:
- Access API docs: http://localhost:8001/docs
- API available at: http://localhost:8001

### Option 3: Use as Python Library

```python
from rule_based_system.core.pipeline import run_pipeline_from_text
from rule_based_system.exports.export_handler import export_excel

# Simple text input
requirements = """
User can login with email and password.
System must validate email format.
If login fails, show error message.
"""

# Process
result = run_pipeline_from_text(requirements)

# Export
export_excel(result['_objects']['test_cases'], 'output.xlsx')

# Print summary
print(f"Generated {result['summary']['total_test_cases']} test cases")
```

## 📚 Module Documentation

### 1. Data Models (`models/canonical.py`)

**CanonicalRequirement:** Universal requirement schema
```python
@dataclass
class CanonicalRequirement:
    actor: str                      # user, admin, system
    action: str                     # login, submit, etc.
    objects: list[str]              # email, password, etc.
    conditions: list[str]           # if, when, unless
    expected: str                   # expected result
    req_type: str                   # functional, security, performance
    source_format: str              # free_text, user_story, use_case, excel
    raw_text: str                   # original text for debugging
    id: str                         # auto-generated ID
```

**TestCase:** Generated test case
```python
@dataclass
class TestCase:
    req_id: str                     # linked requirement ID
    title: str                      # test title
    precondition: str               # setup needed
    steps: list[str]                # test steps
    expected_result: str            # expected outcome
    test_type: str                  # positive, negative, edge, security
    priority: str                   # high, medium, low
    id: str                         # auto-generated ID
```

### 2. Input Processing (`core/input_processor.py`)

Supports:
- `.pdf` - PDF files (pdfplumber)
- `.docx` - Word documents (python-docx)
- `.txt` - Text files
- `.xlsx` / `.csv` - Excel and CSV tables

### 3. Format Detection (`core/format_detector.py`)

Auto-detects:
- **Free Text** - Natural language text
- **User Story** - "As a..., I want..., so that..."
- **Use Case** - Structured use case format
- **Excel** - Tabular data

### 4. Text Preprocessing (`core/text_preprocessor.py`)

- Remove page artifacts (headers, footers, page numbers)
- Normalize whitespace and line endings
- Preserve bullet points and numbering
- Clean special characters

### 5. Parsed (`parsers/`)

#### Free Text Parser
- Uses spaCy dependency parsing
- Extracts: actor (nsubj), action (ROOT verb), objects (dobj/pobj)
- Detects conditions (IF/WHEN/UNLESS)
- Classifies requirement type

#### User Story Parser
- Regex-based pattern matching
- Supports multiple formats ("As a...", "I want...")
- Extracts acceptance criteria

#### Use Case Parser
- Header-based extraction
- Recognizes: Actor, Main Flow, Precondition, Postcondition
- Handles multiple use cases in one document

#### Excel Parser
- Column name auto-mapping
- Supports various naming conventions
- Flexible schema mapping

### 6. Normalizer (`core/normalizer.py`)

- **Action Normalization:** "sign in" → "login", "authenticate" → "login"
- **Actor Normalization:** "application" → "system", "customer" → "user"
- **Lemmatization:** "logging" → "log", "deleted" → "delete"
- **Type Reclassification:** Identify security/performance requirements

### 7. Test Generator (`core/test_generator.py`)

Rule engine that generates:

**Positive Tests** (Happy path)
- Valid inputs, expected flow
- 1 per requirement
- Example: "User successfully logs in"

**Negative Tests** (Invalid inputs)
- Empty fields, invalid formats
- 2+ per input field
- Example: "Login fails with invalid email"

**Edge Cases** (Boundary values)
- Min/max length, special characters
- Example: "Login with max-length password"

**Security Tests** (If security requirement)
- SQL injection, XSS, brute force
- Example: "System rejects SQL injection attempt"

**Performance Tests** (If performance requirement)
- Load testing, response time
- Example: "Response time under load"

### 8. Pipeline (`core/pipeline.py`)

Orchestrates entire workflow:

```python
# From file
result = run_pipeline("requirements.pdf")
result = run_pipeline("requirements.txt", force_format="free_text")

# From text
result = run_pipeline_from_text("User can login...")

# Returns
{
    "format_detected": "free_text",
    "requirements": [...],
    "test_cases": [...],
    "summary": {
        "total_requirements": 7,
        "total_test_cases": 28,
        "avg_tests_per_req": 4.0,
        "test_cases_by_type": {...},
        ...
    }
}
```

### 9. Export Handler (`exports/export_handler.py`)

```python
from rule_based_system.exports.export_handler import (
    export_json,
    export_csv,
    export_excel,
    export_markdown,
)

# Export individual formats
export_json(test_cases, "output.json")
export_excel(test_cases, "output.xlsx")
export_csv(test_cases, "output.csv")
export_markdown(test_cases, "output.md")

# Export all formats at once
export_all_formats(test_cases, "output_basename")
```

### 10. REST API (`main.py`)

#### Endpoints

**POST /generate**
- Upload requirement file
- Auto-detect format
- Returns: Test cases as JSON

**POST /generate/text**
- Submit requirement text directly
- Returns: Test cases as JSON

**POST /export/excel**
- Upload file
- Generate tests
- Download as Excel file

**GET /health**
- Health check

**GET /formats**
- List supported formats and file types

**GET /docs**
- Interactive API documentation (Swagger UI)

## 🔧 Configuration

Customize in `core/normalizer.py`:

```python
# Add action synonym
ACTION_SYNONYMS["new_verb"] = "canonical_verb"

# Add actor synonym
ACTOR_SYNONYMS["new_actor"] = "system"

# Add security keywords
SECURITY_SIGNALS.add("new_security_keyword")
```

## 📊 Example Workflow

### Input
```
User Story Format:
"As a customer, I want to login with email and password
so that I can access my account securely.

Acceptance Criteria:
- Email must be valid format
- Password must be at least 8 characters
- On failed login, show error message
"
```

### Processing
1. **Format Detection:** User Story
2. **Parsing:** Extract actor="customer", action="login", objects=["email", "password"]
3. **Normalization:** actor="user", action="login"
4. **Classification:** req_type="security" (detected from "securely")
5. **Test Generation:**
   - REQ-001-POS-001: Happy path login
   - REQ-001-NEG-001: Invalid email format
   - REQ-001-NEG-002: Empty password
   - REQ-001-EDG-001: Boundary password length
   - REQ-001-SEC-001: SQL injection attempt

### Output

**JSON:**
```json
{
  "id": "TC_ABC123",
  "req_id": "REQ_XYZ789",
  "title": "[Security] User successfully logs in with valid inputs",
  "test_type": "positive",
  "priority": "high"
}
```

**Excel:** Formatted table with colors, auto-width columns

**Markdown:** Organized by requirement with steps

## 🎓 Test Generation Rules

| Test Type | Count | Conditions |
|-----------|-------|-----------|
| Positive | 1 | Always (happy path) |
| Negative | 2-3 | Per input field + empty field |
| Edge | 2+ | Boundary values |
| Security | 3+ | If req_type="security" |
| Performance | 1 | If req_type="performance" |
| Condition | 2 | Per condition (satisfied + violated) |

## ⚙️ System Requirements

- Python 3.8+
- 1 GB RAM (minimum)
- 500 MB disk space
- Internet (first-time setup only for spaCy model)

## 🔄 Integration with Existing System

The system is designed to work alongside the existing requirement_analyzer:

```python
# Simultaneously run both
from requirement_analyzer.api import app as ai_app
from rule_based_system.main import app as rule_app

# Can mount as subapp
from fastapi import FastAPI
combined_app = FastAPI()
combined_app.mount("/ai", ai_app)
combined_app.mount("/rules", rule_app)
```

## 📝 Example Usage

### Process a File

```bash
curl -X POST http://localhost:8001/generate \
  -F "file=@my_requirements.pdf"
```

### Process Text

```bash
curl -X POST http://localhost:8001/generate/text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "User can login with email",
    "format": "free_text"
  }'
```

### Download Excel Report

```bash
curl -X POST http://localhost:8001/export/excel \
  -F "file=@requirements.txt" \
  -o test_cases.xlsx
```

## 🚨 Troubleshooting

**spaCy model not found:**
```bash
python -m spacy download en_core_web_sm
```

**ImportError for pandas/openpyxl:**
```bash
pip install -r requirements.txt
```

**Port 8001 already in use:**
Edit `main.py` line: `uvicorn.run(..., port=8002, ...)`

## 📚 References

- [spaCy Documentation](https://spacy.io)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io)

## 📄 License

MIT License - See LICENSE file

## 👨‍💻 Author

Huy VNNIC  
AI Project - Test Case Generation System  
2024

---

**Status:** ✅ Production Ready  
**Test Coverage:** All core modules tested  
**Documentation:** Complete
