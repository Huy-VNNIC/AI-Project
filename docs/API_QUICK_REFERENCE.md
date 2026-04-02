# API Quick Reference

## Base URL
```
http://localhost:8000
```

## Authentication
No authentication required for current version.

---

## 1. Text-Based Test Case Generation

### Endpoint
```
POST /api/v2/test-generation/generate-test-cases
```

### Description
Generate test cases directly from text requirements (no file upload needed).

### Parameters

| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| `requirements` | string | - | ✅ Yes | Requirement text or multiple requirements separated by newlines |
| `max_tests` | integer | 50 | ❌ No | Maximum number of test cases to generate |
| `threshold` | float | 0.5 | ❌ No | Confidence threshold (0.0-1.0) for filtering test cases |

### Request Examples

#### cURL
```bash
curl -X POST http://localhost:8000/api/v2/test-generation/generate-test-cases \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": "When user enters valid email and password the system authenticates the user",
    "max_tests": 10,
    "threshold": 0.5
  }'
```

#### Python
```python
import requests

url = "http://localhost:8000/api/v2/test-generation/generate-test-cases"
data = {
    "requirements": "User can login with email and password",
    "max_tests": 10,
    "threshold": 0.5
}
response = requests.post(url, json=data)
result = response.json()
print(f"Generated {len(result['test_cases'])} test cases")
```

#### JavaScript/Fetch
```javascript
const data = {
  requirements: "When system receives valid login credentials it authenticates the user",
  max_tests: 10,
  threshold: 0.5
};

fetch('http://localhost:8000/api/v2/test-generation/generate-test-cases', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(data)
})
.then(response => response.json())
.then(data => {
  console.log(`Generated ${data.test_cases.length} test cases`);
  console.log(`Average confidence: ${(data.summary.avg_confidence * 100).toFixed(1)}%`);
});
```

### Response Structure

#### Success Response (200 OK)
```json
{
  "status": "success",
  "test_cases": [
    {
      "id": "TC-GENE-AUTH-001",
      "requirement_id": "REQ-GE-001",
      "title": "Happy Path: User Login",
      "description": "User enters valid credentials and system authenticates",
      "scenario_type": "happy_path",
      "priority": "MEDIUM",
      "risk_level": "LOW",
      "estimated_effort_hours": 1.03,
      "preconditions": ["User is registered", "System is ready"],
      "test_data": { "email": "valid", "password": "valid" },
      "steps": [
        {
          "order": 1,
          "action": "Open login page",
          "expected": "Login form displays",
          "actor": "user",
          "tool": "browser"
        }
      ],
      "expected_result": "User authenticated successfully",
      "postconditions": ["User session created", "Dashboard loaded"],
      "confidence": {
        "overall_score": 0.796,
        "score_percentage": "79.6%",
        "components": {
          "nlp_parsing": 0.55,
          "test_coverage": 0.824,
          "domain_knowledge": 0.65,
          "traceability": 1.0,
          "completeness": 1.0
        }
      },
      "effort": {
        "estimated_minutes": 62,
        "estimated_hours": 1.03,
        "category": "heavy"
      }
    }
  ],
  "summary": {
    "total_test_cases": 5,
    "avg_confidence": 0.815,
    "avg_effort_hours": 1.05,
    "generation_time_ms": 125.4
  },
  "errors": []
}
```

#### Error Response (4xx/5xx)
```json
{
  "status": "error",
  "detail": "Requirements cannot be empty",
  "error_code": "INVALID_INPUT"
}
```

---

## 2. File Upload & Analysis

### Endpoint
```
POST /api/v2/test-generation/analyze-file-detailed
```

### Description
Upload a requirements file (TXT or CSV) and get detailed analysis per requirement.

### Parameters

| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| `file` | file | - | ✅ Yes | TXT or CSV file containing requirements |
| `max_tests` | integer | 10 | ❌ No | Max test cases per requirement (1-50) |

