#!/usr/bin/env python3
"""
Script so sánh mô hình COCOMO II truyền thống với các mô hình ML đã cải tiến

Script này sẽ:
1. Tạo một bộ dữ liệu test với các kích thước khác nhau
2. Dự đoán bằng mô hình COCOMO II truyền thống
3. Dự đoán bằng các mô hình ML đã cải tiến
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
from pathlib import Path
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, mean_absolute_percentage_error

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

# Đường dẫn thư mục
BASE_DIR = Path('/home/huy/Huy-workspace/AI-Project')
RESULTS_DIR = './comparison_results'
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
            
            # Tạo extra_features nếu có
            extra_features = {}
            for col in row.index:
                if col not in ['schema', 'size', 'description'] and not col.startswith('trad_') and not any(col.startswith(f'{m}_') for m in available_models):
                    extra_features[col] = row[col]
            
            # Dự đoán với từng mô hình
            for model_name in available_models:
                try:
                    ml_result = api.predict(schema, size, model_name=model_name, extra_features=extra_features)
                    
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

def calculate_metrics(results, reference_col='trad_effort_pm'):
    """
    Tính toán các chỉ số đánh giá
    
    Args:
        results: DataFrame chứa kết quả dự đoán
        reference_col: Tên cột tham chiếu cho việc tính toán sai số
        
    Returns:
        DataFrame với các chỉ số đánh giá thêm vào
    """
    # Lấy tên các mô hình ML
    ml_models = [col.replace('_effort_pm', '') for col in results.columns if col.endswith('_effort_pm') and col != reference_col]
    
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
            if error_col in schema_data.columns:
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
        if error_col in results.columns:
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
            results[f'{model_name}_real_rel_error'] = (results[col_name] - results['actual_effort']) / results['actual_effort']
            results[f'{model_name}_real_abs_rel_error'] = np.abs(results[f'{model_name}_real_rel_error'])
    
    # Tính các chỉ số cho từng mô hình và từng schema
    metrics = []
    
    for schema in results['schema'].unique():
        schema_data = results[results['schema'] == schema]
        
        for model_name in all_models:
            error_col = f'{model_name}_real_abs_rel_error'
            if error_col in schema_data.columns:
                # Tính các chỉ số
                mmre = schema_data[error_col].mean()
                pred_25 = (schema_data[error_col] <= 0.25).mean()
                mae = np.abs(schema_data[f'{model_name}_effort_pm'] - schema_data['actual_effort']).mean()
                rmse = np.sqrt(((schema_data[f'{model_name}_effort_pm'] - schema_data['actual_effort']) ** 2).mean())
                
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
        if error_col in results.columns:
            mmre = results[error_col].mean()
            pred_25 = (results[error_col] <= 0.25).mean()
            mae = np.abs(results[f'{model_name}_effort_pm'] - results['actual_effort']).mean()
            rmse = np.sqrt(((results[f'{model_name}_effort_pm'] - results['actual_effort']) ** 2).mean())
            
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
            if col_name in schema_data.columns:
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
            if error_col in schema_data.columns:
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
        
        plt.subplot(1, 4, i+1)
        bars = plt.bar(schema_metrics['Model'], schema_metrics['MMRE'], color=['blue', 'orange', 'green', 'red'])
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
        
        plt.subplot(1, 4, i+1)
        bars = plt.bar(schema_metrics['Model'], schema_metrics['PRED(25)'], color=['blue', 'orange', 'green', 'red'])
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
            if col_name in schema_data.columns:
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
            if error_col in schema_data.columns:
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

def compare_real_world_data(verbose=True):
    """
    So sánh mô hình ML và COCOMO II truyền thống trên dữ liệu thực tế
    
    Returns:
        DataFrame chứa kết quả so sánh
    """
    if verbose:
        print("\n=== So sánh mô hình trên dữ liệu thực tế ===")
    
    # Tạo đối tượng API mô hình ML
    model_api = CocomoIIAPI()
    
    # Đọc dữ liệu thực tế Albrecht
    albrecht_file = os.path.join(BASE_DIR, 'effort-estimation-by-using-pre-trained-model', 'outputs', 'outputAlbrecht.csv')
    
    if not os.path.exists(albrecht_file):
        if verbose:
            print("  - Không tìm thấy dữ liệu thực tế Albrecht")
        albrecht_df = None
    else:
        albrecht_df = pd.read_csv(albrecht_file)
        if verbose:
            print(f"  - Đã đọc {len(albrecht_df)} mẫu dữ liệu thực tế Albrecht")
    
    # Đọc dữ liệu thực tế Desharnais
    desharnais_file = os.path.join(BASE_DIR, 'effort-estimation-by-using-pre-trained-model', 'outputs', 'outputDesharnai.csv')
    
    if not os.path.exists(desharnais_file):
        if verbose:
            print("  - Không tìm thấy dữ liệu thực tế Desharnais")
        desharnais_df = None
    else:
        desharnais_df = pd.read_csv(desharnais_file)
        if verbose:
            print(f"  - Đã đọc {len(desharnais_df)} mẫu dữ liệu thực tế Desharnais")
    
    results = []
    
    # So sánh trên dữ liệu Albrecht
    if albrecht_df is not None:
        if verbose:
            print("\n  - So sánh trên dữ liệu Albrecht:")
        
        # Dữ liệu thực tế và dự đoán từ file
        actual_effort = albrecht_df['y_test']
        ml_prediction = albrecht_df['y_pred']
        
        # Dự đoán bằng COCOMO II truyền thống
        cocomo_predictions = []
        
        for _, row in albrecht_df.iterrows():
            # Chuyển đổi FP sang KLOC
            kloc = row['AdjFP'] * 0.1  # Giả định 100 LOC/FP
            
            try:
                # Dự đoán bằng COCOMO II (đúng tham số)
                cocomo_result = cocomo_ii_basic_estimate(kloc, 'kloc')
                cocomo_predictions.append(cocomo_result['effort_pm'])
            except Exception as e:
                print(f"  - Lỗi khi dự đoán với COCOMO II cho Albrecht: {str(e)}")
                return pd.DataFrame()
        
        # Tính toán chỉ số đánh giá
        ml_rmse = np.sqrt(mean_squared_error(actual_effort, ml_prediction))
        ml_mae = mean_absolute_error(actual_effort, ml_prediction)
        ml_r2 = r2_score(actual_effort, ml_prediction)
        ml_mape = np.mean(np.abs((actual_effort - ml_prediction) / (actual_effort + 1e-10))) * 100
        
        cocomo_rmse = np.sqrt(mean_squared_error(actual_effort, cocomo_predictions))
        cocomo_mae = mean_absolute_error(actual_effort, cocomo_predictions)
        cocomo_r2 = r2_score(actual_effort, cocomo_predictions)
        cocomo_mape = np.mean(np.abs((actual_effort - cocomo_predictions) / (actual_effort + 1e-10))) * 100
        
        # Lưu kết quả
        results.append({
            'dataset': 'Albrecht',
            'model': 'ML',
            'rmse': ml_rmse,
            'mae': ml_mae,
            'r2': ml_r2,
            'mape': ml_mape
        })
        
        results.append({
            'dataset': 'Albrecht',
            'model': 'COCOMO II',
            'rmse': cocomo_rmse,
            'mae': cocomo_mae,
            'r2': cocomo_r2,
            'mape': cocomo_mape
        })
        
        if verbose:
            print(f"    + ML RMSE: {ml_rmse:.2f}, MAE: {ml_mae:.2f}, R²: {ml_r2:.4f}, MAPE: {ml_mape:.2f}%")
            print(f"    + COCOMO II RMSE: {cocomo_rmse:.2f}, MAE: {cocomo_mae:.2f}, R²: {cocomo_r2:.4f}, MAPE: {cocomo_mape:.2f}%")
        
        # Vẽ biểu đồ so sánh
        plt.figure(figsize=(14, 6))
        
        plt.subplot(1, 2, 1)
        plt.scatter(actual_effort, ml_prediction, alpha=0.5, label='ML')
        plt.scatter(actual_effort, cocomo_predictions, alpha=0.5, label='COCOMO II')
        plt.plot([0, actual_effort.max()], [0, actual_effort.max()], 'r--')
        plt.xlabel('Giá trị thực tế')
        plt.ylabel('Giá trị dự đoán')
        plt.title('Albrecht: Giá trị thực tế vs Dự đoán')
        plt.legend()
        
        plt.subplot(1, 2, 2)
        plt.bar(['ML', 'COCOMO II'], [ml_rmse, cocomo_rmse], alpha=0.7)
        plt.title('Albrecht: So sánh RMSE')
        plt.ylabel('RMSE')
        
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, 'albrecht_comparison.png'))
    
    # So sánh trên dữ liệu Desharnais
    if desharnais_df is not None:
        if verbose:
            print("\n  - So sánh trên dữ liệu Desharnais:")
        
        # Dữ liệu thực tế và dự đoán từ file
        actual_effort = desharnais_df['y_test']
        ml_prediction = desharnais_df['y_pred']
        
        # Dự đoán bằng COCOMO II truyền thống
        cocomo_predictions = []
        
        for _, row in desharnais_df.iterrows():
            # Chuyển đổi FP sang KLOC
            kloc = row['PointsAjust'] * 0.1  # Giả định 100 LOC/FP
            
            try:
                # Dự đoán bằng COCOMO II (đúng tham số)
                cocomo_result = cocomo_ii_basic_estimate(kloc, 'kloc')
                cocomo_predictions.append(cocomo_result['effort_pm'])
            except Exception as e:
                print(f"  - Lỗi khi dự đoán với COCOMO II cho Desharnais: {str(e)}")
                return pd.DataFrame()
        
        # Tính toán chỉ số đánh giá
        ml_rmse = np.sqrt(mean_squared_error(actual_effort, ml_prediction))
        ml_mae = mean_absolute_error(actual_effort, ml_prediction)
        ml_r2 = r2_score(actual_effort, ml_prediction)
        ml_mape = np.mean(np.abs((actual_effort - ml_prediction) / (actual_effort + 1e-10))) * 100
        
        cocomo_rmse = np.sqrt(mean_squared_error(actual_effort, cocomo_predictions))
        cocomo_mae = mean_absolute_error(actual_effort, cocomo_predictions)
        cocomo_r2 = r2_score(actual_effort, cocomo_predictions)
        cocomo_mape = np.mean(np.abs((actual_effort - cocomo_predictions) / (actual_effort + 1e-10))) * 100
        
        # Lưu kết quả
        results.append({
            'dataset': 'Desharnais',
            'model': 'ML',
            'rmse': ml_rmse,
            'mae': ml_mae,
            'r2': ml_r2,
            'mape': ml_mape
        })
        
        results.append({
            'dataset': 'Desharnais',
            'model': 'COCOMO II',
            'rmse': cocomo_rmse,
            'mae': cocomo_mae,
            'r2': cocomo_r2,
            'mape': cocomo_mape
        })
        
        if verbose:
            print(f"    + ML RMSE: {ml_rmse:.2f}, MAE: {ml_mae:.2f}, R²: {ml_r2:.4f}, MAPE: {ml_mape:.2f}%")
            print(f"    + COCOMO II RMSE: {cocomo_rmse:.2f}, MAE: {cocomo_mae:.2f}, R²: {cocomo_r2:.4f}, MAPE: {cocomo_mape:.2f}%")
        
        # Vẽ biểu đồ so sánh
        plt.figure(figsize=(14, 6))
        
        plt.subplot(1, 2, 1)
        plt.scatter(actual_effort, ml_prediction, alpha=0.5, label='ML')
        plt.scatter(actual_effort, cocomo_predictions, alpha=0.5, label='COCOMO II')
        plt.plot([0, actual_effort.max()], [0, actual_effort.max()], 'r--')
        plt.xlabel('Giá trị thực tế')
        plt.ylabel('Giá trị dự đoán')
        plt.title('Desharnais: Giá trị thực tế vs Dự đoán')
        plt.legend()
        
        plt.subplot(1, 2, 2)
        plt.bar(['ML', 'COCOMO II'], [ml_rmse, cocomo_rmse], alpha=0.7)
        plt.title('Desharnais: So sánh RMSE')
        plt.ylabel('RMSE')
        
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, 'desharnais_comparison.png'))
    
    # Tạo DataFrame kết quả
    results_df = pd.DataFrame(results)
    
    # Lưu kết quả ra file
    results_df.to_csv(os.path.join(RESULTS_DIR, 'real_world_comparison.csv'), index=False)
    
    # Vẽ biểu đồ tổng hợp
    if len(results_df) > 0:
        plt.figure(figsize=(14, 10))
        
        # So sánh RMSE
        plt.subplot(2, 2, 1)
        sns.barplot(x='dataset', y='rmse', hue='model', data=results_df)
        plt.title('So sánh RMSE')
        
        # So sánh MAE
        plt.subplot(2, 2, 2)
        sns.barplot(x='dataset', y='mae', hue='model', data=results_df)
        plt.title('So sánh MAE')
        
        # So sánh R²
        plt.subplot(2, 2, 3)
        sns.barplot(x='dataset', y='r2', hue='model', data=results_df)
        plt.title('So sánh R²')
        
        # So sánh MAPE
        plt.subplot(2, 2, 4)
        sns.barplot(x='dataset', y='mape', hue='model', data=results_df)
        plt.title('So sánh MAPE (%)')
        
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, 'real_world_comparison_all.png'))
    
    return results_df

def main():
    """
    Hàm chính để thực hiện so sánh
    """
    print("\n" + "="*50)
    print("So sánh Mô hình COCOMO II Truyền thống vs. Mô hình ML Cải tiến")
    print("="*50)
    
    # 1. Tạo dữ liệu test từ các kích thước khác nhau
    print("\n1. Tạo dữ liệu test...")
    test_data = generate_test_data()
    print(f"  - Đã tạo {len(test_data)} mẫu test")
    
    # 2. Dự đoán bằng mô hình COCOMO II truyền thống
    print("\n2. Dự đoán với mô hình COCOMO II truyền thống...")
    results = predict_traditional_cocomo(test_data)
    print(f"  - Đã dự đoán xong với mô hình truyền thống")
    
    # 3. Dự đoán bằng các mô hình ML
    print("\n3. Dự đoán với các mô hình ML cải tiến...")
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
    results.to_csv(os.path.join(RESULTS_DIR, 'comparison_results.csv'), index=False)
    metrics.to_csv(os.path.join(RESULTS_DIR, 'comparison_metrics.csv'), index=False)
    
    print(f"\n  - Đã lưu kết quả chi tiết vào file {os.path.join(RESULTS_DIR, 'comparison_results.csv')}")
    print(f"  - Đã lưu chỉ số đánh giá vào file {os.path.join(RESULTS_DIR, 'comparison_metrics.csv')}")
    
    # 6. Trực quan hóa kết quả
    print("\n6. Trực quan hóa kết quả...")
    visualize_comparison(results, metrics)
    print(f"  - Đã tạo và hiển thị các biểu đồ so sánh")
    print(f"  - Các biểu đồ đã được lưu trong thư mục {RESULTS_DIR}")
    
    # 7. So sánh với dữ liệu thực tế
    print("\n7. So sánh với dữ liệu thực tế...")
    real_data = generate_real_world_data()
    
    if len(real_data) > 0:
        print(f"  - Đã tạo {len(real_data)} mẫu test từ dữ liệu thực tế")
        
        # Dự đoán
        real_results = predict_traditional_cocomo(real_data)
        real_results = predict_ml_models(real_results)
        
        # Tính toán các chỉ số đánh giá
        real_metrics = calculate_real_metrics(real_results)
        
        # Hiển thị kết quả
        print("\nBảng chỉ số đánh giá so với dữ liệu thực tế:")
        print(tabulate(real_metrics, headers='keys', tablefmt='pretty', showindex=False))
        
        # Lưu kết quả
        real_results.to_csv(os.path.join(RESULTS_DIR, 'real_comparison_results.csv'), index=False)
        real_metrics.to_csv(os.path.join(RESULTS_DIR, 'real_comparison_metrics.csv'), index=False)
        
        # Trực quan hóa kết quả
        visualize_real_comparison(real_results, real_metrics)
        print(f"  - Đã tạo và hiển thị các biểu đồ so sánh với dữ liệu thực tế")
        print(f"  - Các biểu đồ đã được lưu trong thư mục {RESULTS_DIR}")
    else:
        print("  - Không tìm thấy dữ liệu thực tế phù hợp.")
    
    # 8. So sánh mô hình trên dữ liệu thực tế (Albrecht và Desharnais)
    print("\n8. So sánh mô hình trên dữ liệu thực tế (Albrecht và Desharnais)...")
    compare_results = compare_real_world_data()
    print(f"  - Đã hoàn thành so sánh trên dữ liệu thực tế")
    
    print("\n" + "="*50)
    print("Hoàn thành so sánh mô hình!")
    print("="*50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTrạng thái đã hủy bởi người dùng.")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {str(e)}")
