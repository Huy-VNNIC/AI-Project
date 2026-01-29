# LLM Mode Implementation Guide

## Quick Start: Add LLM Generation in 1 Hour

This guide shows how to add natural language task generation using LLM APIs.

---

## Step 1: Install Dependencies (5 min)

```bash
cd /home/dtu/AI-Project/AI-Project
pip install openai anthropic google-generativeai tenacity
```

**Or add to `requirements.txt`**:
```
openai>=1.12.0
anthropic>=0.18.0
google-generativeai>=0.3.0
tenacity>=8.2.0  # For retry logic
```

---

## Step 2: Set API Keys (2 min)

**Option A: Environment variables**
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="..."
```

**Option B: `.env` file**
```bash
# .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

Then install `python-dotenv`:
```bash
pip install python-dotenv
```

---

## Step 3: Create LLM Generator Module (30 min)

Create file: `requirement_analyzer/task_gen/generator_llm.py`

```python
"""
LLM-based task generator using structured JSON generation.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import re

from .schemas import GeneratedTask, TaskSource

logger = logging.getLogger(__name__)


# =============================================================================
# Prompt Template
# =============================================================================

SYSTEM_PROMPT = """You are an expert software project manager creating detailed Jira tasks from requirements.

Your output must be valid JSON matching this schema:
{
  "title": "string (5-10 words, action-oriented, specific)",
  "description": "string (2-4 sentences with technical details)",
  "acceptance_criteria": ["string", ...] (3-8 testable items),
  "labels": ["string", ...] (2-5 relevant tags)
}

Guidelines:
- Title: Start with verb (Implement, Create, Design, Optimize, etc.)
- Description: Include technical approach, constraints, considerations
- AC: Each item must be testable and specific
- Labels: Use lowercase, hyphen-separated (e.g., "user-auth", "api-endpoint")
- Be specific to the domain and use appropriate terminology
- Avoid generic phrases like "implement functionality" or "ensure quality"
"""


TASK_PROMPT_TEMPLATE = """Generate a Jira task for this requirement:

**Requirement Text:**
{requirement_text}

**Context:**
- Type: {type}
- Priority: {priority}
- Domain: {domain}
- Assigned Role: {role}

**Few-Shot Examples:**

Example 1 (Functional):
Requirement: "Users should be able to reset their password via email"
Output:
{{
  "title": "Implement Password Reset via Email",
  "description": "Build a secure password reset flow where users request a reset link via email, click the link to verify their identity, and set a new password. The reset link should expire after 1 hour and be single-use only.",
  "acceptance_criteria": [
    "User can request password reset by entering email",
    "System sends reset email with unique token link",
    "Link expires after 1 hour",
    "Link can only be used once",
    "User can set new password after verification",
    "Old password is invalidated after reset"
  ],
  "labels": ["authentication", "password-reset", "email"]
}}

Example 2 (Security):
Requirement: "API endpoints must be protected with JWT authentication"
Output:
{{
  "title": "Implement JWT Authentication for API Endpoints",
  "description": "Add JWT-based authentication middleware to all API endpoints. Users obtain a token by logging in with credentials, and include the token in the Authorization header for subsequent requests. Tokens should have a 24-hour expiration and support refresh tokens.",
  "acceptance_criteria": [
    "User receives JWT token upon successful login",
    "All protected endpoints require valid JWT in header",
    "Token expiration is enforced (24 hours)",
    "Refresh token mechanism is implemented",
    "Invalid/expired tokens return 401 Unauthorized",
    "Token payload includes user ID and roles"
  ],
  "labels": ["security", "jwt", "authentication", "api"]
}}

Example 3 (Interface):
Requirement: "Dashboard should display real-time sales metrics"
Output:
{{
  "title": "Design Real-Time Sales Metrics Dashboard",
  "description": "Create a dashboard UI that displays key sales metrics (revenue, orders, conversion rate) updated in real-time via WebSocket connection. Include filters for date range and product category, with responsive charts using Chart.js.",
  "acceptance_criteria": [
    "Dashboard displays 4 key metrics in card layout",
    "Metrics update in real-time without page refresh",
    "User can filter by date range (today, week, month, custom)",
    "Charts are responsive and mobile-friendly",
    "Loading states are displayed during data fetch",
    "Error handling for WebSocket disconnection"
  ],
  "labels": ["dashboard", "real-time", "websocket", "charts", "ui"]
}}

**Your Task:**
Generate a similar detailed task for the requirement above. Output ONLY the JSON, no other text.
"""


# =============================================================================
# LLM Clients
# =============================================================================

class LLMClient:
    """Base class for LLM providers."""
    
    def generate(self, prompt: str, system: str) -> str:
        raise NotImplementedError


class OpenAIClient(LLMClient):
    def __init__(self, model: str = "gpt-4o-mini", api_key: Optional[str] = None):
        import openai
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def generate(self, prompt: str, system: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}  # Structured output
        )
        return response.choices[0].message.content


class AnthropicClient(LLMClient):
    def __init__(self, model: str = "claude-3-haiku-20240307", api_key: Optional[str] = None):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def generate(self, prompt: str, system: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.content[0].text


class GoogleClient(LLMClient):
    def __init__(self, model: str = "gemini-1.5-flash", api_key: Optional[str] = None):
        import google.generativeai as genai
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def generate(self, prompt: str, system: str) -> str:
        full_prompt = f"{system}\n\n{prompt}"
        response = self.model.generate_content(
            full_prompt,
            generation_config={"temperature": 0.7}
        )
        return response.text


# =============================================================================
# JSON Parsing & Repair
# =============================================================================

def parse_and_repair_json(text: str) -> Optional[Dict[str, Any]]:
    """
    Parse JSON from LLM output, with repair logic.
    """
    # Remove markdown code blocks
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*$', '', text)
    text = text.strip()
    
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parse error: {e}. Attempting repair...")
    
    # Repair: Extract JSON object
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except:
            pass
    
    # Repair: Fix common issues
    text = text.replace("'", '"')  # Single quotes
    text = re.sub(r',\s*}', '}', text)  # Trailing commas
    text = re.sub(r',\s*]', ']', text)
    
    try:
        return json.loads(text)
    except:
        logger.error(f"Failed to repair JSON: {text[:200]}")
        return None


# =============================================================================
# LLM Task Generator
# =============================================================================

class TaskLLMGenerator:
    """
    Generate tasks using LLM structured generation.
    """
    
    def __init__(
        self,
        provider: str = "openai",
        model: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Args:
            provider: 'openai', 'anthropic', or 'google'
            model: Model name (defaults to cheapest/fastest)
            api_key: API key (or set via env var)
        """
        self.provider = provider
        
        if provider == "openai":
            self.client = OpenAIClient(model or "gpt-4o-mini", api_key)
        elif provider == "anthropic":
            self.client = AnthropicClient(model or "claude-3-haiku-20240307", api_key)
        elif provider == "google":
            self.client = GoogleClient(model or "gemini-1.5-flash", api_key)
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        logger.info(f"Initialized LLM generator with provider={provider}")
    
    def generate_single(
        self,
        requirement_text: str,
        enrichment: Dict[str, Any],
        source: Optional[TaskSource] = None
    ) -> Optional[GeneratedTask]:
        """
        Generate a single task using LLM.
        
        Args:
            requirement_text: Requirement sentence
            enrichment: Dict with type, priority, domain, role, confidence
            source: Source tracking info
        
        Returns:
            GeneratedTask or None if generation failed
        """
        # Build prompt
        prompt = TASK_PROMPT_TEMPLATE.format(
            requirement_text=requirement_text,
            type=enrichment.get('type', 'functional'),
            priority=enrichment.get('priority', 'Medium'),
            domain=enrichment.get('domain', 'general'),
            role=enrichment.get('role', 'Backend')
        )
        
        try:
            # Call LLM
            response = self.client.generate(prompt, SYSTEM_PROMPT)
            
            # Parse JSON
            task_dict = parse_and_repair_json(response)
            if not task_dict:
                logger.error("Failed to parse LLM response")
                return None
            
            # Validate and create task
            task = GeneratedTask(
                title=task_dict.get('title', 'Untitled Task'),
                description=task_dict.get('description', requirement_text),
                acceptance_criteria=task_dict.get('acceptance_criteria', []),
                type=enrichment.get('type'),
                priority=enrichment.get('priority'),
                domain=enrichment.get('domain'),
                role=enrichment.get('role'),
                labels=task_dict.get('labels', []),
                confidence=enrichment.get('confidence', 0.5),
                source=source
            )
            
            return task
            
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return None
    
    def generate_batch(
        self,
        requirements: List[str],
        enrichments: List[Dict[str, Any]],
        sources: Optional[List[TaskSource]] = None,
        max_concurrent: int = 5
    ) -> List[GeneratedTask]:
        """
        Generate tasks in parallel (for speed).
        
        Args:
            requirements: List of requirement texts
            enrichments: List of enrichment dicts
            sources: Optional source tracking
            max_concurrent: Max parallel requests
        
        Returns:
            List of GeneratedTask
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        if sources is None:
            sources = [None] * len(requirements)
        
        tasks = []
        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            futures = {
                executor.submit(
                    self.generate_single,
                    req,
                    enrich,
                    src
                ): i for i, (req, enrich, src) in enumerate(zip(requirements, enrichments, sources))
            }
            
            for future in as_completed(futures):
                task = future.result()
                if task:
                    tasks.append(task)
        
        logger.info(f"Generated {len(tasks)}/{len(requirements)} tasks successfully")
        return tasks


# =============================================================================
# Singleton
# =============================================================================

_generator_instance = None


def get_llm_generator(
    provider: str = "openai",
    model: Optional[str] = None,
    api_key: Optional[str] = None
) -> TaskLLMGenerator:
    """Get or create singleton LLM generator."""
    global _generator_instance
    
    if _generator_instance is None:
        _generator_instance = TaskLLMGenerator(provider, model, api_key)
    
    return _generator_instance
```

