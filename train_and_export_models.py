#!/usr/bin/env python3
"""
Script để huấn luyện và xuất các mô hình COCOMO II

Script này sẽ:
1. Đọc dữ liệu đã chuẩn hóa từ các file CSV
2. Kết hợp dữ liệu từ 3 schema khác nhau
3. Huấn luyện các mô hình khác nhau
4. Xuất các mô hình ra file .pkl để sử dụng trong backend
"""

import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import json
import warnings
warnings.filterwarnings('ignore')

print("=== Huấn luyện và xuất mô hình COCOMO II ===")

# Thiết lập đường dẫn
INPUT_DIR = './processed_data'
OUTPUT_DIR = './models'
COMBINED_DATA_PATH = './processed_data/combined_data.csv'

# Tạo thư mục đầu ra nếu chưa tồn tại
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print(f"Đã tạo thư mục {OUTPUT_DIR}")

cocomo_dir = os.path.join(OUTPUT_DIR, 'cocomo_ii_extended')
if not os.path.exists(cocomo_dir):
    os.makedirs(cocomo_dir)
    print(f"Đã tạo thư mục {cocomo_dir}")

# 1. Đọc dữ liệu từ các file CSV
print("\n1. Đọc dữ liệu")
loc_path = os.path.join(INPUT_DIR, 'loc_based.csv')
fp_path = os.path.join(INPUT_DIR, 'fp_based.csv')
ucp_path = os.path.join(INPUT_DIR, 'ucp_based.csv')

try:
    loc_df = pd.read_csv(loc_path)
    print(f"  - Đã đọc dữ liệu LOC: {loc_df.shape[0]} dòng × {loc_df.shape[1]} cột")
except Exception as e:
    print(f"  - Lỗi khi đọc file {loc_path}: {str(e)}")
    loc_df = pd.DataFrame()

try:
    fp_df = pd.read_csv(fp_path)
    print(f"  - Đã đọc dữ liệu FP: {fp_df.shape[0]} dòng × {fp_df.shape[1]} cột")
except Exception as e:
    print(f"  - Lỗi khi đọc file {fp_path}: {str(e)}")
    fp_df = pd.DataFrame()

try:
    ucp_df = pd.read_csv(ucp_path)
    print(f"  - Đã đọc dữ liệu UCP: {ucp_df.shape[0]} dòng × {ucp_df.shape[1]} cột")
except Exception as e:
    print(f"  - Lỗi khi đọc file {ucp_path}: {str(e)}")
    ucp_df = pd.DataFrame()

# 2. Chuẩn bị và kết hợp dữ liệu
print("\n2. Kết hợp dữ liệu")

