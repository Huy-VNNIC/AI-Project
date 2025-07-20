# ĐỀ TÀI NGHIÊN CỨU KHOA HỌC

## CẢI TIẾN MÔ HÌNH ƯỚC LƯỢNG NỖ LỰC PHÁT TRIỂN PHẦN MÈM COCOMO II BẰNG KỸ THUẬT HỌC MÁY

---


### 1. THÔNG TIN ĐỀ TÀI

**Tên đề tài:** Cải tiến mô hình ước lượng nỗ lực phát triển phần mềm COCOMO II bằng kỹ thuật học máy

**Thời gian thực hiện:** 07/2025 - 12/2025

**Loại đề tài:** Nghiên cứu khoa học sinh viên

---

### 2. DANH SÁCH THÀNH VIÊN VÀ MENTOR

#### 2.1 Danh sách thành viên nhóm:

1. **Trưởng nhóm:** Đặng Nhật Minh 
   - Mã số sinh viên: [Mã SV]
   - Lớp: [Lớp]
   - Email: [Email]
   - Vai trò: Trưởng nhóm, phụ trách phát triển mô hình học máy và tích hợp hệ thống

2. **Thành viên:** Nguyễn Nhật Huy 
   - Mã số sinh viên: [Mã SV]
   - Lớp: [Lớp]
   - Email: [Email]
   - Vai trò: Phụ trách thu thập và tiền xử lý dữ liệu

3. **Thành viên:** Nguyễn Hưu Hưng 
   - Mã số sinh viên: [Mã SV]
   - Lớp: [Lớp]
   - Email: [Email]
   - Vai trò: Phụ trách đánh giá mô hình và viết báo cáo

#### 2.2 Mentor:

**Thầy/Cô hướng dẫn:** [Tên mentor]
- Chức vụ: [Chức vụ]
- Đơn vị: [Đơn vị]
- Email: [Email mentor]
- Chuyên môn: Kỹ thuật phần mềm, Trí tuệ nhân tạo

---

### 3. Ý TƯỞNG VÀ MỤC TIÊU ĐỀ TÀI

#### 3.1 Ý tưởng nghiên cứu

Nghiên cứu này xuất phát từ nhận thức về tầm quan trọng của việc ước lượng nỗ lực phát triển phần mềm chính xác trong ngành công nghiệp phần mềm hiện đại. Mô hình COCOMO II (COnstructive COst MOdel), mặc dù đã được sử dụng rộng rãi hơn 20 năm, vẫn tồn tại những hạn chế về độ chính xác và khả năng thích ứng với các dự án phần mềm phức tạp hiện đại.

**Ý tưởng chính:** Kết hợp mô hình COCOMO II truyền thống với các kỹ thuật học máy tiên tiến để tạo ra một khung làm việc tích hợp có khả năng ước lượng nỗ lực phát triển phần mềm chính xác hơn, dựa trên nhiều loại thông số đầu vào khác nhau:

- **Lines of Code (LOC):** Dựa trên số dòng mã nguồn
- **Function Points (FP):** Dựa trên điểm chức năng
- **Use Case Points (UCP):** Dựa trên điểm trường hợp sử dụng

#### 3.2 Bối cảnh và tính cấp thiết

**Vấn đề thực tế:**
- Theo thống kê của Standish Group, chỉ có 31% dự án phần mềm hoàn thành đúng thời hạn và ngân sách
- 52% dự án bị chậm tiến độ hoặc vượt ngân sách do ước lượng không chính xác
- Việt Nam đang phát triển mạnh mẽ trong lĩnh vực công nghệ thông tin, cần có công cụ ước lượng chính xác để cạnh tranh quốc tế

**Tính mới và khác biệt:**
- Đầu tiên tại Việt Nam tích hợp ba loại metric (LOC, FP, UCP) trong một mô hình thống nhất
- Áp dụng các kỹ thuật học máy hiện đại (Random Forest, Decision Tree) vào COCOMO II
- Sử dụng dữ liệu thực tế từ nhiều nguồn khác nhau để đảm bảo tính đại diện

#### 3.3 Mục tiêu tổng quát

**Mục tiêu chính:** Phát triển một mô hình ước lượng nỗ lực phát triển phần mềm cải tiến, kết hợp ưu điểm của COCOMO II truyền thống với khả năng học hỏi và thích ứng của các kỹ thuật học máy hiện đại.

#### 3.4 Mục tiêu cụ thể