---

## Step 4: Integrate with Pipeline (10 min)

Edit `requirement_analyzer/task_gen/pipeline.py`:

```python
# Add import at top
from .generator_llm import get_llm_generator

class TaskGenerationPipeline:
    def __init__(
        self,
        mode: str = 'template',  # Add mode parameter
        llm_provider: str = 'openai',
        llm_model: Optional[str] = None,
        ...
    ):
        # ... existing init ...
        
        # Generator
        self.mode = mode
        if mode == 'template':
            from .generator_templates import get_template_generator
            self.generator = get_template_generator()
        elif mode == 'llm':
            self.generator = get_llm_generator(llm_provider, llm_model)
        else:
            raise ValueError(f"Unknown mode: {mode}")
    
    # ... rest stays the same, generator.generate_batch() works for both!
```

Update `__init__.py`:

```python
def get_pipeline(
    mode: str = 'template',
    llm_provider: str = 'openai',
    **kwargs
) -> TaskGenerationPipeline:
    """
    Get singleton pipeline.
    
    Args:
        mode: 'template' or 'llm'
        llm_provider: 'openai', 'anthropic', or 'google' (if mode='llm')
    """
    global _pipeline_instance
    
    if _pipeline_instance is None:
        _pipeline_instance = TaskGenerationPipeline(
            mode=mode,
            llm_provider=llm_provider,
            **kwargs
        )
    
    return _pipeline_instance
```

