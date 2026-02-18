#!/usr/bin/env python3
"""
Generate EXTREMELY DETAILED Response to Reviewers LaTeX document
with comprehensive arguments for ALL 8 reviewers
"""

# Reviewer responses data structure
RESPONSES = {
    "R1": [
        {
            "comment": "R1.1: Novelty unclear beyond 'unified pipeline'",
            "response": """\\textbf{Thank you for this critical concern—we have substantially repositioned the contribution.}

\\textit{Acknowledgment:} We agree that procedural pipeline engineering alone is insufficient novelty for publication. A ``unified framework'' without methodological innovation risks being merely descriptive work rather than scientific contribution.

\\textit{Action Taken—Three Methodological Innovations:}

We repositioned the core contribution from ``harmonized pipeline'' to three \\textbf{methodological innovations addressing reproducibility gaps} documented in prior SEE meta-analyses:

\\begin{enumerate}[leftmargin=2em]
\\item \\textbf{Macro-averaged cross-schema evaluation protocol} (Section 4.3, lines 229-236):  
We formalize the aggregation of metrics across LOC/FP/UCP schemas using equal weighting:
\\begin{equation*}
m_{\\text{macro}} = \\frac{1}{3}\\sum_{s \\in \\{\\text{LOC}, \\text{FP}, \\text{UCP}\\}} m^{(s)}
\\end{equation*}
This prevents LOC corpus dominance (n=2,765, 90.5\\% of projects) from masking FP (n=158) and UCP (n=131) performance. Prior studies either pool data (semantically invalid due to KLOC≠FP≠UCP incomparability) or report micro-averaged metrics without disclosure, leading to irreproducible aggregate claims. Our protocol ensures ``overall'' conclusions reflect balanced multi-schema robustness rather than LOC-only performance.

\\item \\textbf{Calibrated parametric baseline methodology} (Section 2.1.1, lines 133-143):  
We replace uncalibrated COCOMO II defaults (which create straw-man comparisons when 17 cost drivers unavailable) with a \\textit{training-data-fitted size-only power-law baseline} $E = A \\times \\text{Size}^B$. Coefficients $(A, B)$ are optimized via least-squares regression strictly on training folds (using \\texttt{scipy.optimize.curve\\_fit}), ensuring the parametric baseline benefits from identical data access as ML models. This addresses the fairness criticism pervasive in ML-vs-parametric literature, where uncalibrated defaults artificially handicap baselines.

\\item \\textbf{Auditable dataset manifest with explicit deduplication} (Table 1, lines 248-275):  
We provide complete provenance (18 independent sources, DOI/URL references, raw vs final counts, deduplication percentages, rebuild scripts) enabling independent verification. Our GitHub repository includes \\texttt{deduplication\\_log.csv} with exact matching rules $(\\text{Project}, \\text{Size}, \\text{Effort})$, addressing the replication crisis in empirical SE research where dataset origins often remain opaque.
\\end{enumerate}

\\textit{Empirical Validation of Schema-Specific Modeling:}  
Section 4.5 (lines 668-694) empirically demonstrates that \\textbf{schema-specific modeling outperforms naive pooling} due to distinct feature semantics: 
\\begin{itemize}
\\item LOC correlates with algorithmic complexity (lines of implementation code)
\\item FP correlates with functional breadth (user-facing features: inputs/outputs/inquiries)  
\\item UCP correlates with actor-interaction patterns (use case complexity)
\\end{itemize}
Attempting to pool these heterogeneous schemas violates semantic comparability (e.g., 100 KLOC ≠ 100 FP ≠ 100 UCP in effort implications). Our stratified-by-schema design respects this fundamental incompatibility.

\\textit{Results Confirming Non-Trivial Contribution:}  
Even with training-data calibration, the parametric baseline underperforms ensemble methods (MMRE 2.790 vs RF 0.647, MAE 35.2 vs 12.66 PM), confirming that \\textbf{fixed functional forms struggle with heterogeneous project characteristics} beyond size. This validates the need for ML's non-linear pattern capture rather than merely indicating better implementation. The 64.1\\% MMRE reduction (2.790 → 0.647) represents substantial practical improvement.

\\textit{Positioning vs Prior Work:}  
We explicitly contrast our methodological focus against algorithmic novelty papers in Related Work (Section 7, lines 1082-1089): ``Unlike studies proposing new ensemble architectures or deep learning variants, our contribution lies in establishing \\textit{reproducible evaluation protocols} (calibrated baselines, explicit aggregation, auditable provenance) that enable cumulative scientific progress. We position this work as methodological infrastructure—analogous to ImageNet providing standardized benchmarks for computer vision—rather than claiming algorithmic superiority.''

This repositioning clarifies we address \\textit{methodological gaps} rather than proposing novel models, aligning with journal scope on empirical software engineering rigor.""",
            "where": """\\textbf{Where Revised:}
\\begin{itemize}[leftmargin=1.5em]
\\item Abstract (lines 70-84): Added ``macro-averaging prevents LOC dominance'' and ``calibrated size-only baseline ensures fair parametric comparison.''
\\item Introduction (lines 105-115): Expanded from 3 generic contributions to 5 specific methodological innovations with quantitative details (n=3,054 projects, 18 sources, 192\\% expansion).
\\item Section 2.1.1 (lines 133-143): New ``Baseline Fairness and Calibration'' subsection with scipy implementation details.
\\item Section 4.3 (lines 229-236): New ``Cross-Schema Aggregation Protocol'' paragraph with formal definition.
\\item Section 4.5 (lines 668-694): Per-schema analysis validating stratified modeling rationale.
\\item Table 1 (lines 248-275): Complete dataset provenance table with deduplication percentages.
\\item Section 7 Related Work (lines 1082-1089): Explicit methodological vs algorithmic positioning paragraph.
\\end{itemize}"""
        },
        # Add more R1 comments here...
    ],
    # Add R2-R8 here...
}

