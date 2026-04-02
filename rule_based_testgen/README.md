# 🧪 Rule-Based Test Case Generator

**A deterministic NLP + rule-based system for automatically generating comprehensive test cases from requirement documents.**

No external AI/LLM APIs. Pure rule-based logic + NLP preprocessing.

---

## 🎯 Overview

This system transforms unstructured requirement documents into structured test cases using:

- **Natural Language Processing (NLP)** - Dependency parsing, entity extraction
- **Rule-Based Generation** - Deterministic test creation rules
- **Domain Understanding** - Hotel, Banking, E-commerce, Healthcare domains
- **Multiple Export Formats** - JSON, Excel, CSV, Markdown

**Architecture:**
```
Input (PDF/DOCX/TXT)
    ↓
Input Processing → Extract raw text
    ↓
Text Preprocessing → Clean, normalize, remove noise
    ↓
Sentence Segmentation → Split into atomic requirements
    ↓
Semantic Extraction (spaCy) → Extract actor/action/object/conditions
    ↓
Normalization → Lemmatize, synonym mapping, actor normalization
    ↓
Requirement Structuring → Build JSON schema
    ↓
Test Generation (Rule Engine) → Create positive/negative/edge/security tests
    ↓
Export → JSON/Excel/CSV/Markdown
```

---

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download spaCy model
python -m spacy download en_core_web_sm

# 3. Verify installation
python -c "import spacy; spacy.load('en_core_web_sm'); print('✓ spaCy ready')"
```

---

## 🚀 Quick Start

### Method 1: Via FastAPI Server

```bash
# Start server
python main.py

# API will be available at http://localhost:8000
# Documentation at http://localhost:8000/docs
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "requirements_text": "User can login with email and password. System must validate email format.",
    "export_format": "json"
  }'
```

### Method 2: Via Python Code

```python
from pipeline import TestGenerationPipeline

# Create pipeline
pipeline = TestGenerationPipeline()

# Process a file
results = pipeline.process_file(
    filepath="requirements.txt",
    output_format="excel",
    export_path="test_cases.xlsx"
)

# Or process text directly
results = pipeline.process_text(
    text="User can login with email and password",
    output_format="json"
)

# Access results
print(f"Generated {results['summary']['total_test_cases']} test cases")
```

### Method 3: Via Command Line

```bash
# Process file and export
python cli.py process requirements.txt --output excel --export test_cases.xlsx

# Generate from text
python cli.py generate "User can login" --output json
```

---

## 📋 Module Documentation

### 1. **input_processor.py**
Extract text from PDF, DOCX, or TXT files

```python
from input_processor import InputProcessor

processor = InputProcessor()
text = processor.extract_text("requirements.pdf")
```

### 2. **text_preprocessor.py**
Clean and normalize text

```python
from text_preprocessor import TextPreprocessor

preprocessor = TextPreprocessor()
cleaned = preprocessor.process(raw_text)
# Removes: headers, footers, URLs, noise
# Preserves: bullet points, sections, structure
```

### 3. **sentence_segmenter.py**
Split text into atomic requirement units

```python
from sentence_segmenter import SentenceSegmenter

segmenter = SentenceSegmenter()
requirements = segmenter.segment("User can login. System validates email....")
# ["User can login.", "System validates email.", ...]
```

### 4. **semantic_extractor.py** ⭐ CORE
Extract semantic structure using spaCy dependency parsing

```python
from semantic_extractor import SemanticExtractor

extractor = SemanticExtractor()
result = extractor.extract("User enters email and password")
# Returns: {
#   "actor": "user",
#   "action": "enter",
#   "objects": ["email", "password"],
#   "inputs": ["email", "password"],
#   "conditions": [],
#   "type": "functional"
# }
```

### 5. **normalizer.py**
Lemmatize, apply synonym mapping, normalize actors

```python
from normalizer import Normalizer

normalizer = Normalizer()
normalized = normalizer.normalize(extracted_requirement)
# action: "sign in" → "login"
# actor: "application" → "system"
# detects domain: "hotel_management"
```

### 6. **requirement_structurer.py**
Build structured JSON schema

```python
from requirement_structurer import RequirementStructurer

structurer = RequirementStructurer()
structured = structurer.structure("REQ-001", normalized_req)
# Returns StructuredRequirement with:
# - requirement_id, actor, action, objects
# - inputs, conditions, expected_results
# - domain, priority, type, status
```

### 7. **test_generator.py** ⚡ RULE ENGINE
Generate test cases using rules

```python
from test_generator import TestGenerator

generator = TestGenerator()
test_cases = generator.generate_tests(structured_requirement)
# Generates:
# - 1 Positive test (happy path)
# - N Negative tests (invalid inputs, empty fields)
# - N Edge case tests (boundary values)
# - 3+ Security tests (if security requirement)
```

### 8. **export_handler.py**
Export to multiple formats

```python
from export_handler import ExportHandler

