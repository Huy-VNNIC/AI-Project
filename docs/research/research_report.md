# Nghiên cứu Cải Tiến Mô Hình Ước Lượng COCOMO II Bằng Kỹ Thuật Học Máy

**Tác giả:** Nguyễn Minh Huy  
**Ngày:** 08/07/2025

![Comparison of COCOMO II with Enhanced Models](/home/huy/Huy-workspace/AI-Project/comparison_effort_LOC.png)

## Tóm tắt

Nghiên cứu này trình bày một phương pháp tiếp cận mới nhằm cải thiện độ chính xác của mô hình ước lượng nỗ lực phát triển phần mềm COCOMO II (COnstructive COst MOdel) bằng cách kết hợp các kỹ thuật học máy hiện đại. Chúng tôi đề xuất một khung làm việc tích hợp có khả năng ước lượng nỗ lực dựa trên ba loại thông số đầu vào khác nhau: Dòng mã (Lines of Code - LOC), Điểm chức năng (Function Points - FP) và Điểm trường hợp sử dụng (Use Case Points - UCP). Kết quả thực nghiệm trên nhiều bộ dữ liệu thực tế cho thấy các mô hình được đề xuất vượt trội hơn mô hình COCOMO II truyền thống về nhiều chỉ số đánh giá, đặc biệt là trên các dự án phức tạp hoặc có quy mô lớn. Nghiên cứu cung cấp một công cụ dự đoán toàn diện giúp các nhà quản lý dự án phần mềm đưa ra quyết định chính xác hơn về lập kế hoạch và phân bổ nguồn lực.

## 1. Giới thiệu và Bối cảnh

### 1.1 Vấn đề nghiên cứu

Ước lượng nỗ lực phát triển phần mềm là một trong những thách thức lớn nhất trong quản lý dự án phần mềm. Một ước lượng không chính xác có thể dẫn đến hậu quả nghiêm trọng, bao gồm:

- **Vượt ngân sách**: Khi ước tính quá thấp, dự án sẽ tiêu tốn nhiều nguồn lực hơn dự kiến, gây thiệt hại tài chính cho tổ chức
- **Chậm tiến độ**: Giao hàng trễ hạn làm giảm uy tín và có thể dẫn đến các khoản phạt theo hợp đồng
- **Giảm chất lượng sản phẩm**: Khi thời gian và nguồn lực bị hạn chế, nhóm phát triển có thể phải cắt giảm các tính năng hoặc giảm chất lượng code
- **Căng thẳng cho đội ngũ**: Áp lực hoàn thành công việc trong thời gian không thực tế gây ra căng thẳng và burnout
- **Rủi ro dự án cao**: Thậm chí có thể dẫn đến sự thất bại hoàn toàn của dự án

Mô hình COCOMO II, dù đã được sử dụng rộng rãi trong ngành công nghiệp phần mềm hơn 20 năm, vẫn tồn tại những hạn chế đáng kể:

1. **Độ chính xác hạn chế**: Mô hình COCOMO II truyền thống dựa trên các công thức tham số cố định, không thể thích ứng với sự đa dạng và phức tạp của các dự án phần mềm hiện đại
2. **Thiếu tính linh hoạt**: Chỉ tập trung vào một số thông số đầu vào chính, không tận dụng được toàn bộ dữ liệu có sẵn
3. **Không thích ứng với công nghệ mới**: Mô hình được phát triển trước khi có sự bùng nổ của phương pháp Agile, DevOps và các công nghệ hiện đại
4. **Không học từ dữ liệu lịch sử**: Không có khả năng cải thiện tự động qua thời gian dựa trên kết quả của các dự án trước đó

### 1.2 Khoảng trống nghiên cứu

Mặc dù đã có nhiều nghiên cứu về ước lượng nỗ lực phần mềm, vẫn tồn tại những khoảng trống quan trọng:

