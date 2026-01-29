# API Examples - Task Generation

Quick reference for testing the task generation API endpoints.

---

## Prerequisites

```bash
# Start server
cd requirement_analyzer
uvicorn api:app --reload --port 8000

# Or with gunicorn (production)
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## Endpoint 1: Generate Tasks (Basic)

**POST** `/generate-tasks`

### Request Body
```json
{
  "text": "Users must be able to register with email and password. System should validate email format and password strength. After registration, send verification email.",
  "max_tasks": 10,
  "mode": "template",
  "epic_name": "User Management Sprint",
  "domain_hint": "ecommerce"
}
```

### cURL Command
```bash
curl -X POST http://localhost:8000/generate-tasks \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Users must be able to register with email and password. System should validate email format and password strength.",
    "max_tasks": 10
  }'
```

### Python Example
```python
import requests

response = requests.post(
    'http://localhost:8000/generate-tasks',
    json={
        'text': 'Users must login with OAuth2. System should support Google and GitHub providers.',
        'max_tasks': 5,
        'mode': 'template'
    }
)

result = response.json()
print(f"Generated {result['total_tasks']} tasks")

for task in result['tasks']:
    print(f"\n{task['title']}")
    print(f"  Priority: {task['priority']}")
    print(f"  Type: {task['type']}")
    print(f"  AC: {len(task['acceptance_criteria'])} criteria")
```

### Response Example
```json
{
  "tasks": [
    {
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Implement user registration for users",
      "description": "The system needs to register users with email and password.",
      "acceptance_criteria": [
        "User can register successfully",
        "System validates input data before register",
        "System provides appropriate feedback",
        "Error handling is implemented"
      ],
      "type": "functional",
      "priority": "High",
      "domain": "ecommerce",
      "role": "Backend",
      "labels": ["registration", "authentication"],
      "story_points": null,
      "estimated_hours": null,
      "confidence": 0.87,
      "source": {
        "sentence": "Users must be able to register with email and password",
        "section": "User Management",
        "doc_offset": [0, 52]
      }
    }
  ],
  "total_tasks": 3,
  "stats": {
    "type_distribution": {
      "functional": 2,
      "security": 1
    },
    "priority_distribution": {
      "High": 2,
      "Medium": 1
    },
    "domain_distribution": {
      "ecommerce": 3
    },
    "role_distribution": {
      "Backend": 2,
      "Frontend": 1
    },
    "avg_confidence": 0.82
  },
  "processing_time": 1.23
}
```

---

## Endpoint 2: Generate Tasks with Estimation

**POST** `/generate-tasks-estimate`

Includes story points allocation based on COCOMO estimator.

### Request Body
```json
{
  "text": "Build e-commerce platform with user authentication, product catalog, shopping cart, and payment integration.",
  "max_tasks": 20,
  "mode": "template",
  "include_story_points": true
}
```

### cURL Command
```bash
curl -X POST http://localhost:8000/generate-tasks-estimate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Implement REST API with JWT authentication. Support CRUD operations for users, products, and orders.",
    "max_tasks": 15
  }'
```

### Python Example
```python
response = requests.post(
    'http://localhost:8000/generate-tasks-estimate',
    json={
        'text': open('requirements.txt').read(),
        'max_tasks': 50
    }
)

result = response.json()

print(f"Total story points: {result.get('total_story_points', 0)}")
print(f"Estimated duration: {result.get('estimated_duration_days', 0)} days")

for task in result['tasks']:
    print(f"{task['story_points']}pts - {task['title']}")
```

### Response (Additional Fields)
```json
{
  "tasks": [...],
  "total_tasks": 12,
  "total_story_points": 47,
  "estimated_duration_days": 15.6,
  "stats": {...},
  "processing_time": 2.45
}
```

---

## Endpoint 3: Upload File & Generate

**POST** `/upload-requirements-generate-tasks`

Upload PDF, DOCX, TXT, or MD file.

### cURL Command (Multipart Form)
```bash
curl -X POST http://localhost:8000/upload-requirements-generate-tasks \
  -F "file=@requirements.pdf" \
  -F "max_tasks=20" \
  -F "mode=template" \
  -F "epic_name=MVP Sprint 1"
```

### Python Example
```python
with open('requirements.pdf', 'rb') as f:
    files = {'file': ('requirements.pdf', f, 'application/pdf')}
    data = {
        'max_tasks': 30,
        'mode': 'template',
        'domain_hint': 'healthcare'
    }
    
    response = requests.post(
        'http://localhost:8000/upload-requirements-generate-tasks',
        files=files,
        data=data
    )

result = response.json()
print(f"Extracted {result['total_tasks']} tasks from PDF")
```

### Supported File Types
- PDF: `.pdf`
- Word: `.docx`, `.doc`
- Text: `.txt`
- Markdown: `.md`

**Max file size**: 50 MB (configurable in `config_task_gen_template.py`)

---

## Endpoint 4: Submit Feedback

**POST** `/tasks/feedback`

Submit user feedback for learning loop.

### Request Body
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "accepted": false,
  "edited_task": {
    "title": "Implement OAuth2 User Authentication",
    "description": "Build secure OAuth2 login flow with Google and GitHub providers...",
    "acceptance_criteria": [
      "User can select OAuth provider",
      "System redirects to provider auth page",
      "Tokens are stored securely"
    ],
    "type": "security",
    "priority": "High",
    "domain": "ecommerce",
    "role": "Backend"
  },
  "comment": "Changed from generic 'user authentication' to specific OAuth2 implementation"
}
```

