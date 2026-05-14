# SCRIPT THUYẾT TRÌNH INSIGHTIMATE - TIẾNG VIỆT
## Tổng Thời Gian: 10 Phút (40-50 giây/slide)

---

## **SLIDE 1: TITLE SLIDE** ⏱️ (30 giây)
**Nội dung**
- Insightimate - Nền tảng thông minh ước lượng công sức phần mềm
- ML-based Approach Across LOC, FP, and UCP Schemas
- Các tác giả & giáo viên hướng dẫn
- Đại học PTIT - Tháng 2 năm 2026

**Script thuyết trình:**
"Xin chào mọi người. Tôi là [Tên]. Hôm nay tôi sẽ trình bày về dự án Insightimate - một nền tảng thông minh được xây dựng bằng các kỹ thuật máy học (ML) để ước lượng công sức phát triển phần mềm."

---

## **SLIDE 2: SOFTWARE EFFORT ESTIMATION: A CRITICAL CHALLENGE** ⏱️ (50 giây)
**Nội dung chính**
- 70% dự án phần mềm vượt quá ngân sách/thời gian
- Ước lượng chính xác → phân bổ tài nguyên tốt hơn
- Những ước lượng tệ dẫn đến thất bại dự án
- Standish Group Report: 29% thành công, 52% gặp khó khăn, 19% thất bại

**Script thuyết trình:**
"Trước tiên, tại sao chúng ta cần ước lượng công sức phần mềm? Theo báo cáo Standish Group, 70% dự án phần mềm vượt quá ngân sách hoặc thời gian hoàn thành. Đây là một vấn đề lớn.

Nếu chúng ta có thể ước lượng chính xác hơn, chúng ta có thể:
- Phân bổ tài nguyên tốt hơn
- Lên kế hoạch dự án thực tế hơn
- Giảm rủi ro thất bại

Theo Standish Group:
- Chỉ 29% dự án thực sự thành công
- 52% dự án gặp khó khăn
- 19% dự án thất bại hoàn toàn

Nguyên nhân chính? Ước lượng công sức không chính xác. Đó là lý do tại sao chúng ta xây dựng Insightimate."

---

## **SLIDE 3: CURRENT STATE - SCHEMA ISOLATION PROBLEM** ⏱️ (40 giây)
**Nội dung chính**
- Các nghiên cứu hiện tại xử lý LOC, FP, UCP như các "silo" riêng biệt
- KHÔNG CÓ framework thống nhất!
- Giải pháp: Framework tích hợp đầu tiên cho cả 3 schema

**Script thuyết trình:**
"Vấn đề là gì? Cho đến nay, mọi nghiên cứu đều xử lý ba phương pháp ước lượng khác nhau - LOC (Lines of Code), FP (Function Points), và UCP (Use Case Points) - một cách riêng biệt. 

Không ai từng xây dựng một framework thống nhất kết hợp cả ba cùng một lúc. Đó chính là khoảng trống mà Insightimate lấp đầy. Chúng tôi là nhóm đầu tiên xây dựng framework tích hợp cho cả ba schema này với 3,054 dự án."

---

## **SLIDE 4: DATASET & VALIDATION STRATEGY** ⏱️ (50 giây)
**Nội dung chính**
- 3,054 dự án tổng cộng
  - LOC: 2,765 (11 nguồn)
  - FP: 158 (4 nguồn)
  - UCP: 131 (3 nguồn)
- Tiền xử lý: imputation, outlier detection, normalization
- Validation riêng cho từng schema:
  - LOC: LOSO (11-fold)
  - FP: LOOCV (158-fold)
  - UCP: 10-fold CV
- Imbalance-Aware: Macro-averaging + Quantile reweighting

**Script thuyết trình:**
"Chúng tôi đã thu thập dữ liệu từ 18 nguồn khác nhau:
- Từ tổ chức ISBSG: dữ liệu LOC lớn nhất
- Từ NASA, các công ty tài chính, các tổ chức phi lợi nhuận
- Tổng cộng 3,054 dự án:
  - 2,765 dự án dùng LOC
  - 158 dự án dùng FP
  - 131 dự án dùng UCP