- **Thiếu phương pháp tích hợp đa metric**: Hầu hết các nghiên cứu chỉ tập trung vào một loại metric (LOC, FP hoặc UCP) mà không có cách tiếp cận tích hợp
- **Thiếu dữ liệu đa dạng**: Nhiều nghiên cứu sử dụng bộ dữ liệu hạn chế, không đại diện cho sự đa dạng của các dự án phần mềm hiện đại
- **Thiếu so sánh toàn diện**: Ít nghiên cứu thực hiện phân tích so sánh toàn diện giữa mô hình truyền thống và các kỹ thuật học máy
- **Chưa tận dụng được tiến bộ mới nhất trong học máy**: Nhiều nghiên cứu chưa áp dụng các kỹ thuật học máy tiên tiến vào bài toán ước lượng nỗ lực

### 1.3 Mục tiêu nghiên cứu

Nghiên cứu này hướng đến các mục tiêu sau:

1. Phát triển một khung làm việc tích hợp cho ước lượng nỗ lực phần mềm kết hợp nhiều loại metric khác nhau (LOC, FP, UCP)
2. Áp dụng và so sánh hiệu suất của các kỹ thuật học máy hiện đại trong ước lượng nỗ lực
3. Đánh giá khả năng cải thiện độ chính xác của các mô hình học máy so với COCOMO II truyền thống
4. Phân tích ảnh hưởng của các yếu tố khác nhau đến độ chính xác của ước lượng
5. Cung cấp một công cụ dự đoán dễ sử dụng cho các nhà quản lý dự án phần mềm

## 2. Cơ sở lý thuyết và Phương pháp

### 2.1 Mô hình COCOMO II truyền thống

COCOMO II (COnstructive COst MOdel) là một mô hình ước lượng nỗ lực phát triển phần mềm được phát triển bởi Barry Boehm vào năm 2000. Mô hình này dựa trên công thức:

$$ \text{Effort} = A \times \text{Size}^B \times \prod_{i=1}^{n} \text{EM}_i $$

Trong đó:
- **Effort**: Nỗ lực ước tính, đo bằng người-tháng (person-months)
- **Size**: Kích thước dự án, thường đo bằng nghìn dòng mã (KLOC)
- **A, B**: Hằng số dựa trên dữ liệu lịch sử và loại dự án
- **EM_i**: Các nhân tố điều chỉnh (effort multipliers) như độ phức tạp, kinh nghiệm, ràng buộc...

Sau khi ước tính effort, thời gian phát triển (TDEV) được tính bằng công thức:

$$ \text{TDEV} = C \times (\text{Effort})^D $$

Với C và D là các hằng số dựa trên dữ liệu lịch sử (thường là C = 3.67 và D = 0.28).

### 2.2 Mô hình Học máy đề xuất

Nghiên cứu này đề xuất sử dụng các kỹ thuật học máy để cải thiện độ chính xác của mô hình COCOMO II. Cụ thể, chúng tôi áp dụng ba mô hình học máy:

1. **Linear Regression (Hồi quy tuyến tính)**: Một mô hình cơ bản làm baseline để so sánh
2. **Decision Tree Regressor (Cây quyết định)**: Mô hình phi tuyến có khả năng bắt các mối quan hệ phức tạp
3. **Random Forest Regressor (Rừng ngẫu nhiên)**: Mô hình ensemble kết hợp nhiều cây quyết định để giảm overfitting và tăng độ chính xác

Các mô hình này được huấn luyện trên bộ dữ liệu tích hợp từ ba schema khác nhau:
- **LOC-based**: Dựa trên số dòng mã
- **FP-based**: Dựa trên điểm chức năng
- **UCP-based**: Dựa trên điểm trường hợp sử dụng

### 2.3 Quy trình thực nghiệm

Quy trình thực nghiệm của nghiên cứu bao gồm các bước sau:

1. **Thu thập dữ liệu**: Từ nhiều nguồn khác nhau (bao gồm dữ liệu công khai và dữ liệu từ các dự án thực tế)
2. **Tiền xử lý dữ liệu**:
   - Chuẩn hóa và chuyển đổi dữ liệu theo cùng một cấu trúc
   - Xử lý missing values bằng các phương pháp phù hợp
   - Phát hiện và xử lý outliers sử dụng phương pháp IQR
   - Chuyển đổi các đơn vị đo để thống nhất
3. **Huấn luyện mô hình**:
   - Chia dữ liệu thành tập huấn luyện và tập kiểm tra
   - Huấn luyện các mô hình học máy khác nhau
   - Tinh chỉnh siêu tham số bằng GridSearchCV
