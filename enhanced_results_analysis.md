# Phân Tích Chi Tiết Kết Quả So Sánh Các Mô Hình Ước Lượng COCOMO II Cải Tiến

**Tác giả:** Nguyễn Minh Huy  
**Ngày:** 08/07/2025

## 1. Tổng Quan Kết Quả Nâng Cao

Phân tích kết quả nâng cao từ việc so sánh các mô hình ước lượng nỗ lực phát triển phần mềm cho thấy sự cải thiện đáng kể khi áp dụng các kỹ thuật học máy hiện đại. Trong phần này, chúng tôi sẽ trình bày chi tiết kết quả so sánh giữa mô hình COCOMO II truyền thống và các mô hình học máy đã được cải tiến, dựa trên phiên bản nâng cao của các thí nghiệm.

### 1.1 Tổng Quan Các Chỉ Số Hiệu Suất

Bảng dưới đây trình bày tổng quan các chỉ số hiệu suất chính của các mô hình trên từng loại dữ liệu (schema):

| Model             | Schema | MMRE vs COCOMO | PRED(25) vs COCOMO | MMRE vs Actual | PRED(25) vs Actual | MAE      | RMSE     |
|-------------------|--------|----------------|--------------------|-----------------|--------------------|----------|----------|
| Linear_Regression | LOC    | 1.324          | 0.0909             | N/A             | N/A                | N/A      | N/A      |
| Decision_Tree     | LOC    | 0.8557         | 0                  | N/A             | N/A                | N/A      | N/A      |
| Random_Forest     | LOC    | 0.8992         | 0                  | N/A             | N/A                | N/A      | N/A      |
| Gradient_Boosting | LOC    | 1.0479         | 0                  | N/A             | N/A                | N/A      | N/A      |
| Linear_Regression | FP     | 21.945         | 0.1818             | 4.4999          | 0.0000             | 107.5358 | 280.2682 |
| Decision_Tree     | FP     | 0.663          | 0.0909             | 1.3712          | 0.1728             | 18.6321  | 23.6230  |
| Random_Forest     | FP     | 0.7081         | 0                  | 0.6473          | 0.3951             | 12.6558  | 20.0085  |
| Gradient_Boosting | FP     | 0.6085         | 0.0909             | 1.1008          | 0.1975             | 16.1608  | 21.0946  |
| Linear_Regression | UCP    | 4.7679         | 0                  | N/A             | N/A                | N/A      | N/A      |
| Decision_Tree     | UCP    | 1.5928         | 0                  | N/A             | N/A                | N/A      | N/A      |
| Random_Forest     | UCP    | 1.1412         | 0                  | N/A             | N/A                | N/A      | N/A      |
| Gradient_Boosting | UCP    | 2.2039         | 0                  | N/A             | N/A                | N/A      | N/A      |
| Linear_Regression | All    | 9.3456         | 0.0909             | 4.4999          | 0.0000             | 107.5358 | 280.2682 |
| Decision_Tree     | All    | 1.0371         | 0.0303             | 1.3712          | 0.1728             | 18.6321  | 23.6230  |
| Random_Forest     | All    | 0.9162         | 0                  | 0.6473          | 0.3951             | 12.6558  | 20.0085  |
| Gradient_Boosting | All    | 1.2868         | 0.0303             | 1.1008          | 0.1975             | 16.1608  | 21.0946  |

**Chú thích:**
- **MMRE vs COCOMO**: Sai số tương đối trung bình so với dự đoán của mô hình COCOMO II truyền thống
- **PRED(25) vs COCOMO**: Tỷ lệ dự đoán có sai số tương đối dưới 25% so với COCOMO II
- **MMRE vs Actual**: Sai số tương đối trung bình so với dữ liệu thực tế
- **PRED(25) vs Actual**: Tỷ lệ dự đoán có sai số tương đối dưới 25% so với dữ liệu thực tế
- **MAE**: Sai số tuyệt đối trung bình (Mean Absolute Error)
- **RMSE**: Căn bậc hai của sai số bình phương trung bình (Root Mean Squared Error)

### 1.2 So Sánh Hiệu Suất Trên Dữ Liệu Thực Tế

![So sánh MMRE trên dữ liệu thực tế](/home/huy/Huy-workspace/AI-Project/comparison_results/enhanced/real_comparison_mmre.png)

Kết quả so sánh hiệu suất trên dữ liệu thực tế cho thấy:

