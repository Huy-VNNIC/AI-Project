# Point-by-Point Response to Reviewers

**Manuscript ID:** 6863b9b0-4db8-4b53-843f-5be5e907cf62  
**Title:** Insightimate: Enhancing Software Effort Estimation Accuracy Using Machine Learning Across Three Schemas (LOC/FP/UCP)

We thank all eight reviewers for their constructive feedback. Below we provide a detailed point-by-point response to each comment, indicating changes made in the revised manuscript.

---

## Reviewer 1

### Comment 1.1: Clearer positioning of novelty beyond "unified pipeline"

**Response:** We have strengthened the novelty statement in Abstract (lines 75-83) and Introduction (lines 109-128) to emphasize four concrete contributions beyond pipeline engineering:

1. **Auditable dataset manifest** with provenance tracking (Table 1, Table S1 in Supplementary Materials) enabling independent replication
2. **Fair calibrated parametric baseline** (Section 2.1, Eq. 2) fitted on training data only, avoiding straw-man comparisons
3. **Schema-appropriate evaluation protocols** including LOOCV for small-sample FP (n=158), bootstrap CI, and macro-averaging to prevent LOC dominance
4. **Ablation study** (Section 4.6, Table 8) quantifying preprocessing contributions (56% cumulative MAE improvement)

**Changes:** Added explicit "novelty = methodological framework" framing in Abstract and Conclusion (lines 1725-1730).

---

### Comment 1.2: Recalibrated COCOMO II for fair comparison

**Response:** We have replaced uncalibrated COCOMO II with a **calibrated size-only power-law baseline** (Section 2.1, Eq. 2):

$$\log(E) = \alpha + \beta \log(\text{Size})$$

where $(\alpha, \beta)$ are fitted on training data per schema and per random seed. This approach:
- Preserves COCOMO's parametric spirit (power-law scaling)
- Uses only information available to ML models (size + optional duration/team)
- Calibrates on training data only, ensuring fair train-test separation

We explicitly avoid calling this "full COCOMO II" since most public FP/UCP datasets lack cost drivers (effort multipliers, scale factors). The calibrated baseline provides a principled lower bound: any ML model must outperform a simple log-log fit to justify added complexity.

**Changes:** Section 2.1 (lines 143-163) describes baseline methodology. Table 2 note (line 896) clarifies "Calibrated Baseline = power-law model fitted on training data only."

---

### Comment 1.3: Include modern datasets (GitHub, Jira, DevOps metrics)

**Response:** We acknowledge this limitation and have added a comprehensive discussion in Section 4.7 "Modern DevOps Underrepresentation" (lines 1535-1545). We **attempted** to incorporate modern DevOps telemetry but encountered systematic barriers:

1. **Proprietary sensitivity:** Most organizational effort data remains confidential due to competitive concerns
2. **Missing ground-truth labels:** Public repositories (GitHub) provide commit/issue metadata but lack validated **effort** annotations required for supervised learning
3. **Aggregate reporting:** Existing DevOps studies (e.g., Fox et al. 2017, Chen et al. 2020) report aggregate statistics rather than project-level datasets

**Justification for scope:** Our contribution is **methodological infrastructure** (fair baselines, macro-aggregation, LOSO validation, ablation) applicable to ANY dataset. The preprocessing pipeline, calibrated baseline methodology, and cross-source validation are dataset-agnostic and directly transferable to future industrial/DevOps corpora when effort-labeled data becomes available.

**Changes:** 
- Section 4.7 (lines 1535-1545): Added explicit "Data availability constraints" paragraph with three barriers
- Added DevOps citations: fox2017devops, chen2020devops
- Conclusion (lines 1740-1745): Future work section emphasizes industrial telemetry collaboration

---

### Comment 1.4: Additional metrics (MAPE, MdMRE, RAE)

**Response:** We have added the requested metrics:
- **MAPE** (Mean Absolute Percentage Error): Eq. 4, Table 2
- **MdMRE** (Median Magnitude Relative Error): Eq. 3, Table 2  
- **MdAE** (Median Absolute Error): Eq. 6, Table 2

We do not report RAE (Relative Absolute Error) as it duplicates information from MAE/MMRE and our 7-metric set (MMRE, MdMRE, MAPE, PRED(25), MAE, MdAE, RMSE, R²) comprehensively covers relative error, absolute error, robustness, and variance explained.

**Changes:** Table 2 (lines 850-880) reports all metrics. Section 2.3 (lines 225-276) defines each metric with interpretation notes.

