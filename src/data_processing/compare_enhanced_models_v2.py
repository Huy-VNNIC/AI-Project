#!/usr/bin/env python3
"""
Script so sánh mô hình COCOMO II truyền thống với các mô hình ML đã cải tiến - Phiên bản nâng cao

Script này sẽ:
1. Tạo một bộ dữ liệu test với các kích thước khác nhau
2. Dự đoán bằng mô hình COCOMO II truyền thống
3. Dự đoán bằng các mô hình ML đã cải tiến
4. So sánh kết quả và đánh giá sai số
5. Trực quan hóa kết quả
6. Phân tích chi tiết ưu nhược điểm của từng mô hình
"""

import os
import sys
import math
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate
from pathlib import Path
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, mean_absolute_percentage_error

# Import module COCOMO II truyền thống
from demo import cocomo_ii_basic_estimate

# Import module API cho mô hình ML
from cocomo_ii_api import CocomoIIAPI

# Thiết lập trực quan hóa
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12

# Đường dẫn thư mục
BASE_DIR = Path('/home/huy/Huy-workspace/AI-Project')
RESULTS_DIR = './comparison_results/enhanced'
os.makedirs(RESULTS_DIR, exist_ok=True)

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

def generate_real_world_data():
    """
    Tạo dữ liệu test từ dữ liệu thực tế
    
    Returns:
        DataFrame chứa dữ liệu test từ dữ liệu thực tế
    """
    real_data = []
    
    # Thêm dữ liệu từ Albrecht
    try:
        albrecht_path = './sw-effort-predictive-analysis/Datasets/albrecht.csv'
        if os.path.exists(albrecht_path):
            albrecht_df = pd.read_csv(albrecht_path)
            
            for _, row in albrecht_df.iterrows():
                real_data.append({
                    'schema': 'FP',
                    'size': row['AdjFP'],
                    'description': f'Albrecht - {row["AdjFP"]} FP',
                    'actual_effort': row['Effort']
                })
    except Exception as e:
        print(f"Lỗi khi đọc dữ liệu Albrecht: {str(e)}")
    
    # Thêm dữ liệu từ Desharnais
    try:
        desharnais_path = './sw-effort-predictive-analysis/Datasets/02.desharnais.csv'
        if os.path.exists(desharnais_path):
            desharnais_df = pd.read_csv(desharnais_path)
            
            for _, row in desharnais_df.iterrows():
                real_data.append({
                    'schema': 'FP',
                    'size': row['PointsAjust'],
                    'description': f'Desharnais - {row["PointsAjust"]} FP',
                    'actual_effort': row['Effort'] / 180  # Chuyển giờ thành người-tháng
                })
    except Exception as e:
        print(f"Lỗi khi đọc dữ liệu Desharnais: {str(e)}")
    
    # Thêm dữ liệu đầu ra của các mô hình đã huấn luyện
    try:
        # Đọc dữ liệu đầu ra Albrecht
        albrecht_output_path = './effort-estimation-by-using-pre-trained-model/outputs/outputAlbrecht.csv'
        if os.path.exists(albrecht_output_path):
            albrecht_output_df = pd.read_csv(albrecht_output_path)
            
            for _, row in albrecht_output_df.iterrows():
                if 'FP' in row and 'Actual_Effort' in row:
                    real_data.append({
                        'schema': 'FP',
                        'size': row['FP'],
                        'description': f'Albrecht Output - {row["FP"]} FP',
                        'actual_effort': row['Actual_Effort']
                    })
        
        # Đọc dữ liệu đầu ra Desharnais
        desharnais_output_path = './effort-estimation-by-using-pre-trained-model/outputs/outputDesharnai.csv'
        if os.path.exists(desharnais_output_path):
            desharnais_output_df = pd.read_csv(desharnais_output_path)
            
            for _, row in desharnais_output_df.iterrows():
                if 'FP' in row and 'Actual_Effort' in row:
                    real_data.append({
                        'schema': 'FP',
                        'size': row['FP'],
                        'description': f'Desharnais Output - {row["FP"]} FP',
                        'actual_effort': row['Actual_Effort']
                    })
    except Exception as e:
        print(f"Lỗi khi đọc dữ liệu đầu ra: {str(e)}")
    
    if not real_data:
        print("Không tìm thấy dữ liệu thực tế phù hợp.")
        return pd.DataFrame()
    
    return pd.DataFrame(real_data)

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
        
        try:
            # Gọi hàm với đúng tham số
            trad_result = cocomo_ii_basic_estimate(size, size_type)
            
            # Lưu kết quả
            results.loc[idx, 'trad_effort_pm'] = trad_result['effort_pm']
            results.loc[idx, 'trad_time_months'] = trad_result['time_months']
            results.loc[idx, 'trad_developers'] = trad_result['developers']
        except Exception as e:
            print(f"Lỗi khi dự đoán truyền thống cho {schema} size={size}: {str(e)}")
    
    return results

