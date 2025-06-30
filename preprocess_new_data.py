#!/usr/bin/env python3
"""
Script tự động tiền xử lý dữ liệu cho mô hình COCOMO II mở rộng

Script này sẽ:
1. Đọc dữ liệu từ các nguồn khác nhau (LOC, FP, UCP)
2. Chuẩn hóa và chuyển đổi dữ liệu theo cùng một cấu trúc
3. Kết hợp dữ liệu từ các nguồn khác nhau
4. Xuất ra dữ liệu đã tiền xử lý để huấn luyện mô hình
"""

import os
import sys
import numpy as np
import pandas as pd
import json
from datetime import datetime
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

# Đường dẫn thư mục dữ liệu
DATA_DIR = './datasets'
OUTPUT_DIR = './processed_data'
NEW_DATA_DIR = './sw-effort-predictive-analysis/Datasets'
BASE_DIR = './sw-effort-predictive-analysis'

# Đảm bảo thư mục đầu ra tồn tại
os.makedirs(OUTPUT_DIR, exist_ok=True)

def preprocess_loc_data(verbose=True):
    """
    Tiền xử lý dữ liệu dựa trên LOC
    
    Returns:
        DataFrame chứa dữ liệu đã tiền xử lý
    """
    if verbose:
        print("Tiền xử lý dữ liệu LOC...")
    
    # Đọc dữ liệu từ các nguồn LOC
    loc_files = [
        os.path.join(DATA_DIR, 'effortEstimation', 'cocomonasa_v1.arff'),
        os.path.join(DATA_DIR, 'effortEstimation', 'cocomo_sdr.arff'),
        os.path.join(DATA_DIR, 'effortEstimation', 'coc81_1_1.arff'),
        # Thêm các nguồn dữ liệu LOC khác nếu có
    ]
    
    # Đọc và xử lý từng file
    loc_data = []
    
    # Xử lý logic đọc từng file LOC...
    # (Giữ nguyên logic hiện tại của bạn)
    
    # Kết hợp dữ liệu
    if loc_data:
        loc_df = pd.concat(loc_data, ignore_index=True)
        # Xử lý và chuẩn hóa dữ liệu
        # (Giữ nguyên logic hiện tại của bạn)
        
        # Thêm cột schema
        loc_df['schema'] = 'LOC'
        
        if verbose:
            print(f"  - Đã xử lý {len(loc_df)} mẫu dữ liệu LOC")
        return loc_df
    else:
        if verbose:
            print("  - Không tìm thấy dữ liệu LOC phù hợp")
        return pd.DataFrame()

