# 🎯 ACTION CHECKLIST - Next Steps for You

## Status: ✅ System Fixed - Now Awaiting Your Custom AI Model

---

## 📋 IMMEDIATE ACTIONS

### Phase 1: Understand the System (15 minutes)
- [ ] Read `LLMFREE_PIPELINE_READY.md` (architecture overview)
- [ ] Read `CUSTOM_AI_INTEGRATION_GUIDE.py` (implementation guide)
- [ ] Run `python3 test_llmfree_integration.py` (see system working)
- [ ] Examine generated tests structure

### Phase 2: Implement Your Custom AI Extractor (1-2 hours)
- [ ] Create file: `requirement_analyzer/task_gen/my_custom_extractor.py`
- [ ] Inherit from `RequirementExtractor` class
- [ ] Load your trained AI model in `__init__()`
- [ ] Implement `extract(requirement_text: str) -> StructuredIntent`
- [ ] Handle Vietnamese tokenization (underthesea or pyvi)
- [ ] Test extraction with 5 sample requirements

**Example Template:**
```python
from requirement_extractor import RequirementExtractor
from structured_intent import (
    StructuredIntent, DomainType, Entity, Action,
    Constraint, SecurityConcern
)

class MyCustomAIExtractor(RequirementExtractor):
    def __init__(self, model_path: str):
        """Load your trained AI model"""
        self.model = load_your_model(model_path)
        self.tokenizer = setup_vietnamese_tokenizer()
    
    def extract(self, requirement_text: str) -> StructuredIntent:
        """Extract structured intent from requirement"""
        # Tokenize Vietnamese text properly
        tokens = self.tokenizer.tokenize(requirement_text)
        # Run AI model
        output = self.model.predict(tokens)
        # Convert to StructuredIntent
        return StructuredIntent(
            requirement_id="REQ-001",
            domain=output['domain'],  # e.g., DomainType.HOTEL_MANAGEMENT
            entity=Entity(
                name=output['entity_name'],
                description=output['entity_desc'],
                attributes=output['attributes']
            ),
            action=Action(
                verb=output['action_verb'],
                target=output['action_target'],
                description=output['action_desc']
            ),
            constraints=[...],
            security_concerns=[...],
            confidence_score=output['confidence']
        )
```

### Phase 3: Integrate with API (30 minutes)
- [ ] Update `app/routers/tasks.py` line 20-25
  ```python
  from requirement_analyzer.task_gen.my_custom_extractor import MyCustomAIExtractor
  
  def get_adapter():
      global _adapter
      if _adapter is None:
          extractor = MyCustomAIExtractor(model_path="path/to/your/model.pkl")
          _adapter = get_llmfree_adapter(custom_extractor=extractor)
      return _adapter
  ```
- [ ] Test `/generate` endpoint with your model
- [ ] Verify proper TC-HOTEL-* test IDs generated
- [ ] Check real confidence scores (not 0.5)

### Phase 4: Validate & Deploy (30 minutes)
- [ ] Run end-to-end test with hotel requirements
- [ ] Check output has all 4 test types: happy_path, negative, security, edge_case
- [ ] Verify deduplication working (removed duplicates)
- [ ] Check effort estimates are realistic
- [ ] Deploy to staging/production
- [ ] Monitor first 10 requests for errors

---

## ✅ VERIFICATION CHECKLIST

After implementing your extractor, verify:

### Data Quality
- [ ] Domain detection: `hotel_management` ✅ (not generic)
- [ ] Test IDs: `TC-HOTEL-HAPP-001` ✅ (not TC-UNKNOWN)
- [ ] Confidence: 0.70-0.95 ✅ (not hardcoded 0.5)
- [ ] Effort: 0.2-1.0h ✅ (not hardcoded 0.0h)

### Test Generation
- [ ] Happy path tests generated ✅
- [ ] Negative tests generated ✅
- [ ] Security tests generated ✅
- [ ] Edge case tests generated ✅
- [ ] Deduplication working (>50% reduction) ✅

### API Integration
- [ ] POST /generate → returns test cases ✅
- [ ] POST /feedback → accepts user feedback ✅
- [ ] GET /stats → returns statistics ✅
- [ ] Vietnamese requirements handled ✅
- [ ] Error handling working ✅

### Performance
- [ ] Response time < 2 seconds ✅
- [ ] Concurrency supported ✅
- [ ] No memory leaks ✅
- [ ] Can handle 100+ tests ✅

---

## 📊 EXPECTED RESULTS

When you implement your custom AI extractor properly:

**Input:** 5 Hotel Requirements (Vietnamese)
```
Hệ thống phải cho phép đặt phòng mới với các thông tin: loại phòng, ngày check-in, ngày check-out
Hệ thống phải kiểm tra tính khả dụng của phòng theo loại và ngày
Hệ thống phải hỗ trợ đặt phòng trực tuyến và tại quầy lễ tân
Hệ thống phải cho phép xác nhận, hủy, và chỉnh sửa đơn đặt phòng
Hệ thống phải gửi email xác nhận khi đặt phòng thành công
```

**Output:** 4-6 Unique Domain-Specific Tests
```json
✅ TC-HOTEL-HAPP-001: Successfully book room with valid details
   Type: happy_path | Priority: HIGH | Confidence: 0.85 | Effort: 0.5h

✅ TC-HOTEL-NEGA-002: Reject booking with invalid dates
   Type: negative | Priority: HIGH | Confidence: 0.80 | Effort: 0.3h

✅ TC-HOTEL-SECU-003: Verify booking info not accessible to other users
   Type: security | Priority: HIGH | Confidence: 0.82 | Effort: 0.4h

✅ TC-HOTEL-EDGE-004: Handle concurrent booking for same room
   Type: edge_case | Priority: MEDIUM | Confidence: 0.75 | Effort: 0.2h
```