def predict_ml_models(test_data, model_dir='./models/cocomo_ii_extended'):
    """
    Dự đoán bằng các mô hình ML đã huấn luyện
    
    Args:
        test_data: DataFrame chứa dữ liệu test
        model_dir: Đường dẫn đến thư mục chứa các mô hình
        
    Returns:
        DataFrame với kết quả dự đoán thêm vào
    """
    # Khởi tạo API
    try:
        api = CocomoIIAPI(model_dir)
        
        # Lấy danh sách mô hình có sẵn
        available_models = api.get_available_models()
        
        # Tạo bản sao DataFrame
        results = test_data.copy()
        
        # Thêm cột dự đoán cho từng mô hình
        for model_name in available_models:
            results[f'{model_name}_effort_pm'] = np.nan
            results[f'{model_name}_time_months'] = np.nan
            results[f'{model_name}_developers'] = np.nan
        
        # Dự đoán cho từng dòng
        for idx, row in results.iterrows():
            schema = row['schema']
            size = row['size']
            
            # Dự đoán với từng mô hình
            for model_name in available_models:
                try:
                    # Chuẩn bị đặc trưng bổ sung nếu có
                    extra_features = {}
                    
                    # Dự đoán
                    pred = api.predict(schema, size, model_name, extra_features)
                    
                    # Lưu kết quả
                    results.loc[idx, f'{model_name}_effort_pm'] = pred['predictions']['effort_pm']
                    results.loc[idx, f'{model_name}_time_months'] = pred['predictions']['time_months']
                    results.loc[idx, f'{model_name}_developers'] = pred['predictions']['developers']
                except Exception as e:
                    print(f"Lỗi khi dự đoán {model_name} cho {schema} size={size}: {str(e)}")
                    # In thêm chi tiết lỗi để debug
                    import traceback
                    traceback.print_exc()
        
        return results
    except Exception as e:
        print(f"Lỗi khi khởi tạo API: {str(e)}")
        return test_data

def compare_ml_with_traditional(results):
    """
    So sánh các mô hình ML với COCOMO II truyền thống
    
    Args:
        results: DataFrame chứa kết quả dự đoán
        
    Returns:
        DataFrame chứa các chỉ số đánh giá
    """
    # Lấy tên các mô hình ML
    ml_models = [col.replace('_effort_pm', '') for col in results.columns if col.endswith('_effort_pm') and col != 'trad_effort_pm']
    
    # Tạo cột tham chiếu cho COCOMO II truyền thống
    reference_col = 'trad_effort_pm'
    
    # Tính relative error và absolute relative error
    for model_name in ml_models:
        col_name = f'{model_name}_effort_pm'
        if col_name in results.columns:
            results[f'{model_name}_rel_error'] = (results[col_name] - results[reference_col]) / results[reference_col]
            results[f'{model_name}_abs_rel_error'] = np.abs(results[f'{model_name}_rel_error'])
    
    # Tính các chỉ số cho từng mô hình và từng schema
    metrics = []
    
    for schema in results['schema'].unique():
        schema_data = results[results['schema'] == schema]
        
        for model_name in ml_models:
            error_col = f'{model_name}_abs_rel_error'
            if error_col in schema_data.columns and not schema_data[error_col].isna().all():
                # Tính các chỉ số
                mmre = schema_data[error_col].mean()
                pred_25 = (schema_data[error_col] <= 0.25).mean()
                
                metrics.append({
                    'Schema': schema,
                    'Model': model_name,
                    'MMRE': mmre,
                    'PRED(25)': pred_25
                })
    
    # Tính chỉ số tổng thể
    for model_name in ml_models:
        error_col = f'{model_name}_abs_rel_error'
        if error_col in results.columns and not results[error_col].isna().all():
            mmre = results[error_col].mean()
            pred_25 = (results[error_col] <= 0.25).mean()
            
            metrics.append({
                'Schema': 'All',
                'Model': model_name,
                'MMRE': mmre,
                'PRED(25)': pred_25
            })
    
    return pd.DataFrame(metrics)

