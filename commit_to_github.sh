#!/bin/bash
# Script để commit dự án lên GitHub một cách có tổ chức

echo "==== Bắt đầu quá trình commit dự án lên GitHub ===="

# Bước 1: Thêm các script mới
echo "Thêm các script mới..."
git add run_api_service.sh fix_sklearn_version.sh retrain_with_current_features.sh

# Bước 2: Commit các script
echo "Commit các script..."
git commit -m "Thêm script để chạy API service và fix model compatibility"

# Bước 3: Thêm các file Python mới
echo "Thêm các file Python mới..."
git add requirement_analyzer/fix_models.py requirement_analyzer/retrain_models.py

# Bước 4: Commit các file Python
echo "Commit các file Python..."
git commit -m "Thêm module để retrain và fix models"

# Bước 5: Thêm các file model và metadata
echo "Thêm các file model và metadata..."
git add models/feature_list.txt models/neural_network_model.h5 models/param_indices.json models/req_effort_connector.h5

# Bước 6: Commit các file model
echo "Commit các file model..."
git commit -m "Cập nhật model params và feature list"

# Bước 7: Thêm tài liệu
echo "Thêm tài liệu..."
git add API_SERVICE_USAGE.md COMMIT_GUIDE.md setup_github.sh

# Bước 8: Commit tài liệu
echo "Commit tài liệu..."
git commit -m "Thêm tài liệu hướng dẫn sử dụng API và setup GitHub"

# Bước 9: Push tất cả lên GitHub
echo "Push tất cả lên GitHub..."
git push origin main

echo "==== Hoàn thành quá trình commit dự án lên GitHub ===="
