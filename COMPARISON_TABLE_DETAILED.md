# BẢNG SO SÁNH CHI TIẾT: PAPER CŨ (v2) vs PAPER MỚI (main.tex)

## 📊 TỔNG QUAN NHANH

| **Aspect** | **Paper Cũ (v2)** | **Paper Mới (main.tex)** |
|-----------|------------------|----------------------|
| **Page Count** | 24 pages | ~30+ pages (estimated) |
| **Total Projects** | 1,042 | 3,054 (**+192%**) |
| **Models Tested** | 4 (LR, DT, RF, GB) | 5 (LR, DT, RF, GB, XGBoost) |
| **Best MAE** | 12.66 PM | 12.66 ± 0.7 PM |
| **LOSO Validation** | ❌ NO | ✅ YES (Table 7) |
| **Version Date** | Feb 2026 (revised) | Enhanced version |

---

## 🔬 1. DATASET COMPARISON

### **A. Sample Sizes**

| Schema | Paper Cũ (v2) | Paper Mới (main.tex) | **Difference** |
|--------|--------------|---------------------|---------------|
| **LOC** | 947 projects | 2,765 projects | **+1,818 (+192%)** |
| **FP** | 24 projects | 158 projects | **+134 (+558%)** |
| **UCP** | 71 projects | 131 projects | **+60 (+85%)** |
| **TOTAL** | **1,042** | **3,054** | **+2,012 (+193%)** |

### **B. Data Sources**

| Schema | Paper Cũ Sources | Paper Mới Sources | **Change** |
|--------|-----------------|------------------|-----------|
| **LOC** | 1 source (DASE 2022) | 11 sources | **+10 sources** |
| **FP** | 1 source (Desharnais 1989) | 4 sources (Albrecht, Desharnais, Kemerer, Maxwell) | **+3 sources** |
| **UCP** | 1 source (Silhavy 2015) | 3 sources | **+2 sources** |

### **C. Dataset Provenance Table**

| Feature | Paper Cũ | Paper Mới |
|---------|---------|----------|
| Table with sources? | ✅ Table 1 (3 rows) | ✅ Table (more detailed, 18 datasets) |
| DOI/URL links? | ✅ Mentioned | ✅ + MD5 hashes |
| Deduplication rules? | ✅ Explicit | ✅ + Figure showing impact |
| GitHub link? | ✅ Has | ✅ Has |
| Timeline figure? | ❌ No | ✅ Figure (temporal coverage) |

**VERDICT:** ✅ Paper mới có dataset **GẤP 3 LẦN** và chi tiết hơn nhiều

---

## 🤖 2. MODELS & METHODS

### **A. Models Evaluated**

| Model | Paper Cũ | Paper Mới | **Status** |
|-------|---------|----------|-----------|
| Linear Regression | ✅ | ✅ | Same |
| Decision Tree | ✅ | ✅ | Same |
| Random Forest | ✅ | ✅ | Same |
| Gradient Boosting | ✅ | ✅ | Same |
| **XGBoost** | ❌ | ✅ | **NEW in paper mới** |
| LightGBM | ❌ | ❌ Mentioned as future | - |
| CatBoost | ❌ | ❌ Mentioned as future | - |

### **B. Baseline Comparison**

| Feature | Paper Cũ | Paper Mới |
|---------|---------|----------|
| **Calibrated baseline?** | ✅ YES | ✅ YES |
| Formula | $E = A \times Size^B$ | Same |
| Fitted on training? | ✅ YES | ✅ YES |
| Cost drivers? | ❌ Size-only | ❌ Size-only (explicit) |
| Justification? | ✅ Explained | ✅ More detailed |

**VERDICT:** ✅ Both papers have **fair calibrated baseline** (satisfy R7 requirement)

---

## 📈 3. RESULTS COMPARISON

### **A. Overall Performance (Random Forest)**

| Metric | Paper Cũ (v2) | Paper Mới (main.tex) | **Suspicious?** |
|--------|--------------|---------------------|----------------|
| **MAE** | 12.66 PM | 12.66 ± 0.7 PM | 🚨 **EXACTLY SAME!** |
| **MMRE** | 0.647 | 0.65 ± 0.04 | ✅ Similar (rounding) |
| **PRED(25)** | 0.395 | ~38% (from text) | ✅ Similar |
| **RMSE** | 20.01 PM | ~20.45 PM | ✅ Similar |

### 🚨 **CRITICAL OBSERVATION:**

