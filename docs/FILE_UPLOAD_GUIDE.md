# 📄 File Upload & Requirement Analysis Guide

## Overview

The **File Upload Module** provides a comprehensive solution for uploading requirement files and analyzing them to generate detailed test cases. The system extracts each requirement, analyzes it using NLP, and generates tailored test cases with metrics.

## Features

### ✅ Core Features
- **Drag-and-Drop Upload** - Easy file upload with drag-drop interface
- **Multi-Format Support** - TXT, CSV file formats
- **Line-by-Line Analysis** - Extract and analyze each requirement individually
- **Detailed Metrics** - Word count, character count, NLP confidence score
- **Test Case Generation** - Automatic test case generation per requirement
- **Effort Estimation** - Automated effort calculation in hours
- **Export Options** - Download results as JSON or CSV

### ✅ Analysis Metrics
For each requirement, the system extracts:
- **Word Count** - Number of words in requirement
- **Character Count** - Total characters (including spaces)
- **NLP Confidence** - Quality of requirement parsing (0-100%)
- **Test Cases Count** - Number of test cases generated
- **Average Effort** - Estimated effort in hours

### ✅ Test Case Details
For each generated test case:
- **ID** - Unique test case identifier (e.g., TC-001)
- **Title** - Descriptive test case title
- **Scenario Type** - happy_path, negative, validation, etc.
- **Priority** - HIGH, MEDIUM, LOW
- **Estimated Effort** - Hours required to execute
- **Confidence** - NLP confidence score (0-100%)
- **Steps Count** - Number of test execution steps

## Usage Guide

### Method 1: Web Interface

#### 1. Navigate to Upload Page
```
URL: http://localhost:8000/testcase/upload
```

#### 2. Upload File
- Click on the upload zone or drag-drop a file
- Supported formats: `.txt`, `.csv`
- File size: No limit (tested with 1MB+ files)

#### 3. Configure Settings
- **Max Test Cases per Requirement**: 1-50 (default: 10)
  - Higher values generate more comprehensive test suites
  - Lower values for quick analysis

#### 4. Analyze
- Click "Analyze & Generate Test Cases"
- Wait for processing (typically 1-2 seconds per requirement)

#### 5. Review Results
- See statistics dashboard (total requirements, test cases, avg confidence)
- Browse each requirement with detailed breakdown
- Review generated test cases

#### 6. Download Results
- **JSON Format** - Full data structure for programmatic use
- **CSV Format** - Spreadsheet-ready format for Excel/Sheets

### Method 2: API Endpoint

#### Endpoint Details
```bash
POST /api/v2/test-generation/analyze-file-detailed
```

#### Parameters
| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `file` | File | Required | - | TXT or CSV file containing requirements |
| `max_tests` | Integer | 10 | 1-50 | Max test cases per requirement |

#### Request Example
```bash
curl -X POST http://localhost:8000/api/v2/test-generation/analyze-file-detailed \
  -F "file=@requirements.txt" \
  -F "max_tests=5"
```

#### Response Format
```json
{
  "status": "success",
  "filename": "requirements.txt",
  "total_requirements": 11,
  "detailed": [
    {
      "index": 1,
      "requirement": "User Authentication System",
      "word_count": 3,
      "character_count": 24,
      "nlp_confidence": 0.65,
      "test_cases_count": 5,
      "avg_effort": 1.2,
      "test_cases": [
        {
          "id": "TC-001",
          "title": "Happy Path: User Login",
          "scenario_type": "happy_path",
          "priority": "MEDIUM",
          "estimated_effort_hours": 1.03,
          "confidence": 0.79,
          "steps_count": 5
        }
      ]
    }
  ]
}
```

## File Format Specifications

### TXT Format
```
User Authentication System
When a registered user enters valid email and password the system must authenticate
The system must validate email format before accepting credentials
Password must be at least 8 characters with special characters
Failed login attempts must be logged
Account locks after 5 failed attempts
Users can reset password via email
```

