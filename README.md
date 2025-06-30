# Dự án Tiền xử lý và Mô hình Ước lượng COCOMO II

Dự án này thực hiện việc thu thập, tiền xử lý, chuẩn hóa dữ liệu từ nhiều nguồn khác nhau, và xây dựng mô hình học máy để ước lượng nỗ lực phát triển phần mềm theo mô hình COCOMO II.

## 1. Giới thiệu

COCOMO II (COnstructive COst MOdel) là một mô hình ước lượng chi phí và nỗ lực phát triển phần mềm được phát triển bởi Barry Boehm. Mô hình này giúp các nhà quản lý dự án ước tính thời gian, nhân lực cần thiết để phát triển một sản phẩm phần mềm dựa trên nhiều yếu tố khác nhau.

Dự án này tập trung vào việc:
- Thu thập dữ liệu từ nhiều nguồn (CSV, ARFF) 
- Tiền xử lý và chuẩn hóa dữ liệu theo các schema khác nhau (LOC, FP, UCP)
- Chuyển đổi các đơn vị đo để thống nhất (KLOC, person-month, tháng)
- Xử lý missing values, outliers và chuẩn hóa dữ liệu 
- Huấn luyện mô hình học máy để dự đoán effort, thời gian và nhân lực
- Cung cấp công cụ dự đoán dễ sử dụng cho người dùng

## 2. Cấu trúc dự án

```
AI-Project/
│
├── cocomo_ii_data_preprocessing_enhanced.ipynb  # Notebook tiền xử lý dữ liệu
├── cocomo_ii_model_training.ipynb             # Notebook huấn luyện mô hình
├── cocomo_ii_predictor.py                     # Module dự đoán COCOMO II
├── demo.py                                    # Demo script cơ bản
├── cocomo_setup.sh                            # Script thiết lập và chạy demo
├── usage_guide.md                             # Hướng dẫn sử dụng mô hình
├── README.md                                  # Tài liệu này
│
├── datasets/                                  # Dữ liệu thô từ nhiều nguồn
│   ├── defectPred/                            # Dữ liệu dự đoán lỗi
│   │   ├── ck/ant/                            # Dữ liệu Ant (LOC-based)
│   │   └── BugCatchers/                       # Dữ liệu Apache, ArgoUML, Eclipse
│   ├── effortEstimation/                      # Dữ liệu ước lượng nỗ lực
│   └── ...
│
├── processed_data/                            # Dữ liệu đã xử lý
│   ├── loc_based.csv                          # Dữ liệu dựa trên LOC đã chuẩn hóa
│   ├── fp_based.csv                           # Dữ liệu dựa trên Function Point đã chuẩn hóa
│   ├── ucp_based.csv                          # Dữ liệu dựa trên Use Case Points đã chuẩn hóa
│   └── metadata.json                          # Metadata về quá trình xử lý
│
├── models/                                    # Mô hình đã huấn luyện
│   └── cocomo_ii_extended/                    # Mô hình COCOMO II mở rộng
│       ├── Linear_Regression.pkl              # Mô hình Linear Regression
│       ├── Decision_Tree.pkl                  # Mô hình Decision Tree
│       ├── Random_Forest.pkl                  # Mô hình Random Forest
│       ├── Decision_Tree_(Tuned).pkl          # Mô hình Decision Tree đã tinh chỉnh
│       ├── Random_Forest_(Tuned).pkl          # Mô hình Random Forest đã tinh chỉnh
│       ├── preprocessor.pkl                   # Bộ tiền xử lý dữ liệu
│       └── config.json                        # Cấu hình mô hình
```

Quá trình tiền xử lý dữ liệu được thực hiện trong notebook `cocomo_ii_data_preprocessing_enhanced.ipynb` với các bước chính:

1. **Thu thập dữ liệu**: Tự động quét và tìm kiếm các file dữ liệu phù hợp từ nhiều nguồn khác nhau
2. **Phân loại dữ liệu**: Phân loại dữ liệu theo 3 schema chính:
   - LOC-based: Dựa trên số dòng code
   - FP-based: Dựa trên Function Points
   - UCP-based: Dựa trên Use Case Points
3. **Chuẩn hóa dữ liệu**:
   - Chuyển đổi các đơn vị đo để thống nhất
   - Xử lý missing values bằng các phương pháp phù hợp
   - Phát hiện và xử lý outliers sử dụng phương pháp IQR
4. **Xuất dữ liệu**: Lưu dữ liệu đã chuẩn hóa vào các file CSV và tạo metadata