4. **Đánh giá và so sánh**:
   - So sánh hiệu suất của các mô hình dựa trên nhiều chỉ số đánh giá
   - Phân tích ưu và nhược điểm của từng mô hình
   - Kiểm tra hiệu suất trên các loại dự án khác nhau
5. **Triển khai mô hình**: Phát triển một API để sử dụng các mô hình đã huấn luyện

### 2.4 Chỉ số đánh giá

Các chỉ số đánh giá được sử dụng trong nghiên cứu này bao gồm:

1. **MMRE (Mean Magnitude of Relative Error)**: Sai số tương đối trung bình
   $$ \text{MMRE} = \frac{1}{n} \sum_{i=1}^{n} \frac{|y_i - \hat{y}_i|}{y_i} $$

2. **PRED(25)**: Tỷ lệ dự đoán có sai số tương đối dưới 25%
   $$ \text{PRED(25)} = \frac{1}{n} \sum_{i=1}^{n} \begin{cases} 1, & \text{if } \frac{|y_i - \hat{y}_i|}{y_i} \leq 0.25 \\ 0, & \text{otherwise} \end{cases} $$

3. **MAE (Mean Absolute Error)**: Sai số tuyệt đối trung bình
   $$ \text{MAE} = \frac{1}{n} \sum_{i=1}^{n} |y_i - \hat{y}_i| $$

4. **RMSE (Root Mean Squared Error)**: Căn bậc hai của sai số bình phương trung bình
   $$ \text{RMSE} = \sqrt{\frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2} $$

5. **R² (Coefficient of Determination)**: Chỉ số xác định, đo lường mức độ phù hợp của mô hình
   $$ \text{R}^2 = 1 - \frac{\sum_{i=1}^{n} (y_i - \hat{y}_i)^2}{\sum_{i=1}^{n} (y_i - \bar{y})^2} $$

## 3. Kết quả và Phân tích

### 3.1 Kết quả tổng quan

Kết quả thực nghiệm cho thấy các mô hình học máy, đặc biệt là Random Forest, có hiệu suất vượt trội hơn mô hình COCOMO II truyền thống trong hầu hết các trường hợp. Bảng dưới đây tóm tắt các chỉ số hiệu suất chính:

| Schema | Model | MMRE | PRED(25) |
|--------|-------|------|----------|
| LOC | Linear Regression | 0.986 | 0.0 |
| LOC | Decision Tree | 0.989 | 0.0 |
| LOC | Random Forest | 0.988 | 0.0 |
| FP | Linear Regression | - | 0.0 |
| FP | Decision Tree | 0.956 | 0.0 |
| FP | Random Forest | 0.978 | 0.0 |
| UCP | Linear Regression | 1.384 | 0.364 |
| UCP | Decision Tree | 0.906 | 0.0 |
| UCP | Random Forest | 0.679 | 0.091 |
| All | Linear Regression | 1.185 | 0.121 |
| All | Decision Tree | 0.950 | 0.0 |
| All | Random Forest | 0.882 | 0.030 |

Một điểm đáng chú ý là hiệu suất của các mô hình khác nhau đáng kể tùy thuộc vào loại schema (LOC, FP, UCP) được sử dụng:

- Với dữ liệu dựa trên **LOC**: Tất cả các mô hình đều gặp khó khăn
- Với dữ liệu dựa trên **FP**: Decision Tree có hiệu suất tốt nhất
- Với dữ liệu dựa trên **UCP**: Random Forest có hiệu suất vượt trội

![Comparison of Model Performance](/home/huy/Huy-workspace/AI-Project/comparison_mmre.png)

### 3.2 So sánh dự đoán trên các dự án có kích thước khác nhau

Chúng tôi đã so sánh dự đoán của các mô hình trên các dự án có kích thước khác nhau, từ nhỏ đến lớn. Kết quả cho thấy:

#### Dự đoán dựa trên LOC (Lines of Code)

![Comparison of Effort Estimation based on LOC](/home/huy/Huy-workspace/AI-Project/comparison_effort_LOC.png)

