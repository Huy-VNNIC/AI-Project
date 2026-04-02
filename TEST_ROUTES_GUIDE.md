# 🧪 Test Routes & Testing Guide

## What Was Added

I've created a comprehensive testing system with multiple test pages and routers to help you test both the **Requirement Analyzer** and **Test Generator** systems.

## New Routes Overview

```
/test                - Main testing hub (navigation center)
/test/analyzer       - Requirement analyzer test page
/test/testgen        - Test case generator test page
/test/unified        - Unified side-by-side interface
/test/comparison    - Compare both systems in parallel
/test/api           - API testing tool with all endpoints
```

## Quick Start

### 1. Start the System
```bash
cd /home/dtu/AI-Project/AI-Project
bash START_BOTH_SYSTEMS.sh
```

### 2. Access Test Center
Open these URLs in your browser:

- **Main Test Hub:** http://localhost:8000/test
- **Analyzer Test:** http://localhost:8000/test/analyzer
- **Test Generator:** http://localhost:8000/test/testgen
- **Side-by-Side:** http://localhost:8000/test/unified
- **Comparison:** http://localhost:8000/test/comparison
- **API Testing:** http://localhost:8000/test/api

## Test Pages Description

### 1. **Main Test Hub** (`/test`)
Central navigation hub with:
- Overview of all systems
- Quick access buttons to each test page
- Available API endpoints list
- System status information

**What you can do:**
- Navigate to different test tools
- See all available API endpoints
- Check system status

### 2. **Analyzer Test Page** (`/test/analyzer`)
Test the Requirement Analyzer component.

**Features:**
- Text input for requirements
- Format selection (Free Text, User Story, Use Case)
- Real-time analysis with responses
- JSON result display

**Example input:**
```
- Users should be able to login with email
- System must validate password strength
- All data must be encrypted
```

### 3. **Test Generator Page** (`/test/testgen`)
Test the Test Case Generation component.

**Features:**
- Requirements input field
- Format selection
- Generate test cases
- View results in JSON format

**Example input:**
```
User login functionality
Password validation
Session management
```

### 4. **Unified Interface** (`/test/unified`)
Side-by-side view of both systems working together.

**Features:**
- Left panel: Requirement Analyzer
- Right panel: Test Generator
- Real-time health monitoring
- Theme toggle (Dark/Light)
- Compare outputs side-by-side

### 5. **Comparison Tool** (`/test/comparison`)
Run both systems with identical input and compare results.

**Features:**
- Single input field
- Parallel execution of both systems
- Side-by-side result display
- Visual comparison capability

### 6. **API Testing Tool** (`/test/api`)
Interactive API endpoint testing without code.

**Supported endpoints:**
- `GET /api/unified/health` - System health check
- `POST /api/v3/generate` - Analyze requirements
- `POST /api/v2/test-generation/generate-test-cases` - Generate tests
- `POST /api/unified/generate` - Run both systems
- `GET /docs` - Swagger UI (opens in new tab)

## File Structure

```
app/routers/
├── test_routes.py (NEW - 400+ lines)
├── unified.py (API endpoints)
├── tasks.py (Task management)
└── __init__.py

app/
├── main.py (UPDATED - added test_routes import)
└── ...

templates/
├── unified_ui.html (Unified interface)
└── ...
```

## Testing Workflows

### Workflow 1: Simple Requirement Analysis
1. Go to http://localhost:8000/test/analyzer
2. Enter requirements: "Users can login with email"
3. Click "Analyze Requirements"
4. View extracted tasks and entities

### Workflow 2: Generate Test Cases
1. Go to http://localhost:8000/test/testgen
2. Enter requirements: "Login functionality with email validation"
3. Click "Generate Test Cases"
4. View generated test scenarios

### Workflow 3: Comparison Testing
1. Go to http://localhost:8000/test/comparison
2. Enter: "User authentication with password reset"
3. Click "Compare Both Systems"
4. See side-by-side results from both systems

### Workflow 4: API Testing
1. Go to http://localhost:8000/test/api
2. Select an endpoint (e.g., "Analyze Requirements")
3. Modify the JSON payload if needed
4. Click "Send Request"
5. View the API response in real-time

## Test Examples

### Example 1: Login Feature
**Input:**
```
Users can login with email and password.
The system validates password strength (min 8 characters, special character).
Session timeout after 30 minutes of inactivity.
Users can reset their password via email.
```

**What to test:**
- Does analyzer extract all features?
- Are test cases comprehensive?
- Does test generator cover all scenarios?