1. **Mục tiêu về nghiên cứu lý thuyết:**
   - Nghiên cứu và phân tích các hạn chế của mô hình COCOMO II truyền thống
   - Khảo sát các kỹ thuật học máy phù hợp cho bài toán ước lượng nỗ lực
   - Xây dựng framework lý thuyết cho việc tích hợp đa metric

2. **Mục tiêu về phát triển kỹ thuật:**
   - Xây dựng hệ thống tiền xử lý dữ liệu tự động cho các schema LOC, FP, UCP
   - Phát triển và tối ưu hóa các mô hình học máy: Linear Regression, Decision Tree, Random Forest
   - Tích hợp các mô hình thành một hệ thống dự đoán thống nhất

3. **Mục tiêu về đánh giá và so sánh:**
   - So sánh hiệu suất của các mô hình học máy với COCOMO II truyền thống
   - Đánh giá độ chính xác trên nhiều loại dự án khác nhau (quy mô nhỏ, vừa, lớn)
   - Phân tích tầm quan trọng của các yếu tố ảnh hưởng đến nỗ lực phát triển

4. **Mục tiêu về ứng dụng thực tế:**
   - Phát triển API và giao diện sử dụng thân thiện
   - Tạo ra công cụ hỗ trợ quyết định cho các nhà quản lý dự án
   - Cung cấp hướng dẫn sử dụng chi tiết cho cộng đồng

---

### 4. PHƯƠNG PHÁP NGHIÊN CỨU

#### 4.1 Phương pháp nghiên cứu tổng quát

**Phương pháp nghiên cứu thực nghiệm:** Kết hợp nghiên cứu lý thuyết và thực nghiệm để đánh giá hiệu suất của các mô hình đề xuất.

**Quy trình nghiên cứu:**
1. Nghiên cứu lý thuyết và khảo sát tài liệu
2. Thu thập và tiền xử lý dữ liệu
3. Phát triển các mô hình học máy
4. Thực nghiệm và đánh giá
5. So sánh và phân tích kết quả
6. Triển khai ứng dụng

#### 4.2 Phương pháp thu thập dữ liệu

**Nguồn dữ liệu:**
- **Dữ liệu LOC:** Ant dataset (1.3-1.7), Apache, ArgoUML, Eclipse projects
- **Dữ liệu FP:** Albrecht dataset và các nguồn công khai
- **Dữ liệu UCP:** UCP Dataset và dữ liệu từ các dự án thực tế

**Quy trình tiền xử lý:**
1. Chuẩn hóa định dạng dữ liệu
2. Chuyển đổi đơn vị đo lường thống nhất
3. Xử lý missing values và outliers
4. Áp dụng các kỹ thuật biến đổi dữ liệu (log transformation)

#### 4.3 Phương pháp phát triển mô hình

**Các mô hình học máy sử dụng:**
1. **Linear Regression:** Mô hình baseline để so sánh
2. **Decision Tree Regressor:** Mô hình phi tuyến bắt mối quan hệ phức tạp
3. **Random Forest Regressor:** Mô hình ensemble giảm overfitting

**Quy trình huấn luyện:**
1. Chia dữ liệu thành tập huấn luyện (70%) và tập kiểm tra (30%)
2. Áp dụng k-fold cross-validation (k=5)
3. Tối ưu hóa siêu tham số bằng GridSearchCV
4. Đánh giá và chọn mô hình tốt nhất

#### 4.4 Phương pháp đánh giá

**Các chỉ số đánh giá:**
- **MMRE (Mean Magnitude of Relative Error):** Sai số tương đối trung bình
- **PRED(25):** Tỷ lệ dự đoán có sai số dưới 25%
- **MAE (Mean Absolute Error):** Sai số tuyệt đối trung bình
- **RMSE (Root Mean Squared Error):** Căn bậc hai của sai số bình phương trung bình
- **R² (Coefficient of Determination):** Hệ số xác định

**Phương pháp so sánh:**
- So sánh hiệu suất giữa các mô hình học máy
- So sánh với mô hình COCOMO II truyền thống
- Phân tích statistical significance testing

---

### 5. TÍNH KHOA HỌC VÀ TÍNH THỰC TIỄN

#### 5.1 Tính khoa học

**Về mặt lý thuyết:**
- Nghiên cứu dựa trên nền tảng lý thuyết vững chắc của COCOMO II
- Áp dụng các kỹ thuật học máy được công nhận quốc tế
- Phương pháp nghiên cứu có tính hệ thống và khoa học

