# Báo cáo so sánh các mô hình ước lượng nỗ lực phần mềm

## 1. Bảng so sánh các chỉ số

| Model             | Schema   |   MMRE vs COCOMO |   PRED(25) vs COCOMO | MMRE vs Actual   | PRED(25) vs Actual   | MAE      | RMSE     |
|:------------------|:---------|-----------------:|---------------------:|:-----------------|:---------------------|:---------|:---------|
| Linear_Regression | LOC      |           1.324  |               0.0909 | N/A              | N/A                  | N/A      | N/A      |
| Decision_Tree     | LOC      |           0.8557 |               0      | N/A              | N/A                  | N/A      | N/A      |
| Random_Forest     | LOC      |           0.8992 |               0      | N/A              | N/A                  | N/A      | N/A      |
| Gradient_Boosting | LOC      |           1.0479 |               0      | N/A              | N/A                  | N/A      | N/A      |
| Linear_Regression | FP       |          21.945  |               0.1818 | 4.4999           | 0.0000               | 107.5358 | 280.2682 |
| Decision_Tree     | FP       |           0.663  |               0.0909 | 1.3712           | 0.1728               | 18.6321  | 23.6230  |
| Random_Forest     | FP       |           0.7081 |               0      | 0.6473           | 0.3951               | 12.6558  | 20.0085  |
| Gradient_Boosting | FP       |           0.6085 |               0.0909 | 1.1008           | 0.1975               | 16.1608  | 21.0946  |
| Linear_Regression | UCP      |           4.7679 |               0      | N/A              | N/A                  | N/A      | N/A      |
| Decision_Tree     | UCP      |           1.5928 |               0      | N/A              | N/A                  | N/A      | N/A      |
| Random_Forest     | UCP      |           1.1412 |               0      | N/A              | N/A                  | N/A      | N/A      |
| Gradient_Boosting | UCP      |           2.2039 |               0      | N/A              | N/A                  | N/A      | N/A      |
| Linear_Regression | All      |           9.3456 |               0.0909 | 4.4999           | 0.0000               | 107.5358 | 280.2682 |
| Decision_Tree     | All      |           1.0371 |               0.0303 | 1.3712           | 0.1728               | 18.6321  | 23.6230  |
| Random_Forest     | All      |           0.9162 |               0      | 0.6473           | 0.3951               | 12.6558  | 20.0085  |
| Gradient_Boosting | All      |           1.2868 |               0.0303 | 1.1008           | 0.1975               | 16.1608  | 21.0946  |

## 2. Phân tích các mô hình

### COCOMO II Traditional

**Điểm mạnh:**

- Đơn giản, dễ triển khai
- Không yêu cầu dữ liệu huấn luyện
- Dựa trên nền tảng nghiên cứu lâu năm

**Điểm yếu:**

- Độ chính xác thấp trên dữ liệu thực tế (PRED(25) = 0.0123)
- Sai số lớn trên dữ liệu thực tế (MMRE = 2.7896)
- Không tận dụng được các đặc trưng phong phú từ dữ liệu
- Công thức cố định, ít linh hoạt
- Không thể tự điều chỉnh theo dữ liệu mới

**Phù hợp nhất cho:**

- Các dự án có ít dữ liệu lịch sử
- Ước lượng sơ bộ giai đoạn đầu dự án
- Dự án tuân theo các quy trình truyền thống

### Linear_Regression

**Điểm mạnh:**

- Đơn giản, dễ hiểu, giải thích được
- Huấn luyện nhanh
- Hiệu quả với tập dữ liệu nhỏ

**Điểm yếu:**

- Sai số cao hơn COCOMO II trên dữ liệu thực tế (MMRE = 4.4999 vs 2.7896)
- Độ chính xác thấp hơn COCOMO II trên dữ liệu thực tế (PRED(25) = 0.0000 vs 0.0123)
- Không thể mô hình hóa quan hệ phi tuyến phức tạp
- Nhạy cảm với dữ liệu outlier
- Giả định quan hệ tuyến tính giữa các biến

**Phù hợp nhất cho:**

- Dự án có quan hệ tuyến tính rõ ràng giữa kích thước và nỗ lực
- Các trường hợp cần giải thích rõ ràng về cách ước lượng

### Decision_Tree

**Điểm mạnh:**

- Sai số thấp hơn COCOMO II trên dữ liệu thực tế (MMRE = 1.3712 vs 2.7896)
- Độ chính xác cao hơn COCOMO II trên dữ liệu thực tế (PRED(25) = 0.1728 vs 0.0123)
- Dễ hiểu và giải thích
- Xử lý được cả dữ liệu số và phân loại
- Không yêu cầu chuẩn hóa dữ liệu

**Điểm yếu:**

- Có thể quá khớp với dữ liệu huấn luyện
- Không ổn định (thay đổi nhỏ trong dữ liệu có thể dẫn đến cây khác biệt)
- Hiệu suất không cao như các mô hình phức tạp hơn

**Phù hợp nhất cho:**

- Dự án cần phân loại theo đặc điểm rõ ràng
- Trường hợp cần quy tắc quyết định rõ ràng

### Random_Forest

**Điểm mạnh:**

- Sai số thấp hơn COCOMO II trên dữ liệu thực tế (MMRE = 0.6473 vs 2.7896)
- Độ chính xác cao hơn COCOMO II trên dữ liệu thực tế (PRED(25) = 0.3951 vs 0.0123)
- Mạnh mẽ với dữ liệu nhiễu và outlier
- Giảm thiểu overfitting so với Decision Tree
- Xử lý hiệu quả tập dữ liệu lớn với nhiều đặc trưng

**Điểm yếu:**

- Phức tạp hơn, khó giải thích
- Huấn luyện chậm hơn các mô hình đơn giản
- Cần nhiều dữ liệu để hoạt động tốt

**Phù hợp nhất cho:**

- Dự án phức tạp với nhiều yếu tố ảnh hưởng
- Tập dữ liệu có nhiều đặc trưng

### Gradient_Boosting

**Điểm mạnh:**

- Sai số thấp hơn COCOMO II trên dữ liệu thực tế (MMRE = 1.1008 vs 2.7896)
- Độ chính xác cao hơn COCOMO II trên dữ liệu thực tế (PRED(25) = 0.1975 vs 0.0123)
- Hiệu suất cao, thường có kết quả tốt nhất
- Xử lý tốt các quan hệ phi tuyến phức tạp
- Tích hợp quá trình học từ lỗi

**Điểm yếu:**

- Phức tạp, khó giải thích
- Nhạy cảm với hyperparameter
- Dễ bị overfitting nếu không điều chỉnh cẩn thận

**Phù hợp nhất cho:**

- Dự án cần độ chính xác cao nhất
- Có đủ dữ liệu để huấn luyện và điều chỉnh tham số

