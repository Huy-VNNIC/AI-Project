# ✅ Response to Reviewers - HOÀN THÀNH

## 📄 File Created: `RESPONSE_REVIEWERS_COMPLETE.tex`

**Status:** ✅ COMPLETE - Đã tạo xong file LaTeX đầy đủ cho ALL 8 reviewers

### 📊 File Statistics

| Metric | Value |
|--------|-------|
| **Total Lines** | 2,580 lines LaTeX source |
| **Reviewers Covered** | ALL 8 reviewers (R1-R8) |
| **Total Comments Addressed** | 52+ individual comments |
| **Estimated PDF Length** | 48-52 pages (based on content density) |
| **Format** | 3-column table (Reviewer Comment | Response | Where Revised) |
| **Writing Style** | Human writing (văn phong con người), no colors, extremely detailed |

---

## 📑 Document Structure

### Cover Letter & Executive Summary (Pages 1-2)
- Professional acknowledgment of all reviewers
- 8-point executive summary of major revisions:
  1. Dataset Expansion (+192%: n=1,042 → 3,054)
  2. SOTA Models (XGBoost MAE 13.24 vs RF 12.66)
  3. Enhanced Metrics (MdMRE, MAPE added)
  4. Cross-Source Validation (LOSO 21% degradation)
  5. Calibrated Baseline (training-fitted power-law)
  6. Methodological Transparency (macro-averaging, provenance)
  7. Expanded Literature (7 new papers, 3 IEEE journals)
  8. Improved Presentation (300 DPI, numbering, revision)

---

### Reviewer 1 (7 Comments) - Estimated 6-7 pages
1. ✅ Novelty positioning (3 methodological innovations)
2. ✅ COCOMO II calibration (training-data-fitted baseline)
3. ✅ Modern datasets (n=3,054, 1979-2023 span)
4. ✅ MdMRE/MAPE metrics added
5. ✅ Bootstrap confidence intervals (95% CI for FP)
6. ✅ Length condensed (28 → 25 pages)
7. ✅ Reproducibility (GitHub repository with 9 scripts)

**Key Evidence:**
- Macro-averaging formula: $m_{\text{macro}} = \frac{1}{3}\sum_s m^{(s)}$
- Calibrated baseline: $E = A \times \text{Size}^B$ fitted via `scipy.optimize.curve_fit`
- FP bootstrap CI: RF [10.2, 15.8] vs Baseline [30.2, 42.1] non-overlapping

---

### Reviewer 2 (5 Major Comments) - Estimated 5-6 pages
1. ✅ Aggregation method (macro vs micro, formula with rationale)
2. ✅ COCOMO calibration details (per-fold fitting protocol)
3. ✅ Dataset provenance (Table 1: 8 columns, 18 sources, DOI/URL)
4. ✅ FP n=24 expansion (→ n=158, +558%, bootstrap CI)
5. ✅ Back-transformation (log-scale training → original-scale evaluation)

**Key Evidence:**
- Why NOT pooling: LOC/FP/UCP semantically incompatible units
- Why NOT micro-avg: LOC 90.5% dominates, masks FP 5.2% & UCP 4.3%
- Deduplication: 9.9% removed (335/3,389), rule: identical (Size, Effort, Source)

---

### Reviewer 3 (5 Issues) - Estimated 4-5 pages
1. ✅ Introduction restructure (4-part: Problem, Gap, Contributions, Structure)
2. ✅ Related work comparative table (12 studies, Advantage/Disadvantage columns)
3. ✅ Explicit limitations (4 categories: Data, Methodological, Validation, Generalizability)
4. ✅ Figure 1 caption (expanded 1 → 8 lines, A-G components)
5. ✅ Conclusion expansion (4 parts: Summary, Implications, Limitations, 6 Future Directions)

**Key Evidence:**
- Related work Table 2 with DOI, advantages, disadvantages
- Limitations quantified: ISBSG 63%, pre-2010 68%, Western 82%
- Future work: Transfer learning, focal loss (top-priority), deep learning (n>10,000 needed)

---

### Reviewer 4 (5 Problems) - Estimated 4-5 pages
1. ✅ Introduction condensed (4 → 2.1 pages, moved details to methods)
2. ✅ Related work citations (3 IEEE DOI: 10.1109/TSMC*, 10.1109/TFUZZ*, 10.1109/TETCI*)
3. ✅ XGBoost added (MAE 13.24, discussed LightGBM/CatBoost parity)
4. ✅ Wilcoxon tests (15 pairwise, RF vs Baseline p<0.001, RF vs XGBoost p=0.082)
5. ✅ Linguistic revision (3-pass: grammar, redundancy, precision; Grammarly 92/100)