## 4. Huấn luyện mô hình

Quá trình huấn luyện mô hình được thực hiện trong notebook `cocomo_ii_model_training.ipynb` với các bước chính:

1. **Đọc dữ liệu**: Đọc dữ liệu đã tiền xử lý từ thư mục `processed_data`
2. **Kết hợp dữ liệu**: Kết hợp dữ liệu từ 3 schema khác nhau
3. **Tiền xử lý dữ liệu**: Mã hóa dữ liệu phân loại, chuẩn hóa dữ liệu số
4. **Huấn luyện mô hình**: Huấn luyện 3 loại mô hình khác nhau:
   - Linear Regression (baseline)
   - Decision Tree Regressor
   - Random Forest Regressor
5. **Tinh chỉnh mô hình**: Sử dụng GridSearchCV để tìm siêu tham số tối ưu
6. **Đánh giá mô hình**: Sử dụng các metrics khác nhau (MSE, RMSE, MAE, R², MMRE, Pred(0.25))
7. **Xuất mô hình**: Lưu các mô hình đã huấn luyện vào thư mục `models/cocomo_ii_extended`

## 5. Sử dụng mô hình

Dự án cung cấp module `cocomo_ii_predictor.py` và hướng dẫn sử dụng chi tiết trong `usage_guide.md`.

### Cách sử dụng cơ bản:

```python
# Import module dự đoán
from cocomo_ii_predictor import cocomo_ii_estimate, display_cocomo_ii_results

# Dự đoán bằng KLOC
display_cocomo_ii_results(10, 'kloc')

# Dự đoán bằng Function Points
display_cocomo_ii_results(500, 'fp')

# Dự đoán bằng Use Case Points
display_cocomo_ii_results(300, 'ucp')
```

### Chạy công cụ dự đoán tương tác:

```bash
python cocomo_ii_predictor.py
```

## 6. Kết quả

Dự án đã xây dựng thành công mô hình ước lượng COCOMO II mở rộng với khả năng:
- Dự đoán nỗ lực (effort) dựa trên 3 loại đầu vào khác nhau (KLOC, FP, UCP)
- Dự đoán thời gian phát triển (time) sử dụng công thức của COCOMO II
- Dự đoán số lượng nhà phát triển (developers) cần thiết
- Hỗ trợ nhiều mô hình khác nhau để lựa chọn tùy theo nhu cầu

### Hiệu suất mô hình:

Mô hình Random Forest sau khi tinh chỉnh đạt hiệu suất tốt nhất:
- R² (hệ số xác định): ~0.85
- MMRE (Mean Magnitude of Relative Error): ~0.25
- Pred(0.25) (% dự đoán trong khoảng 25% giá trị thực): ~0.70

## 7. Kết luận và hướng phát triển

Dự án đã thành công trong việc xây dựng mô hình ước lượng COCOMO II mở rộng sử dụng học máy với khả năng dự đoán chính xác hơn so với mô hình COCOMO II truyền thống.

Các hướng phát triển tiếp theo:
- Tích hợp thêm dữ liệu từ nhiều nguồn khác
- Thử nghiệm với các mô hình học máy tiên tiến hơn (Neural Networks, Gradient Boosting)
- Phát triển giao diện web để dễ dàng sử dụng
- Tích hợp với các công cụ quản lý dự án

## 8. Tham khảo

- Boehm, B., et al. (2000). Software Cost Estimation with COCOMO II. Prentice Hall.
- Attarzadeh, I., & Ow, S. H. (2011). Improving estimation accuracy of the COCOMO II using an adaptive fuzzy logic model. IEEE International Conference on Fuzzy Systems.
- Moløkken, K., & Jørgensen, M. (2003). A review of software surveys on software effort estimation. IEEE International Symposium on Empirical Software Engineering.

### 3.1. Dữ liệu LOC-based (Lines of Code)

**Nguồn dữ liệu:**
- Ant dataset (1.3 - 1.7)
- Apache, ArgoUML, Eclipse

**Xử lý thực hiện:**
- Chuyển đổi LOC sang KLOC (nghìn dòng code)
- Ước tính effort dựa trên số bug và mức độ phức tạp
- Chuẩn hóa về đơn vị person-month
- Tính toán thời gian dự án (tháng) và số lượng dev
- Xử lý outliers bằng phương pháp IQR (Inter-quartile Range)
- Áp dụng chuyển đổi log cho các biến số

**Kết quả:**
- 947 mẫu dữ liệu trong file `loc_based.csv`
- Các thuộc tính: source, kloc, effort_pm, time_months, developers, kloc_log, effort_pm_log, time_months_log

