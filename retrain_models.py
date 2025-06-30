#!/usr/bin/env python3
"""
Script tự động huấn luyện lại mô hình COCOMO II mở rộng

Script này sẽ:
1. Đọc dữ liệu đã tiền xử lý
2. Huấn luyện lại các mô hình ML với dữ liệu mới
3. Đánh giá hiệu suất mô hình
4. Xuất mô hình đã huấn luyện lại
"""

import os
import sys
import numpy as np
import pandas as pd
import json
import joblib
from datetime import datetime
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder, PowerTransformer, RobustScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, mean_absolute_percentage_error
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn

# Đường dẫn thư mục dữ liệu và mô hình
DATA_DIR = './processed_data'
MODEL_DIR = './models/cocomo_ii_extended'

# Đảm bảo thư mục mô hình tồn tại
os.makedirs(MODEL_DIR, exist_ok=True)

def load_data(verbose=True):
    """
    Đọc dữ liệu đã tiền xử lý
    
    Returns:
        DataFrame chứa dữ liệu đã tiền xử lý
    """
    if verbose:
        print("Đọc dữ liệu đã tiền xử lý...")
    
    # Đường dẫn đến file dữ liệu kết hợp
    data_path = os.path.join(DATA_DIR, 'combined_data.csv')
    
    if not os.path.exists(data_path):
        if verbose:
            print(f"Không tìm thấy file dữ liệu: {data_path}")
            print("Vui lòng chạy script tiền xử lý dữ liệu trước.")
        sys.exit(1)
    
    # Đọc dữ liệu
    df = pd.read_csv(data_path)
    
    if verbose:
        print(f"Đã đọc {len(df)} mẫu dữ liệu từ {data_path}")
        print(f"Phân bố theo schema: {df['schema'].value_counts().to_dict()}")
    
    return df