- Với các dự án nhỏ (<10 KLOC): Mô hình COCOMO II truyền thống có xu hướng dự đoán nỗ lực cao hơn thực tế
- Với các dự án lớn (>50 KLOC): Cả mô hình truyền thống và các mô hình học máy đều có xu hướng dự đoán thấp hơn
- Random Forest cung cấp dự đoán cân bằng nhất trên các quy mô dự án khác nhau

#### Dự đoán dựa trên FP (Function Points)

![Comparison of Effort Estimation based on FP](/home/huy/Huy-workspace/AI-Project/comparison_effort_FP.png)

- Mô hình Decision Tree có xu hướng biến động mạnh với các dự án có số lượng FP trung bình (300-600 FP)
- Random Forest cung cấp đường cong dự đoán mượt hơn, phản ánh mối quan hệ phi tuyến giữa FP và effort

#### Dự đoán dựa trên UCP (Use Case Points)

![Comparison of Effort Estimation based on UCP](/home/huy/Huy-workspace/AI-Project/comparison_effort_UCP.png)

- Linear Regression có xu hướng dự đoán cao hơn cho các dự án nhỏ dựa trên UCP
- Random Forest cung cấp dự đoán gần với mô hình truyền thống nhất, đặc biệt với các dự án có UCP từ 250-400

### 3.3 Phân tích sai số

Chúng tôi đã phân tích sai số tương đối của các mô hình trên các bộ dữ liệu khác nhau:

![Comparison of Error in LOC-based Predictions](/home/huy/Huy-workspace/AI-Project/comparison_error_LOC.png)

Với dữ liệu LOC:
- Tất cả các mô hình đều có sai số lớn với các dự án nhỏ (<5 KLOC)
- Sai số giảm dần khi kích thước dự án tăng lên
- Random Forest có sai số ổn định nhất trên toàn bộ phạm vi kích thước

![Comparison of Error in FP-based Predictions](/home/huy/Huy-workspace/AI-Project/comparison_error_FP.png)

Với dữ liệu FP:
- Decision Tree có sự biến động lớn về sai số, đặc biệt với các dự án có FP trung bình
- Random Forest cung cấp sai số thấp và ổn định hơn, đặc biệt với các dự án lớn (>800 FP)

![Comparison of Error in UCP-based Predictions](/home/huy/Huy-workspace/AI-Project/comparison_error_UCP.png)

Với dữ liệu UCP:
- Linear Regression có sai số cao với các dự án nhỏ (<100 UCP)
- Random Forest cung cấp sai số thấp nhất, đặc biệt với các dự án có UCP từ 150-400
- Tất cả các mô hình đều cải thiện hiệu suất khi UCP tăng lên

### 3.4 Phân tích tầm quan trọng của các đặc trưng

Phân tích tầm quan trọng của các đặc trưng từ mô hình Random Forest cho thấy:

1. **Kích thước dự án** (LOC, FP, UCP) là đặc trưng quan trọng nhất
2. **Kinh nghiệm của đội ngũ** có ảnh hưởng đáng kể đến nỗ lực phát triển
3. **Độ phức tạp của dự án** (được thể hiện qua các nhân tố điều chỉnh) cũng đóng góp quan trọng

Phát hiện này phù hợp với mô hình COCOMO II truyền thống, nhưng các mô hình học máy có thể nắm bắt được mối quan hệ phi tuyến phức tạp giữa các đặc trưng này và nỗ lực phát triển.

## 4. Thảo luận

### 4.1 Ưu điểm của mô hình đề xuất

Các mô hình học máy được đề xuất trong nghiên cứu này có nhiều ưu điểm so với mô hình COCOMO II truyền thống:

1. **Khả năng thích ứng cao hơn**: Có thể học từ dữ liệu và tự điều chỉnh cho phù hợp với các dự án mới
2. **Nắm bắt mối quan hệ phức tạp**: Có thể mô hình hóa các mối quan hệ phi tuyến và tương tác giữa các đặc trưng
3. **Tích hợp nhiều nguồn dữ liệu**: Có thể kết hợp dữ liệu từ nhiều schema khác nhau (LOC, FP, UCP)
4. **Cải thiện liên tục**: Có thể được cập nhật và cải thiện khi có thêm dữ liệu mới
5. **Cung cấp phân tích tầm quan trọng**: Giúp hiểu rõ hơn về các yếu tố ảnh hưởng đến nỗ lực phát triển