**Rules:**
- One requirement per line
- Empty lines are skipped
- Lines starting with `#` are treated as comments
- Supports multi-word requirements

### CSV Format
```csv
ID,Requirement Description,Priority
1,User can login with email and password,High
2,System validates email format,High
3,Password requires special characters,Medium
```

**Rules:**
- First column contains requirement description
- Header row is skipped
- Other columns are optional
- Requirements with empty description are skipped

## Quality Gates & Validation

### NLP Confidence Threshold
```
< 55% - Too ambiguous (SKIPPED)
55-75% - Acceptable quality
75-85% - Good quality
> 85% - Excellent quality
```

### Requirement Quality Checklist
| Aspect | Good Example | Poor Example |
|--------|--------------|--------------|
| Clarity | "User can login with email" | "User can do normal actions" |
| Specificity | "Account locks after 5 failed attempts" | "System should behave correctly" |
| Quantifiable | "Password ≥ 8 characters" | "Password should be strong" |
| Action-oriented | "System validates email format" | "Email validation" |

## Examples

### Example 1: Basic Authentication Requirement
**Input:**
```
When a registered user enters valid email and password the system must authenticate the user
```

**Output:**
```
- Requirements analyzed: 1
- Test cases generated: 5
- NLP Confidence: 82%
- Average effort: 1.0 hour

Test Cases:
1. TC-001: Happy Path - User Login (1.03h)
2. TC-002: Invalid Password Error (0.85h)
3. TC-003: Account Lock After Failures (1.2h)
4. TC-004: Email Format Validation (0.8h)
5. TC-005: Session Timeout (0.9h)
```

### Example 2: Multi-Requirement Analysis
**Input File (requirements.txt):**
```
User Registration
Users can create account with email and password
System validates email is unique
Password must be minimum 8 characters
User receives confirmation email
Account activation requires email click
```

**Output:**
```
- Total requirements: 6
- Total test cases: 30
- Average confidence: 76%

Requirement 1: "User Registration"
├─ Words: 2 | Chars: 18 | Confidence: 68%
├─ Test Cases: 5
└─ Avg Effort: 1.1h

Requirement 2: "Users can create account with email and password"
├─ Words: 9 | Chars: 51 | Confidence: 85%
├─ Test Cases: 5
└─ Avg Effort: 1.2h
...
```

## Advanced Usage

### Batch Processing
```bash
# Process all requirement files in folder
for file in requirements/*.txt; do
  curl -X POST http://localhost:8000/api/v2/test-generation/analyze-file-detailed \
    -F "file=@$file" \
    -F "max_tests=5"
done
```

### Integration with CI/CD
```bash
#!/bin/bash
# requirements_analysis.sh

FILE=$1
OUTPUT_FILE="${FILE%.txt}_analysis.json"

curl -X POST http://localhost:8000/api/v2/test-generation/analyze-file-detailed \
  -F "file=@$FILE" \
  -F "max_tests=10" \
  -o "$OUTPUT_FILE"

# Check if analysis successful
if grep -q '"status":"success"' "$OUTPUT_FILE"; then
  echo "✅ Analysis successful: $OUTPUT_FILE"
  exit 0
else
  echo "❌ Analysis failed"
  exit 1
fi
```

### Custom Analysis Script
```python
import requests
import json

def analyze_requirements(file_path, max_tests=10):
    """Analyze requirements file"""
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {'max_tests': max_tests}
        
        response = requests.post(
            'http://localhost:8000/api/v2/test-generation/analyze-file-detailed',
            files=files,
            data=data
        )
    
    result = response.json()
    
    # Print summary
    print(f"Analyzed: {result['total_requirements']} requirements")
    
    # Print per-requirement details
    for req in result['detailed']:
        print(f"\n[{req['index']}] {req['requirement'][:50]}...")
        print(f"  NLP Confidence: {req['nlp_confidence']:.1%}")
        print(f"  Test Cases: {req['test_cases_count']}")
        print(f"  Effort: {req['avg_effort']:.1f}h")
    
    return result

# Usage
results = analyze_requirements('requirements.txt', max_tests=5)
with open('analysis_results.json', 'w') as f:
    json.dump(results, f, indent=2)
```