def prepare_combined_data(loc_df, fp_df, ucp_df):
    """
    Chuẩn bị và kết hợp dữ liệu từ các schema khác nhau
    
    Args:
        loc_df, fp_df, ucp_df: DataFrame của từng schema
        
    Returns:
        DataFrame đã kết hợp
    """
    dfs = []
    
    # Chuẩn bị dữ liệu LOC
    if not loc_df.empty:
        loc_df_copy = loc_df.copy()
        loc_df_copy['schema'] = 'LOC'
        loc_df_copy['size'] = loc_df_copy['kloc']  # Đổi tên để thống nhất
        # Thêm các cột giả để cấu trúc thống nhất với các schema khác
        if 'fp' not in loc_df_copy.columns:
            loc_df_copy['fp'] = np.nan
        if 'ucp' not in loc_df_copy.columns:
            loc_df_copy['ucp'] = np.nan
        if 'uaw' not in loc_df_copy.columns:
            loc_df_copy['uaw'] = np.nan
        if 'uucw' not in loc_df_copy.columns:
            loc_df_copy['uucw'] = np.nan
        if 'tcf' not in loc_df_copy.columns:
            loc_df_copy['tcf'] = np.nan
        if 'ecf' not in loc_df_copy.columns:
            loc_df_copy['ecf'] = np.nan
        if 'sector' not in loc_df_copy.columns:
            loc_df_copy['sector'] = np.nan
        if 'language' not in loc_df_copy.columns:
            loc_df_copy['language'] = np.nan
        if 'methodology' not in loc_df_copy.columns:
            loc_df_copy['methodology'] = np.nan
        if 'applicationtype' not in loc_df_copy.columns:
            loc_df_copy['applicationtype'] = np.nan
        dfs.append(loc_df_copy)
    
    # Chuẩn bị dữ liệu FP
    if not fp_df.empty:
        fp_df_copy = fp_df.copy()
        fp_df_copy['schema'] = 'FP'
        fp_df_copy['size'] = fp_df_copy['fp']  # Đổi tên để thống nhất
        # Thêm các cột giả để cấu trúc thống nhất với các schema khác
        if 'kloc' not in fp_df_copy.columns:
            fp_df_copy['kloc'] = np.nan
        if 'ucp' not in fp_df_copy.columns:
            fp_df_copy['ucp'] = np.nan
        if 'uaw' not in fp_df_copy.columns:
            fp_df_copy['uaw'] = np.nan
        if 'uucw' not in fp_df_copy.columns:
            fp_df_copy['uucw'] = np.nan
        if 'tcf' not in fp_df_copy.columns:
            fp_df_copy['tcf'] = np.nan
        if 'ecf' not in fp_df_copy.columns:
            fp_df_copy['ecf'] = np.nan
        if 'sector' not in fp_df_copy.columns:
            fp_df_copy['sector'] = np.nan
        if 'language' not in fp_df_copy.columns:
            fp_df_copy['language'] = np.nan
        if 'methodology' not in fp_df_copy.columns:
            fp_df_copy['methodology'] = np.nan
        if 'applicationtype' not in fp_df_copy.columns:
            fp_df_copy['applicationtype'] = np.nan
        dfs.append(fp_df_copy)
    
    # Chuẩn bị dữ liệu UCP
    if not ucp_df.empty:
        ucp_df_copy = ucp_df.copy()
        ucp_df_copy['schema'] = 'UCP'
        ucp_df_copy['size'] = ucp_df_copy['ucp']  # Đổi tên để thống nhất
        # Thêm các cột giả để cấu trúc thống nhất với các schema khác
        if 'kloc' not in ucp_df_copy.columns:
            ucp_df_copy['kloc'] = np.nan
        if 'fp' not in ucp_df_copy.columns:
            ucp_df_copy['fp'] = np.nan
        dfs.append(ucp_df_copy)
    
    # Kết hợp các DataFrame
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        
        # Đảm bảo các cột cần thiết tồn tại
        required_columns = ['source', 'schema', 'size', 'effort_pm', 'time_months', 'developers']
        for col in required_columns:
            if col not in combined_df.columns:
                print(f"  - Cảnh báo: Cột {col} không tồn tại trong dữ liệu kết hợp!")
        
        return combined_df
    else:
        print("  - Lỗi: Không có dữ liệu nào để kết hợp!")
        return pd.DataFrame()

# Kết hợp dữ liệu
combined_df = prepare_combined_data(loc_df, fp_df, ucp_df)

if not combined_df.empty:
    print(f"  - Dữ liệu kết hợp: {combined_df.shape[0]} dòng × {combined_df.shape[1]} cột")
    print(f"  - Phân bố theo schema: {combined_df['schema'].value_counts().to_dict()}")
    
    # Lưu dữ liệu kết hợp
    combined_df.to_csv(COMBINED_DATA_PATH, index=False)
    print(f"  - Đã lưu dữ liệu kết hợp vào {COMBINED_DATA_PATH}")
else:
    print("  - Lỗi: Không thể kết hợp dữ liệu!")
    exit(1)

