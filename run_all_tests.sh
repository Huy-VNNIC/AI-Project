#!/bin/bash
# Script chạy tất cả các test cho COCOMO II

echo "===== BẮT ĐẦU KIỂM TRA MÔ HÌNH COCOMO II ====="

# Tạo thư mục kết quả
mkdir -p comparison_results
mkdir -p notebook_results

# 1. Chạy test API cơ bản
echo -e "\n1. Chạy test API cơ bản..."
python test_cocomo_api.py

# 2. Chạy test trên dữ liệu thực tế
echo -e "\n2. Chạy test trên dữ liệu thực tế..."
python test_on_real_data.py

# 3. Chạy script so sánh với mô hình truyền thống
echo -e "\n3. Chạy script so sánh với mô hình truyền thống..."
python compare_enhanced_models_v2.py

echo -e "\n===== HOÀN THÀNH KIỂM TRA ====="
echo "Kết quả được lưu trong các thư mục:"
echo "  - comparison_results/"
echo "  - notebook_results/"
echo -e "\nBạn có thể mở Jupyter Notebook để tương tác với mô hình:"
echo "jupyter notebook test_cocomo_models.ipynb"