def calculate_real_metrics(results):
    """
    Tính toán các chỉ số đánh giá cho dữ liệu thực tế
    
    Args:
        results: DataFrame chứa kết quả dự đoán và dữ liệu thực tế
        
    Returns:
        DataFrame với các chỉ số đánh giá thêm vào
    """
    if 'actual_effort' not in results.columns:
        print("Không có cột actual_effort trong dữ liệu.")
        return pd.DataFrame()
    
    # Lấy tên các mô hình
    all_models = ['trad'] + [col.replace('_effort_pm', '') for col in results.columns if col.endswith('_effort_pm') and col != 'trad_effort_pm']
    
    # Tính relative error và absolute relative error
    for model_name in all_models:
        col_name = f'{model_name}_effort_pm'
        if col_name in results.columns:
            # Đảm bảo không có giá trị NaN
            valid_mask = results['actual_effort'].notna() & results[col_name].notna() & (results['actual_effort'] > 0)
            
            # Chỉ tính cho dữ liệu hợp lệ
            results.loc[valid_mask, f'{model_name}_real_rel_error'] = (results.loc[valid_mask, col_name] - results.loc[valid_mask, 'actual_effort']) / results.loc[valid_mask, 'actual_effort']
            results.loc[valid_mask, f'{model_name}_real_abs_rel_error'] = np.abs(results.loc[valid_mask, f'{model_name}_real_rel_error'])
    
    # Tính các chỉ số cho từng mô hình và từng schema
    metrics = []
    
    for schema in results['schema'].unique():
        schema_data = results[results['schema'] == schema]
        
        for model_name in all_models:
            error_col = f'{model_name}_real_abs_rel_error'
            pred_col = f'{model_name}_effort_pm'
            
            if error_col in schema_data.columns and not schema_data[error_col].isna().all():
                # Lọc dữ liệu hợp lệ
                valid_data = schema_data.dropna(subset=[error_col, 'actual_effort', pred_col])
                
                if len(valid_data) > 0:
                    # Tính các chỉ số
                    mmre = valid_data[error_col].mean()
                    pred_25 = (valid_data[error_col] <= 0.25).mean()
                    mae = np.abs(valid_data[pred_col] - valid_data['actual_effort']).mean()
                    rmse = np.sqrt(((valid_data[pred_col] - valid_data['actual_effort']) ** 2).mean())
                    
                    metrics.append({
                        'Schema': schema,
                        'Model': model_name,
                        'MMRE': mmre,
                        'PRED(25)': pred_25,
                        'MAE': mae,
                        'RMSE': rmse
                    })
    
    # Tính chỉ số tổng thể
    for model_name in all_models:
        error_col = f'{model_name}_real_abs_rel_error'
        pred_col = f'{model_name}_effort_pm'
        
        if error_col in results.columns and not results[error_col].isna().all():
            # Lọc dữ liệu hợp lệ
            valid_data = results.dropna(subset=[error_col, 'actual_effort', pred_col])
            
            if len(valid_data) > 0:
                mmre = valid_data[error_col].mean()
                pred_25 = (valid_data[error_col] <= 0.25).mean()
                mae = np.abs(valid_data[pred_col] - valid_data['actual_effort']).mean()
                rmse = np.sqrt(((valid_data[pred_col] - valid_data['actual_effort']) ** 2).mean())
                
                metrics.append({
                    'Schema': 'All',
                    'Model': model_name,
                    'MMRE': mmre,
                    'PRED(25)': pred_25,
                    'MAE': mae,
                    'RMSE': rmse
                })
    
    return pd.DataFrame(metrics)