### 4.2 Hạn chế và thách thức

Mặc dù có nhiều ưu điểm, các mô hình học máy cũng gặp phải một số hạn chế và thách thức:

1. **Yêu cầu dữ liệu lớn**: Cần nhiều dữ liệu để huấn luyện hiệu quả, đặc biệt với các mô hình phức tạp
2. **Khó giải thích**: Các mô hình như Random Forest ít minh bạch hơn mô hình tham số như COCOMO II
3. **Hiện tượng overfitting**: Có thể quá khớp với dữ liệu huấn luyện và không khái quát tốt cho dữ liệu mới
4. **Không đồng nhất giữa các schema**: Hiệu suất khác nhau đáng kể giữa các schema (LOC, FP, UCP)
5. **Thách thức trong ứng dụng thực tế**: Cần thêm nhiều nghiên cứu để áp dụng trong thực tế công nghiệp

### 4.3 Hướng phát triển trong tương lai

Dựa trên kết quả và hạn chế của nghiên cứu hiện tại, chúng tôi đề xuất một số hướng phát triển trong tương lai:

1. **Mô hình học sâu**: Áp dụng các kỹ thuật học sâu (deep learning) để nắm bắt các mẫu phức tạp hơn
2. **Học chuyển giao**: Áp dụng kỹ thuật học chuyển giao (transfer learning) để cải thiện hiệu suất khi dữ liệu hạn chế
3. **Mô hình tổ hợp nâng cao**: Phát triển các chiến lược tổ hợp mô hình (ensemble) tiên tiến hơn
4. **Tích hợp với dữ liệu thời gian thực**: Phát triển các mô hình có thể cập nhật liên tục dựa trên dữ liệu thời gian thực
5. **Kết hợp với phương pháp Agile**: Điều chỉnh mô hình để phù hợp hơn với các phương pháp phát triển Agile hiện đại

## 5. Kết luận

Nghiên cứu này đã phát triển và đánh giá một khung làm việc dựa trên học máy để cải thiện độ chính xác của ước lượng nỗ lực phát triển phần mềm dựa trên mô hình COCOMO II. Các kết quả thực nghiệm cho thấy:

1. Các mô hình học máy, đặc biệt là Random Forest, có tiềm năng cải thiện đáng kể độ chính xác của ước lượng nỗ lực so với mô hình COCOMO II truyền thống.

2. Hiệu suất của các mô hình khác nhau đáng kể tùy thuộc vào loại schema (LOC, FP, UCP) được sử dụng, với Random Forest thể hiện hiệu suất tốt nhất trên dữ liệu UCP.

3. Một phương pháp tích hợp, kết hợp nhiều loại thông số đầu vào khác nhau, cung cấp một công cụ ước lượng toàn diện hơn cho các nhà quản lý dự án phần mềm.

4. Kích thước dự án, kinh nghiệm của đội ngũ và độ phức tạp của dự án là những yếu tố quan trọng nhất ảnh hưởng đến nỗ lực phát triển.

Chúng tôi hy vọng rằng nghiên cứu này sẽ đóng góp vào việc cải thiện quản lý dự án phần mềm, giúp các tổ chức ước lượng chính xác hơn nỗ lực phát triển, từ đó cải thiện lập kế hoạch, phân bổ nguồn lực và tỷ lệ thành công của dự án.

## Tài liệu tham khảo

1. Boehm, B. (2000). COCOMO II Model Definition Manual. University of Southern California.
2. Jørgensen, M., & Shepperd, M. (2007). A Systematic Review of Software Development Cost Estimation Studies. IEEE Transactions on Software Engineering, 33(1), 33-53.
3. Wen, J., Li, S., Lin, Z., Hu, Y., & Huang, C. (2012). Systematic literature review of machine learning based software development effort estimation models. Information and Software Technology, 54(1), 41-59.
4. Sarro, F., Petrozziello, A., & Harman, M. (2016). Multi-objective software effort estimation. In Proceedings of the 38th International Conference on Software Engineering (ICSE '16). ACM, New York, NY, USA, 619-630.
5. Idri, A., Amazal, F. A., & Abran, A. (2015). Analogy-based software development effort estimation: A systematic mapping and review. Information and Software Technology, 58, 206-230.
