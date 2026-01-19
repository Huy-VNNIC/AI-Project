# OOD Evaluation - Status Report

**Date**: 2026-01-20  
**Status**: ✅ Ready for Pilot Scoring  
**Generator**: ModelBasedTaskGenerator (confirmed)

---

## 📊 Generation Statistics

| Metric | Value | Note |
|--------|-------|------|
| **Total Requirements** | 250 | Diverse domains (banking, healthcare, e-commerce, HR, etc.) |
| **Successful** | 184 (73.6%) | Generated tasks |
| **Failed** | 66 (26.4%) | No output |
| **Generator Used** | `ModelBasedTaskGenerator` | ✅ Confirmed model mode |

---

## 🔍 Failure Taxonomy (66 cases)

| Category | Count | % of Failures | Root Cause |
|----------|-------|---------------|------------|
| **Other** | 35 | 53.0% | Detector threshold too strict for OOD patterns |
| **Modal Only** | 12 | 18.2% | Requirements starting with "shall be able to..." |
| **Not a Requirement** | 11 | 16.7% | Descriptions/notes (not actual requirements) |
| **Too Complex** | 8 | 12.1% | Multiple clauses, long specs |

### Key Insights:

1. **53% "Other" failures** → Detector threshold is tuned for in-domain, struggles with OOD styles
2. **18% Modal-only** → Need to extract main verb AFTER modal ("shall be able to prescribe" → "prescribe")
3. **17% Not requirements** → Dataset includes descriptions/notes that should be filtered

### Recommendations:

✅ **High Impact**:
- Lower detector confidence threshold for OOD (0.5 → 0.3)
- Improve modal verb handling: extract verb after "shall/must be able to"

✅ **Medium Impact**:
- Pre-filter dataset: remove rows starting with "A ", "An ", "These are", "When in"
- Add sentence splitting for complex multi-clause requirements

---

## 🎯 Quality Issues (Success Cases)

### Issue 1: Generic/Poor Titles (High Priority)

**Problem**: Titles use generic objects instead of specific ones.

**Examples**:
| Requirement | Generated Title | Expected |
|-------------|----------------|----------|
| "The system must verify user identity through two-factor auth..." | ❌ "Verify the system" | ✅ "Enable two-factor authentication" |
| "Users should transfer funds between accounts instantly..." | ❌ "Add users transfer" | ✅ "Transfer funds between accounts" |
| "The application must encrypt financial transactions..." | ❌ "Build the application capability" | ✅ "Encrypt financial transactions" |

**Root Cause**:
- Entity extraction prioritizes generic objects: `{system, application, platform}`
- Should skip these and use specific noun phrases: `{user identity, funds, transactions}`

**Fix**:
```python
# In generate_title(), skip generic objects
GENERIC_OBJECTS = {'system', 'application', 'platform', 'feature', 'functionality'}

for candidate in entities['objects']:
    if candidate.lower() not in GENERIC_OBJECTS:
        obj = candidate
        break
```

---

### Issue 2: Wrong Domain Labels (Expected for OOD)

**Problem**: Many requirements assigned wrong domain.

**Examples**:
- Banking requirement → labeled "ecommerce"
- Healthcare requirement → labeled "finance"
- HR requirement → labeled "ecommerce"

**Root Cause**: Model only knows 5 domains: {ecommerce, finance, healthcare, iot, education}

**Not a Bug**: This is expected for OOD domains (HR, gaming, real estate, logistics).

**Fix for Scoring**:
- Add `domain_applicable` column (1 if in-scope, 0 if OOD)
- Only calculate domain accuracy for in-scope domains
- For OOD domains, mark as "N/A" or add "general" class

---

### Issue 3: Boilerplate Acceptance Criteria (Medium Priority)

**Problem**: Many AC are generic boilerplate, not testable.

**Examples**:
- ❌ "Feature works correctly for X"
- ❌ "All error conditions handled gracefully"
- ❌ "System validates all input before processing"
- ❌ "Response time under 2 seconds" (not related to requirement)

**Root Cause**: Template patterns bleeding into model generation.

**Fix**:
- Deduplicate AC by normalized text
- Filter generic phrases if confidence < threshold
- Prioritize requirement-specific criteria

---

### Issue 4: WCAG in Non-UI Tasks (Fixed ✅)

