# Integration Guide

> **Last Updated:** April 2, 2026  
> **Version:** 1.0  
> **Audience:** Developers, system integrators, DevOps engineers

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [API Integration](#api-integration)
4. [Webhook Integration](#webhook-integration)
5. [Database Integration](#database-integration)
6. [Third-Party Services](#third-party-services)
7. [Authentication & Security](#authentication--security)
8. [Deployment Integration](#deployment-integration)

---

## Overview

This guide explains how to integrate the Test Case Generation system with other applications, services, and infrastructure.

### Integration Options

- **Direct API Integration** - Call REST endpoints directly
- **Batch Processing** - Process large requirement files asynchronously
- **Webhook Callbacks** - Receive results via webhooks
- **Database Sync** - Store/retrieve data from external databases
- **CI/CD Pipeline** - Automate test generation in build pipelines

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    External Systems                         │
│  (Project Management, DevOps, Documentation, etc.)         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTP/REST API
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Test Case Generation System                     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │   Router Layer (FastAPI)                             │  │
│  │  - /api/v2/test-generation/analyze-file-detailed    │  │
│  │  - /testcase/upload                                 │  │
│  │  - /api/v3/generate                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                      │                                       │
│  ┌──────────────────▼──────────────────────────────────┐   │
│  │   Service Layer                                     │   │
│  │  - File Parsing (RequirementFileParser)            │   │
│  │  - Test Case Generation (AITestCaseGeneratorV2)    │   │
│  │  - NLP Analysis (spaCy)                            │   │
│  └──────────────────────────────────────────────────────┘  │
│                      │                                       │
│  ┌──────────────────▼──────────────────────────────────┐   │
│  │   Data Layer                                        │   │
│  │  - Requirements Repository                          │   │
│  │  - Test Cases Repository                            │   │
│  │  - Analysis Cache                                   │   │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                     ▲
                     │ WebSocket (optional)
                     │
            Status Updates & Results
```

---

## API Integration

### 1. **Synchronous Test Generation**

**Scenario:** Generate test cases and wait for results

**Code Example - Python:**
```python
import requests
import json

# Upload file and get results
url = "http://localhost:8000/api/v2/test-generation/analyze-file-detailed"

with open('requirements.txt', 'rb') as f:
    files = {'file': f}
    data = {'max_tests': 5}
    response = requests.post(url, files=files, data=data)

if response.status_code == 200:
    results = response.json()
    for req in results['detailed']:
        print(f"Requirement: {req['requirement']}")
        print(f"Test Cases Generated: {req['test_cases_count']}")
        print(f"NLP Confidence: {req['nlp_confidence']:.0%}")
else:
    print(f"Error: {response.text}")
```

**Code Example - JavaScript:**
```javascript
async function generateTestCases(file) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('max_tests', 5);
    
    try {
        const response = await fetch(
            'http://localhost:8000/api/v2/test-generation/analyze-file-detailed',
            { method: 'POST', body: formData }
        );
        
        if (!response.ok) throw new Error('API Error');
        
        const results = await response.json();
        console.log(`Generated ${results.total_requirements} requirements`);
        
        return results;
    } catch (error) {
        console.error('Error:', error);
    }
}
```

**Code Example - cURL:**
```bash
curl -X POST http://localhost:8000/api/v2/test-generation/analyze-file-detailed \
  -F "file=@requirements.txt" \
  -F "max_tests=5" \
  -H "Accept: application/json"
```

### 2. **Text-Based Generation**

**Scenario:** Generate test cases directly from requirement text

```bash
curl -X POST http://localhost:8000/api/v3/generate \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "requirements=User can login with email and password" \
  -d "max_tests=3"
```

---

## Webhook Integration

### Setting Up Webhook Callbacks

**Scenario:** Receive automatic notifications when test generation completes

**Implementation (in FastAPI app):**

```python
from typing import Optional

# Store webhook URLs
WEBHOOKS = {}

@router.post("/api/webhooks/register")
async def register_webhook(webhook_url: str, event_type: str = "test_generation_complete"):
    """Register webhook for events"""
    if event_type not in WEBHOOKS:
        WEBHOOKS[event_type] = []
    WEBHOOKS[event_type].append(webhook_url)
    return {"status": "registered", "webhook_url": webhook_url}

async def notify_webhooks(event_type: str, data: dict):
    """Send webhook notifications"""
    if event_type not in WEBHOOKS:
        return
    
    import aiohttp
    async with aiohttp.ClientSession() as session:
        for webhook_url in WEBHOOKS[event_type]:
            try:
                await session.post(webhook_url, json=data)
            except Exception as e:
                print(f"Webhook error: {e}")

# In your generation endpoint:
# After generation completes:
# await notify_webhooks("test_generation_complete", {
#     "requirement_id": "REQ-001",
#     "test_cases_count": 5,
#     "timestamp": datetime.now().isoformat()
# })
```

**Example: Receiving Webhook in Node.js:**

```javascript
const express = require('express');
const app = express();

app.post('/webhooks/test-generation', express.json(), (req, res) => {
    const { requirement_id, test_cases_count } = req.body;
    
    console.log(`Test generation completed for ${requirement_id}`);
    console.log(`Generated ${test_cases_count} test cases`);
    
    // Update your system with results
    updateTestResults(requirement_id, test_cases_count);
    
    res.json({ status: "received" });
});

app.listen(3000, () => {
    // Register webhook
    fetch('http://localhost:8000/api/webhooks/register', {
        method: 'POST',
        body: new URLSearchParams({
            webhook_url: 'http://localhost:3000/webhooks/test-generation',
            event_type: 'test_generation_complete'
        })
    });
});
```

---

## Database Integration

### 1. **MongoDB Integration**

```python
from pymongo import MongoClient
import json

client = MongoClient('mongodb://localhost:27017/')
db = client['test_generation']
requirements_col = db['requirements']
test_cases_col = db['test_cases']

async def store_analysis(analysis_results):
    """Store analysis in MongoDB"""
    for item in analysis_results['detailed']:
        # Store requirement
        requirements_col.insert_one({
            'requirement_id': f"REQ-{item['index']}",
            'text': item['requirement'],
            'nlp_confidence': item['nlp_confidence'],
            'word_count': item['word_count'],
            'created_at': datetime.now()
        })
        
        # Store test cases
        for tc in item['test_cases']:
            test_cases_col.insert_one({
                'requirement_id': f"REQ-{item['index']}",
                'test_case': tc,
                'created_at': datetime.now()
            })
```

### 2. **PostgreSQL Integration**

```python
import asyncpg

async def store_in_postgres(analysis_results):
    """Store analysis in PostgreSQL"""
    conn = await asyncpg.connect('postgresql://user:password@localhost/tests')
    
    for item in analysis_results['detailed']:
        # Insert requirement
        req_id = await conn.fetchval(
            '''INSERT INTO requirements (text, confidence, word_count)
               VALUES ($1, $2, $3) RETURNING id''',
            item['requirement'],
            item['nlp_confidence'],
            item['word_count']
        )
        
        # Insert test cases
        for tc in item['test_cases']:
            await conn.execute(
                '''INSERT INTO test_cases (requirement_id, title, effort)
                   VALUES ($1, $2, $3)''',
                req_id,
                tc['title'],
                tc['estimated_effort_hours']
            )
    
    await conn.close()
```

---

## Third-Party Services

### 1. **Jira Integration**

```python
from jira import JIRA

jira = JIRA('https://your-jira.atlassian.net', auth=('user', 'token'))

async def create_jira_test_cases(analysis_results):
    """Create test cases as Jira issues"""
    for item in analysis_results['detailed']:
        for tc in item['test_cases']:
            issue = jira.create_issue(
                project='TEST',
                issuetype='Test',
                summary=tc['title'],
                description=f"Steps: {json.dumps(tc['steps'])}",
                customfield_10000=item['nlp_confidence']  # Custom field
            )
            print(f"Created Jira issue: {issue.key}")
```

### 2. **GitHub Integration**

```python
import asyncio
from aiohttp import ClientSession

async def create_github_issues(analysis_results, repo_token):
    """Create GitHub issues for test cases"""
    headers = {
        'Authorization': f'token {repo_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    async with ClientSession() as session:
        for item in analysis_results['detailed']:
            for tc in item['test_cases']:
                payload = {
                    'title': tc['title'],
                    'body': f"**Requirement:** {item['requirement']}\n\n**Steps:** {json.dumps(tc['steps'])}",
                    'labels': ['auto-generated', 'test-case']
                }
                
                async with session.post(
                    'https://api.github.com/repos/owner/repo/issues',
                    json=payload,
                    headers=headers
                ) as resp:
                    issue = await resp.json()
                    print(f"Created GitHub issue: {issue['number']}")
```

### 3. **Slack Notifications**

```python
import aiohttp

async def notify_slack(webhook_url, analysis_results):
    """Send test generation summary to Slack"""
    total_tests = sum(
        item['test_cases_count'] 
        for item in analysis_results['detailed']
    )
    
    message = {
        'text': f"📊 Test Generation Complete",
        'blocks': [
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f"✅ *{total_tests} test cases generated* from {analysis_results['total_requirements']} requirements"
                }
            },
            {
                'type': 'context',
                'elements': [{
                    'type': 'mrkdwn',
                    'text': f"File: {analysis_results['filename']}"
                }]
            }
        ]
    }
    
    async with aiohttp.ClientSession() as session:
        await session.post(webhook_url, json=message)
```

---

## Authentication & Security

### 1. **API Key Authentication**

```python
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

VALID_API_KEYS = {
    "test-key-12345": "Internal Tests",
    "prod-key-67890": "Production"
}

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return VALID_API_KEYS[api_key]

@router.post("/api/v2/test-generation/analyze-file-detailed")
async def analyze_file_detailed(
    file: UploadFile = File(...),
    max_tests: int = 10,
    api_key_info: str = Depends(verify_api_key)
):
    """Generate test cases (requires API key)"""
    # Implementation...
```

### 2. **Rate Limiting**

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v2/test-generation/analyze-file-detailed")
@limiter.limit("10/minute")  # 10 requests per minute
async def analyze_file_detailed(request: Request, file: UploadFile):
    # Implementation...
```

---

## Deployment Integration

### Docker Integration

```dockerfile
# Dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY requirement_analyzer/ ./requirement_analyzer/

EXPOSE 8000

CMD ["python", "-m", "requirement_analyzer.api"]
```

**Docker Compose:**

```yaml
version: '3.8'

services:
  test-generator:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
      - MAX_FILE_SIZE=10485760
    volumes:
      - ./uploads:/app/uploads
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Kubernetes Integration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: test-generator-config
data:
  LOG_LEVEL: "INFO"
  MAX_FILE_SIZE: "10485760"

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-generator
spec:
  replicas: 3
  selector:
    matchLabels:
      app: test-generator
  template:
    metadata:
      labels:
        app: test-generator
    spec:
      containers:
      - name: test-generator
        image: test-generator:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: test-generator-config
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
```

---

## Support

- 📖 See [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md) for complete API documentation
- 🔍 See [TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md) for integration issues
- 📊 See [SYSTEM_UPGRADE_PHASE2.md](SYSTEM_UPGRADE_PHASE2.md) for system architecture

---

*Last updated: April 2, 2026*