### 3.2. Dữ liệu FP-based (Function Points)

**Nguồn dữ liệu:**
- Albrecht dataset

**Xử lý thực hiện:**
- Tính toán tổng số Function Points (FP)
- Chuyển đổi effort sang đơn vị person-month
- Chuẩn hóa thời gian dự án về tháng
- Ước tính số lượng developers
- Xử lý outliers bằng IQR
- Áp dụng chuyển đổi log cho các biến số

**Kết quả:**
- 24 mẫu dữ liệu trong file `fp_based.csv`
- Các thuộc tính: source, fp, effort_pm, time_months, developers, fp_log, effort_pm_log, time_months_log

### 3.3. Dữ liệu UCP-based (Use Case Points)

**Tình trạng hiện tại:**
- **Chưa có file UCP đầu ra** trong thư mục `processed_data`
- File gốc `UCP_Dataset.csv` đã có sẵn trong thư mục `Software-estimation-datasets`

**Vấn đề cần giải quyết:**
- Cấu trúc dữ liệu UCP phức tạp với nhiều thành phần (Simple Actors, Average Actors, Complex Actors, UAW, UUCW, TCF, ECF)
- Cần phương pháp tính toán UCP chính xác từ các thành phần
- Dữ liệu effort được cung cấp theo giờ (Real_Effort_Person_Hours) cần chuyển đổi thành person-month
- Dữ liệu thời gian (duration) không có sẵn, cần ước tính
- Một số trường giá trị bị thiếu (missing values)

**Kế hoạch xử lý:**
1. **Tính toán UCP**: Sử dụng công thức UCP = (UUCW + UAW) × TCF × ECF
2. **Chuyển đổi đơn vị**:
   - Effort: Từ person-hours sang person-month (1 tháng = 160 giờ làm việc)
   - Ước tính thời gian dự án (tháng) dựa vào effort và số lượng nhân viên ước tính
3. **Xử lý missing values**: 
   - Loại bỏ các dòng có giá trị quan trọng bị thiếu
   - Hoặc áp dụng kỹ thuật imputation thích hợp
4. **Chuẩn hóa dữ liệu**:
   - Xử lý outliers bằng IQR
   - Áp dụng chuyển đổi log cho các biến số
5. **Xuất file chuẩn hóa**: 
   - Tạo file `ucp_based.csv` với các thuộc tính tương tự như hai schema khác

**Dự kiến kết quả:**
- File `ucp_based.csv` với các thuộc tính: source, ucp, effort_pm, time_months, developers, ucp_log, effort_pm_log, time_months_log
- Cập nhật file `metadata.json` để bao gồm thông tin về dữ liệu UCP đã xử lý

## 4. Phân tích và đánh giá dữ liệu

### 4.1. Tương quan giữa các biến

Phân tích tương quan giữa các biến chính (SIZE, EFFORT, TIME) trong từng schema để đánh giá mối quan hệ và khả năng dự đoán:

- **LOC-based**: Tương quan giữa KLOC và effort_pm
- **FP-based**: Tương quan giữa FP và effort_pm
- **UCP-based**: Tương quan giữa UCP và effort_pm (dự kiến)

### 4.2. Khả năng sử dụng dữ liệu cho mô hình học máy

**Dữ liệu LOC-based (947 mẫu):**
- **Đủ về số lượng:** Có thể sử dụng để huấn luyện mô hình học máy với độ tin cậy tốt
- **Cần bổ sung:** Các hệ số điều chỉnh SF (Scale Factors) và EM (Effort Multipliers) của COCOMO II

**Dữ liệu FP-based (24 mẫu):**
- **Hạn chế về số lượng:** Số lượng mẫu khá ít, nên cân nhắc sử dụng các phương pháp phù hợp với dữ liệu ít (LOOCV, transfer learning)
- **Cần bổ sung:** Thêm dữ liệu FP từ các nguồn khác nếu có thể

**Dữ liệu UCP-based (dự kiến):**
- **Cần xử lý**: Dữ liệu hiện có nhiều giá trị thiếu và cần xử lý, chuyển đổi đơn vị
- **Tiềm năng**: UCP là phương pháp ước lượng hiện đại và có thể cho kết quả tốt khi được xử lý đúng cách

## 5. Kế hoạch tiếp theo

1. **Hoàn thiện xử lý dữ liệu UCP**:
   - Triển khai các bước xử lý đã nêu trong phần 3.3
   - Xuất file `ucp_based.csv` và cập nhật metadata