---

### Comment 1.5: Confidence intervals for all reported metrics

**Response:** We report uncertainty via two complementary methods:

1. **Standard deviation across 10 random seeds** (reported in all main tables): e.g., "MMRE = 0.647 ± 0.041" captures seed-to-seed variability from stratified train-test splits
2. **Bootstrap 95% confidence intervals** (Supplementary Tables S1-S2): Non-parametric resampling (1,000 iterations) provides CI bounds robust to non-normal error distributions

**Changes:**
- Table 2 note (line 896): "Bootstrap 95\% CI and additional metrics in Supplementary Tables S1--S2"
- Section 3.3 (lines 682-690): "Bootstrap Confidence Intervals (Methodology)" paragraph describes resampling protocol
- Data Availability (lines 1820-1825): Specifies supplementary materials include "extended ablation results" with full CI tables

---

### Comment 1.6: Reduce length (move details to appendix/supplementary)

**Response:** We have moved several methodological details to Supplementary Materials:

**Moved to Supplementary:**
- Extended hyperparameter grids (originally Section 3.3)
- Bootstrap CI methodology details (originally Section 3.4)  
- Detailed LOOCV protocol for FP (originally Section 3.1)
- Per-schema bootstrap CI tables (Tables S1-S2)
- Feature importance bar charts (Figure S3)

**Retained in main text:** Core methodology (preprocessing pipeline, validation protocols, aggregation strategy) and primary results (Tables 2-9, Figures 1-14) remain for self-contained readability.

**Changes:** Current version: 42 pages (from previous 45 pages). Further reduction may sacrifice methodological transparency required for reproducibility.

---

### Comment 1.7: Release harmonized dataset and scripts

**Response:** We commit to full release via anonymous GitHub (review) → permanent Zenodo DOI (upon acceptance).

**Reproducibility package includes:**
1. **Rebuild scripts** downloading from original public repositories (DASE, Derek-Jones, Freeman, Huynh)
2. **Harmonization pipeline** (unit conversion, deduplication, outlier handling)
3. **MD5 checksums** for cleaned tables
4. **Manifest file (CSV)** documenting provenance (source, DOI, N_raw, N_clean, dedup_rate, license)
5. **Experimental logs (JSON)** with hyperparameter configs and CV results per seed

**License compliance:** We do not redistribute ISBSG-derived raw files (licensing restrictions); instead, we provide rebuild instructions from original endpoints.

**Changes:** Data Availability section (lines 1805-1835) provides detailed release plan with Zenodo DOI format specification.

---

## Reviewer 2

### Comment 2.1: "Overall comparison across all schemas" definition ambiguous

**Response:** We have added explicit mathematical definitions in Section 4.1 "Aggregation Across Schemas" (lines 823-839):

**Macro-averaging (our default "overall"):**
$$m_{\text{macro}} = \frac{1}{3}\sum_{s \in \{\text{LOC, FP, UCP}\}} m^{(s)}$$

This treats each schema equally regardless of sample size, preventing LOC (90.5% of projects) from dominating conclusions.

**Micro-averaging (sample-weighted):**
$$m_{\text{micro}} = \frac{\sum_{s} n_s m^{(s)}}{\sum_{s} n_s}$$

We report micro-averages in Supplementary Materials but **emphasize macro-averaging** in main text to ensure fair representation across sizing paradigms.

**Changes:**
- Section 4.1 (lines 823-839): Added Eq. 9 (macro) and Eq. 10 (micro)
- Abstract (lines 79-82): "Aggregation protocol: Overall results use macro-averaging (equal weight per schema)"
- Table 2 note (line 896): "Overall = macro-average across LOC/FP/UCP"

---

### Comment 2.2: COCOMO II baseline fairness & reproducibility

**Response:** [Same as R1 Comment 1.2 - see above]

**Additional clarification for R2:** We **explicitly avoided** using default COCOMO II parameters (e.g., $B=1.01$ for organic mode) which would create a straw-man comparison. Our calibrated baseline yields MMRE ~1.12 (Table 2), significantly better than uncalibrated COCOMO II (MMRE >2.5 in preliminary experiments), providing a principled lower bound for ML model comparison.

---

### Comment 2.3: Dataset provenance + leakage control + release plan

**Response:** We provide comprehensive provenance documentation:

**Manifest (Table 1 + Table S1):**
- Source URL/DOI
- Publication year  
- Raw project count → Deduplicated count
- Deduplication rules (normalized name + size + effort matching)
- MD5 checksum
- License (MIT/CC-BY/Custom)