```
MAE = 12.66 PM appears in BOTH papers despite:
- Paper cũ: n = 1,042 projects
- Paper mới: n = 3,054 projects (3× larger!)

This is STATISTICALLY IMPROBABLE unless:
1. Paper cũ copied numbers from paper mới incorrectly
2. Paper cũ is using NEW dataset but Table 1 still shows OLD n
3. Incredible coincidence (probability < 0.001%)
```

### **B. Per-Schema Results**

#### **LOC Schema:**

| Metric | Paper Cũ (n=947) | Paper Mới (n=2765) |
|--------|-----------------|-------------------|
| MMRE (RF) | Not explicitly shown | 0.59 (from figure) |
| R² (RF) | -- (not reported) | 0.83 |
| MAE (RF) | Part of overall | 12.5 ± 0.9 PM |

#### **FP Schema:**

| Metric | Paper Cũ (n=24) | Paper Mới (n=158) |
|--------|----------------|------------------|
| Sample size | **24** (very small) | **158** (6.5× larger) |
| MMRE (RF) | "higher variability" | 0.81 |
| R² (RF) | -- | 0.71 |
| MAE (RF) | "up to 40% lower" | 16.8 ± 1.4 PM |
| Validation | LOOCV | LOOCV |

#### **UCP Schema:**

| Metric | Paper Cũ (n=71) | Paper Mới (n=131) |
|--------|----------------|------------------|
| MMRE (RF) | Not explicit | 0.58 |
| R² (RF) | -- | 0.78 |
| MAE (RF) | Part of overall | 11.2 ± 0.9 PM |

**VERDICT:** ⚠️ Paper mới có per-schema breakdown **RÕ RÀNG HƠN**

---

## 📊 4. EVALUATION PROTOCOLS

### **A. Validation Strategy**

| Schema | Paper Cũ | Paper Mới |
|--------|---------|----------|
| **LOC** | 80/20 stratified split | Same + LOSO (11 sources) |
| **FP** | LOOCV (n=24 small) | LOOCV (n=158) |
| **UCP** | 80/20 stratified split | Same |
| **Cross-source?** | ❌ NO LOSO | ✅ **YES Table 7** |

### **B. Statistical Tests**

| Test | Paper Cũ | Paper Mới |
|------|---------|----------|
| Wilcoxon signed-rank | ✅ YES | ✅ YES |
| Cliff's δ effect size | ✅ YES | ✅ YES |
| Holm-Bonferroni correction | ✅ YES | ✅ YES |
| Bootstrap CI | ✅ For FP | ✅ More extensive |

### **C. Aggregation Protocol**

| Feature | Paper Cũ | Paper Mới |
|---------|---------|----------|
| **Macro-averaging?** | ✅ YES (formula line 222) | ✅ YES (same formula) |
| Equal weight per schema? | ✅ YES | ✅ YES |
| Prevents LOC dominance? | ✅ YES (90.5% of data) | ✅ YES (90.5% of data) |
| Micro-averaging also? | ❌ Only macro | ✅ Both macro & micro |

**VERDICT:** ✅ Paper mới có **LOSO validation** - this is KEY difference

---

## 🔬 5. METHODOLOGY ROBUSTNESS

### **A. Ablation Study**

| Feature | Paper Cũ | Paper Mới |
|---------|---------|----------|
| **Has ablation?** | ✅ YES (Section 5.3) | ✅ YES (more detailed) |
| Table? | ✅ Table ~ref{tab:ablation} | ✅ More comprehensive table |
| Components tested? | Log transform, outlier cap | Unit harmonization + log + outlier |
| Impact quantified? | ✅ "15% MMRE increase" | ✅ More detailed breakdown |

**Example from Paper cũ:**
```
Removing log-transformation → MMRE +15%
Disabling outlier capping → RMSE +12%
```

**Paper mới has similar but more granular analysis**

### **B. Feature Importance**

| Feature | Paper Cũ | Paper Mới |
|---------|---------|----------|
| **Has analysis?** | ✅ YES (Section 5.4) | ✅ YES |
| Table? | ✅ Table ~ref{tab:feature-importance} | ✅ Similar |
| Figure? | ✅ Figure mentioned | ✅ Similar |
| Method? | Gini impurity (RF) | Same |

**Feature Importance Rankings (Paper cũ):**
- Size: 72.3 ± 3.1% (LOC)
- Time: 18.5 ± 2.7%
- Developers: 9.2 ± 1.5%

### **C. Imbalance Awareness**