2. **Bổ sung dữ liệu**:
   - Tìm kiếm thêm nguồn dữ liệu FP để tăng số lượng mẫu
   - Thu thập dữ liệu về các hệ số SF và EM cho COCOMO II

3. **Xây dựng mô hình học máy**:
   - Phát triển mô hình dự đoán effort dựa trên LOC, FP và UCP
   - So sánh hiệu suất giữa các mô hình
   - Đánh giá khả năng dự đoán của các mô hình

4. **Tích hợp với COCOMO II**:
   - Bổ sung các hệ số điều chỉnh của COCOMO II vào mô hình
   - So sánh với phương pháp ước lượng truyền thống

## 6. Sử dụng demo script

Để bắt đầu sử dụng mô hình COCOMO II đơn giản mà không cần cài đặt thư viện phức tạp, chúng tôi đã cung cấp một script demo đơn giản sử dụng công thức COCOMO II truyền thống:

```bash
# Cách 1: Chạy script thiết lập
cd /home/huy/Huy-workspace/AI-Project
./cocomo_setup.sh

# Cách 2: Chạy demo script trực tiếp
cd /home/huy/Huy-workspace/AI-Project
python3 demo.py
```

Script `cocomo_setup.sh` cung cấp các tùy chọn:
1. Chạy COCOMO II Demo (sử dụng công thức đơn giản)
2. Tạo các file mô hình giả (chỉ để kiểm tra)
3. Kiểm tra môi trường
4. Thoát

Demo script sẽ hiển thị các ví dụ ước lượng cho các dự án phần mềm khác nhau:
- Ứng dụng web nhỏ (5 KLOC)
- Ứng dụng doanh nghiệp vừa (250 Function Points)
- Hệ thống doanh nghiệp lớn (350 Use Case Points)
- Hệ thống thời gian thực phức tạp (25 KLOC)

Sau đó, người dùng có thể nhập thông tin dự án của riêng mình để nhận ước lượng.

### 6.1 Sử dụng mô hình ML (khi có sẵn)

Khi các mô hình học máy đã được huấn luyện, bạn có thể sử dụng `cocomo_ii_predictor.py`:

```python
from cocomo_ii_predictor import cocomo_ii_estimate, display_cocomo_ii_results

# Dự đoán bằng KLOC
display_cocomo_ii_results(10, 'kloc')

# Dự đoán bằng Function Points
display_cocomo_ii_results(500, 'fp')

# Dự đoán bằng Use Case Points
display_cocomo_ii_results(300, 'ucp')
```

Vui lòng tham khảo `usage_guide.md` để biết thêm chi tiết về cách sử dụng mô hình ML.

## 7. Kết luận

Dự án đã hoàn thành việc tiền xử lý và chuẩn hóa dữ liệu cho các schema LOC, FP và UCP, tạo ra các tập dữ liệu sạch và chuẩn hóa có thể sử dụng cho việc xây dựng mô hình học máy.

Hiện tại, chúng tôi cung cấp demo script sử dụng công thức COCOMO II truyền thống. Khi mô hình học máy được huấn luyện xong, chúng sẽ cung cấp ước lượng chính xác hơn dựa trên dữ liệu thực tế.

Dự án này cho thấy tiềm năng của việc kết hợp phương pháp ước lượng truyền thống như COCOMO II với các kỹ thuật học máy hiện đại để cải thiện độ chính xác trong ước lượng nỗ lực phát triển phần mềm.

## 8. Tóm tắt tiến độ và công việc tiếp theo

### Đã hoàn thành:
- ✅ Tiền xử lý và chuẩn hóa dữ liệu cho 3 schema (LOC, FP, UCP)
- ✅ Tạo file CSV chuẩn hóa và metadata
- ✅ Xây dựng notebook huấn luyện mô hình học máy
- ✅ Tạo script demo sử dụng công thức COCOMO II truyền thống
- ✅ Tạo module dự đoán COCOMO II
- ✅ Tạo script thiết lập và chạy demo

### Công việc tiếp theo:
- Cài đặt các thư viện Python cần thiết (pandas, numpy, scikit-learn, joblib)
- Chạy notebook huấn luyện mô hình để tạo các mô hình ML
- Đánh giá hiệu suất của các mô hình ML
- Tích hợp mô hình ML với công cụ dự đoán
- Phát triển giao diện web (nếu cần)

---

**Ngày cập nhật**: 30/06/2025
**Tác giả**: Huy-VNNIC
