# Performance Tuning Guide

> **Last Updated:** April 2, 2026  
> **Version:** 1.0  
> **Audience:** DevOps engineers, system administrators, performance specialists

## Table of Contents

1. [Performance Metrics](#performance-metrics)
2. [System Profiling](#system-profiling)
3. [Optimization Strategies](#optimization-strategies)
4. [Caching Strategies](#caching-strategies)
5. [Database Optimization](#database-optimization)
6. [Memory Management](#memory-management)
7. [Concurrency Tuning](#concurrency-tuning)
8. [Monitoring & Alerting](#monitoring--alerting)

---

## Performance Metrics

### Key Performance Indicators (KPIs)

| Metric | Target | Critical |
|--------|--------|----------|
| Response Time (Single Req) | < 500ms | > 2s |
| File Upload Processing | < 3s per req | > 10s |
| Batch Processing (100 reqs) | < 30s | > 60s |
| API Availability | > 99.5% | < 95% |
| Error Rate | < 0.1% | > 1% |
| Memory Usage | < 500MB | > 1GB |
| CPU Usage | < 70% | > 90% |

### Baseline Performance (Standard Setup)

```
System: 4-core CPU, 4GB RAM
Single Requirement: 250-400ms
Batch (10 requirements): 2.5-4s
File Upload (1MB): 1-2s
Average Confidence Score: 78-85%
Database Query: 10-20ms
```

---

## System Profiling

### 1. **Python Profiling with cProfile**

```bash
# Profile entire API run
python -m cProfile -o api_profile.stats -m requirement_analyzer.api

# Analyze results
python -m pstats api_profile.stats
# In interactive mode:
# stats  (top 20 functions by time)
# sort cumulative  (sort by cumulative time)
# stats 20  (show top 20)
```

### 2. **Line-by-Line Profiling with line_profiler**

```bash
# Install
pip install line_profiler

# Create profiler script
kernprof -l -v requirement_analyzer/task_gen/test_case_generator_v2.py

# View results (decorated with @profile)
```

### 3. **Memory Profiling with memory_profiler**

```bash
# Install
pip install memory-profiler

# Profile memory usage
python -m memory_profiler requirement_analyzer/api.py

# Identify memory leaks
from pympler import tracker
tr = tracker.SummaryTracker()
# ... run code ...
tr.print_diff()
```

### 4. **Request Timing with Middleware**

```python
import time
from fastapi import Request

@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    
    response.headers["X-Process-Time"] = str(duration)
    
    if duration > 1.0:  # Log slow requests
        print(f"SLOW: {request.url.path} took {duration:.2f}s")
    
    return response
```

---

## Optimization Strategies

### 1. **Requirement Parsing Optimization**

**Problem:** Large file parsing is slow

**Current Implementation:**
```python
def parse_txt(content: str):
    lines = content.split('\n')  # Entire content in memory
    requirements = [line.strip() for line in lines]
    return requirements
```

**Optimized Implementation (Streaming):**
```python
def parse_txt_streaming(file_path: str, chunk_size: int = 1024*100):
    """Parse large files in chunks"""
    requirements = []
    buffer = ""
    
    with open(file_path, 'r') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                if buffer:
                    requirements.append(buffer.strip())
                break
            
            buffer += chunk
            lines = buffer.split('\n')
            
            # Keep last incomplete line in buffer
            buffer = lines[-1]
            
            # Process complete lines
            for line in lines[:-1]:
                if line.strip():
                    requirements.append(line.strip())
    
    return requirements
```

### 2. **NLP Processing Optimization**

**Problem:** spaCy NLP processing is slow for large batches

**Current Implementation:**
```python
model = spacy.load("en_core_web_sm")
for req in requirements:
    doc = model(req)  # Process one by one
```

**Optimized Implementation (Batch Processing):**
```python
model = spacy.load("en_core_web_sm", disable=['parser', 'ner'])  # Disable unused pipes

# Process in batches
docs = list(model.pipe(requirements, batch_size=50, n_process=4))
```

**Metrics:**
- Single processing: 100ms per requirement
- Batch processing: 10ms per requirement (10x faster)
- Disabled pipes: 15-20% speed improvement

### 3. **Test Case Generation Optimization**

**Problem:** Generating multiple test cases per requirement is slow

**Optimization:**
```python
def generate_optimized(requirements, max_tests=5):
    """Generate with early termination"""
    test_cases = []
    
    for req in requirements:
        # Skip ambiguous requirements early (avoid wasted NLP)
        if req_confidence(req) < 0.65:
            continue
        
        # Generate only needed test cases
        cases = generate_scenarios(req, max_tests)
        
        # Use cache to avoid duplicate scenarios
        dedup_cases = [c for c in cases if content_hash(c) not in seen_hashes]
        test_cases.extend(dedup_cases)
    
    return test_cases
```

---

## Caching Strategies

### 1. **LRU Cache for Parsed Requirements**

```python
from functools import lru_cache
from hashlib import md5

@lru_cache(maxsize=1000)
def cache_requirement_analysis(requirement_hash: str):
    """Cache analysis of commonly analyzed requirements"""
    # Retrieve from cache or compute
    pass

def analyze_requirement(req: str):
    req_hash = md5(req.encode()).hexdigest()
    return cache_requirement_analysis(req_hash)
```

### 2. **Redis Caching for API Results**

```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379)

async def get_cached_result(file_hash: str):
    """Try to get from Redis"""
    cached = redis_client.get(f"analysis:{file_hash}")
    if cached:
        return json.loads(cached)
    return None

async def cache_result(file_hash: str, result: dict, ttl: int = 3600):
    """Cache result in Redis for 1 hour"""
    redis_client.setex(
        f"analysis:{file_hash}",
        ttl,
        json.dumps(result)
    )
```

### 3. **Database Query Caching**

```python
# Cache expensive database queries
@router.get("/api/v2/requirements/{req_id}")
@cache(expire=300)  # Cache for 5 minutes
async def get_requirement(req_id: int):
    # Database query here
    pass
```

---

## Database Optimization

### 1. **Indexing Strategy**

```sql
-- For PostgreSQL

-- Index on requirement text for full-text search
CREATE INDEX idx_requirements_text ON requirements USING gin(to_tsvector('english', text));

-- Index on NLP confidence for filtering
CREATE INDEX idx_requirements_confidence ON requirements(nlp_confidence);

-- Composite index for common queries
CREATE INDEX idx_requirements_status_confidence 
  ON requirements(status, nlp_confidence DESC);

-- Index on test cases for fast lookups
CREATE INDEX idx_testcases_req_id ON test_cases(requirement_id);
CREATE INDEX idx_testcases_priority ON test_cases(priority);
```

### 2. **Query Optimization**

```python
# SLOW QUERY - N+1 Problem
requirements = db.query(Requirement).all()
for req in requirements:
    test_cases = db.query(TestCase).filter_by(req_id=req.id).all()

# FAST QUERY - Eager Loading
requirements = db.query(Requirement).options(
    joinedload(Requirement.test_cases)
).all()
```

### 3. **Bulk Operations**

```python
# SLOW - Insert one by one
for tc in test_cases:
    db.add(tc)
    db.commit()

# FAST - Bulk insert
db.bulk_insert_mappings(TestCase, test_cases)
db.commit()

# VERY FAST - Batch with batch size
def bulk_insert_batches(objects, batch_size=1000):
    for i in range(0, len(objects), batch_size):
        db.bulk_insert_mappings(TestCase, objects[i:i+batch_size])
        db.commit()
```

---

## Memory Management

### 1. **Memory Profiling**

```python
import tracemalloc

tracemalloc.start()

# Your code here
requirements = parse_large_file('requirements.txt')
test_cases = generate_test_cases(requirements)

current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024 / 1024:.1f}MB")
print(f"Peak: {peak / 1024 / 1024:.1f}MB")
```

### 2. **Generators for Large Data**

```python
# MEMORY INTENSIVE
def parse_file(file_path):
    with open(file_path) as f:
        content = f.read()  # Entire file in memory
        lines = content.split('\n')
        return [line.strip() for line in lines]

# MEMORY EFFICIENT
def parse_file_generator(file_path):
    """Generate requirements one by one"""
    with open(file_path) as f:
        for line in f:
            req = line.strip()
            if req:
                yield req

# Usage
for requirement in parse_file_generator('large_file.txt'):
    process_requirement(requirement)
```

### 3. **Proper Resource Cleanup**

```python
# Use context managers
import tempfile

with tempfile.NamedTemporaryFile(mode='w', delete=True) as tmp:
    # File automatically deleted
    tmp.write(data)

# Or with open()
with open('file.txt') as f:
    content = f.read()
# File automatically closed
```

---

## Concurrency Tuning

### 1. **AsyncIO Optimization**

```python
# SEQUENTIAL - Slow
for req in requirements:
    result = await process_requirement(req)

# CONCURRENT - Fast (up to limit)
from asyncio import gather

tasks = [process_requirement(req) for req in requirements]
results = await gather(*tasks, return_exceptions=True)

# WITH LIMIT - Balanced
from asyncio import Semaphore

semaphore = Semaphore(10)

async def limited_task(req):
    async with semaphore:
        return await process_requirement(req)

tasks = [limited_task(req) for req in requirements]
results = await gather(*tasks)
```

### 2. **Thread Pool for CPU-Bound Work**

```python
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

# Run CPU-bound NLP in threads
loop = asyncio.get_event_loop()
results = await loop.run_in_executor(
    executor,
    process_nlp_batch,
    requirements
)
```

---

## Monitoring & Alerting

### 1. **Prometheus Metrics**

```python
from prometheus_client import Counter, Histogram, Gauge

# Track request counts
test_gen_requests = Counter(
    'test_generation_requests_total',
    'Total test generation requests'
)

# Track response times
test_gen_duration = Histogram(
    'test_generation_duration_seconds',
    'Test generation processing time'
)

# Track active processes
active_processes = Gauge(
    'test_generation_active_processes',
    'Currently processing requirements'
)

@router.post("/api/v2/test-generation/analyze-file-detailed")
async def analyze_file_detailed(file: UploadFile):
    test_gen_requests.inc()
    active_processes.inc()
    
    with test_gen_duration.time():
        # Process file
        pass
    
    active_processes.dec()
```

### 2. **Health Check with Metrics**

```python
@router.get("/health/detailed")
async def health_detailed():
    return {
        "status": "healthy",
        "service": "test-generator",
        "metrics": {
            "memory_mb": psutil.Process().memory_info().rss / 1024 / 1024,
            "cpu_percent": psutil.Process().cpu_percent(interval=0.1),
            "active_requests": len(asyncio.all_tasks()),
            "uptime_seconds": time.time() - START_TIME
        }
    }
```

---

## Performance Checklist

- [ ] Profile code to identify bottlenecks
- [ ] Implement streaming for large files
- [ ] Use batch processing for NLP
- [ ] Enable caching for frequent operations
- [ ] Create proper database indexes
- [ ] Use bulk operations for inserts
- [ ] Implement concurrency limits
- [ ] Monitor memory usage
- [ ] Set up Prometheus metrics
- [ ] Configure alerting thresholds
- [ ] Document performance baseline
- [ ] Regularly benchmark after changes

---

## Support

- 📊 See [SYSTEM_UPGRADE_PHASE2.md](SYSTEM_UPGRADE_PHASE2.md) for current performance metrics
- 🔍 See [TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md) for performance issues
- 📖 See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for deployment options

---

*Last updated: April 2, 2026*