# 3. Tiền xử lý dữ liệu
print("\n3. Tiền xử lý dữ liệu")

def preprocess_data(df, target='effort_pm', log_transform=True):
    """
    Tiền xử lý dữ liệu cho huấn luyện mô hình
    
    Args:
        df: DataFrame đầu vào
        target: Tên biến mục tiêu
        log_transform: Có áp dụng biến đổi logarithmic hay không
        
    Returns:
        X, y, preprocessor: Dữ liệu đã xử lý và bộ tiền xử lý
    """
    if df.empty:
        print("  - Lỗi: DataFrame đầu vào rỗng!")
        return None, None, None
    
    # Tạo bản sao để không ảnh hưởng đến dữ liệu gốc
    df_copy = df.copy()
    
    # Xác định các biến phân loại và số
    categorical_cols = ['schema', 'sector', 'language', 'methodology', 'applicationtype']
    categorical_cols = [col for col in categorical_cols if col in df.columns]
    
    numeric_cols = ['size', 'time_months', 'developers']
    # Thêm các cột số khác nếu có
    for col in ['kloc', 'fp', 'ucp', 'uaw', 'uucw', 'tcf', 'ecf']:
        if col in df.columns and col not in numeric_cols:
            numeric_cols.append(col)
    
    # Sắp xếp lại các đặc trưng để chỉ giữ lại các cột quan trọng
    features = categorical_cols + numeric_cols
    
    # Lọc các cột tồn tại trong dữ liệu
    features = [col for col in features if col in df.columns]
    
    # Chuẩn bị dữ liệu
    X = df_copy[features]
    y = df_copy[target]
    
    # Áp dụng biến đổi logarithmic nếu cần
    if log_transform:
        y = np.log1p(y)
    
    # Thiết lập bộ tiền xử lý
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='unknown')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, [col for col in numeric_cols if col in X.columns]),
            ('cat', categorical_transformer, [col for col in categorical_cols if col in X.columns])
        ],
        remainder='drop'
    )
    
    return X, y, preprocessor

# Tiền xử lý dữ liệu
X, y, preprocessor = preprocess_data(combined_df, target='effort_pm', log_transform=True)

if X is not None and y is not None:
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"  - Tập huấn luyện: {X_train.shape[0]} mẫu")
    print(f"  - Tập kiểm thử: {X_test.shape[0]} mẫu")
    print(f"  - Các đặc trưng được sử dụng: {', '.join(X.columns.tolist())}")
else:
    print("  - Lỗi: Không thể tiền xử lý dữ liệu!")
    exit(1)

# 4. Huấn luyện các mô hình
print("\n4. Huấn luyện các mô hình")

def train_models(X_train, y_train, preprocessor):
    """
    Huấn luyện các mô hình khác nhau
    
    Args:
        X_train: Dữ liệu huấn luyện
        y_train: Nhãn huấn luyện
        preprocessor: Bộ tiền xử lý dữ liệu
        
    Returns:
        Dictionary chứa các pipeline đã huấn luyện
    """
    # Khởi tạo các mô hình
    models = {
        'Linear_Regression': LinearRegression(),
        'Decision_Tree': DecisionTreeRegressor(random_state=42, max_depth=10),
        'Random_Forest': RandomForestRegressor(random_state=42, n_estimators=100)
    }
    
    # Tạo pipeline và huấn luyện
    pipelines = {}
    
    for name, model in models.items():
        print(f"  - Đang huấn luyện mô hình {name}...")
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('model', model)
        ])
        
        # Huấn luyện mô hình
        pipeline.fit(X_train, y_train)
        
        # Lưu pipeline đã huấn luyện
        pipelines[name] = pipeline
    
    return pipelines

# Huấn luyện các mô hình
models = train_models(X_train, y_train, preprocessor)

# 5. Đánh giá các mô hình
print("\n5. Đánh giá các mô hình")