def preprocess_fp_data(verbose=True):
    """
    Tiền xử lý dữ liệu dựa trên Function Points (FP)
    
    Returns:
        DataFrame chứa dữ liệu đã tiền xử lý
    """
    if verbose:
        print("Tiền xử lý dữ liệu Function Points...")
    
    # Đọc dữ liệu từ các nguồn FP
    fp_files = [
        os.path.join(DATA_DIR, 'effortEstimation', 'china.arff'),
        os.path.join(DATA_DIR, 'effortEstimation', 'finnish.arff'),
        os.path.join(DATA_DIR, 'effortEstimation', 'kemerer.csv'),
        # Thêm các nguồn dữ liệu FP khác
        os.path.join(DATA_DIR, 'effortEstimation', 'albretch.csv'),
        os.path.join(DATA_DIR, 'effortEstimation', 'desharnais.csv'),
        os.path.join(NEW_DATA_DIR, 'albrecht.csv'),
        os.path.join(NEW_DATA_DIR, '02.desharnais.csv')
    ]
    
    # Đọc và xử lý từng file
    fp_data = []
    
    # Thêm logic xử lý file Albrecht mới
    try:
        albrecht_file = os.path.join(NEW_DATA_DIR, 'albrecht.csv')
        if os.path.exists(albrecht_file):
            albrecht_df = pd.read_csv(albrecht_file)
            
            # Xử lý và chuẩn hóa dữ liệu Albrecht - có cấu trúc: effort, size
            processed_df = pd.DataFrame({
                'source': 'albrecht_new',
                'effort_pm': albrecht_df['effort'],  # Đã ở định dạng PM
                'fp': albrecht_df['size'],  # Sử dụng size làm FP
                'size': albrecht_df['size'],
                'schema': 'FP'
            })
            
            # Ước tính thời gian và số nhà phát triển dựa trên COCOMO II
            # effort = a * (size)^b
            # time = c * (effort)^d
            # developers = effort / time
            a, b = 2.94, 0.91  # Hệ số COCOMO II
            c, d = 3.67, 0.28  # Hệ số cho time
            
            # Chuyển đổi FP sang KLOC (xấp xỉ)
            processed_df['kloc'] = processed_df['fp'] * 0.1  # Giả định 100 LOC/FP
            
            # Tính time và developers
            processed_df['time_months'] = c * (processed_df['effort_pm'] ** d)
            processed_df['developers'] = np.ceil(processed_df['effort_pm'] / processed_df['time_months'])
            
            fp_data.append(processed_df)
            if verbose:
                print(f"  - Đã xử lý {len(processed_df)} mẫu dữ liệu Albrecht mới")
    except Exception as e:
        if verbose:
            print(f"  - Lỗi khi xử lý dữ liệu Albrecht mới: {str(e)}")
    
    # Thêm logic xử lý file Desharnais mới
    try:
        desharnais_file = os.path.join(NEW_DATA_DIR, '02.desharnais.csv')
        if os.path.exists(desharnais_file):
            desharnais_df = pd.read_csv(desharnais_file)
            
            # Xử lý và chuẩn hóa dữ liệu Desharnais
            processed_df = pd.DataFrame({
                'source': 'desharnais',
                'effort_pm': desharnais_df['Effort'] / 180,  # Chuyển đổi giờ thành người-tháng (giả định 180 giờ/tháng)
                'fp': desharnais_df['PointsAjust'],
                'size': desharnais_df['PointsAjust'],
                'time_months': desharnais_df['Length'],
                'transactions': desharnais_df['Transactions'],
                'entities': desharnais_df['Entities'],
                'points_non_adjust': desharnais_df['PointsNonAdjust'],
                'adjustment': desharnais_df['Adjustment'],
                'team_exp': desharnais_df['TeamExp'],
                'manager_exp': desharnais_df['ManagerExp'],
                'year_end': desharnais_df['YearEnd'],
                'language': desharnais_df['Language'],
                'schema': 'FP'
            })
            
            # Tính developers
            processed_df['developers'] = np.ceil(processed_df['effort_pm'] / processed_df['time_months'])
            
            # Chuyển đổi FP sang KLOC (xấp xỉ)
            processed_df['kloc'] = processed_df['fp'] * 0.1  # Giả định 100 LOC/FP
            
            fp_data.append(processed_df)
            if verbose:
                print(f"  - Đã xử lý {len(processed_df)} mẫu dữ liệu Desharnais")
    except Exception as e:
        if verbose:
            print(f"  - Lỗi khi xử lý dữ liệu Desharnais: {str(e)}")
    
    # Thêm logic xử lý file Desharnais mới (cấu trúc mới)
    try:
        desharnais_file_simple = os.path.join(DATA_DIR, 'effortEstimation', 'desharnais.csv')
        if os.path.exists(desharnais_file_simple):
            desharnais_simple_df = pd.read_csv(desharnais_file_simple)
            
            # Xử lý và chuẩn hóa dữ liệu Desharnais đơn giản (effort, size)
            processed_df = pd.DataFrame({
                'source': 'desharnais_simple',
                'effort_pm': desharnais_simple_df['effort'] / 180,  # Chuyển đổi giờ thành người-tháng (giả định 180 giờ/tháng)
                'fp': desharnais_simple_df['size'],
                'size': desharnais_simple_df['size'],
                'schema': 'FP'
            })
            
            # Ước tính thời gian dựa trên COCOMO II
            a, b = 2.94, 0.91  # Hệ số COCOMO II
            c, d = 3.67, 0.28  # Hệ số cho time
            
            # Tính time
            processed_df['time_months'] = c * (processed_df['effort_pm'] ** d)
            
            # Tính developers
            processed_df['developers'] = np.ceil(processed_df['effort_pm'] / processed_df['time_months'])
            
            # Chuyển đổi FP sang KLOC (xấp xỉ)
            processed_df['kloc'] = processed_df['fp'] * 0.1  # Giả định 100 LOC/FP
            
            fp_data.append(processed_df)
            if verbose:
                print(f"  - Đã xử lý {len(processed_df)} mẫu dữ liệu Desharnais đơn giản")
    except Exception as e:
        if verbose:
            print(f"  - Lỗi khi xử lý dữ liệu Desharnais đơn giản: {str(e)}")
    
    # Thêm logic xử lý file Desharnais chi tiết
    try:
        desharnais_file_detailed = os.path.join(NEW_DATA_DIR, '02.desharnais.csv')
        if os.path.exists(desharnais_file_detailed):
            desharnais_df = pd.read_csv(desharnais_file_detailed)
            
            # Xử lý và chuẩn hóa dữ liệu Desharnais
            processed_df = pd.DataFrame({
                'source': 'desharnais_detailed',
                'effort_pm': desharnais_df['Effort'] / 180,  # Chuyển đổi giờ thành người-tháng (giả định 180 giờ/tháng)
                'fp': desharnais_df['PointsAjust'],
                'size': desharnais_df['PointsAjust'],
                'time_months': desharnais_df['Length'],
                'transactions': desharnais_df['Transactions'],
                'entities': desharnais_df['Entities'],
                'points_non_adjust': desharnais_df['PointsNonAdjust'],
                'adjustment': desharnais_df['Adjustment'],
                'team_exp': desharnais_df['TeamExp'],
                'manager_exp': desharnais_df['ManagerExp'],
                'year_end': desharnais_df['YearEnd'],
                'language': desharnais_df['Language'],
                'schema': 'FP'
            })
            
            # Tính developers
            processed_df['developers'] = np.ceil(processed_df['effort_pm'] / processed_df['time_months'])
            
            # Chuyển đổi FP sang KLOC (xấp xỉ)
            processed_df['kloc'] = processed_df['fp'] * 0.1  # Giả định 100 LOC/FP
            
            fp_data.append(processed_df)
            if verbose:
                print(f"  - Đã xử lý {len(processed_df)} mẫu dữ liệu Desharnais chi tiết")
    except Exception as e:
        if verbose:
            print(f"  - Lỗi khi xử lý dữ liệu Desharnais chi tiết: {str(e)}")
    
    # Xử lý dữ liệu Desharnais từ outputDesharnai.csv (dữ liệu thực tế)
    try:
        desharnais_output_file = os.path.join(BASE_DIR, 'effort-estimation-by-using-pre-trained-model', 'outputs', 'outputDesharnai.csv')
        if os.path.exists(desharnais_output_file):
            desharnais_output_df = pd.read_csv(desharnais_output_file)
            
            # Xử lý và chuẩn hóa dữ liệu Desharnais từ output
            processed_df = pd.DataFrame({
                'source': 'desharnais_real_world',
                'effort_pm': desharnais_output_df['y_test'] / 180,  # Chuyển đổi giờ thành người-tháng
                'fp': desharnais_output_df['PointsAjust'],
                'size': desharnais_output_df['PointsAjust'],
                'time_months': np.nan,  # Sẽ ước tính dựa trên effort
                'transactions': desharnais_output_df['Transactions'],
                'entities': desharnais_output_df['Entities'],
                'points_non_adjust': desharnais_output_df['PointsNonAdjust'],
                'schema': 'FP'
            })
            
            # Ước tính thời gian dựa trên COCOMO II
            c, d = 3.67, 0.28  # Hệ số cho time
            
            # Tính time
            processed_df['time_months'] = c * (processed_df['effort_pm'] ** d)
            
            # Tính developers
            processed_df['developers'] = np.ceil(processed_df['effort_pm'] / processed_df['time_months'])
            
            # Chuyển đổi FP sang KLOC (xấp xỉ)
            processed_df['kloc'] = processed_df['fp'] * 0.1  # Giả định 100 LOC/FP
            
            # Thêm predicted effort cho so sánh sau này
            processed_df['predicted_effort_pm'] = desharnais_output_df['y_pred'] / 180
            
            fp_data.append(processed_df)
            if verbose:
                print(f"  - Đã xử lý {len(processed_df)} mẫu dữ liệu Desharnais thực tế")
    except Exception as e:
        if verbose:
            print(f"  - Lỗi khi xử lý dữ liệu Desharnais thực tế: {str(e)}")
    
    # Xử lý các nguồn dữ liệu FP khác từ logic hiện tại của bạn
    
    # Kết hợp dữ liệu
    if fp_data:
        fp_df = pd.concat(fp_data, ignore_index=True)
        
        # Xử lý và chuẩn hóa dữ liệu nếu cần
        # Đảm bảo các cột cơ bản đều có
        for col in ['sector', 'language', 'methodology', 'applicationtype']:
            if col not in fp_df.columns:
                fp_df[col] = np.nan
        
        if verbose:
            print(f"  - Đã xử lý tổng cộng {len(fp_df)} mẫu dữ liệu FP")
        return fp_df
    else:
        if verbose:
            print("  - Không tìm thấy dữ liệu FP phù hợp")
        return pd.DataFrame()