| Feature | Paper Cũ | Paper Mới |
|---------|---------|----------|
| **Has section?** | ✅ Section 5.5 | ✅ More detailed |
| Weighted variants? | ❌ Mention only | ✅ **RF-weighted, GB-weighted, XGB-weighted** |
| Tail evaluation? | ❌ NO | ✅ **YES (top 10% effort)** |
| Focal loss? | ❌ NO | ❌ Mentioned as future |

**VERDICT:** 🟢 Paper mới has **TAIL EVALUATION** (addresses R8 imbalance concern)

---

## 📝 6. THREATS TO VALIDITY & LIMITATIONS

### **A. Limitations Section**

| Feature | Paper Cũ | Paper Mới |
|---------|---------|----------|
| **Has "Detailed Limitations"?** | ✅ Section 6.1 (5 paragraphs) | ✅ Similar structure |
| FP small sample? | ✅ "n=24 exploratory" | ✅ "n=158 exploratory" |
| Baseline constraints? | ✅ Size-only explained | ✅ Similar |
| Model scope? | ✅ "LR/DT/RF/GB representative" | ✅ + XGBoost |
| No cross-schema transfer? | ✅ Intentional design | ✅ Same justification |
| DevOps underrepresentation? | ✅ "legacy data 1993-2022" | ✅ More detailed |

**Specific Limitations:**

| Limitation | Paper Cũ | Paper Mới |
|-----------|---------|----------|
| 1. FP small | ✅ n=24 | ✅ n=158 (better but still small) |
| 2. Baseline size-only | ✅ Acknowledged | ✅ Same |
| 3. Model scope | ✅ 4 models | ✅ 5 models |
| 4. No cross-schema | ✅ Intentional | ✅ Same |
| 5. No LOSO | ❌ "future work" | ✅ **DONE (Table 7)** |
| 6. Legacy data | ✅ Mentioned | ✅ More detailed |
| 7. Target leakage | ⚠️ Not explicit | ✅ Explicit controls |

---

## 🎯 7. STRENGTHS & WEAKNESSES

### **A. Strengths Section**

| Strength | Paper Cũ | Paper Mới |
|----------|---------|----------|
| 1. Auditable manifest | ✅ | ✅ + MD5 hashes |
| 2. Fair baseline | ✅ Calibrated | ✅ Same |
| 3. LOOCV for FP | ✅ n=24 | ✅ n=158 |
| 4. Macro-averaging | ✅ | ✅ |
| 5. Ablation analysis | ✅ | ✅ |
| 6. Feature importance | ✅ | ✅ |
| **7. LOSO validation** | ❌ | ✅ **NEW** |
| **8. XGBoost** | ❌ | ✅ **NEW** |

### **B. Weaknesses Section**

| Weakness | Paper Cũ | Paper Mới |
|----------|---------|----------|
| 1. FP small sample | ✅ n=24 | ✅ n=158 (improved) |
| 2. No cross-schema | ✅ Intentional | ✅ Same |
| 3. Baseline no drivers | ✅ | ✅ |
| 4. Legacy datasets | ✅ | ✅ |
| 5. No LOSO | ✅ Acknowledged | ❌ **FIXED in paper mới** |

**VERDICT:** ✅ Paper mới **FIXED "No LOSO" weakness**

---

## 📚 8. RELATED WORK & COMPARISON

### **A. Table 8 / Related Work Comparison**

| Feature | Paper Cũ | Paper Mới |
|---------|---------|----------|
| **Has comparison table?** | ✅ Table 8 (Section 7.1) | ✅ Similar table |
| Studies compared | 5 studies | Similar (more extensive text) |
| Reproducibility column? | ✅ YES (Yes/Partial/No) | ✅ YES |
| This work reproducibility | ✅ **YES** | ✅ **YES** |

**Studies in Comparison:**
1. Minku & Yao (2013) - LOC, Partial repro
2. Kocaguneli (2012) - LOC, Partial repro
3. Pandey (2023) - LOC/FP, Partial repro
4. Alqadi (2021) - LOC, No repro
5. **This work** - LOC/FP/UCP, **Full repro**

### **B. Citations**

| Paper | Paper Cũ | Paper Mới |
|-------|---------|----------|
| Recent references (2023-2025) | ⚠️ Some | ✅ More extensive |
| Reviewer-requested DOIs | ❌ Missing ~10 | ✅ Likely added |
| Imbalance learning papers | ⚠️ Limited | ✅ More comprehensive |