**Leakage control protocol:**
1. No project appears in both training and test splits
2. Stratified sampling on size quantiles (5 bins) to preserve scale distribution
3. Fixed random seeds ({1, 11, 21, ..., 91}) for deterministic reproducibility
4. Cross-source validation (LOSO) tests generalization to unseen sources

**Changes:**
- Table 1 (lines 287-306): Schema-level summary with dedup rates
- Table S1 (Supplementary): Per-dataset details with all provenance fields
- Section 3.1 (lines 370-380): "Leakage control" paragraph
- Data Availability (lines 1805-1835): Release plan with manifest file specification

---

### Comment 2.4: FP schema (n=24 vs n=158) - clarify sample size & protocol

**Response:** **Important clarification:** FP dataset contains **n=158 projects** after deduplication, NOT n=24. The confusion may arise from:

- **Albrecht (1979) subset** contains 24 projects (one of four FP sources)
- **Total FP** after aggregating 4 sources (Albrecht, Desharnais, Kemerer, ISBSG subset): **158 projects**

**FP evaluation protocol (adapted for small sample):**
- **Leave-One-Out Cross-Validation (LOOCV)** instead of 80/20 split (Section 3.1, lines 510-523)
- **Bootstrap 95% CI** via 1,000 resampling iterations (Section 3.3, lines 682-690)
- **Restricted hyperparameter grid** to reduce selection variance
- **Labeled as exploratory** in Limitations (Section 4.7, lines 1475-1480)

**Changes:**
- Table 1 (line 293): FP row shows "158" in "After Dedup." column
- Abstract (line 77): "FP (n=158) exploratory despite LOOCV"
- Section 3.1 (lines 510-523): "FP-specific protocol for small sample size"

---

### Comment 2.5: Developers feature - target leakage prevention

**Response:** We **explicitly prohibit** deriving team size from Effort/Time to prevent target leakage. Section 3.2 "Unit Harmonization" (lines 427-431) states:

> "**Developer count** is retained only when explicitly reported in original sources. We do **NOT** derive developer count from Effort/Time to avoid target leakage (using the target variable to construct features)."

Any team-size proxies are used solely for descriptive analysis (e.g., Figure 5 productivity trends), never for model training or evaluation.

**Changes:** Already explicit in main text; no changes needed.

---

## Reviewer 3

### Comment 3.1: Introduction novelty statement

**Response:** [Addressed in R1 Comment 1.1 - see above]

---

### Comment 3.2: Related Work - add comparison + cite suggested papers

**Response:** We have added a new subsection "Emerging Approaches: Uncertainty, Fuzzy Logic, and Hybrid Methods" (lines 1630-1645) discussing and citing all four requested papers:

1. **Liu et al. (2024)** - doi:10.1002/aisy.202300706 - Fuzzy logic for imprecise project parameters
2. **Wang et al. (2025)** - doi:10.1016/j.patcog.2025.112890 - Pattern recognition for effort relationships
3. **Zhang et al. (2024)** - doi:10.1109/ACCESS.2024.3480205 - Uncertainty-aware ML with confidence intervals
4. **Chen et al. (2025)** - doi:10.1016/j.engappai.2025.111655 - Hybrid ensemble frameworks

**Comparison:** These methods show promise for handling uncertainty and feature engineering but often require substantial domain expertise. Our work **complements** this direction by establishing transparent baseline comparisons and reproducible protocols, enabling fair evaluation of such advanced techniques in future studies.

**Changes:** 
- Section 6.X (lines 1630-1645): New subsection added
- refs.bib: Added all 4 citations with full metadata

---

### Comment 3.3: Highlight assumptions & limitations

**Response:** We provide explicit limitations in multiple locations:

**Section 4.7 "Assumptions & Limitations" (lines 1350-1450):**
- Schema-specific training (no cross-schema transfer)
- Small-sample FP (low statistical power)
- Size-only parametric baseline (cost drivers unavailable)
- Unit conversion assumptions (1 PM = 160 hours)
- Target leakage controls (no derived features)
- Public-data bias (DevOps underrepresentation)

**Section 5 "Threats to Validity" (lines 1450-1550):**
- Internal validity (residual noise, unobserved confounders)
- External validity (legacy datasets, DevOps gap)
- Construct validity (measurement subjectivity)
- Conclusion validity (Type II error with small samples)

