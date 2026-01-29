# Task Generation Mode Comparison

## Overview

Your task generation system supports **2 modes**:

| Mode | Description | Pros | Cons | Best For |
|------|-------------|------|------|----------|
| **Template** | Rule-based using NLP parsing + templates | Fast, free, deterministic | Less natural, rigid structure | Development, testing, cost-sensitive |
| **LLM** | AI-powered natural language generation | Natural, flexible, context-aware | Costs money, slower, requires API key | Production, high-quality output |

---

## Mode 1: Template-Based (Default)

### How It Works
```
Requirement → spaCy NLP → Extract action/object → Apply template → Generate task
```

**Example:**
```
Input: "Users must reset password via email"
Output:
  Title: "Implement password reset via email"
  Description: "Implement functionality for password reset via email..."
  AC: ["User can request password reset", "Email contains reset link", ...]
```

### Setup
```bash
# No extra setup needed - works out of the box
export TASK_GEN_MODE=template
```

### Characteristics
- ✅ **Fast**: <100ms per task
- ✅ **Free**: No API costs
- ✅ **Deterministic**: Same input = same output
- ✅ **Offline**: No internet needed
- ⚠️ **Structured**: Uses type-specific templates
- ⚠️ **Less flexible**: Limited variation

### Use Cases
- Quick prototyping
- Budget-constrained projects
- High-volume batch processing
- Environments with strict data privacy (no external API calls)

---

## Mode 2: LLM-Based

### How It Works
```
Requirement → Structured prompt → LLM API call → JSON validation → Generate task
```

**Example:**
```
Input: "Users must reset password via email"
LLM Output:
  Title: "Enable User Password Reset via Email"
  Description: "Implement a secure password reset mechanism allowing users 
                to request a reset link via email. The system should generate
                a time-limited token, send it to the registered email address,
                and allow the user to create a new password after verification."
  AC: ["User can initiate password reset from login page",
       "System validates email exists in database",
       "Reset link expires after 1 hour",
       "Old password is invalidated after successful reset",
       "User receives confirmation email after reset"]
```

### Setup

**Option A: OpenAI (Recommended)**
```bash
# Install OpenAI SDK
pip install openai

# Set API key
export OPENAI_API_KEY="sk-..."
export TASK_GEN_MODE=llm
export LLM_PROVIDER=openai
export LLM_MODEL=gpt-4o-mini  # Or gpt-4o for better quality
```

**Option B: Anthropic (Claude)**
```bash
# Install Anthropic SDK
pip install anthropic

# Set API key
export ANTHROPIC_API_KEY="sk-ant-..."
export TASK_GEN_MODE=llm
export LLM_PROVIDER=anthropic
export LLM_MODEL=claude-3-haiku-20240307  # Or claude-3-5-sonnet for better quality
```

### Characteristics
- ✅ **Natural**: Human-like writing
- ✅ **Flexible**: Adapts to context
- ✅ **Context-aware**: Understands nuance
- ✅ **Better AC**: More comprehensive acceptance criteria
- ⚠️ **Costs money**: $0.15-$7.50 per 1M tokens (varies by model)
- ⚠️ **Slower**: 1-3s per task (due to API latency)
- ⚠️ **Requires internet**: API calls needed
- ⚠️ **Non-deterministic**: Slight variation between runs

### Cost Estimation

**OpenAI Pricing (as of 2024):**
- `gpt-4o-mini`: $0.15/1M input, $0.60/1M output (~$0.001 per task)
- `gpt-4o`: $2.50/1M input, $10/1M output (~$0.015 per task)

**Anthropic Pricing:**
- `claude-3-haiku`: $0.25/1M input, $1.25/1M output (~$0.002 per task)
- `claude-3-5-sonnet`: $3/1M input, $15/1M output (~$0.020 per task)

**Example:** Generating 100 tasks with gpt-4o-mini = ~$0.10

### Use Cases
- Production systems requiring high-quality output
- Customer-facing deliverables (proposals, project plans)
- Complex requirements needing nuanced understanding
- When budget allows for API costs

---

## How to Switch Modes

### Method 1: Environment Variables
```bash
# Template mode (default)
export TASK_GEN_MODE=template

# LLM mode
export TASK_GEN_MODE=llm
export LLM_PROVIDER=openai
export LLM_MODEL=gpt-4o-mini
export OPENAI_API_KEY=sk-...
```

### Method 2: Config File
Create `.env` file in project root:
```bash
# .env
TASK_GEN_MODE=llm
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-...
```

Then load in code:
```python
from dotenv import load_dotenv
load_dotenv()
```

### Method 3: Programmatic
```python
from requirement_analyzer.task_gen import use_llm_mode, use_template_mode

# Switch to LLM
use_llm_mode(provider="openai", model="gpt-4o-mini")

# Or switch to template
use_template_mode()
```

