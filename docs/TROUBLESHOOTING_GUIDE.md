# Troubleshooting Guide

> **Last Updated:** April 2, 2026  
> **Version:** 1.0  
> **Audience:** Users experiencing issues, support engineers

## Table of Contents

1. [Quick Solutions](#quick-solutions)
2. [File Upload Issues](#file-upload-issues)
3. [Test Generation Issues](#test-generation-issues)
4. [API Issues](#api-issues)
5. [Quality & Validation Issues](#quality--validation-issues)
6. [Performance Issues](#performance-issues)
7. [Browser & Environment Issues](#browser--environment-issues)
8. [Getting Help](#getting-help)

---

## Quick Solutions

### The System Isn't Working!

**First, try these:**

| Issue | Solution | Time |
|-------|----------|------|
| Page won't load | Refresh browser (Ctrl+F5) | 10 sec |
| Upload button disabled | Check file size < 10MB | 1 min |
| No results generated | Check requirement clarity | 2 min |
| API error 500 | Check logs, restart system | 5 min |
| Session timeout | Log in again | 1 min |

**Still broken? Follow specific section below.** ↓

---

## File Upload Issues

### ❌ "File Upload Failed" Error

**Symptom:**
```
Error: File upload failed
No file received by server
```

**Solutions:**
1. **Check file size**
   ```
   Maximum file size: 10 MB
   To check file size: Right-click file > Properties > Size
   ```

2. **Check file format**
   ```
   Supported: TXT, CSV
   Not supported: PDF, DOCX, XLS, etc.
   ```

3. **Verify file integrity**
   - File not corrupted
   - File not password-protected
   - File path not too long (> 255 chars)

4. **Clear browser cache**
   ```
   Chrome: Ctrl+Shift+Delete > Clear all
   Firefox: Ctrl+Shift+Delete > Everything
   Safari: Cmd+Option+E
   ```

5. **Try different browser**
   - If works in Chrome but not Firefox, it's a browser issue
   - Clear that browser's cache and try again

**Still failing?** Use the API directly:
```bash
curl -X POST http://localhost:8000/api/v2/test-generation/analyze-file-detailed \
  -F "file=@requirements.txt" \
  -F "max_tests=5"
```

---

### ❌ "File Too Large" Error

**Symptom:**
```
Error: File exceeds maximum size of 10 MB
```

**Solution:**
1. **Check actual file size**
   ```bash
   ls -lh requirements.txt
   # Output: -rw-r--r-- 1 user group 12M requirements.txt (TOO LARGE)
   ```

2. **Split large file into smaller chunks**
   ```bash
   # Split into 2MB chunks
   split -b 2M large_file.txt requirements_part_
   
   # Process each part separately
   ```

3. **Remove duplicates if applicable**
   ```bash
   sort requirements.txt | uniq > requirements_unique.txt
   ```

4. **Clean up empty lines**
   ```bash
   grep -v '^[[:space:]]*$' requirements.txt > requirements_clean.txt
   ```

---

### ❌ "Invalid File Format" Error

**Symptom:**
```
Error: This file format is not supported
Supported formats: TXT, CSV
```

**Solutions:**

**For PDF Files:**
```
1. Convert PDF to TEXT:
   pdftotext document.pdf requirements.txt
   
2. Then upload requirements.txt
```

**For Excel/CSV Files:**
```
1. Save as CSV instead of XLS
   File > Export > CSV
   
2. Or save as TXT
   File > Save As > Text Format
```

**For Word Documents:**
```
1. Open in Word
2. File > Save As > Plain Text (.txt)
3. Upload .txt file
```

---

### ❌ Missing Headers in CSV

**Symptom:**
```
System skipped first line
No requirements extracted
```

**Solution:**
CSV parser skips header row automatically. If your data looks like:
```csv
Requirement,Priority,Status
User can login,High,Done
Admin views logs,High,Done
```

The first row is recognized as header and skipped. This is correct.

**If first line contains actual requirement:**
```csv
First requirement here,High,Done
User can login,High,Done
```

Add a header row:
```csv
Requirement,Priority,Status
First requirement here,High,Done
User can login,High,Done
```

---

### ⚠️ "Encoding Error" - Special Characters Not Processed

**Symptom:**
```
Special characters shown as ??? or garbled
Non-ASCII characters not recognized
```

**Solution:**
Save file with UTF-8 encoding:

**Windows:**
- Notepad: File > Save As > UTF-8

**Mac/Linux:**
```bash
# Convert to UTF-8
iconv -f ISO-8859-1 -t UTF-8 old_file.txt > new_file.txt

# Or use Python
python3 -c "
with open('file.txt', 'r', encoding='ISO-8859-1') as f:
    data = f.read()
with open('file_utf8.txt', 'w', encoding='utf-8') as f:
    f.write(data)
"
```

---

## Test Generation Issues

### ❌ "No Test Cases Generated"

**Symptom:**
```
JSON Response:
{
  "test_cases": [],
  "total": 0
}
```

**Causes & Solutions:**

1. **Requirements too vague (Quality Gate)**
   ```
   Likely issue: Requirement failed NLP confidence check (< 65%)
   
   Your requirement:
   "User can do things"  ← Too vague
   
   Better requirement:
   "User can log in with email and password"  ← Clear action
   ```

   **Fix:** Make requirements more specific:
   ```
   ❌ CHANGE: "System handles user data"
   ✅ TO: "System validates and stores user data with encryption"
   ```

2. **File uploaded but is empty**
   ```
   Check file has actual content:
   
   Linux/Mac:
   wc -l requirements.txt  (# shows line count)
   cat requirements.txt    (# displays content)
   
   Windows:
   findstr /c:"" requirements.txt  (# shows line count)
   type requirements.txt           (# displays content)
   ```

3. **Requirements all rejected by quality gate**
   Get detailed feedback:
   ```bash
   curl -X POST http://localhost:8000/api/v2/test-generation/analyze-file-detailed \
     -F "file=@requirements.txt" | jq '.analysis[] | {requirement, errors}'
   ```

4. **System overloaded / timeout**
   - Reduce max_tests parameter
   - Try with smaller file first
   - Check system resources (see Performance Issues)

---

### ⚠️ "Generated Tests Seem Low Quality"

**Symptom:**
```
Test cases are generic or don't match requirement details
```

**Solutions:**

1. **Improve requirement clarity**
   ```
   Current:
   "User authentication system"
   
   Better:
   "Users can log in with email and password, and be rejected if either is incorrect"
   ```

2. **Add more context to requirements**
   ```
   Current:
   "Process payment"
   
   Better:
   "System processes credit card payment via Stripe API and returns transaction ID or error"
   ```

3. **Specify error conditions**
   ```
   Current:
   "Upload file"
   
   Better:
   "System accepts PDF files up to 10MB, rejects oversized files with error message"
   ```

---

### ⚠️ "Duplicate Test Cases Generated"

**Symptom:**
```
Similar test cases repeated multiple times
```

**Note:** System has deduplication enabled. If you're seeing duplicates:

1. **They're not actually duplicates**
   - Review test case steps carefully
   - Different expected results
   - Different preconditions

2. **File has duplicate requirements**
   ```bash
   # Find duplicates
   sort requirements.txt | uniq -d
   
   # Remove duplicates
   sort requirements.txt | uniq > requirements_unique.txt
   ```

3. **Different aspect of same feature**
   - "User can log in" (happy path)
   - "User rejected if password wrong" (error path)
   - Both are needed—not duplicates

---

## API Issues

### ❌ "Error 404 - Endpoint Not Found"

**Symptom:**
```
Error 404: POST /api/v2/test-generation/analyze-file-detailed not found
```

**Solutions:**

1. **Verify API is running**
   ```bash
   curl http://localhost:8000/health
   
   Expected:
   {"status":"healthy","service":"ai-estimation-api"}
   ```

2. **Check endpoint URL spelling**
   ```bash
   ❌ WRONG: /api/v1/analyze (doesn't exist)
   ✅ RIGHT: /api/v2/test-generation/analyze-file-detailed
   ```

3. **Restart API if needed**
   ```bash
   # Kill existing process
   lsof -ti:8000 | xargs kill -9
   
   # Restart
   cd /home/dtu/AI-Project/AI-Project
   source .venv/bin/activate
   python -m requirement_analyzer.api > /tmp/api.log 2>&1 &
   
   # Verify
   sleep 3
   curl http://localhost:8000/health
   ```

---

### ❌ "Error 422 - Unprocessable Entity"

**Symptom:**
```
Error: 422 Unprocessable Entity
detail: [body content issue]
```

**Solutions:**

1. **Check Content-Type header**
   ```bash
   ❌ WRONG with JSON content-type:
   curl -X POST http://localhost:8000/api/v2/test-generation/analyze-file \
     -H "Content-Type: application/json" \
     -d '{"requirements": "text"}'
   
   ✅ CORRECT with form data:
   curl -X POST http://localhost:8000/api/v2/test-generation/analyze-file-detailed \
     -F "file=@requirements.txt"
   ```

2. **Verify request body format**
   ```bash
   # File upload endpoint expects form data
   -F "file=@filename"
   -F "max_tests=5"
   
   # NOT JSON
   -d '{"file": "data"}'
   ```

3. **Check required parameters**
   ```
   Required for /analyze-file-detailed:
   - file (form field): actual file upload
   
   Optional:
   - max_tests (default 5)
   - detailed (default true)
   ```

---

### ❌ "Error 500 - Internal Server Error"

**Symptom:**
```
Error: 500 Internal Server Error
Something went wrong on the server
```

**Solutions:**

1. **Check server logs**
   ```bash
   tail -100 /tmp/api.log
   
   # Look for error messages
   # Common issues: out of memory, file permissions, database errors
   ```

2. **Restart API server**
   ```bash
   lsof -ti:8000 | xargs kill -9
   sleep 2
   
   cd /home/dtu/AI-Project/AI-Project
   source .venv/bin/activate
   python -m requirement_analyzer.api > /tmp/api.log 2>&1 &
   ```

3. **Check system resources**
   ```bash
   # CPU and Memory
   top -bn1 | head -20
   
   # Disk space
   df -h
   
   # Available memory
   free -h
   ```

4. **Review error details**
   ```bash
   tail -50 /tmp/api.log | grep -i error
   ```

---

### ❌ "Connection Refused" / "Cannot Connect"

**Symptom:**
```
Error: Cannot connect to localhost:8000
Connection refused
```

**Solutions:**

1. **Verify API is running**
   ```bash
   # Check if port 8000 is listening
   lsof -i :8000
   
   # Expected output shows Python process
   # If no output, API not running
   ```

2. **Start API if not running**
   ```bash
   cd /home/dtu/AI-Project/AI-Project
   source .venv/bin/activate
   python -m requirement_analyzer.api > /tmp/api.log 2>&1 &
   
   # Wait for startup
   sleep 3
   
   # Verify
   curl http://localhost:8000/health
   ```

3. **Check port 8000 not in use by other process**
   ```bash
   # See what's on port 8000
   netstat -tulpn | grep 8000
   
   # If something else is using it, kill it
   lsof -ti:8000 | xargs kill -9
   ```

4. **Check firewall if accessing from different machine**
   ```bash
   # Allow port 8000
   sudo ufw allow 8000  # Ubuntu/Debian
   sudo firewall-cmd --add-port=8000/tcp  # RedHat/CentOS
   ```

---

## Quality & Validation Issues

### ⚠️ "Low NLP Confidence Score"

**Symptom:**
```
Requirement skipped - NLP confidence 45% (needs > 65%)
```

**What it means:**
AI system wasn't confident interpreting your requirement.

**Solutions:**

1. **Make requirement more specific**
   ```
   ❌ VAGUE (confidence 35%):
   "User system"
   
   ✅ SPECIFIC (confidence 92%):
   "User can log in with email and password"
   ```

2. **Add clear action verbs**
   ```
   ❌ WEAK:
   "Login functionality"
   
   ✅ STRONG:
   "System authenticates user with email and password"
   ```

3. **Include who, what, and how**
   ```
   ❌ INCOMPLETE:
   "Validation required"
   
   ✅ COMPLETE:
   "System validates email format using regex pattern and rejects invalid addresses"
   ```

4. **Check requirement length**
   ```
   Too short (< 5 words): May be ambiguous
   Too long (> 50 words): Split into multiple requirements
   
   IDEAL: 10-20 words
   ```

---

### ⚠️ "Requirement Rejected by Quality Gate"

**Symptom:**
```
⚠️ SKIPPED (ambiguous): "This doesn't include enough detail"
```

**Solutions:**
Add more specific details:

| Current | Problem | Better |
|---------|---------|--------|
| "Handle errors" | Too vague | "System catches validation errors and shows error message to user" |
| "Support users" | What support? | "System allows users to contact support via email form" |
| "Works fast" | Not measurable | "System returns search results within 500 milliseconds" |
| "Secure system" | Vague security | "System encrypts passwords using bcrypt and enforces 8+ char passwords" |

---

## Performance Issues

### ⏱️ "Processing Takes Too Long"

**Symptom:**
```
Request takes 30+ seconds to process
```

**Causes & Solutions:**

1. **File is too large**
   ```bash
   # Check file size
   ls -lh requirements.txt
   
   # If > 5MB:
   # Split file and process in batches
   split -l 50 requirements.txt req_batch_
   ```

2. **max_tests is too high**
   ```bash
   # Reduce for faster processing
   # SLOW: max_tests=50
   # FAST: max_tests=5
   
   curl -F "file=@requirements.txt" -F "max_tests=5" ...
   ```

3. **System under heavy load**
   ```bash
   # Check CPU and memory usage
   top -bn1 | head -20
   
   # If > 90% used, wait and retry
   ```

4. **NLP processing bottleneck**
   ```
   Confirm processing is running:
   
   tail -f /tmp/api.log
   Look for: "Analyzing requirement: User can..."
   ```

---

### 💾 "Out of Memory" Error

**Symptom:**
```
Error: MemoryError
System ran out of memory
```

**Solutions:**

1. **Check available memory**
   ```bash
   free -h
   
   # If < 500MB free, stop other processes
   ```

2. **Reduce file size**
   ```bash
   # Remove duplicate requirements
   sort requirements.txt | uniq > requirements_clean.txt
   
   # Check new size
   ls -lh requirements_clean.txt
   ```

3. **Lower max_tests**
   ```
   max_tests=50 (uses more memory)
   max_tests=3  (uses less memory)
   ```

4. **Restart system**
   ```bash
   # Kill API process
   lsof -ti:8000 | xargs kill -9
   
   # Wait for memory to free
   sleep 5
   
   # Restart
   python -m requirement_analyzer.api > /tmp/api.log 2>&1 &
   ```

---

## Browser & Environment Issues

### 🌐 "Web Page Won't Load"

**Symptom:**
```
Connection timeout or blank page
```

**Solutions:**

1. **Verify API is running**
   ```bash
   curl http://localhost:8000/health
   
   Should return: {"status":"healthy"}
   ```

2. **Clear browser cache**
   ```
   Chrome/Edge: Ctrl+Shift+Delete
   Firefox: Ctrl+Shift+Delete
   Safari: Cmd+Shift+Delete
   ```

3. **Try incognito/private mode**
   - Chrome/Edge: Ctrl+Shift+N
   - Firefox: Ctrl+Shift+P
   
   If works in incognito, clear cache (step 2)

4. **Try different browser**
   - If works in Chrome but not Firefox, it's a browser issue
   - Try Safari, Edge, etc.

---

### 🔐 "CORS Error" / "Blocked by Browser"

**Symptom:**
```
Error: Cross-Origin Request Blocked
```

**Common when:**
- API on one domain, web page on different domain
- API on port 8000, web page on port 3000

**Solution:**
- For local testing: Ensure API and web pages on same port
- For production: Configure CORS headers in API

---

### 🌍 "Cannot Access from Different Machine"

**Symptom:**
```
Works on localhost:8000
Doesn't work on another-machine:8000
```

**Solutions:**

1. **Verify API allows remote connections**
   ```bash
   # Check API binding (should be 0.0.0.0, not just 127.0.0.1)
   lsof -i :8000
   ```

2. **Check firewall**
   ```bash
   # Open port 8000
   sudo ufw allow 8000        # Ubuntu
   sudo firewall-cmd --add-port=8000/tcp --permanent  # CentOS
   ```

3. **Use machine IP instead of localhost**
   ```bash
   # Find machine IP
   hostname -I
   
   # Use that IP from other machine
   http://192.168.1.100:8000
   ```

---

## Getting Help

### Information to Provide When Asking for Help

When reporting an issue, include:

```
1. What were you trying to do?
   - Upload file? Call API? View web page?

2. What error did you get?
   - Exact error message (screenshots helpful)

3. What have you already tried?
   - Steps you've taken to fix it

4. Environment details:
   - Operating System (Windows/Mac/Linux)
   - Browser (Chrome/Firefox/Safari)
   - File type and size

5. Relevant logs:
   tail -50 /tmp/api.log
   curl \-v [command]  # verbose output
```

### Still Stuck? Try These

1. **Restart everything**
   ```bash
   # Kill API
   lsof -ti:8000 | xargs kill -9
   
   # Clear caches
   cd /home/dtu/AI-Project/AI-Project
   rm -rf __pycache__ .pytest_cache
   
   # Restart
   source .venv/bin/activate
   python -m requirement_analyzer.api > /tmp/api.log 2>&1 &
   ```

2. **Check logs for details**
   ```bash
   tail -100 /tmp/api.log
   ```

3. **Test with curl command**
   ```bash
   # Simple health check
   curl http://localhost:8000/health
   ```

4. **Review other documentation**
   - [FILE_UPLOAD_GUIDE.md](FILE_UPLOAD_GUIDE.md)
   - [REQUIREMENTS_FORMAT_GUIDE.md](REQUIREMENTS_FORMAT_GUIDE.md)
   - [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md)

---

*Last updated: April 2, 2026*