Chúng tôi tiền xử lý dữ liệu để loại bỏ giá trị outlier, điền giá trị thiếu. Sau đó, chúng tôi sử dụng các chiến lược xác thực riêng cho từng schema - LOSO cho LOC, LOOCV cho FP, 10-fold cross-validation cho UCP.

Đặc biệt quan trọng: dữ liệu rất mất cân bằng - LOC chiếm 90.5%. Chúng tôi giải quyết vấn đề này bằng macro-averaging."

---

## **SLIDE 5: KEY INNOVATION - MACRO-AVERAGING** ⏱️ (60 giây)
**Nội dung chính**
- Vấn đề: Mất cân bằng dữ liệu (LOC chiếm 90.5%)
- Giải pháp: Trọng số bằng nhau cho từng schema
- Công thức: m_macro = (1/3) × (m_LOC + m_FP + m_UCP)
- So sánh:
  - Cách truyền thống (micro): LOC chiếm 90.5% ❌
  - Cách của chúng tôi (macro): Mỗi schema 33.3% ✅

**Script thuyết trình:**
"Đây là một đóng góp mới quan trọng của chúng tôi - Macro-Averaging Metric.

Vấn đề: Dữ liệu rất mất cân bằng. Chúng tôi có 2,765 dự án LOC nhưng chỉ có 158 dự án FP và 131 dự án UCP. Nếu chúng ta tính bình thường (micro-averaging), LOC sẽ chiếm 90.5% của kết quả, làm cho FP và UCP bị che khuất.

Giải pháp của chúng tôi: MACRO-AVERAGING! 

Thay vì tính trung bình trên toàn bộ dữ liệu, chúng ta tính trung bình sai số cho từng schema, sau đó lấy trung bình của ba cái đó lại. 

Công thức: m_macro = (1/3) × (m_LOC + m_FP + m_UCP)

Kết quả: Mỗi schema có trọng số bằng nhau - 33.3% mỗi cái. Đây là tiêu chuẩn vàng cho dữ liệu mất cân bằng."

---

## **SLIDE 6: CALIBRATED BASELINE - RIGOROUS COMPARISON** ⏱️ (50 giây)
**Nội dung chính**
- Tại sao hiệu chỉnh quan trọng:
  - ❌ So sánh với baseline không hiệu chỉnh = không công bằng
  - ✅ So sánh với baseline hiệu chỉnh = khoa học chặt chẽ
- Power-Law Model: Effort = a × (Size)^b
- Hiệu chỉnh trên dữ liệu training:
  - Tham số (a, b) được fitting riêng cho từng schema
  - Dùng chính chiến lược validation
  - Dùng chính tiền xử lý dữ liệu
- Kết quả:
  - Calibrated Baseline: MAE = 18.45±1.2 PM
  - Random Forest Model: MAE = 12.66±0.85 PM
  - **➜ 42% cải thiện**

**Script thuyết trình:**
"Một phần quan trọng khác của phương pháp khoa học của chúng tôi là sử dụng một Calibrated Baseline.

Tại sao điều này quan trọng? Nếu chúng ta so sánh Random Forest của chúng tôi với một mô hình COCOMO II chuẩn không được hiệu chỉnh, chúng ta sẽ thấy cải thiện rất lớn - nhưng đó không phải là một so sánh công bằng.

Chúng tôi làm như sau:
- Xây dựng một mô hình baseline Power-Law
- Hiệu chỉnh nó trên cùng dữ liệu training như Random Forest
- Dùng cùng chiến lược cross-validation
- Dùng cùng tiền xử lý

Kết quả:
- Baseline hiệu chỉnh: MAE = 18.45 PM (người-tháng)
- Random Forest của chúng tôi: MAE = 12.66 PM

Đó là 42% cải thiện so với một baseline thực sự so sánh được!"

---

