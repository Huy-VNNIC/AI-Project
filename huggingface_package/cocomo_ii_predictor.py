#!/usr/bin/env python3
"""
COCOMO II Predictor - Utility module for software effort estimation

This module provides functions to estimate software development effort, duration, 
and team size based on different size metrics (LOC, Function Points, Use Case Points).
"""

import os
import pandas as pd
import numpy as np
import joblib
import json

class CocomoIIPredictor:
    """
    Mô hình COCOMO II mở rộng kết hợp dự đoán dựa trên LOC, FP, và UCP
    """
    def __init__(self, model_path=None):
        self.models = {}
        self.preprocessor = None
        self.log_transform = True
        
        if model_path:
            self.load(model_path)
    
    def fit(self, models, preprocessor, log_transform=True):
        """
        Lưu các mô hình đã huấn luyện
        
        Args:
            models: Dictionary chứa các pipeline đã huấn luyện
            preprocessor: Bộ tiền xử lý dữ liệu
            log_transform: Áp dụng biến đổi logarithmic hay không
        """
        self.models = models
        self.preprocessor = preprocessor
        self.log_transform = log_transform
        return self
    
    def predict_effort(self, input_data, model_name='Random Forest (Tuned)'):
        """
        Dự đoán effort dựa trên đầu vào
        
        Args:
            input_data: DataFrame chứa dữ liệu đầu vào
            model_name: Tên mô hình để sử dụng
            
        Returns:
            Giá trị effort dự đoán (người-tháng)
        """
        if model_name not in self.models:
            raise ValueError(f"Mô hình '{model_name}' không tồn tại!")
        
        model = self.models[model_name]
        
        # Dự đoán
        effort_pred = model.predict(input_data)
        
        # Chuyển đổi ngược nếu đã áp dụng biến đổi logarithmic
        if self.log_transform:
            effort_pred = np.expm1(effort_pred)
        
        return effort_pred
    
    def predict_schedule(self, effort):
        """
        Dự đoán lịch trình (thời gian) dựa trên effort
        Sử dụng công thức COCOMO II: TDEV = 3.67 × (PM)^0.28
        
        Args:
            effort: Effort dự đoán (người-tháng)
            
        Returns:
            Thời gian dự kiến (tháng)
        """
        return 3.67 * (effort ** 0.28)
    
    def predict_team_size(self, effort, time):
        """
        Dự đoán kích thước đội ngũ dựa trên effort và thời gian
        
        Args:
            effort: Effort dự đoán (người-tháng)
            time: Thời gian dự kiến (tháng)
            
        Returns:
            Số lượng nhà phát triển
        """
        return np.ceil(effort / time)
    
    def predict_all(self, input_data, model_name='Random Forest (Tuned)'):
        """
        Dự đoán effort, thời gian và kích thước đội ngũ
        
        Args:
            input_data: DataFrame chứa dữ liệu đầu vào
            model_name: Tên mô hình để sử dụng
            
        Returns:
            Dictionary chứa các kết quả dự đoán
        """
        # Dự đoán effort
        effort = self.predict_effort(input_data, model_name)
        
        # Dự đoán lịch trình
        schedule = self.predict_schedule(effort)
        
        # Dự đoán kích thước đội ngũ
        team_size = self.predict_team_size(effort, schedule)
        
        return {
            'effort_pm': effort,
            'time_months': schedule,
            'developers': team_size
        }
    
    def save(self, model_path):
        """
        Lưu mô hình vào file
        
        Args:
            model_path: Đường dẫn thư mục để lưu mô hình
        """
        if not os.path.exists(model_path):
            os.makedirs(model_path)
        
        # Lưu các pipeline
        for name, pipeline in self.models.items():
            file_path = os.path.join(model_path, f"{name.replace(' ', '_')}.pkl")
            joblib.dump(pipeline, file_path)
            print(f"Đã lưu mô hình {name} vào {file_path}")
        
        # Lưu preprocessor
        preprocessor_path = os.path.join(model_path, "preprocessor.pkl")
        joblib.dump(self.preprocessor, preprocessor_path)
        print(f"Đã lưu bộ tiền xử lý vào {preprocessor_path}")
        
        # Lưu cấu hình
        config = {
            'log_transform': self.log_transform,
            'models': list(self.models.keys()),
            'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        config_path = os.path.join(model_path, "config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"Đã lưu cấu hình vào {config_path}")
    
    def load(self, model_path):
        """
        Tải mô hình từ file
        
        Args:
            model_path: Đường dẫn thư mục chứa mô hình đã lưu
        """
        # Tải cấu hình
        config_path = os.path.join(model_path, "config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            self.log_transform = config['log_transform']
            model_names = config['models']
            
            # Tải preprocessor
            preprocessor_path = os.path.join(model_path, "preprocessor.pkl")
            if os.path.exists(preprocessor_path):
                self.preprocessor = joblib.load(preprocessor_path)
                print(f"Đã tải bộ tiền xử lý từ {preprocessor_path}")
            
            # Tải các mô hình
            for name in model_names:
                file_path = os.path.join(model_path, f"{name.replace(' ', '_')}.pkl")
                if os.path.exists(file_path):
                    self.models[name] = joblib.load(file_path)
                    print(f"Đã tải mô hình {name} từ {file_path}")
                else:
                    print(f"Không tìm thấy mô hình {name} tại {file_path}")
            
            print(f"Đã tải {len(self.models)} mô hình")
        else:
            print(f"Không tìm thấy file cấu hình tại {config_path}")


def cocomo_ii_estimate(size, size_type='kloc', model_path=None, model_name='Random Forest (Tuned)'):
    """
    Ước lượng effort, thời gian và kích thước đội ngũ dựa trên kích thước
    
    Args:
        size: Kích thước dự án (KLOC, FP hoặc UCP)
        size_type: Loại kích thước ('kloc', 'fp', 'ucp')
        model_path: Đường dẫn đến mô hình đã lưu
        model_name: Tên mô hình để sử dụng
        
    Returns:
        Dictionary chứa các kết quả dự đoán
    """
    if model_path is None:
        # Default path to models
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, 'models', 'cocomo_ii_extended')
    
    # Tải mô hình
    cocomo_predictor = CocomoIIPredictor(model_path)
    
    # Tạo dữ liệu đầu vào
    input_data = pd.DataFrame({
        'schema': [size_type.upper()],
        'size': [size]
    })
    
    # Thêm các cột khác tùy theo loại kích thước
    if size_type == 'kloc':
        input_data['kloc'] = size
        input_data['fp'] = np.nan
        input_data['ucp'] = np.nan
    elif size_type == 'fp':
        input_data['kloc'] = np.nan
        input_data['fp'] = size
        input_data['ucp'] = np.nan
    elif size_type == 'ucp':
        input_data['kloc'] = np.nan
        input_data['fp'] = np.nan
        input_data['ucp'] = size
    else:
        raise ValueError("size_type phải là 'kloc', 'fp', hoặc 'ucp'")
    
    # Dự đoán
    return cocomo_predictor.predict_all(input_data, model_name)


def display_cocomo_ii_results(size, size_type='kloc', model_name='Random Forest (Tuned)'):
    """
    Hiển thị kết quả ước lượng COCOMO II
    
    Args:
        size: Kích thước dự án (KLOC, FP hoặc UCP)
        size_type: Loại kích thước ('kloc', 'fp', 'ucp')
        model_name: Tên mô hình để sử dụng
    """
    try:
        # Thực hiện ước lượng
        results = cocomo_ii_estimate(size, size_type, model_name=model_name)
        
        # Hiển thị kết quả
        print(f"\n--- COCOMO II Estimation Results ---")
        print(f"Input: {size} {size_type.upper()}")
        print(f"Model: {model_name}")
        print("\nResults:")
        print(f"  - Effort: {results['effort_pm'][0]:.2f} person-months")
        print(f"  - Duration: {results['time_months'][0]:.2f} months")
        print(f"  - Team Size: {int(results['developers'][0])} developers")
        
        # Hiển thị thông báo về chi phí (nếu cần)
        rate_per_month = 5000  # Giả định chi phí trung bình mỗi người/tháng
        cost = results['effort_pm'][0] * rate_per_month
        print(f"\nEstimated Cost (at ${rate_per_month}/person-month): ${cost:.2f}")
        
        return results
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


if __name__ == "__main__":
    """
    Interactive command-line tool for COCOMO II estimation
    """
    print("\n=== COCOMO II Extended Estimation Tool ===\n")
    
    # Get size type
    print("Select size metric:")
    print("1. KLOC (Kilo Lines of Code)")
    print("2. FP (Function Points)")
    print("3. UCP (Use Case Points)")
    choice = input("Enter your choice (1-3): ")
    
    size_types = {
        '1': 'kloc',
        '2': 'fp',
        '3': 'ucp'
    }
    
    size_type = size_types.get(choice, 'kloc')
    
    # Get size value
    size = float(input(f"\nEnter project size ({size_type.upper()}): "))
    
    # Get model
    print("\nSelect prediction model:")
    print("1. Linear Regression")
    print("2. Decision Tree")
    print("3. Random Forest")
    print("4. Decision Tree (Tuned)")
    print("5. Random Forest (Tuned) [Default]")
    model_choice = input("Enter your choice (1-5): ")
    
    models = {
        '1': 'Linear Regression',
        '2': 'Decision Tree',
        '3': 'Random Forest',
        '4': 'Decision Tree (Tuned)',
        '5': 'Random Forest (Tuned)'
    }
    
    model_name = models.get(model_choice, 'Random Forest (Tuned)')
    
    # Display results
    display_cocomo_ii_results(size, size_type, model_name)