1. **Mô hình COCOMO II truyền thống** có MMRE = 2.7896, cho thấy sai số tương đối cao
2. **Random Forest** có hiệu suất tốt nhất với MMRE = 0.6473, giảm sai số hơn 76% so với mô hình truyền thống
3. **Gradient Boosting** đứng thứ hai với MMRE = 1.1008, giảm sai số hơn 60% so với mô hình truyền thống
4. **Decision Tree** có MMRE = 1.3712, giảm sai số hơn 50% so với mô hình truyền thống
5. **Linear Regression** có hiệu suất kém nhất với MMRE = 4.4999, cao hơn cả mô hình truyền thống

![So sánh PRED(25) trên dữ liệu thực tế](/home/huy/Huy-workspace/AI-Project/comparison_results/enhanced/real_comparison_pred25.png)

Về chỉ số PRED(25) - tỷ lệ dự đoán có sai số tương đối dưới 25%:

1. **Random Forest** có hiệu suất vượt trội với PRED(25) = 0.3951, gấp 32 lần mô hình truyền thống
2. **Gradient Boosting** đạt PRED(25) = 0.1975, gấp 16 lần mô hình truyền thống
3. **Decision Tree** đạt PRED(25) = 0.1728, gấp 14 lần mô hình truyền thống
4. **COCOMO II truyền thống** chỉ đạt PRED(25) = 0.0123
5. **Linear Regression** có hiệu suất kém nhất với PRED(25) = 0.0000

### 1.3 So Sánh Sai Số Tuyệt Đối và Bình Phương

![So sánh MAE và RMSE trên dữ liệu thực tế](/home/huy/Huy-workspace/AI-Project/comparison_results/enhanced/real_comparison_error_metrics.png)

Về các chỉ số sai số tuyệt đối (MAE) và sai số bình phương (RMSE):

1. **Random Forest** có hiệu suất tốt nhất với MAE = 12.6558 và RMSE = 20.0085
2. **Gradient Boosting** đứng thứ hai với MAE = 16.1608 và RMSE = 21.0946
3. **Decision Tree** xếp thứ ba với MAE = 18.6321 và RMSE = 23.6230
4. **COCOMO II truyền thống** có MAE = 45.0322 và RMSE = 53.7011
5. **Linear Regression** có hiệu suất kém nhất với MAE = 107.5358 và RMSE = 280.2682

## 2. Chi Tiết Kết Quả Theo Từng Schema

### 2.1 Dự Đoán Dựa Trên LOC (Lines of Code)

![So sánh ước lượng nỗ lực dựa trên LOC](/home/huy/Huy-workspace/AI-Project/comparison_results/enhanced/comparison_effort_LOC.png)

Khi so sánh các dự đoán dựa trên LOC (Lines of Code):

1. **Mô hình COCOMO II truyền thống** cho đường cong tăng dần theo kích thước dự án, phản ánh công thức lũy thừa của COCOMO II.
2. **Decision Tree** có xu hướng phân nhóm dự án theo kích thước, tạo ra các "bậc thang" trong dự đoán.
3. **Random Forest** tạo ra đường cong mượt hơn, thể hiện khả năng kết hợp nhiều cây quyết định.
4. **Gradient Boosting** tạo ra đường cong tương tự Random Forest nhưng có độ dốc lớn hơn với các dự án lớn.

![So sánh sai số dựa trên LOC](/home/huy/Huy-workspace/AI-Project/comparison_results/enhanced/comparison_error_LOC.png)

Phân tích sai số trên dữ liệu LOC:

1. Tất cả các mô hình có sai số giảm dần khi kích thước dự án tăng lên
2. **Decision Tree** có sai số thấp nhất với các dự án có kích thước trung bình (20-50 KLOC)
3. **Random Forest** có sai số ổn định nhất trên toàn bộ phạm vi kích thước
4. **Linear Regression** có sai số cao nhất với các dự án nhỏ (<10 KLOC)

### 2.2 Dự Đoán Dựa Trên FP (Function Points)

![So sánh ước lượng nỗ lực dựa trên FP](/home/huy/Huy-workspace/AI-Project/comparison_results/enhanced/comparison_effort_FP.png)

Với dữ liệu dựa trên Function Points:

1. **Mô hình COCOMO II truyền thống** có đường cong tăng nhanh theo số lượng FP, đặc biệt với các dự án lớn (>1000 FP).
2. **Decision Tree** có xu hướng tạo ra các "bậc thang" rõ rệt, phản ánh cấu trúc phân nhóm của cây quyết định.
3. **Random Forest** tạo ra đường cong mượt mà, tăng dần theo kích thước dự án nhưng với tốc độ chậm hơn mô hình truyền thống.
4. **Gradient Boosting** có đường cong tương tự Random Forest nhưng với độ dốc lớn hơn ở các dự án có số lượng FP trung bình.