def prepare_data(df, verbose=True):
    """
    Chuẩn bị dữ liệu cho huấn luyện mô hình
    
    Args:
        df: DataFrame chứa dữ liệu
        
    Returns:
        X: Đặc trưng
        y: Biến mục tiêu
        feature_names: Tên các đặc trưng
    """
    if verbose:
        print("Chuẩn bị dữ liệu cho huấn luyện mô hình...")
    
    # Xác định biến mục tiêu
    target = 'effort_pm'
    
    # Kiểm tra phân bố của biến mục tiêu
    if verbose:
        plt.figure(figsize=(12, 5))
        plt.subplot(1, 2, 1)
        sns.histplot(df[target], kde=True)
        plt.title('Phân bố biến effort_pm')
        plt.xlabel('Effort (person-months)')
        plt.ylabel('Số lượng')
        
        plt.subplot(1, 2, 2)
        sns.histplot(np.log1p(df[target]), kde=True)
        plt.title('Phân bố log(effort_pm + 1)')
        plt.xlabel('Log(Effort + 1)')
        plt.ylabel('Số lượng')
        
        plt.tight_layout()
        plt.savefig(os.path.join(MODEL_DIR, 'target_distribution.png'))
        plt.close()
    
    # Áp dụng log transform cho biến mục tiêu để cân bằng phân bố
    y = np.log1p(df[target])
    
    # Chọn đặc trưng
    numeric_features = ['size']
    categorical_features = ['schema']
    
    # Thêm đặc trưng nếu có
    if 'time_months' in df.columns:
        numeric_features.append('time_months')
    
    if 'developers' in df.columns and df['developers'].notna().sum() > 0:
        numeric_features.append('developers')
    
    # Thêm các đặc trưng đặc biệt cho FP
    fp_features = ['input', 'output', 'inquiry', 'file', 'fp_adj', 'raw_fp']
    for feature in fp_features:
        if feature in df.columns and df[feature].notna().sum() > len(df) * 0.1:  # Ít nhất 10% dữ liệu có giá trị
            numeric_features.append(feature)
    
    # Thêm các đặc trưng cho Desharnais
    desharnais_features = ['transactions', 'entities', 'points_non_adjust', 'adjustment', 'team_exp', 'manager_exp']
    for feature in desharnais_features:
        if feature in df.columns and df[feature].notna().sum() > len(df) * 0.1:  # Ít nhất 10% dữ liệu có giá trị
            numeric_features.append(feature)
    
    # Tạo đặc trưng mới: tỉ lệ FP/người (productivity)
    if 'fp' in df.columns and 'developers' in df.columns:
        df['fp_per_dev'] = df['fp'] / df['developers'].replace(0, 1)
        numeric_features.append('fp_per_dev')
    
    # Tạo đặc trưng mới: tỉ lệ KLOC/người
    if 'kloc' in df.columns and 'developers' in df.columns:
        df['kloc_per_dev'] = df['kloc'] / df['developers'].replace(0, 1)
        numeric_features.append('kloc_per_dev')
    
    # Tạo đặc trưng mới: FP/thời gian
    if 'fp' in df.columns and 'time_months' in df.columns:
        df['fp_per_month'] = df['fp'] / df['time_months'].replace(0, 1)
        numeric_features.append('fp_per_month')
    
    # Tạo đặc trưng mới: KLOC/thời gian
    if 'kloc' in df.columns and 'time_months' in df.columns:
        df['kloc_per_month'] = df['kloc'] / df['time_months'].replace(0, 1)
        numeric_features.append('kloc_per_month')
    
    # Lọc các đặc trưng không có quá nhiều giá trị null
    valid_numeric_features = []
    for feature in numeric_features:
        if feature in df.columns and df[feature].notna().sum() > len(df) * 0.5:  # Ít nhất 50% dữ liệu có giá trị
            valid_numeric_features.append(feature)
    
    # Loại bỏ các đặc trưng bị trùng lặp
    valid_numeric_features = list(set(valid_numeric_features))
    
    if verbose:
        print(f"Đặc trưng số: {valid_numeric_features}")
        print(f"Đặc trưng phân loại: {categorical_features}")
    
    # Tạo preprocessor
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', RobustScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, valid_numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ],
        remainder='drop'
    )
    
    # Tiền xử lý dữ liệu
    X = preprocessor.fit_transform(df)
    
    # Lưu bộ tiền xử lý
    joblib.dump(preprocessor, os.path.join(MODEL_DIR, 'preprocessor.pkl'))
    
    # Lưu tên đặc trưng
    feature_names = valid_numeric_features + categorical_features
    
    # Lưu thông tin đặc trưng
    with open(os.path.join(MODEL_DIR, 'feature_info.json'), 'w') as f:
        json.dump({
            'numeric_features': valid_numeric_features,
            'categorical_features': categorical_features,
            'target': target,
            'log_transform': True
        }, f, indent=4)
    
    return X, y, feature_names

def create_preprocessor(categorical_cols, numeric_cols, verbose=True):
    """
    Tạo bộ tiền xử lý dữ liệu
    
    Args:
        categorical_cols: Danh sách các cột phân loại
        numeric_cols: Danh sách các cột số
        
    Returns:
        Bộ tiền xử lý dữ liệu
    """
    if verbose:
        print("Tạo bộ tiền xử lý dữ liệu...")
    
    # Tiền xử lý cho đặc trưng phân loại
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='unknown')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    # Tiền xử lý nâng cao cho đặc trưng số
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('power', PowerTransformer(method='yeo-johnson', standardize=False)),
        ('scaler', RobustScaler())
    ])
    
    # Kết hợp các transformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_cols),
            ('cat', categorical_transformer, categorical_cols)
        ],
        remainder='drop'
    )
    
    return preprocessor

