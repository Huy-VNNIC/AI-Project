# 🚀 Quick Access Routes - Your Test System is Ready!

## System Status
✅ **Running on http://localhost:8000**
- Main System: http://0.0.0.0:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📋 All Available Routes

### 🧪 Test Pages (`/test`)
| Route | Purpose | Type |
|-------|---------|------|
| `/test` | **Main Test Hub** - Navigation center | GET |
| `/test/analyzer` | Requirement Analyzer test page | GET |
| `/test/testgen` | Test case generator test page | GET |
| `/test/unified` | Side-by-side both systems | GET |
| `/test/comparison` | Compare outputs from both systems | GET |
| `/test/api` | Interactive API endpoint tester | GET |

### 🧬 Test Case Generation (`/testcase`)
| Route | Purpose | Type |
|-------|---------|------|
| `/testcase` | **Main test case generator page** | GET |
| `/testcase/` | Alternative access | GET |
| `/testcase/generation` | Alias for main page | GET |
| `/testcase/dashboard` | Test generation dashboard & stats | GET |
| `/testcase/generate` | API endpoint for programmatic generation | POST |

### 🔌 API Endpoints
| Route | Purpose | Type |
|-------|---------|------|
| `/api/unified/health` | Check system health | GET |
| `/api/unified/status` | Detailed system status | GET |
| `/api/v3/generate` | Analyze requirements (Analyzer) | POST |
| `/api/v2/test-generation/generate-test-cases` | Generate test cases | POST |
| `/api/unified/generate` | Both systems in one call | POST |

### 📚 Documentation
| Route | Purpose | Type |
|-------|---------|------|
| `/docs` | **Swagger UI** - Interactive API documentation | GET |
| `/redoc` | **ReDoc** - Alternative API documentation | GET |
| `/openapi.json` | OpenAPI specification | GET |

---

## 🎯 Quick Start Links

### For Testing
1. **Start Here**: http://localhost:8000/test
2. **Analyze Requirements**: http://localhost:8000/test/analyzer
3. **Generate Tests**: http://localhost:8000/test/testgen
4. **Advanced Generator**: http://localhost:8000/testcase

### For API Testing
1. **Interactive Tester**: http://localhost:8000/test/api
2. **API Docs**: http://localhost:8000/docs
3. **Compare Systems**: http://localhost:8000/test/comparison

### For Comparison
- http://localhost:8000/test/unified - Side-by-side view
- http://localhost:8000/test/comparison - Direct comparison

---

## 📊 Test Types Supported

The test case generator creates:
- ✅ **Positive Tests** - Valid inputs, expected behavior
- ✅ **Negative Tests** - Invalid inputs, error handling
- ✅ **Boundary Tests** - Edge cases and limits
- ✅ **Security Tests** - Authentication, authorization, data protection

Each test includes:
- 🎯 Test ID and title
- 📝 Type classification
- 🔧 Preconditions required
- 📋 Step-by-step instructions
- ✔️ Expected results
- 📊 Confidence percentage (AI model certainty)

---

## 💡 Example Usage

### Generate Test Cases via Web UI
1. Visit: http://localhost:8000/testcase
2. Enter requirements
3. Select test types
4. Set coverage target
5. Click "Generate Test Cases"
6. Export results (JSON/CSV) or copy to clipboard

### Generate via API
```bash
curl -X POST http://localhost:8000/api/v2/test-generation/generate-test-cases \
  -F "requirements=User authentication with email and password"
```

### Use Unified API
```bash
curl -X POST http://localhost:8000/api/unified/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "User login functionality",
    "format": "free_text",
    "analyze": true,
    "generate": true
  }'
```

---

## 🔧 System Management

### Check System Status
```bash
curl http://localhost:8000/api/unified/health
```

### Get Detailed Status
```bash
curl http://localhost:8000/api/unified/status
```

### Restart System
```bash
# Kill processes
pkill -f "uvicorn"

# Start again
cd /home/dtu/AI-Project/AI-Project
bash START_BOTH_SYSTEMS.sh
```

### View Logs
```bash
tail -f /tmp/startup_corrected.log
```

---

## 📱 Access Methods

### Local Machine
- http://localhost:8000

### From Another Machine (on same network)
- http://<YOUR_IP>:8000