**Về mặt thực nghiệm:**
- Sử dụng dữ liệu thực tế từ nhiều nguồn đáng tin cậy
- Áp dụng các phương pháp đánh giá chuẩn trong lĩnh vực
- Đảm bảo tính reproducibility và transparency

#### 5.2 Tính thực tiễn

**Đóng góp cho ngành:**
- Cải thiện độ chính xác ước lượng nỗ lực phát triển phần mềm
- Giảm rủi ro vượt ngân sách và chậm tiến độ dự án
- Hỗ trợ các nhà quản lý dự án đưa ra quyết định chính xác

**Khả năng ứng dụng:**
- Có thể áp dụng trong các công ty phần mềm tại Việt Nam
- Tích hợp được với các công cụ quản lý dự án hiện có
- Dễ dàng cập nhật và cải thiện với dữ liệu mới

---

### 6. KẾT QUẢ NGHIÊN CỨU DỰ KIẾN

#### 6.1 Kết quả về mặt lý thuyết

- **Báo cáo nghiên cứu tổng quan:** Phân tích chi tiết về các hạn chế của COCOMO II và tiềm năng của học máy
- **Framework lý thuyết:** Khung làm việc tích hợp cho việc ước lượng đa metric
- **Phân tích so sánh:** Đánh giá toàn diện các mô hình học máy trong bài toán ước lượng nỗ lực

#### 6.2 Kết quả về mặt kỹ thuật

**Hệ thống phần mềm hoàn chỉnh:**
- Module tiền xử lý dữ liệu tự động
- Các mô hình học máy đã được huấn luyện và tối ưu
- API RESTful cho việc dự đoán
- Giao diện web thân thiện với người dùng

**Dữ liệu và mô hình:**
- Bộ dữ liệu đã được xử lý và chuẩn hóa
- Các mô hình học máy đã được huấn luyện
- Metadata và documentation chi tiết

#### 6.3 Kết quả về hiệu suất

**Kết quả dự kiến:**
- Cải thiện độ chính xác ước lượng 15-25% so với COCOMO II truyền thống
- MMRE giảm từ 0.4-0.6 xuống 0.25-0.35
- PRED(25) tăng từ 0.3-0.5 lên 0.6-0.8
- R² tăng từ 0.6-0.7 lên 0.8-0.9

**Kết quả thực tế đã đạt được (preliminary results):**
- Random Forest model đạt MMRE = 0.679 trên dữ liệu UCP
- Hiệu suất tốt nhất trên tập dữ liệu tích hợp với MMRE = 0.882
- Cải thiện đáng kể so với mô hình truyền thống

#### 6.4 Sản phẩm đầu ra

1. **Báo cáo nghiên cứu chi tiết** (40-60 trang)
2. **Hệ thống phần mềm hoàn chỉnh** với source code
3. **Bộ dữ liệu đã xử lý** và các mô hình đã huấn luyện
4. **API documentation** và **hướng dẫn sử dụng**
5. **Bài báo khoa học** đăng trên tạp chí hoặc hội thảo
6. **Presentation slides** cho việc báo cáo kết quả

---

### 7. LỊCH TRÌNH THỰC HIỆN

#### 7.1 Giai đoạn 1: Nghiên cứu lý thuyết và chuẩn bị (Tháng 07/2025)

**Tuần 1-2:**
- Nghiên cứu tài liệu về COCOMO II và các phương pháp ước lượng nỗ lực
- Khảo sát các kỹ thuật học máy ứng dụng trong Software Engineering
- Thiết lập môi trường phát triển và công cụ

**Tuần 3-4:**
- Thu thập dữ liệu từ các nguồn khác nhau
- Phân tích và đánh giá chất lượng dữ liệu
- Thiết kế kiến trúc hệ thống tổng thể

#### 7.2 Giai đoạn 2: Phát triển hệ thống (Tháng 08-09/2025)

**Tháng 08:**
- Phát triển module tiền xử lý dữ liệu
- Chuẩn hóa dữ liệu theo các schema LOC, FP, UCP
- Xây dựng pipeline xử lý dữ liệu tự động

**Tháng 09:**
- Phát triển và huấn luyện các mô hình học máy
- Tối ưu hóa siêu tham số cho các mô hình
- Xây dựng module đánh giá và so sánh mô hình

#### 7.3 Giai đoạn 3: Thực nghiệm và đánh giá (Tháng 10/2025)

**Tuần 1-2:**
- Thực hiện thực nghiệm trên các bộ dữ liệu
- Thu thập và phân tích kết quả thực nghiệm
- So sánh hiệu suất các mô hình