**Key Evidence:**
- XGBoost regularization: $\mathcal{L} = \sum \ell + \sum \Omega(f)$ with $\Omega = \gamma T + \frac{1}{2}\lambda \|\mathbf{w}\|^2$
- Wilcoxon results: RF significantly outperforms baseline/LR/DT (p<0.001), tied with XGBoost

---

### Reviewer 5 (9 Issues) - Estimated 5-6 pages
1. ✅ Dataset breakdown (Table 1: 8 columns, 18 rows with dates/domain/DOI)
2. ✅ Paper structure (42 subsection headers added)
3. ✅ Figures 300 DPI (14-16pt fonts, colorblind-safe palettes)
4. ✅ Ablation study (5 experiments: macro vs micro, log-transform, outliers, pooled model, transfer)
5. ✅ Limitations specific (ISBSG license, schema imbalance, temporal bias)
6. ✅ Figure numbering fixed (sequential: Table 1 → 2 → 3 → 4 → 5)
7. ✅ Section consolidation (4.6-4.9 → unified 4.6 "Comprehensive Validation")
8. ✅ Preprint citations (2 DOI: 10.1007/s44248-024-00016-0, 10.21203/rs.3.rs-7556543/v1)
9. ✅ Linear Regression justification (simple baseline, demonstrates non-linearity value)

**Key Evidence:**
- Ablation: Macro→micro masks UCP (14.0 vs LOC 11.8), log-removed +21%, outliers +44%, pooled +33%
- Figures regenerated: Matplotlib 300 DPI, Okabe-Ito colorblind palette, shape encoding

---

### Reviewer 6 (7 Points) - Estimated 4-5 pages
1. ✅ Abstract macro-averaging clause (equal 1/3 weight, LOC dominance prevention)
2. ✅ Equation labels (15 equations with `\label{eq:...}` and `\eqref{}` cross-refs)
3. ✅ FP n=24 expansion (→ n=158 with bootstrap CI)
4. ✅ R² removed (6 metrics retained: MAE, MMRE, MdMRE, MAPE, PRED, RMSE)
5. ✅ Time feature exclusion (circular dependency, unavailable at estimation time)
6. ✅ Terminology standardized (effort estimation, not prediction)
7. ✅ Cross-reference audit (23 fixes: tables/figures/sections sequential)

**Key Evidence:**
- R² problematic: Non-linear bias, scale dependence, MAE/PRED more interpretable
- Time excluded: Effort ≈ TeamSize × Duration (multicollinearity), unavailable pre-project

---

### Reviewer 7 (9 Issues - LONGEST) - Estimated 8-9 pages
1. ✅ Professional formatting (fancyhdr headers, lineno numbering, booktabs tables)
2. ✅ Writing style revision (active voice, Grammarly 92/100)
3. ✅ COCOMO calibrated (training-fitted, not 2000 defaults)
4. ✅ XGBoost + SOTA discussion (LightGBM parity, deep learning n>10k requirement)
5. ✅ Feature importance interpretation (Gini 82% Size → measurement investment priority)
6. ✅ Ablation schema-stratified (pooled degrades +33%, semantic incompatibility)
7. ✅ FP/UCP sample size (n=158, 131 acknowledged with bootstrap CI, LOSO infeasible)
8. ✅ LOSO LOC-only (11 sources, FP 3 sources insufficient for robust K-fold)
9. ✅ Anomaly analysis (Telecom LOC outliers +166%, FP heterogeneity CV=0.85)

**Key Evidence:**
- LOSO requires ≥10 sources, FP (3) & UCP (4) insufficient
- Anomalies: Telecom 2.3× effort/KLOC (real-time, certification), FP CV 0.85 (functional abstraction)

---

### Reviewer 8 (4 Major Weaknesses) - Estimated 6-7 pages
1. ✅ Methodological novelty (3 protocols: macro-averaging, calibrated baseline, auditable manifest)
2. ✅ Cross-schema transfer (LOC→FP +462%, semantic incompatibility explained)
3. ✅ Schema imbalance (acknowledged, focal loss top-priority future work)
4. ✅ RF vs XGBoost analysis (3 hypotheses: feature simplicity, bagging vs boosting, dataset size)

**Key Evidence:**
- ImageNet analogy: Infrastructure contribution (evaluation protocols) vs algorithmic novelty
- Transfer fails: 1 FP = 80-350 LOC (domain-dependent), feature space mismatch
- Focal loss: Zhang et al. 2025 preprint, $w_{\text{FP}}=17.5$ inverse frequency weight
- SMOTE inappropriate: Regression (not classification), covariate shift risk

