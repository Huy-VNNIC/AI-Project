# 🧪 Testing Guide - Unified Test & Task Generation

## Quick Test Steps

### Step 1: Start Both Systems
```bash
cd /home/dtu/AI-Project/AI-Project
bash START_BOTH_SYSTEMS.sh
```

Wait for the output:
```
╔═══════════════════════════════════════════════════════════════╗
║                   ✅ SYSTEMS STARTED                          ║
╚═══════════════════════════════════════════════════════════════╝

📱 Access the systems:
  Main UI:             http://localhost:8000
  Requirement Analyzer:  http://localhost:8000/docs
  Test Generator:        http://localhost:8001/docs

```

### Step 2: Open the Unified UI
Go to: **http://localhost:8000**

You should see:
- Header with theme toggle (🌙)
- System status cards showing both systems are online (✓)
- Two side-by-side panels (Analyzer & Test Generator)

---

## 📋 Test Case 1: Authentication Feature

### Left Panel (Requirement Analyzer)
**Input:**
```
Users need to login with email and password
System must validate email format before assignment
Password must be at least 8 characters long
System should lock account after 5 failed login attempts
```

**Expected Output:**
- Status: "Analysis complete!"
- JSON showing parsed requirements
- Identified actors, actions, and preconditions

### Right Panel (Test Generator)
**Input:**
```
Users should be able to create accounts
System must encrypt passwords before storage
Email confirmation is required before account activation
```

**Expected Output:**
- Status: "Generated X test cases!"
- Test cases with IDs, titles, and expected results
- Mix of positive, negative, edge, and security tests

---

## 📊 Test Case 2: E-Commerce Workflow

### Left Panel
**Input:**
```
As a customer, I want to browse products so that I can find what I need
As a system admin, I want to manage inventory so that stock is accurate
As a developer, I need an API to process payments securely
```

**Expected Result:**
- Parsed user stories
- Identified requirements and acceptance criteria
- Task breakdown

### Right Panel
**Input:**
```
Customer can add items to cart
Items in cart cannot exceed quantity
Checkout must show total price calculation
Payment must be validated before processing
```

**Expected Result:**
- Generated test cases (Positive, Negative, Edge, Security)
- Test data and expected results
- Coverage metrics

---

## 🔒 Test Case 3: Security Features

### Left Panel
**Input:**
```
All user data must be encrypted at rest
System should implement two-factor authentication
Session tokens must expire after 30 minutes
API endpoints must validate CSRF tokens
```

**Expected Output:**
- Security requirements identified
- Validation rules extracted

### Right Panel
**Input:**
```
System should prevent SQL injection attacks
XSS vulnerabilities must be mitigated
CORS headers must be properly configured
Rate limiting must block excessive requests
```

**Expected Output:**
- Security test cases
- Vulnerability check tests
- Attack vector tests

---

## 🚀 Test Case 4: Performance & Scalability

### Left Panel
**Input:**
```
System must handle 1000 concurrent users
API response time should be under 500ms
Database queries must be optimized
Reports must generate within 5 minutes
```

**Expected Output:**
- Performance requirements parsed
- Metrics identified

### Right Panel
**Input:**
```
System should process 100 requests per second
Memory usage should not exceed 2GB
CPU utilization should stay below 80%
```

**Expected Output:**
- Performance test cases
- Load test scenarios
- Benchmark tests

---

## 🎯 Test Case 5: Simple Login

### Both Panels
**Input (Free Text):**
```
User can login with username
System validates credentials
Valid users get access
Invalid credentials show error
```

**Expected Output:**
- Both systems generate test cases
- Results appear in "Results" section
- Tab switcher shows both responses

---

## ✅ Verification Checklist

- [ ] **System Health**
  - [ ] Requirement Analyzer shows "Online" (green)
  - [ ] Test Generator shows "Online" (green)
  - [ ] Status updates every 10 seconds

- [ ] **Analyzer Panel**
  - [ ] Can enter requirements
  - [ ] Format dropdown works
  - [ ] "Analyze Requirements" button is clickable
  - [ ] Results display in JSON format
  - [ ] No errors in browser console

- [ ] **Test Generator Panel**
  - [ ] Can enter requirements
  - [ ] Format dropdown works
  - [ ] "Generate Test Cases" button is clickable
  - [ ] Results show test case count
  - [ ] Different test types are generated

- [ ] **Results Section**
  - [ ] Appears after generating
  - [ ] Can switch between Analyzer/TestGen results
  - [ ] JSON is properly formatted
  - [ ] Results are readable

- [ ] **Theme**
  - [ ] Toggle button works
  - [ ] Dark mode works
  - [ ] Light mode works
  - [ ] Preference is saved

---

## 🔧 API Testing (Advanced)