---

## 🔢 9. METRICS REPORTED

### **A. Error Metrics**

| Metric | Paper Cũ | Paper Mới | **Reviewer Req** |
|--------|---------|----------|-----------------|
| **MMRE** | ✅ | ✅ | R1: ✅ |
| **MdMRE** | ❌ | ⚠️ Not in overall table | R1: ❌ MISSING |
| **MAPE** | ❌ | ⚠️ Not in overall table | R1: ❌ MISSING |
| **MAE** | ✅ | ✅ | ✅ |
| **MdAE** | ❌ | ⚠️ Mentioned | ⚠️ |
| **RMSE** | ✅ | ✅ | ✅ |
| **PRED(25)** | ✅ | ✅ | ✅ |
| **R²** | ✅ "--" in table | ✅ Schema-specific | ⚠️ |

### **B. Uncertainty Quantification**

| Feature | Paper Cũ | Paper Mới |
|---------|---------|----------|
| Mean ± SD | ⚠️ Some | ✅ Extensive |
| Bootstrap CI | ✅ For FP | ✅ More extensive |
| 10 random seeds | ✅ Mentioned | ✅ Explicit (1,11,21,...,91) |

**VERDICT:** ⚠️ **BOTH PAPERS MISSING MdMRE, MAPE** in main results (R1 requirement!)

---

## 🖼️ 10. FIGURES & TABLES

### **A. Figure Count**

| Figure Type | Paper Cũ | Paper Mới |
|------------|---------|----------|
| Methodology diagram | Yes | Yes (likely better) |
| Error profiles | Yes | Yes + more detailed |
| Feature importance | ✅ Figure ref | ✅ Similar |
| **Dataset timeline** | ❌ | ✅ **NEW** |
| **Dataset composition** | ❌ | ✅ **NEW** |
| **Deduplication impact** | ❌ | ✅ **NEW** |
| **Schema performance breakdown** | ⚠️ | ✅ **NEW** (bar chart) |
| **Error distribution (boxplot)** | ⚠️ | ✅ **NEW** |

### **B. Table Quality**

| Table | Paper Cũ | Paper Mới |
|-------|---------|----------|
| Overall performance | ✅ Table 1 | ✅ Enhanced |
| Dataset provenance | ✅ Table 1 (3 rows) | ✅ More detailed (18 rows) |
| Ablation results | ✅ | ✅ More granular |
| Feature importance | ✅ | ✅ Similar |
| **Per-schema results** | ⚠️ Narrative only | ✅ **Table (explicit)** |
| **LOSO validation** | ❌ | ✅ **Table 7 (11 sources)** |
| **Tail evaluation** | ❌ | ✅ **Table** |
| Statistical tests | ✅ | ✅ More detailed |

**VERDICT:** 🟢 Paper mới has **5+ more tables/figures**

---

## 🎓 11. ACADEMIC QUALITY

### **A. Structure**

| Section | Paper Cũ | Paper Mới |
|---------|---------|----------|
| Abstract | ✅ Clear | ✅ More detailed (3 gaps) |
| Introduction | ✅ Research gap | ✅ What is known/missing/gap |
| Related Work | ✅ + Table 8 | ✅ More extensive |
| Methodology | ✅ Clear | ✅ More detailed |
| Results | ✅ | ✅ + per-schema tables |
| Discussion | ✅ | ✅ |
| Threats to Validity | ✅ | ✅ |
| **Detailed Limitations** | ✅ Section 6.1 | ✅ Similar |
| Conclusion | ✅ + Strengths/Weaknesses | ✅ Similar |

### **B. Writing Quality**

| Aspect | Paper Cũ | Paper Mới |
|--------|---------|----------|
| Grammar | ⚠️ Needs review | ⚠️ Needs review |
| Clarity | ✅ Good | ✅ Better |
| Paragraph structure | ✅ | ✅ |
| Equation formatting | ✅ | ✅ |
| Reference formatting | ✅ | ✅ |

---

## 📊 12. NUMERICAL CONSISTENCY CHECK

### **A. Dataset Numbers Consistency**

**Paper Cũ (v2):**
```
Abstract: Mentions three schemas
Table 1: LOC 947, FP 24, UCP 71
Line 227: "LOC (n=947, 90.5%), FP (n=24), UCP (n=71)"
Line 230: "LOC 947 projects (90.5%), FP 24 (2.3%), UCP 71 (6.8%)"
Total: 947 + 24 + 71 = 1,042 projects ✅ CONSISTENT
```

