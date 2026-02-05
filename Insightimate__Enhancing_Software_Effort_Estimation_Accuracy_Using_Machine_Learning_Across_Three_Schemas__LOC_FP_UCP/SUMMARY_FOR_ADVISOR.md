# BÁO CÁO SƠ BỘ CHO THẦY MẬN
## Revision Plan - 10 Ngày

---

## 📊 TÓM TẮT TÌNH HUỐNG

**Decision:** Major Revision (cơ hội accept 75-85% nếu sửa tốt)  
**Số reviewers:** 8 reviewers  
**Thời hạn:** 10 ngày (khuyến nghị xin thêm 5 ngày → tổng 15)  
**Mức độ:** Không có vấn đề chí mạng về tính đúng đắn khoa học, CHỦ YẾU là vấn đề trình bày, baseline comparison, và documentation

---

## 🎯 3 QUYẾT ĐỊNH CHIẾN LƯỢC CẦN THẦY CHỐT NGAY

### 1. COCOMO II Recalibration (QUAN TRỌNG NHẤT)

**Vấn đề:** Reviewers 1, 7, 8 cho rằng so sánh với COCOMO II "out-of-the-box" không công bằng. Cần calibrate parameters A, B trên training data.

**Options:**
- **(A) Làm đầy đủ** (2-3 ngày): Fit A, B trên train từng schema → báo cáo "COCOMO II (original)" vs "COCOMO II (calibrated)" vs "RF"
  - ✅ Tăng cơ hội accept 15-20%
  - ✅ Chứng minh RF tốt hơn CẢ optimized baseline (stronger claim)
  - ⚠️ Cần 2-3 ngày

- **(B) Chỉ giải thích** (0.5 ngày): Nói "preliminary calibration shows MMRE improves to ~1.85, but RF remains superior"
  - ⚠️ Reviewer có thể không hài lòng

**👉 Khuyến nghị: Option A** - Đây là yêu cầu cốt lõi của 3 reviewers.

---

### 2. XGBoost / Modern SOTA Models

**Vấn đề:** Reviewers 4, 7 chê model selection "outdated" - thiếu XGBoost/LightGBM/CatBoost.

**Options:**
- **(A) Thêm XGBoost** (1-2 ngày): Train XGBoost làm model thứ 5, so sánh với RF/GB
  - ✅ Dễ implement (scikit-learn có sẵn)
  - ✅ Tăng điểm với R4/R7
  - ⚠️ Cần 1-2 ngày + rerun experiments

- **(B) Không thêm**: Giải thích scope + đưa Future Work
  - ✅ Tiết kiệm thời gian
  - ⚠️ R4/R7 có thể vẫn không hài lòng

**👉 Khuyến nghị: Option A nếu còn thời gian** - XGBoost là "low-hanging fruit", dễ làm, impact cao.

---

### 3. GitHub/Jira Modern Data

**Vấn đề:** Reviewer 1 muốn validation trên dữ liệu hiện đại (GitHub/Jira).

**Options:**
- **(A) Thu thập mini-set** (3-4 ngày): 30-50 projects từ GitHub có effort trong README → validation
  - ⚠️ Khó: GitHub không có effort ground truth tốt
  - ⚠️ Cần 3-4 ngày

- **(B) Giải thích limitation**: "GitHub/Jira data present challenges: (1) effort not directly logged, (2) validation difficult. We acknowledge as limitation and recommend for future work."
  - ✅ Honest và hợp lý
  - ✅ Tiết kiệm thời gian cho việc quan trọng hơn

**👉 Khuyến nghị: Option B** - GitHub data quality không đảm bảo, giải thích rõ ràng là đủ.

---

## 🚨 6 VẤN ĐỀ CRITICAL - BẮT BUỘC PHẢI SỬA

### Priority 1: "Overall across schemas" mơ hồ
**Vấn đề:** Table 1 "overall" không định nghĩa → LOC n=947 áp đảo FP n=24

**Cách sửa:**
1. Abstract: Thêm 1 câu "Overall metrics computed as macro-average (unweighted mean) across three schemas"
2. Results: Thêm subsection "Aggregation Strategy" với công thức
3. NEW table: Báo cáo per-schema (LOC | FP | UCP) riêng

**Thời gian:** 0.5 ngày  
**Reviewer:** R6, R8

---

### Priority 2: COCOMO II baseline không fair
**→ Đã nói ở Decision 1**

---

### Priority 3: Target Leakage - Developers
**Vấn đề:** Code hiện tại tính `Developers = ceil(Effort / Time)` → dùng target tạo feature (NGHIÊM TRỌNG)

