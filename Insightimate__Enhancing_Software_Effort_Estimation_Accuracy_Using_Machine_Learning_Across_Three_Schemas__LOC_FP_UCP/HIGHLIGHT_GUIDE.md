# 🎯 HƯỚNG DẪN HIGHLIGHT - CHỖ NÀO ĐÃ SỬA

## 📍 DANH SÁCH CHÍNH XÁC CÁC CHỖ CẦN HIGHLIGHT

Thầy muốn highlight để thấy chỗ nào đã sửa theo yêu cầu reviewers. Dưới đây là **DANH SÁCH ĐẦY ĐỦ** với số dòng, số trang, và nội dung chính xác.

---

## 🔴 1. SCIPY.OPTIMIZE.CURVE_FIT (CRITICAL - MỚI SỬA SESSION NÀY)

### 📄 Vị trí trong main.tex:
- **Dòng: 172-176** 
- **Section:** 2.1 Calibrated Size-Only Power-Law Baseline
- **Trang PDF:** ~4-5

### 📝 Nội dung CHÍNH XÁC cần highlight:

```
Implementation Details.
We implement the calibration using scipy.optimize.curve_fit, which performs 
non-linear least squares optimization to find optimal (α, β) parameters for 
Eq. [number]. For each schema (s ∈ {LOC, FP, UCP}) and random seed (k=1,...,10), 
we fit the power-law model exclusively on the training split, then apply the 
learned parameters to predict test-set efforts. This ensures the parametric 
baseline receives identical data access as ML models, providing a fair lower 
bound for comparison. The optimization minimizes squared residuals in log-space: 
Σᵢ(log Eᵢ - (α + β log Sizeᵢ))², converging via the Levenberg-Marquardt algorithm.
```

### 🎨 Trong PDF - Highlight:
- **Trang 4-5:** Tìm paragraph bắt đầu bằng "**Implementation Details.**"
- **Highlight MÀU VÀNG** toàn bộ paragraph này (khoảng 6-8 dòng)
- **ĐẶC BIỆT chú ý:** Chữ "scipy.optimize.curve_fit" phải được highlight

---

## 🔴 2. IMBALANCE-AWARE LEARNING (CRITICAL)

### 📄 Vị trí trong main.tex:
- **Dòng: 671-688**
- **Section:** 3.6 Imbalance-Aware Training via Quantile Reweighting
- **Trang PDF:** ~15-16

### 📝 Nội dung:

```
Section 3.6: Imbalance-Aware Training via Quantile Reweighting

To address the skewed effort distribution (most projects are small, but 
high-effort outliers matter disproportionately), we introduce quantile-based 
sample reweighting for tree-based models (Random Forest, Gradient Boosting, 
XGBoost).

For each training observation i, we assign a weight wᵢ based on its effort 
quantile:
[Equation with quantile formula showing 4× weight for tail projects]

This scheme assigns 4× weight to the top 10% effort projects (tail), 
promoting better calibration on high-stakes outliers.
```

### 🎨 Trong PDF - Highlight:
- **Trang 15-16:** Tìm **Section 3.6 title** "Imbalance-Aware Training via Quantile Reweighting"
- **Highlight MÀU VÀNG:**
  - Section title (1 dòng)
  - First paragraph (explaining quantile reweighting)
  - Equation với w_i formula
  - Paragraph after equation (explaining 4× weight)

---

## 🔴 3. XGBOOST (CRITICAL)

### 📄 Vị trí trong main.tex:
- **Dòng: 661-669**
- **Section:** 3.5 Modeling Details
- **Trang PDF:** ~14-15

### 📝 Nội dung:

```
XGBoost [Chen & Guestrin, 2016]: Extreme Gradient Boosting with 
learning_rate ∈ {0.01, 0.05, 0.1}, max_depth ∈ {3, 5, 7}, 
n_estimators ∈ {50, 100, 200}, and L1/L2 regularization. 
We use squared error loss for regression.
```

### 🎨 Trong PDF - Highlight:
- **Trang 14-15:** Tìm paragraph về "**XGBoost**"
- **Highlight MÀU VÀNG** toàn bộ bullet/paragraph về XGBoost (3-5 dòng)
- **ĐẶC BIỆT:** Chữ "XGBoost" và citation phải được highlight

---

## 🔴 4. STATISTICAL TESTS (CRITICAL)

### 📄 Vị trí trong main.tex:
- **Dòng: 734-750**
- **Section:** 3.9 Uncertainty & Significance Testing
- **Trang PDF:** ~17-18

### 📝 Nội dung:

```
Section 3.9: Uncertainty & Significance Testing

We perform paired Wilcoxon signed-rank tests between each ML model and the 
calibrated baseline across 10 seeds. To control the family-wise error rate, 
we apply Holm–Bonferroni correction. We report Cliff's delta (δ) as a 
non-parametric effect size measure:

δ = (# wins - # losses) / (n₁ × n₂)

where |δ| < 0.147 is negligible, 0.147-0.33 small, 0.33-0.474 medium, 
>0.474 large.
```

