# 🚀 Quick Test Guide

## Test 1: Run System Test Suite (2 minutes)

Verify all modules work correctly:

```bash
cd rule_based_testgen
python3 test_system.py
```

Expected output:
```
✅ ALL TESTS PASSED!
- Requirements found: 7
- Test cases generated: 45
```

---

## Test 2: Start API Server (5 minutes)

```bash
cd rule_based_testgen
python3 main.py
```

Expected output:
```
Uvicorn running on http://127.0.0.1:8000
Press CTRL+C to quit
```

Then open browser: http://localhost:8000/docs

---

## Test 3: Test via API (without server)

### Option A: Copy this Python code into a terminal

```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/dtu/AI-Project/AI-Project/rule_based_testgen')

from pipeline import TestGenerationPipeline

# Create input text
requirements_text = """
System Requirements:
- User can login with email and password
- System must validate email format
- If login fails, display error message
- Admin can create new user
- When user is created, send confirmation email
- System must encrypt password before storing
- User can reset password by email link
"""

# Process
pipeline = TestGenerationPipeline()
results = pipeline.process_text(requirements_text, "json")

# Display results
print(f"✅ Generated {results['summary']['total_test_cases']} test cases")
print(f"📊 Requirements found: {results['summary']['total_requirements']}")

# Show first 3 tests
print("\n📋 First 3 Test Cases:")
for i, test in enumerate(results['test_cases'][:3], 1):
    print(f"\n{i}. {test['test_id']}: {test['title']}")
    print(f"   Type: {test['test_type']}")
    print(f"   Steps: {test['steps'][:2]}...")
EOF
```

---

## Test 4: Test with Sample Requirements File

```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/dtu/AI-Project/AI-Project/rule_based_testgen')

from pipeline import TestGenerationPipeline

# Read sample requirements
pipeline = TestGenerationPipeline()
results = pipeline.process_file(
    "sample_requirements.txt",
    output_format="json",
    export_path="test_output.json"
)

print(f"✅ Processed: {results['summary']['total_requirements']} requirements")
print(f"📊 Generated: {results['summary']['total_test_cases']} test cases")
print(f"💾 Exported to: {results.get('export_file', 'N/A')}")
EOF
```

---

## Test 5: Test Export Formats

### JSON Export
```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/dtu/AI-Project/AI-Project/rule_based_testgen')

from pipeline import TestGenerationPipeline
from export_handler import ExportHandler
import json

# Generate tests
pipeline = TestGenerationPipeline()
results = pipeline.process_text(
    "User can login with email. System validates email format.",
    output_format="json"
)

# Show JSON structure
print("📋 JSON Output Sample:")
print(json.dumps({
    "total_requirements": results['summary']['total_requirements'],
    "total_test_cases": results['summary']['total_test_cases'],
    "first_test": results['test_cases'][0].to_dict() if results['test_cases'] else None
}, indent=2, default=str))
EOF
```

### Excel Export
```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/dtu/AI-Project/AI-Project/rule_based_testgen')

from pipeline import TestGenerationPipeline

# Generate and export to Excel
pipeline = TestGenerationPipeline()
results = pipeline.process_text(
    "User can login. System validates credentials.",
    output_format="excel",
    export_path="test_results.xlsx"
)

print(f"✅ Excel file created: {results.get('export_file', 'test_results.xlsx')}")
print(f"📊 Contains {results['summary']['total_test_cases']} test cases")
EOF
```

### CSV Export
```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/dtu/AI-Project/AI-Project/rule_based_testgen')

from pipeline import TestGenerationPipeline

# Generate and export to CSV
pipeline = TestGenerationPipeline()
results = pipeline.process_text(
    "User can login. System validates credentials.",
    output_format="csv",
    export_path="test_results.csv"
)

print(f"✅ CSV file created: {results.get('export_file', 'test_results.csv')}")
# Show first few lines
with open(results.get('export_file', 'test_results.csv')) as f:
    lines = f.readlines()
    print("\n📋 CSV Preview:")
    for line in lines[:5]:
        print(line.rstrip())
    if len(lines) > 5:
        print(f"... and {len(lines)-5} more lines")
EOF
```

---

## Test 6: Test Different Domains

The system automatically detects domains and applies domain-specific rules:

```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/dtu/AI-Project/AI-Project/rule_based_testgen')

from pipeline import TestGenerationPipeline

# Banking domain
banking_req = "Customer can transfer money to another account. System must validate account number."
pipeline = TestGenerationPipeline()
results = pipeline.process_text(banking_req)
print(f"🏦 Banking: {results['summary']['total_test_cases']} tests")

# Hotel domain  
hotel_req = "Guest can book a room. System must check room availability."
results = pipeline.process_text(hotel_req)
print(f"🏨 Hotel: {results['summary']['total_test_cases']} tests")

# E-commerce domain
ecom_req = "Customer can add product to cart. System must validate quantity."
results = pipeline.process_text(ecom_req)
print(f"🛒 E-commerce: {results['summary']['total_test_cases']} tests")

# Healthcare domain
health_req = "Patient can schedule appointment. System must check doctor availability."
results = pipeline.process_text(health_req)
print(f"🏥 Healthcare: {results['summary']['total_test_cases']} tests")
EOF
```

---

## Test 7: Performance Test (Large File)

```bash
python3 << 'EOF'
import sys
import time
sys.path.insert(0, '/home/dtu/AI-Project/AI-Project/rule_based_testgen')

from pipeline import TestGenerationPipeline

# Create large sample
large_text = """
- """ + """\n- """.join([f"User can perform action {i}" for i in range(50)])

print("⏱️ Testing performance with 50 requirements...")
start = time.time()

pipeline = TestGenerationPipeline()
results = pipeline.process_text(large_text)

elapsed = time.time() - start
print(f"✅ Completed in {elapsed:.2f} seconds")
print(f"📊 Generated {results['summary']['total_test_cases']} tests from {results['summary']['total_requirements']} requirements")
print(f"⚡ Rate: {results['summary']['total_test_cases']/elapsed:.0f} tests/second")
EOF
```

---

## Test 8: API Server Full Workflow

```bash
# Terminal 1: Start server
cd rule_based_testgen
python3 main.py

# Terminal 2: Test API endpoints
# 1. Health check
curl http://localhost:8000/health

# 2. API stats
curl http://localhost:8000/api/stats | jq .

# 3. Generate from text
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "requirements_text": "User login with email and password",
    "export_format": "json"
  }' | jq '.summary'

# 4. Generate from file
curl -X POST http://localhost:8000/api/generate-file \
  -F "file=@sample_requirements.txt" \
  -F "export_format=excel" \
  -o results.xlsx

echo "✅ Excel file: $(ls -lh results.xlsx | awk '{print $9, $5}')"
```

---

## ✅ Validation Checklist

After running tests:

- [ ] `test_system.py` passes all 6 module tests
- [ ] Pipeline test generates 45+ test cases
- [ ] API server starts without errors
- [ ] Can POST to `/api/generate`
- [ ] Can upload files to `/api/generate-file`
- [ ] Excel export creates valid file
- [ ] Test cases have all fields (id, title, type, steps, expected_result)
- [ ] Different test types generated (positive, negative, edge, security)

---

## 🎯 Test Classification

| Test | Difficulty | Time | What It Tests |
|------|-----------|------|---------------|
| 1. System Test | ⭐ Easy | 2 min | All modules individually |
| 2. Server Start | ⭐ Easy | 1 min | FastAPI startup |
| 3. Python API | ⭐ Easy | 3 min | In-process pipeline |
| 4. File Processing | ⭐ Easy | 2 min | File upload + processing |
| 5. Export Formats | ⭐⭐ Medium | 5 min | JSON/Excel/CSV/Markdown |
| 6. Domains | ⭐⭐ Medium | 5 min | Domain detection + rules |
| 7. Performance | ⭐⭐ Medium | 10 min | Scalability with many requirements |
| 8. Full Workflow | ⭐⭐⭐ Hard | 10 min | Complete REST API usage |

---

## 💡 Tips

- Tests 1-4 work offline (no server needed)
- Test 8 requires server running
- Use `jq` for pretty JSON output (install: `pip install jq`)
- Check `/api/stats` endpoint to see system metrics
- Modify `config.py` to add new domains or rules

---

## 📊 Example Output

When you run Test 1 (System Test):
```
======================================================================
🧪 TESTING RULE-BASED TEST CASE GENERATOR
======================================================================

✓ Processing requirements...
  ✓ Processing complete
  - Requirements found: 7
  - Test cases generated: 45

✅ ALL TESTS PASSED!

📚 Next steps:
1. Run: python main.py
2. Open: http://localhost:8000/docs
3. Try API: http://localhost:8000/api/generate
```

---

**Next:** Read [GETTING_STARTED.md](GETTING_STARTED.md) for detailed setup instructions.
