# Config Directory

Thư mục này chứa các file cấu hình, data files và các file khác liên quan đến configuration.

## Danh sách Files

### CSV Files
- `comparison_metrics.csv` - Metrics so sánh
- `comparison_results.csv` - Kết quả so sánh

### Text Files
- `requirements.txt` - Python dependencies
- `requirements-docker.txt` - Docker specific requirements
- `requirements-task-generation.txt` - Task generation requirements
- `test_requirements.txt` - Testing requirements
- `test_results.txt` - Kết quả test

### Configuration Files
- `Spacefile` - Deta Space configuration
- `GITIGNORE_TASK_GEN.txt` - Gitignore cho task generation

### Other Files
- `*.patch` - Patch files
- `*.png` - Image files (diagrams, charts)
- `CHANGELOG_TASK_GENERATION.md` - Changelog cho task generation

## Lưu ý

- File `requirements.txt` chính được sử dụng cho development
- File `requirements-docker.txt` được sử dụng khi build Docker images
- Các file CSV chứa kết quả đánh giá và so sánh models