def visualize_comparison(results, metrics):
    """
    Trực quan hóa kết quả so sánh
    
    Args:
        results: DataFrame chứa kết quả dự đoán
        metrics: DataFrame chứa các chỉ số đánh giá
    """
    # Lấy tên các mô hình ML
    ml_models = [col.replace('_effort_pm', '') for col in results.columns if col.endswith('_effort_pm') and col != 'trad_effort_pm']
    
    # 1. So sánh effort dự đoán
    # Chia theo schema
    for schema in results['schema'].unique():
        schema_data = results[results['schema'] == schema].sort_values('size')
        
        plt.figure(figsize=(14, 8))
        plt.plot(schema_data['size'], schema_data['trad_effort_pm'], 'k-', marker='o', linewidth=2, label='COCOMO II Traditional')
        
        for model_name in ml_models:
            col_name = f'{model_name}_effort_pm'
            if col_name in schema_data.columns and not schema_data[col_name].isna().all():
                plt.plot(schema_data['size'], schema_data[col_name], marker='s', label=model_name)
        
        plt.title(f'So sánh Effort (PM) dự đoán - Schema: {schema}')
        plt.xlabel(f'Size ({schema})')
        plt.ylabel('Effort (person-months)')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, f'comparison_effort_{schema}.png'))
        plt.close()
    
    # 2. So sánh sai số tương đối
    for schema in results['schema'].unique():
        schema_data = results[results['schema'] == schema].sort_values('size')
        
        plt.figure(figsize=(14, 8))
        
        for model_name in ml_models:
            error_col = f'{model_name}_rel_error'
            if error_col in schema_data.columns and not schema_data[error_col].isna().all():
                plt.plot(schema_data['size'], schema_data[error_col], marker='s', label=model_name)
        
        plt.axhline(y=0, color='r', linestyle='-')
        plt.title(f'Sai số tương đối so với COCOMO II truyền thống - Schema: {schema}')
        plt.xlabel(f'Size ({schema})')
        plt.ylabel('Relative Error')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, f'comparison_error_{schema}.png'))
        plt.close()
    
    # 3. So sánh các chỉ số đánh giá
    # Trực quan hóa MMRE
    plt.figure(figsize=(14, 6))
    
    # Lọc dữ liệu cho từng schema
    for i, schema in enumerate(['LOC', 'FP', 'UCP', 'All']):
        schema_metrics = metrics[metrics['Schema'] == schema]
        
        if not schema_metrics.empty:
            plt.subplot(1, 4, i+1)
            bars = plt.bar(schema_metrics['Model'], schema_metrics['MMRE'], color=['orange', 'green', 'red', 'blue'])
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
    plt.savefig(os.path.join(RESULTS_DIR, 'comparison_mmre.png'))
    plt.close()
    
    # Trực quan hóa PRED(25)
    plt.figure(figsize=(14, 6))
    
    # Lọc dữ liệu cho từng schema
    for i, schema in enumerate(['LOC', 'FP', 'UCP', 'All']):
        schema_metrics = metrics[metrics['Schema'] == schema]
        
        if not schema_metrics.empty:
            plt.subplot(1, 4, i+1)
            bars = plt.bar(schema_metrics['Model'], schema_metrics['PRED(25)'], color=['orange', 'green', 'red', 'blue'])
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
    plt.savefig(os.path.join(RESULTS_DIR, 'comparison_pred25.png'))
    plt.close()

