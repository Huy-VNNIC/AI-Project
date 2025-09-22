#!/usr/bin/env python3
"""
Script so sánh mô hình COCOMO II truyền thống với các mô hình ML

Script này sẽ:
1. Tạo một bộ dữ liệu test với các kích thước khác nhau
2. Dự đoán bằng mô hình COCOMO II truyền thống
3. Dự đoán bằng các mô hình ML đã huấn luyện
4. So sánh kết quả và đánh giá sai số
5. Trực quan hóa kết quả
"""

import os
import sys
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate

# Import module COCOMO II truyền thống
from demo import cocomo_ii_basic_estimate

# Import module API cho mô hình ML
from src.models.cocomo.cocomo_ii_api import CocomoIIAPI

# Thiết lập trực quan hóa
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12

def generate_test_data():
    """
    Tạo dữ liệu test cho so sánh các mô hình
    
    Returns:
        DataFrame chứa dữ liệu test
    """
    # Tạo dữ liệu test cho 3 schema
    loc_sizes = [1, 5, 10, 15, 20, 25, 30, 40, 50, 75, 100]
    fp_sizes = [50, 100, 200, 300, 400, 500, 600, 800, 1000, 1500, 2000]
    ucp_sizes = [30, 60, 100, 150, 200, 250, 300, 350, 400, 500, 600]
    
    # Tạo DataFrame
    test_data = []
    
    # Thêm dữ liệu LOC
    for size in loc_sizes:
        test_data.append({
            'schema': 'LOC',
            'size': size,
            'description': f'{size} KLOC'
        })
    
    # Thêm dữ liệu FP
    for size in fp_sizes:
        test_data.append({
            'schema': 'FP',
            'size': size,
            'description': f'{size} Function Points'
        })
    
    # Thêm dữ liệu UCP
    for size in ucp_sizes:
        test_data.append({
            'schema': 'UCP',
            'size': size,
            'description': f'{size} Use Case Points'
        })
    
    return pd.DataFrame(test_data)

def predict_traditional_cocomo(test_data):
    """
    Dự đoán bằng mô hình COCOMO II truyền thống
    
    Args:
        test_data: DataFrame chứa dữ liệu test
        
    Returns:
        DataFrame với kết quả dự đoán thêm vào
    """
    # Tạo bản sao DataFrame
    results = test_data.copy()
    
    # Thêm cột dự đoán
    results['trad_effort_pm'] = np.nan
    results['trad_time_months'] = np.nan
    results['trad_developers'] = np.nan
    
    # Dự đoán cho từng dòng
    for idx, row in results.iterrows():
        schema = row['schema'].lower()
        size = row['size']
        
        # Dự đoán bằng mô hình truyền thống
        if schema == 'loc':
            size_type = 'kloc'
        elif schema == 'fp':
            size_type = 'fp'
        elif schema == 'ucp':
            size_type = 'ucp'
        else:
            continue
        
        trad_result = cocomo_ii_basic_estimate(size, size_type)
        
        # Lưu kết quả
        results.loc[idx, 'trad_effort_pm'] = trad_result['effort_pm']
        results.loc[idx, 'trad_time_months'] = trad_result['time_months']
        results.loc[idx, 'trad_developers'] = trad_result['developers']
    
    return results

def predict_ml_models(test_data):
    """
    Dự đoán bằng các mô hình ML đã huấn luyện
    
    Args:
        test_data: DataFrame chứa dữ liệu test
        
    Returns:
        DataFrame với kết quả dự đoán thêm vào
    """
    # Khởi tạo API
    try:
        api = CocomoIIAPI('./models/cocomo_ii_extended')
        
        # Tạo bản sao DataFrame
        results = test_data.copy()
        
        # Thêm cột dự đoán cho từng mô hình
        for model_name in ['Linear_Regression', 'Decision_Tree', 'Random_Forest']:
            results[f'{model_name}_effort_pm'] = np.nan
            results[f'{model_name}_time_months'] = np.nan
            results[f'{model_name}_developers'] = np.nan
        
        # Dự đoán cho từng dòng
        for idx, row in results.iterrows():
            schema = row['schema']
            size = row['size']
            
            # Dự đoán với từng mô hình
            for model_name in ['Linear_Regression', 'Decision_Tree', 'Random_Forest']:
                try:
                    ml_result = api.predict(schema, size, model_name=model_name)
                    
                    # Lưu kết quả
                    results.loc[idx, f'{model_name}_effort_pm'] = ml_result['predictions']['effort_pm']
                    results.loc[idx, f'{model_name}_time_months'] = ml_result['predictions']['time_months']
                    results.loc[idx, f'{model_name}_developers'] = ml_result['predictions']['developers']
                except Exception as e:
                    print(f"Lỗi khi dự đoán với {model_name} cho {schema} size={size}: {str(e)}")
        
        return results
    except Exception as e:
        print(f"Lỗi khi khởi tạo API: {str(e)}")
        sys.exit(1)