def train_models(X, y, feature_names, verbose=True):
    """
    Huấn luyện các mô hình ML
    
    Args:
        X: Đặc trưng
        y: Biến mục tiêu
        feature_names: Tên các đặc trưng
        
    Returns:
        dict: Từ điển chứa các mô hình đã huấn luyện
    """
    if verbose:
        print("Huấn luyện các mô hình ML...")
    
    # Chia dữ liệu thành tập huấn luyện và tập kiểm tra
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Định nghĩa các mô hình
    models = {
        'Linear_Regression': LinearRegression(),
        'Decision_Tree': DecisionTreeRegressor(random_state=42),
        'Random_Forest': RandomForestRegressor(random_state=42),
        'Gradient_Boosting': GradientBoostingRegressor(random_state=42)
    }
    
    # Cấu hình tham số cho grid search
    param_grids = {
        'Linear_Regression': {},
        'Decision_Tree': {
            'max_depth': [None, 5, 10, 15, 20],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        },
        'Random_Forest': {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 10, 20],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        },
        'Gradient_Boosting': {
            'n_estimators': [50, 100, 200],
            'learning_rate': [0.01, 0.05, 0.1],
            'max_depth': [3, 5, 7],
            'subsample': [0.8, 1.0]
        }
    }
    
    # Huấn luyện và đánh giá từng mô hình
    trained_models = {}
    model_metrics = []
    
    for name, model in models.items():
        try:
            # Grid search nếu có tham số
            if param_grids[name]:
                if verbose:
                    print(f"  - Tinh chỉnh siêu tham số cho {name}...")
                
                # Cross-validation với 5 fold
                grid_search = GridSearchCV(
                    model, param_grids[name], 
                    cv=5, scoring='neg_mean_squared_error',
                    n_jobs=-1
                )
                grid_search.fit(X_train, y_train)
                
                # Lấy mô hình tốt nhất
                best_model = grid_search.best_estimator_
                best_params = grid_search.best_params_
                
                if verbose:
                    print(f"    + Tham số tốt nhất: {best_params}")
            else:
                # Huấn luyện mô hình trực tiếp nếu không cần grid search
                best_model = model
                best_model.fit(X_train, y_train)
                best_params = {}
            
            # Đánh giá trên tập kiểm tra
            y_pred = best_model.predict(X_test)
            
            # Đảo ngược log transform
            y_test_orig = np.expm1(y_test)
            y_pred_orig = np.expm1(y_pred)
            
            # Tính các chỉ số đánh giá
            mse = mean_squared_error(y_test_orig, y_pred_orig)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_test_orig, y_pred_orig)
            r2 = r2_score(y_test_orig, y_pred_orig)
            
            try:
                mape = mean_absolute_percentage_error(y_test_orig, y_pred_orig) * 100
            except:
                mape = np.mean(np.abs((y_test_orig - y_pred_orig) / (y_test_orig + 1e-10))) * 100
            
            # Lưu kết quả
            model_metrics.append({
                'model': name,
                'best_params': best_params,
                'mse': mse,
                'rmse': rmse,
                'mae': mae,
                'r2': r2,
                'mape': mape
            })
            
            # Lưu mô hình
            trained_models[name] = best_model
            
            if verbose:
                print(f"  - {name}:")
                print(f"    + RMSE: {rmse:.2f}")
                print(f"    + MAE: {mae:.2f}")
                print(f"    + R²: {r2:.4f}")
                print(f"    + MAPE: {mape:.2f}%")
                
                # Vẽ biểu đồ so sánh giá trị thực tế và dự đoán
                plt.figure(figsize=(10, 6))
                plt.scatter(y_test_orig, y_pred_orig, alpha=0.5)
                plt.plot([0, y_test_orig.max()], [0, y_test_orig.max()], 'r--')
                plt.xlabel('Giá trị thực tế')
                plt.ylabel('Giá trị dự đoán')
                plt.title(f'{name}: Giá trị thực tế vs Dự đoán')
                plt.savefig(os.path.join(MODEL_DIR, f'{name}_predictions.png'))
                
                # Vẽ biểu đồ phân bố lỗi
                plt.figure(figsize=(10, 6))
                error = y_test_orig - y_pred_orig
                sns.histplot(error, kde=True)
                plt.xlabel('Lỗi')
                plt.ylabel('Tần suất')
                plt.title(f'{name}: Phân bố lỗi')
                plt.axvline(x=0, color='r', linestyle='--')
                plt.savefig(os.path.join(MODEL_DIR, f'{name}_error_dist.png'))
                
        except Exception as e:
            if verbose:
                print(f"  - Lỗi khi huấn luyện {name}: {str(e)}")
    
    # Lưu thông tin so sánh các mô hình
    metrics_df = pd.DataFrame(model_metrics)
    metrics_df.to_csv(os.path.join(MODEL_DIR, 'model_comparison.csv'), index=False)
    
    # Vẽ biểu đồ so sánh các mô hình
    if len(metrics_df) > 0 and verbose:
        plt.figure(figsize=(12, 8))
        
        # So sánh RMSE
        plt.subplot(2, 2, 1)
        sns.barplot(x='model', y='rmse', data=metrics_df)
        plt.title('RMSE')
        plt.xticks(rotation=45)
        
        # So sánh MAE
        plt.subplot(2, 2, 2)
        sns.barplot(x='model', y='mae', data=metrics_df)
        plt.title('MAE')
        plt.xticks(rotation=45)
        
        # So sánh R²
        plt.subplot(2, 2, 3)
        sns.barplot(x='model', y='r2', data=metrics_df)
        plt.title('R²')
        plt.xticks(rotation=45)
        
        # So sánh MAPE
        plt.subplot(2, 2, 4)
        sns.barplot(x='model', y='mape', data=metrics_df)
        plt.title('MAPE (%)')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig(os.path.join(MODEL_DIR, 'model_comparison.png'))
    
    return trained_models