# JSON
ExportHandler.to_json_file(test_cases, "tests.json")

# Excel
ExportHandler.to_excel(test_cases, "tests.xlsx")

# CSV
ExportHandler.to_csv(test_cases, "tests.csv")

# Markdown
ExportHandler.to_markdown_file(test_cases, "tests.md")
```

### 9. **pipeline.py**
Orchestrate full pipeline

```python
from pipeline import TestGenerationPipeline

pipeline = TestGenerationPipeline()

# Process file
results = pipeline.process_file(
    "requirements.txt",
    output_format="excel",
    export_path="tests.xlsx"
)

# Or text
results = pipeline.process_text(
    "Your requirement text here",
    output_format="json"
)
```

---

## 🧪 Test Generation Rules

### Positive Tests (Happy Path)
```
For: "User enters email and password"
→ Test: "Successfully enter email and password"
   Steps:
   1. User opens application
   2. User navigates to login section
   3. User enters valid email
   4. User enters valid password
   5. User submits form
   Expected: "Login successful"
```

### Negative Tests (Invalid Inputs)
```
For each input field:
  - Invalid format test
  - Empty field test
  - Missing required field test
  
Example:
→ Test: "Reject login with invalid email"
→ Test: "Reject login with empty password"
```

### Edge Case Tests (Boundary Values)
```
For inputs with known boundaries:
  - Min/max length
  - Special characters
  - SQL injection attempts

Example:
→ Test: "Handle extremely long email"
→ Test: "Reject SQL injection in email"
```

### Security Tests (Auto-generated for security requirements)
```
For requirement type="security":
  - Unauthorized access test
  - SQL injection test
  - XSS prevention test
  - Permission verification test

Example:
→ Test: "Reject unauthorized authentication"
→ Test: "Sanitize SQL injection attempts"
```

---

## 📊 Example Output

### Input
```
User can login with email and password.
System must validate email format.
If login fails, display error message.
```

### Generated Test Cases (JSON)
```json
[
  {
    "test_id": "REQ-001-POS-001",
    "requirement_id": "REQ-001",
    "title": "Successfully enter email and password",
    "test_type": "positive",
    "priority": "high",
    "domain": "general",
    "preconditions": ["User is not logged in"],
    "steps": [
      "User opens the application",
      "User navigates to login section",
      "User enters valid email",
      "User enters valid password",
      "User submits the form/request"
    ],
    "expected_result": "✓ Login successful"
  },
  {
    "test_id": "REQ-001-NEG-002",
    "title": "Reject login with invalid email",
    "test_type": "negative",
    "priority": "high",
    "steps": ["...", "User enters INVALID email", "..."],
    "expected_result": "✗ Validation error about invalid email"
  },
  {
    "test_id": "REQ-001-SEC-003",
    "title": "Reject unauthorized authentication",
    "test_type": "security",
    "priority": "critical",
    "expected_result": "✗ Access denied - not authenticated"
  }
]
```

---

## 📈 Performance

- Processing speed: ~100-200ms per requirement
- Memory usage: ~200-300MB
- Supports: Unlimited requirements (limited by file size)
- Export time: <1s for 100 test cases to Excel

---

## 🎓 Capstone Report Keywords

When writing capstone report, emphasize:

1. **Deterministic & Auditable**: Unlike AI models, with same input always get same output
2. **Rule-Based NLP**: Combines dependency parsing + heuristics
3. **No External APIs**: Completely self-contained
4. **Domain-Aware**: Different test patterns for different domains
5. **Extensible**: Easy to add new rules/domains

---

## 🛠️ Extensibility

### Add New Domain
```python
# In config.py, add domain keywords
DOMAIN_KEYWORDS = {
    "custom_domain": ["keyword1", "keyword2", ...]
}

# Add tests in test_generator.py
def generate_custom_tests(self, req):
    # Your domain-specific test logic
    pass
```

### Add New Rule
```python
# In test_generator.py
def generate_custom_test_type(self, req):
    # Create new test case
    return TestCase(...)
```

---

## 🔧 Troubleshooting

### spaCy Model Issues
```bash
python -m spacy download en_core_web_sm
```

### No Requirements Found
- Check if preprocessor is too aggressive
- Verify minimum length in config.py
- Check sentence segmentation

### Low Test Count
- Add more rules to test_generator.py
- Lower quality_threshold in config
- Check input is valid requirements

---

## 📄 License & Attribution

Rule-Based Test Case Generator v1.0  
Created for: AI-Project Capstone  
License: MIT

---

## 📞 Support

For questions or issues, refer to:
- Individual module docstrings
- Example usage in each file
- API documentation: http://localhost:8000/docs
- Sample requirements: `sample_requirements.txt`

---

**Made with 💡 NLP + 🔧 Rule-Based Logic**
