# Hướng dẫn triển khai

## Cấu trúc thư mục triển khai đã được cập nhật

Sau khi cập nhật, thư mục `/workspaces/AI-Project/huggingface_deployment` đã bao gồm:

1. **app/**: Thư mục chứa mã nguồn backend
   - **requirement_analyzer/**: Module phân tích yêu cầu
   - **models/**: Thư mục chứa các mô hình ML đã được sao chép từ thư mục gốc
     - **cocomo_ii_extended/**: Các mô hình COCOMO II mở rộng (Random Forest, Decision Tree, etc.)
     - Các tập tin mô hình neural network, tham số và chỉ số

2. **static/**: Thư mục chứa tài nguyên tĩnh
   - **css/**: Stylesheet
   - **js/**: JavaScript
   
3. **templates/**: Các template HTML
   - **index.html**: Trang chủ
   - **debug.html**: Trang gỡ lỗi

4. **Các tập tin chính**:
   - **app.py**: Ứng dụng FastAPI chính
   - **packages.py**: Quản lý cài đặt các gói phụ thuộc
   - **requirements.txt**: Danh sách các phụ thuộc
   - **Dockerfile**: Cấu hình Docker cho việc triển khai
   - **check_models.py**: Công cụ kiểm tra mô hình
   - **API_DOCUMENTATION.md**: Tài liệu API
   - **deploy_simplified.sh**: Script triển khai đơn giản
   - **deploy_to_huggingface.sh**: Script triển khai đầy đủ

## Thay đổi chính

1. **Mô hình**:
   - Đã sao chép tất cả mô hình từ `/models` vào `/app/models`
   - Đã thêm biến môi trường `MODEL_DIR` để ứng dụng có thể tìm thấy mô hình

2. **Tài nguyên tĩnh**:
   - Đã sao chép đầy đủ thư mục `static` và `templates` từ `requirement_analyzer`
   - Đảm bảo cấu trúc thư mục thống nhất

3. **Cấu hình**:
   - Đã cập nhật Dockerfile để sao chép mô hình
   - Đã cập nhật script triển khai để bao gồm việc sao chép mô hình
   - Đã thêm công cụ kiểm tra mô hình (`check_models.py`)

4. **Phụ thuộc**:
   - Đã bổ sung các phụ thuộc còn thiếu trong `requirements.txt`

## Hướng dẫn triển khai

1. **Kiểm tra cấu trúc**:
   ```bash
   ls -la /workspaces/AI-Project/huggingface_deployment
   ls -la /workspaces/AI-Project/huggingface_deployment/app/models
   ```

2. **Kiểm tra mô hình**:
   ```bash
   python /workspaces/AI-Project/huggingface_deployment/check_models.py
   ```

3. **Triển khai**:
   
   **Phương án 1**: Sử dụng Docker
   ```bash
   cd /workspaces/AI-Project
   ./huggingface_deployment/deploy_to_huggingface.sh
   ```
   
   **Phương án 2**: Sử dụng Python SDK
   - Tạo Space trên Hugging Face với SDK Python
   - Đẩy nội dung thư mục `huggingface_deployment` lên Space

## API endpoints

1. **`/api/estimate`**: Ước lượng nỗ lực từ văn bản yêu cầu
2. **`/api/upload-requirements`**: Ước lượng nỗ lực từ tài liệu được tải lên
3. **`/health`**: Kiểm tra trạng thái hoạt động