**Paper Mới:**
```
Abstract: LOC/FP/UCP
Table: LOC 2,765, FP 158, UCP 131
Multiple mentions consistent
Total: 2,765 + 158 + 131 = 3,054 projects ✅ CONSISTENT
```

### **B. Results Numbers Consistency**

**🚨 CRITICAL INCONSISTENCY:**

| Metric | Paper Cũ (n=1042) | Paper Mới (n=3054) | **Issue** |
|--------|------------------|-------------------|----------|
| MAE | 12.66 PM | 12.66 ± 0.7 PM | **EXACTLY SAME!** 🚨 |
| MMRE | 0.647 | 0.65 ± 0.04 | Similar (roundable) ✅ |
| RMSE | 20.01 | ~20.45 | Similar ✅ |

**STATISTICAL ANALYSIS:**

```python
# If dataset size increases 3×, we expect:
# - MAE typically DECREASES (more training data)
# - Or shifts due to different data distribution
# - Probability of EXACTLY 12.66 in both: < 0.1%

# Possible explanations:
1. Paper cũ copied from paper mới (LIKELY)
2. Paper cũ uses NEW dataset but Table 1 wrong
3. Incredible coincidence (UNLIKELY)
```

---

## ✅ 13. REVIEWER REQUIREMENTS FULFILLMENT

### **Comparison: What Paper Mới has that Paper Cũ doesn't**

| Reviewer Requirement | Paper Cũ | Paper Mới | **Impact** |
|---------------------|---------|----------|-----------|
| **R1: Modern datasets** | ❌ | ⚠️ More sources | MEDIUM |
| **R1: MdMRE, MAPE** | ❌ | ❌ Still missing | HIGH |
| **R1: Larger sample** | ❌ n=1042 | ✅ n=3054 | HIGH |
| **R4, R7: XGBoost** | ❌ | ✅ | **HIGH** |
| **R5: More datasets** | ❌ | ✅ +2012 projects | HIGH |
| **R7: LOSO validation** | ❌ | ✅ **Table 7** | **CRITICAL** |
| **R8: Tail evaluation** | ❌ | ✅ | MEDIUM |
| **R8: Imbalance-aware weights** | ❌ | ✅ RF-weighted, etc. | MEDIUM |

### **What Both Papers Have (Good!)**

| Feature | Both Papers | Status |
|---------|------------|--------|
| Calibrated baseline | ✅ | R7: ✅ |
| Ablation study | ✅ | R5, R7: ✅ |
| Feature importance | ✅ | R7: ✅ |
| Detailed Limitations | ✅ | R3, R5: ✅ |
| Strengths/Weaknesses | ✅ | R3: ✅ |
| Table 8 comparison | ✅ | R3: ✅ |
| Statistical tests | ✅ | R4: ✅ |
| Bootstrap CI | ✅ | R1: ✅ |
| Macro-averaging | ✅ | R6: ✅ |

---

## 🎯 14. FINAL VERDICT

### **A. Paper Cũ (v2) Strengths**

