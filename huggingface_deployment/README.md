---
title: Software Requirement Analyzer API
emoji: 📊
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# Software Requirement Analyzer API

This API provides endpoints for analyzing software requirements and estimating development effort based on requirement specifications.

## API Endpoints

### POST /api/estimate
Estimate development effort based on requirement text.

Example:
```bash
curl -X POST "https://nhathuyyne-requirement-analyzer-api.hf.space/api/estimate" \
     -H "Content-Type: application/json" \
     -d '{"text": "Develop hospital management system", "method": "weighted_average"}'
```

### POST /api/upload-requirements
Upload a requirements document file for analysis.

Supported file types:
- .txt, .md: Plain text files
- .pdf: PDF documents
- .doc, .docx: Microsoft Word documents

### GET /health
Check API status

## Cấu trúc Triển khai

Thư mục triển khai này bao gồm:

- `app.py`: File ứng dụng FastAPI chính
- `app/`: Thư mục chứa các module và mô hình
  - `requirement_analyzer/`: Module phân tích yêu cầu
  - `models/`: Thư mục chứa các mô hình ML đã được huấn luyện
- `static/`: Thư mục chứa tệp CSS, JavaScript và tài nguyên tĩnh khác
- `templates/`: Thư mục chứa các template HTML
- `requirements.txt`: Danh sách các phụ thuộc Python
- `packages.py`: Script tự động tải các gói NLTK và thiết lập môi trường
- `check_models.py`: Script kiểm tra cấu hình mô hình

## Hướng dẫn Triển khai

1. **Chuẩn bị**:
   - Đảm bảo tất cả mô hình đã được sao chép vào `app/models/`
   - Kiểm tra `requirements.txt` để đảm bảo tất cả các phụ thuộc cần thiết

2. **Triển khai trên Hugging Face Spaces**:
   - Tạo một Space mới với SDK Python
   - Đẩy toàn bộ thư mục này lên không gian đó
   - Space sẽ tự động cài đặt các phụ thuộc và chạy ứng dụng

3. **Kiểm tra**:
   - Chạy `python check_models.py` để xác minh tất cả mô hình đã được cấu hình đúng
