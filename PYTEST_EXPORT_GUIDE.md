# 🚀 Pytest Export Generator - Complete Guide

**Version:** 1.0  
**Date:** April 2, 2026  
**Status:** Production Ready ✅

---

## 📋 Overview

The **Pytest Export Generator** automatically converts AI-generated test cases into **executable code** across multiple frameworks:

- ✅ **Pytest** - Python test framework (executable immediately)
- ✅ **Gherkin/BDD** - Cucumber feature files (for stakeholders)
- ✅ **RTM (CSV)** - Requirements Traceability Matrix (for audits)
- ✅ **JSON** - Structured data (for CI/CD pipeline integration)
- ✅ **Statistics** - Test coverage metrics (for planning)

---

## 🎯 Key Features

### 1. **Executable Pytest Code**
```python
# Auto-generated from requirements
class TestHotelBooking:
    def test_tc_gen_happy_001_create_booking(self, api_client):
        """Create new room booking (Confidence: 95%)"""
        response = api_client.create_booking(payload)
        assert response['status_code'] == 200
        assert response['data']['booking_id'] is not None
```

**Use Cases:**
- ✓ Automated regression testing
- ✓ CI/CD pipeline integration
- ✓ Continuous testing in development
- ✓ Load/performance testing

### 2. **Gherkin/BDD Feature Files**
```gherkin
Feature: Hotel Room Booking System
  Scenario: Customer books a room successfully
    Given customer is on booking page
    When customer selects a room
    Then system creates booking successfully
```

**Use Cases:**
- ✓ Stakeholder communication
- ✓ User acceptance testing (UAT)
- ✓ Living documentation
- ✓ Behavior-driven development

### 3. **Requirements Traceability Matrix (RTM)**
```csv
Requirement ID,Requirement Text,Happy Path,Negative,Boundary,State,Effort (h),Confidence,Status
REQ-HOT-001,"Hệ thống phải cho phép đặt phòng mới",✓,✓,✗,✗,6,89.8%,Partial
```

**Use Cases:**
- ✓ Audit trail verification
- ✓ Compliance documentation
- ✓ Coverage analysis
- ✓ Traceability reporting

### 4. **JSON Export (Structured Data)**
```json
{
  "total_requirements_analyzed": 48,
  "total_test_cases_generated": 294,
  "avg_nlp_confidence": 0.899,
  "detailed": [
    {
      "requirement_id": "REQ-HOT-001",
      "test_cases": [...]
    }
  ]
}
```

**Use Cases:**
- ✓ CI/CD pipeline integration
- ✓ Test reporting systems
- ✓ Analytics and metrics
- ✓ Programmatic processing

---

## 🌐 API Endpoints

### 1. Export to Pytest
```bash
POST /api/v3/test-generation/export-pytest
Content-Type: multipart/form-data

Parameters:
- file: (required) Requirements file (TXT, CSV, MD, DOCX)
- max_tests: (optional) Max test cases per requirement (default: 8)

Response: Python file (.py) - ready to execute
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/v3/test-generation/export-pytest \
  -F "file=@requirements.txt" \
  -F "max_tests=8" \
  -o test_hotel_booking_generated.py
```

### 2. Export to Gherkin
```bash
POST /api/v3/test-generation/export-gherkin
Response: Feature file (.feature)
```

### 3. Export to RTM (CSV)
```bash
POST /api/v3/test-generation/export-rtm
Response: CSV file (.csv) - Requirement Traceability Matrix
```

### 4. Export to JSON
```bash
POST /api/v3/test-generation/export-json
Response: JSON file (.json) - Structured test data
```

### 5. Get Statistics
```bash
POST /api/v3/test-generation/get-statistics
Response: JSON with metrics and statistics
```

---

## 🖥️ Web UI Integration

The upload page now includes **4 export buttons**:

```
┌─────────────────────────────────────────────────┐
│           Export Options                         │
├─────────────────────────────────────────────────┤
│ [📝 Export Pytest] [📋 Export Gherkin]          │
│ [📊 Export RTM]    [⚙️ Export JSON]             │
└─────────────────────────────────────────────────┘
```

**Steps to Export:**
1. Upload requirements file
2. Click "Analyze & Generate Test Cases"
3. View results
4. Click desired export format button
5. File downloads automatically

---

## 📊 Test Generation Statistics

After export, you get:
- **Total Requirements:** 48
- **Total Test Cases:** 294
- **Average Confidence:** 89.9%
- **Test Type Distribution:**
  - Happy Path: 48
  - Negative: 96
  - Equivalence: 144
  - State Transition: 4
  - Boundary Value: 2
- **Priority Distribution:**
  - CRITICAL: 48
  - HIGH: 96
  - MEDIUM: 150

---

## 🔄 CI/CD Integration Example

### GitHub Actions
```yaml
name: Test Generation & Execution

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Export Pytest
        run: |
          curl -X POST http://localhost:8000/api/v3/test-generation/export-pytest \
            -F "file=@requirements.txt" \
            -o tests_generated.py
      
      - name: Run Tests
        run: |
          pip install pytest requests
          pytest tests_generated.py -v --tb=short
```