**Key Metrics:**
- Total Generated: 12 tests
- Deduplicated: 8 removed (0.85 similarity)
- Final Unique: 4 tests
- Average Quality: 0.81 confidence
- Average Effort: 0.35 hours
- Processing Time: <500ms

Now compare with BEFORE (the broken output):
```
❌ TC-UNKNOWN: System manages resource successfully
❌ TC-UNKNOWN: System manages resource with invalid data
❌ TC-UNKNOWN: System manages patient successfully
... (210 identical broken tests)
```

---

## 🚨 COMMON PITFALLS (Avoid These!)

### Pitfall 1: Not Handling Vietnamese Properly
```python
# ❌ WRONG
def extract(self, text):
    return self.model.predict(text)  # No tokenization!

# ✅ RIGHT
def extract(self, text):
    tokens = self.tokenizer.tokenize(text)  # Proper Vietnamese
    output = self.model.predict(tokens)
    return StructuredIntent(...)
```

### Pitfall 2: Returning Wrong Data Types
```python
# ❌ WRONG
return {
    "domain": "hotel",  # String, not DomainType enum
    "confidence": "0.85"  # String, not float
}

# ✅ RIGHT
return StructuredIntent(
    domain=DomainType.HOTEL_MANAGEMENT,  # Enum
    confidence_score=0.85  # Float
)
```

### Pitfall 3: Not Implementing Both Methods
```python
# ❌ WRONG - Only implements extract()
class MyExtractor(RequirementExtractor):
    def extract(self, text):
        return StructuredIntent(...)

# ✅ RIGHT - Implements both required methods
class MyExtractor(RequirementExtractor):
    def extract(self, text):
        return StructuredIntent(...)
    
    def extract_batch(self, texts):
        return [self.extract(t) for t in texts]
```

### Pitfall 4: Not Confidence Scoring
```python
# ❌ WRONG - All tests hardcoded 0.5
return StructuredIntent(..., confidence_score=0.5)

# ✅ RIGHT - Real scores from your model
score = self.model.get_confidence(tokens)
return StructuredIntent(..., confidence_score=score)
```

### Pitfall 5: Ignoring Errors
```python
# ❌ WRONG
def extract(self, text):
    return self.model.predict(text)  # No error handling

# ✅ RIGHT
def extract(self, text):
    if not text or len(text) < 10:
        raise ValueError("Requirement too short")
    try:
        output = self.model.predict(text)
        return StructuredIntent(...)
    except Exception as e:
        print(f"Extraction failed: {e}")
        raise
```

---

## 📞 SUPPORT RESOURCES

### Documentation Files
- `LLMFREE_PIPELINE_READY.md` - Complete system overview
- `CUSTOM_AI_INTEGRATION_GUIDE.py` - Step-by-step implementation guide
- `README_AI_PIPELINE.md` - Architecture and deployment
- `FIX_SUMMARY.py` - Before/after comparison

### Code Files Ready for Reference
- `requirement_analyzer/task_gen/structured_intent.py` - Data models
- `requirement_analyzer/task_gen/requirement_extractor.py` - Interface
- `requirement_analyzer/task_gen/test_generation_pipeline.py` - Main pipeline
- `requirement_analyzer/task_gen/deduplication_engine.py` - Dedup logic
- `requirement_analyzer/task_gen/api_adapter_llmfree.py` - API adapter

### Test Files
- `test_llmfree_integration.py` - Integration test (you can run this)
- `test_api_endpoint.py` - API endpoint test

---

## 🎓 LEARNING OBJECTIVES

By the end of Phase 2, you should understand:

- [ ] What StructuredIntent contains
- [ ] How RequirementExtractor interface works
- [ ] Why Vietnamese tokenization matters
- [ ] How domain detection works
- [ ] What confident scoring means
- [ ] How deduplication removes duplicates
- [ ] How API integration works

---

## ⏱️ ESTIMATED TIMELINE

- Phase 1 (Setup): 15 minutes
- Phase 2 (Implementation): 1-2 hours
- Phase 3 (Integration): 30 minutes
- Phase 4 (Testing): 30 minutes
- **Total: 2-3 hours** to working system

---

## 📈 SUCCESS CRITERIA

System is working when:

✅ You run `/generate` with hotel requirements
✅ You get back 4-10 unique tests (not 210 TC-UNKNOWN)
✅ Test IDs are TC-HOTEL-HAPP-001 format (not TC-UNKNOWN)
✅ Confidence scores are 0.70-0.95 (not hardcoded 0.5)
✅ Effort estimates are 0.2-1.0h (not hardcoded 0.0h)
✅ Tests are domain-specific (hotel_management, not generic)
✅ No broken Vietnamese in output
✅ Deduplication removed at least 50% of initial tests

---

## 🎯 YOUR GOAL

**Transform from:**
```
210 broken TC-UNKNOWN tests (0% quality)
with hardcoded metrics and broken Vietnamese
```

**To:**
```
4-10 unique domain-specific tests (80%+ quality)
with real metrics and proper Vietnamese support
```

---

Good luck! You've got this! 🚀

If you have questions, check the integration guide or existing test files.