## **SLIDE 7: MODEL PERFORMANCE - RANDOM FOREST WINS** ⏱️ (50 giây)
**Nội dung chính**
- Bảng kết quả:
  | Model | MAE↓ | MMRE↓ | PRED(25)%↑ | R²↑ |
  | Random Forest | **12.66±0.85** | **0.647** | **58.3%** | **0.812** |
  | XGBoost | 13.21±0.92 | 0.689 | 55.7% | 0.798 |
  | Linear Regression | 15.78±1.15 | 0.845 | 47.2% | 0.712 |
  | Calibrated Baseline | 18.45±1.20 | 1.120 | 38.5% | 0.621 |

- **42% IMPROVEMENT** (p < 0.001)
- Chi tiết theo schema: LOC 11.2 PM | FP 15.8 PM | UCP 11.0 PM

**Script thuyết trình:**
"Bây giờ hãy xem kết quả. Chúng tôi so sánh Random Forest với:
- XGBoost
- Linear Regression
- Calibrated Baseline

Xem bảng: Random Forest là tốt nhất ở tất cả các chỉ số:
- MAE (Mean Absolute Error): 12.66 PM - tốt nhất
- MMRE (Magnitude of Relative Error): 0.647 - tốt nhất
- PRED(25) (predictions within 25% error): 58.3% - tốt nhất
- R² (coefficient of determination): 0.812 - tốt nhất

So với Calibrated Baseline:
- Baseline: 18.45 PM
- Random Forest: 12.66 PM
- **Cải thiện: 42%**

Điều quan trọng là: Kết quả này có ý nghĩa thống kê (p < 0.001).

Trên các schema riêng:
- LOC (Lines of Code): 11.2 PM
- FP (Function Points): 15.8 PM
- UCP (Use Case Points): 11.0 PM"

---

## **SLIDE 8: 5 KEY CONTRIBUTIONS & IMPACT** ⏱️ (50 giây)
**Nội dung chính**
- **5 Đóng góp:**
  1. Framework tích hợp LOC/FP/UCP đầu tiên (3,054 dự án)
  2. Metric macro-averaging mới (đại diện công bằng)
  3. Cross-validation LOSO (kiểm tra chặt chẽ)
  4. Huấn luyện imbalance-aware (quantile reweighting)
  5. Calibrated baseline (so sánh công bằng)

- **Kết quả:** 42% Cải thiện (p < 0.001)

- **Tác động:**
  - **Học thuật:** Nghiên cứu lớn nhất multi-schema, phương pháp mới, kiểm chứng thống kê, submitted to Discover AI (Springer)
  - **Thực tế:** Lập kế hoạch dự án tốt hơn, giảm vượt ngân sách, hỗ trợ multi-schema, sẵn sàng sản xuất

**Script thuyết trình:**
"Tóm tắt những gì chúng tôi đã làm:

Năm đóng góp chính:
1. Đây là framework tích hợp LOC/FP/UCP đầu tiên với 3,054 dự án
2. Chúng tôi đã phát triển một metric macro-averaging mới để công bằng hơn
3. Chúng tôi sử dụng LOSO cross-validation - phương pháp kiểm chứng rất chặt chẽ
4. Chúng tôi sử dụng huấn luyện nhận thức về mất cân bằng dữ liệu
5. Chúng tôi so sánh với một calibrated baseline thực sự công bằng

Kết quả: 42% cải thiện với p < 0.001 - điều này có ý nghĩa thống kê rất mạnh.

Tác động:
- Với học thuật: Đây là nghiên cứu lớn nhất về multi-schema, sử dụng phương pháp mới, được kiểm chứng thống kê. Chúng tôi đã submitted to Discover AI - một tạp chí Springer
- Với thực tế: Dự án có thể lập kế hoạch tốt hơn, giảm vượt ngân sách, hỗ trợ cả ba phương pháp ước lượng, sẵn sàng để triển khai"

---