def preprocess_ucp_data(verbose=True):
    """
    Tiền xử lý dữ liệu dựa trên Use Case Points (UCP)
    
    Returns:
        DataFrame chứa dữ liệu đã tiền xử lý
    """
    if verbose:
        print("Tiền xử lý dữ liệu Use Case Points...")
    
    # Đọc dữ liệu từ các nguồn UCP
    ucp_files = [
        # Thêm các nguồn dữ liệu UCP
        # (Giữ nguyên logic hiện tại của bạn)
    ]
    
    # Kết hợp dữ liệu
    # (Giữ nguyên logic hiện tại của bạn)
    
    # Mẫu logic xử lý
    ucp_df = pd.DataFrame()  # Thay thế bằng logic thực tế của bạn
    
    if len(ucp_df) > 0:
        if verbose:
            print(f"  - Đã xử lý {len(ucp_df)} mẫu dữ liệu UCP")
        return ucp_df
    else:
        if verbose:
            print("  - Không tìm thấy dữ liệu UCP phù hợp")
        return pd.DataFrame()

def combine_data(loc_df, fp_df, ucp_df, verbose=True):
    """
    Kết hợp dữ liệu từ các nguồn khác nhau
    
    Args:
        loc_df: DataFrame chứa dữ liệu LOC
        fp_df: DataFrame chứa dữ liệu FP
        ucp_df: DataFrame chứa dữ liệu UCP
        
    Returns:
        DataFrame chứa dữ liệu đã kết hợp
    """
    if verbose:
        print("Kết hợp dữ liệu từ các nguồn...")
    
    # Danh sách DataFrame không rỗng
    dfs = []
    if len(loc_df) > 0:
        dfs.append(loc_df)
    if len(fp_df) > 0:
        dfs.append(fp_df)
    if len(ucp_df) > 0:
        dfs.append(ucp_df)
    
    if not dfs:
        if verbose:
            print("  - Không có dữ liệu để kết hợp")
        return pd.DataFrame()
    
    # Kết hợp dữ liệu
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Đảm bảo các cột cơ bản đều có
    required_columns = ['source', 'schema', 'size', 'effort_pm', 'time_months', 'developers']
    for col in required_columns:
        if col not in combined_df.columns:
            combined_df[col] = np.nan
    
    # Xử lý dữ liệu thiếu
    # Thay thế giá trị thiếu trong cột phân loại bằng 'unknown'
    categorical_cols = ['sector', 'language', 'methodology', 'applicationtype']
    for col in categorical_cols:
        if col in combined_df.columns:
            combined_df[col] = combined_df[col].fillna('unknown')
    
    # Thêm một số cột mới có thể giúp cải thiện mô hình
    if 'effort_pm' in combined_df.columns and 'time_months' in combined_df.columns:
        combined_df['productivity'] = combined_df['size'] / combined_df['effort_pm']
        combined_df['size_per_month'] = combined_df['size'] / combined_df['time_months']
    
    if verbose:
        print(f"  - Đã kết hợp {len(combined_df)} mẫu dữ liệu")
        print(f"  - Phân bố theo schema: {combined_df['schema'].value_counts().to_dict()}")
    
    return combined_df

