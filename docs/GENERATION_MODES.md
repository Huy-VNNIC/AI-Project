# Task Generation Modes Comparison

## Overview

Hệ thống có 2 chế độ tạo tasks từ requirements:

1. **Template Mode (M1)** - Rule-based với ML classification
2. **LLM Mode (M2)** - Natural language generation

---

## Mode 1: Template-Based Generation

### ✅ Advantages
- **Fast**: ~1000 tasks/second
- **Deterministic**: Cùng input → cùng output
- **Cheap**: No API costs
- **Offline**: Không cần internet
- **Interpretable**: Có thể debug templates
- **Lightweight**: ~220MB models

### ❌ Disadvantages  
- **Rigid output**: Tasks nhìn giống nhau (cứng, lặp lại)
- **Limited creativity**: Bị giới hạn bởi templates
- **Generic**: Không capture được ngữ cảnh phức tạp
- **Not natural**: "Nhìn rất giả" - người dùng dễ nhận ra tự động

### Architecture
```
Requirement Text
    ↓
spaCy Dependency Parsing
    ↓
Extract: action, object, condition
    ↓
Select Template (by type)
    ↓
Fill Template
    ↓
Generated Task (JSON)
```

### Example Output
**Input**: "System must authenticate users via OAuth2"

**Generated**:
```json
{
  "title": "Implement authenticate for users",
  "description": "The system needs to authenticate users via OAuth2.",
  "acceptance_criteria": [
    "User can authenticate users successfully",
    "System validates input data before authenticate",
    "System provides appropriate feedback",
    "Error handling is implemented"
  ]
}
```

❌ **Issues**:
- Generic AC (không specific về OAuth2)
- Title nghe giống nhau cho mọi auth tasks
- Không có chi tiết kỹ thuật (OAuth flow, tokens, scopes)

---

## Mode 2: LLM Structured Generation

### ✅ Advantages
- **Natural output**: Tasks như do người viết
- **Context-aware**: Hiểu ngữ cảnh, domain knowledge
- **Flexible**: Adapt theo complexity của requirement
- **Rich details**: Tạo chi tiết kỹ thuật phù hợp
- **Variety**: Không lặp lại, mỗi task khác nhau

### ❌ Disadvantages
- **Slower**: ~1-2 seconds/task (với API), ~5-10 tasks/sec (local model)
- **Costs**: API calls ($0.002-0.01 per task với GPT-3.5/4)
- **Non-deterministic**: Cùng input có thể khác output
- **Requires internet**: Nếu dùng API
- **Harder to debug**: Black box LLM
- **JSON parsing**: Cần validation + repair logic

### Architecture (Option A: API-based)
```
Requirement Text + Labels (from ML)
    ↓
Construct Prompt (JSON schema + examples)
    ↓
LLM API (GPT-4, Claude, Gemini)
    ↓
Parse JSON response
    ↓
Validate with Pydantic
    ↓ (if invalid)
Repair JSON (regex + heuristics)
    ↓
Generated Task (JSON)
```

### Architecture (Option B: Local Model)
```
Requirement Text + Labels (from ML)
    ↓
Fine-tuned T5/BART/Llama-7B
    ↓
Text → JSON generation
    ↓
Validate + Repair
    ↓
Generated Task (JSON)
```

### Example Output (Same Input)
**Input**: "System must authenticate users via OAuth2"

**Generated** (LLM):
```json
{
  "title": "Implement OAuth2 User Authentication",
  "description": "Integrate OAuth2 authentication flow to allow users to securely log in using external identity providers (Google, GitHub, Facebook). The system should handle authorization code flow, token exchange, and user session management.",
  "acceptance_criteria": [
    "User can initiate OAuth2 login by selecting a provider",
    "System redirects to provider authorization page",
    "After user approval, system receives authorization code",
    "Backend exchanges code for access/refresh tokens",
    "User profile is fetched and stored in database",
    "JWT session token is issued to client",
    "Token refresh mechanism is implemented",
    "Logout invalidates tokens on both client and server"
  ]
}
```

✅ **Better because**:
- Title cụ thể về OAuth2
- Description chi tiết flow (authorization code, token exchange)
- AC cover đầy đủ OAuth2 flow (8 items vs 4)
- Mention cụ thể providers (Google, GitHub)
- Có session management + token refresh

---

## Comparison Table