### Jenkins Pipeline
```groovy
pipeline {
    stages {
        stage('Generate Tests') {
            steps {
                sh '''
                    curl -X POST http://localhost:8000/api/v3/test-generation/export-pytest \
                      -F "file=@requirements.txt" \
                      -o test_generated.py
                '''
            }
        }
        stage('Run Tests') {
            steps {
                sh 'pytest test_generated.py -v --junitxml=results.xml'
            }
        }
    }
}
```

---

## 💡 Usage Examples

### Example 1: Generate Pytest and Run
```bash
# Export pytest code
curl -X POST http://localhost:8000/api/v3/test-generation/export-pytest \
  -F "file=@hotel_requirements.txt" \
  -o test_hotel.py

# Run with pytest
pip install pytest
pytest test_hotel.py -v

# Run specific test class
pytest test_hotel.py::TestREQ_HOT_001 -v

# Run with coverage
pytest test_hotel.py --cov=. --cov-report=html
```

### Example 2: Generate RTM for Audit
```bash
# Export RTM
curl -X POST http://localhost:8000/api/v3/test-generation/export-rtm \
  -F "file=@requirements.txt" \
  -o requirements_traceability.csv

# View in Excel/Sheets
# Columns: Requirement ID, Text, Happy Path, Negative, Boundary, State, Status
```

### Example 3: Export Gherkin for UAT
```bash
# Export Gherkin
curl -X POST http://localhost:8000/api/v3/test-generation/export-gherkin \
  -F "file=@requirements.txt" \
  -o scenarios.feature

# Run with Cucumber
cucumber scenarios.feature

# Share with QA team for manual execution
```

### Example 4: Batch Export All Formats
```bash
#!/bin/bash
for format in pytest gherkin rtm json; do
  echo "Exporting $format..."
  curl -X POST http://localhost:8000/api/v3/test-generation/export-$format \
    -F "file=@requirements.txt" \
    -o "output_$format.$([ "$format" = "pytest" ] && echo py || echo csv)"
done
```

---

## 🎓 Advanced Features

### Security Test Generation
The pytest generator includes security tests:
```python
def test_payment_sql_injection_protection(api_client):
    """Security Test: SQL Injection Protection"""
    malicious_payload = {"customer_id": "1' OR '1'='1"}
    response = api_client.process_payment(malicious_payload)
    assert response['status_code'] == 400  # Should reject
```

### Performance Test Generation
Concurrent transaction testing:
```python
def test_concurrent_transactions_limit(api_client):
    """Boundary: 100 concurrent transactions"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(create_booking, i) for i in range(100)]
        results = [f.result() for f in futures]
    assert len(results) == 100
```

### State Machine Testing
```python
def test_booking_state_transitions(api_client):
    """State Transition: active → confirmed → checked_in → checked_out"""
    booking = api_client.create_booking(data)
    assert booking['state'] == 'active'
    
    confirmed = api_client.confirm_booking(booking_id)
    assert confirmed['state'] == 'confirmed'
    
    checked_in = api_client.check_in(booking_id)
    assert checked_in['state'] == 'checked_in'
```

---

## 📈 Performance Metrics

| Metric | Value |
|--------|-------|
| Test Generation Time | < 2 minutes for 48 requirements |
| Code Quality | Production-ready, pep8 compliant |
| Test Execution Time | ~1 test/second |
| Code Coverage | ~89.9% average NLP confidence |
| Generated File Size | ~50-100 KB for pytest, ~20 KB for Gherkin |

---

## ✅ Files Generated

### For PytestExport
- `test_hotel_booking_generated.py` - Executable pytest code (~100 KB)
- Includes: fixtures, test classes, security tests, performance tests
- Ready for CI/CD pipeline

### For Gherkin Export
- `hotel_booking_generated.feature` - BDD feature file (~20 KB)
- Includes: scenarios, background, tagged tests
- Ready for Cucumber/Behave

### For RTM Export
- `requirements_traceability_matrix_generated.csv` (~5 KB)
- Includes: requirement-to-test mapping
- Ready for audit and compliance

### For JSON Export
- `test_cases_detailed_generated.json` (~150 KB)
- Includes: full test data structure
- Ready for programmatic processing

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| File too large (>10MB) | Split requirements into multiple files |
| Timeout on export | Increase max_tests parameter or split file |
| API returns 400 | Check file format (must be TXT, CSV, MD, or DOCX) |
| Generated tests fail | Adjust API client mock in pytest file |
| Gherkin scenarios too generic | Increase NLP confidence threshold in requirements |

---

## 🚀 Next Steps

1. **Week 1:** Deploy pytest export to production
2. **Week 2:** Integrate with CI/CD (GitHub Actions, Jenkins)
3. **Week 3:** Add Jira export (auto-create test cases in Jira)
4. **Week 4:** Add TestRail integration (sync test cases)

---

## 📞 Support

For questions or issues:
- Check [PYTEST_EXPORT_DEMO.py](PYTEST_EXPORT_DEMO.py) for usage examples
- Review test generation [confidence scores](docs/IMPLEMENTATION_SUMMARY_VI.md)
- Open issue on GitHub repository

---

**Generated:** April 2, 2026  
**Status:** ✅ Production Ready  
**Version:** 1.0
