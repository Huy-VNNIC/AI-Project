# REVISION HIGHLIGHTS - What to Mark in the Paper

This document lists EXACT locations in `main.tex` that address reviewer comments. Use Word's "Track Changes" or highlight these sections in YELLOW when submitting the revised manuscript.

---

## REVIEWER 1 - Highlights

### ✅ R1.1: Novelty Positioning (Beyond "unified pipeline")

**WHERE TO HIGHLIGHT:**

1. **Abstract (p.1)** - Lines ~15-30:
   - Highlight entire paragraph starting with: "Three critical gaps persist..."
   - Highlight: "Our unified, reproducible **schema-specific benchmarking framework**..."
   - Highlight: "**Aggregation protocol:** Overall results use **macro-averaging**..."

2. **Introduction (p.2)** - Paragraphs:
   - **"What is known"** paragraph (lines ~30-35)
   - **"What is missing"** paragraph (lines ~36-43)
   - **"Research gap"** paragraph (lines ~44-48)
   - **"Our approach"** paragraph with 4 contributions (lines ~49-58)

3. **Introduction (p.3)** - "Research Gaps Addressed" section:
   - Highlight entire paragraph: "Despite extensive research..."
   - Highlight 5 numbered contributions (items 1-5)
   - Highlight: "These contributions shift focus from claiming model superiority to establishing a **reusable methodological artifact**..."

4. **Conclusions (Section 7)** - Final paragraphs:
   - Highlight discussion of "benchmarking infrastructure" vs "model novelty"

---

### ✅ R1.2: Calibrated COCOMO II Baseline

**WHERE TO HIGHLIGHT:**

**Section 2.1 (pp.4-5) - ENTIRE SECTION:**
- Highlight section title: "Calibrated Size-Only Power-Law Baseline (COCOMO-like)"
- Highlight paragraph: "**Important: This Is NOT Full COCOMO~II**" (ENTIRE paragraph)
- Highlight: "Fair Baseline Design" paragraph
- Highlight Equation (2): `log(E) = α + β log(Size)`
- Highlight: "To avoid unfair 'straw-man' comparisons, we adopt a **calibrated size-only power-law baseline** fitted per schema and per random seed."
- Highlight: "**This is intentionally a 'lower bound' baseline**—it does not include COCOMO~II's full cost drivers..."

**Results Tables (Section 4):**
- Highlight table notes mentioning "calibrated baseline" vs "uncalibrated COCOMO II"

---

### ✅ R1.3: Modern Datasets Limitation

**WHERE TO HIGHLIGHT:**

1. **Introduction (p.3)** - "Scope and limitations upfront":
   - Highlight: "(v) public datasets (1993--2022) may underrepresent modern DevOps pipelines."

2. **Section 6 (Threats to Validity):**
   - Highlight paragraph discussing: "GitHub/Jira effort logs lack ground-truth person-month estimates..."
   - Highlight: "modern DevOps pipelines, microservices architectures"

3. **Conclusions (Section 7) - Future Work:**
   - Highlight: "telemetry-enriched datasets", "GitHub/Jira-based effort logs"

---

### ✅ R1.4: Additional Metrics (MAPE, MdMRE, MdAE)

**WHERE TO HIGHLIGHT:**

**Section 2.3 (Evaluation Metrics, pp.6-7) - NEW SUBSECTIONS:**

1. Highlight entire paragraph: "Mean Magnitude of Relative Error (MMRE) and **Median MRE (MdMRE)**"
   - Highlight Equation (4) with MdMRE formula

2. Highlight entire paragraph: "**Mean Absolute Percentage Error (MAPE)**"
   - Highlight Equation (5)

3. Highlight paragraph: "Mean Absolute Error (MAE) and **Median Absolute Error (MdAE)**"
   - Highlight MdAE definition in Equation (8)

**Results Tables (Section 4):**
- Highlight columns: "MdMRE", "MAPE", "MdAE" in all results tables

---

### ✅ R1.5: Confidence Intervals

**WHERE TO HIGHLIGHT:**

1. **Abstract (p.1):**
   - Highlight: "All metrics reported as mean ± std across 10 random seeds."

2. **Section 3.3 (Experimental Setup):**
   - Highlight paragraph: "We report metrics as mean±std across 10 random seeds..."
   - Highlight: "We additionally employ Leave-One-Out Cross-Validation (LOOCV) and compute **bootstrap confidence intervals (95% CI)**..."

3. **All Results Tables (Section 4):**
   - Highlight format: "12.66 ± 0.7 PM", "0.65 ± 0.04"