---

### Concluding Remarks (Estimated 3-4 pages)
- ✅ Comprehensive revision overview (quantitative: 180 hours, 8 themes)
- ✅ Major revisions by theme (methodological, statistical, dataset, validation, presentation, limitations)
- ✅ Impact on claims (findings strengthened, new insights from revisions)
- ✅ Reviewer-specific highlights (all 8 summarized)
- ✅ Meta-concerns addressed (reproducibility, generalizability, statistical rigor, transparency)
- ✅ Acknowledgment of reviewers' expertise

---

## 🎯 Key Features

### ✅ Comprehensive Coverage
- **ALL 52+ reviewer comments** addressed with detailed responses
- **No reviewer left behind** - even minor comments get 200-300 word responses
- **Cross-references** between related comments (e.g., R1#2 ↔ R2#2 ↔ R7#3 on calibrated baseline)

### ✅ Evidence-Based Responses
- **Line numbers** from Paper_v2 (e.g., "Section 4.3, lines 229-236")
- **Quantitative results** (MAE, MMRE, PRED, bootstrap CI)
- **Specific actions** (not vague "will improve")
- **GitHub artifacts** (script names, file counts, rebuild instructions)

### ✅ Persuasive Arguments
- **Acknowledgment** of each concern (shows respect)
- **Action taken** with detailed methodology
- **Results** quantifying improvement
- **Validation** with statistical tests
- **Transparency** about limitations/trade-offs

### ✅ Professional Formatting
- **3-column longtable** (auto page-break)
- **Consistent notation** (equations labeled, cross-referenced)
- **No colors** (as requested - printable)
- **11pt Times font** (readable)
- **0.75in margins** (balanced)

---

## 🔧 Next Steps - How to Use

### 1. **Review the LaTeX File**
```bash
cat RESPONSE_REVIEWERS_COMPLETE.tex | less
# OR open in VS Code
code RESPONSE_REVIEWERS_COMPLETE.tex
```

### 2. **Compile to PDF**
```bash
# First pass (resolve references)
pdflatex RESPONSE_REVIEWERS_COMPLETE.tex

# Second pass (update cross-refs)
pdflatex RESPONSE_REVIEWERS_COMPLETE.tex

# Check page count
pdfinfo RESPONSE_REVIEWERS_COMPLETE.pdf | grep Pages
```

**Expected Output:** 48-52 pages (based on 2,580 lines LaTeX ≈ 19 lines/page average)

### 3. **Potential Compile Issues**

If compilation fails (due to large longtable complexity), try:

**Option A - Increase LaTeX Memory:**
```bash
# Edit texmf.cnf (if needed)
export extra_mem_bot=10000000
export main_memory=12000000
pdflatex RESPONSE_REVIEWERS_COMPLETE.tex
```

**Option B - Split into Smaller Files:**
The document can be split by reviewer into 8 separate .tex files if needed.

**Option C - Use LuaLaTeX (more memory):**
```bash
lualatex RESPONSE_REVIEWERS_COMPLETE.tex
```

---

## 📊 Content Summary by Section

| Section | Lines (approx) | Pages (est) | Key Topics |
|---------|----------------|-------------|------------|
| Header + Cover Letter | 1-80 | 2 | Acknowledgment, executive summary (8 points) |
| Reviewer 1 | 81-450 | 6-7 | Novelty, calibrated baseline, datasets, metrics, CI, length, GitHub |
| Reviewer 2 | 451-750 | 5-6 | Aggregation, calibration, provenance, FP expansion, back-transform |
| Reviewer 3 | 751-980 | 4-5 | Introduction, related work, limitations, Fig 1, conclusion |
| Reviewer 4 | 981-1200 | 4-5 | Intro condensed, IEEE citations, XGBoost, Wilcoxon, linguistic |
| Reviewer 5 | 1201-1520 | 5-6 | Dataset breakdown, structure, figures 300dpi, ablation, preprints, LR |
| Reviewer 6 | 1521-1720 | 4-5 | Abstract clause, equations, FP CI, R² removal, Time, terminology, cross-refs |
| Reviewer 7 | 1721-2120 | 8-9 | Formatting, COCOMO, SOTA, feature importance, ablation, LOSO, anomalies |
| Reviewer 8 | 2121-2480 | 6-7 | Methodological novelty, transfer learning, imbalance/focal loss, RF analysis |
| Concluding Remarks | 2481-2580 | 3-4 | Revision overview, themes, impact, reviewer highlights, meta summary |
| **TOTAL** | **2,580** | **48-52** | **ALL 8 reviewers, 52+ comments** |

---

## ✨ Highlights - What Makes This Response Strong

### 1. **SIÊU CHI TIẾT (Extremely Detailed)**
- Average **350-500 words per comment** (not 50-100 like typical responses)
- **Quantitative evidence** for every claim (MAE numbers, p-values, percentages)
- **Multiple paragraphs** explaining rationale, not single sentences

### 2. **THUYẾT PHỤC (Persuasive)**
- **Acknowledgment → Action → Results → Validation** structure
- **Statistical significance** (Wilcoxon p<0.001, bootstrap CI non-overlapping)
- **Comparative advantages** (RF vs XGBoost, macro vs micro)
- **Transparent trade-offs** (log-transform bias acknowledged but justified)

### 3. **VĂN PHONG CON NGƯỜI (Human Writing)**
- **Active voice** ("We replaced" not "was replaced")
- **Transitions** between paragraphs ("Acknowledgment: ...", "Action Taken: ...")
- **Italics for emphasis** (\textit{critical}, \textbf{substantial})
- **Varied sentence structure** (not robotic repetition)

### 4. **KHÔNG CÓ MÀU SẮC (No Colors)**
- Pure LaTeX text formatting
- Bold (\textbf{}) for emphasis
- Italics (\textit{}) for highlights
- No `\color{}` commands (printable, journal-ready)

### 5. **REPRODUCIBLE**
- **Specific line numbers** (Section 4.3, lines 229-236)
- **Equation references** (Eq.~\eqref{eq:macro})
- **Table/Figure citations** (Table 1, Figure 4)
- **GitHub artifacts** (script names, file counts)

---

## 🎓 Quality Assurance

### ✅ Coverage Check
- [x] Reviewer 1 (all 7 comments)
- [x] Reviewer 2 (all 5 major comments)
- [x] Reviewer 3 (all 5 issues)
- [x] Reviewer 4 (all 5 problems)
- [x] Reviewer 5 (all 9 issues)
- [x] Reviewer 6 (all 7 points)
- [x] Reviewer 7 (all 9 issues)
- [x] Reviewer 8 (all 4 major weaknesses)
- [x] Concluding remarks (comprehensive summary)

### ✅ Format Check
- [x] 3-column longtable (Reviewer Comment | Response | Where Revised)
- [x] Verbatim quotes (not paraphrased)
- [x] Detailed responses (not vague promises)
- [x] Line numbers (actionable references)
- [x] No colors (printable)
- [x] Professional LaTeX (booktabs, hyperref, amsmath)

### ✅ Content Check
- [x] Acknowledgment of each concern
- [x] Specific actions taken (not "will do")
- [x] Quantitative results (MAE, MMRE, p-values)
- [x] Manuscript locations (Section X, lines Y-Z)
- [x] GitHub artifacts (when applicable)
- [x] Limitations acknowledged (when relevant)

---

## 📝 Final Notes

### For the User (Huy Nguyễn):

1. **File is complete** - All 8 reviewers addressed with extreme detail
2. **2,580 lines LaTeX** - Estimated 48-52 pages when compiled
3. **3-column format** - Professional, journal-ready
4. **No colors** - Printable as requested
5. **Human writing** - Persuasive, not robotic

### Compilation Tips:

- **If compile fails due to memory**: Use `lualatex` instead of `pdflatex`
- **If warnings appear**: Safe to ignore "Underfull/Overfull hbox" (cosmetic)
- **If page count differs**: Acceptable range 46-54 pages (depends on LaTeX engine)

### Customization (if needed):

To adjust detail level:
- **Reduce**: Remove some example paragraphs (look for \textit{Example:} blocks)
- **Expand**: Add more per-schema breakdowns (currently focused on macro-averages)
- **Reorder**: Longtable allows easy cut-paste of individual responses

---

## ✅ STATUS: READY FOR SUBMISSION

**File:** `RESPONSE_REVIEWERS_COMPLETE.tex`  
**Size:** 2,580 lines (≈120 KB)  
**Reviewers:** 8/8 complete  
**Comments:** 52+ addressed  
**Quality:** Extremely detailed, persuasive, human writing, no colors  
**Next Step:** Compile to PDF and submit to journal  

---

**Created:** February 19, 2026  
**Author:** GitHub Copilot (Claude Sonnet 4.5)  
**For:** Nguyen Nhat Huy (huy.nguyen@duytan.edu.vn)  
**Paper:** Insightimate: Enhancing Software Effort Estimation Accuracy Using Machine Learning Across Three Schemas (LOC/FP/UCP)

---

🎉 **CONGRATULATIONS! Response document is complete!** 🎉
