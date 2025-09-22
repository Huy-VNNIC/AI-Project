# Hướng Dẫn Commit và Push Lên GitHub

## Chuẩn Bị

1. Đảm bảo các tệp cần thiết đã được chuẩn bị
2. Bạn đã có tài khoản GitHub
3. Đã cấu hình Git trên máy tính của bạn

## Quy Trình Commit

### Bước 1: Kiểm tra trạng thái

```bash
git status
```

### Bước 2: Tổ chức các file cần commit

#### Cách 1: Thêm tất cả các file

```bash
git add .
```

#### Cách 2: Thêm từng file cụ thể (khuyến nghị cho dự án lớn)

```bash
# Thêm các file script
git add run_api_service.sh fix_sklearn_version.sh retrain_with_current_features.sh setup_github.sh

# Thêm các file tài liệu
git add API_SERVICE_USAGE.md

# Thêm các file trong thư mục requirement_analyzer
git add requirement_analyzer/fix_models.py requirement_analyzer/retrain_models.py

# Thêm các model được train
git add models/neural_network_model.h5 models/param_indices.json models/req_effort_connector.h5 models/feature_list.txt
```

### Bước 3: Tạo commit với thông điệp mô tả rõ ràng

```bash
git commit -m "Cải thiện hệ thống phân tích yêu cầu và ước lượng nỗ lực"
```

Hoặc commit chi tiết hơn:

```bash
git commit -m "Cải thiện hệ thống phân tích yêu cầu và ước lượng nỗ lực

- Thêm API service riêng biệt
- Thêm scripts cho việc fix sklearn version
- Thêm công cụ retrain model với feature hiện tại
- Cập nhật model params và feature list
- Thêm tài liệu hướng dẫn sử dụng API"
```

### Bước 4: Push lên GitHub

```bash
git push origin main
```

## Chiến Lược Commit Hiệu Quả

1. **Commit thường xuyên**: Commit mỗi khi hoàn thành một tính năng nhỏ
2. **Thông điệp commit rõ ràng**: Mô tả ngắn gọn những gì bạn đã thay đổi
3. **Tổ chức commit theo chức năng**: Nhóm các thay đổi liên quan vào cùng một commit
4. **Sử dụng các branch**: Tạo branch riêng cho mỗi tính năng lớn

## Ví Dụ Thông Điệp Commit Tốt

- "Thêm API service độc lập cho requirement analyzer"
- "Fix lỗi mismatch giữa model và feature extraction"
- "Cải thiện độ chính xác của neural network model"
- "Thêm tài liệu hướng dẫn API"
- "Tối ưu hóa hiệu suất của requirement analyzer"

## Commit Step-by-Step cho Dự Án Hiện Tại

```bash
# Bước 1: Thêm các script mới
git add run_api_service.sh fix_sklearn_version.sh retrain_with_current_features.sh

# Bước 2: Commit các script
git commit -m "Thêm script để chạy API service và fix model compatibility"

# Bước 3: Thêm các file Python mới
git add requirement_analyzer/fix_models.py requirement_analyzer/retrain_models.py

# Bước 4: Commit các file Python
git commit -m "Thêm module để retrain và fix models"

# Bước 5: Thêm các file model và metadata
git add models/

# Bước 6: Commit các file model
git commit -m "Cập nhật model params và feature list"

# Bước 7: Thêm tài liệu
git add API_SERVICE_USAGE.md setup_github.sh

# Bước 8: Commit tài liệu
git commit -m "Thêm tài liệu hướng dẫn sử dụng API và setup GitHub"

# Bước 9: Push tất cả lên GitHub
git push origin main
```