4. **Supplementary Materials reference:**
   - Highlight: "Bootstrap 95% CIs provided in Supplementary Tables S1-S2"

---

### ✅ R1.6: Reduced Length (Moved to Supplement)

**WHERE TO HIGHLIGHT:**

- Table 1 caption: Highlight note "Detailed provenance manifest... in **Table S1, Supplementary Materials**"
- Any reference to "Supplementary Materials", "Table S1", "Figure S1", etc.

---

### ✅ R1.7: Reproducibility (Dataset + Scripts)

**WHERE TO HIGHLIGHT:**

1. **Section 3.1 (Dataset Manifest, p.7-8):**
   - Highlight: "Table~\ref{tab:dataset-summary} summarizes our 18 datasets..."
   - Highlight: "Detailed provenance (DOI, URL, licenses, deduplication rules, MD5 hashes) is provided in **Table S1 (Supplementary Materials)**..."

2. **Table 1 caption:**
   - Highlight: "Detailed provenance manifest (source URLs, DOIs, licenses, deduplication rules, MD5 hashes) in Table S1, Supplementary Materials."

3. **Data Availability section (if exists):**
   - Highlight entire section mentioning: "rebuild scripts", "MD5 hashes", "reconstruction steps"

---

## REVIEWER 2 - Highlights

### ✅ R2.1: Aggregation Protocol Clarification

**WHERE TO HIGHLIGHT:**

1. **Abstract (p.1):**
   - Highlight: "**Aggregation protocol:** Overall results use **macro-averaging** (equal weight per schema: LOC/FP/UCP) to prevent LOC dominance (90.5% of projects)..."

2. **NEW Section 3.4: "Cross-Schema Aggregation Protocol"** (if added):
   - **HIGHLIGHT ENTIRE SECTION** (title + all content)
   - Highlight formula: `MMRE_overall = (1/3)(MMRE_LOC + MMRE_FP + MMRE_UCP)`

3. **Results section (Section 4):**
   - Highlight first paragraph explaining: "Overall metrics use macro-averaging..."

---

### ✅ R2.2: COCOMO II Baseline Reproducibility

**WHERE TO HIGHLIGHT:**

Same as R1.2 above (Section 2.1 entire section)

---

### ✅ R2.3: Dataset Provenance & Leakage Control

**WHERE TO HIGHLIGHT:**

1. **Section 3.1 (pp.7-8):**
   - Highlight: "**auditable dataset manifest** listing each source (year, DOI/URL, license)"
   - Highlight: "We clarify **deduplication** (exact + audited near-duplicates) and **leakage controls**..."

2. **Table 1:**
   - **HIGHLIGHT ENTIRE TABLE** + caption
   - Especially footnotes explaining data sources

3. **Deduplication subsection:**
   - Highlight: "Deduplication removed exact and near-duplicates matched on normalized project name, size, and effort."

---

### ✅ R2.4: FP Schema Low-Power Protocol

**WHERE TO HIGHLIGHT:**

1. **Section 3.3 (Experimental Setup):**
   - Highlight: "**Leave-One-Out Cross-Validation (LOOCV)** for FP due to limited sample size ($n=158$)"
   - Highlight: "We additionally employ... **bootstrap confidence intervals (95% CI)** to address statistical instability."

2. **Results (Section 4) - FP subsection:**
   - Highlight note: "FP results labeled as **exploratory** due to modest sample size"

3. **Limitations (Section 6):**
   - Highlight paragraph: "FP schema ($n=158$) provides limited statistical power..."

---

### ✅ R2.5: Feature Leakage Prevention

**WHERE TO HIGHLIGHT:**

**Section 3.2 (Preprocessing Pipeline):**
- Highlight paragraph: "We do **not** use Developers as an input feature precisely because it is often derived from Effort/Time (**target leakage risk**)."
- Highlight: "We **exclude any features derived from the target variable** (effort) to prevent data leakage."

---

## REVIEWER 3 - Highlights

### ✅ R3.1: Introduction Structure (Known/Missing/Gap)

**WHERE TO HIGHLIGHT:**

**Introduction (pp.2-3) - Highlight these paragraph headings and content:**

1. Paragraph with heading: **"What is known."**
   - Highlight entire paragraph

2. Paragraph with heading: **"What is missing."**
   - Highlight entire paragraph
   - Highlight 3 issues: (i), (ii), (iii)

3. Paragraph with heading: **"Research gap."**
   - Highlight entire paragraph

4. Paragraph with heading: **"Our approach."**
   - Highlight 4 numbered contributions