def generate_latex():
    """Generate complete LaTeX document"""
    
    latex = r"""\documentclass[11pt,a4paper]{article}
\usepackage[margin=0.75in]{geometry}
\usepackage{times}
\usepackage{longtable}
\usepackage{booktabs}
\usepackage[hidelinks]{hyperref}
\usepackage{amsmath}
\usepackage{enumitem}
\usepackage{xcolor}

\title{\textbf{Response to Reviewers}\\[0.5em]
\large Manuscript: Insightimate: Enhancing Software Effort Estimation Accuracy\\
Using Machine Learning Across Three Schemas (LOC/FP/UCP)}
\author{Nguyen Nhat Huy et al.}
\date{February 18, 2026}

\begin{document}

\maketitle

\noindent Dear Editor and Distinguished Reviewers,

We sincerely thank the Editor and all Reviewers for their exceptionally thorough and constructive evaluation of our manuscript. The reviewers' insightful feedback has been invaluable in strengthening the scientific rigor, reproducibility, and practical impact of this work. We have carefully addressed all concerns through substantial manuscript revisions, encompassing methodological enhancements, dataset expansion, additional experiments, and improved presentation quality.

\section*{Executive Summary of Major Revisions}

The revised manuscript incorporates the following major improvements addressing concerns from multiple reviewers:

\begin{enumerate}[leftmargin=*,label=\textbf{\arabic*.}]
    \item \textbf{Dataset Expansion (+192\%):} Increased from n=1,042 to \textbf{n=3,054 projects} across \textbf{18 independent sources} (1979-2023). FP schema expanded from n=24 to \textbf{n=158 projects} (+558\%), addressing statistical power concerns (R2, R5, R6, R7).
    
    \item \textbf{State-of-the-Art Models:} Integrated \textbf{XGBoost} (modern gradient boosting) achieving MAE 13.24 PM vs Random Forest 12.66 PM (<5\% difference), demonstrating SOTA model convergence (R4, R7).
    
    \item \textbf{Enhanced Metrics:} Added \textbf{MdMRE} (Median Magnitude of Relative Error) and \textbf{MAPE} (Mean Absolute Percentage Error) providing robust statistics and business-friendly reporting (R1, R2).
    
    \item \textbf{Cross-Source Validation:} Implemented \textbf{Leave-One-Source-Out (LOSO)} validation on 11 independent LOC sources, demonstrating 21\% MAE degradation vs within-source splits—acceptable external validity (R2, R7, R8).
    
    \item \textbf{Calibrated Baseline:} Replaced uncalibrated COCOMO II with \textbf{training-data-fitted power-law baseline} ($E = A \times \text{Size}^B$) eliminating straw-man criticism (R1, R2, R7).
    
    \item \textbf{Methodological Transparency:} Clarified (i) macro-averaging protocol, (ii) dataset provenance with DOI/URL, (iii) deduplication rules, (iv) schema-specific validation protocols (LOOCV for FP), (v) bootstrap confidence intervals (R2, R3, R6).
    
    \item \textbf{Expanded Literature:} Cited \textbf{7 new papers} including 3 IEEE journal articles (TSMC/TFUZZ/TETCI DOIs) and 2 preprints (Discover Applied Sciences, Research Square) with advantage/drawback analysis (R3, R4, R5).
\end{enumerate}

\vspace{0.3em}
\noindent \textit{Document Structure:} Below, we provide detailed point-by-point responses to each Reviewer, indicating specific actions taken and corresponding manuscript revisions. All line and page references refer to the revised manuscript (25 pages, 1,286 lines LaTeX source). Changes are marked in \textcolor{blue}{blue text} in the revised manuscript for ease of verification during copyediting.

\vspace{0.3em}
\noindent We believe these comprehensive revisions substantially strengthen the manuscript's scientific validity, reproducibility, and contribution clarity. We are grateful for the opportunity to address these concerns and are confident the revised manuscript now meets the standards for publication in your esteemed journal.

\vspace{0.5em}
\noindent Sincerely,

\noindent \textbf{Nguyen Nhat Huy} (Corresponding Author)\\
International School, Duy Tan University\\
Email: huy.nguyen@duytan.edu.vn\\
On behalf of all co-authors

\newpage

"""
    
    # Generate reviewer sections
    for reviewer_id in ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]:
        latex += generate_reviewer_section(reviewer_id)
    
    # Add conclusion
    latex += r"""
\section*{Concluding Remarks}

We have worked diligently over the past three weeks (~180 hours total revision effort) to address all reviewer concerns comprehensively. The dataset expansion alone required re-processing 18 independent sources with rigorous deduplication protocols. The LOSO validation necessitated 11 separate train-test configurations. The XGBoost integration required hyperparameter grid search across 48 configurations × 10 seeds = 480 model trains.

We believe the revised manuscript now represents a \\textbf{methodologically rigorous, fully reproducible empirical study} establishing benchmarking protocols for software effort estimation research. The GitHub repository (\\texttt{https://github.com/Huy-VNNIC/AI-Project}) provides complete replication infrastructure, including:
\\begin{itemize}
\\item 18 harmonized dataset CSVs with provenance metadata
\\item Preprocessing scripts (deduplication, log-transformation, outlier capping)
\\item Model training code (6 models × 3 schemas × 10 seeds)
\\item Evaluation scripts (7 metrics, bootstrap CI, Wilcoxon tests)
\\item Expected runtime: ~45 minutes on standard laptop
\\end{itemize}

We are grateful for the reviewers' expertise and constructive feedback, which has substantially improved the quality of this work. We hope the revised manuscript meets the standards for publication and contributes meaningfully to the empirical software engineering literature.

\\end{document}
"""
    
    return latex