### 🎨 Trong PDF - Highlight:
- **Trang 17-18:** Tìm **Section 3.9** hoặc subsection về statistical testing
- **Highlight MÀU VÀNG:**
  - Section/subsection title
  - Paragraph mentioning "Wilcoxon", "Holm-Bonferroni", "Cliff's delta"
  - Equation hoặc formula của Cliff's delta
  - Interpretation thresholds (negligible, small, medium, large)
- **NOTE:** Cũng highlight **Table 2** nếu có (significance test results)

---

## 🔴 5. FEATURE IMPORTANCE (CRITICAL)

### 📄 Vị trí trong main.tex:
- **Dòng: 1284-1320**
- **Section:** 4.10 Feature Importance and Interpretability
- **Trang PDF:** ~29-30

### 📝 Nội dung:

```
Section 4.10: Feature Importance and Interpretability

To address interpretability concerns, we perform permutation feature importance 
analysis on the best-performing Random Forest model. Permutation importance 
measures the increase in prediction error when a feature's values are randomly 
shuffled, quantifying each feature's contribution to model performance.

Key findings:
- Size (LOC/FP/UCP) is the dominant predictor (importance > 0.XX)
- [Other findings about complexity, development time, etc.]

This analysis provides transparency into what drives the model's predictions, 
addressing black-box concerns raised by reviewers.
```

### 🎨 Trong PDF - Highlight:
- **Trang 29-30:** Tìm **Section 4.10** "Feature Importance and Interpretability"
- **Highlight MÀU VÀNG:**
  - Section title (1 dòng)
  - Entire first paragraph (explaining permutation importance)
  - Key findings bullet points or paragraph
  - Any figure caption về feature importance
- **NOTE:** Nếu có **Figure** về feature importance → Highlight caption của figure đó

---

## 🔴 6. ABLATION STUDY (CRITICAL)

### 📄 Vị trí trong main.tex:
- **Dòng: 1161-1240**
- **Section:** 4.6 Ablation Study
- **Trang PDF:** ~26-27

### 📝 Nội dung:

```
Section 4.6: Ablation Study

To quantify the contribution of each preprocessing component, we systematically 
remove preprocessing steps and measure MAE degradation:

Results:
- No harmonization: MAE increases by +X%
- No IQR capping (outlier removal): MAE increases by +Y%
- No log transformation: MAE increases by +Z%

This demonstrates that each preprocessing step contributes meaningfully to 
final performance.
```

### 🎨 Trong PDF - Highlight:
- **Trang 26-27:** Tìm **Section 4.6** "Ablation Study"
- **Highlight MÀU VÀNG:**
  - Section title (1 dòng)
  - Introduction paragraph explaining ablation methodology
  - **Table** hoặc **list** showing MAE changes when removing components
  - Conclusion paragraph
- **NOTE:** Nếu có **Table** về ablation results → Highlight toàn bộ table

---

## 🟡 7. ABSTRACT (OPTIONAL - ĐÃ CÓ SẴN, NÊN HIGHLIGHT)

### 📄 Vị trí trong main.tex:
- **Dòng: 76-78**
- **Section:** Abstract
- **Trang PDF:** 1

### 📝 Nội dung:

```
...calibrated size-only power-law baselines...imbalance-aware weighting...
stratified tail evaluation...
```

### 🎨 Trong PDF - Highlight:
- **Trang 1:** Abstract (đầu tiên của paper)
- **CHỈ HIGHLIGHT** các phrases sau (không cần highlight toàn bộ abstract):
  - "calibrated size-only power-law baseline"
  - "imbalance-aware weighting" hoặc "imbalance-aware"
  - "stratified tail evaluation"

---

## 📋 TÓM TẮT - HIGHLIGHT 6 CHỖ CHÍNH:

| # | Section | Trang PDF | Keyword để tìm | Màu |
|---|---------|-----------|----------------|-----|
| 1 | **Section 2.1 - Implementation Details** | 4-5 | "scipy.optimize.curve_fit" | 🟨 VÀNG |
| 2 | **Section 3.6 - Imbalance Training** | 15-16 | "Quantile Reweighting" | 🟨 VÀNG |
| 3 | **Section 3.5 - XGBoost** | 14-15 | "XGBoost" | 🟨 VÀNG |
| 4 | **Section 3.9 - Statistical Tests** | 17-18 | "Wilcoxon", "Cliff's delta" | 🟨 VÀNG |
| 5 | **Section 4.10 - Feature Importance** | 29-30 | "Permutation", "Interpretability" | 🟨 VÀNG |
| 6 | **Section 4.6 - Ablation Study** | 26-27 | "Ablation" | 🟨 VÀNG |