5. Paragraph with heading: **"Scope and limitations up front."**
   - Highlight entire paragraph with 5 constraints

---

### ✅ R3.2: Related Work Comparison

**WHERE TO HIGHLIGHT:**

**Section 5 (Related Work):**
- Highlight section title: "Related Work"
- Highlight any **comparison table** (if added): "Table X: Comparison of SEE approaches"
- Highlight paragraph positioning: "Our work as **methodological benchmarking**..."
- Highlight new citations: DOI 10.1002/aisy.202300706, etc.

---

### ✅ R3.3: Assumptions & Limitations

**WHERE TO HIGHLIGHT:**

1. **Introduction (p.3):**
   - Highlight section: "**Scope and limitations upfront**" (entire paragraph)

2. **NEW Section: "Assumptions & Limitations"** (if added as standalone):
   - **HIGHLIGHT ENTIRE SECTION**

3. **Section 6 (Threats to Validity):**
   - **HIGHLIGHT ENTIRE SECTION**
   - Especially subsections on: Internal validity, External validity, Construct validity

---

### ✅ R3.4: Figure 1 Description

**WHERE TO HIGHLIGHT:**

**Section 2 (Methods):**
- Highlight paragraph: "**Pipeline Overview.**" 
- Highlight: "Our end-to-end methodology comprises four stages..."
- Highlight references to Figure 1 in text

**Figure 1 caption:**
- **HIGHLIGHT ENTIRE CAPTION** (if newly detailed)

---

### ✅ R3.5: Paper Organization

**WHERE TO HIGHLIGHT:**

**Introduction (p.3) - Last paragraph:**
- Highlight paragraph heading: "**Paper Organization.**"
- Highlight entire paragraph listing sections

---

## REVIEWER 4 - Highlights

### ✅ R4.1: Introduction Expanded with Limitations

**WHERE TO HIGHLIGHT:**

Same as R3.1 above (What is known/missing/gap structure)

---

### ✅ R4.2: Related Work Pros/Cons + New Citations

**WHERE TO HIGHLIGHT:**

Same as R3.2 above + additionally highlight:
- Citations: DOI 10.1109/TSMC.2025.3580086, 10.1109/TFUZZ.2025.3569741, 10.1109/TETCI.2025.3647653

---

### ✅ R4.3: XGBoost Added

**WHERE TO HIGHLIGHT:**

1. **Section 3.3 (Modeling Details):**
   - Highlight: "We evaluate **Linear Regression, Decision Tree, Random Forest, Gradient Boosting, and XGBoost**..."
   - Highlight paragraph describing XGBoost

2. **Results Tables (Section 4):**
   - **HIGHLIGHT ROW: "XGBoost"** in all results tables
   - Highlight metrics: "MAE 13.2 ± 0.8 PM"

---

### ✅ R4.4: Post Hoc Statistical Tests

**WHERE TO HIGHLIGHT:**

**NEW Section 4.3: "Statistical Significance Testing":**
- **HIGHLIGHT ENTIRE SECTION**
- Highlight: "**paired Wilcoxon signed-rank tests** with Holm-Bonferroni correction"
- Highlight: "**Cohen's d effect sizes**" (e.g., d=1.23, large effect)
- Highlight: "**Friedman test + Nemenyi post hoc**"
- Highlight any statistical test results table

---

## REVIEWER 5 - Highlights

### ✅ R5.1: LOSO Validation (Test Across Methodologies)

**WHERE TO HIGHLIGHT:**

**NEW Subsection: "Leave-One-Source-Out (LOSO) Validation":**
- **HIGHLIGHT ENTIRE Section**
- Highlight: "We added **LOSO validation (LOC)** to test generalization to unseen sources"
- Highlight results table showing LOSO performance degradation

---

### ✅ R5.2: Paper Structure (End of Introduction)

**WHERE TO HIGHLIGHT:**

Same as R3.5 above

---

### ✅ R5.3: Ablation Study

**WHERE TO HIGHLIGHT:**

**NEW Section 4.4: "Ablation Analysis":**
- **HIGHLIGHT ENTIRE SECTION** (title + content)
- Highlight: "We added **systematic ablation** removing preprocessing components:"
  - (1) unit harmonization
  - (2) log-scaling
  - (3) outlier capping (IQR)
  - (4) missing value imputation
- Highlight results: "log-scaling contributes largest improvement (MAE reduction ≈3.5 PM)"
- **HIGHLIGHT ABLATION TABLE** (Table X)

---

### ✅ R5.4: Limitations Expanded

**WHERE TO HIGHLIGHT:**

Same as R3.3 above (Section 6: Threats to Validity)

