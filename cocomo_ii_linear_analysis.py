#!/usr/bin/env python3
"""
COCOMO II Linear Relationship Analysis

Script này tạo ra một loạt biểu đồ phân tán để hiển thị mối quan hệ giữa chỉ số kích thước 
(metric) và nỗ lực (effort) cho từng schema như được mô tả trong comments:

- Trục X: Kích thước dự án theo metric tương ứng (KLOC, FP hoặc UCP)
- Trục Y: Nỗ lực phát triển (effort_pm) tính bằng người-tháng
- Đường hồi quy tuyến tính (đường đỏ đứt): y = ax + b
  * y: effort_pm (nỗ lực)
  * x: metric (KLOC/FP/UCP)
  * a: hệ số góc, thể hiện tốc độ tăng của effort khi metric tăng
  * b: hệ số tự do, thể hiện effort cơ bản khi metric = 0
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Thiết lập matplotlib để tránh lỗi backend
import matplotlib
matplotlib.use('Agg')

# Thiết lập style cho các biểu đồ
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 12

def load_datasets():
    """
    Tải dữ liệu từ các file CSV đã xử lý
    
    Returns:
        dict: Dictionary chứa dữ liệu cho từng schema
    """
    datasets = {}
    
    # Tải dữ liệu LOC-based
    try:
        loc_data = pd.read_csv('./processed_data/loc_based.csv')
        # Đổi tên cột để thống nhất
        if 'kloc' in loc_data.columns:
            loc_data['size'] = loc_data['kloc']
            loc_data['schema'] = 'LOC'
            datasets['LOC'] = loc_data[['size', 'effort_pm', 'schema']].copy()
            print(f"Đã tải {len(loc_data)} mẫu dữ liệu LOC")
    except FileNotFoundError:
        print("Không tìm thấy file loc_based.csv")
    
    # Tải dữ liệu FP-based  
    try:
        fp_data = pd.read_csv('./processed_data/fp_based.csv')
        if 'fp' in fp_data.columns:
            fp_data['size'] = fp_data['fp']
            fp_data['schema'] = 'FP'
            datasets['FP'] = fp_data[['size', 'effort_pm', 'schema']].copy()
            print(f"Đã tải {len(fp_data)} mẫu dữ liệu FP")
    except FileNotFoundError:
        print("Không tìm thấy file fp_based.csv")
    
    # Tải dữ liệu UCP-based
    try:
        ucp_data = pd.read_csv('./processed_data/ucp_based.csv')
        if 'ucp' in ucp_data.columns:
            ucp_data['size'] = ucp_data['ucp']
            ucp_data['schema'] = 'UCP'
            datasets['UCP'] = ucp_data[['size', 'effort_pm', 'schema']].copy()
            print(f"Đã tải {len(ucp_data)} mẫu dữ liệu UCP")
    except FileNotFoundError:
        print("Không tìm thấy file ucp_based.csv")
    
    return datasets

def perform_linear_regression_analysis(x, y):
    """
    Thực hiện phân tích hồi quy tuyến tính
    
    Args:
        x: Dữ liệu đầu vào (size metric)
        y: Dữ liệu đầu ra (effort_pm)
        
    Returns:
        dict: Kết quả phân tích bao gồm coefficients, R², p-value
    """
    # Loại bỏ các giá trị NaN
    mask = ~(np.isnan(x) | np.isnan(y))
    x_clean = x[mask]
    y_clean = y[mask]
    
    if len(x_clean) < 2:
        return None
    
    # Thực hiện hồi quy tuyến tính với scikit-learn
    X = x_clean.reshape(-1, 1)
    model = LinearRegression()
    model.fit(X, y_clean)
    
    # Dự đoán
    y_pred = model.predict(X)
    
    # Tính các chỉ số
    r2 = r2_score(y_clean, y_pred)
    mse = mean_squared_error(y_clean, y_pred)
    
    # Tính p-value bằng scipy
    slope, intercept, r_value, p_value, std_err = stats.linregress(x_clean, y_clean)
    
    return {
        'slope': model.coef_[0],  # Hệ số a
        'intercept': model.intercept_,  # Hệ số b
        'r2': r2,  # R²
        'p_value': p_value,  # p-value
        'mse': mse,  # Mean Squared Error
        'n_samples': len(x_clean),  # Số mẫu
        'model': model  # Mô hình để dự đoán
    }

def create_scatter_plot_with_regression(data, schema, output_dir='./'):
    """
    Tạo biểu đồ phân tán với đường hồi quy tuyến tính
    
    Args:
        data: DataFrame chứa dữ liệu
        schema: Tên schema (LOC, FP, UCP)
        output_dir: Thư mục lưu biểu đồ
    """
    # Chuẩn bị dữ liệu
    x = data['size'].values
    y = data['effort_pm'].values
    
    # Loại bỏ outliers quá lớn (optional)
    q99_x = np.percentile(x, 99)
    q99_y = np.percentile(y, 99)
    mask = (x <= q99_x) & (y <= q99_y) & (x > 0) & (y > 0)
    x_filtered = x[mask]
    y_filtered = y[mask]
    
    # Thực hiện phân tích hồi quy
    analysis = perform_linear_regression_analysis(x_filtered, y_filtered)
    
    if analysis is None:
        print(f"Không thể thực hiện phân tích cho schema {schema}")
        return
    
    # Tạo biểu đồ
    plt.figure(figsize=(12, 8))
    
    # Biểu đồ phân tán
    plt.scatter(x_filtered, y_filtered, alpha=0.6, s=50, color='blue', label=f'Dữ liệu thực tế ({analysis["n_samples"]} mẫu)')
    
    # Đường hồi quy tuyến tính
    x_range = np.linspace(x_filtered.min(), x_filtered.max(), 100)
    X_range = x_range.reshape(-1, 1)
    y_range = analysis['model'].predict(X_range)
    
    plt.plot(x_range, y_range, 'r--', linewidth=2, 
             label=f'Hồi quy tuyến tính: y = {analysis["slope"]:.3f}x + {analysis["intercept"]:.3f}')
    
    # Thêm thông tin thống kê lên biểu đồ
    stats_text = f'''Thống kê hồi quy:
• Hệ số góc (a): {analysis["slope"]:.3f}
• Hệ số tự do (b): {analysis["intercept"]:.3f}
• R² = {analysis["r2"]:.3f}
• p-value = {analysis["p_value"]:.3e}
• MSE = {analysis["mse"]:.3f}
• Số mẫu: {analysis["n_samples"]}'''
    
    plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
             fontsize=11)
    
    # Thiết lập labels và title
    unit_map = {'LOC': 'KLOC', 'FP': 'Function Points', 'UCP': 'Use Case Points'}
    plt.xlabel(f'Kích thước dự án ({unit_map.get(schema, schema)})')
    plt.ylabel('Nỗ lực phát triển (person-months)')
    plt.title(f'Mối quan hệ tuyến tính giữa kích thước và nỗ lực - Schema: {schema}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Lưu biểu đồ
    filename = f'cocomo_ii_linear_analysis_{schema.lower()}.png'
    filepath = os.path.join(output_dir, filename)
    plt.tight_layout()
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"Đã lưu biểu đồ: {filepath}")
    plt.close()
    
    return analysis

def create_comparison_summary(analyses):
    """
    Tạo bảng tóm tắt so sánh các schema
    
    Args:
        analyses: Dictionary chứa kết quả phân tích cho từng schema
    """
    print("\n" + "="*80)
    print("TỔNG KẾT PHÂN TÍCH HỒI QUY TUYẾN TÍNH COCOMO II")
    print("="*80)
    
    print(f"{'Schema':<10} {'Hệ số a':<12} {'Hệ số b':<12} {'R²':<10} {'p-value':<12} {'Số mẫu':<10}")
    print("-"*80)
    
    for schema, analysis in analyses.items():
        if analysis is not None:
            print(f"{schema:<10} {analysis['slope']:<12.4f} {analysis['intercept']:<12.2f} "
                  f"{analysis['r2']:<10.3f} {analysis['p_value']:<12.3e} {analysis['n_samples']:<10}")
    
    print("\nGiải thích:")
    print("• Hệ số a (slope): Tốc độ tăng effort khi size tăng 1 đơn vị")
    print("• Hệ số b (intercept): Effort cơ bản khi size = 0")
    print("• R²: Độ phù hợp của mô hình (0-1, càng gần 1 càng tốt)")
    print("• p-value: Mức ý nghĩa thống kê (< 0.05 có ý nghĩa)")

def create_combined_comparison_plot(datasets, analyses, output_dir='./'):
    """
    Tạo biểu đồ so sánh tất cả schemas trên cùng một đồ thị
    
    Args:
        datasets: Dictionary chứa dữ liệu các schema
        analyses: Dictionary chứa kết quả phân tích
        output_dir: Thư mục lưu biểu đồ
    """
    plt.figure(figsize=(15, 10))
    
    colors = {'LOC': 'blue', 'FP': 'green', 'UCP': 'red'}
    
    for schema, data in datasets.items():
        if schema in analyses and analyses[schema] is not None:
            analysis = analyses[schema]
            
            # Chuẩn bị dữ liệu
            x = data['size'].values
            y = data['effort_pm'].values
            
            # Loại bỏ outliers
            q99_x = np.percentile(x, 99)
            q99_y = np.percentile(y, 99)
            mask = (x <= q99_x) & (y <= q99_y) & (x > 0) & (y > 0)
            x_filtered = x[mask]
            y_filtered = y[mask]
            
            # Chuẩn hóa để hiển thị trên cùng một đồ thị
            # Chia cho max để đưa về scale 0-1
            x_norm = x_filtered / x_filtered.max()
            y_norm = y_filtered / y_filtered.max()
            
            color = colors.get(schema, 'black')
            
            # Scatter plot
            plt.scatter(x_norm, y_norm, alpha=0.6, s=30, color=color, 
                       label=f'{schema} (R²={analysis["r2"]:.3f})')
            
            # Đường hồi quy (cũng chuẩn hóa)
            x_range_norm = np.linspace(0, 1, 50)
            # Tính toán đường hồi quy trên dữ liệu gốc rồi chuẩn hóa
            x_range_orig = x_range_norm * x_filtered.max()
            X_range_orig = x_range_orig.reshape(-1, 1)
            y_range_orig = analysis['model'].predict(X_range_orig)
            y_range_norm = y_range_orig / y_filtered.max()
            
            plt.plot(x_range_norm, y_range_norm, '--', color=color, linewidth=2,
                    alpha=0.8)
    
    plt.xlabel('Kích thước dự án (chuẩn hóa)')
    plt.ylabel('Nỗ lực phát triển (chuẩn hóa)')
    plt.title('So sánh mối quan hệ tuyến tính giữa các Schema COCOMO II')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Lưu biểu đồ
    filepath = os.path.join(output_dir, 'cocomo_ii_schemas_comparison.png')
    plt.tight_layout()
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"Đã lưu biểu đồ so sánh: {filepath}")
    plt.close()

def main():
    """
    Hàm chính thực hiện phân tích
    """
    print("\n" + "="*60)
    print("PHÂN TÍCH HỒI QUY TUYẾN TÍNH COCOMO II")
    print("="*60)
    
    # 1. Tải dữ liệu
    print("\n1. Tải dữ liệu...")
    datasets = load_datasets()
    
    if not datasets:
        print("Không có dữ liệu để phân tích!")
        return
    
    # 2. Thực hiện phân tích cho từng schema
    print("\n2. Thực hiện phân tích hồi quy tuyến tính...")
    analyses = {}
    
    for schema, data in datasets.items():
        print(f"\nPhân tích schema {schema}...")
        
        # Tạo biểu đồ phân tán với đường hồi quy
        analysis = create_scatter_plot_with_regression(data, schema)
        analyses[schema] = analysis
    
    # 3. Tạo biểu đồ so sánh tổng thể
    print("\n3. Tạo biểu đồ so sánh...")
    create_combined_comparison_plot(datasets, analyses)
    
    # 4. Tóm tắt kết quả
    print("\n4. Tóm tắt kết quả:")
    create_comparison_summary(analyses)
    
    print("\n" + "="*60)
    print("HOÀN THÀNH PHÂN TÍCH!")
    print("="*60)
    print("\nCác file đã được tạo:")
    print("• cocomo_ii_linear_analysis_loc.png - Phân tích LOC")
    print("• cocomo_ii_linear_analysis_fp.png - Phân tích Function Points")
    print("• cocomo_ii_linear_analysis_ucp.png - Phân tích Use Case Points")
    print("• cocomo_ii_schemas_comparison.png - So sánh tất cả schemas")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPhân tích bị hủy bởi người dùng.")
    except Exception as e:
        print(f"Lỗi xảy ra: {str(e)}")
        import traceback
        traceback.print_exc()