![So sánh dự đoán trên dữ liệu thực tế dựa trên FP](/home/huy/Huy-workspace/AI-Project/comparison_results/enhanced/real_comparison_effort_FP.png)

Trên dữ liệu thực tế:

1. **COCOMO II truyền thống** có xu hướng dự đoán cao hơn giá trị thực tế, đặc biệt với các dự án có FP cao
2. **Random Forest** có dự đoán gần với giá trị thực tế nhất
3. **Gradient Boosting** và **Decision Tree** có dự đoán nằm giữa Random Forest và mô hình truyền thống
4. **Linear Regression** có dự đoán biến động mạnh và thường cao hơn giá trị thực tế nhiều lần

![So sánh sai số trên dữ liệu thực tế dựa trên FP](/home/huy/Huy-workspace/AI-Project/comparison_results/enhanced/real_comparison_error_FP.png)

Phân tích sai số trên dữ liệu FP thực tế:

1. **Random Forest** có sai số thấp nhất và ổn định nhất trên toàn bộ phạm vi FP
2. **Gradient Boosting** có sai số thấp thứ hai, tăng nhẹ với các dự án có FP cao
3. **Decision Tree** có sai số cao hơn và biến động nhiều hơn
4. **COCOMO II truyền thống** có sai số tăng nhanh theo kích thước dự án
5. **Linear Regression** có sai số cao nhất, đặc biệt với các dự án có FP cao

### 2.3 Dự Đoán Dựa Trên UCP (Use Case Points)

![So sánh ước lượng nỗ lực dựa trên UCP](/home/huy/Huy-workspace/AI-Project/comparison_results/enhanced/comparison_effort_UCP.png)

Khi phân tích dự đoán dựa trên Use Case Points:

1. **Mô hình COCOMO II truyền thống** tạo ra đường cong tương tự như với FP và LOC
2. **Linear Regression** có xu hướng dự đoán cao hơn nhiều so với các mô hình khác cho các dự án nhỏ (UCP < 200)
3. **Random Forest** và **Gradient Boosting** tạo ra các đường cong mượt mà, tăng dần theo UCP nhưng với tốc độ chậm hơn nhiều so với mô hình truyền thống
4. **Decision Tree** tạo ra các bậc thang rõ rệt, thể hiện cách mô hình phân loại dự án theo nhóm kích thước

![So sánh sai số dựa trên UCP](/home/huy/Huy-workspace/AI-Project/comparison_results/enhanced/comparison_error_UCP.png)

Phân tích sai số trên dữ liệu UCP:

1. **Linear Regression** có sai số rất cao với các dự án nhỏ (UCP < 100), sau đó giảm dần
2. **Random Forest** có sai số thấp nhất trên toàn bộ phạm vi UCP
3. **Decision Tree** có sai số thấp với các dự án có UCP từ 100-300, sau đó tăng dần
4. **Gradient Boosting** có sai số trung bình, nhưng ổn định hơn Decision Tree với các dự án lớn

## 3. Phân Tích Chi Tiết Từng Mô Hình

### 3.1 Mô Hình COCOMO II Truyền Thống

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

### 3.2 Linear Regression

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

### 3.3 Decision Tree

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

### 3.4 Random Forest

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

### 3.5 Gradient Boosting

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

## 4. So Sánh MMRE và PRED(25) Tổng Hợp

![So sánh MMRE trên các mô hình](/home/huy/Huy-workspace/AI-Project/comparison_results/enhanced/comparison_mmre.png)

So sánh chỉ số MMRE trên tất cả các schema:

1. **Random Forest** có hiệu suất tốt nhất trên cả dữ liệu thực tế và dữ liệu so sánh với COCOMO II
2. **Gradient Boosting** có hiệu suất tốt thứ hai trên dữ liệu FP, nhưng kém hơn trên dữ liệu UCP
3. **Decision Tree** có hiệu suất ổn định trên cả ba schema
4. **Linear Regression** có hiệu suất kém nhất, đặc biệt trên dữ liệu FP

![So sánh PRED(25) trên các mô hình](/home/huy/Huy-workspace/AI-Project/comparison_results/enhanced/comparison_pred25.png)

So sánh chỉ số PRED(25):

1. **Random Forest** có PRED(25) cao nhất trên dữ liệu thực tế (0.3951)
2. **Gradient Boosting** đứng thứ hai (0.1975)
3. **Decision Tree** đứng thứ ba (0.1728)
4. **COCOMO II truyền thống** và **Linear Regression** có PRED(25) rất thấp

## 5. Kết Luận và Ứng Dụng Thực Tế

