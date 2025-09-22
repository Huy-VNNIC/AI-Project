#!/usr/bin/env python3
"""
Script so sánh dự đoán của COCOMO II API với dữ liệu thực tế
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from src.models.cocomo.cocomo_ii_api import CocomoIIAPI

def test_on_real_data():
    # Khởi tạo API
    api = CocomoIIAPI()
    
    # Đường dẫn đến dữ liệu
    albrecht_path = './sw-effort-predictive-analysis/Datasets/albrecht.csv'
    desharnais_path = './sw-effort-predictive-analysis/Datasets/02.desharnais.csv'
    
    results = []
    
    # Test với dữ liệu Albrecht
    if os.path.exists(albrecht_path):
        print("\n=== SO SÁNH TRÊN DỮ LIỆU ALBRECHT ===")
        albrecht_df = pd.read_csv(albrecht_path)
        
        actual_efforts = []
        predicted_efforts = {}
        
        for model_name in api.get_available_models():
            predicted_efforts[model_name] = []
        
        for _, row in albrecht_df.iterrows():
            size = row['AdjFP']
            actual_effort = row['Effort']
            actual_efforts.append(actual_effort)
            
            for model_name in api.get_available_models():
                result = api.predict('FP', size, model_name)
                pred_effort = result['predictions']['effort_pm']
                predicted_efforts[model_name].append(pred_effort)
        
        # Tính các chỉ số đánh giá
        for model_name in api.get_available_models():
            mae = mean_absolute_error(actual_efforts, predicted_efforts[model_name])
            rmse = np.sqrt(mean_squared_error(actual_efforts, predicted_efforts[model_name]))
            r2 = r2_score(actual_efforts, predicted_efforts[model_name])
            
            print(f"\nMô hình {model_name}:")
            print(f"  - MAE: {mae:.2f}")
            print(f"  - RMSE: {rmse:.2f}")
            print(f"  - R²: {r2:.2f}")
            
            results.append({
                'Dataset': 'Albrecht',
                'Model': model_name,
                'MAE': mae,
                'RMSE': rmse,
                'R2': r2
            })
        
        # Vẽ biểu đồ so sánh
        plt.figure(figsize=(12, 8))
        plt.scatter(actual_efforts, actual_efforts, color='black', label='Ideal')
        
        for model_name in api.get_available_models():
            plt.scatter(actual_efforts, predicted_efforts[model_name], label=model_name)
        
        plt.xlabel('Effort thực tế (người-tháng)')
        plt.ylabel('Effort dự đoán (người-tháng)')
        plt.title('So sánh dự đoán với giá trị thực tế trên dữ liệu Albrecht')
        plt.legend()
        plt.grid(True)
        plt.savefig('./comparison_results/albrecht_comparison.png')
    
    # Test với dữ liệu Desharnais
    if os.path.exists(desharnais_path):
        print("\n=== SO SÁNH TRÊN DỮ LIỆU DESHARNAIS ===")
        desharnais_df = pd.read_csv(desharnais_path)
        
        actual_efforts = []
        predicted_efforts = {}
        
        for model_name in api.get_available_models():
            predicted_efforts[model_name] = []
        
        for _, row in desharnais_df.iterrows():
            size = row['PointsAjust']
            actual_effort = row['Effort'] / 180  # Chuyển từ giờ sang người-tháng
            actual_efforts.append(actual_effort)
            
            for model_name in api.get_available_models():
                result = api.predict('FP', size, model_name)
                pred_effort = result['predictions']['effort_pm']
                predicted_efforts[model_name].append(pred_effort)
        
        # Tính các chỉ số đánh giá
        for model_name in api.get_available_models():
            mae = mean_absolute_error(actual_efforts, predicted_efforts[model_name])
            rmse = np.sqrt(mean_squared_error(actual_efforts, predicted_efforts[model_name]))
            r2 = r2_score(actual_efforts, predicted_efforts[model_name])
            
            print(f"\nMô hình {model_name}:")
            print(f"  - MAE: {mae:.2f}")
            print(f"  - RMSE: {rmse:.2f}")
            print(f"  - R²: {r2:.2f}")
            
            results.append({
                'Dataset': 'Desharnais',
                'Model': model_name,
                'MAE': mae,
                'RMSE': rmse,
                'R2': r2
            })
        
        # Vẽ biểu đồ so sánh
        plt.figure(figsize=(12, 8))
        plt.scatter(actual_efforts, actual_efforts, color='black', label='Ideal')
        
        for model_name in api.get_available_models():
            plt.scatter(actual_efforts, predicted_efforts[model_name], label=model_name)
        
        plt.xlabel('Effort thực tế (người-tháng)')
        plt.ylabel('Effort dự đoán (người-tháng)')
        plt.title('So sánh dự đoán với giá trị thực tế trên dữ liệu Desharnais')
        plt.legend()
        plt.grid(True)
        plt.savefig('./comparison_results/desharnais_comparison.png')
    
    # Tạo bảng so sánh tổng hợp
    if results:
        results_df = pd.DataFrame(results)
        print("\n=== BẢNG SO SÁNH TỔNG HỢP ===")
        print(results_df)
        
        # Lưu kết quả vào file
        os.makedirs('./comparison_results', exist_ok=True)
        results_df.to_csv('./comparison_results/model_evaluation.csv', index=False)
        print("\nĐã lưu kết quả vào ./comparison_results/model_evaluation.csv")

if __name__ == "__main__":
    test_on_real_data()
