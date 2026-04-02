# 🧪 Test Scenarios for Custom AI

## Scenario 1: Simple Feature
```bash
Requirements: "User should be able to login"
Expected: 5-8 test cases, avg confidence > 0.90
```

## Scenario 2: With Validation
```bash
Requirements: "User must login with email (valid format) and password (8+ chars)"
Expected: 8-12 test cases, identifies validation rules
```

## Scenario 3: Security Feature
```bash
Requirements: "User login. Prevent SQL injection. Lock after 3 failed attempts"
Expected: 9-15 test cases, detects security risks
```

## Scenario 4: Complex Multi-Feature
```bash
Requirements: 
- User login with email and password
- Email validation (RFC 5322)
- Password requirements (8+ chars, uppercase, lowercase, numbers)
- Account lock after 3 failed attempts
- Session timeout after 30 mins
- Two-factor authentication (2FA) support

Expected: 12-20 test cases, comprehensive analysis
```

## Scenario 5: API Endpoint
```bash
Requirements: "POST /api/users/login with email and password. Returns JWT token. Handle authentication failures"
Expected: Test cases for various HTTP responses, authentication flows
```

---

## How to Read Results

### ✅ Good Results
```json
{
  "status": "success",
  "test_cases": [7 test cases],
  "summary": {
    "avg_confidence": 0.96,
    "total_test_cases": 7
  },
  "analysis": {
    "entities": 2,
    "edge_cases": 5,
    "complexity": 0.1
  }
}
```
**Interpretation:**
- Status = success ✅
- Good number of tests ✅
- High confidence (0.96) ✅
- AI found edge cases ✅

### ⚠️ Check This
```json
{
  "test_cases": [1 only],
  "summary": {
    "avg_confidence": 0.5
  }
}
```
**Interpretation:**
- Very few test cases (might be too simple requirement)
- Low confidence (requirement unclear?)
- Try more detailed requirement

---

## Common Test Results

| Requirement | Tests | Confidence | Time | Analysis |
|-------------|-------|-----------|------|----------|
| "User login" | 5-7 | 0.92-0.98 | 3-4s | 2 entities, 5 edge cases |
| "User login with validation" | 8-12 | 0.88-0.96 | 3-5s | 3 entities, 8 edge cases |
| "Complex auth system" | 12-18 | 0.85-0.95 | 4-6s | 5+ entities, 10+ edge cases |

---

## Troubleshooting

### No tests generated
❌ Empty requirement
✅ Solution: Provide clear requirement text

### Low confidence scores
❌ Vague requirement
✅ Solution: Be more specific

### Slow response (10+ seconds)
❌ First run (spaCy model loading)
✅ Solution: Second request will be faster

### API Error 422
❌ Invalid JSON payload
✅ Solution: Check JSON syntax

### API Error 500
❌ Server error
✅ Solution: Check server logs, restart if needed

---

## Batch Testing

Run multiple requirements at once:

```bash
# Test 1
curl -X POST http://localhost:8000/api/v2/test-generation/generate-ai \
  -H "Content-Type: application/json" \
  -d '{"requirements": "Login with email"}' | jq '.summary'

# Test 2
curl -X POST http://localhost:8000/api/v2/test-generation/generate-ai \
  -H "Content-Type: application/json" \
  -d '{"requirements": "Payment processing with credit card"}' | jq '.summary'

# Test 3
curl -X POST http://localhost:8000/api/v2/test-generation/generate-ai \
  -H "Content-Type: application/json" \
  -d '{"requirements": "File upload with virus scanning"}' | jq '.summary'
```

---

## Advanced: Parse Full Response

```bash
curl -s http://localhost:8000/api/v2/test-generation/generate-ai \
  -H "Content-Type: application/json" \
  -d '{"requirements": "User login"}' | python3 << 'EOF'
import json, sys
data = json.load(sys.stdin)

print("="*60)
print(f"Total Tests: {len(data['test_cases'])}")
print(f"Avg Confidence: {data['summary']['avg_confidence']:.2%}")
print(f"\nEdge Cases Detected:")
for ec in data['analysis']['edge_cases']:
    print(f"  - {ec}")
print(f"\nFirst 3 Tests:")
for i, tc in enumerate(data['test_cases'][:3], 1):
    print(f"{i}. {tc['title']} ({tc['ai_confidence']:.0%})")
print("="*60)
EOF
```