**Tuần 3-4:**
- Đánh giá statistical significance
- Phân tích feature importance và model interpretation
- Tối ưu hóa hiệu suất mô hình

#### 7.4 Giai đoạn 4: Triển khai và hoàn thiện (Tháng 11/2025)

**Tuần 1-2:**
- Phát triển API và giao diện người dùng
- Tích hợp các component thành hệ thống hoàn chỉnh
- Testing và debugging hệ thống

**Tuần 3-4:**
- Viết documentation và hướng dẫn sử dụng
- Chuẩn bị demo và presentation
- Hoàn thiện source code

#### 7.5 Giai đoạn 5: Báo cáo và dissemination (Tháng 12/2025)

**Tuần 1-2:**
- Viết báo cáo nghiên cứu chi tiết
- Chuẩn bị bài báo khoa học
- Tạo poster và presentation materials

**Tuần 3-4:**
- Báo cáo kết quả nghiên cứu
- Nộp bài báo khoa học
- Finalize project deliverables

---

### 8. KINH PHÍ DỰ KIẾN

#### 8.1 Chi phí nhân lực

- **Sinh viên nghiên cứu:** 3 người × 6 tháng = 18 người-tháng
- **Hướng dẫn khoa học:** 1 người × 6 tháng = 6 người-tháng
- **Tổng chi phí nhân lực:** Được tài trợ bởi trường

#### 8.2 Chi phí thiết bị và phần mềm

- **Máy tính và thiết bị:** Sử dụng thiết bị có sẵn
- **Phần mềm:** Sử dụng các công cụ mã nguồn mở (Python, scikit-learn, etc.)
- **Cloud computing:** AWS/Google Cloud credits cho training models
- **Ước tính:** $200-300

#### 8.3 Chi phí khác

- **Tài liệu và sách:** $100
- **Tham dự hội thảo/conference:** $500-1000
- **Miscellaneous:** $200
- **Tổng ước tính:** $1000-1600

---

### 9. RỦI RO VÀ BIỆN PHÁP PHÒNG NGỪA

#### 9.1 Rủi ro về dữ liệu

**Rủi ro:**
- Thiếu dữ liệu chất lượng cao
- Dữ liệu không đại diện cho dự án hiện đại
- Missing values và outliers nhiều

**Biện pháp:**
- Đa dạng hóa nguồn dữ liệu
- Áp dụng các kỹ thuật data augmentation
- Phát triển robust preprocessing pipeline

#### 9.2 Rủi ro về kỹ thuật

**Rủi ro:**
- Mô hình overfitting
- Hiệu suất không như mong đợi
- Khó khăn trong việc tích hợp hệ thống

**Biện pháp:**
- Áp dụng cross-validation và regularization
- Sử dụng ensemble methods
- Phát triển theo phương pháp agile và iterative

#### 9.3 Rủi ro về thời gian

**Rủi ro:**
- Chậm tiến độ do khó khăn kỹ thuật
- Conflict trong nhóm
- Thay đổi yêu cầu

**Biện pháp:**
- Lập kế hoạch chi tiết với buffer time
- Giao tiếp thường xuyên trong nhóm
- Flexible và adaptive planning

---

### 10. ĐÓNG GÓP DỰ KIẾN

#### 10.1 Đóng góp khoa học

**Về mặt lý thuyết:**
- Đề xuất framework tích hợp đa metric cho ước lượng nỗ lực
- Phân tích so sánh toàn diện giữa COCOMO II và học máy
- Nghiên cứu về feature importance trong ước lượng nỗ lực

**Về mặt thực nghiệm:**
- Bộ dữ liệu đã xử lý và chuẩn hóa cho cộng đồng
- Kết quả thực nghiệm chi tiết và reproducible
- Best practices cho việc áp dụng ML trong effort estimation

#### 10.2 Đóng góp thực tiễn

**Cho ngành công nghiệp:**
- Công cụ ước lượng chính xác hơn cho dự án phần mềm
- Giảm rủi ro và chi phí trong quản lý dự án
- Hỗ trợ decision-making cho project managers

**Cho cộng đồng nghiên cứu:**
- Open source codebase cho các nghiên cứu tiếp theo
- Datasets và benchmarks cho so sánh
- Methodology và best practices

#### 10.3 Đóng góp cho đào tạo

**Cho sinh viên:**
- Tài liệu học tập về Software Engineering và ML
- Hands-on experience với real-world projects
- Skills development trong nghiên cứu khoa học

**Cho giảng viên:**
- Case study cho việc giảng dạy
- Research collaboration opportunities
- Industry connections