---

## Step 5: Update API (5 min)

Edit `requirement_analyzer/api.py`:

```python
# Add mode parameter to generate-tasks endpoint
@app.post("/generate-tasks", response_model=TaskGenerationResponse)
async def generate_tasks_endpoint(request: TaskGenerationRequest):
    """Generate tasks from requirements text."""
    try:
        # Initialize pipeline with mode
        mode = request.mode or 'template'  # Add mode to TaskGenerationRequest
        pipeline = get_pipeline(mode=mode, llm_provider=request.llm_provider or 'openai')
        
        # Generate
        result = pipeline.generate_tasks(
            text=request.text,
            max_tasks=request.max_tasks,
            epic_name=request.epic_name,
            domain_hint=request.domain_hint
        )
        
        return result
    except Exception as e:
        logger.error(f"Task generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

Update `TaskGenerationRequest` schema in `schemas.py`:

```python
class TaskGenerationRequest(BaseModel):
    text: str
    max_tasks: int = 50
    mode: str = 'template'  # Add this
    llm_provider: Optional[str] = 'openai'  # Add this
    epic_name: Optional[str] = None
    domain_hint: Optional[str] = None
    include_story_points: bool = False
```

---

## Step 6: Test! (10 min)

### Test 1: Direct Python
```python
from requirement_analyzer.task_gen import get_pipeline

# LLM mode
pipeline = get_pipeline(mode='llm', llm_provider='openai')

doc = """
User Requirements:
1. Users must be able to register with email and password
2. System should send verification email after registration
3. Users can reset password via email link
"""

result = pipeline.generate_tasks(doc, max_tasks=10)

for task in result.tasks:
    print(f"\n{task.title}")
    print(f"  Description: {task.description[:100]}...")
    print(f"  AC: {len(task.acceptance_criteria)} criteria")
```

### Test 2: API Request
```bash
curl -X POST http://localhost:8000/generate-tasks \
  -H "Content-Type: application/json" \
  -d '{
    "text": "System must authenticate users via OAuth2",
    "mode": "llm",
    "llm_provider": "openai",
    "max_tasks": 5
  }'
```

### Test 3: Compare Modes
```python
# Template mode
pipeline_t = get_pipeline(mode='template')
result_t = pipeline_t.generate_tasks(doc)

# LLM mode
pipeline_l = get_pipeline(mode='llm')
result_l = pipeline_l.generate_tasks(doc)

# Compare
print("\n=== TEMPLATE MODE ===")
print(result_t.tasks[0].description)