### 5.1 Kết Luận Tổng Thể

Dựa trên các kết quả phân tích chi tiết, chúng tôi có thể rút ra một số kết luận quan trọng:

1. **Random Forest** là mô hình có hiệu suất tốt nhất nhìn chung, với MMRE thấp nhất (0.6473) và PRED(25) cao nhất (0.3951) trên dữ liệu thực tế. Mô hình này vượt trội so với COCOMO II truyền thống và các mô hình học máy khác.

2. **Gradient Boosting** là lựa chọn tốt thứ hai, đặc biệt khi cần cân bằng giữa độ chính xác và tốc độ huấn luyện.

3. **Decision Tree** mặc dù đơn giản hơn nhưng vẫn cải thiện đáng kể so với COCOMO II truyền thống, với MMRE giảm gần 51% và PRED(25) tăng 14 lần.

4. **Linear Regression** không phù hợp cho bài toán ước lượng nỗ lực phần mềm, thể hiện qua hiệu suất kém hơn cả mô hình COCOMO II truyền thống.

5. **Hiệu suất của các mô hình khác nhau đáng kể tùy thuộc vào loại dữ liệu đầu vào (LOC, FP, UCP)**, với hiệu suất tốt nhất trên dữ liệu FP và kém nhất trên dữ liệu LOC.

### 5.2 Ứng Dụng Thực Tế

Dựa trên kết quả nghiên cứu, chúng tôi đề xuất các ứng dụng thực tế sau:

1. **Sử dụng Random Forest cho các dự án quan trọng** cần độ chính xác cao trong ước lượng nỗ lực, đặc biệt khi có đủ dữ liệu lịch sử.

2. **Sử dụng Gradient Boosting cho các dự án trung bình** cần cân bằng giữa độ chính xác và hiệu suất tính toán.

3. **Sử dụng Decision Tree cho các dự án nhỏ hoặc khi cần giải thích rõ ràng** cách ước lượng cho các bên liên quan.

4. **Kết hợp các mô hình dựa trên giai đoạn dự án**:
   - Giai đoạn đầu: COCOMO II truyền thống hoặc Decision Tree
   - Giai đoạn giữa: Gradient Boosting
   - Giai đoạn chi tiết: Random Forest

5. **Tích hợp các mô hình vào công cụ quản lý dự án** để tự động cập nhật ước lượng khi có thêm dữ liệu.

### 5.3 Hạn Chế và Hướng Phát Triển

Mặc dù các mô hình học máy cải tiến cho kết quả tốt hơn, chúng vẫn còn một số hạn chế:

1. **Yêu cầu dữ liệu chất lượng cao** để huấn luyện hiệu quả
2. **Khó giải thích** đối với các mô hình phức tạp như Random Forest và Gradient Boosting
3. **Cần điều chỉnh tham số** để đạt hiệu suất tối ưu
4. **Có thể không khái quát tốt** cho các loại dự án mới, khác biệt

Hướng phát triển trong tương lai:

1. **Kết hợp với phương pháp Deep Learning** để xử lý các mối quan hệ phức tạp hơn
2. **Phát triển mô hình tích hợp đa nguồn dữ liệu** bao gồm cả dữ liệu phi cấu trúc
3. **Xây dựng hệ thống học liên tục** cập nhật mô hình theo thời gian thực
4. **Tích hợp với hệ thống DevOps và Agile** để cải thiện ước lượng trong môi trường phát triển hiện đại

## 6. Tài Liệu Tham Khảo

1. Boehm, B. (2000). COCOMO II Model Definition Manual. University of Southern California.
2. Jørgensen, M., & Shepperd, M. (2007). A Systematic Review of Software Development Cost Estimation Studies. IEEE Transactions on Software Engineering, 33(1), 33-53.
3. Wen, J., Li, S., Lin, Z., Hu, Y., & Huang, C. (2012). Systematic literature review of machine learning based software development effort estimation models. Information and Software Technology, 54(1), 41-59.
4. Sarro, F., Petrozziello, A., & Harman, M. (2016). Multi-objective software effort estimation. In Proceedings of the 38th International Conference on Software Engineering (ICSE '16). ACM, New York, NY, USA, 619-630.
5. Idri, A., Amazal, F. A., & Abran, A. (2015). Analogy-based software development effort estimation: A systematic mapping and review. Information and Software Technology, 58, 206-230.
6. Breiman, L. (2001). Random forests. Machine learning, 45(1), 5-32.
7. Friedman, J. H. (2001). Greedy function approximation: a gradient boosting machine. Annals of statistics, 1189-1232.