### With SSH Port Forward
```bash
ssh -L 8000:localhost:8000 user@host
# Then visit http://localhost:8000
```

---

## ✨ Feature Highlights

**Web Interfaces**:
- 🎨 Beautiful neumorphism design
- 🌙 Dark/Light theme toggle
- 📱 Mobile responsive
- ⚡ Real-time updates
- 🔒 No external icons (pure text/CSS)

**Generators**:
- 🚀 ML-powered generation
- 📊 Automatic coverage analysis
- 💯 Confidence scoring
- 🔄 Multiple test type support

**Export**:
- 📥 JSON export for integration
- 📊 CSV export for spreadsheets
- 📋 Copy to clipboard for quick use

---

## 🎓 Test Page Descriptions

### `/test` - Test Hub
Central navigation page showing all available test tools with descriptions and quick access buttons.

### `/test/analyzer`
Test the Requirement Analyzer component:
- Input: Free text, user stories, or use cases
- Output: Extracted entities, tasks, and NLP analysis
- Format: JSON structured data

### `/test/testgen`
Test the Test Case Generator:
- Input: Requirements description
- Output: Detailed test case scenarios
- Includes: Preconditions, steps, expected results

### `/test/unified`
**Side-by-side interface** showing both systems:
- Left: Requirement Analyzer
- Right: Test Case Generator
- Features: Health monitoring, theme toggle, auto-updates

### `/test/comparison`
**Direct comparison tool**:
- Single input analyzed by both systems
- Parallel execution
- Side-by-side result display
- Useful for accuracy comparison

### `/test/api`
**Interactive API testing** (no code needed):
- Select endpoint from dropdown
- Edit JSON payload
- Send request
- View response in real-time

### `/testcase` - Advanced Generator
Professional test case generation with:
- Multiple test type selection
- Coverage percentage targeting
- Individual test result display
- Export functionality (JSON, CSV)
- Coverage visualization

---

## 📖 Documentation Files Created

1. **TEST_ROUTES_GUIDE.md** - Comprehensive guide for /test routes
2. **TESTCASE_ROUTER_GUIDE.md** - Complete test case generation guide
3. **QUICK_ACCESS_ROUTES.md** - This file (quick reference)

---

## 🆘 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Port 8000 in use | `lsof -ti:8000 \| xargs kill -9` |
| Page returns 404 | Wait 10-15 seconds, refresh page |
| API timeout | Models loading, wait and retry |
| No results | Ensure requirements text is not empty |
| Export not working | Try copying to clipboard instead |

---

## 🎯 Testing Workflows

### Workflow 1: Quick Test
1. Go to `/test/testgen`
2. Enter requirements
3. Click "Generate Test Cases"
4. View results

### Workflow 2: Detailed Analysis  
1. Go to `/test/analyzer`
2. Analyze requirements deeply
3. See extracted entities
4. Review NLP results

### Workflow 3: System Comparison
1. Go to `/test/comparison`
2. Enter requirements
3. See both systems' output
4. Compare results

### Workflow 4: Professional Testing
1. Go to `/testcase`
2. Select test types
3. Set coverage target
4. Generate and export

---

## 💾 Export Formats

### JSON Export
```json
{
  "test_cases": [
    {
      "title": "Test case title",
      "type": "Positive",
      "preconditions": "Setup needed",
      "steps": ["Step 1", "Step 2"],
      "expected_result": "Expected output",
      "confidence": 0.95
    }
  ],
  "coverage_percentage": 87.5,
  "total_count": 12
}
```

### CSV Export
```
TC ID,Title,Type,Preconditions,Steps,Expected Result,Confidence
TC-001,"Test title","Positive","Setup","Steps...","Result",95%
```

---

## 🚀 Getting Started Right Now!

1. **All systems are ready** - no additional setup needed!
2. **Visit test hub**: http://localhost:8000/test
3. **Try test case generator**: http://localhost:8000/testcase
4. **Check API docs**: http://localhost:8000/docs

---

**Status: ✅ SYSTEM FULLY OPERATIONAL**

*Latest Update: 2026-04-02*
*Routes Added: 6 test pages + 2 testcase pages + APIs*
*All systems integrated and tested ✓*