def visualize_real_comparison(results, metrics):
    """
    Trực quan hóa kết quả so sánh với dữ liệu thực tế
    
    Args:
        results: DataFrame chứa kết quả dự đoán và dữ liệu thực tế
        metrics: DataFrame chứa các chỉ số đánh giá
    """
    if 'actual_effort' not in results.columns:
        return
    
    # Lấy tên các mô hình
    all_models = ['trad'] + [col.replace('_effort_pm', '') for col in results.columns if col.endswith('_effort_pm') and col != 'trad_effort_pm']
    
    # 1. So sánh effort dự đoán với actual effort
    # Chia theo schema
    for schema in results['schema'].unique():
        schema_data = results[results['schema'] == schema].sort_values('actual_effort')
        
        plt.figure(figsize=(14, 8))
        plt.scatter(range(len(schema_data)), schema_data['actual_effort'], color='black', marker='o', s=100, label='Actual Effort')
        
        for model_name in all_models:
            col_name = f'{model_name}_effort_pm'
            if col_name in schema_data.columns and not schema_data[col_name].isna().all():
                plt.scatter(range(len(schema_data)), schema_data[col_name], marker='s', label=model_name)
        
        plt.title(f'So sánh Effort (PM) dự đoán vs Actual - Schema: {schema}')
        plt.xlabel('Dự án (đã sắp xếp theo Actual Effort)')
        plt.ylabel('Effort (person-months)')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, f'real_comparison_effort_{schema}.png'))
        plt.close()
    
    # 2. So sánh sai số tương đối với actual effort
    for schema in results['schema'].unique():
        schema_data = results[results['schema'] == schema].sort_values('actual_effort')
        
        plt.figure(figsize=(14, 8))
        
        for model_name in all_models:
            error_col = f'{model_name}_real_rel_error'
            if error_col in schema_data.columns and not schema_data[error_col].isna().all():
                plt.plot(range(len(schema_data)), schema_data[error_col], marker='s', label=model_name)
        
        plt.axhline(y=0, color='r', linestyle='-')
        plt.title(f'Sai số tương đối so với Actual Effort - Schema: {schema}')
        plt.xlabel('Dự án (đã sắp xếp theo Actual Effort)')
        plt.ylabel('Relative Error')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, f'real_comparison_error_{schema}.png'))
        plt.close()
    
    # 3. So sánh các chỉ số đánh giá
    # Trực quan hóa MMRE
    plt.figure(figsize=(10, 6))
    
    all_schema_metrics = metrics[metrics['Schema'] == 'All']
    if not all_schema_metrics.empty:
        bars = plt.bar(all_schema_metrics['Model'], all_schema_metrics['MMRE'], color=['blue', 'orange', 'green', 'red'])
        plt.title('MMRE so với Actual Effort')
        plt.ylabel('MMRE (thấp hơn = tốt hơn)')
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Thêm giá trị lên các cột
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{height:.3f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'real_comparison_mmre.png'))
    plt.close()
    
    # Trực quan hóa PRED(25)
    plt.figure(figsize=(10, 6))
    
    if not all_schema_metrics.empty:
        bars = plt.bar(all_schema_metrics['Model'], all_schema_metrics['PRED(25)'], color=['blue', 'orange', 'green', 'red'])
        plt.title('PRED(25) so với Actual Effort')
        plt.ylabel('PRED(25) (cao hơn = tốt hơn)')
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Thêm giá trị lên các cột
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{height:.3f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'real_comparison_pred25.png'))
    plt.close()
    
    # Trực quan hóa MAE và RMSE
    plt.figure(figsize=(14, 6))
    
    if not all_schema_metrics.empty:
        # MAE
        plt.subplot(1, 2, 1)
        bars = plt.bar(all_schema_metrics['Model'], all_schema_metrics['MAE'], color=['blue', 'orange', 'green', 'red'])
        plt.title('MAE so với Actual Effort')
        plt.ylabel('MAE (thấp hơn = tốt hơn)')
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Thêm giá trị lên các cột
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{height:.3f}', ha='center', va='bottom')
        
        # RMSE
        plt.subplot(1, 2, 2)
        bars = plt.bar(all_schema_metrics['Model'], all_schema_metrics['RMSE'], color=['blue', 'orange', 'green', 'red'])
        plt.title('RMSE so với Actual Effort')
        plt.ylabel('RMSE (thấp hơn = tốt hơn)')
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Thêm giá trị lên các cột
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{height:.3f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'real_comparison_error_metrics.png'))
    plt.close()

def create_comparison_table(metrics, real_metrics=None):
    """
    Tạo bảng so sánh các mô hình
    
    Args:
        metrics: DataFrame chứa các chỉ số đánh giá
        real_metrics: DataFrame chứa các chỉ số đánh giá với dữ liệu thực tế
        
    Returns:
        Markdown table
    """
    # Tạo bảng so sánh với dữ liệu tổng hợp
    table_rows = []
    
    # Thêm header
    if real_metrics is not None:
        header = ["Model", "Schema", "MMRE vs COCOMO", "PRED(25) vs COCOMO", "MMRE vs Actual", "PRED(25) vs Actual", "MAE", "RMSE"]
    else:
        header = ["Model", "Schema", "MMRE vs COCOMO", "PRED(25) vs COCOMO"]
    
    table_rows.append(header)
    
    # Thêm dữ liệu
    for schema in ['LOC', 'FP', 'UCP', 'All']:
        schema_metrics = metrics[metrics['Schema'] == schema]
        
        for _, row in schema_metrics.iterrows():
            model_name = row['Model']
            
            if real_metrics is not None:
                # Tìm dữ liệu tương ứng trong real_metrics
                real_row = real_metrics[(real_metrics['Schema'] == schema) & (real_metrics['Model'] == model_name)]
                
                if not real_row.empty:
                    table_rows.append([
                        model_name, 
                        schema, 
                        f"{row['MMRE']:.4f}", 
                        f"{row['PRED(25)']:.4f}",
                        f"{real_row['MMRE'].values[0]:.4f}",
                        f"{real_row['PRED(25)'].values[0]:.4f}",
                        f"{real_row['MAE'].values[0]:.4f}",
                        f"{real_row['RMSE'].values[0]:.4f}"
                    ])
                else:
                    table_rows.append([
                        model_name, 
                        schema, 
                        f"{row['MMRE']:.4f}", 
                        f"{row['PRED(25)']:.4f}",
                        "N/A", "N/A", "N/A", "N/A"
                    ])
            else:
                table_rows.append([
                    model_name, 
                    schema, 
                    f"{row['MMRE']:.4f}", 
                    f"{row['PRED(25)']:.4f}"
                ])
    
    # Tạo table markdown
    table_md = tabulate(table_rows, headers="firstrow", tablefmt="pipe")
    
    return table_md