def calculate_metrics(results):
    """
    Tính toán các chỉ số đánh giá
    
    Args:
        results: DataFrame chứa kết quả dự đoán
        
    Returns:
        DataFrame với các chỉ số đánh giá thêm vào
    """
    # Giả sử dữ liệu COCOMO II truyền thống là "ground truth" để so sánh
    # Trong thực tế, có thể dùng dữ liệu thực tế nếu có
    
    # Tính relative error và absolute relative error
    for model_name in ['Linear_Regression', 'Decision_Tree', 'Random_Forest']:
        results[f'{model_name}_rel_error'] = (results[f'{model_name}_effort_pm'] - results['trad_effort_pm']) / results['trad_effort_pm']
        results[f'{model_name}_abs_rel_error'] = np.abs(results[f'{model_name}_rel_error'])
    
    # Tính các chỉ số cho từng mô hình và từng schema
    metrics = []
    
    for schema in results['schema'].unique():
        schema_data = results[results['schema'] == schema]
        
        for model_name in ['Linear_Regression', 'Decision_Tree', 'Random_Forest']:
            # Tính các chỉ số
            mmre = schema_data[f'{model_name}_abs_rel_error'].mean()
            pred_25 = (schema_data[f'{model_name}_abs_rel_error'] <= 0.25).mean()
            
            metrics.append({
                'Schema': schema,
                'Model': model_name,
                'MMRE': mmre,
                'PRED(25)': pred_25
            })
    
    # Tính chỉ số tổng thể
    for model_name in ['Linear_Regression', 'Decision_Tree', 'Random_Forest']:
        mmre = results[f'{model_name}_abs_rel_error'].mean()
        pred_25 = (results[f'{model_name}_abs_rel_error'] <= 0.25).mean()
        
        metrics.append({
            'Schema': 'All',
            'Model': model_name,
            'MMRE': mmre,
            'PRED(25)': pred_25
        })
    
    return pd.DataFrame(metrics)