**Cách sửa:**
- REMOVE `Developers` khỏi features nếu nó được suy ra từ Effort
- CHỈ dùng `Developers` nếu có sẵn trong dataset gốc

**Thời gian:** 0.5 ngày  
**Reviewer:** R8 (review.md Question 3)

---

### Priority 4: FP n=24 - Protocol không phù hợp
**Vấn đề:** 80/20 split → test set chỉ ~5 samples, grid search dễ overfit

**Cách sửa:**
1. Với FP: dùng **Leave-One-Out Cross-Validation (LOOCV)** thay vì 80/20
2. Giảm hyperparameter search space cho FP
3. Báo cáo **bootstrap 95% CI** (wider CIs)
4. Kết luận FP: "Results considered exploratory due to small sample size"

**Thời gian:** 1 ngày  
**Reviewer:** R6, R7, R8

---

### Priority 5: Dataset Manifest thiếu
**Vấn đề:** Không audit được data sources, dedup criteria dễ gây leakage

**Cách sửa:**
NEW table trong Section 3.1:

| Source Name | Year | Link/DOI | Schema | Raw Count | After Dedup | Final Count |
|-------------|------|----------|--------|-----------|-------------|-------------|
| DASE GitHub | 2023 | https://... | LOC | 1200 | -150 (dup) | 1050 |
| ISBSG FP | 2015 | ... | FP | 30 | -6 (invalid) | 24 |
| ... | ... | ... | ... | ... | ... | ... |

**Thời gian:** 1 ngày  
**Reviewer:** R7, R8

---

### Priority 6: Formatting - No Captions / Mờ / Thiếu Line Numbers
**Vấn đề:** R7 nói "no captions", figures mờ, khó review

**Cách sửa:**
1. **All figures:** Xuất vector PDF hoặc 600dpi PNG + caption đầy đủ
2. **LaTeX preamble:** Thêm `\usepackage{lineno}` + `\linenumbers` để có line numbers khi resubmit
3. Check tất cả `\caption{}` - KHÔNG có figure nào thiếu caption

**Thời gian:** 1 ngày  
**Reviewer:** R5, R6, R7

---

## 📅 TIMELINE 10 NGÀY (hoặc 15 nếu xin thêm)

| Ngày | Công việc | Priority | Người làm |
|------|-----------|----------|-----------|
| **1-2** | **CRITICAL Block 1:**<br>• Fix "overall" aggregation definition<br>• COCOMO recalibration<br>• Remove Developers leakage<br>• FP LOOCV protocol | 1,2,3,4 | Huy code + Thầy review strategy |
| **3** | **CRITICAL Block 2:**<br>• Dataset manifest table<br>• Fix all figures (captions, high-res) | 5,6 | Huy |
| **4-5** | **MAJOR Block 1:**<br>• Viết lại Intro (novelty rõ hơn)<br>• Viết Related Work + cite 4 DOIs<br>• Fix equations (delete duplicate Time) | 7,8,9,10 | Huy draft + Thầy edit |
| **6-7** | **MAJOR Block 2:**<br>• Feature importance plots (interpretability)<br>• Ablation study (RF với/không log/IQR)<br>• Add metrics (MAPE, MdMRE, RAE)<br>• Compute R² cho tất cả models | 11,12,13,16,17 | Huy |
| **8** | **OPTIONAL:**<br>• XGBoost nếu kịp<br>• Polish language | 15 | Huy (nếu còn năng lượng) |
| **9** | **Integration:**<br>• Tích hợp tất cả changes<br>• Consistency check<br>• Generate all updated figures/tables | All | Huy + Thầy spot-check |
| **10** | **Final Review & Submit:**<br>• Thầy review toàn bộ<br>• Finalize Response Letter<br>• Submit | All | Thầy approve → Submit |

**🔴 Nếu thấy 10 ngày GẤP → XIN THÊM 5 NGÀY** (email template có trong REVISION_PRIORITY_TABLES.tex)

---

## ✅ CHECKLIST - Làm Xong Đánh Dấu

### CRITICAL (BẮT BUỘC)
- [ ] 1. Overall aggregation defined (Abstract + Results)
- [ ] 2. COCOMO II calibrated (A, B fitted on train)
- [ ] 3. Developers leakage removed (không dùng inferred)
- [ ] 4. FP protocol changed to LOOCV + bootstrap CI
- [ ] 5. Dataset manifest table added (6 columns)
- [ ] 6. All figures: captions + high-res + line numbers

### MAJOR (NÊN LÀM)
- [ ] 7. Equation lỗi fixed (delete duplicate Time)
- [ ] 8. R² computed cho tất cả models
- [ ] 9. Novelty rewritten (3 clear contributions)
- [ ] 10. Related Work section added (2-3 pages, cite 4 DOIs)
- [ ] 11. XGBoost added (nếu kịp)
- [ ] 12. Feature importance plot added
- [ ] 13. Ablation study table added