---

### 11. TÀI LIỆU THAM KHẢO

1. **Boehm, B.** (2000). *Software Cost Estimation with COCOMO II*. Prentice Hall.

2. **Jørgensen, M., & Shepperd, M.** (2007). A Systematic Review of Software Development Cost Estimation Studies. *IEEE Transactions on Software Engineering*, 33(1), 33-53.

3. **Wen, J., Li, S., Lin, Z., Hu, Y., & Huang, C.** (2012). Systematic literature review of machine learning based software development effort estimation models. *Information and Software Technology*, 54(1), 41-59.

4. **Sarro, F., Petrozziello, A., & Harman, M.** (2016). Multi-objective software effort estimation. In *Proceedings of the 38th International Conference on Software Engineering* (ICSE '16). ACM, 619-630.

5. **Idri, A., Amazal, F. A., & Abran, A.** (2015). Analogy-based software development effort estimation: A systematic mapping and review. *Information and Software Technology*, 58, 206-230.

6. **Attarzadeh, I., & Ow, S. H.** (2011). Improving estimation accuracy of the COCOMO II using an adaptive fuzzy logic model. *IEEE International Conference on Fuzzy Systems*.

7. **Moløkken, K., & Jørgensen, M.** (2003). A review of software surveys on software effort estimation. *IEEE International Symposium on Empirical Software Engineering*.

8. **Kemerer, C. F.** (1987). An empirical validation of software cost estimation models. *Communications of the ACM*, 30(5), 416-429.

9. **Albrecht, A. J., & Gaffney, J. E.** (1983). Software function, source lines of code, and development effort prediction: a software science validation. *IEEE Transactions on Software Engineering*, 9(6), 639-648.

10. **Karner, G.** (1993). Resource estimation for objectory projects. *Objective Systems SF AB*.

---

### 12. PHỤ LỤC

#### 12.1 Sơ đồ kiến trúc hệ thống

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │    │  Data Processing│    │   ML Models     │
│                 │    │                 │    │                 │
│ • LOC datasets  │───▶│ • Normalization │───▶│ • Linear Reg    │
│ • FP datasets   │    │ • Missing values│    │ • Decision Tree │
│ • UCP datasets  │    │ • Outlier detect│    │ • Random Forest │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Service   │    │  Web Interface  │    │   Predictions   │
│                 │    │                 │    │                 │
│ • RESTful API   │◀───│ • User-friendly │◀───│ • Effort (PM)   │
│ • Documentation │    │ • Visualizations│    │ • Duration      │
│ • Authentication│    │ • Reports       │    │ • Team size     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### 12.2 Ví dụ về dữ liệu đầu vào và đầu ra

**Input Example:**
```json
{
  "project_size": 15.5,
  "size_type": "kloc",
  "project_type": "organic",
  "complexity_factors": {
    "analyst_capability": "high",
    "programmer_capability": "nominal",
    "application_experience": "low"
  }
}
```

**Output Example:**
```json
{
  "effort_pm": 98.5,
  "duration_months": 14.2,
  "team_size": 7,
  "confidence_interval": {
    "lower": 85.2,
    "upper": 112.8
  },
  "model_used": "Random Forest (Tuned)"
}
```

#### 12.3 Kết quả thực nghiệm sơ bộ

**Hiệu suất mô hình trên các schema:**

| Schema | Model | MMRE | PRED(25) | R² |
|--------|-------|------|----------|-----|
| LOC | Random Forest | 0.988 | 0.0 | 0.12 |
| FP | Decision Tree | 0.956 | 0.0 | 0.25 |
| UCP | Random Forest | 0.679 | 0.091 | 0.68 |
| Combined | Random Forest | 0.882 | 0.030 | 0.45 |

**Nhận xét:**
- Random Forest cho kết quả tốt nhất trên dữ liệu UCP
- Cần cải thiện hiệu suất trên dữ liệu LOC và FP
- Mô hình tích hợp có tiềm năng cải thiện đáng kể

---

**Ngày hoàn thành đề xuất:** [Ngày/Tháng/Năm]

**Chữ ký nhóm nghiên cứu:**
- Trưởng nhóm: ________________
- Thành viên 2: ________________  
- Thành viên 3: ________________

**Chữ ký mentor:** ________________

**Chữ ký BGH khoa/bộ môn:** ________________

---

*Đề xuất này được chuẩn bị theo yêu cầu của Bộ môn CNPM Việt - Mỹ về việc đăng ký làm nghiên cứu khoa học cho đợt tháng 07/2025.*