**BONUS (optional):**
- Abstract (trang 1): Highlight các keyword: "calibrated baseline", "imbalance-aware"

---

## 🔧 CÁCH HIGHLIGHT BẰNG XOURNAL++

### Bước 1: Cài Xournal++ (nếu chưa có)
```bash
sudo apt update
sudo apt install xournalpp
```

### Bước 2: Mở main.pdf
```bash
cd /home/dtu/AI-Project/AI-Project/Insightimate__Enhancing_Software_Effort_Estimation_Accuracy_Using_Machine_Learning_Across_Three_Schemas__LOC_FP_UCP
xournalpp main.pdf
```

### Bước 3: Highlight
1. **Tools → Highlighter** (hoặc nhấn `H`)
2. **Chọn màu VÀNG** (yellow)
3. **Độ dày:** Medium
4. **Drag chuột** qua các đoạn cần highlight theo bảng trên

### Bước 4: Lưu file
1. **File → Export as PDF**
2. **Tên file:** `main_highlighted.pdf` hoặc `main_tracked.pdf`
3. **Save**

### Bước 5: Verify
```bash
evince main_highlighted.pdf &
```
Kiểm tra 6 chỗ trên có được highlight màu vàng không.

---

## 🔧 CÁCH KHÁC: SỬ DỤNG OKULAR (PDF VIEWER CÓ SẴN)

### Bước 1: Mở PDF
```bash
okular main.pdf
```

### Bước 2: Enable Annotation Mode
- **Tools → Review** (hoặc `F6`)
- **Chọn Highlight tool** (icon marker vàng)

### Bước 3: Highlight
- **Click & drag** qua text cần highlight
- Tự động màu vàng

### Bước 4: Save
- **File → Save As**
- Tên: `main_highlighted.pdf`

---

## 📧 GỬI CHO THẦY

Sau khi highlight xong, gửi thầy:

1. ✅ **main_highlighted.pdf** (bản có highlight màu vàng)
2. ✅ **main.pdf** (bản gốc clean)
3. ✅ **response_to_reviewers.pdf** (nếu đã compile)

**Email:**
> Thầy ơi,
> 
> Em đã highlight (màu vàng) **6 chỗ chính** đã sửa theo yêu cầu reviewers:
> 1. ✅ scipy.optimize.curve_fit (Section 2.1, trang 4-5)
> 2. ✅ Imbalance-aware training (Section 3.6, trang 15-16)
> 3. ✅ XGBoost (Section 3.5, trang 14-15)
> 4. ✅ Statistical tests (Section 3.9, trang 17-18)
> 5. ✅ Feature importance (Section 4.10, trang 29-30)
> 6. ✅ Ablation study (Section 4.6, trang 26-27)
> 
> Em attach:
> - main_highlighted.pdf (có màu vàng)
> - main.pdf (bản sạch)
> 
> Thầy xem qua có OK không ạ?

---

## ⚡ NHANH NHẤT - 1 LỆNH:

```bash
# Cài tool + mở PDF
sudo apt install -y xournalpp && xournalpp /home/dtu/AI-Project/AI-Project/Insightimate__Enhancing_Software_Effort_Estimation_Accuracy_Using_Machine_Learning_Across_Three_Schemas__LOC_FP_UCP/main.pdf
```

Rồi highlight theo 6 chỗ trong bảng trên, **Save as** `main_highlighted.pdf`, XONG!

---

## 📝 CHECKLIST

Sau khi highlight xong, check lại:

- [ ] Section 2.1 (trang 4-5): "scipy.optimize.curve_fit" có màu vàng ✅
- [ ] Section 3.6 (trang 15-16): "Imbalance-Aware Training" có màu vàng ✅
- [ ] Section 3.5 (trang 14-15): "XGBoost" có màu vàng ✅
- [ ] Section 3.9 (trang 17-18): "Wilcoxon, Cliff's delta" có màu vàng ✅
- [ ] Section 4.10 (trang 29-30): "Feature Importance" có màu vàng ✅
- [ ] Section 4.6 (trang 26-27): "Ablation Study" có màu vàng ✅

**Nếu 6 cái trên OK → GỬI THẦY NGAY!** 🚀

---

## 🔍 TÌM NHANH TRONG PDF

Nếu khó tìm, dùng **Ctrl+F** (Find) trong PDF viewer:

1. **Trang 4-5:** Search "scipy.optimize" → Highlight đoạn đó
2. **Trang 15-16:** Search "Imbalance-Aware Training" hoặc "Quantile" → Highlight section đó
3. **Trang 14-15:** Search "XGBoost" → Highlight đoạn đó
4. **Trang 17-18:** Search "Wilcoxon" hoặc "Cliff" → Highlight section đó
5. **Trang 29-30:** Search "Permutation" hoặc "Interpretability" → Highlight section đó
6. **Trang 26-27:** Search "Ablation" → Highlight section đó

**XONG!** 🎉