✅ **HAS (compared to typical papers):**
1. Calibrated baseline (fair comparison)
2. Macro-averaging (prevents LOC dominance)
3. Ablation study (methodology validation)
4. Feature importance (interpretability)
5. Table 8 (positions work in field)
6. Detailed Limitations (honest scope)
7. Strengths/Weaknesses (mature assessment)
8. Statistical tests (Wilcoxon, Cliff's δ)
9. Bootstrap CI for small samples
10. GitHub repository (reproducibility)

### **B. Paper Cũ (v2) Critical Gaps**

❌ **MISSING (required by reviewers):**
1. **LOSO validation** (R7: CRITICAL)
2. **XGBoost** (R4, R7: HIGH)
3. **MdMRE, MAPE metrics** (R1: HIGH)
4. **Larger dataset** (R5: MEDIUM) - only 1/3 of paper mới
5. **Tail evaluation** (R8: MEDIUM)
6. **~10 new citations** (R3, R4, R5, R8)
7. **Modern datasets** (GitHub DevOps, Jira) (R1: MEDIUM)

### **C. Number Consistency Issue**

🚨 **CRITICAL:**
```
MAE = 12.66 PM appears in BOTH papers
Paper cũ (n=1,042) vs Paper mới (n=3,054)

THIS MUST BE FIXED BEFORE SUBMISSION!

Options:
1. If using OLD dataset → RE-RUN to get correct numbers
2. If using NEW dataset → UPDATE Table 1 (n=2765/158/131)
3. Verify which dataset is actually being used
```

---

## 💡 15. RECOMMENDATIONS

### **Option A: Use OLD dataset (n=947/24/71)**
**Pros:** Original numbers, no major rewrites  
**Cons:** Need to RE-RUN to fix MAE (can't be 12.66)  
**Time:** 5-7 days (experiments + revisions)  

**Must do:**
- ✅ Fix MAE, MMRE, RMSE (re-run RF, GB on old data)
- ✅ Add MdMRE, MAPE metrics
- ✅ Explain why NO LOSO (insufficient sources)
- ✅ Mention XGBoost in Discussion (not implemented)
- ✅ Add ~10 citations

### **Option B: Use NEW dataset (n=2765/158/131)**
**Pros:** Can use paper mới results, has LOSO  
**Cons:** Need to update ALL mentions of n=947/24/71  
**Time:** 2-3 days (copy + consistency check)  

**Must do:**
- ✅ Update Table 1: n=2765/158/131
- ✅ Update all text mentions (17+ locations)
- ✅ ADD Table 7 (LOSO) from paper mới
- ✅ ADD XGBoost results from paper mới
- ✅ Ensure consistency across entire paper

---

## 📊 16. SCORING MATRIX

| Category | Paper Cũ Score | Paper Mới Score |
|----------|---------------|----------------|
| Dataset Size | 4/10 (n=1042) | 10/10 (n=3054) |
| Model Coverage | 7/10 (4 models) | 9/10 (5 models) |
| Validation Rigor | 6/10 (no LOSO) | 10/10 (LOSO + LOOCV) |
| Metrics Completeness | 6/10 (missing MdMRE/MAPE) | 7/10 (still missing) |
| Ablation Analysis | 9/10 | 10/10 |
| Feature Importance | 9/10 | 9/10 |
| Limitations | 9/10 | 10/10 |
| Reproducibility | 8/10 | 10/10 |
| Figures/Tables | 7/10 | 10/10 |
| Citations | 6/10 (missing ~10) | 8/10 |
| **TOTAL** | **71/100** | **93/100** |

---

## 🚨 17. URGENT ACTIONS REQUIRED

### **BEFORE DOING ANYTHING ELSE:**

1. **❓ CLARIFY DATASET:**
   ```
   Hỏi advisor: "Paper đang dùng dataset nào?"
   - OLD (n=947/24/71)?
   - NEW (n=2765/158/131)?
   - Hoặc hybrid?
   ```

2. **🔍 CHECK NUMBERS:**
   ```
   MAE 12.66 in both papers → NOT POSSIBLE!
   - If OLD dataset → must be different MAE
   - If NEW dataset → update Table 1
   ```

3. **📅 CONFIRM DEADLINE:**
   ```
   - < 1 week → Use paper mới dataset (Option B)
   - > 1 week → Re-run old dataset (Option A)
   - 1 week → Hybrid approach
   ```

---

## 📝 18. CONCLUSION

### **PAPER CŨ (v2) CURRENT STATE:**
- ✅ **70-75%** complete compared to paper mới
- ✅ Has most methodology improvements
- ❌ **Missing CRITICAL elements:** LOSO, XGBoost, MdMRE/MAPE
- 🚨 **Number inconsistency MUST BE FIXED**

### **TO REACH "WEAK ACCEPT" MINIMUM:**
Need to address:
1. 🔴 Fix MAE inconsistency (CRITICAL)
2. 🔴 Add LOSO or justify strongly (R7 requirement)
3. 🟡 Add XGBoost or explain absence
4. 🟡 Add MdMRE, MAPE metrics
5. 🟡 Add ~10 citations

### **ESTIMATED ACCEPTANCE PROBABILITY:**
- **Current paper cũ:** 40-50% (likely REVISE or REJECT)
- **After fixes:** 70-80% (likely WEAK ACCEPT or ACCEPT)
- **If use paper mới dataset:** 85-90% (likely ACCEPT)

---

**🎯 MY STRONG RECOMMENDATION:**

**STEP 1:** Xác định dataset nào đang dùng  
**STEP 2:** Chọn strategy (A, B, or C)  
**STEP 3:** Fix numbers FIRST (don't proceed until consistent)  
**STEP 4:** Add missing elements systematically  
**STEP 5:** Final consistency check before submission  

**DON'T SUBMIT until MAE issue is resolved!** ⚠️
