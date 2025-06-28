# Dự án Tiền xử lý và Chuẩn hóa Dữ liệu COCOMO II

Dự án này thực hiện việc thu thập, tiền xử lý và chuẩn hóa dữ liệu từ nhiều nguồn khác nhau để phục vụ cho việc xây dựng mô hình ước lượng nỗ lực phát triển phần mềm theo mô hình COCOMO II.

## 1. Giới thiệu

COCOMO II (COnstructive COst MOdel) là một mô hình ước lượng chi phí và nỗ lực phát triển phần mềm được phát triển bởi Barry Boehm. Mô hình này giúp các nhà quản lý dự án ước tính thời gian, nhân lực cần thiết để phát triển một sản phẩm phần mềm dựa trên nhiều yếu tố khác nhau.

Dự án này tập trung vào việc:
- Thu thập dữ liệu từ nhiều nguồn (CSV, ARFF) 
- Tiền xử lý và chuẩn hóa dữ liệu theo các schema khác nhau (LOC, FP, UCP)
- Chuyển đổi các đơn vị đo để thống nhất (KLOC, person-month, tháng)
- Xử lý missing values, outliers và chuẩn hóa dữ liệu 
- Xuất dữ liệu đã xử lý để phục vụ cho việc xây dựng mô hình ML

## 2. Cấu trúc dự án

```
AI-Project/
│
├── cocomo_ii_data_preprocessing.ipynb   # Notebook chính cho việc tiền xử lý dữ liệu
├── README.md                           # Tài liệu này
│
├── datasets/                           # Dữ liệu thô từ nhiều nguồn
│   ├── data_countries.csv
│   ├── defectPred/                     # Dữ liệu dự đoán lỗi
│   │   ├── ck/ant/                     # Dữ liệu Ant (LOC-based)
│   │   └── BugCatchers/                # Dữ liệu Apache, ArgoUML, Eclipse
│   ├── effortEstimation/
│   ├── other/
│   ├── sna/
│   ├── textMining/
│   └── timeSeries/
│
├── Software-estimation-datasets/       # Bộ dữ liệu ước lượng phần mềm khác
│   ├── albrecht.arff                   # Dữ liệu Albrecht (FP-based)
│   ├── COCOMO-81.csv                   # Dữ liệu COCOMO I gốc
│   ├── Desharnais.csv                  # Dữ liệu Desharnais
│   ├── UCP_Dataset.csv                 # Dữ liệu UCP (Use Case Points)
│   └── ...
│
├── processed_data/                     # Dữ liệu đã xử lý
│   ├── loc_based.csv                   # Dữ liệu dựa trên LOC đã chuẩn hóa
│   ├── fp_based.csv                    # Dữ liệu dựa trên Function Point đã chuẩn hóa
│   └── metadata.json                   # Metadata về quá trình xử lý
│
└── effort-estimation-by-using-pre-trained-model/  # Mô hình học máy được huấn luyện trước
```

## 3. Quá trình tiền xử lý dữ liệu

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

## 6. Kết luận

Dự án đã hoàn thành việc tiền xử lý và chuẩn hóa dữ liệu cho hai schema LOC và FP, tạo ra các tập dữ liệu sạch và chuẩn hóa có thể sử dụng cho việc xây dựng mô hình học máy. Tuy nhiên, dữ liệu UCP vẫn cần được xử lý thêm để có thể sử dụng hiệu quả.

Dữ liệu hiện tại đủ để bắt đầu xây dựng các mô hình ML cơ bản, nhưng cần được bổ sung thêm các hệ số điều chỉnh để có thể áp dụng đầy đủ phương pháp COCOMO II.

---

**Ngày cập nhật**: 28/06/2025  
**Tác giả**: Huy-VNNIC