### Check Unified Health
```bash
curl http://localhost:8000/api/unified/health
```

**Expected Response:**
```json
{
  "analyzer": true,
  "testgen": true,
  "both_online": true
}
```

### Generate with Unified Endpoint
```bash
curl -X POST http://localhost:8000/api/unified/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Users should be able to login",
    "format": "free_text",
    "analyze": true,
    "generate": true
  }'
```

### Get System Status
```bash
curl http://localhost:8000/api/unified/status
```

---

## 📊 Expected Test Output

### Positive Tests (Happy Path)
```json
{
  "id": "TC-001-AUTH-POS-001",
  "title": "Valid user login",
  "precondition": "User has valid credentials",
  "steps": [
    "Enter valid email",
    "Enter valid password",
    "Click login"
  ],
  "expected_result": "User is logged in successfully"
}
```

### Negative Tests (Error Cases)
```json
{
  "id": "TC-001-AUTH-NEG-001",
  "title": "Invalid password",
  "precondition": "User has incorrect password",
  "steps": [
    "Enter valid email",
    "Enter invalid password",
    "Click login"
  ],
  "expected_result": "Error message displayed"
}
```

### Edge Case Tests
```json
{
  "id": "TC-001-AUTH-EDGE-001",
  "title": "Boundary password length",
  "precondition": "Testing password edge cases",
  "steps": [
    "Enter 7-character password (min-1)",
    "Enter 256-character password (max+1)"
  ],
  "expected_result": "Validation errors shown"
}
```

### Security Tests
```json
{
  "id": "TC-001-AUTH-SEC-001",
  "title": "SQL injection prevention",
  "precondition": "Testing SQL injection",
  "steps": [
    "Enter: admin' OR '1'='1",
    "Click login"
  ],
  "expected_result": "Attack is blocked"
}
```

---

## 🐛 Troubleshooting

### Systems Not Starting
```bash
# Kill any existing processes
lsof -ti:8000 | xargs kill -9
lsof -ti:8001 | xargs kill -9

# Try again
bash START_BOTH_SYSTEMS.sh
```

### Systems Show as Offline
- Wait 5-10 seconds after starting
- Check if both terminals show "Server running"
- Check browser console for CORS errors
- Try refreshing the page

### No Results After Click
- Check browser console (F12) for errors
- Verify both systems are online (green status)
- Try simpler input text first
- Check `/docs` endpoints work

### Style Issues (No Colors)
- Refresh page (Ctrl+R or Cmd+R)
- Clear browser cache
- Try different browser
- Check browser console for CSS errors

---

## 📝 Sample Test Scenarios

### Scenario 1: User Registration Feature
**Requirement:** "Users can register with email and password"

**Generated Tests:**
1. Valid registration with correct format
2. Invalid email format rejection
3. Password too short rejection
4. Duplicate email handling
5. SQL injection prevention
6. XSS payload handling

### Scenario 2: Payment Processing
**Requirement:** "System processes payments securely"

**Generated Tests:**
1. Valid payment processing
2. Insufficient funds rejection
3. Invalid card number handling
4. SSL/TLS validation
5. PCI DSS compliance checks
6. Transaction timeout handling

### Scenario 3: File Upload
**Requirement:** "Users can upload documents"

**Generated Tests:**
1. Valid file upload
2. Oversized file rejection
3. Invalid file type handling
4. Virus scanning integration
5. File storage security
6. Concurrent upload handling

---

## 📈 Success Criteria

✅ **You'll know it's working when:**
1. Both status cards show green "Online"
2. You can enter text and click buttons
3. Results appear within 5-10 seconds
4. JSON is properly formatted
5. Test cases have IDs, titles, and expected results
6. Dark/light theme toggle works
7. Status updates automatically

✅ **Your tests are good if:**
1. All test types are generated (Positive, Negative, Edge, Security)
2. Test IDs are sequential
3. Preconditions and steps are specific
4. Expected results are clear
5. Security tests are included
6. Edge cases are covered

---

## 🎓 Next Steps

Once testing is complete:
1. **Review the output** - Check if test cases are realistic
2. **Export results** - Use the `/export/excel` endpoint
3. **Integrate with CI/CD** - Use the REST APIs
4. **Provide feedback** - Help improve the quality
5. **Scale up** - Test with larger documents

---

## 💬 Questions?

If you encounter issues:
1. **Check API docs:**
   - http://localhost:8000/docs
   - http://localhost:8001/docs

2. **Review logs:**
   - Check terminal output for error messages
   - Check browser console (F12) for JavaScript errors

3. **Test endpoints directly:**
   ```bash
   # Test Analyzer
   curl http://localhost:8000/health
   
   # Test Generator
   curl http://localhost:8001/health
   ```

---

**Enjoy testing! 🚀**
