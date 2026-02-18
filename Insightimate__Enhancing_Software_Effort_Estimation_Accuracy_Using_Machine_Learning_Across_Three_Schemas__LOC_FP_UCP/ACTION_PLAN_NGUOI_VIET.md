# 📋 HƯỚNG DẪN CỤ THỂ - LÀM GÌ TIẾP THEO?

**Ngày:** 12/02/2026  
**Situation:** Thầy yêu cầu nộp bài + highlight changes cho Major Revision

---

## 🎯 BẠN CẦN NỘP CHO JOURNAL 3 FILE:

1. ✅ **main.pdf** (Clean version - bản sạch không có highlight)
2. ✅ **main_tracked.pdf** (Highlighted version - đánh dấu chỗ sửa)
3. ✅ **response_to_reviewers.pdf** (Trả lời từng reviewer)

---

## 📝 BƯỚC 1: COMPILE PDF BẢN SẠCH (10 phút)

**Làm thế nào:**

```bash
# Mở terminal, chạy lệnh:
cd /home/dtu/AI-Project/AI-Project/Insightimate__Enhancing_Software_Effort_Estimation_Accuracy_Using_Machine_Learning_Across_Three_Schemas__LOC_FP_UCP

# Compile PDF
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex

# Kiểm tra file
ls -lh main.pdf
```

**Kết quả:** Có file `main.pdf` (~3-5 MB)

**Check xem có lỗi không:**
- Mở main.pdf
- Xem có hiển thị đúng không
- Check Section 2.1 có "scipy.optimize.curve_fit" chưa
- Check có "Imbalance-Aware Training" ở Section 3.6 chưa

---

## 🟨 BƯỚC 2: TẠO BẢN HIGHLIGHT (30 phút)

**Có 2 CÁCH - Chọn 1:**

### 🔴 CÁCH 1: DÙNG LaTeX PACKAGE `changes` (RECOMMENDED)

**Ưu điểm:** Professional, giữ nguyên format LaTeX

**Làm thế nào:**

1. **Thêm package vào main.tex:**

```latex
% Thêm vào preamble (sau line 30)
\usepackage[final]{changes}  % final = show changes, draft = hide
\definechangesauthor[color=yellow]{revised}

% Các commands để dùng:
% \added{text mới}
% \deleted{text xóa}
% \replaced{text cũ}{text mới}
% \highlight{text cần nhấn mạnh}
```

2. **Bọc các đoạn quan trọng:**

Tôi sẽ tạo file hướng dẫn chi tiết bên dưới!

### 🟡 CÁCH 2: DÙNG WORD (DỄ HƠN NHƯNG MẤT FORMAT)

**Làm thế nào:**

```bash
# Convert PDF sang Word
pandoc main.tex -o main.docx --bibliography=refs.bib

# Mở trong Word
libreoffice main.docx  # hoặc MS Word nếu có

# Trong Word:
# 1. Review tab → Track Changes → ON
# 2. Dùng Highlight tool (màu vàng)
# 3. Highlight các sections đã list trong REVISION_HIGHLIGHTS.md

# Save as PDF
# File → Export as PDF → main_tracked.pdf
```

---

## 📋 BƯỚC 3: TẠO RESPONSE TO REVIEWERS LETTER

**Có SẴN template!** Bạn đã có draft trong conversation trước.

**File template:** `response_to_reviewers.tex` (cần tạo lại)

Tôi sẽ tạo file LaTeX template ngay bây giờ!

---

## ⚡ NHANH NHẤT - DÙNG CÁCH NÀY (1 TIẾNG)

### Plan A: Không cần highlight chi tiết

**Nếu journal chấp nhận:**
- ✅ Nộp clean main.pdf
- ✅ Nộp response letter với TABLE chỉ rõ "Where revised in manuscript"
- ✅ Trong response table, ghi rõ: "Section X, Page Y, Lines Z"

**Ví dụ response table:**

| Reviewer Comment | Our Response | Where Revised |
|------------------|--------------|---------------|
| R8: Limited novelty | Implemented imbalance-aware learning | **Section 3.6 (p.15), Abstract (p.1), Results Section 4.X (p.28)** |

→ **KHÔNG CẦN highlight PDF**, chỉ cần TABLE chi tiết!

---

### Plan B: Cần highlight PDF (nếu journal yêu cầu)

**Nhanh nhất:**

1. **Dùng PDF editor như Okular hoặc Xournal++:**

```bash
# Cài Xournal++
sudo apt install xournalpp

# Mở PDF
xournalpp main.pdf

# Dùng Highlight tool (màu vàng)
# Highlight theo list trong REVISION_HIGHLIGHTS.md

# Save as main_tracked.pdf
```

2. **Các đoạn CẦN HIGHLIGHT (PRIORITY 1):**

📍 **Page 1 (Abstract):**
- Line 76-78: "imbalance-aware weighting", "calibrated size-only power-law baselines"

📍 **Page 4-5 (Section 2.1):**
- **ENTIRE SECTION** "Calibrated Size-Only Power-Law Baseline"
- Line ~171-175: "scipy.optimize.curve_fit" paragraph

📍 **Page 15 (Section 3.6):**
- **ENTIRE SECTION** "Imbalance-Aware Training via Quantile Reweighting"

📍 **Page 28 (Section 4.10):**
- **ENTIRE SECTION** "Feature Importance and Interpretability"

📍 **Tables: Table 2 (Statistical Tests):**
- **ENTIRE TABLE** với Wilcoxon results

---

## 🎯 TÓM TẮT - QUYẾT ĐỊNH NGAY:

### ❓ Thầy yêu cầu gì?

**Nếu thầy chỉ cần:**
1. ✅ "Xem qua bài" → Compile main.pdf cho thầy
2. ✅ "Finalize để submit" → Làm theo Plan A (không cần highlight)
3. ✅ "Highlight rõ ràng" → Làm theo Plan B (dùng Xournal++)

### 📞 HỎI THẦY TRƯỚC KHI LÀM:

**Message cho thầy:**

> Thầy ơi, em đã sửa xong hết rồi. Giờ em cần nộp cho thầy:
> 
> 1. **File PDF bản sạch** (main.pdf) - đã compile xong
> 2. **Response to reviewers** - em có template sẵn, cần thầy review
> 3. **Highlight changes**: Journal có yêu cầu file PDF với highlights không thầy?
>    - Nếu KHÔNG: Em chỉ ghi rõ "Where revised" trong response table
>    - Nếu CÓ: Em sẽ dùng PDF editor để highlight các sections mới
> 
> Thầy muốn em làm theo cách nào ạ?

---

## ⚡ ACTION NGAY BÂY GIỜ - 3 COMMANDS:

```bash
# 1. Compile PDF
cd /home/dtu/AI-Project/AI-Project/Insightimate__Enhancing_Software_Effort_Estimation_Accuracy_Using_Machine_Learning_Across_Three_Schemas__LOC_FP_UCP
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex

# 2. Check kết quả
evince main.pdf &  # Hoặc: xdg-open main.pdf

# 3. Tạo response letter (tôi sẽ gen template ngay)
```

**Tôi ĐANG TẠO:**
1. ✅ Response to reviewers LaTeX template
2. ✅ Quick highlight guide (PDF annotator)
3. ✅ Submission checklist

**Bạn CHỜ 2 PHÚT!**