## Performance Considerations

### Processing Time
| Requirement Count | Typical Time | Max Tests |
|------------------|--------------|-----------|
| 1-5 | < 5s | 10 |
| 5-10 | 5-10s | 10 |
| 10-20 | 10-20s | 5 |
| 20+ | > 20s | 3 |

### Optimization Tips
1. **Reduce max_tests** for large files (set to 3-5)
2. **Clear requirements** - Better NLP parsing → faster processing
3. **Batch files** - Process smaller files (10-15 requirements each)
4. **Run during off-peak** - Avoid concurrent requests

## Troubleshooting

### Issue: "No requirements found in file"
**Cause:** File is empty or all lines are comments
**Solution:** Ensure file has at least one non-empty, non-comment line

### Issue: Low NLP Confidence (< 55%)
**Cause:** Requirement is too vague or ambiguous
**Solution:** Rewrite requirement with:
- Clear actor (user, system, admin)
- Specific action (login, validate, display)
- Expected behavior

**Before:** "System should handle errors"
**After:** "System must display error message when login fails"

### Issue: No test cases generated
**Cause:** Requirement didn't meet quality threshold (65%)
**Solution:** Review requirement clarity and resubmit

### Issue: Upload fails with "Unsupported file type"
**Cause:** File format is not TXT or CSV
**Solution:** Use only `.txt` or `.csv` extensions

## API Error Codes

| Code | Error | Cause | Solution |
|------|-------|-------|----------|
| 400 | No requirements found | Empty file | Add requirements to file |
| 422 | Ambiguous requirement | Low NLP confidence | Improve requirement clarity |
| 500 | Could not analyze | Server error | Check API logs |
| 413 | File too large | File size exceeded | Split into smaller files |

## Best Practices

### ✅ Writing Good Requirements
```
✓ "When user enters invalid password, system displays error message"
✓ "System must validate email format before accepting user data"
✓ "Account locks after 5 consecutive failed login attempts"

✗ "User authentication"
✗ "System should work correctly"
✗ "Do validation"
```

### ✅ File Organization
```
requirements/
├── authentication.txt    (10-15 requirements)
├── payment.txt          (10-15 requirements)
├── reporting.txt        (10-15 requirements)
└── integration.txt      (10-15 requirements)
```

### ✅ Analysis Workflow
1. Upload file
2. Review statistics (look for < 60% confidence items)
3. Download JSON for detailed review
4. Improve low-confidence requirements
5. Re-upload improved file
6. Export final results as CSV/JSON

## Support & Resources

### Documentation
- [Main API Documentation](../docs/API_DOCUMENTATION_GUIDE.md)
- [Test Case Generation](../docs/GENERATION_MODES.md)
- [Architecture Overview](../docs/ARCHITECTURE.md)

### API Endpoints
- **Text Input:** POST `/api/v2/test-generation/generate-test-cases`
- **File Upload:** POST `/api/v2/test-generation/analyze-file-detailed`
- **UI Pages:** GET `/testcase`, GET `/testcase/upload`

### Example Files
- [Sample Requirements](../datasets/sample_requirements.txt)
- [Sample CSV](../datasets/sample_requirements.csv)

## Changelog

### Version 1.0 (April 2, 2026)
- ✅ Initial release
- ✅ File upload UI with drag-drop
- ✅ TXT and CSV format support
- ✅ Detailed requirement analysis
- ✅ JSON and CSV export
- ✅ NLP confidence scoring
- ✅ Effort estimation per test case

---

**Last Updated:** April 2, 2026  
**Maintained By:** AI-Project Team  
**License:** MIT