### MINOR (NẾU KỊP)
- [ ] 14. Leave-one-source-out generalization
- [ ] 15. Language polished (reduce AI-like tone)
- [ ] 16. MAPE, MdMRE, RAE added
- [ ] 17. Bootstrap 95% CIs for all metrics

---

## 💡 MẸO QUAN TRỌNG

### Về Response Letter:
- **Luôn bắt đầu:** "We thank the reviewer for this valuable/excellent suggestion."
- **Format:** Point-by-point, mỗi comment 1 đoạn riêng
- **Nêu rõ:** "Changes in manuscript: Section X, lines Y-Z" (có line numbers)
- **Khi không đồng ý:** Dùng "We respectfully note that..." + evidence, KHÔNG tranh cãi

### Về LaTeX:
- **Compile thường xuyên** để catch lỗi sớm
- **Git commit** sau mỗi major change (để có thể rollback)
- **Đặt tên figure rõ ràng:** `fig_overall_performance.pdf` thay vì `fig1.pdf`

### Về Code:
- **Backup** tất cả notebooks/scripts trước khi sửa
- **Log** tất cả experiments (timestamp, config, results) để reproducible
- **Test** trên small subset trước khi run full dataset

---

## 🎓 LIKELIHOOD OF ACCEPTANCE

| Scenario | Probability | Note |
|----------|-------------|------|
| Làm Priority 1-6 (CRITICAL only) | **60-70%** | Đủ để avoid reject, nhưng chưa strong |
| Làm Priority 1-10 (CRITICAL + key MAJOR) | **75-85%** | Recommended minimum |
| Làm Priority 1-14 (gần như tất cả) | **85-90%** | Ideal, nếu còn năng lượng |

**Khuyến nghị:** Tập trung 1-10 trước, làm 11-14 nếu còn thời gian. **Xin thêm 5 ngày** để chất lượng tốt hơn.

---

## 📞 NEXT STEPS IMMEDIATE

### Trong 24h:
1. ✅ **Thầy đọc file này** + REVISION_PRIORITY_TABLES.tex
2. ✅ **Quyết định 3 chiến lược:** COCOMO recalibration? XGBoost? GitHub data?
3. ✅ **Phân công:** Huy làm gì, Thầy review gì
4. ✅ **Quyết định:** Xin thêm thời gian hay không?

### Email cho Editor (nếu xin thêm thời gian):
```
Subject: Request for Extension - Manuscript 6863b9b0-4db8-4b53-843f-5be5e907cf62

Dear Editor,

We have received detailed reviews from 8 reviewers for our manuscript. 
We are committed to addressing all concerns comprehensively, including:
- Baseline recalibration for fair comparison
- Additional statistical analyses and ablation studies  
- Enhanced dataset documentation with provenance table
- Improved methodological clarity

Given the substantive revisions requested, we respectfully request a 
5-day extension (total 15 working days) to ensure rigorous implementation 
rather than superficial changes.

Thank you for your consideration.

Best regards,
[Authors]
```

---

## 📂 FILES CREATED

1. ✅ **REVISION_PRIORITY_TABLES.tex** - Bảng LaTeX đầy đủ (compile được)
2. ✅ **SUMMARY_FOR_ADVISOR.md** - File này (tóm tắt cho Thầy)
3. ✅ **RESPONSE_TO_REVIEWERS.md** - Point-by-point response draft (đã có trước)
4. ✅ **STRATEGY_FOR_ADVISOR.md** - Chiến lược chi tiết (đã có trước)

---

## ❓ CÂU HỎI CHO THẦY

1. **COCOMO recalibration:** Option A (làm đầy đủ) hay B (giải thích)?
2. **XGBoost:** Có thêm hay không?
3. **Timeline:** Xin thêm 5 ngày hay làm trong 10 ngày?
4. **Phân công:** Thầy review phần nào? Huy tự quyết định phần nào?

**Khi có câu trả lời → Huy bắt đầu implement ngay.**

---

**Liên hệ:** Huy sẵn sàng họp với Thầy bất cứ lúc nào để clarify bất kỳ điểm nào.

**Tinh thần:** Đây là Major Revision, KHÔNG phải Reject. Cơ hội accept rất cao nếu làm tốt. 8 reviewers có vẻ nhiều nhưng hầu hết yêu cầu OVERLAP (cùng 1 vấn đề), không phải 8 vấn đề riêng biệt. **Chúng ta làm được!** 💪
