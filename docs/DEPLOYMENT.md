# Production Deployment Guide

How to deploy the task generation system to production.

---

## Overview

**Tech Stack**:
- FastAPI (Python 3.10+)
- Gunicorn (WSGI server)
- Nginx (reverse proxy)
- Linux (Ubuntu 20.04+ recommended)

**Requirements**:
- 4 GB RAM minimum (8 GB recommended)
- 10 GB disk space (for models + data)
- CPU: 2+ cores
- (Optional) GPU for LLM mode

---

## Deployment Options

### Option 1: Simple (Single Server)
- FastAPI + Gunicorn
- Serves API directly
- Good for: Low traffic, testing

### Option 2: Production (Load Balanced)
- Nginx → N × (Gunicorn + FastAPI)
- Horizontal scaling
- Good for: Production, high traffic

### Option 3: Docker (Containerized)
- Docker Compose
- Easy deployment
- Good for: Consistent environments

---

## Option 1: Simple Deployment

### Step 1: Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10+
sudo apt install python3.10 python3.10-venv python3-pip -y

# Install system dependencies
sudo apt install build-essential libssl-dev libffi-dev python3-dev -y
```

### Step 2: Clone & Setup

```bash
# Clone repository
git clone <your-repo-url>
cd AI-Project

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### Step 3: Train Models

```bash
# Run training pipeline (15 min)
bash scripts/task_generation/run_full_pipeline.sh

# Verify models
ls models/task_gen/
# Should see: requirement_detector_*.joblib, type_*.joblib, etc.
```

### Step 4: Configure

```bash
# Copy config template
cp config_task_gen_template.py config_task_gen.py

# Edit settings (optional)
nano config_task_gen.py

# Set environment variables
export PYTHONPATH=/path/to/AI-Project:$PYTHONPATH
export API_HOST=0.0.0.0
export API_PORT=8000
```

### Step 5: Run with Gunicorn

```bash
cd requirement_analyzer

# Test with Uvicorn first
uvicorn api:app --host 0.0.0.0 --port 8000

# Production: Gunicorn + Uvicorn workers
gunicorn api:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 300 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  --log-level info
```

**Gunicorn Options**:
- `-w 4`: 4 worker processes (= CPU cores)
- `--timeout 300`: 5-minute timeout (for large documents)
- `--bind 0.0.0.0:8000`: Listen on all interfaces

### Step 6: Systemd Service (Auto-restart)

Create `/etc/systemd/system/task-gen-api.service`:

```ini
[Unit]
Description=Task Generation API
After=network.target

[Service]
Type=notify
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/AI-Project/requirement_analyzer
Environment="PATH=/home/ubuntu/AI-Project/venv/bin"
Environment="PYTHONPATH=/home/ubuntu/AI-Project"
ExecStart=/home/ubuntu/AI-Project/venv/bin/gunicorn api:app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 300 \
    --access-logfile /home/ubuntu/AI-Project/logs/access.log \
    --error-logfile /home/ubuntu/AI-Project/logs/error.log
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable & Start**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable task-gen-api
sudo systemctl start task-gen-api

# Check status
sudo systemctl status task-gen-api

# View logs
sudo journalctl -u task-gen-api -f
```

---

## Option 2: Production with Nginx

### Step 1: Install Nginx

```bash
sudo apt install nginx -y
```

### Step 2: Configure Nginx

Create `/etc/nginx/sites-available/task-gen-api`:

```nginx
upstream task_gen_backend {
    # Load balancing across workers
    server 127.0.0.1:8000;
    # Add more if running multiple instances:
    # server 127.0.0.1:8001;
    # server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name your-domain.com;  # Change this

    # Request size limit (for file uploads)
    client_max_body_size 50M;

    # Timeouts
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;

    # Logging
    access_log /var/log/nginx/task-gen-access.log;
    error_log /var/log/nginx/task-gen-error.log;

    # API endpoints
    location / {
        proxy_pass http://task_gen_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://task_gen_backend/health;
        access_log off;
    }
}
```

**Enable site**:
```bash
sudo ln -s /etc/nginx/sites-available/task-gen-api /etc/nginx/sites-enabled/
sudo nginx -t  # Test config
sudo systemctl restart nginx
```

### Step 3: HTTPS (Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Step 4: Firewall

```bash
# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Deny direct access to API port
sudo ufw deny 8000/tcp

sudo ufw enable
```

---

## Option 3: Docker Deployment

### Step 1: Create Dockerfile

`Dockerfile.task-gen`:

```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy code
COPY requirement_analyzer/ /app/requirement_analyzer/
COPY models/ /app/models/
COPY config_task_gen.py /app/

# Expose port
EXPOSE 8000

# Run Gunicorn
CMD ["gunicorn", "requirement_analyzer.api:app", \
     "-w", "4", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "300"]
```

### Step 2: Docker Compose

`docker-compose.task-gen.yml`:

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.task-gen
    container_name: task-gen-api
    restart: always
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs
    environment:
      - PYTHONPATH=/app
      - LOG_LEVEL=INFO
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    container_name: task-gen-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
```

### Step 3: Build & Run

```bash
# Build image
docker-compose -f docker-compose.task-gen.yml build

