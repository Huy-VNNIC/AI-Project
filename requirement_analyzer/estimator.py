"""
Module kết nối các phân tích yêu cầu với mô hình ước lượng nỗ lực
"""

import os
import sys
import pickle
import joblib
import numpy as np
import pandas as pd
import json
from pathlib import Path

# Thêm thư mục gốc vào sys.path để import các module khác
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import các module cần thiết
try:
    from multi_model_integration.estimation_models import COCOMOII, FunctionPoints, UseCasePoints
    from multi_model_integration.multi_model_integration import MultiModelIntegration
except ImportError:
    print("Warning: multi_model_integration module not found. Some features may not be available.")

class EffortEstimator:
    """
    Sử dụng các tham số trích xuất từ tài liệu yêu cầu để ước lượng nỗ lực
    """
    
    def __init__(self, model_path=None):
        """
        Khởi tạo EffortEstimator
        
        Args:
            model_path (str, optional): Đường dẫn đến thư mục chứa các mô hình đã train
        """
        self.model_path = model_path or os.path.join(PROJECT_ROOT, "models")
        
        # Khởi tạo các mô hình
        self.models = {}
        self.ml_models = {}
        
        # Khởi tạo các mô hình cơ bản
        self._init_base_models()
        
        # Tải các mô hình ML đã train
        self._load_ml_models()
        
        # Khởi tạo tích hợp đa mô hình
        self.multi_model = MultiModelIntegration(models=list(self.models.values()))
    
    def _init_base_models(self):
        """Khởi tạo các mô hình cơ bản"""
        # Khởi tạo COCOMO II
        self.models['cocomo'] = COCOMOII()
        
        # Khởi tạo Function Points
        self.models['function_points'] = FunctionPoints()
        
        # Khởi tạo Use Case Points
        self.models['use_case_points'] = UseCasePoints()
    
    def _load_ml_models(self):
        """Tải các mô hình ML đã train"""
        if not os.path.exists(self.model_path):
            print(f"Warning: Model path {self.model_path} not found")
            return
        
        # Tìm kiếm các mô hình trong thư mục cocomo_ii_extended
        model_dir = os.path.join(self.model_path, "cocomo_ii_extended")
        if not os.path.exists(model_dir):
            print(f"Warning: COCOMO II extended model directory not found at {model_dir}")
            return
        
        # Tải cấu hình
        config_path = os.path.join(model_dir, "config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                self.model_config = config
                model_names = config.get('models', [])
        else:
            print(f"Warning: Model config not found at {config_path}")
            # Tìm tất cả các file .pkl trong thư mục
            model_names = [os.path.splitext(f)[0] for f in os.listdir(model_dir) 
                          if f.endswith('.pkl') and not f == 'preprocessor.pkl']
        
        # Tải preprocessor nếu có
        preprocessor_path = os.path.join(model_dir, "preprocessor.pkl")
        if os.path.exists(preprocessor_path):
            try:
                self.preprocessor = joblib.load(preprocessor_path)
            except Exception as e:
                print(f"Error loading preprocessor: {e}")
        
        # Tải từng mô hình
        for model_name in model_names:
            model_path = os.path.join(model_dir, f"{model_name}.pkl")
            if os.path.exists(model_path):
                try:
                    model = joblib.load(model_path)
                    self.ml_models[model_name] = model
                    print(f"Loaded ML model: {model_name}")
                except Exception as e:
                    print(f"Error loading model {model_name}: {e}")
        
        # Tải thông tin về đặc trưng
        feature_info_path = os.path.join(model_dir, "feature_info.json")
        if os.path.exists(feature_info_path):
            try:
                with open(feature_info_path, 'r') as f:
                    self.feature_info = json.load(f)
            except Exception as e:
                print(f"Error loading feature info: {e}")

    def estimate_from_parameters(self, params, model_name='cocomo'):
        """
        Ước lượng nỗ lực dựa trên các tham số đã trích xuất
        
        Args:
            params (dict): Các tham số đầu vào cho mô hình
            model_name (str): Tên mô hình cần sử dụng
            
        Returns:
            dict: Kết quả ước lượng
        """
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not available")
        
        model = self.models[model_name]
        result = model.estimate_effort(params)
        
        return result
    
    def estimate_from_ml_model(self, features, model_name="Random_Forest"):
        """
        Ước lượng nỗ lực sử dụng mô hình ML đã train
        
        Args:
            features (dict): Các đặc trưng đầu vào cho mô hình
            model_name (str): Tên mô hình ML cần sử dụng
            
        Returns:
            float: Nỗ lực ước lượng (người-tháng)
        """
        if model_name not in self.ml_models:
            available_models = list(self.ml_models.keys())
            if not available_models:
                raise ValueError("No ML models available")
            model_name = available_models[0]
            print(f"Warning: Requested model not found. Using {model_name} instead")
        
        model = self.ml_models[model_name]
        
        # Xác định các đặc trưng cần thiết
        required_features = []
        if hasattr(model, 'feature_names_in_'):
            required_features = model.feature_names_in_
        elif self.model_config and 'feature_names' in self.model_config:
            required_features = self.model_config['feature_names']
        else:
            # Giả định một tập đặc trưng phổ biến nếu không tìm thấy thông tin
            required_features = [
                'developers', 'size', 'team_exp', 'manager_exp', 'adjustment',
                'transactions', 'points_non_adjust', 'time_months', 'entities'
            ]
        
        # Chuẩn bị dữ liệu đầu vào
        X = np.zeros((1, len(required_features)))
        for i, feature in enumerate(required_features):
            X[0, i] = features.get(feature, 0)
        
        # Dự đoán: Thử áp dụng preprocessor, nếu có lỗi thì bỏ qua và dùng dữ liệu gốc
        try:
            # Thử áp dụng preprocessor
            if self.preprocessor:
                try:
                    X_transformed = self.preprocessor.transform(X)
                    effort = model.predict(X_transformed)[0]
                except Exception as e:
                    print(f"Warning: Error applying preprocessor: {e}")
                    # Nếu lỗi, thử dự đoán trực tiếp với dữ liệu gốc
                    effort = model.predict(X)[0]
            else:
                effort = model.predict(X)[0]
                
            # Xử lý trường hợp logarithmic transform
            if hasattr(self, 'model_config') and self.model_config.get('log_transform', False):
                effort = np.exp(effort)
                
            return float(effort)
        except Exception as e:
            print(f"Error during prediction: {e}")
            # Trả về một ước lượng đơn giản dựa trên COCOMO cơ bản nếu dự đoán thất bại
            size = features.get('size', 5)
            return 2.4 * (size ** 1.05)

    def integrated_estimate(self, all_params, method="weighted_average"):
        """
        Ước lượng nỗ lực sử dụng tích hợp đa mô hình
        
        Args:
            all_params (dict): Các tham số cho tất cả các mô hình
            method (str): Phương pháp tích hợp
            
        Returns:
            dict: Kết quả ước lượng tích hợp
        """
        # Chuẩn bị dữ liệu cho tất cả các mô hình
        project_data = {}
        
        # Thêm các tham số COCOMO
        for key, value in all_params['cocomo'].items():
            project_data[key] = value
        
        # Thêm các tham số Function Points
        for key, value in all_params['function_points'].items():
            project_data[key] = value
        
        # Thêm các tham số Use Case Points
        for key, value in all_params['use_case_points'].items():
            project_data[key] = value
        
        # Thêm các đặc trưng ML
        if 'ml_features' in all_params:
            for key, value in all_params['ml_features'].items():
                project_data[key] = value
                
        # Thêm các thông tin từ features để giúp chuẩn đoán tốt hơn
        if 'features' in all_params:
            project_data['has_security_requirements'] = all_params['features'].get('has_security_requirements', False)
            project_data['has_performance_requirements'] = all_params['features'].get('has_performance_requirements', False)
            project_data['has_interface_requirements'] = all_params['features'].get('has_interface_requirements', False)
            project_data['has_data_requirements'] = all_params['features'].get('has_data_requirements', False)
            project_data['complexity'] = all_params['features'].get('complexity', 1.0)
            project_data['text_complexity'] = all_params['features'].get('text_complexity', 1.0)
            
            # Thêm thông tin về công nghệ
            if 'technologies' in all_params['features']:
                project_data['technologies'] = all_params['features']['technologies']
                project_data['num_technologies'] = all_params['features'].get('num_technologies', 0)
        
        # Ước lượng từ các mô hình rule-based
        estimates = {}
        for name, model in self.models.items():
            try:
                result = model.estimate(project_data)
                estimates[name] = result.get('effort_pm', 0)
            except Exception as e:
                print(f"Error estimating with {name}: {e}")
        
        # Ước lượng từ các mô hình ML
        for name, model in self.ml_models.items():
            try:
                ml_effort = self.estimate_from_ml_model(project_data, name)
                estimates[f"ml_{name}"] = ml_effort
            except Exception as e:
                print(f"Error estimating with ML model {name}: {e}")
        
        # Tích hợp các ước lượng
        integrated_effort = self.multi_model.estimate(project_data, method=method)
        
        # Tính toán thời gian và kích thước nhóm
        duration = self._estimate_duration(integrated_effort.get('effort_pm', 0), project_data)
        team_size = self._estimate_team_size(integrated_effort.get('effort_pm', 0), duration)
        
        # Tạo kết quả cuối cùng
        confidence_level = self._calculate_confidence_level(estimates)
        result = {
            'total_effort': round(integrated_effort.get('effort_pm', 0), 2),
            'duration': round(duration, 2),
            'team_size': round(team_size, 2),
            'confidence_level': confidence_level,
            'model_estimates': {k: round(v, 2) for k, v in estimates.items()}
        }
        
        return result
    
    def _estimate_duration(self, effort, project_data):
        """Ước lượng thời gian dự án từ nỗ lực"""
        # Sử dụng công thức COCOMO II cho thời gian
        size = project_data.get('size', 5)  # KLOC
        exponent = 0.33 + 0.2 * (effort - 2.5) / 100  # Điều chỉnh dựa trên nỗ lực
        exponent = max(0.2, min(0.4, exponent))  # Giới hạn exponent
        return 3.0 * (effort ** exponent)
    
    def _estimate_team_size(self, effort, duration):
        """Ước lượng kích thước nhóm từ nỗ lực và thời gian"""
        if duration <= 0:
            return 1
        team_size = effort / duration
        return max(1, team_size)  # Tối thiểu 1 người
    
    def _calculate_confidence_level(self, estimates):
        """Tính toán mức độ tin cậy dựa trên sự nhất quán của các ước lượng"""
        if not estimates:
            return "Low"
        
        values = list(estimates.values())
        if len(values) == 1:
            return "Medium"  # Chỉ một mô hình
        
        # Tính biến thiên tương đối
        mean = sum(values) / len(values)
        if mean == 0:
            return "Low"  # Tránh chia cho 0
        
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        relative_std = (variance ** 0.5) / mean
        
        if relative_std < 0.2:
            return "High"  # Các mô hình rất nhất quán
        elif relative_std < 0.4:
            return "Medium"  # Nhất quán vừa phải
        else:
            return "Low"  # Không nhất quán
    
    def estimate_from_requirements(self, text, method="weighted_average"):
        """
        Ước lượng nỗ lực từ văn bản yêu cầu
        
        Args:
            text (str): Văn bản yêu cầu
            method (str): Phương pháp tích hợp
            
        Returns:
            dict: Kết quả ước lượng và phân tích
        """
        from .analyzer import RequirementAnalyzer
        
        # Phân tích yêu cầu
        analyzer = RequirementAnalyzer()
        all_params = analyzer.analyze_requirements_document(text)
        
        # Ước lượng nỗ lực
        estimation = self.integrated_estimate(all_params, method)
        
        # Kết hợp kết quả
        result = {
            "estimation": estimation,
            "analysis": all_params
        }
        
        return result