def analyze_model_strengths(results, metrics, real_metrics):
    """
    Phân tích ưu nhược điểm của từng mô hình
    
    Args:
        results: DataFrame chứa kết quả dự đoán
        metrics: DataFrame chứa các chỉ số đánh giá
        real_metrics: DataFrame chứa các chỉ số đánh giá với dữ liệu thực tế
        
    Returns:
        Dictionary chứa phân tích
    """
    analysis = {}
    
    # Lấy tên các mô hình
    ml_models = [col.replace('_effort_pm', '') for col in results.columns if col.endswith('_effort_pm') and col != 'trad_effort_pm']
    
    # Phân tích COCOMO II truyền thống
    trad_analysis = {
        "strengths": [],
        "weaknesses": [],
        "best_for": []
    }
    
    # Phân tích dựa trên dữ liệu thực tế
    if not real_metrics.empty:
        trad_real = real_metrics[(real_metrics['Model'] == 'trad') & (real_metrics['Schema'] == 'All')]
        if not trad_real.empty:
            trad_mmre = trad_real['MMRE'].values[0]
            trad_pred25 = trad_real['PRED(25)'].values[0]
            
            if trad_pred25 < 0.25:
                trad_analysis["weaknesses"].append(f"Độ chính xác thấp trên dữ liệu thực tế (PRED(25) = {trad_pred25:.4f})")
            else:
                trad_analysis["strengths"].append(f"Độ chính xác chấp nhận được trên dữ liệu thực tế (PRED(25) = {trad_pred25:.4f})")
            
            if trad_mmre > 1.0:
                trad_analysis["weaknesses"].append(f"Sai số lớn trên dữ liệu thực tế (MMRE = {trad_mmre:.4f})")
    
    # Thêm các điểm mạnh/yếu chung
    trad_analysis["strengths"].extend([
        "Đơn giản, dễ triển khai",
        "Không yêu cầu dữ liệu huấn luyện",
        "Dựa trên nền tảng nghiên cứu lâu năm"
    ])
    
    trad_analysis["weaknesses"].extend([
        "Không tận dụng được các đặc trưng phong phú từ dữ liệu",
        "Công thức cố định, ít linh hoạt",
        "Không thể tự điều chỉnh theo dữ liệu mới"
    ])
    
    trad_analysis["best_for"].extend([
        "Các dự án có ít dữ liệu lịch sử",
        "Ước lượng sơ bộ giai đoạn đầu dự án",
        "Dự án tuân theo các quy trình truyền thống"
    ])
    
    analysis['COCOMO II Traditional'] = trad_analysis
    
    # Phân tích từng mô hình ML
    for model_name in ml_models:
        model_analysis = {
            "strengths": [],
            "weaknesses": [],
            "best_for": []
        }
        
        # Phân tích dựa trên dữ liệu tổng hợp
        model_all = metrics[(metrics['Model'] == model_name) & (metrics['Schema'] == 'All')]
        if not model_all.empty:
            model_mmre = model_all['MMRE'].values[0]
            model_pred25 = model_all['PRED(25)'].values[0]
            
            # So với COCOMO II truyền thống
            if model_mmre < 0.5:  # Sai số nhỏ so với COCOMO
                model_analysis["strengths"].append(f"Gần với COCOMO II truyền thống (MMRE = {model_mmre:.4f})")
            
        # Phân tích dựa trên dữ liệu thực tế
        if not real_metrics.empty:
            model_real = real_metrics[(real_metrics['Model'] == model_name) & (real_metrics['Schema'] == 'All')]
            if not model_real.empty:
                model_real_mmre = model_real['MMRE'].values[0]
                model_real_pred25 = model_real['PRED(25)'].values[0]
                
                # So sánh với COCOMO II truyền thống trên dữ liệu thực tế
                trad_real = real_metrics[(real_metrics['Model'] == 'trad') & (real_metrics['Schema'] == 'All')]
                if not trad_real.empty:
                    trad_real_mmre = trad_real['MMRE'].values[0]
                    trad_real_pred25 = trad_real['PRED(25)'].values[0]
                    
                    if model_real_mmre < trad_real_mmre:
                        model_analysis["strengths"].append(f"Sai số thấp hơn COCOMO II trên dữ liệu thực tế (MMRE = {model_real_mmre:.4f} vs {trad_real_mmre:.4f})")
                    else:
                        model_analysis["weaknesses"].append(f"Sai số cao hơn COCOMO II trên dữ liệu thực tế (MMRE = {model_real_mmre:.4f} vs {trad_real_mmre:.4f})")
                    
                    if model_real_pred25 > trad_real_pred25:
                        model_analysis["strengths"].append(f"Độ chính xác cao hơn COCOMO II trên dữ liệu thực tế (PRED(25) = {model_real_pred25:.4f} vs {trad_real_pred25:.4f})")
                    else:
                        model_analysis["weaknesses"].append(f"Độ chính xác thấp hơn COCOMO II trên dữ liệu thực tế (PRED(25) = {model_real_pred25:.4f} vs {trad_real_pred25:.4f})")
        
        # Thêm các điểm mạnh/yếu đặc trưng cho từng loại mô hình
        if model_name == 'Linear_Regression':
            model_analysis["strengths"].extend([
                "Đơn giản, dễ hiểu, giải thích được",
                "Huấn luyện nhanh",
                "Hiệu quả với tập dữ liệu nhỏ"
            ])
            
            model_analysis["weaknesses"].extend([
                "Không thể mô hình hóa quan hệ phi tuyến phức tạp",
                "Nhạy cảm với dữ liệu outlier",
                "Giả định quan hệ tuyến tính giữa các biến"
            ])
            
            model_analysis["best_for"].extend([
                "Dự án có quan hệ tuyến tính rõ ràng giữa kích thước và nỗ lực",
                "Các trường hợp cần giải thích rõ ràng về cách ước lượng"
            ])
            
        elif model_name == 'Decision_Tree':
            model_analysis["strengths"].extend([
                "Dễ hiểu và giải thích",
                "Xử lý được cả dữ liệu số và phân loại",
                "Không yêu cầu chuẩn hóa dữ liệu"
            ])
            
            model_analysis["weaknesses"].extend([
                "Có thể quá khớp với dữ liệu huấn luyện",
                "Không ổn định (thay đổi nhỏ trong dữ liệu có thể dẫn đến cây khác biệt)",
                "Hiệu suất không cao như các mô hình phức tạp hơn"
            ])
            
            model_analysis["best_for"].extend([
                "Dự án cần phân loại theo đặc điểm rõ ràng",
                "Trường hợp cần quy tắc quyết định rõ ràng"
            ])
            
        elif model_name == 'Random_Forest':
            model_analysis["strengths"].extend([
                "Mạnh mẽ với dữ liệu nhiễu và outlier",
                "Giảm thiểu overfitting so với Decision Tree",
                "Xử lý hiệu quả tập dữ liệu lớn với nhiều đặc trưng"
            ])
            
            model_analysis["weaknesses"].extend([
                "Phức tạp hơn, khó giải thích",
                "Huấn luyện chậm hơn các mô hình đơn giản",
                "Cần nhiều dữ liệu để hoạt động tốt"
            ])
            
            model_analysis["best_for"].extend([
                "Dự án phức tạp với nhiều yếu tố ảnh hưởng",
                "Tập dữ liệu có nhiều đặc trưng"
            ])
            
        elif model_name == 'Gradient_Boosting':
            model_analysis["strengths"].extend([
                "Hiệu suất cao, thường có kết quả tốt nhất",
                "Xử lý tốt các quan hệ phi tuyến phức tạp",
                "Tích hợp quá trình học từ lỗi"
            ])
            
            model_analysis["weaknesses"].extend([
                "Phức tạp, khó giải thích",
                "Nhạy cảm với hyperparameter",
                "Dễ bị overfitting nếu không điều chỉnh cẩn thận"
            ])
            
            model_analysis["best_for"].extend([
                "Dự án cần độ chính xác cao nhất",
                "Có đủ dữ liệu để huấn luyện và điều chỉnh tham số"
            ])
        
        analysis[model_name] = model_analysis
    
    return analysis