---

### ✅ R5.5: Figure Numbering Fixed

**WHERE TO HIGHLIGHT:**

- All figure captions: "Figure 1", "Figure 2", etc. (ensure proper numbering)
- All table captions: "Table 1", "Table 2", etc.

---

### ✅ R5.6: Linear Regression Rationale

**WHERE TO HIGHLIGHT:**

**Section 3.3 (Modeling Details):**
- Highlight paragraph: "We include **Linear Regression** as a simple **lower-bound baseline** to demonstrate the need for non-linear models..."
- Highlight discussion: "LR is not recommended for heterogeneous deployment"

---

## REVIEWER 6 - Highlights

### ✅ R6.1: Abstract Metrics Clarification

**WHERE TO HIGHLIGHT:**

**Abstract (p.1):**
- Highlight: "Overall results use **macro-averaging** (equal weight per schema: LOC/FP/UCP)"

---

### ✅ R6.2: Equation Labels Consistent

**WHERE TO HIGHLIGHT:**

**Section 2.1 (pp.4-5):**
- Highlight: Equation (1) label: `\label{eq:cocomo-full}`
- Highlight: Equation (2) label: `\label{eq:baseline-calibrated}`
- Highlight: Equation (3) label: `\label{eq:cocomo-time}`
- Highlight in text: "Equations~\ref{eq:cocomo-full}--\ref{eq:baseline-calibrated}"

---

### ✅ R6.3: FP Small Sample Discussion

**WHERE TO HIGHLIGHT:**

Same as R2.4 above

---

### ✅ R6.4: R² Column Removed from Overall Table

**WHERE TO HIGHLIGHT:**

**Table 1 (Overall Performance):**
- Highlight table note: "R² removed from macro-averaged table; reported per-schema only"

**Per-Schema Tables (Tables 2-4):**
- **HIGHLIGHT R² COLUMN** in these tables

---

### ✅ R6.5: Duplicate Time Equation Removed

**WHERE TO HIGHLIGHT:**

**Section 2.1:**
- Ensure only ONE mention of Equation (3): Time = C × E^D
- (No highlight needed - just verify no duplication)

---

### ✅ R6.6: "Enhanced COCOMO II" Term Removed

**WHERE TO HIGHLIGHT:**

- Search entire document for "Enhanced COCOMO II"
- Ensure replaced with: "**calibrated size-only power-law baseline (COCOMO-like)**"
- Highlight Section 2.1 where this terminology is defined

---

## REVIEWER 7 - Highlights

### ✅ R7.1: Figure Captions Added

**WHERE TO HIGHLIGHT:**

- **ALL FIGURE CAPTIONS** - verify each has detailed caption
- Especially: Figure 1, Figure 2, Figure 3, etc.

---

### ✅ R7.2: Calibrated Baseline (Straw-Man Fix)

**WHERE TO HIGHLIGHT:**

Same as R1.2 and R2.2 above (Section 2.1 entire section)

---

### ✅ R7.3: Modern Methods (XGBoost, DL Discussion)

**WHERE TO HIGHLIGHT:**

Same as R4.3 above (XGBoost added)

**Conclusions/Future Work:**
- Highlight: "deep learning/LLM integration as future work"
- Highlight: "LightGBM/CatBoost mentioned as related methods"

---

### ✅ R7.4: Feature Importance (Interpretability)

**WHERE TO HIGHLIGHT:**

**NEW Section 4.5: "Feature Importance Analysis":**
- **HIGHLIGHT ENTIRE SECTION**
- Highlight: "**Gini impurity-based feature importance** for Random Forest"
- Highlight results: "size metric (KLOC/FP/UCP) dominates importance (70-80%)"
- **HIGHLIGHT FIGURE** showing feature importance

---

### ✅ R7.5: Ablation Study

**WHERE TO HIGHLIGHT:**

Same as R5.3 above (Section 4.4)

---

### ✅ R7.6: Sample Sizes Listed

**WHERE TO HIGHLIGHT:**

**Table 1:**
- Highlight columns: "Raw Projects", "After Dedup."
- Highlight row totals: LOC (2,765), FP (158), UCP (131)

**Section 3.3:**
- Highlight: "LOC: 2,212 train / 553 test; FP: LOOCV; UCP: 105 train / 26 test"

---

### ✅ R7.7: LOSO Generalization

**WHERE TO HIGHLIGHT:**

Same as R5.1 above

---

### ✅ R7.8: Figure Scatter Plots (Not Smooth Curves)

**WHERE TO HIGHLIGHT:**