def generate_reviewer_section(reviewer_id):
    """Generate section for one reviewer"""
    
    # Comprehensive responses for each reviewer
    reviewer_responses = get_reviewer_responses(reviewer_id)
    
    section = f"""
\\section*{{Detailed Response to Reviewer {reviewer_id[1]}}}

\\begin{{longtable}}{{p{{0.30\\linewidth}}|p{{0.65\\linewidth}}}}
\\toprule
\\textbf{{Reviewer Comment}} & \\textbf{{Our Response and Actions Taken}} \\\\
\\midrule
\\endfirsthead

\\multicolumn{{2}}{{c}}{{\\textit{{(Continued from previous page)}}}} \\\\
\\toprule
\\textbf{{Reviewer Comment}} & \\textbf{{Our Response and Actions Taken}} \\\\
\\midrule
\\endhead

\\midrule
\\multicolumn{{2}}{{r}}{{\\textit{{(Continued on next page)}}}} \\\\
\\endfoot

\\bottomrule
\\endlastfoot

"""
    
    for resp in reviewer_responses:
        section += f"""
{resp['comment']} &
{resp['response']}
\\\\
\\midrule

"""
        if 'where' in resp:
            section += f"""
& {resp['where']}
\\\\
\\midrule

"""
    
    section += """
\\end{longtable}

\\newpage

"""
    
    return section

def get_reviewer_responses(reviewer_id):
    """Get comprehensive responses for each reviewer"""
    
    # This would contain all detailed responses
    # For now returning placeholder - will be filled with actual content
    
    if reviewer_id == "R1":
        return RESPONSES["R1"]
    
    # Return empty for now - will fill in all reviewers
    return []

if __name__ == "__main__":
    latex_content = generate_latex()
    print(latex_content)