### Request Examples

#### cURL
```bash
curl -X POST http://localhost:8000/api/v2/test-generation/analyze-file-detailed \
  -F "file=@requirements.txt" \
  -F "max_tests=5"
```

#### Python
```python
import requests

with open('requirements.txt', 'rb') as f:
    files = {'file': f}
    data = {'max_tests': 5}
    response = requests.post(
        'http://localhost:8000/api/v2/test-generation/analyze-file-detailed',
        files=files,
        data=data
    )

result = response.json()
print(f"Total requirements: {result['total_requirements']}")
for item in result['detailed']:
    print(f"  [{item['index']}] {item['requirement'][:50]}...")
    print(f"      Confidence: {item['nlp_confidence']:.1%}")
    print(f"      Test cases: {item['test_cases_count']}")
```

#### JavaScript/FormData
```javascript
const fileInput = document.getElementById('fileInput');
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('max_tests', 5);

fetch('http://localhost:8000/api/v2/test-generation/analyze-file-detailed', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log(`Analyzed ${data.total_requirements} requirements`);
  data.detailed.forEach(item => {
    console.log(`[${item.index}] ${item.requirement.slice(0, 50)}...`);
    console.log(`  Words: ${item.word_count}, Confidence: ${(item.nlp_confidence*100).toFixed(1)}%`);
  });
});
```

### Response Structure

#### Success Response (200 OK)
```json
{
  "status": "success",
  "filename": "requirements.txt",
  "total_requirements": 3,
  "detailed": [
    {
      "index": 1,
      "requirement": "User can login with email and password",
      "word_count": 7,
      "character_count": 42,
      "nlp_confidence": 0.82,
      "test_cases_count": 5,
      "avg_effort": 1.02,
      "test_cases": [
        {
          "id": "TC-GE-001",
          "title": "Happy Path: User Login",
          "scenario_type": "happy_path",
          "priority": "MEDIUM",
          "estimated_effort_hours": 1.03,
          "confidence": 0.796,
          "steps_count": 5
        }
      ]
    },
    {
      "index": 2,
      "requirement": "System must validate email format",
      "word_count": 6,
      "character_count": 35,
      "nlp_confidence": 0.75,
      "test_cases_count": 4,
      "avg_effort": 0.85,
      "test_cases": [...]
    }
  ]
}
```

---

## 3. UI Pages

### Test Case Generator (Main)
```
GET /testcase
```
- Main interface for text-based test case generation
- Side-by-side input/output layout
- Real-time test case preview

### File Upload Page
```
GET /testcase/upload
```
- Drag-and-drop file upload interface
- Detailed per-requirement analysis view
- Export to JSON/CSV buttons
- Statistics dashboard

### Test Hub
```
GET /test
```
- Navigation hub for all test pages
- Links to different testing modes

---

## Status Codes

| Code | Status | Meaning |
|------|--------|---------|
| 200 | OK | Request successful |
| 400 | Bad Request | Missing/invalid parameters |
| 422 | Unprocessable Entity | Requirements don't meet quality threshold |
| 500 | Internal Server Error | Server-side processing error |

---

## Common Use Cases

### Use Case 1: Quick Single Requirement Analysis
```bash
curl -X POST http://localhost:8000/api/v2/test-generation/generate-test-cases \
  -H "Content-Type: application/json" \
  -d '{"requirements":"User logs in with valid credentials"}'
```

### Use Case 2: Batch File Processing
```bash
for file in requirements/*.txt; do
  echo "Processing $file..."
  curl -X POST http://localhost:8000/api/v2/test-generation/analyze-file-detailed \
    -F "file=@$file" \
    > "${file%.txt}_analysis.json"
done
```