def export_data(df, filename, verbose=True):
    """
    Xuất dữ liệu ra file CSV
    
    Args:
        df: DataFrame chứa dữ liệu
        filename: Tên file xuất
        verbose: In thông báo chi tiết
    """
    if len(df) == 0:
        if verbose:
            print(f"Không có dữ liệu để xuất ra {filename}")
        return
    
    output_path = os.path.join(OUTPUT_DIR, filename)
    df.to_csv(output_path, index=False)
    
    if verbose:
        print(f"Đã xuất {len(df)} mẫu dữ liệu ra {output_path}")

def update_metadata(datasets, verbose=True):
    """
    Cập nhật file metadata.json
    
    Args:
        datasets: Dictionary chứa thông tin về các bộ dữ liệu
        verbose: In thông báo chi tiết
    """
    metadata_path = os.path.join(OUTPUT_DIR, 'metadata.json')
    
    # Đọc metadata hiện có nếu có
    metadata = {}
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        except:
            metadata = {}
    
    # Cập nhật metadata
    metadata.update(datasets)
    metadata['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Lưu metadata
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    if verbose:
        print(f"Đã cập nhật metadata tại {metadata_path}")

def main():
    """
    Hàm chính để thực hiện tiền xử lý dữ liệu
    """
    print("\n" + "="*50)
    print("Tiền xử lý dữ liệu tự động cho mô hình COCOMO II mở rộng")
    print("="*50)
    
    # Tiền xử lý dữ liệu từ các nguồn
    loc_df = preprocess_loc_data()
    fp_df = preprocess_fp_data()
    ucp_df = preprocess_ucp_data()
    
    # Kết hợp dữ liệu
    combined_df = combine_data(loc_df, fp_df, ucp_df)
    
    # Xuất dữ liệu đã xử lý
    if len(loc_df) > 0:
        export_data(loc_df, 'loc_based.csv')
    
    if len(fp_df) > 0:
        export_data(fp_df, 'fp_based.csv')
    
    if len(ucp_df) > 0:
        export_data(ucp_df, 'ucp_based.csv')
    
    if len(combined_df) > 0:
        export_data(combined_df, 'combined_data.csv')
    
    # Cập nhật metadata
    datasets = {
        'loc_based': {
            'rows': len(loc_df),
            'columns': list(loc_df.columns) if len(loc_df) > 0 else [],
            'schema': 'LOC',
            'description': 'Dữ liệu dựa trên Lines of Code (LOC)'
        },
        'fp_based': {
            'rows': len(fp_df),
            'columns': list(fp_df.columns) if len(fp_df) > 0 else [],
            'schema': 'FP',
            'description': 'Dữ liệu dựa trên Function Points (FP)'
        },
        'ucp_based': {
            'rows': len(ucp_df),
            'columns': list(ucp_df.columns) if len(ucp_df) > 0 else [],
            'schema': 'UCP',
            'description': 'Dữ liệu dựa trên Use Case Points (UCP)'
        },
        'combined_data': {
            'rows': len(combined_df),
            'columns': list(combined_df.columns) if len(combined_df) > 0 else [],
            'schema': 'mixed',
            'description': 'Dữ liệu kết hợp từ các nguồn LOC, FP, UCP'
        }
    }
    update_metadata(datasets)
    
    print("\n" + "="*50)
    print("Hoàn thành tiền xử lý dữ liệu!")
    print("="*50)

if __name__ == "__main__":
    main()
