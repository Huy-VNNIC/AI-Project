# Academic Presentation: Multi-Schema Software Effort Estimation

## Tổng quan

Presentation học thuật chuyên nghiệp theo format **Claim–Evidence–Impact** để bảo vệ đề tài và tranh giải.

## Cấu trúc Presentation (16 slides chính + backup)

### Phần I: Introduction & Motivation (Slides 1-3)
1. **Title Slide** - Tiêu đề và thông tin tác giả
2. **Motivation** - Vấn đề và tầm quan trọng (có hình minh họa)
3. **Research Contributions** - Đóng góp chính (3 trụ cột)

### Phần II: Background & Methodology (Slides 4-7)
4. **COCOMO II Background** - Nền tảng lý thuyết + công thức
5. **Dataset Overview** - Nguồn dữ liệu và thống kê
6. **Data Heterogeneity** - Vấn đề Before/After
7. **Preprocessing Pipeline** - Flowchart chi tiết

### Phần III: Experiments & Results (Slides 8-12)
8. **Experimental Setup** - Mô hình và metrics
9. **Overall Results** - So sánh hiệu suất tổng quát
10. **Schema-Specific Performance** - Kết quả theo LOC/FP/UCP
11. **Error Analysis** - Actual vs Predicted + Feature Importance
12. **Residual Analysis** - Phân tích phần dư

### Phần IV: Applications & Conclusion (Slides 13-16)
13. **Deployment Architecture** - System architecture + API
14. **Practical Applications** - Use cases thực tế
15. **Limitations & Future Work** - Trung thực về hạn chế
16. **Conclusion** - Tổng kết và key takeaways

### Backup Slides
- References (thư mục tài liệu tham khảo)
- Detailed Metrics Table (bảng số liệu chi tiết)
- Hyperparameter Tuning (cấu hình mô hình)

## Hình ảnh đã tạo

Tất cả 10 hình đã được tạo tự động trong `figures/`:

1. `fig1_problem_illustration.pdf` - Vấn đề estimation sai
2. `fig2_data_heterogeneity.pdf` - Before/After normalization
3. `fig3_pipeline_flowchart.pdf` - Pipeline preprocessing
4. `fig4_model_comparison.pdf` - So sánh 5 mô hình (4 metrics)
5. `fig5_schema_performance.pdf` - Hiệu suất theo schema
6. `fig6_actual_vs_predicted.pdf` - Scatter plot RF
7. `fig7_feature_importance.pdf` - Feature importance
8. `fig8_residual_analysis.pdf` - Residual plots
9. `fig9_system_architecture.pdf` - Kiến trúc hệ thống
10. `fig10_cocomo_formula.pdf` - Công thức COCOMO II

## Cách sử dụng

### 1. Tạo hình ảnh (đã hoàn thành)
```bash
python presentation/generate_figures.py
```

### 2. Compile LaTeX Beamer
```bash
cd presentation
pdflatex academic_presentation.tex
pdflatex academic_presentation.tex  # Chạy 2 lần để cập nhật references
```

Hoặc dùng XeLaTeX nếu cần font Unicode:
```bash
xelatex academic_presentation.tex
```

### 3. Xem kết quả
```bash
evince academic_presentation.pdf  # Linux
open academic_presentation.pdf    # macOS
```

## Tùy chỉnh

### Thay đổi thông tin cá nhân
Chỉnh sửa trong file `academic_presentation.tex`:
```latex
\title[...]{...}
\author[Your Name]{Your Name \\ \texttt{your.email@university.edu}}
\institute[Your University]{...}
```

### Điều chỉnh số liệu thực tế
Nếu bạn có kết quả thực nghiệm thực tế từ code, chỉnh sửa trong:
- `generate_figures.py` - Hàm `generate_model_comparison()` và các hàm khác
- `academic_presentation.tex` - Các số liệu trong slides 9-12

### Thay đổi màu sắc theme
```latex
\definecolor{primaryblue}{RGB}{52,152,219}
\definecolor{secondarygreen}{RGB}{39,174,96}
\definecolor{accentorange}{RGB}{243,156,18}
\definecolor{alertred}{RGB}{231,76,60}
```

## Tips thuyết trình

### Thời gian chuẩn
- **7 phút:** Chọn 10 slides chính (bỏ backup)
- **10 phút:** Đầy đủ 16 slides
- **15 phút:** Thêm demo live hoặc Q&A

### Nguyên tắc thuyết trình
1. **Mỗi slide ≤ 1 phút** - Không dừng quá lâu
2. **Chỉ vào hình** - Đừng đọc text
3. **Claim → Evidence → Impact** - Luận điểm → Bằng chứng → Ý nghĩa

### 3 câu chốt cuối (phải thuộc lòng)
1. *"Đóng góp chính: Pipeline chuẩn hóa dữ liệu đa schema"*
2. *"Random Forest giảm MMRE 34% so với COCOMO II baseline"*
3. *"Hệ thống đã deploy API, có roadmap mở rộng thực tế"*

## Cấu trúc thư mục

```
presentation/
├── academic_presentation.tex    # File LaTeX chính
├── academic_presentation.pdf    # PDF output (sau khi compile)
├── generate_figures.py          # Script tạo hình
├── figures/                     # Thư mục chứa hình
│   ├── fig1_problem_illustration.pdf
│   ├── fig2_data_heterogeneity.pdf
│   ├── ...
│   └── fig10_cocomo_formula.pdf
└── README.md                    # File này
```

## Dependencies

### Python (để tạo hình)
```bash
pip install matplotlib seaborn numpy pandas scipy scikit-learn
```

### LaTeX (để compile)
```bash
# Ubuntu/Debian
sudo apt-get install texlive-full

# macOS
brew install --cask mactex

# Hoặc dùng Overleaf online
```

## Lưu ý quan trọng

### Để "ăn giải"
1. ✅ **Có insight sâu** - Slide 11, 12, 15 (error analysis + limitations)
2. ✅ **Số liệu thuyết phục** - Slide 9, 10 (metrics + comparison)
3. ✅ **Ứng dụng thực tế** - Slide 13, 14 (deployment + use cases)
4. ✅ **Trung thực** - Slide 15 (honest về limitations)

### Checklist trước khi trình bày
- [ ] Chạy lại `generate_figures.py` với dữ liệu thực tế
- [ ] Cập nhật số liệu trong slides 9-12
- [ ] Thay thông tin cá nhân (tên, email, trường)
- [ ] Test compile LaTeX không lỗi
- [ ] In thử 1 slide để check font size
- [ ] Luyện nói với đồng hồ bấm giờ

## Tài liệu tham khảo

Tất cả references đã được include trong slide cuối:
- Boehm (2000) - COCOMO II
- Conte (1986) - Industry metrics
- Wen (2012) - ML-based estimation
- Jørgensen (2007) - Systematic review

## Liên hệ

Nếu cần hỗ trợ thêm về:
- Chỉnh sửa LaTeX: xem documentation LaTeX Beamer
- Tạo hình: xem comments trong `generate_figures.py`
- Dữ liệu thực tế: chạy lại các script training trong `src/models/`

---

**Good luck với presentation! 🎓🏆**
