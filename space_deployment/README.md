---
title: Software Requirement Analyzer API
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# Software Requirement Analyzer API

API này cung cấp các endpoint để phân tích yêu cầu phần mềm và ước lượng nỗ lực phát triển dựa trên đặc điểm yêu cầu.

## Endpoints API

### POST /api/estimate
Ước lượng nỗ lực phát triển dựa trên văn bản yêu cầu.

Ví dụ:
```bash
curl -X POST "https://nhathuyyne-requirement-analyzer-api.hf.space/api/estimate" \
     -H "Content-Type: application/json" \
     -d '{"text": "Phát triển hệ thống quản lý bệnh viện", "method": "weighted_average"}'
```

### POST /api/upload-requirements
Tải lên tài liệu yêu cầu để phân tích.

Các định dạng file được hỗ trợ:
- .txt, .md: Files văn bản đơn giản
- .pdf: Tài liệu PDF
- .doc, .docx: Tài liệu Microsoft Word

### GET /health
Kiểm tra trạng thái API

## Demo trực tuyến
Truy cập tài liệu API tại: https://nhathuyyne-requirement-analyzer-api.hf.space/docs