print("\n=== LLM MODE ===")
print(result_l.tasks[0].description)
```

---

## Performance Tuning

### Parallel Requests (Speed Up 5x)
```python
generator = get_llm_generator()
tasks = generator.generate_batch(
    requirements,
    enrichments,
    max_concurrent=10  # Adjust based on API limits
)
```

**Speed comparison** (50 tasks):
- Sequential: 50 × 2s = 100 seconds
- Parallel (10): 50 / 10 × 2s = 10 seconds

### Use Faster Models
```python
# OpenAI
pipeline = get_pipeline(mode='llm', llm_provider='openai', llm_model='gpt-4o-mini')  # Fast & cheap

# Google
pipeline = get_pipeline(mode='llm', llm_provider='google', llm_model='gemini-1.5-flash')  # Fastest

# Anthropic
pipeline = get_pipeline(mode='llm', llm_provider='anthropic', llm_model='claude-3-haiku')  # Balanced
```

### Caching (Avoid Duplicate Calls)
```python
# Add simple cache
_cache = {}

def generate_with_cache(req_text, enrichment):
    key = (req_text, tuple(sorted(enrichment.items())))
    if key in _cache:
        return _cache[key]
    
    task = generator.generate_single(req_text, enrichment)
    _cache[key] = task
    return task
```

---

## Cost Estimation

### OpenAI GPT-4o-mini
- Input: 200 tokens × $0.15/1M = $0.00003
- Output: 300 tokens × $0.60/1M = $0.00018
- **Total: ~$0.0002 per task**

**Examples**:
- 100 tasks: $0.02
- 1,000 tasks: $0.20
- 10,000 tasks: $2.00

### Google Gemini Flash (Cheapest)
- Input: 200 tokens × $0.075/1M = $0.000015
- Output: 300 tokens × $0.30/1M = $0.00009
- **Total: ~$0.0001 per task** (50% cheaper!)

### Anthropic Claude Haiku
- Input: 200 tokens × $0.25/1M = $0.00005
- Output: 300 tokens × $1.25/1M = $0.000375
- **Total: ~$0.0004 per task**

---

## Error Handling

### Retry Logic (Already Included)
```python
@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def generate(self, prompt, system):
    # Auto-retry on API errors
```

### Fallback to Template
```python
def generate_with_fallback(req, enrichment):
    try:
        # Try LLM first
        return llm_generator.generate_single(req, enrichment)
    except Exception as e:
        logger.warning(f"LLM failed, falling back to template: {e}")
        return template_generator.generate_single(req, enrichment)
```

### Validate Output
```python
task = generator.generate_single(req, enrichment)
if task is None:
    # Generation failed
    logger.error("Task generation returned None")
    continue

# Pydantic validation happens automatically
# Additional checks:
if len(task.acceptance_criteria) < 2:
    logger.warning("Too few acceptance criteria, regenerating...")
```

---

## Monitoring

### Log Metrics
```python
import time

start = time.time()
task = generator.generate_single(req, enrichment)
latency = time.time() - start

logger.info(f"Generated task in {latency:.2f}s, confidence={task.confidence}")
```

### Track Costs
```python
# Rough estimation
input_tokens = len(prompt.split()) * 1.3  # Words to tokens
output_tokens = len(task.description.split()) * 1.3

cost = (input_tokens * 0.15 + output_tokens * 0.60) / 1_000_000
logger.info(f"Estimated cost: ${cost:.5f}")
```

---

## Troubleshooting

### Issue: "API key not found"
**Solution**: Set environment variable
```bash
export OPENAI_API_KEY="your-key"
# Or in code:
pipeline = get_pipeline(mode='llm', api_key='your-key')
```

### Issue: "JSON parse error"
**Solution**: Check `parse_and_repair_json()` logs, may need to improve regex

### Issue: "Rate limit exceeded"
**Solution**: Reduce `max_concurrent` or add delay
```python
import time
time.sleep(0.1)  # 100ms delay between requests
```

### Issue: Tasks are too generic
**Solution**: Improve prompt with more examples or stricter guidelines
```python
SYSTEM_PROMPT += "\nBe extremely specific. Include exact technologies, APIs, and implementation details."
```

---

## Next Steps

1. **A/B Test**: Compare template vs LLM acceptance rate
2. **Collect Feedback**: Use `/tasks/feedback` endpoint
3. **Fine-tune**: Train local model on feedback data
4. **Optimize Costs**: Batch requests, use cheaper models, cache

---

**Estimated Implementation Time**: 1 hour  
**Estimated Cost**: $0.0002 per task (OpenAI GPT-4o-mini)  
**Expected Quality Improvement**: 60% → 85% acceptance rate

Ready to implement! 🚀
