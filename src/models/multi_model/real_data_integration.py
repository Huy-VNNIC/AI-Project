#!/usr/bin/env python3
"""
Tích hợp dữ liệu thực tế từ các bộ dữ liệu phần mềm vào hệ thống ước lượng đa mô hình
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Đảm bảo có thể import mô hình từ cùng thư mục
try:
    # Khi import từ package
    from .estimation_models import COCOMOII, FunctionPoints, UseCasePoints, PlanningPoker
    from .multi_model_integration import MultiModelIntegration
    from .agile_cocomo import AgileCOCOMO
except ImportError:
    # Khi chạy trực tiếp
    from estimation_models import COCOMOII, FunctionPoints, UseCasePoints, PlanningPoker
    from src.models.multi_model import MultiModelIntegration
    from agile_cocomo import AgileCOCOMO

# Đường dẫn tới các bộ dữ liệu
PROJECT_ROOT = Path(__file__).parent.parent
DATASETS_DIR = PROJECT_ROOT / "datasets" / "effortEstimation"
SW_DATASETS_DIR = PROJECT_ROOT / "Software-estimation-datasets"

def load_cocomo_dataset():
    """Tải dữ liệu COCOMO từ bộ dữ liệu có sẵn"""
    cocomo_path = SW_DATASETS_DIR / "COCOMO-81.csv"
    if cocomo_path.exists():
        df = pd.read_csv(cocomo_path)
        print(f"Đã tải dữ liệu COCOMO từ {cocomo_path}")
        return df
    
    # Fallback to other COCOMO datasets
    alternative_paths = [
        SW_DATASETS_DIR / "nasa93.arff",
        DATASETS_DIR / "cocomo_sdr.arff",
        DATASETS_DIR / "cocomonasa_v1.arff"
    ]
    
    for path in alternative_paths:
        if path.exists() and path.suffix == ".arff":
            from scipy.io import arff
            data, meta = arff.loadarff(path)
            print(f"Đã tải dữ liệu COCOMO từ {path}")
            return pd.DataFrame(data)
    
    # If no datasets found, return None
    print("Không tìm thấy dữ liệu COCOMO II")
    return None

def load_function_points_dataset():
    """Tải dữ liệu Function Points từ bộ dữ liệu có sẵn"""
    fp_paths = [
        SW_DATASETS_DIR / "Desharnais.csv",
        SW_DATASETS_DIR / "albrecht.arff",
        DATASETS_DIR / "albretch.csv",
        DATASETS_DIR / "china.arff",
        SW_DATASETS_DIR / "china.arff"
    ]
    
    for path in fp_paths:
        if path.exists():
            if path.suffix == ".arff":
                from scipy.io import arff
                data, meta = arff.loadarff(path)
                df = pd.DataFrame(data)
                print(f"Đã tải dữ liệu Function Points từ {path}")
                return df
            elif path.suffix == ".csv":
                df = pd.read_csv(path)
                print(f"Đã tải dữ liệu Function Points từ {path}")
                return df
    
    # If no datasets found, return None
    print("Không tìm thấy dữ liệu Function Points")
    return None

def load_use_case_points_dataset():
    """Tải dữ liệu Use Case Points từ bộ dữ liệu có sẵn"""
    ucp_path = SW_DATASETS_DIR / "UCP_Dataset.csv"
    
    if ucp_path.exists():
        df = pd.read_csv(ucp_path, sep=';')
        print(f"Đã tải dữ liệu Use Case Points từ {ucp_path}")
        return df
    
    # If no datasets found, return None
    print("Không tìm thấy dữ liệu Use Case Points")
    return None

def preprocess_cocomo_data(df):
    """Tiền xử lý dữ liệu COCOMO II để phù hợp với mô hình"""
    if df is None:
        return None
    
    # Kiểm tra xem có các cột cần thiết không
    required_columns = ['loc', 'actual']
    
    # Kiểm tra và map các tên cột phổ biến
    column_mapping = {
        'loc': 'kloc',
        'sloc': 'kloc',
        'ksloc': 'kloc',
        'size': 'kloc',
        'actual': 'effort',
        'acteff': 'effort',
        'actualeffort': 'effort',
        'actual_effort': 'effort',
        'months': 'effort'
    }
    
    # Chuẩn hóa tên cột
    df.columns = [col.lower() if isinstance(col, str) else col for col in df.columns]
    
    # Map các tên cột
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns and new_col not in df.columns:
            df[new_col] = df[old_col]
    
    # Kiểm tra xem có các cột bắt buộc không
    missing_columns = []
    for col in required_columns:
        mapped_col = column_mapping.get(col, col)
        if col not in df.columns and mapped_col not in df.columns:
            missing_columns.append(col)
    
    if missing_columns:
        print(f"Không tìm thấy các cột {missing_columns} trong dữ liệu COCOMO")
        return None
    
    # Chỉ giữ các hàng có giá trị hợp lệ
    if 'kloc' in df.columns and 'effort' in df.columns:
        df = df.dropna(subset=['kloc', 'effort'])
    else:
        print("Không tìm thấy cột kloc hoặc effort sau khi map")
        return None
    
    # Chuyển đổi KLOC sang số thực nếu cần
    df['kloc'] = pd.to_numeric(df['kloc'], errors='coerce')
    df['effort'] = pd.to_numeric(df['effort'], errors='coerce')
    
    # Lọc các giá trị không hợp lệ
    df = df[(df['kloc'] > 0) & (df['effort'] > 0)]
    
    print(f"Đã xử lý {len(df)} dự án COCOMO hợp lệ")
    
    # Tạo các tham số cần thiết cho COCOMO II
    project_data_list = []
    
    for _, row in df.iterrows():
        project_data = {
            'size': float(row['kloc']),
            'reliability': 1.0,
            'complexity': 1.0,
            'reuse': 0.0,
            'documentation': 1.0,
            'time_constraint': 1.0,
            'storage_constraint': 1.0,
            'platform_volatility': 1.0,
            'tool_experience': 1.0,
            'personnel_capability': 1.0,
            'personnel_experience': 1.0,
            'language_experience': 1.0,
            'team_cohesion': 1.0,
            'process_maturity': 1.0
        }
        
        # Thêm các trường nếu có trong dữ liệu
        optional_fields = [
            'rely', 'data', 'cplx', 'time', 'stor', 'virt', 'turn',
            'acap', 'aexp', 'pcap', 'vexp', 'lexp', 'modp', 'tool', 'sced'
        ]
        
        for field in optional_fields:
            if field in row:
                if pd.notna(row[field]):
                    # Map các trường COCOMO-81 sang các trường trong model
                    if field == 'rely':
                        project_data['reliability'] = float(row[field])
                    elif field == 'cplx':
                        project_data['complexity'] = float(row[field])
                    elif field == 'time':
                        project_data['time_constraint'] = float(row[field])
                    elif field == 'stor':
                        project_data['storage_constraint'] = float(row[field])
                    elif field == 'acap' or field == 'pcap':
                        project_data['personnel_capability'] = float(row[field])
                    elif field == 'aexp' or field == 'vexp' or field == 'lexp':
                        project_data['personnel_experience'] = float(row[field])
                    elif field == 'tool':
                        project_data['tool_experience'] = float(row[field])
        
        # Thêm actual_effort
        project_data['actual_effort'] = float(row['effort'])
        
        project_data_list.append(project_data)
    
    return project_data_list

def preprocess_fp_data(df):
    """Tiền xử lý dữ liệu Function Points để phù hợp với mô hình"""
    if df is None:
        return None
    
    # Chuẩn hóa tên cột
    df.columns = [col.lower() if isinstance(col, str) else col for col in df.columns]
    
    # Kiểm tra nếu là Desharnais dataset
    if 'pointsajust' in df.columns and 'effort' in df.columns:
        print("Đã phát hiện dữ liệu Desharnais")
        project_data_list = []
        
        for _, row in df.iterrows():
            if pd.isna(row['pointsajust']) or pd.isna(row['effort']):
                continue
                
            project_data = {
                'function_points': float(row['pointsajust']),
                'complexity_multiplier': 1.0,
                'language_multiplier': 53,  # Giá trị mặc định
                'actual_effort': float(row['effort'])
            }
            
            project_data_list.append(project_data)
        
        print(f"Đã xử lý {len(project_data_list)} dự án Function Points (Desharnais) hợp lệ")
        return project_data_list
    
    # Kiểm tra nếu là Albrecht dataset
    if 'output' in df.columns and 'input' in df.columns and 'file' in df.columns and 'fpoints' in df.columns:
        print("Đã phát hiện dữ liệu Albrecht")
        project_data_list = []
        
        effort_column = None
        for col in ['effort', 'effortmonths', 'months']:
            if col in df.columns:
                effort_column = col
                break
        
        if not effort_column:
            print("Không tìm thấy cột effort trong dữ liệu Albrecht")
            return None
        
        for _, row in df.iterrows():
            if pd.isna(row['fpoints']) or pd.isna(row[effort_column]):
                continue
                
            project_data = {
                'function_points': float(row['fpoints']),
                'complexity_multiplier': 1.0,
                'language_multiplier': 53,  # Giá trị mặc định
                'actual_effort': float(row[effort_column])
            }
            
            # Thêm chi tiết về các thành phần FP nếu có
            fp_components = ['input', 'output', 'inquiry', 'file', 'interface']
            for comp in fp_components:
                if comp in df.columns and not pd.isna(row[comp]):
                    project_data[comp] = float(row[comp])
            
            project_data_list.append(project_data)
        
        print(f"Đã xử lý {len(project_data_list)} dự án Function Points (Albrecht) hợp lệ")
        return project_data_list
    
    # Xử lý trường hợp chung
    print("Xử lý dữ liệu Function Points định dạng chung")
    
    # Kiểm tra các cột cần thiết
    fp_columns = [
        'input', 'output', 'inquiry', 'file', 'interface',  # Các cột FP cơ bản
        'inputs', 'outputs', 'enquiries', 'files', 'interfaces',  # Các tên thay thế
        'ufp', 'rawfp', 'fps', 'fp', 'fpoints'  # Các cột UFP/FP tổng
    ]
    
    effort_columns = ['effort', 'months', 'actualeffort', 'actual_effort', 'effortmonths']
    
    # Kiểm tra xem có ít nhất một cột FP không
    has_fp = any(col in df.columns for col in fp_columns)
    has_effort = any(col in df.columns for col in effort_columns)
    
    if not has_fp or not has_effort:
        print("Dữ liệu Function Points không đủ các cột cần thiết")
        return None
    
    # Map các tên cột phổ biến
    column_mapping = {
        'inputs': 'input',
        'outputs': 'output',
        'enquiries': 'inquiry',
        'files': 'file',
        'interfaces': 'interface',
        'actualeffort': 'effort',
        'actual_effort': 'effort',
        'months': 'effort',
        'effortmonths': 'effort',
        'rawfp': 'ufp',
        'fps': 'ufp',
        'fp': 'ufp',
        'fpoints': 'ufp'
    }
    
    # Map các tên cột
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns and new_col not in df.columns:
            df[new_col] = df[old_col]
    
    # Tạo danh sách dự án
    project_data_list = []
    
    for _, row in df.iterrows():
        project_data = {
            'function_points': 0,
            'complexity_multiplier': 1.0,
            'language_multiplier': 53  # Giá trị mặc định cho ngôn ngữ lập trình trung bình
        }
        
        # Nếu có UFP, sử dụng nó
        if 'ufp' in df.columns and not pd.isna(row['ufp']):
            project_data['function_points'] = float(row['ufp'])
        # Nếu không, tính từ các thành phần
        elif all(c in df.columns for c in ['input', 'output', 'inquiry', 'file', 'interface']):
            fp_components = {
                'input': float(row['input']) if not pd.isna(row['input']) else 0,
                'output': float(row['output']) if not pd.isna(row['output']) else 0,
                'inquiry': float(row['inquiry']) if not pd.isna(row['inquiry']) else 0,
                'file': float(row['file']) if not pd.isna(row['file']) else 0,
                'interface': float(row['interface']) if not pd.isna(row['interface']) else 0
            }
            project_data.update(fp_components)
            # Tính tổng UFP
            project_data['function_points'] = sum(fp_components.values())
        else:
            # Không đủ thông tin
            continue
        
        # Thêm effort nếu có
        if 'effort' in df.columns and not pd.isna(row['effort']):
            project_data['actual_effort'] = float(row['effort'])
        else:
            # Không có thông tin effort
            continue
        
        project_data_list.append(project_data)
    
    print(f"Đã xử lý {len(project_data_list)} dự án Function Points hợp lệ")
    return project_data_list

def preprocess_ucp_data(df):
    """Tiền xử lý dữ liệu Use Case Points để phù hợp với mô hình"""
    if df is None:
        return None
    
    # Chuẩn hóa tên cột
    df.columns = [col.lower() if isinstance(col, str) else col for col in df.columns]
    
    # Thay thế dấu phẩy bằng dấu chấm trong các cột số
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.replace(',', '.', regex=False) if isinstance(df[col], pd.Series) else df[col]
    
    # Kiểm tra nếu là UCP_Dataset
    if 'uaw' in df.columns and 'uucw' in df.columns and 'tcf' in df.columns and 'ecf' in df.columns:
        print("Đã phát hiện dữ liệu UCP Dataset")
        
        effort_column = None
        for col in ['real_effort_person_hours', 'effort', 'actual_effort', 'actual']:
            if col in df.columns:
                effort_column = col
                break
        
        if not effort_column:
            print("Không tìm thấy cột effort trong dữ liệu UCP")
            return None
        
        project_data_list = []
        
        for _, row in df.iterrows():
            # Kiểm tra giá trị hợp lệ
            required_fields = ['uaw', 'uucw', 'tcf', 'ecf', effort_column]
            if any(pd.isna(row[field]) for field in required_fields):
                continue
            
            # Chuyển đổi các chuỗi sang số
            uaw = float(row['uaw']) if isinstance(row['uaw'], str) else row['uaw']
            uucw = float(row['uucw']) if isinstance(row['uucw'], str) else row['uucw']
            tcf = float(row['tcf']) if isinstance(row['tcf'], str) else row['tcf']
            ecf = float(row['ecf']) if isinstance(row['ecf'], str) else row['ecf']
            effort = float(row[effort_column]) if isinstance(row[effort_column], str) else row[effort_column]
            
            # Tính UCP
            ucp = (uaw + uucw) * tcf * ecf
            
            project_data = {
                'use_case_points': ucp,
                'uaw': uaw,
                'uucw': uucw,
                'tcf': tcf,
                'ecf': ecf,
                'productivity_factor': 20,  # Giá trị mặc định
                'actual_effort': effort
            }
            
            project_data_list.append(project_data)
        
        print(f"Đã xử lý {len(project_data_list)} dự án Use Case Points hợp lệ")
        return project_data_list
    
    # Xử lý trường hợp có UCP trực tiếp
    if 'ucp' in df.columns:
        print("Đã phát hiện dữ liệu có trường UCP")
        
        effort_column = None
        for col in ['effort', 'actualeffort', 'actual_effort', 'months']:
            if col in df.columns:
                effort_column = col
                break
        
        if not effort_column:
            print("Không tìm thấy cột effort trong dữ liệu UCP")
            return None
        
        project_data_list = []
        
        for _, row in df.iterrows():
            if pd.isna(row['ucp']) or pd.isna(row[effort_column]):
                continue
                
            project_data = {
                'use_case_points': float(row['ucp']),
                'productivity_factor': 20,  # Giá trị mặc định
                'actual_effort': float(row[effort_column])
            }
            
            project_data_list.append(project_data)
        
        print(f"Đã xử lý {len(project_data_list)} dự án Use Case Points hợp lệ")
        return project_data_list
    
    print("Không tìm thấy cấu trúc dữ liệu UCP phù hợp")
    return None

def evaluate_model_performance(model, dataset, model_name):
    """Đánh giá hiệu suất của mô hình trên tập dữ liệu thực tế"""
    if not dataset:
        print(f"Không có dữ liệu cho mô hình {model_name}")
        return None
    
    results = []
    actual_efforts = []
    predicted_efforts = []
    errors = 0
    
    for project_data in dataset:
        # Kiểm tra xem có actual_effort không
        if 'actual_effort' not in project_data:
            continue
        
        # Lưu giá trị actual_effort
        actual_effort = project_data['actual_effort']
        if actual_effort <= 0:
            # Bỏ qua dự án có actual_effort không hợp lệ
            continue
        
        try:
            # Ước lượng nỗ lực
            estimation = model.estimate_effort(project_data)
            
            # Kiểm tra kết quả
            if not estimation or 'effort_pm' not in estimation:
                continue
            
            predicted_effort = estimation['effort_pm']
            
            # Bỏ qua dự án có predicted_effort không hợp lệ
            if predicted_effort <= 0 or not np.isfinite(predicted_effort):
                continue
            
            # Tính toán sai số
            error = abs(predicted_effort - actual_effort)
            mre = error / actual_effort
            
            # Lưu kết quả
            results.append({
                'actual_effort': actual_effort,
                'predicted_effort': predicted_effort,
                'error': error,
                'mre': mre
            })
            
            actual_efforts.append(actual_effort)
            predicted_efforts.append(predicted_effort)
            
        except Exception as e:
            errors += 1
            if errors <= 3:  # Chỉ in ra 3 lỗi đầu tiên để tránh rối mắt
                print(f"Lỗi khi ước lượng dự án với {model_name}: {e}")
            continue
    
    if not results:
        print(f"Không có kết quả đánh giá cho mô hình {model_name}")
        return None
    
    print(f"Đã đánh giá thành công {len(results)} dự án với mô hình {model_name}")
    
    # Tính các chỉ số đánh giá
    mre_values = [result['mre'] for result in results]
    mmre = np.mean(mre_values)
    pred_25 = sum(1 for mre in mre_values if mre <= 0.25) / len(mre_values)
    rmse = np.sqrt(np.mean([(result['actual_effort'] - result['predicted_effort'])**2 for result in results]))
    
    # Trả về kết quả
    return {
        'model': model_name,
        'actual_efforts': actual_efforts,
        'predicted_efforts': predicted_efforts,
        'results': results,
        'mmre': mmre,
        'pred_25': pred_25,
        'rmse': rmse
    }
    pred_25 = sum(1 for mre in mre_values if mre <= 0.25) / len(mre_values)
    rmse = np.sqrt(np.mean([(result['actual_effort'] - result['predicted_effort'])**2 for result in results]))
    
    # Trả về kết quả
    return {
        'model': model_name,
        'actual_efforts': actual_efforts,
        'predicted_efforts': predicted_efforts,
        'results': results,
        'mmre': mmre,
        'pred_25': pred_25,
        'rmse': rmse
    }

def visualize_model_performance(evaluation_results, title="Hiệu suất mô hình trên dữ liệu thực tế"):
    """Trực quan hóa hiệu suất của các mô hình"""
    # Lọc bỏ các kết quả None
    valid_results = [result for result in evaluation_results if result is not None]
    
    if not valid_results:
        print("Không có kết quả đánh giá hợp lệ để trực quan hóa")
        return
    
    # Kiểm tra xem có đủ dữ liệu trong các kết quả không
    for result in valid_results:
        if not result.get('actual_efforts') or not result.get('predicted_efforts'):
            print(f"Không đủ dữ liệu để trực quan hóa cho mô hình {result.get('model')}")
            return
    
    try:
        plt.figure(figsize=(20, 15))
        
        # Subplot 1: Actual vs Predicted
        plt.subplot(2, 2, 1)
        for result in valid_results:
            model_name = result['model']
            actual = result['actual_efforts']
            predicted = result['predicted_efforts']
            
            plt.scatter(actual, predicted, label=model_name, alpha=0.7)
        
        # Tìm giá trị lớn nhất để vẽ đường tham chiếu
        all_actual = [val for result in valid_results for val in result['actual_efforts']]
        all_predicted = [val for result in valid_results for val in result['predicted_efforts']]
        
        if all_actual and all_predicted:
            max_val = max(max(all_actual), max(all_predicted))
            # Đảm bảo max_val không quá lớn gây vấn đề hiển thị
            if max_val > 1000:
                # Lấy phần lớn của dữ liệu, bỏ qua các điểm ngoại lai
                actual_95 = np.percentile(all_actual, 95)
                predicted_95 = np.percentile(all_predicted, 95)
                max_val = max(actual_95, predicted_95) * 1.1
            
            plt.plot([0, max_val], [0, max_val], 'k--')
            plt.xlim(0, max_val)
            plt.ylim(0, max_val)
        
        plt.title('Actual vs Predicted Effort')
        plt.xlabel('Actual Effort (person-months)')
        plt.ylabel('Predicted Effort (person-months)')
        plt.legend()
        plt.grid(True)
        
        # Subplot 2: MMRE
        plt.subplot(2, 2, 2)
        models = [result['model'] for result in valid_results]
        mmre_values = [min(result['mmre'], 2.0) for result in valid_results]  # Giới hạn MMRE để hiển thị tốt hơn
        
        plt.bar(models, mmre_values)
        plt.title('Mean Magnitude of Relative Error (MMRE)')
        plt.xlabel('Model')
        plt.ylabel('MMRE (Lower is better)')
        plt.xticks(rotation=45)
        plt.grid(True)
        
        # Hiển thị giá trị thực
        for i, v in enumerate(mmre_values):
            plt.text(i, v + 0.05, f'{valid_results[i]["mmre"]:.2f}', 
                    ha='center', va='bottom', fontweight='bold')
        
        # Subplot 3: PRED(25)
        plt.subplot(2, 2, 3)
        pred_values = [result['pred_25'] for result in valid_results]
        
        plt.bar(models, pred_values)
        plt.title('PRED(25) - Percentage of predictions within 25% of actual')
        plt.xlabel('Model')
        plt.ylabel('PRED(25) (Higher is better)')
        plt.xticks(rotation=45)
        plt.ylim(0, 1.0)
        plt.grid(True)
        
        # Hiển thị giá trị thực
        for i, v in enumerate(pred_values):
            plt.text(i, v + 0.02, f'{v:.2f}', ha='center', va='bottom', fontweight='bold')
        
        # Subplot 4: RMSE
        plt.subplot(2, 2, 4)
        rmse_values = [min(result['rmse'], result['rmse'] * 2) for result in valid_results]  # Giới hạn RMSE để hiển thị tốt hơn
        
        plt.bar(models, rmse_values)
        plt.title('Root Mean Square Error (RMSE)')
        plt.xlabel('Model')
        plt.ylabel('RMSE (Lower is better)')
        plt.xticks(rotation=45)
        plt.grid(True)
        
        # Hiển thị giá trị thực
        for i, v in enumerate(rmse_values):
            plt.text(i, v + 0.05, f'{valid_results[i]["rmse"]:.2f}', 
                    ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.suptitle(title, fontsize=16)
        plt.subplots_adjust(top=0.92)
        
        # Lưu hình
        output_dir = PROJECT_ROOT / "comparison_results"
        if not output_dir.exists():
            output_dir.mkdir(parents=True)
        
        output_path = output_dir / "real_data_model_performance.png"
        plt.savefig(output_path)
        print(f"Hình ảnh phân tích hiệu suất đã được lưu tại: {output_path}")
        
    except Exception as e:
        print(f"Lỗi khi trực quan hóa kết quả: {e}")
    finally:
        plt.close()

def demo_with_real_data():
    """Demo sử dụng dữ liệu thực tế từ các bộ dữ liệu có sẵn"""
    print("=" * 50)
    print("ĐÁNH GIÁ MÔ HÌNH VỚI DỮ LIỆU THỰC TẾ")
    print("=" * 50)
    
    # Tải dữ liệu
    print("\nĐang tải dữ liệu...")
    cocomo_df = load_cocomo_dataset()
    fp_df = load_function_points_dataset()
    ucp_df = load_use_case_points_dataset()
    
    # Tiền xử lý dữ liệu
    print("\nĐang tiền xử lý dữ liệu...")
    cocomo_projects = preprocess_cocomo_data(cocomo_df)
    fp_projects = preprocess_fp_data(fp_df)
    ucp_projects = preprocess_ucp_data(ucp_df)
    
    # Thông tin về bộ dữ liệu
    print(f"\nSố lượng dự án COCOMO: {len(cocomo_projects) if cocomo_projects else 0}")
    print(f"Số lượng dự án Function Points: {len(fp_projects) if fp_projects else 0}")
    print(f"Số lượng dự án Use Case Points: {len(ucp_projects) if ucp_projects else 0}")
    
    # Khởi tạo các mô hình
    print("\nĐang khởi tạo các mô hình...")
    cocomo_model = COCOMOII()
    fp_model = FunctionPoints()
    ucp_model = UseCasePoints()
    
    # Đánh giá hiệu suất của từng mô hình
    print("\nĐang đánh giá hiệu suất các mô hình...")
    cocomo_eval = evaluate_model_performance(cocomo_model, cocomo_projects, "COCOMO II") if cocomo_projects else None
    fp_eval = evaluate_model_performance(fp_model, fp_projects, "Function Points") if fp_projects else None
    ucp_eval = evaluate_model_performance(ucp_model, ucp_projects, "Use Case Points") if ucp_projects else None
    
    # Trực quan hóa hiệu suất
    print("\nĐang trực quan hóa kết quả...")
    
    # Kiểm tra xem có kết quả hợp lệ nào không
    valid_evals = [eval_result for eval_result in [cocomo_eval, fp_eval, ucp_eval] if eval_result is not None]
    if valid_evals:
        try:
            visualize_model_performance(valid_evals)
        except Exception as e:
            print(f"Lỗi khi trực quan hóa kết quả: {e}")
    else:
        print("Không có kết quả đánh giá hợp lệ để trực quan hóa")
    
    # Demo tích hợp đa mô hình với dữ liệu thực tế
    print("\nDemo tích hợp đa mô hình với dữ liệu thực tế...")
    
    # Chọn một dự án từ mỗi bộ dữ liệu để minh họa
    example_project = {}
    
    # Thêm thông tin từ COCOMO nếu có
    if cocomo_projects and len(cocomo_projects) > 0:
        for key, value in cocomo_projects[0].items():
            if key != 'actual_effort':  # Không sử dụng actual_effort
                example_project[key] = value
        print("Đã thêm thông tin từ dữ liệu COCOMO vào dự án mẫu")
    
    # Thêm thông tin từ Function Points nếu có
    if fp_projects and len(fp_projects) > 0:
        for key, value in fp_projects[0].items():
            if key != 'actual_effort':  # Không sử dụng actual_effort
                example_project[key] = value
        print("Đã thêm thông tin từ dữ liệu Function Points vào dự án mẫu")
        
        # Add missing fields for FunctionPoints model
        # Đảm bảo có đủ các trường cần thiết cho mô hình Function Points
        if 'function_points' in example_project:
            if 'external_inputs' not in example_project:
                example_project['external_inputs'] = example_project['function_points'] * 0.3
            if 'external_outputs' not in example_project:
                example_project['external_outputs'] = example_project['function_points'] * 0.2
            if 'external_inquiries' not in example_project:
                example_project['external_inquiries'] = example_project['function_points'] * 0.2
            if 'internal_files' not in example_project:
                example_project['internal_files'] = example_project['function_points'] * 0.2
            if 'external_files' not in example_project:
                example_project['external_files'] = example_project['function_points'] * 0.1
            print("Đã thêm các trường cần thiết cho mô hình Function Points")
        
        # Map các trường từ dataset cụ thể cho FunctionPoints model
        fp_mapping = {
            'input': 'external_inputs',
            'output': 'external_outputs',
            'inquiry': 'external_inquiries',
            'file': 'internal_files',
            'interface': 'external_files'
        }
        
        for old_field, new_field in fp_mapping.items():
            if old_field in example_project and new_field not in example_project:
                example_project[new_field] = example_project[old_field]
    
    # Kiểm tra xem có đủ dữ liệu cho ít nhất một mô hình không
    print("\nThông tin dự án mẫu:")
    for key, value in example_project.items():
        print(f"- {key}: {value}")
    
    # Tạo danh sách mô hình có dữ liệu
    available_models = []
    if cocomo_projects and len(cocomo_projects) > 0:
        available_models.append(cocomo_model)
    if fp_projects and len(fp_projects) > 0:
        available_models.append(fp_model)
    if ucp_projects and len(ucp_projects) > 0:
        available_models.append(ucp_model)
    
    if not available_models:
        print("\nKhông có đủ dữ liệu để demo tích hợp đa mô hình")
    else:
        # Khởi tạo multi-model integration với các mô hình có sẵn
        multi_model = MultiModelIntegration(models=available_models)
        
        # Ước lượng với tích hợp đa mô hình
        try:
            print("\nỨng dụng tích hợp đa mô hình với dữ liệu thực tế:")
            result = multi_model.estimate(example_project, method="weighted_average")
            
            print(f"\nKết quả ước lượng:")
            print(f"Nỗ lực: {result['effort_pm']:.2f} người-tháng")
            print(f"Thời gian: {result['time_months']:.2f} tháng")
            print(f"Kích thước team: {result['team_size']:.2f} người")
            print(f"Độ tin cậy: {result['confidence']:.2f}")
            
            # Hiển thị đóng góp của từng mô hình
            print("\nĐóng góp của từng mô hình:")
            for contribution in result['model_contributions']:
                print(f"- {contribution['model']}: {contribution['effort_pm']:.2f} người-tháng (trọng số: {contribution['weight']:.2f})")
        
        except Exception as e:
            print(f"Lỗi khi ước lượng với tích hợp đa mô hình: {e}")
    
    # Demo Agile COCOMO với dự án thực tế
    print("\n" + "=" * 50)
    print("DEMO AGILE COCOMO VỚI DỮ LIỆU THỰC TẾ")
    print("=" * 50)
    
    # Khởi tạo Agile COCOMO
    agile_cocomo = AgileCOCOMO()
    
    # Chuẩn bị dữ liệu dự án
    if cocomo_projects and len(cocomo_projects) > 0:
        agile_project = cocomo_projects[0].copy()
        
        # Đảm bảo size > 0
        if 'size' in agile_project and agile_project['size'] <= 0:
            agile_project['size'] = 10  # Default value
        
        # Thêm thông tin Agile
        agile_project.update({
            'sprint_length_weeks': 2,
            'team_size': 5,
            'team_velocity': 25,  # Default velocity
            'velocity_data': [
                {'sprint': 1, 'velocity': 25, 'effort_hours': 160},
                {'sprint': 2, 'velocity': 28, 'effort_hours': 170}
            ]
        })
        
        try:
            # Ước lượng với Agile COCOMO
            print("\nỨoc lượng với Agile COCOMO:")
            result = agile_cocomo.estimate_effort(agile_project)
            
            print(f"\nKết quả ước lượng:")
            print(f"Nỗ lực: {result['effort_pm']:.2f} người-tháng")
            print(f"Thời gian: {result['time_months']:.2f} tháng")
            print(f"Kích thước team: {result['team_size']:.2f} người")
            print(f"Độ tin cậy: {result['confidence']:.2f}")
            
            # Hiển thị thông tin Agile
            print("\nThông tin Agile:")
            print(f"Số sprint còn lại: {result['sprints_remaining']:.1f}")
            # Handle both naming conventions for backward compatibility
            agile_adjustment = result.get('agile_adjustment', result.get('agile_adjustment_factor', 0))
            print(f"Hệ số điều chỉnh Agile: {agile_adjustment:.2f}")
            
            # Hiển thị dự báo sprint
            if result.get('sprint_forecast'):
                print("\nDự báo các sprint:")
                for sprint in result['sprint_forecast'][:3]:  # Chỉ hiển thị 3 sprint đầu
                    print(f"Sprint {sprint['sprint']}: {sprint['story_points']:.1f} SP, {sprint['effort_hours']:.1f} giờ ({sprint['effort_pm']:.2f} PM)")
        
        except Exception as e:
            print(f"Lỗi khi ước lượng với Agile COCOMO: {e}")
    else:
        print("Không có dữ liệu COCOMO để demo Agile COCOMO")
    
    print("\n" + "=" * 50)
    print("DEMO HOÀN THÀNH")
    print("=" * 50)

if __name__ == "__main__":
    demo_with_real_data()