### cURL Command
```bash
curl -X POST http://localhost:8000/tasks/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "accepted": true,
    "comment": "Perfect! No changes needed."
  }'
```

### Python Example
```python
# Accepted without edit
feedback = {
    'task_id': task['task_id'],
    'accepted': True
}

# Rejected with edit
feedback = {
    'task_id': task['task_id'],
    'accepted': False,
    'edited_task': {
        'title': 'Better title',
        'description': 'More detailed description...',
        'acceptance_criteria': ['AC 1', 'AC 2', 'AC 3'],
        'type': task['type'],
        'priority': task['priority'],
        'domain': task['domain'],
        'role': task['role']
    },
    'comment': 'Made it more specific'
}

response = requests.post(
    'http://localhost:8000/tasks/feedback',
    json=feedback
)

print(response.json()['message'])
# "Feedback received. Thank you!"
```

---

## Batch Processing Example

Generate tasks for multiple documents:

```python
import requests
from pathlib import Path

documents = [
    'requirements_auth.txt',
    'requirements_payments.txt',
    'requirements_analytics.txt'
]

all_tasks = []

for doc_path in documents:
    text = Path(doc_path).read_text()
    
    response = requests.post(
        'http://localhost:8000/generate-tasks',
        json={
            'text': text,
            'max_tasks': 20,
            'epic_name': Path(doc_path).stem
        }
    )
    
    result = response.json()
    all_tasks.extend(result['tasks'])
    print(f"{doc_path}: {result['total_tasks']} tasks")

print(f"\nTotal: {len(all_tasks)} tasks across all documents")

# Export to JSON
import json
with open('all_tasks.json', 'w') as f:
    json.dump(all_tasks, f, indent=2)
```

---

## Error Handling

### 400 Bad Request
```json
{
  "detail": "Text is required and cannot be empty"
}
```

**Causes**:
- Missing `text` field
- Empty text
- Invalid file format

### 413 Payload Too Large
```json
{
  "detail": "File size exceeds maximum allowed (50 MB)"
}
```

**Solution**: Split large files or increase limit in config

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "max_tasks"],
      "msg": "ensure this value is less than or equal to 500",
      "type": "value_error.number.not_le"
    }
  ]
}
```

**Causes**:
- Invalid field types
- Out-of-range values
- Missing required fields

### 500 Internal Server Error
```json
{
  "detail": "Task generation failed: [error details]"
}
```

**Causes**:
- Models not loaded
- spaCy model missing
- Processing error

**Check**: Run `python scripts/task_generation/check_health.py`

---

## Performance Tips

### 1. Batch Similar Requests
Instead of multiple small requests, combine texts:
```python
combined_text = '\n\n'.join([doc1, doc2, doc3])
response = requests.post(
    'http://localhost:8000/generate-tasks',
    json={'text': combined_text, 'max_tasks': 50}
)
```

### 2. Use Domain Hints
Helps classifiers be more accurate:
```python
{'text': text, 'domain_hint': 'healthcare'}
```

### 3. Set Reasonable max_tasks
- 10-20 for quick exploration
- 50-100 for full documents
- Default: 50

### 4. Enable Story Points Only When Needed
Adds ~500ms overhead for COCOMO calculation:
```python
# Faster (no estimation)
/generate-tasks

# Slower (with estimation)
/generate-tasks-estimate
```

---

## Testing Script

Save as `test_api.py`:

```python
import requests
import sys

BASE_URL = 'http://localhost:8000'

def test_basic():
    """Test basic task generation."""
    response = requests.post(
        f'{BASE_URL}/generate-tasks',
        json={
            'text': 'Users must login. System validates credentials.',
            'max_tasks': 5
        }
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result['total_tasks'] > 0
    print(f"✅ Basic generation: {result['total_tasks']} tasks")

def test_estimation():
    """Test with story points."""
    response = requests.post(
        f'{BASE_URL}/generate-tasks-estimate',
        json={
            'text': 'Build REST API with authentication.',
            'max_tasks': 10
        }
    )
    
    assert response.status_code == 200
    result = response.json()
    assert 'total_story_points' in result
    print(f"✅ Estimation: {result['total_story_points']} points")

def test_feedback():
    """Test feedback submission."""
    response = requests.post(
        f'{BASE_URL}/tasks/feedback',
        json={
            'task_id': 'test-123',
            'accepted': True
        }
    )
    
    assert response.status_code == 200
    print("✅ Feedback submission")

if __name__ == '__main__':
    try:
        test_basic()
        test_estimation()
        test_feedback()
        print("\n🎉 All API tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
```

Run:
```bash
python test_api.py
```

---

## API Documentation

When server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Interactive testing and full schema available.

---

## Rate Limiting (Recommended)

For production, add rate limiting:

```python
# In api.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/generate-tasks")
@limiter.limit("10/minute")
async def generate_tasks_endpoint(...):
    ...
```

---

## Monitoring

Track key metrics:
```python
import time
import logging

logger = logging.getLogger(__name__)

start = time.time()
result = pipeline.generate_tasks(text)
duration = time.time() - start

logger.info(f"Generated {result.total_tasks} tasks in {duration:.2f}s")
logger.info(f"Avg confidence: {result.stats['avg_confidence']:.2f}")
```

---

**For full API specification**: See auto-generated docs at `/docs` when server is running.