def evaluate_models(models, X_test, y_test, log_transform=True):
    """
    Đánh giá hiệu suất của các mô hình
    
    Args:
        models: Dictionary chứa các pipeline đã huấn luyện
        X_test: Dữ liệu kiểm thử
        y_test: Nhãn kiểm thử
        log_transform: Biến đổi logarithmic đã được áp dụng hay chưa
        
    Returns:
        DataFrame chứa các chỉ số hiệu suất
    """
    results = []
    
    for name, pipeline in models.items():
        # Dự đoán
        y_pred = pipeline.predict(X_test)
        
        # Chuyển đổi ngược lại nếu đã áp dụng biến đổi logarithmic
        if log_transform:
            y_test_orig = np.expm1(y_test)
            y_pred_orig = np.expm1(y_pred)
        else:
            y_test_orig = y_test
            y_pred_orig = y_pred
        
        # Tính các chỉ số hiệu suất
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Tính các chỉ số hiệu suất trên thang đo gốc
        mse_orig = mean_squared_error(y_test_orig, y_pred_orig)
        rmse_orig = np.sqrt(mse_orig)
        mae_orig = mean_absolute_error(y_test_orig, y_pred_orig)
        r2_orig = r2_score(y_test_orig, y_pred_orig)
        
        # Tính MMRE (Mean Magnitude of Relative Error)
        are = np.abs(y_pred_orig - y_test_orig) / y_test_orig
        mmre = np.mean(are)
        pred_25 = np.mean(are <= 0.25)  # Tỷ lệ dự đoán trong khoảng 25%
        
        results.append({
            'model': name,
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'r2': r2,
            'mse_orig': mse_orig,
            'rmse_orig': rmse_orig,
            'mae_orig': mae_orig,
            'r2_orig': r2_orig,
            'mmre': mmre,
            'pred_25': pred_25
        })
    
    return pd.DataFrame(results)

# Đánh giá các mô hình
evaluation = evaluate_models(models, X_test, y_test, log_transform=True)
print("  - Kết quả đánh giá các mô hình:")
print(evaluation[['model', 'r2_orig', 'mmre', 'pred_25']].to_string(index=False))

# 6. Xuất các mô hình
print("\n6. Xuất các mô hình")

def export_models(models, preprocessor, output_dir, log_transform=True):
    """
    Xuất các mô hình ra file .pkl
    
    Args:
        models: Dictionary chứa các pipeline đã huấn luyện
        preprocessor: Bộ tiền xử lý dữ liệu
        output_dir: Đường dẫn thư mục đầu ra
        log_transform: Biến đổi logarithmic đã được áp dụng hay chưa
    """
    # Lưu các pipeline
    for name, pipeline in models.items():
        model_path = os.path.join(output_dir, f"{name}.pkl")
        joblib.dump(pipeline, model_path)
        print(f"  - Đã xuất mô hình {name} vào {model_path}")
    
    # Lưu preprocessor
    preprocessor_path = os.path.join(output_dir, "preprocessor.pkl")
    joblib.dump(preprocessor, preprocessor_path)
    print(f"  - Đã xuất bộ tiền xử lý vào {preprocessor_path}")
    
    # Lưu cấu hình
    config = {
        'log_transform': log_transform,
        'models': list(models.keys()),
        'features': list(X.columns),
        'evaluation': evaluation.to_dict(orient='records'),
        'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    config_path = os.path.join(output_dir, "config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)
    print(f"  - Đã xuất cấu hình vào {config_path}")

# Xuất các mô hình
export_models(models, preprocessor, cocomo_dir, log_transform=True)

print("\n=== Hoàn thành quá trình huấn luyện và xuất mô hình ===")
print(f"Các mô hình đã được xuất vào thư mục: {cocomo_dir}")
print(f"Dữ liệu kết hợp đã được lưu vào: {COMBINED_DATA_PATH}")
print("Bạn có thể sử dụng các mô hình này để kết nối với backend.")