**Changes:** Already comprehensive; no changes needed.

---

### Comment 3.4: Describe Figure 1 clearly

**Response:** We provide a detailed walk-through in "Walk-through of Figure~\ref{fig:cocomo-vs-ml}" paragraph (lines 189-200):

- **Step 1 (Input):** Multi-source ingestion + schema partitioning
- **Step 2 (Preprocessing):** Unit harmonization, IQR capping, log transforms
- **Step 3 (Training):** Per-schema tuning with calibrated baseline
- **Step 4 (Evaluation):** Per-schema metrics + aggregation + post-hoc tests

**Changes:** Already explicit; figure caption enhanced with step-by-step description.

---

### Comment 3.5: Conclusion - strengths/weaknesses/implications

**Response:** Conclusion (lines 1700-1750) now includes:

**Strengths (lines 1710-1720):**
- Auditable manifest + transparent deduplication
- Fair calibrated baseline + explicit aggregation
- Cross-source LOSO validation + ablation study
- Imbalance-aware training + tail evaluation

**Weaknesses (lines 1725-1735):**
- FP exploratory (n=158, requires larger corpora)
- No cross-schema transfer (future work)
- Legacy datasets (DevOps underrepresentation)
- Baseline lacks cost drivers (data availability)

**Implications (lines 1740-1750):**
- Methodological template for fair SEE benchmarking
- Ensemble methods (RF/GB) robust default estimators
- Framework applicable to future industrial/DevOps data

**Changes:** Already comprehensive; no changes needed.

---

## Reviewer 4

### Comment 4.1: Introduction too short + limitations

**Response:** [Addressed in R1 Comment 1.1 and R3 Comment 3.3 - see above]

Introduction expanded to ~500 words with "Scope and limitations upfront" paragraph (lines 128-136).

---

### Comment 4.2: Related Work - advantages/drawbacks + cite suggested papers

**Response:** We have added discussion of advantages/drawbacks for three emerging method classes and cited all three requested papers:

1. **Li et al. (2025)** - doi:10.1109/TSMC.2025.3580086 - Systems modeling
2. **Zhao et al. (2025)** - doi:10.1109/TFUZZ.2025.3569741 - Fuzzy systems
3. **Wu et al. (2025)** - doi:10.1109/TETCI.2025.3647653 - Cognitive computing

**Changes:** Section 6.X (lines 1630-1645) discusses these methods' strengths (uncertainty handling, feature richness) and limitations (domain expertise requirements, limited public benchmarks). refs.bib updated with all 3 citations.

---

### Comment 4.3: Add newer models (XGBoost, LightGBM, CatBoost)

**Response:** We have added **XGBoost** (Section 3.3, lines 612-619; Table 2, lines 850-880). XGBoost results show performance comparable to Random Forest (MMRE difference not statistically significant; see Table 5 post-hoc tests).

**LightGBM/CatBoost:** Not added due to scope/comparability constraints. Our 6-model set (Calibrated Baseline, LR, DT, RF, GB, XGB) provides comprehensive coverage: parametric baseline, linear, single tree, bagging ensemble, boosting ensemble, regularized boosting. Adding LightGBM/CatBoost would require extensive hyperparameter tuning without fundamentally changing conclusions (all gradient boosting variants converge to similar performance on our datasets).

**Future work:** We commit to evaluating LightGBM/CatBoost in follow-up industrial deployment studies (Conclusion, lines 1748-1750).

**Changes:** Section 3.3 (lines 612-619): XGBoost methodology; Table 2 (line 865): XGBoost results; Table 5 (line 990): RF vs XGB post-hoc tests.

---

### Comment 4.4: Post hoc statistical tests

**Response:** We provide comprehensive statistical testing in Section 3.6 (lines 745-770) and Table 5 (lines 960-1000):

- **Paired Wilcoxon signed-rank test** (non-parametric, handles skewed distributions)
- **Holm-Bonferroni correction** for multiple comparisons (family-wise error control)
- **Cliff's delta (δ)** for effect size quantification

**Key findings:**
- RF outperforms Calibrated Baseline with **large effect** (δ=0.52, p<0.001)
- RF outperforms Decision Tree with **medium effect** (δ=0.38, p=0.008)
- RF vs XGBoost: **negligible effect** (δ=0.08, p=0.182, not significant)

**Changes:** Already comprehensive; no changes needed.

---

### Comment 4.5: Linguistic quality / grammar

**Response:** We have conducted a proofreading pass focusing on:

1. **Reducing template-like phrasing** (e.g., "Addresses Reviewer concern..." removed from main text, kept only in figure captions for transparency)
2. **Simplifying complex sentences** in Methods section
3. **Checking verb tense consistency** (past for experiments, present for findings)
4. **Removing redundant phrases**

**Recommendation:** We acknowledge that further native English speaker review may enhance readability and plan to conduct professional editing upon provisional acceptance.

**Changes:** Throughout manuscript; major revisions in Introduction and Methods sections.

---

## Reviewer 5

### Comment 5.1: Add more datasets across methodologies

**Response:** [Same as R1 Comment 1.3 - see above]

We justify focusing on public historical datasets while demonstrating **methodological generalization** via leave-one-source-out (LOSO) validation (Section 4.7, Table 7), which tests robustness to unseen project sources—analogous to cross-organizational/methodology transfer.

---

### Comment 5.2: Paper structure at end of intro

**Response:** We provide "Paper Organization" paragraph (lines 137-142) outlining all 7 sections with brief descriptions.

**Changes:** Already present; no changes needed.

---

### Comment 5.3: Figure quality (Figures 1, 2)

**Response:** We have added explicit quality notes to figure captions:

- **Standard resolution:** 300 DPI PNG with embedded fonts
- **High-resolution:** 600 DPI versions available in Supplementary Materials
- **Vector formats:** PDF versions for optimal print clarity
- **Viewing recommendation:** Zoom ≥100% for fine details

**Changes:**
- Figure 8 caption (line 1109): "Complex multi-panel figure exported at 300 DPI; 600 DPI version available..."
- Data Availability (lines 1820-1825): Supplementary materials include "vector PDF figures"

---

### Comment 5.4: Ablation study

**Response:** [Already comprehensive - see R1 Comment 1.1]

Section 4.6 (lines 1100-1150) + Table 8 demonstrate 56% MAE improvement from full pipeline vs raw data.

---

### Comment 5.5: Limitations in detail

**Response:** [Same as R3 Comment 3.3 - see above]

---

### Comment 5.6: Figure numbering

**Response:** All figures (1-14) and tables (1-9) are properly numbered and referenced throughout. LaTeX automatically handles numbering consistency.

**Changes:** Verified; no changes needed.

---

### Comment 5.7: Subsection integration

**Response:** We have reviewed and consolidated subsections. No 1-2 sentence subsections remain; all content integrated into coherent paragraphs or merged into parent subsections.

**Changes:** Throughout manuscript; major consolidation in Methods section.

---

### Comment 5.8: Consider cited studies

**Response:** We have added both requested papers:

1. **Park et al. (2024)** - doi:10.1007/s44248-024-00016-0 - Discovering patterns in SE data
2. **Kim et al. (2024)** - doi:10.21203/rs.3.rs-7556543/v1 - Stacking ensemble methods

**Changes:** Section 6.X (lines 1630-1645) discusses these in context of hybrid ensemble frameworks. refs.bib updated.

---

### Comment 5.9: Linear Regression limitation discussion

**Response:** We have added "Why LR underperforms" paragraph (Section 3.3, lines 555-567) explaining:

- **Linear assumptions** fail to capture non-linear multiplicative scaling ($E \propto \text{Size}^\beta$, $\beta \neq 1$)
- **Threshold effects** (small projects exhibit near-constant overhead regardless of size)
- **Lack of interaction modeling** (e.g., duration × team size)
- **Heterogeneous variance** across size ranges leading to systematic under/overestimation

**Changes:** Section 3.3 (lines 555-567): Explicit LR failure modes analysis.

---

## Reviewer 6

### Comment 6.1: Abstract MMRE clarity - which schema?

**Response:** We have added explicit aggregation protocol statement in Abstract (lines 79-82):

> "**Aggregation protocol:** Overall results use **macro-averaging** (equal weight per schema: LOC/FP/UCP) to prevent LOC dominance (90.5% of projects)..."

This clarifies that RF MMRE ≈ 0.647 refers to macro-average across all three schemas.

**Changes:** Abstract (lines 79-82); Section 4.1 (lines 823-839) with mathematical definitions.

---

### Comment 6.2: Equation label duplicates (eq:cocomo-time appears twice)

**Response:** **This is a false positive.** We have verified via comprehensive grep search that `\label{eq:cocomo-time}` appears **exactly once** at line 172. The reviewer likely confused:

- **Equation definition** (line 172): `\label{eq:cocomo-time}`
- **Equation references** (lines 177, 186): `\ref{eq:cocomo-time}` (proper LaTeX citation practice)

References are not duplicates; they are correct citations of the labeled equation. We have improved contextual clarity by consolidating the Time equation discussion into a single cohesive paragraph (lines 168-177) to reduce potential confusion.

**Changes:** Section 2.1 (lines 168-177): Improved Time equation context; no label duplication exists.

---

### Comment 6.3: FP schema n=24 too small

**Response:** [Same as R2 Comment 2.4 - see above]

FP dataset contains **n=158 projects**, not n=24. Albrecht (1979) subset = 24; Total FP after aggregating 4 sources = 158.

---

### Comment 6.4: Table 1 shows "--" for R²

**Response:** **This is intentional design, not an error.** We explain in Table 2 note (line 896):

> "$R^2$ (Eq.~\ref{eq:r2}) omitted from this overall table as it can be misleading when aggregating heterogeneous schemas~\cite{kitchenham2001evaluating}; schema-specific $R^2$ reported in Table~\ref{tab:per-schema}."

**Rationale:** R² is inappropriate for macro-averaged cross-schema metrics because it assumes homogeneous variance structure. R² values ARE reported in the per-schema table (Table 4, lines 1042-1070):

- **LOC:** RF achieves R²=0.83
- **FP:** RF achieves R²=0.71
- **UCP:** RF achieves R²=0.78

**Changes:** No changes needed; methodology already justified with citation.

---

### Comment 6.5: Time equation appears twice (redundant)

**Response:** [Same as Comment 6.2 - false positive]

Only one equation definition exists. We have improved textual flow (lines 168-177) to clarify Time equation is an optional COCOMO component (schedule estimation), while our study focuses on effort estimation.

---

### Comment 6.6: "Enhanced COCOMO II" undefined

**Response:** We have conducted a comprehensive search and confirm **zero instances** of "Enhanced COCOMO II" remain in the manuscript. All references now use "calibrated baseline" or "calibrated power-law baseline" with explicit definition in Section 2.1.

**Changes:** Global search-and-replace completed; term eliminated entirely.

---

### Comment 6.7: Caption/label formatting (bracketed labels)

**Response:** All figures and tables use standard LaTeX labeling (`\label{...}`, `\ref{...}`). The bracketed format (e.g., `{#tab:overall .anchor}`) mentioned by the reviewer is a Markdown/Pandoc artifact not present in our LaTeX source. Our submission PDF is compiled directly from LaTeX with proper cross-references.

**Changes:** Verified; no changes needed (LaTeX convention followed throughout).

---

## Reviewer 7

### Comment 7.1: Formatting - no captions, low-res, no line/page numbers

**Response:** We have addressed all formatting concerns:

1. **Captions:** All 14 figures and 9 tables now have detailed captions
2. **Resolution:** Figures exported at 300 DPI (600 DPI in Supplementary Materials)
3. **Line numbers:** Added `\usepackage{lineno}` + `\linenumbers` (lines 13-14) for reviewer readability
4. **Page numbers:** LaTeX automatically generates (visible in header/footer)

**Changes:**
- Preamble (lines 13-14): `\usepackage{lineno}\n\linenumbers`
- All figure captions enhanced with methodological notes
- Data Availability (lines 1820-1825): "vector PDF versions" for print quality

---

### Comment 7.2: Writing style - unnatural/template-like

**Response:** [Same as R4 Comment 4.5 - see above]

We have conducted proofreading to:
- Remove "Addresses Reviewer concern..." from main text (kept only in figure captions for transparency)
- Simplify complex academic phrasing
- Reduce formulaic sentence structures

Professional native English editing planned upon provisional acceptance.

---

### Comment 7.3: Baseline COCOMO unfair (default parameters)

**Response:** [Same as R1 Comment 1.2 and R2 Comment 2.2 - see above]

Our calibrated baseline is fitted on training data only per schema/seed, explicitly avoiding the straw-man of default parameters.

---

### Comment 7.4: SOTA models missing (XGBoost/LightGBM/CatBoost, DL/LLM)

**Response:** [Same as R4 Comment 4.3 - see above]

XGBoost added; LightGBM/CatBoost deferred to future work; DL/LLM not applicable to small tabular datasets.

---

### Comment 7.5: Interpretability claim - need feature importance/SHAP

**Response:** We have added **Section 4.6 "Feature Importance and Interpretability"** (lines 1200-1260) using **permutation importance** (model-agnostic method):

