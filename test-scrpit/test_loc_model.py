#!/usr/bin/env python

"""
Script để kiểm tra các thay đổi cho mô hình LOC
"""

import os
import sys
from pathlib import Path

# Thêm thư mục gốc vào sys.path
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

# Import các module cần thiết
from requirement_analyzer.loc_model import LOCModel
from requirement_analyzer.estimator import EffortEstimator
from requirement_analyzer.analyzer import RequirementAnalyzer

def test_loc_model():
    """
    Kiểm tra mô hình LOC
    """
    print("Kiểm tra mô hình LOC")
    
    # Tạo các đối tượng
    loc_model_linear = LOCModel(model_type="linear")
    loc_model_rf = LOCModel(model_type="random_forest")
    analyzer = RequirementAnalyzer()
    estimator = EffortEstimator()
    
    # Tạo dữ liệu kiểm tra
    test_texts = [
        "Dự án nhỏ có 3 KLOC, độ phức tạp thấp, team 2 người có kinh nghiệm cao",
        "Dự án trung bình có 10 KLOC, độ phức tạp trung bình, team 5 người có kinh nghiệm trung bình",
        "Dự án lớn có 30 KLOC, độ phức tạp cao, team 10 người có kinh nghiệm thấp",
        "Xây dựng hệ thống quản lý nhân sự với các chức năng quản lý thông tin nhân viên, chấm công, tính lương",
        "Phát triển hệ thống thương mại điện tử với các chức năng giỏ hàng, thanh toán, quản lý đơn hàng và tích hợp cổng thanh toán"
    ]
    
    # Thực hiện kiểm tra
    for i, text in enumerate(test_texts):
        print(f"\nKiểm tra văn bản {i+1}:")
        print(f"Nội dung: {text}")
        
        # Trích xuất tham số
        params = analyzer.extract_loc_parameters(text)
        print(f"\nTham số trích xuất: {params}")
        
        # Ước lượng với mô hình Linear
        linear_estimate = loc_model_linear.estimate(params)
        print(f"Ước lượng Linear: {linear_estimate}")
        
        # Ước lượng với mô hình Random Forest
        rf_estimate = loc_model_rf.estimate(params)
        print(f"Ước lượng Random Forest: {rf_estimate}")
        
        # Ước lượng động với Estimator
        dynamic_linear = estimator._dynamic_loc_estimate(params, 'linear')
        print(f"Ước lượng động Linear: {dynamic_linear}")
        
        dynamic_rf = estimator._dynamic_loc_estimate(params, 'random_forest')
        print(f"Ước lượng động Random Forest: {dynamic_rf}")
        
        # Kẻ dòng phân cách
        print("-" * 80)
        
    # Kiểm tra ghi đè ước lượng
    print("\nKiểm tra ghi đè ước lượng:")
    loc_model_linear.override_estimate(15.5, 85.0)
    params = {"kloc": 5.0, "complexity": 1.0}
    override_estimate = loc_model_linear.estimate(params)
    print(f"Ước lượng sau khi ghi đè: {override_estimate}")

if __name__ == "__main__":
    test_loc_model()
