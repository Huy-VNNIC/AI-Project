#!/usr/bin/env python3
"""
Script để huấn luyện các mô hình Machine Learning cho ước lượng nỗ lực phần mềm.
Sử dụng các bộ dữ liệu có sẵn để huấn luyện mô hình và lưu chúng dưới dạng tương thích với Python 3.12.
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import matplotlib.pyplot as plt
import io
import scipy.io
import arff
import warnings

# Thêm thư mục gốc vào sys.path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Cấu hình đường dẫn
DATASETS_DIR = os.path.join(PROJECT_ROOT, "datasets", "effortEstimation")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models", "cocomo_ii_extended")
os.makedirs(MODELS_DIR, exist_ok=True)

# Thiết lập cài đặt
pd.set_option('display.max_columns', None)
warnings.filterwarnings('ignore')

def load_dataset(dataset_name):
    """
    Tải dữ liệu từ file .arff
    
    Args:
        dataset_name (str): Tên bộ dữ liệu
        
    Returns:
        pd.DataFrame: Dữ liệu đã tải
    """
    try:
        file_path = os.path.join(DATASETS_DIR, f"{dataset_name}.arff")
        with open(file_path, 'r') as f:
            dataset = arff.load(f)
        
        # Chuyển đổi thành DataFrame
        df = pd.DataFrame(dataset['data'], columns=[attr[0] for attr in dataset['attributes']])
        
        print(f"Loaded {dataset_name} dataset with {df.shape[0]} rows and {df.shape[1]} columns")
        return df
    except Exception as e:
        print(f"Error loading {dataset_name}: {e}")
        return None

def combine_datasets():
    """
    Kết hợp các bộ dữ liệu
    
    Returns:
        pd.DataFrame: Dữ liệu kết hợp
    """
    # Danh sách các bộ dữ liệu phổ biến
    datasets = ["desharnais", "china", "coc81_1_1", "maxwell", "miyazaki94"]
    dfs = []
    
    for dataset in datasets:
        df = load_dataset(dataset)
        if df is not None:
            # Thêm cột nguồn dữ liệu
            df['source'] = dataset
            dfs.append(df)
    
    if not dfs:
        print("No datasets loaded successfully!")
        return None
    
    # Tìm các cột chung giữa các bộ dữ liệu
    common_columns = set.intersection(*[set(df.columns) for df in dfs])
    
    # Đảm bảo có cột nỗ lực (effort)
    effort_columns = ["effort", "Effort", "ActualEffort", "actual_effort"]
    target_column = None
    for col in effort_columns:
        if any(col in df.columns for df in dfs):
            target_column = col
            break
    
    if target_column is None:
        print("No effort column found in datasets!")
        return None
    
    # Chuẩn hóa tên cột
    standardized_dfs = []
    for df in dfs:
        # Tìm cột effort trong DataFrame hiện tại
        effort_col = None
        for col in effort_columns:
            if col in df.columns:
                effort_col = col
                break
        
        if effort_col is not None:
            df_copy = df.copy()
            df_copy['effort'] = df[effort_col]  # Chuẩn hóa tên cột effort
            standardized_dfs.append(df_copy[['effort', 'source']])
        else:
            print(f"Warning: No effort column in dataset from {df['source'].iloc[0]}")
    
    # Kết hợp dữ liệu
    combined_df = pd.concat(standardized_dfs, ignore_index=True)
    
    print(f"Combined dataset has {combined_df.shape[0]} rows and {combined_df.shape[1]} columns")
    return combined_df

def preprocess_combined_data(df):
    """
    Tiền xử lý dữ liệu kết hợp
    
    Args:
        df (pd.DataFrame): Dữ liệu cần xử lý
        
    Returns:
        tuple: X, y, preprocessor
    """
    if df is None:
        return None, None, None
    
    # Tạo các tính năng cho mô hình ML
    df['size'] = np.random.uniform(1, 100, df.shape[0])  # Giả lập kích thước dự án
    df['complexity'] = np.random.uniform(1, 5, df.shape[0])  # Giả lập độ phức tạp
    df['team_experience'] = np.random.uniform(1, 5, df.shape[0])  # Giả lập kinh nghiệm đội ngũ
    df['requirements_quality'] = np.random.uniform(1, 5, df.shape[0])  # Giả lập chất lượng yêu cầu
    
    # Tính toán tính năng bổ sung dựa trên effort và size
    df['productivity'] = df['effort'] / df['size']
    df['effort_per_complexity'] = df['effort'] / df['complexity']
    
    # Tính năng của mô hình COCOMO II
    for feature in ['PREC', 'FLEX', 'RESL', 'TEAM', 'PMAT', 'RELY', 'DATA', 'CPLX', 'DOCU', 
                   'TIME', 'STOR', 'PVOL', 'ACAP', 'PCAP', 'PCON', 'APEX', 'PLEX', 'LTEX', 
                   'TOOL', 'SITE', 'SCED']:
        df[feature] = np.random.uniform(0.7, 1.3, df.shape[0])  # Giả lập các hệ số COCOMO
    
    # Định nghĩa tính năng đầu vào và mục tiêu
    X = df.drop(['effort', 'productivity', 'effort_per_complexity', 'source'], axis=1, errors='ignore')
    y = df['effort']
    
    # Chia thành tập huấn luyện và kiểm thử
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Xác định các cột số và danh mục
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_features = X.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # Tạo bộ tiền xử lý
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features) if categorical_features else ('cat', 'passthrough', [])
        ])
    
    # Lưu thông tin tính năng
    feature_info = {
        "numeric_features": numeric_features,
        "categorical_features": categorical_features
    }
    
    with open(os.path.join(MODELS_DIR, 'feature_info.json'), 'w') as f:
        json.dump(feature_info, f, indent=2)
    
    # Tiền xử lý dữ liệu
    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)
    
    # Lưu bộ tiền xử lý
    joblib.dump(preprocessor, os.path.join(MODELS_DIR, 'preprocessor.joblib'))
    
    return (X_train, X_test, y_train, y_test, X_train_processed, X_test_processed, 
            preprocessor, feature_info)

def train_and_evaluate_models(X_train, X_test, y_train, y_test, 
                             X_train_processed, X_test_processed, preprocessor):
    """
    Huấn luyện và đánh giá các mô hình
    
    Args:
        X_train, X_test, y_train, y_test: Dữ liệu huấn luyện và kiểm thử
        X_train_processed, X_test_processed: Dữ liệu đã qua tiền xử lý
        preprocessor: Bộ tiền xử lý
        
    Returns:
        dict: Kết quả đánh giá và các mô hình đã huấn luyện
    """
    models = {
        'Random_Forest': RandomForestRegressor(n_estimators=100, random_state=42),
        'Gradient_Boosting': GradientBoostingRegressor(random_state=42),
        'Decision_Tree': DecisionTreeRegressor(random_state=42),
        'Linear_Regression': LinearRegression()
    }
    
    results = {}
    trained_models = {}
    
    for name, model in models.items():
        # Huấn luyện mô hình
        print(f"\nTraining {name}...")
        model.fit(X_train_processed, y_train)
        
        # Dự đoán
        y_pred = model.predict(X_test_processed)
        
        # Đánh giá
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"{name} - RMSE: {rmse:.2f}, MAE: {mae:.2f}, R²: {r2:.4f}")
        
        # Lưu kết quả
        results[name] = {
            'RMSE': rmse,
            'MAE': mae,
            'R2': r2
        }
        
        # Lưu mô hình
        trained_models[name] = model
        joblib.dump(model, os.path.join(MODELS_DIR, f"{name}.joblib"))
        
        # Tạo biểu đồ dự đoán vs thực tế
        plt.figure(figsize=(10, 6))
        plt.scatter(y_test, y_pred, alpha=0.5)
        plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
        plt.xlabel('Effort thực tế')
        plt.ylabel('Effort dự đoán')
        plt.title(f'{name} - Dự đoán vs Thực tế')
        plt.tight_layout()
        plt.savefig(os.path.join(MODELS_DIR, f"{name}_predictions.png"))
        plt.close()
        
        # Nếu mô hình có feature_importances_
        if hasattr(model, 'feature_importances_'):
            # Lấy tên các tính năng
            feature_names = X_train.columns.tolist()
            
            # Tạo DataFrame cho feature importances
            importances = pd.DataFrame({
                'feature': feature_names,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            # Lưu DataFrame
            importances.to_csv(os.path.join(MODELS_DIR, f"{name}_feature_importance.csv"), index=False)
            
            # Tạo biểu đồ feature importances
            plt.figure(figsize=(12, 8))
            importances.set_index('feature').sort_values('importance').plot(kind='barh')
            plt.title(f'{name} - Feature Importances')
            plt.tight_layout()
            plt.savefig(os.path.join(MODELS_DIR, f"{name}_feature_importance.png"))
            plt.close()
        
        # Biểu đồ phân phối lỗi
        plt.figure(figsize=(10, 6))
        plt.hist(y_test - y_pred, bins=30, edgecolor='black')
        plt.xlabel('Error (Actual - Predicted)')
        plt.ylabel('Frequency')
        plt.title(f'{name} - Error Distribution')
        plt.tight_layout()
        plt.savefig(os.path.join(MODELS_DIR, f"{name}_error_dist.png"))
        plt.close()
    
    # Tạo cấu hình chung
    config = {
        "models": list(models.keys()),
        "features": list(X_train.columns),
        "default_method": "weighted_average"
    }
    
    with open(os.path.join(MODELS_DIR, 'config.json'), 'w') as f:
        json.dump(config, f, indent=2)
    
    # Lưu kết quả đánh giá
    results_df = pd.DataFrame.from_dict({model: metrics for model, metrics in results.items()}, 
                                       orient='index')
    results_df.to_csv(os.path.join(MODELS_DIR, 'model_comparison.csv'))
    
    # Biểu đồ so sánh các mô hình
    plt.figure(figsize=(12, 8))
    results_df[['RMSE', 'MAE']].plot(kind='bar')
    plt.title('So sánh các mô hình ML')
    plt.ylabel('Metric Value')
    plt.tight_layout()
    plt.savefig(os.path.join(MODELS_DIR, 'model_comparison.png'))
    plt.close()
    
    return trained_models, results

def create_feature_importance_summary(trained_models, feature_info):
    """
    Tạo tổng hợp tầm quan trọng của các tính năng
    
    Args:
        trained_models (dict): Các mô hình đã huấn luyện
        feature_info (dict): Thông tin về các tính năng
    """
    feature_importance = {}
    for name, model in trained_models.items():
        if hasattr(model, 'feature_importances_'):
            feature_names = feature_info['numeric_features'] + feature_info['categorical_features']
            for i, feature in enumerate(feature_names):
                if i < len(model.feature_importances_):
                    if feature not in feature_importance:
                        feature_importance[feature] = []
                    feature_importance[feature].append(model.feature_importances_[i])
    
    # Tính giá trị trung bình cho mỗi tính năng
    avg_importance = {}
    for feature, values in feature_importance.items():
        avg_importance[feature] = sum(values) / len(values) if values else 0
    
    # Lưu kết quả
    with open(os.path.join(MODELS_DIR, 'feature_importance.json'), 'w') as f:
        json.dump(avg_importance, f, indent=2)
    
    # Hiển thị top 10 tính năng quan trọng nhất
    top_features = sorted(avg_importance.items(), key=lambda x: x[1], reverse=True)[:10]
    print("\nTop 10 tính năng quan trọng nhất:")
    for feature, importance in top_features:
        print(f"{feature}: {importance:.4f}")

def create_synthetic_data():
    """
    Tạo dữ liệu tổng hợp dựa trên các tham số COCOMO II
    
    Returns:
        pd.DataFrame: Dữ liệu tổng hợp
    """
    # Số lượng dự án
    n_projects = 1000
    
    # Tạo kích thước dự án (KLOC)
    sizes = np.exp(np.random.uniform(np.log(1), np.log(1000), n_projects))
    
    # Tạo các hệ số nhân COCOMO II
    scale_factors = {
        'PREC': np.random.uniform(0.7, 1.3, n_projects),  # Tính tiền lệ
        'FLEX': np.random.uniform(0.7, 1.3, n_projects),  # Tính linh hoạt
        'RESL': np.random.uniform(0.7, 1.3, n_projects),  # Giải quyết kiến trúc/rủi ro
        'TEAM': np.random.uniform(0.7, 1.3, n_projects),  # Đoàn kết nhóm
        'PMAT': np.random.uniform(0.7, 1.3, n_projects),  # Mức độ trưởng thành quy trình
    }
    
    # Tạo các hệ số nhân nỗ lực
    effort_multipliers = {
        'RELY': np.random.uniform(0.7, 1.3, n_projects),  # Độ tin cậy
        'DATA': np.random.uniform(0.7, 1.3, n_projects),  # Kích thước cơ sở dữ liệu
        'CPLX': np.random.uniform(0.7, 1.3, n_projects),  # Độ phức tạp
        'RUSE': np.random.uniform(0.7, 1.3, n_projects),  # Tính tái sử dụng
        'DOCU': np.random.uniform(0.7, 1.3, n_projects),  # Tài liệu
        'TIME': np.random.uniform(0.7, 1.3, n_projects),  # Ràng buộc thời gian
        'STOR': np.random.uniform(0.7, 1.3, n_projects),  # Ràng buộc lưu trữ
        'PVOL': np.random.uniform(0.7, 1.3, n_projects),  # Biến động nền tảng
        'ACAP': np.random.uniform(0.7, 1.3, n_projects),  # Khả năng phân tích
        'PCAP': np.random.uniform(0.7, 1.3, n_projects),  # Khả năng lập trình
        'PCON': np.random.uniform(0.7, 1.3, n_projects),  # Tính liên tục nhân sự
        'APEX': np.random.uniform(0.7, 1.3, n_projects),  # Kinh nghiệm ứng dụng
        'PLEX': np.random.uniform(0.7, 1.3, n_projects),  # Kinh nghiệm nền tảng
        'LTEX': np.random.uniform(0.7, 1.3, n_projects),  # Kinh nghiệm ngôn ngữ/công cụ
        'TOOL': np.random.uniform(0.7, 1.3, n_projects),  # Sử dụng công cụ
        'SITE': np.random.uniform(0.7, 1.3, n_projects),  # Phát triển nhiều địa điểm
        'SCED': np.random.uniform(0.7, 1.3, n_projects),  # Ràng buộc lịch trình
    }
    
    # Tính toán các tham số khác
    complexity = effort_multipliers['CPLX'] * 3  # Độ phức tạp
    team_experience = (effort_multipliers['ACAP'] + effort_multipliers['PCAP'] + scale_factors['TEAM']) / 3 * 3
    requirements_quality = scale_factors['PREC'] * 3
    
    # Tính EAF (Effort Adjustment Factor)
    eaf = np.prod(np.array([effort_multipliers[em] for em in effort_multipliers]), axis=0)
    
    # Tính toán hệ số mũ
    B = 0.91 + 0.01 * np.sum([scale_factors[sf] for sf in scale_factors], axis=0)
    
    # Hằng số COCOMO II
    A = 2.94
    
    # Tính nỗ lực theo COCOMO II: PM = A * Size^B * EAF
    effort = A * (sizes ** B) * eaf
    
    # Thêm nhiễu ngẫu nhiên
    effort = effort * np.random.normal(1, 0.2, n_projects)
    
    # Tạo DataFrame
    data = {
        'size': sizes,
        'effort': effort,
        'complexity': complexity,
        'team_experience': team_experience,
        'requirements_quality': requirements_quality,
    }
    
    # Thêm các hệ số nhân
    data.update(scale_factors)
    data.update(effort_multipliers)
    
    # Tạo DataFrame
    df = pd.DataFrame(data)
    
    print(f"Created synthetic dataset with {df.shape[0]} rows and {df.shape[1]} columns")
    return df

def main():
    """
    Hàm chính để chạy quá trình huấn luyện
    """
    print("Bắt đầu quá trình huấn luyện mô hình ML...")
    
    # Tạo dữ liệu tổng hợp thay vì tải dữ liệu thực
    df = create_synthetic_data()
    
    # Tiền xử lý dữ liệu
    (X_train, X_test, y_train, y_test, X_train_processed, X_test_processed, 
     preprocessor, feature_info) = preprocess_combined_data(df)
    
    # Huấn luyện và đánh giá mô hình
    trained_models, results = train_and_evaluate_models(
        X_train, X_test, y_train, y_test, X_train_processed, X_test_processed, preprocessor)
    
    # Tạo tổng hợp tầm quan trọng của các tính năng
    create_feature_importance_summary(trained_models, feature_info)
    
    print("\nQuá trình huấn luyện mô hình ML hoàn tất!")
    print(f"Các mô hình đã được lưu tại: {MODELS_DIR}")
    
    # Vẽ biểu đồ phân phối biến mục tiêu
    plt.figure(figsize=(10, 6))
    plt.hist(df['effort'], bins=30, edgecolor='black')
    plt.xlabel('Effort (person-months)')
    plt.ylabel('Frequency')
    plt.title('Target Distribution')
    plt.tight_layout()
    plt.savefig(os.path.join(MODELS_DIR, 'target_distribution.png'))
    plt.close()

if __name__ == "__main__":
    main()