def fine_tune_models(X, y, preprocessor, verbose=True):
    """
    Tinh chỉnh siêu tham số cho các mô hình
    
    Args:
        X: Đặc trưng
        y: Biến mục tiêu
        preprocessor: Bộ tiền xử lý dữ liệu
        
    Returns:
        Dictionary chứa các mô hình đã tinh chỉnh
    """
    if verbose:
        print("\nTinh chỉnh siêu tham số cho các mô hình...")
    
    # Chia dữ liệu thành tập huấn luyện và kiểm thử
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Tinh chỉnh cho Random Forest
    if verbose:
        print("Tinh chỉnh mô hình Random Forest...")
    
    # Tạo pipeline cho Random Forest
    rf_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', RandomForestRegressor(random_state=42))
    ])
    
    # Các siêu tham số cần tinh chỉnh
    param_grid = {
        'model__n_estimators': [50, 100, 200],
        'model__max_depth': [None, 10, 20, 30],
        'model__min_samples_split': [2, 5, 10],
        'model__min_samples_leaf': [1, 2, 4]
    }
    
    # Tìm kiếm lưới
    grid_search = GridSearchCV(
        rf_pipeline, param_grid, cv=5,
        scoring='neg_mean_absolute_percentage_error',
        n_jobs=-1, verbose=0
    )
    
    # Huấn luyện
    grid_search.fit(X_train, y_train)
    
    # Lấy mô hình tốt nhất
    best_rf = grid_search.best_estimator_
    
    # Đánh giá mô hình tốt nhất
    y_pred = best_rf.predict(X_test)
    
    # Chuyển đổi ngược lại để đánh giá
    y_test_orig = np.expm1(y_test)
    y_pred_orig = np.expm1(y_pred)
    
    # Tính MMRE và PRED(25)
    are = np.abs(y_pred_orig - y_test_orig) / y_test_orig
    mmre = np.mean(are)
    pred_25 = np.mean(are <= 0.25)
    
    if verbose:
        print(f"Siêu tham số tốt nhất cho Random Forest: {grid_search.best_params_}")
        print(f"MMRE: {mmre:.4f}")
        print(f"PRED(25): {pred_25:.4f} ({pred_25*100:.2f}%)")
    
    # Trả về mô hình đã tinh chỉnh
    return {
        'Random_Forest_Tuned': best_rf
    }