### Use Case 3: Quality Filtering
```python
import requests

response = requests.post(
    'http://localhost:8000/api/v2/test-generation/analyze-file-detailed',
    files={'file': open('requirements.txt', 'rb')},
    data={'max_tests': 10}
)

data = response.json()

# Filter by confidence
high_quality = [
    item for item in data['detailed']
    if item['nlp_confidence'] >= 0.75
]

print(f"High quality requirements: {len(high_quality)}/{len(data['detailed'])}")
```

### Use Case 4: Export Processing
```bash
# Analyze file
curl -X POST http://localhost:8000/api/v2/test-generation/analyze-file-detailed \
  -F "file=@requirements.txt" \
  > analysis.json

# Process JSON
python process_analysis.py analysis.json

# Convert to CSV for Excel
jq -r '.detailed[] | [.index, .requirement, .word_count, .nlp_confidence] | @csv' \
  analysis.json > analysis.csv
```

---

## Error Handling

### Common Errors

#### Error: Ambiguous Requirement
```json
{
  "status": "error",
  "detail": "⚠️ SKIPPED (ambiguous): requirements - NLP confidence 55.0% < 65%. Please specify: actor, action, and expected behavior clearly."
}
```

**Solution:** Rewrite requirement with clearer action and expected behavior

#### Error: Empty File
```json
{
  "status": "error",
  "message": "No requirements found in file"
}
```

**Solution:** Ensure file has at least one non-empty requirement line

#### Error: Invalid File Format
```json
{
  "status": "error",
  "message": "Unsupported file type: pdf"
}
```

**Solution:** Convert file to TXT or CSV format

---

## Performance Tips

1. **Batch Size:** Process 10-15 requirements per file
2. **Max Tests:** Use 3-5 for large files, 10+ for small files
3. **Threshold:** Default 0.5 works for most cases
4. **Concurrency:** Submit requests sequentially for stability

---

## Response Examples

### Minimal Response (1 requirement, raw)
```
Status: 200 OK
Size: ~5KB
Time: <100ms
Test Cases: 1-3
```

### Medium Response (10 requirements)
```
Status: 200 OK
Size: ~50KB
Time: 5-10s
Test Cases: 30-50
```

### Large Response (50 requirements)
```
Status: 200 OK
Size: ~200KB
Time: 30-60s
Test Cases: 150-250
```

---

## SDKs & Libraries

### Python
```python
import requests

class TestCaseGenerator:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def generate_from_text(self, requirements, max_tests=10):
        response = requests.post(
            f"{self.base_url}/api/v2/test-generation/generate-test-cases",
            json={"requirements": requirements, "max_tests": max_tests}
        )
        return response.json()
    
    def analyze_file(self, file_path, max_tests=5):
        with open(file_path, 'rb') as f:
            response = requests.post(
                f"{self.base_url}/api/v2/test-generation/analyze-file-detailed",
                files={'file': f},
                data={'max_tests': max_tests}
            )
        return response.json()

# Usage
gen = TestCaseGenerator()
result = gen.generate_from_text("User can login")
print(f"Generated {len(result['test_cases'])} test cases")
```

---

## Monitoring & Logging

### Check API Health
```bash
curl http://localhost:8000/health
# {"status":"healthy","service":"ai-estimation-api"}
```

### Check API Logs
```bash
tail -f /tmp/api_v2.log
```

### Metrics
```bash
# Count test cases generated per request
grep "Generated.*tests" /tmp/api_v2.log | tail -10
```

---

## Rate Limiting
Currently no rate limiting enabled. Recommended:
- Max 10 concurrent requests
- Max 1000 test cases per hour
- File size limit: 5MB

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | Apr 2, 2026 | Added file upload, detailed analysis, quality gates |
| 1.0 | Mar 15, 2026 | Initial release, text-based generation |

---

## Support

**API Endpoint Status:** ✅ ACTIVE  
**Documentation:** Available in `/docs/`  
**Issue Reporting:** Create GitHub issue with API details

---

*Last Updated: April 2, 2026*