### Example 2: Payment Processing
**Input:**
```
Users can make payments using credit card.
The system encrypts all payment data.
Payment transactions are logged for audit.
Users receive confirmation email after payment.
```

**What to test:**
- Are security aspects identified?
- Are all test scenarios generated?
- Compare accuracy of both systems

### Example 3: User Registration
**Input:**
```
New users can register with email.
Email validation is required.
Password must be strong (8+ chars, numbers, symbols).
Users get welcome email after registration.
```

**What to test:**
- Feature extraction accuracy
- Test case completeness
- Edge case coverage

## Testing Checklist

### Basic Testing Tasks

- [ ] **Test /test page loads correctly**
  - Command: `curl http://localhost:8000/test`
  - Expected: HTML page with test navigation

- [ ] **Test Analyzer page**
  - Go to http://localhost:8000/test/analyzer
  - Enter sample requirements
  - Verify analysis results appear
  - Check JSON format

- [ ] **Test TestGen page**
  - Go to http://localhost:8000/test/testgen
  - Enter sample requirements
  - Verify test cases are generated
  - Check JSON format

- [ ] **Test Comparison tool**
  - Go to http://localhost:8000/test/comparison
  - Enter requirements
  - Verify both systems run in parallel
  - Compare side-by-side results

- [ ] **Test API endpoints**
  - Go to http://localhost:8000/test/api
  - Test each endpoint
  - Verify responses are correct
  - Check error handling

- [ ] **Test Unified interface**
  - Go to http://localhost:8000/test/unified
  - Verify both panels work
  - Test theme toggle
  - Check health monitoring

### Advanced Testing Tasks

- [ ] **Load testing** - Multiple simultaneous requests
- [ ] **Error handling** - Invalid inputs
- [ ] **Large inputs** - Long requirements documents
- [ ] **Format variations** - Different input formats
- [ ] **API documentation** - Visit `/docs` for Swagger UI

## API Endpoints for Testing

### Health Check
```bash
curl http://localhost:8000/api/unified/health
```

### Analyze Requirements
```bash
curl -X POST http://localhost:8000/api/v3/generate \
  -F "text=Users can login" \
  -F "format=free_text"
```

### Generate Test Cases
```bash
curl -X POST http://localhost:8000/api/v2/test-generation/generate-test-cases \
  -F "requirements=User login functionality"
```

### Unified Generation
```bash
curl -X POST http://localhost:8000/api/unified/generate \
  -H "Content-Type: application/json" \
  -d '{"text":"User login","format":"free_text","analyze":true,"generate":true}'
```

## Troubleshooting

### Issue: Port 8000 already in use
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# Restart
bash START_BOTH_SYSTEMS.sh
```

### Issue: Page not loading
1. **Check if system is running:**
   ```bash
   curl http://localhost:8000/api/unified/health
   ```

2. **Wait for models to load:** Usually takes 10-15 seconds after startup

3. **Check logs:**
   ```bash
   tail -100 /tmp/startup3.log
   ```

### Issue: API returning errors
1. Verify requirements text is not empty
2. Check JSON format is valid
3. Try smaller/simpler requirements first
4. Check the `/docs` page for endpoint documentation

## Features of Test Pages

### All Test Pages Include:
- ✅ Simple, clean interface
- ✅ Real-time response display
- ✅ JSON result formatting
- ✅ Error handling and messages
- ✅ No complex icons (pure text/UI)
- ✅ Mobile responsive design
- ✅ Dark/Light theme support (where applicable)
- ✅ Copy-paste friendly output

## Next Steps

1. **Start the system**
   ```bash
   bash START_BOTH_SYSTEMS.sh
   ```

2. **Visit the test hub**
   ```
   http://localhost:8000/test
   ```

3. **Try each test page** and verify functionality

4. **Test with real requirements** from your project

5. **Review API endpoints** at `/docs` for deeper integration

6. **Provide feedback** on what works well and what needs improvement

## Files Modified/Created

- ✅ **Created:** `app/routers/test_routes.py` (400+ lines)
- ✅ **Modified:** `app/main.py` (added test_routes import and registration)
- ✅ **Status:** All changes integrated and ready to use

## Summary

You now have a complete testing system with:
- 6 different test pages
- Side-by-side comparison interface
- Interactive API testing tool
- Comprehensive navigation hub
- Multiple workflows for different testing scenarios

**All test pages are accessible immediately after starting the system!**

---

*Last Updated: 2026-04-02*
*Testing Suite Version: 1.0*