def export_models(models, feature_names, verbose=True):
    """
    Xuất các mô hình ra file
    
    Args:
        models: Từ điển chứa các mô hình đã huấn luyện
        feature_names: Tên các đặc trưng
        
    Returns:
        None
    """
    if verbose:
        print("Xuất các mô hình ra file...")
    
    # Xuất từng mô hình
    for name, model in models.items():
        model_path = os.path.join(MODEL_DIR, f'{name}.pkl')
        joblib.dump(model, model_path)
        if verbose:
            print(f"  - Đã xuất mô hình {name} ra {model_path}")
    
    # Phân tích đặc trưng quan trọng cho các mô hình cây
    tree_models = ['Decision_Tree', 'Random_Forest', 'Gradient_Boosting']
    feature_importance = {}
    
    for name in tree_models:
        if name in models:
            model = models[name]
            
            if hasattr(model, 'feature_importances_'):
                # Lấy danh sách tên đặc trưng sau khi đã mã hóa
                preprocessor = joblib.load(os.path.join(MODEL_DIR, 'preprocessor.pkl'))
                
                # Thử lấy tên đặc trưng từ ColumnTransformer
                feature_names_after_preprocessing = []
                
                try:
                    # Xử lý đặc trưng số
                    numeric_features = [f for f in feature_names if f not in ['schema']]
                    feature_names_after_preprocessing.extend(numeric_features)
                    
                    # Xử lý đặc trưng phân loại
                    if 'schema' in feature_names:
                        onehot_features = preprocessor.named_transformers_['cat'].named_steps['onehot'].get_feature_names_out(['schema'])
                        feature_names_after_preprocessing.extend(onehot_features)
                except:
                    # Nếu không thể lấy tên đặc trưng, sử dụng indices
                    feature_names_after_preprocessing = [f'feature_{i}' for i in range(len(model.feature_importances_))]
                
                # Đảm bảo độ dài của tên đặc trưng khớp với số lượng đặc trưng quan trọng
                if len(feature_names_after_preprocessing) != len(model.feature_importances_):
                    feature_names_after_preprocessing = [f'feature_{i}' for i in range(len(model.feature_importances_))]
                
                # Tạo DataFrame để lưu mức độ quan trọng của đặc trưng
                importance_df = pd.DataFrame({
                    'feature': feature_names_after_preprocessing,
                    'importance': model.feature_importances_
                })
                importance_df = importance_df.sort_values('importance', ascending=False)
                
                # Lưu vào file
                importance_df.to_csv(os.path.join(MODEL_DIR, f'{name}_feature_importance.csv'), index=False)
                
                # Lưu vào từ điển
                feature_importance[name] = importance_df.to_dict('records')
                
                if verbose:
                    print(f"\n  - Đặc trưng quan trọng nhất cho {name}:")
                    for i, row in importance_df.head(10).iterrows():
                        print(f"    + {row['feature']}: {row['importance']:.4f}")
                    
                    # Vẽ biểu đồ đặc trưng quan trọng
                    plt.figure(figsize=(10, 8))
                    sns.barplot(x='importance', y='feature', data=importance_df.head(15))
                    plt.title(f'Top 15 đặc trưng quan trọng nhất - {name}')
                    plt.tight_layout()
                    plt.savefig(os.path.join(MODEL_DIR, f'{name}_feature_importance.png'))
    
    # Xuất thông tin đặc trưng quan trọng
    if feature_importance:
        with open(os.path.join(MODEL_DIR, 'feature_importance.json'), 'w') as f:
            json.dump(feature_importance, f, indent=4)
    
    # Xuất thông tin cấu hình
    config = {
        'models': list(models.keys()),
        'feature_names': feature_names,
        'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'python_version': sys.version,
        'libraries': {
            'scikit-learn': sklearn.__version__,
            'numpy': np.__version__,
            'pandas': pd.__version__
        }
    }
    
    with open(os.path.join(MODEL_DIR, 'config.json'), 'w') as f:
        json.dump(config, f, indent=4)
    
    if verbose:
        print(f"  - Đã xuất thông tin cấu hình ra {os.path.join(MODEL_DIR, 'config.json')}")
        print("\nXuất mô hình hoàn tất!")