def visualize_comparison(results, metrics):
    """
    Trực quan hóa kết quả so sánh
    
    Args:
        results: DataFrame chứa kết quả dự đoán
        metrics: DataFrame chứa các chỉ số đánh giá
    """
    # 1. So sánh effort dự đoán
    # Chia theo schema
    for schema in results['schema'].unique():
        schema_data = results[results['schema'] == schema].sort_values('size')
        
        plt.figure(figsize=(14, 8))
        plt.plot(schema_data['size'], schema_data['trad_effort_pm'], 'k-', marker='o', linewidth=2, label='COCOMO II Traditional')
        plt.plot(schema_data['size'], schema_data['Linear_Regression_effort_pm'], 'b-', marker='s', label='Linear Regression')
        plt.plot(schema_data['size'], schema_data['Decision_Tree_effort_pm'], 'orange', marker='^', label='Decision Tree')
        plt.plot(schema_data['size'], schema_data['Random_Forest_effort_pm'], 'g-', marker='d', label='Random Forest')
        
        plt.title(f'So sánh Effort (PM) dự đoán - Schema: {schema}')
        plt.xlabel(f'Size ({schema})')
        plt.ylabel('Effort (person-months)')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f'comparison_effort_{schema}.png')
        plt.show()
    
    # 2. So sánh sai số tương đối
    for schema in results['schema'].unique():
        schema_data = results[results['schema'] == schema].sort_values('size')
        
        plt.figure(figsize=(14, 8))
        plt.plot(schema_data['size'], schema_data['Linear_Regression_rel_error'], 'b-', marker='s', label='Linear Regression')
        plt.plot(schema_data['size'], schema_data['Decision_Tree_rel_error'], 'orange', marker='^', label='Decision Tree')
        plt.plot(schema_data['size'], schema_data['Random_Forest_rel_error'], 'g-', marker='d', label='Random Forest')
        plt.axhline(y=0, color='r', linestyle='-')
        
        plt.title(f'Sai số tương đối so với COCOMO II truyền thống - Schema: {schema}')
        plt.xlabel(f'Size ({schema})')
        plt.ylabel('Relative Error')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f'comparison_error_{schema}.png')
        plt.show()
    
    # 3. So sánh các chỉ số đánh giá
    # Trực quan hóa MMRE
    plt.figure(figsize=(14, 6))
    
    # Lọc dữ liệu cho từng schema
    for i, schema in enumerate(['LOC', 'FP', 'UCP', 'All']):
        schema_metrics = metrics[metrics['Schema'] == schema]
        
        plt.subplot(1, 4, i+1)
        bars = plt.bar(schema_metrics['Model'], schema_metrics['MMRE'], color=['blue', 'orange', 'green'])
        plt.title(f'MMRE - {schema}')
        plt.ylabel('MMRE (thấp hơn = tốt hơn)')
        plt.xticks(rotation=90)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Thêm giá trị lên các cột
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{height:.3f}', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig('comparison_mmre.png')
    plt.show()
    
    # Trực quan hóa PRED(25)
    plt.figure(figsize=(14, 6))
    
    # Lọc dữ liệu cho từng schema
    for i, schema in enumerate(['LOC', 'FP', 'UCP', 'All']):
        schema_metrics = metrics[metrics['Schema'] == schema]
        
        plt.subplot(1, 4, i+1)
        bars = plt.bar(schema_metrics['Model'], schema_metrics['PRED(25)'], color=['blue', 'orange', 'green'])
        plt.title(f'PRED(25) - {schema}')
        plt.ylabel('PRED(25) (cao hơn = tốt hơn)')
        plt.xticks(rotation=90)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Thêm giá trị lên các cột
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{height:.3f}', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig('comparison_pred25.png')
    plt.show()

def main():
    """
    Hàm chính để thực hiện so sánh
    """
    print("\n" + "="*50)
    print("So sánh Mô hình COCOMO II Truyền thống vs. Mô hình ML")
    print("="*50)
    
    # 1. Tạo dữ liệu test
    print("\n1. Tạo dữ liệu test...")
    test_data = generate_test_data()
    print(f"  - Đã tạo {len(test_data)} mẫu test")
    
    # 2. Dự đoán bằng mô hình COCOMO II truyền thống
    print("\n2. Dự đoán với mô hình COCOMO II truyền thống...")
    results = predict_traditional_cocomo(test_data)
    print(f"  - Đã dự đoán xong với mô hình truyền thống")
    
    # 3. Dự đoán bằng các mô hình ML
    print("\n3. Dự đoán với các mô hình ML...")
    results = predict_ml_models(results)
    print(f"  - Đã dự đoán xong với các mô hình ML")
    
    # 4. Tính toán các chỉ số đánh giá
    print("\n4. Tính toán các chỉ số đánh giá...")
    metrics = calculate_metrics(results)
    print(f"  - Đã tính toán xong các chỉ số đánh giá")
    
    # 5. Hiển thị kết quả
    print("\n5. Kết quả so sánh:")
    
    # In bảng chỉ số đánh giá
    print("\nBảng chỉ số đánh giá:")
    print(tabulate(metrics, headers='keys', tablefmt='pretty', showindex=False))
    
    # Lưu kết quả
    results.to_csv('comparison_results.csv', index=False)
    metrics.to_csv('comparison_metrics.csv', index=False)
    
    print(f"\n  - Đã lưu kết quả chi tiết vào file comparison_results.csv")
    print(f"  - Đã lưu chỉ số đánh giá vào file comparison_metrics.csv")
    
    # 6. Trực quan hóa kết quả
    print("\n6. Trực quan hóa kết quả...")
    visualize_comparison(results, metrics)
    print(f"  - Đã tạo và hiển thị các biểu đồ so sánh")
    print(f"  - Các biểu đồ đã được lưu dưới dạng file PNG")
    
    print("\n" + "="*50)
    print("Hoàn thành so sánh mô hình!")
    print("="*50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperating cancelled by user.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