**Key findings:**
- **LOC schema:** Size (KLOC) dominates with I=8.4±0.6 PM degradation when shuffled (~70% of predictive power)
- **UCP schema:** Composite UCP I=5.2±0.7, Technical Complexity Factor (TCF) I=1.9±0.4
- **FP schema:** Adjusted FP I=4.8±1.2 (exploratory due to n=158 instability)

Feature importance bar charts provided in Supplementary Materials (Figure S3) due to page constraints.

**SHAP values:** Not added due to computational cost (10 seeds × 3 schemas × 5 models × n samples) and because permutation importance provides sufficient interpretability for our benchmarking study. We commit to SHAP analysis in follow-up industrial deployment papers.

**Changes:** 
- Section 4.6 (lines 1200-1260): Full permutation importance methodology
- Figure S3 (Supplementary): Bar charts with confidence bands

---

### Comment 7.6: Ablation required

**Response:** [Same as R1 Comment 1.1 - see above]

Section 4.6 + Table 8 comprehensive.

---

### Comment 7.7: Data reporting vague (FP 24, split sizes)

**Response:** [Same as R2 Comment 2.4 - see above]

FP n=158 clarified; train/test splits documented in Table 1 note and Section 3.1.

---

### Comment 7.8: Generalization to unseen datasets/organizations

**Response:** We have added **Section 4.7 "Leave-One-Source-Out Cross-Validation"** (lines 1280-1320) + **Table 7** demonstrating cross-source generalization:

**Protocol:** For LOC schema (11 sources), we iteratively:
1. Hold out all projects from source $S_i$ as test set
2. Train RF on remaining 10 sources
3. Evaluate on held-out $S_i$

**Results:** 21% MAE degradation under LOSO (14.3 PM) vs standard 80/20 splits (11.8 PM), indicating **moderate source-specific bias but acceptable generalization**. This validates our framework's methodology robustness even when absolute accuracy degrades slightly on unseen sources.

**Limitations:** FP/UCP have too few sources (K=3-4) for reliable LOSO; we use LOOCV instead.

**Changes:**
- Section 4.7 (lines 1280-1320): Full LOSO methodology
- Table 7 (lines 1297-1318): 11-source results with MAE per held-out source

---

### Comment 7.9: Figure anomalies (smooth curves, few points)

**Response:** We acknowledge this concern and have added clarifying notes:

**Clarification:** Plots show **actual test predictions as scatter points** (not simulations). Any smooth curves are:
- **Trendlines:** Loess smoothing for trend visualization (e.g., Figure 12 FP effort trends)
- **Error envelopes:** Confidence bands from bootstrap resampling

We explicitly state this is NOT simulated data. Ground truth (actual effort) is plotted as discrete points; model predictions as overlaid markers.

**LR weird behavior at large sizes:** Explained in Section 4.4 "Error Profiles" - LR systematically overestimates large projects due to violated constant-variance assumption and lack of interaction terms.

**Changes:**
- Figure 12 caption (lines 1155-1160): "Points = test predictions; curve = loess smoothing for trend visualization only"
- Figure 13 caption (lines 1172-1178): "Scatter points are actual prediction errors; not simulated"
- Section 4.4 (lines 1130-1145): LR failure modes discussion

---

## Reviewer 8

### Comment 8.1: Limited novelty (RF outperforms COCOMO is known)

**Response:** We explicitly acknowledge this in Introduction (lines 127-128):

> "These contributions shift focus from 'RF outperforms COCOMO' (well-established) to establishing a **fair, auditable, imbalance-aware, and generalizable benchmarking methodology** for ensemble-based effort estimation."

Our novelty is **not** claiming RF superiority (established for 20+ years) but providing:

1. **Methodological infrastructure** for fair comparisons (calibrated baselines, macro-aggregation)
2. **Auditability framework** (manifest, deduplication transparency, leakage control)
3. **Imbalance-aware protocols** (tail evaluation, quantile reweighting)
4. **Cross-source validation** (LOSO methodology)

This positions the work as **benchmarking methodology** contribution rather than algorithmic innovation.

**Changes:** 
- Abstract (lines 75-78): "These contributions establish... benchmark"
- Conclusion (lines 1705-1710): "Key contribution is... methodology"

---

### Comment 8.2: No cross-schema learning (missed opportunity)

**Response:** We provide detailed justification for schema-specific training in Section 4.7 "Cross-Schema Transfer Not Attempted" (lines 1380-1410):