def create_model_comparison(models, verbose=True):
    """
    Tạo so sánh giữa các mô hình
    
    Args:
        models: Dictionary chứa các mô hình và kết quả đánh giá
    """
    if verbose:
        print("\nTạo so sánh giữa các mô hình...")
    
    # Tạo DataFrame để so sánh các mô hình
    comparison_data = []
    
    for name, model_info in models.items():
        if 'metrics' in model_info:
            metrics = model_info['metrics']['original_space']
            comparison_data.append({
                'Model': name,
                'MAE': metrics['mae'],
                'RMSE': metrics['rmse'],
                'R²': metrics['r2'],
                'MMRE': metrics['mmre'],
                'PRED(25)': metrics['pred_25']
            })
    
    if not comparison_data:
        if verbose:
            print("Không có dữ liệu để so sánh")
        return
    
    # Tạo DataFrame
    comparison_df = pd.DataFrame(comparison_data)
    
    # Lưu so sánh
    comparison_path = os.path.join(MODEL_DIR, 'model_comparison.csv')
    comparison_df.to_csv(comparison_path, index=False)
    
    if verbose:
        print(f"Đã lưu so sánh mô hình ra {comparison_path}")
        print("\nSo sánh các mô hình:")
        print(comparison_df.to_string(index=False))
    
    # Trực quan hóa so sánh
    if verbose:
        # So sánh MMRE
        plt.figure(figsize=(10, 6))
        plt.bar(comparison_df['Model'], comparison_df['MMRE'], color='skyblue')
        plt.title('So sánh MMRE giữa các mô hình')
        plt.xlabel('Mô hình')
        plt.ylabel('MMRE (thấp hơn = tốt hơn)')
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Thêm giá trị lên các cột
        for i, v in enumerate(comparison_df['MMRE']):
            plt.text(i, v + 0.01, f'{v:.4f}', ha='center')
        
        plt.tight_layout()
        plt.savefig(os.path.join(MODEL_DIR, 'mmre_comparison.png'))
        plt.close()
        
        # So sánh PRED(25)
        plt.figure(figsize=(10, 6))
        plt.bar(comparison_df['Model'], comparison_df['PRED(25)'], color='lightgreen')
        plt.title('So sánh PRED(25) giữa các mô hình')
        plt.xlabel('Mô hình')
        plt.ylabel('PRED(25) (cao hơn = tốt hơn)')
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Thêm giá trị lên các cột
        for i, v in enumerate(comparison_df['PRED(25)']):
            plt.text(i, v + 0.01, f'{v:.4f}', ha='center')
        
        plt.tight_layout()
        plt.savefig(os.path.join(MODEL_DIR, 'pred25_comparison.png'))
        plt.close()

def main():
    """
    Hàm chính
    """
    print("\n" + "="*50)
    print("Huấn luyện lại mô hình COCOMO II mở rộng")
    print("="*50)
    
    # Đọc dữ liệu
    df = load_data()
    
    # Chuẩn bị dữ liệu
    X, y, feature_names = prepare_data(df)
    
    # Huấn luyện mô hình
    models = train_models(X, y, feature_names)
    
    # Xuất mô hình
    export_models(models, feature_names)
    
    print("\n" + "="*50)
    print("Huấn luyện mô hình hoàn tất!")
    print("="*50)

if __name__ == "__main__":
    main()