# Start services
docker-compose -f docker-compose.task-gen.yml up -d

# Check logs
docker-compose -f docker-compose.task-gen.yml logs -f api

# Scale API instances
docker-compose -f docker-compose.task-gen.yml up -d --scale api=4
```

---

## Performance Tuning

### 1. Worker Configuration

**CPU-bound** (template mode):
```bash
# Workers = (2 × CPU cores) + 1
gunicorn -w 9  # For 4 cores
```

**I/O-bound** (LLM API mode):
```bash
# More workers (waiting on API calls)
gunicorn -w 16
```

### 2. Model Loading

Pre-load models in workers:
```python
# In api.py
from requirement_analyzer.task_gen import get_pipeline

# Load once per worker
task_pipeline = get_pipeline(mode='template')

@app.on_event("startup")
async def startup_event():
    logger.info("Models loaded in worker")
```

### 3. Caching

Add Redis for caching:
```python
import redis
from functools import lru_cache

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@lru_cache(maxsize=100)
def cached_generate(text_hash):
    # Check Redis first
    cached = redis_client.get(text_hash)
    if cached:
        return json.loads(cached)
    
    # Generate
    result = pipeline.generate_tasks(text)
    
    # Cache for 1 hour
    redis_client.setex(text_hash, 3600, json.dumps(result))
    return result
```

### 4. Database (for feedback)

Use PostgreSQL:
```bash
sudo apt install postgresql postgresql-contrib -y
sudo -u postgres createdb task_gen_feedback
```

Schema:
```sql
CREATE TABLE task_feedback (
    id SERIAL PRIMARY KEY,
    task_id UUID NOT NULL,
    accepted BOOLEAN NOT NULL,
    edited_task JSONB,
    comment TEXT,
    user_id UUID,
    submitted_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_task_feedback_task_id ON task_feedback(task_id);
CREATE INDEX idx_task_feedback_accepted ON task_feedback(accepted);
```

---

## Monitoring & Logging

### 1. Application Logs

```python
# In api.py
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/task_generation.log',
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### 2. Metrics (Prometheus)

Add prometheus client:
```bash
pip install prometheus-client
```

```python
from prometheus_client import Counter, Histogram, make_asgi_app

# Metrics
request_count = Counter('task_gen_requests_total', 'Total requests')
processing_time = Histogram('task_gen_processing_seconds', 'Processing time')
error_count = Counter('task_gen_errors_total', 'Total errors')

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

### 3. Health Check Endpoint

```python
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers."""
    try:
        # Check models loaded
        pipeline = get_pipeline()
        
        return {
            "status": "healthy",
            "version": "1.0.0",
            "models_loaded": True
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }, 503
```

---

## Security

### 1. API Key Authentication

```python
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

@app.post("/generate-tasks")
async def generate_tasks(
    request: TaskGenerationRequest,
    api_key: str = Depends(get_api_key)
):
    ...
```

### 2. Rate Limiting

```bash
pip install slowapi
```

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/generate-tasks")
@limiter.limit("10/minute")
async def generate_tasks(...):
    ...
```

### 3. CORS

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)
```

---

## Backup & Recovery

### 1. Model Backup

```bash
# Backup models (weekly)
tar -czf models-backup-$(date +%Y%m%d).tar.gz models/task_gen/

# Upload to S3
aws s3 cp models-backup-*.tar.gz s3://your-bucket/backups/
```

### 2. Database Backup

```bash
# PostgreSQL
pg_dump task_gen_feedback > backup-$(date +%Y%m%d).sql
```

---

## Troubleshooting

### Issue: High memory usage

**Solution**: Reduce workers or add swap:
```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Issue: Slow response times

**Solution**:
1. Check CPU usage: `htop`
2. Check logs: `tail -f logs/task_generation.log`
3. Profile: Add `--profile` to Gunicorn
4. Reduce max_tasks limit

### Issue: Out of disk space

**Solution**:
```bash
# Clean logs
find logs/ -name "*.log" -mtime +7 -delete

# Clean cache
rm -rf __pycache__ .spacy/
```

---

## Cost Estimation

### Small Scale (100 requests/day)
- Server: AWS t3.medium ($30/month)
- Total: **$30/month**

### Medium Scale (10K requests/day)
- Server: AWS t3.xlarge × 2 ($300/month)
- Load balancer: $20/month
- Total: **$320/month**

### Large Scale (100K requests/day)
- Server: AWS c5.2xlarge × 5 ($850/month)
- Load balancer: $50/month
- Database: RDS t3.medium ($60/month)
- Total: **$960/month**

---

## Checklist

Before deploying:

- [ ] Models trained and validated
- [ ] Health check passes: `python scripts/task_generation/check_health.py`
- [ ] API tests pass: `python test_api.py`
- [ ] Logs configured
- [ ] Monitoring enabled
- [ ] Backups scheduled
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] Rate limiting enabled
- [ ] Documentation updated

---

**Deployment complete!** 🚀

Monitor: `sudo journalctl -u task-gen-api -f`