def main():
    print("===== So sánh mô hình COCOMO II và các mô hình ML cải tiến =====")
    
    # 1. Tạo dữ liệu test
    print("\n1. Tạo dữ liệu test...")
    test_data = generate_test_data()
    print(f"  - Đã tạo {len(test_data)} mẫu dữ liệu test")
    
    # 2. Dự đoán bằng mô hình COCOMO II truyền thống
    print("\n2. Dự đoán bằng mô hình COCOMO II truyền thống...")
    results = predict_traditional_cocomo(test_data)
    print("  - Đã hoàn thành dự đoán")
    
    # 3. Dự đoán bằng các mô hình ML
    print("\n3. Dự đoán bằng các mô hình ML...")
    results = predict_ml_models(results)
    print("  - Đã hoàn thành dự đoán")
    
    # 4. So sánh các mô hình ML với COCOMO II truyền thống
    print("\n4. So sánh các mô hình...")
    metrics = compare_ml_with_traditional(results)
    
    # Lưu kết quả
    results.to_csv(os.path.join(RESULTS_DIR, 'comparison_results.csv'), index=False)
    metrics.to_csv(os.path.join(RESULTS_DIR, 'comparison_metrics.csv'), index=False)
    
    # 5. Trực quan hóa kết quả
    print("\n5. Trực quan hóa kết quả...")
    visualize_comparison(results, metrics)
    
    # 6. So sánh trên dữ liệu thực tế
    print("\n6. So sánh trên dữ liệu thực tế...")
    real_data = generate_real_world_data()
    
    if not real_data.empty:
        print(f"  - Đã tạo {len(real_data)} mẫu dữ liệu thực tế")
        
        # Dự đoán
        real_results = predict_traditional_cocomo(real_data)
        real_results = predict_ml_models(real_results)
        
        # Tính toán các chỉ số
        real_metrics = calculate_real_metrics(real_results)
        
        # Lưu kết quả
        real_results.to_csv(os.path.join(RESULTS_DIR, 'real_comparison_results.csv'), index=False)
        real_metrics.to_csv(os.path.join(RESULTS_DIR, 'real_comparison_metrics.csv'), index=False)
        
        # Trực quan hóa
        visualize_real_comparison(real_results, real_metrics)
        
        # 7. Tạo bảng so sánh
        print("\n7. Tạo bảng so sánh...")
        comparison_table = create_comparison_table(metrics, real_metrics)
        
        with open(os.path.join(RESULTS_DIR, 'comparison_table.md'), 'w') as f:
            f.write(comparison_table)
        
        # 8. Phân tích ưu nhược điểm
        print("\n8. Phân tích ưu nhược điểm của các mô hình...")
        model_analysis = analyze_model_strengths(results, metrics, real_metrics)
        
        with open(os.path.join(RESULTS_DIR, 'model_analysis.json'), 'w') as f:
            json.dump(model_analysis, f, indent=4)
        
        # Tạo báo cáo markdown
        with open(os.path.join(RESULTS_DIR, 'comparison_report.md'), 'w') as f:
            f.write("# Báo cáo so sánh các mô hình ước lượng nỗ lực phần mềm\n\n")
            
            f.write("## 1. Bảng so sánh các chỉ số\n\n")
            f.write(comparison_table)
            f.write("\n\n")
            
            f.write("## 2. Phân tích các mô hình\n\n")
            
            for model_name, analysis in model_analysis.items():
                f.write(f"### {model_name}\n\n")
                
                f.write("**Điểm mạnh:**\n\n")
                for strength in analysis['strengths']:
                    f.write(f"- {strength}\n")
                f.write("\n")
                
                f.write("**Điểm yếu:**\n\n")
                for weakness in analysis['weaknesses']:
                    f.write(f"- {weakness}\n")
                f.write("\n")
                
                f.write("**Phù hợp nhất cho:**\n\n")
                for best_for in analysis['best_for']:
                    f.write(f"- {best_for}\n")
                f.write("\n")
        
        print(f"\nĐã lưu báo cáo so sánh tại {os.path.join(RESULTS_DIR, 'comparison_report.md')}")
    else:
        print("  - Không tìm thấy dữ liệu thực tế phù hợp")
    
    print("\n===== Hoàn thành so sánh =====")

if __name__ == "__main__":
    main()