### Method 4: API Request
```bash
# LLM mode via API (not implemented yet, requires API modification)
curl -X POST http://localhost:8000/generate-tasks \
  -H "Content-Type: application/json" \
  -d '{
    "text": "...",
    "mode": "llm",
    "llm_provider": "openai",
    "llm_model": "gpt-4o-mini"
  }'
```

---

## Testing Both Modes

### Template Mode Test
```bash
cd scripts/task_generation
python demo.py
```

### LLM Mode Test
```bash
# Set API key first
export OPENAI_API_KEY=sk-...

cd scripts/task_generation
python demo_llm.py
```

### Compare Outputs
```bash
# Generate with both modes
python demo.py  # Creates demo_tasks.json
python demo_llm.py  # Creates demo_llm_tasks.json

# Compare side-by-side
jq '.tasks[0]' demo_tasks.json
jq '.tasks[0]' demo_llm_tasks.json
```

---

## Hybrid Approach (Recommended)

Use **both modes** strategically:

1. **Development**: Template mode for fast iteration
2. **QA/Review**: LLM mode for final quality check
3. **Refinement**: Template generates draft → LLM enhances selected tasks

**Example workflow:**
```python
from requirement_analyzer.task_gen import get_pipeline

# Step 1: Generate initial tasks with template (fast, free)
template_pipeline = get_pipeline(generator_mode="template")
draft_tasks = template_pipeline.generate_tasks(text)

# Step 2: User reviews and selects high-priority tasks

# Step 3: Re-generate selected tasks with LLM (high quality)
llm_pipeline = get_pipeline(
    generator_mode="llm",
    llm_provider="openai",
    llm_model="gpt-4o-mini"
)
final_tasks = []
for task in selected_draft_tasks:
    enhanced = llm_pipeline.generate_tasks(
        text=task.source.sentence,
        max_tasks=1
    )
    final_tasks.append(enhanced.tasks[0])
```

---

## Performance Comparison

| Metric | Template | LLM (gpt-4o-mini) | LLM (gpt-4o) |
|--------|----------|-------------------|--------------|
| Speed | 0.05s/task | 1.5s/task | 2.5s/task |
| Cost | Free | $0.001/task | $0.015/task |
| Quality (subjective) | 6/10 | 8/10 | 9/10 |
| Consistency | 10/10 | 7/10 | 7/10 |
| Offline | Yes | No | No |

---

## Troubleshooting

### LLM Mode Not Working

**Problem:** `ImportError: No module named 'openai'`
```bash
# Solution
pip install openai
# or
pip install anthropic
```

**Problem:** `AuthenticationError: Invalid API key`
```bash
# Solution: Check your API key
echo $OPENAI_API_KEY  # Should show sk-...
# Get key from: https://platform.openai.com/api-keys
```

**Problem:** `RateLimitError: Rate limit exceeded`
```bash
# Solution: Add delay between calls
export LLM_RATE_LIMIT_DELAY=1.0  # seconds
```

**Problem:** Tasks quality is poor
```bash
# Solution: Use better model
export LLM_MODEL=gpt-4o  # Instead of gpt-4o-mini
export LLM_TEMPERATURE=0.3  # Lower = more consistent
```

### Template Mode Issues

**Problem:** Tasks too generic
```bash
# Solution: Improve requirements specificity
# Bad: "System should handle errors"
# Good: "System should display user-friendly error message when login fails"
```

**Problem:** Missing spaCy model
```bash
# Solution
python -m spacy download en_core_web_sm
```

---

## Recommendations

### When to Use Template Mode
- ✅ Development and testing
- ✅ Budget < $100/month
- ✅ Batch processing > 1000 tasks/day
- ✅ Offline or air-gapped environments
- ✅ Requirements are already well-structured

### When to Use LLM Mode
- ✅ Production deliverables
- ✅ Budget allows API costs
- ✅ Quality > speed
- ✅ Requirements are natural language (not structured)
- ✅ Customer-facing documentation

### When to Use Hybrid
- ✅ Large projects (> 100 tasks)
- ✅ Need speed AND quality
- ✅ Two-stage workflow (draft → refine)

---

## Next Steps

1. **Test template mode first**: `python scripts/task_generation/demo.py`
2. **If satisfied**: Stop here, use template mode
3. **If need better quality**: Get API key, test LLM mode: `python scripts/task_generation/demo_llm.py`
4. **Compare outputs**: Review both `demo_tasks.json` and `demo_llm_tasks.json`
5. **Choose mode** based on your budget, quality needs, and use case

---

## Related Documents
- [TASK_GENERATION_GUIDE.md](TASK_GENERATION_GUIDE.md) - Full API reference
- [config.py](../requirement_analyzer/task_gen/config.py) - Configuration options