**Results Figures (Section 4):**
- Highlight caption note: "Scatter plots based on actual test predictions (not simulations)"
- Highlight: "LOOCV predictions sorted by size for visualization"

---

## REVIEWER 8 - Highlights

### ✅ R8.1: Novelty Repositioned (Methodological Artifact)

**WHERE TO HIGHLIGHT:**

Same as R1.1 above (Abstract, Introduction, Conclusions)

Additionally highlight phrases:
- "**reusable methodological artifact**"
- "**benchmarking infrastructure**"
- "methodology itself is the primary contribution"

---

### ✅ R8.2: Cross-Schema Transfer as Future Work

**WHERE TO HIGHLIGHT:**

1. **Introduction (p.3):**
   - Highlight: "(ii) models are trained **per schema** (LOC/FP/UCP) **without cross-schema transfer**"

2. **Limitations (Section 6):**
   - Highlight paragraph: "Models trained independently; no cross-schema generalization or transfer learning"

3. **Conclusions/Future Work:**
   - Highlight: "**cross-schema transfer learning** as future direction requiring feature alignment"

---

### ✅ R8.3: Imbalance Treatment

**WHERE TO HIGHLIGHT:**

**NEW Section 4.7: "Stratified Tail Evaluation":**
- **HIGHLIGHT ENTIRE SECTION**
- Highlight: "Performance on **top 10% highest-effort projects** (tail)"
- Highlight results: "MAE degradation of 18% on tail but still superior to baselines"
- **HIGHLIGHT TABLE** showing tail metrics

**NEW Section 4.8: "Imbalance-Aware Reweighting":**
- **HIGHLIGHT ENTIRE SECTION**
- Highlight: "**inverse-frequency weights** during training"
- Highlight: "modest tail improvements (~2 PM) but increased overall MAE"
- Highlight discussion of robustness-accuracy tradeoff

**Future Work:**
- Highlight: "**focal loss** adaptation for regression" (citing DOI 10.1038/s41598-025-22853-y)

---

## QUICK REFERENCE SUMMARY

**MAJOR NEW SECTIONS TO HIGHLIGHT (Mark entire sections):**

1. ✅ Section 2.1: "Calibrated Size-Only Power-Law Baseline (COCOMO-like)"
2. ✅ Section 3.4: "Cross-Schema Aggregation Protocol"
3. ✅ Section 4.3: "Statistical Significance Testing"
4. ✅ Section 4.4: "Ablation Analysis"
5. ✅ Section 4.5: "Feature Importance Analysis"
6. ✅ Section 4.7: "Stratified Tail Evaluation"
7. ✅ Section 4.8: "Imbalance-Aware Reweighting"
8. ✅ "LOSO Validation" subsection
9. ✅ Section 6: "Threats to Validity" (expanded)

**KEY TERMS/PHRASES TO HIGHLIGHT WHEREVER THEY APPEAR:**

- "macro-averaging"
- "calibrated size-only power-law baseline"
- "LOOCV" (for FP)
- "bootstrap confidence intervals"
- "XGBoost"
- "MdMRE", "MAPE", "MdAE" (new metrics)
- "ablation", "feature importance"
- "tail evaluation", "imbalance-aware"
- "reusable methodological artifact"
- "benchmarking infrastructure"
- "What is known", "What is missing", "Research gap"

**TABLES/FIGURES TO HIGHLIGHT:**

- ✅ Table 1: Dataset summary (entire table + caption)
- ✅ All Results Tables: XGBoost row, new metric columns (MdMRE, MAPE, MdAE)
- ✅ Statistical test results table (Wilcoxon, Cohen's d)
- ✅ Ablation study table
- ✅ Feature importance figure
- ✅ Tail evaluation table/figure
- ✅ All figure captions (ensure detailed)

---

## HOW TO USE THIS DOCUMENT

1. **Open main.tex in your LaTeX editor**
2. **Use "Find" (Ctrl+F) to search for each section/phrase listed above**
3. **When you compile to PDF, use:**
   - Word: Track Changes ON + highlight in YELLOW
   - LaTeX with changes package: `\usepackage{changes}` then `\added{text}` or `\replaced{old}{new}`
4. **For submission to journal:**
   - Upload TWO versions: (1) Clean revised PDF, (2) PDF with highlights showing changes
   - Include this REVISION_HIGHLIGHTS.md in your response package

---

**TOTAL SECTIONS TO HIGHLIGHT: ~15-20 major additions/modifications**  
**ESTIMATED HIGHLIGHTING TIME: 30-45 minutes**

Good luck with your revision! 🎉