| Aspect | Template (M1) | LLM (M2) |
|--------|---------------|----------|
| **Output Quality** | ⭐⭐ Generic | ⭐⭐⭐⭐⭐ Natural |
| **Speed** | ⭐⭐⭐⭐⭐ <1ms/task | ⭐⭐ 1-2s/task (API) |
| **Cost** | ⭐⭐⭐⭐⭐ Free | ⭐⭐ $0.002-0.01/task |
| **Consistency** | ⭐⭐⭐⭐⭐ 100% | ⭐⭐⭐ ~90% valid JSON |
| **Context Awareness** | ⭐⭐ Limited | ⭐⭐⭐⭐⭐ Excellent |
| **Maintainability** | ⭐⭐⭐ Edit templates | ⭐⭐⭐⭐ Tune prompt |
| **Offline Capable** | ✅ Yes | ❌ (API) / ✅ (Local) |
| **Debuggability** | ⭐⭐⭐⭐ Easy | ⭐⭐ Hard |

---

## Hybrid Approach (Recommended)

### Strategy: ML Classification + LLM Generation

**Why hybrid?**
- Use ML models (fast, cheap) for **labels** (type, priority, domain)
- Use LLM (smart, natural) for **text generation** (title, description, AC)

**Benefits**:
- ✅ Fast classification (~5000 req/sec)
- ✅ Natural task text
- ✅ Reduced LLM cost (don't ask LLM to classify, just generate)
- ✅ Better accuracy (ML classifier trained on 1M examples)

### Workflow
```
1. Document → Segmenter → Sentences
2. Sentences → ML Detector → Requirements (5ms/sentence)
3. Requirements → ML Enrichers → Labels (type/priority/domain) (10ms/req)
4. Requirements + Labels → LLM → Task JSON (1-2s/task)
5. Tasks → Post-processor → Dedupe, filter
```

**Cost savings example** (100-page document → 50 tasks):
- Classification: 0 cost (local ML)
- LLM calls: 50 tasks × $0.005 = **$0.25**
- vs pure LLM (classify + generate): 50 × $0.015 = **$0.75** (**3x more**)

---

## Implementation Roadmap

### Phase 1 (DONE): Template Mode
✅ ML classification
✅ Template generator
✅ API integration
✅ Story points

### Phase 2A: LLM Prompt Engineering
1. Create `generator_llm.py`:
   - Prompt template with JSON schema
   - Few-shot examples (3-5 per type)
   - LLM API integration (OpenAI/Anthropic/Google)
   - JSON parsing + validation
   - Repair logic for malformed JSON
2. Add `mode='llm'` to pipeline
3. Test on sample documents
4. Compare output quality

**Timeline**: 2-3 days

### Phase 2B: Local Model Fine-tuning
1. Generate **Silver dataset**:
   - Use LLM to generate tasks for 10K requirements
   - Auto-label with high confidence
2. Human review **Gold subset** (1K tasks):
   - Sample stratified by type/priority/domain
   - Correct errors, improve quality
3. Fine-tune T5-base/BART/Flan-T5:
   - Input: requirement text + labels
   - Output: JSON task
   - Train on 1K gold + 9K silver
4. Deploy local model:
   - ~500MB model size
   - ~5-10 tasks/second on CPU
   - ~50 tasks/second on GPU

**Timeline**: 1-2 weeks

### Phase 3: Continuous Learning
1. Collect user feedback (accept/edit/reject)
2. Periodically retrain:
   - Add accepted tasks to gold dataset
   - Fine-tune model monthly
3. A/B testing:
   - Compare template vs LLM acceptance rate
   - Track: edit distance, user satisfaction

---

## Code Examples

### Template Mode (Current)
```python
from requirement_analyzer.task_gen import get_pipeline

pipeline = get_pipeline(mode='template')
result = pipeline.generate_tasks(
    text=document,
    max_tasks=50
)
# Fast: ~2s for 50 tasks
# Output: Generic but consistent
```

### LLM Mode (To Implement)
```python
pipeline = get_pipeline(mode='llm', llm_provider='openai')
result = pipeline.generate_tasks(
    text=document,
    max_tasks=50
)
# Slow: ~60s for 50 tasks (parallel: ~10s)
# Output: Natural and context-aware
```

### Hybrid Config
```python
{
  "classification": "ml",      # ML models (fast)
  "generation": "llm",         # LLM (natural)
  "llm_provider": "openai",
  "llm_model": "gpt-4o-mini",  # Cheap: $0.15/1M input tokens
  "parallel_requests": 5        # Speed up
}
```

---

## Prompt Engineering (LLM Mode)

### Prompt Structure
```
You are a software project manager creating Jira tasks from requirements.

**Input:**
- Requirement: {requirement_text}
- Type: {type}
- Priority: {priority}
- Domain: {domain}
- Role: {role}

**Output JSON Schema:**
{
  "title": "string (5-10 words, action-oriented)",
  "description": "string (2-4 sentences, technical details)",
  "acceptance_criteria": ["string", ...] (3-8 items, testable),
  "labels": ["string", ...]
}

**Examples:**
[Few-shot examples here - 3 per type]

**Your task:**
Generate a realistic Jira task. Be specific, use domain terminology, include technical details.
```

### Few-Shot Examples (Critical!)
```json
[
  {
    "requirement": "System must support concurrent users",
    "type": "performance",
    "output": {
      "title": "Optimize Database for Concurrent User Load",
      "description": "Implement connection pooling and query optimization...",
      "acceptance_criteria": [...]
    }
  },
  // ... 2 more examples
]
```

**Why few-shot?**
- Guides LLM output format
- Shows level of detail expected
- Reduces hallucination

---

## Cost Analysis

### Template Mode
- **Dev cost**: 1 week (done)
- **Runtime cost**: $0
- **Infrastructure**: CPU only (~$20/month)

### LLM API Mode (GPT-4o-mini)
- **Dev cost**: 2-3 days
- **Runtime cost**:
  - Input: ~200 tokens/request × $0.15/1M = $0.00003
  - Output: ~300 tokens × $0.60/1M = $0.00018
  - **Total: ~$0.0002/task** → $10 for 50K tasks
- **Infrastructure**: Same + API key

### Local Fine-tuned Model
- **Dev cost**: 1-2 weeks (data prep + training)
- **Training cost**: ~$50 (GPU hours)
- **Runtime cost**: $0
- **Infrastructure**: GPU (~$100/month) or CPU (~$30/month, slower)

### ROI Calculation (1 year, 10K tasks/month)
| Mode | Setup | Monthly | Annual Total |
|------|-------|---------|--------------|
| Template | $0 | $20 | $240 |
| LLM API | $0 | $20 + $20 | $480 |
| Local Fine-tuned | $50 | $100 | $1,250 |

**But**: User acceptance rate matters!
- Template: 60% accepted → waste 40% of PM time reviewing
- LLM: 85% accepted → save PM time

**Adjusted ROI** (PM time = $50/hour, 5min/task review):
- Template: 10K × 40% × 5min × $50/60 = **$1,666/month waste**
- LLM: 10K × 15% × 5min × $50/60 = **$625/month waste**
- **Savings: $1,041/month** → LLM pays for itself!

---

## Recommendation

### For Your Project

**Short-term (Now)**: Deploy Template Mode
- Reason: Fast to market, no extra dependencies
- Use case: Internal tool, low volume

**Medium-term (Next sprint)**: Add LLM Mode
- Reason: User feedback "output rất giả"
- Use GPT-4o-mini (cheap: $0.0002/task)
- Implement parallel requests (5-10 concurrent)
- Expected: 85%+ acceptance rate

**Long-term (3 months)**: Fine-tune Local Model
- Reason: Cost savings at scale, offline capability
- Collect 1K gold labels from user feedback
- Fine-tune Flan-T5-base (~500MB)
- Expected: 80%+ acceptance, $0 runtime cost

---

## Decision Matrix

Choose mode based on:

| Criteria | Template | LLM API | Local Fine-tuned |
|----------|----------|---------|------------------|
| **Volume** < 1K tasks/month | ✅ | ✅ | ❌ (overkill) |
| **Volume** 1K-10K/month | ⚠️ | ✅ | ⚠️ |
| **Volume** > 10K/month | ❌ | ⚠️ | ✅ |
| **Quality priority** | ❌ | ✅ | ✅ |
| **Speed priority** | ✅ | ❌ | ⚠️ |
| **Budget < $50/month** | ✅ | ⚠️ | ❌ |
| **Offline required** | ✅ | ❌ | ✅ |

---

## Next Steps

1. **Test current template mode**:
   ```bash
   bash scripts/task_generation/run_full_pipeline.sh
   python scripts/task_generation/demo_task_generation.py
   ```

2. **Decide on LLM provider**:
   - OpenAI GPT-4o-mini: Best quality/cost
   - Anthropic Claude Haiku: Fast, good
   - Google Gemini Flash: Cheapest
   - Groq (free tier): Fast inference

3. **Implement LLM mode** (if approved):
   - Create `generator_llm.py`
   - Add prompt templates
   - Integrate with pipeline
   - A/B test vs template

4. **Collect feedback**:
   - Use `/tasks/feedback` endpoint
   - Track acceptance rate
   - Build gold dataset

---

**Document Version**: 1.0  
**Author**: AI Team  
**Last Updated**: 2026-01-20
