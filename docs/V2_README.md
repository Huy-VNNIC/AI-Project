# V2 Requirements Engineering Pipeline - Quick Start

## What is V2?

V2 is a comprehensive Requirements Engineering system that:
- ✅ Transforms raw requirements → User Stories with proper AC (Given/When/Then)
- ✅ Detects gaps, ambiguities, contradictions (10+ rule types)
- ✅ Slices requirements into vertical stories (Workflow/Data/Risk/Role)
- ✅ Scores stories using INVEST criteria (Independent, Negotiable, Valuable, Estimable, Small, Testable)
- ✅ Generates 5-7x more tasks than V1 with full traceability
- ✅ Supports Vietnamese language throughout

## Quick Test

```bash
# Run V2 pipeline on first 5 hotel requirements
python3 test_v2_pipeline.py

# Output:
# ✅ 5 reqs → 27 stories → 81 subtasks
# ✅ 10 gaps detected
# ✅ 24.0/30 average INVEST score
# ✅ Report: V2_EVAL_REPORT.md
```

## Results Summary

**V1 (Old System):**
- 57 requirements → 165 tasks (2.9x)
- Simple role-based splitting (Backend/Frontend/QA)
- No gap detection, no INVEST scoring

**V2 (New System):**
- 5 requirements → 27 stories → 81 subtasks (5.4x stories, 16.2x tasks)
- User Stories with Given/When/Then AC
- 10 gaps detected (2.0 per requirement)
- 24/30 average INVEST score
- Full traceability

## Key Features

### 1. Refinement (User Story + AC)
```yaml
Input: "Phát triển hệ thống quản lý khách sạn"

Output:
  user_story: "Là một Quản lý, tôi muốn quản lý khách sạn, để tự động hóa quy trình"
  acceptance_criteria:
    - AC1: Given đã đăng nhập, When thực hiện, Then thành công
    - AC2: Given invalid input, When cố gắng, Then hiển thị lỗi
```

### 2. Gap Detection (10+ Rules)
- ❌ Missing actor: "Ai sử dụng?"
- ❌ Missing error handling: "Lỗi xử lý sao?"
- ❌ Missing permissions: "Ai có quyền?"
- ❌ Ambiguity: "etc", "vv", "hợp lý"

### 3. Smart Slicing (5 Strategies)
- **Workflow**: Happy path + Edge cases
- **Data**: CRUD operations
- **Risk**: High-risk scenarios
- **Role**: Different users
- **Integration**: External systems

### 4. INVEST Scoring (0-30)
- **27-30**: Excellent story ✅
- **20-26**: Good story ✅
- **15-19**: Needs work ⚠️
- **<15**: Poor story ❌

## Architecture

```
Raw Requirement
    ↓
[Stage 1: Refinement] → User Story + AC
    ↓
[Stage 2: Gap Detection] → Gaps + Questions
    ↓
[Stage 3: Smart Slicing] → Slices + Stories
    ↓
[Stage 4: Task Generation] → Backend/Frontend/QA Tasks
    ↓
Output: Stories + Tasks + Gaps + Traceability
```

## File Structure

```
requirement_analyzer/task_gen/
├── schemas_v2.py         # Pydantic models + validation
├── refinement.py         # User Story + AC generator
├── gap_detector.py       # 10+ gap detection rules
├── slicer.py            # Smart slicing + INVEST
└── pipeline_v2.py       # Pipeline orchestrator

test_v2_pipeline.py      # Test script
V2_EVAL_REPORT.md        # Evaluation report
V2_DOCUMENTATION.md      # Full documentation
```

## Test Output Sample

```
======================================================================
V2 Pipeline: Processing 5 requirements
======================================================================

[1/5] Processing REQ001...
  [Stage 1] Refining REQ001...
  [Stage 2] Detecting gaps in REQ001...
  [Stage 3] Slicing REQ001 into stories...
  ✅ Completed REQ001 in 0.00s
     └─ 5 stories, 15 subtasks, 2 gaps

...

======================================================================
V2 Pipeline: Completed in 0.00s
======================================================================
  Requirements: 5 → 5 processed (100.0%)
  Stories: 27 (5.4 per req)
  Subtasks: 81 (16.2 per req)
  Gaps: 10 (2.0 per req)
  INVEST Score: 24.0/30 average
  Critical Gaps: 0
======================================================================
```

## Next Steps

1. **Read Full Docs**: See `V2_DOCUMENTATION.md`
2. **Test More**: Run on your requirements file
3. **Integrate API**: Add `/api/v2/generate` endpoint
4. **Customize**: Add domain-specific gap rules

## Key Metrics

| Metric | V1 | V2 | Improvement |
|--------|----|----|-------------|
| Stories/Req | 0 | 5.4 | ♾️ |
| Tasks/Req | 2.9 | 16.2 | +459% |
| Gap Detection | ❌ | ✅ 2.0/req | New |
| INVEST Score | ❌ | ✅ 24/30 | New |
| User Stories | ❌ | ✅ Proper format | New |
| AC Format | Simple | Given/When/Then | ✅ |
| Traceability | Partial | Full | ✅ |

## Status

- ✅ **Core Pipeline**: Implemented (5 modules, 1,673 LOC)
- ✅ **Testing**: 100% success rate on 5 requirements
- ✅ **Documentation**: Complete (V2_DOCUMENTATION.md, V2_README.md)
- ⏳ **API Integration**: Not yet implemented
- ⏳ **Frontend**: Not yet implemented
- ⏳ **LLM Integration**: Not yet implemented (gaps detection only uses rules)

## Branch

`feature/v2-requirements-engineering`

## Commit

`85fcf13b - feat(v2): Implement Requirements Engineering pipeline`