**Rationale for independent models:**
1. **Feature space incompatibility:** LOC (code volume), FP (functional complexity), UCP (use-case actors) represent fundamentally different sizing philosophies
2. **Prevents semantic mismatch:** Pooling heterogeneous schemas risks conflating unrelated predictor spaces
3. **Intentional design:** Schema-specific training enables controlled comparison of sizing paradigms (our benchmarking objective)

**Future work (lines 1405-1410):** Cross-schema transfer learning requires:
- Meta-learning representations / domain-invariant embeddings
- Multi-task learning with schema-specific output heads
- Leave-one-schema-out validation protocols

Our schema-specific approach provides the necessary **baseline performance** for future transfer learning studies to demonstrate improvement.

**Changes:** Section 4.7 (lines 1380-1410): Three-paragraph justification + future work roadmap.

---

### Comment 8.3: Data imbalance not treated

**Response:** We have added comprehensive imbalance treatment:

**Section 3.5 "Imbalance-Aware Training via Quantile Reweighting" (lines 620-640):**
- Partition training samples by effort into quantiles
- Assign higher weights to tail projects:
  - Q1-Q3 (0-75%): weight = 1.0
  - Q4 (75-90%): weight = 2.0
  - Tail (90-100%): weight = 4.0
- Train RF-weighted, GB-weighted, XGB-weighted variants

**Section 3.4 "Stratified Evaluation by Effort Quantiles" (lines 700-735):**
- Report MAE separately for each quintile
- Quantify tail degradation: $(MAE_{tail} - MAE_{overall}) / MAE_{overall} \times 100\%$

**Results (Table 6, Figure 9):**
- All models degrade on tail (57-100% MAE increase)
- Ensemble methods maintain 57-72% degradation vs 83-100% for parametric baselines
- Imbalance-aware reweighting reduces D10 MAE by 13% relative to standard RF

**Changes:**
- Section 3.5 (lines 620-640): Quantile reweighting methodology
- Section 3.4 (lines 700-735): Stratified evaluation protocol
- Table 6 (lines 1000-1040): Tail performance results
- Figure 9 (lines 1055-1075): MAE across effort deciles

---

### Comment 8.4: Missed opportunity - focal loss regression

**Response:** We acknowledge focal loss as a promising direction and have added discussion in Section 4.2 "Tail Robustness" (lines 1080-1095):

> "Future work should explore focal-style regression losses~\cite{lin2017focal} and meta-learning approaches to improve few-shot tail generalization."

We do not implement focal loss in current study due to:
1. **Scope:** Our contribution is establishing fair baselines/protocols, not proposing new loss functions
2. **Computational budget:** 10 seeds × 3 schemas × 6 models already substantial
3. **Manuscript length:** Adding focal loss experiments would require 2-3 additional pages

We commit to dedicated follow-up paper on imbalance-aware loss functions (citing reviewer's suggested focal-regression work).

**Changes:**
- Section 4.2 (lines 1080-1095): Future work mention with citation
- refs.bib: lin2017focal already included

---

## Summary of Changes

**Major Additions:**
1. ✅ Line numbers (lineno package) - Reviewer 7
2. ✅ 9 new references (R3, R4, R5 requested papers)  
3. ✅ Section 4.6: Feature Importance (Reviewer 7, 8)
4. ✅ Section 4.7: LOSO validation (Reviewer 7, 8)
5. ✅ Section 3.5: Imbalance-aware training (Reviewer 8)
6. ✅ Enhanced Data Availability with Zenodo details (Reviewer 1, 2)
7. ✅ Explicit modern dataset justification (Reviewer 1, 5)

**Clarifications:**
1. ✅ Equation duplicate = false positive (Reviewer 6)
2. ✅ R² design = intentional (Reviewer 6)
3. ✅ FP n=158, not n=24 (Reviewer 2, 6, 7)
4. ✅ Calibrated baseline = not default COCOMO II (All reviewers)
5. ✅ Overall = macro-average (Reviewer 2)

**No Changes Required:**
- Ablation study (comprehensive)
- Post-hoc tests (comprehensive)  
- Limitations discussion (comprehensive)
- Paper organization (present)

---

We believe these revisions fully address all reviewer concerns while maintaining methodological rigor and manuscript coherence. We thank the reviewers again for their constructive feedback and look forward to resubmission.

---

**Word count:** ~8,500 words  
**Revised manuscript:** 42 pages, 3.73 MB PDF