**Status**: Already fixed in postprocessor
- WCAG criteria now filtered from `type != interface` tasks

---

## 📋 Next Steps

### Phase 1: Pilot Evaluation (NOW)

1. ✅ **Rubric created**: [OOD_SCORING_RUBRIC.md](OOD_SCORING_RUBRIC.md)
2. ✅ **Pilot sample extracted**: [ood_pilot.csv](ood_pilot.csv) (50 rows)
3. 🔄 **Manual scoring** (10-15 min/row):
   - Open [ood_pilot.csv](ood_pilot.csv) in spreadsheet
   - Score using rubric
   - Save scored file
4. 🔄 **Run summary**:
   ```bash
   python scripts/eval/02_summarize_ood_scores.py scripts/eval/ood_pilot.csv
   ```

### Checkpoint: If avg_quality < 3.2 → STOP and apply fixes

---

### Phase 2: Quality Fixes (If Needed)

**Priority 1 - High Impact, Low Effort**:

1. **Fix generic title objects** (20 lines of code):
   ```python
   # requirement_analyzer/task_gen/generator_model_based.py
   GENERIC_OBJECTS = {'system', 'application', 'platform', 'feature'}
   
   for candidate in entities['objects']:
       words = candidate.split()
       if not words or words[0].lower() not in GENERIC_OBJECTS:
           obj = candidate
           break
   ```

2. **Improve modal verb extraction** (15 lines):
   ```python
   # Extract main verb after "shall/must be able to"
   if 'be able to' in text.lower():
       match = re.search(r'(?:shall|must|should) be able to (\w+)', text.lower())
       if match:
           action = match.group(1)
   ```

3. **Deduplicate AC** (already in postprocessor, may need tuning)

**Priority 2 - Medium Impact**:

4. **Lower detector threshold**: Change from 0.5 → 0.3 for OOD
5. **Filter dataset**: Remove descriptions/notes before generation

---

### Phase 3: Full Evaluation (After Pilot Pass)

- Score all 184 success rows
- Calculate final metrics
- Document for "Production Ready" status

---

## 🎯 Pass Criteria (Production Ready)

| Metric | Target | Current Status |
|--------|--------|----------------|
| **Avg Quality Score** | ≥ 3.5/5 | 🔄 Pending pilot |
| **Duplicate Rate** | ≤ 10% | 🔄 Pending pilot |
| **Type Accuracy** | ≥ 80% | 🔄 Pending pilot |
| **Domain Accuracy** | ≥ 80% (in-scope only) | ⚠️ Expected low for OOD |
| **Generation Coverage** | ≥ 80% | ⚠️ 73.6% (need fixes) |

---

## 📁 Files Created

| File | Purpose |
|------|---------|
| [OOD_SCORING_RUBRIC.md](OOD_SCORING_RUBRIC.md) | Detailed scoring guide |
| [ood_pilot.csv](ood_pilot.csv) | 50 random rows for pilot |
| [failure_analysis.txt](failure_analysis.txt) | Detailed failure breakdown |
| [extract_pilot_sample.py](extract_pilot_sample.py) | Sample extraction tool |
| [analyze_failures.py](analyze_failures.py) | Failure taxonomy analyzer |

---

## 🚀 Action Items (Checklist)

### TODAY (Pilot Evaluation):

- [ ] Score 50 pilot rows using [OOD_SCORING_RUBRIC.md](OOD_SCORING_RUBRIC.md)
- [ ] Run summary: `python scripts/eval/02_summarize_ood_scores.py scripts/eval/ood_pilot.csv`
- [ ] If avg < 3.2: Apply Priority 1 fixes (generic objects, modal verbs)
- [ ] If avg ≥ 3.5: Proceed to full evaluation

### AFTER PILOT (If Fixes Needed):

- [ ] Fix generic title objects (generator_model_based.py)
- [ ] Improve modal verb handling
- [ ] Retrain or lower detector threshold
- [ ] Re-run OOD generation on failed 66 rows
- [ ] Re-evaluate pilot

### FINAL (Production Ready):

- [ ] Score all 184 rows
- [ ] Generate final report
- [ ] Update README with OOD evaluation results
- [ ] Commit to GitHub with tag `v1.0-production-ready`

---

**Prepared by**: AI Task Generation Team  
**Next Review**: After pilot scoring complete