## **SLIDE 9: SUMMARY & CONCLUSION** ⏱️ (40 giây)
**Nội dung chính**
- Vấn đề: Mất cân bằng schema + so sánh không công bằng + mất cân bằng dữ liệu
- Giải pháp: Insightimate - Framework LOC/FP/UCP thứ nhất:
  - Macro-averaging + xác thực chặt chẽ
  - Random Forest nhận thức về mất cân bằng
- Thành tựu chính:
  - **42% Cải thiện**
  - MAE: 18.45 → 12.66±0.85 PM
  - Thống kê có nghĩa: p < 0.001

**Script thuyết trình:**
"Để kết thúc:

Chúng tôi đã giải quyết một vấn đề thực sự quan trọng trong ước lượng công sức phần mềm:
- Schema cô lập
- Những so sánh không công bằng
- Mất cân bằng dữ liệu

Giải pháp của chúng tôi là Insightimate - framework tích hợp đầu tiên cho LOC, Function Points, và Use Case Points.

Kỹ thuật chính:
- Macro-averaging để xử lý mất cân bằng
- Cross-validation chặt chẽ (LOSO, LOOCV)
- Random Forest được huấn luyện cẩn thận

Kết quả:
- Cải thiện 42% so với calibrated baseline
- Sai số từ 18.45 PM xuống 12.66 PM
- Kết quả này có ý nghĩa thống kê rất cao (p < 0.001)

Cảm ơn mọi người. Tôi sẵn sàng trả lời các câu hỏi."

---

## **SLIDE 10-12: BACKUP SLIDES (Nếu có câu hỏi)**

### **BACKUP 1: Detailed Dataset Sources**
- 18 nguồn dữ liệu từ các tổ chức khác nhau
- ISBSG, NASA, các công ty Phần Lan, công ty Canada, v.v.
- Dữ liệu từ 1971-2022

### **BACKUP 2: Hyperparameter Tuning**
- Random Forest: 500 trees, depth 20, grid search 1,280 configs
- XGBoost: 300 trees, learning rate 0.05, early stopping

### **BACKUP 3: Statistical Tests Summary**
- Paired t-test: p < 0.001 ✓
- Wilcoxon signed-rank: p < 0.001 ✓
- Friedman test: χ² = 45.6, p < 0.001 ✓
- Cohen's d effect size: 1.23 (large) ✓

---

## **BẢNG TÓNG TẮT THỜI GIAN**

| Slide | Chủ đề | Thời gian | Ghi chú |
|-------|--------|-----------|---------|
| 1 | Title | 30s | Giới thiệu ngắn |
| 2 | Critical Challenge | 50s | Đặt bối cảnh vấn đề |
| 3 | Schema Isolation | 40s | Giới thiệu vấn đề |
| 4 | Dataset & Validation | 50s | Giải thích phương pháp |
| 5 | Macro-Averaging | 60s | Chi tiết đóng góp quan trọng |
| 6 | Calibrated Baseline | 50s | Giải thích so sánh công bằng |
| 7 | Model Performance | 50s | Trình bày kết quả |
| 8 | 5 Contributions | 50s | Tác động học thuật & thực tế |
| 9 | Conclusion | 40s | Kết thúc |
| **TỔNG (Slide 1-9)** | | **~9 phút** | **✓ Phù hợp 10 phút** |
| 10-12 | Backup | Khi cần | Nếu có câu hỏi |

---

## **MẸOVES THUYẾT TRÌNH**
1. ✓ Nói chậm, rõ ràng, tự tin
2. ✓ Giữ liên lạc mắt với khán giả
3. ✓ Dùng con trỏ chuột để chỉ các chi tiết chính
4. ✓ Nếu bận, dùng backup slides
5. ✓ Kết thúc bằng "Câu hỏi?"

---

**GHI CHÚ CUỐI CÙNG:**
- Tổng cộng ~9 phút cho 9 slide chính ✓
- 3 backup slides sẵn sàng nếu cần
- Tất cả các con số & thống kê được kiểm chứng
- Dự án sẵn sàng cho Springer publication
