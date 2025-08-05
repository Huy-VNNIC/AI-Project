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
        # Các đặc trưng cốt lõi cần thiết cho một ước tính hợp lý
        core_features = ['size', 'complexity']
        for feature in core_features:
            if feature not in features or not isinstance(features[feature], (int, float)) or np.isnan(features[feature]):
                print(f"Warning: Missing or invalid essential feature '{feature}'. Setting default.")
                if feature == 'size':
                    features[feature] = 5.0  # Default size: 5 KLOC
                elif feature == 'complexity':
                    features[feature] = 1.0  # Default complexity: Medium
        try:
            if model_name not in self.ml_models:
                available_models = list(self.ml_models.keys())
                if not available_models:
                    raise ValueError("No ML models available")
                model_name = available_models[0]
                print(f"Warning: Requested model not found. Using {model_name} instead")
            
            model = self.ml_models[model_name]
            
            # Đảm bảo các đặc trưng cần thiết dựa trên feature_info.json
            required_features = []
            if hasattr(self, 'feature_info'):
                required_features = self.feature_info.get('numeric_features', []) + self.feature_info.get('categorical_features', [])
            
            # Nếu không có thông tin đặc trưng từ file, sử dụng các đặc trưng được biết là cần thiết
            if not required_features:
                required_features = [
                    'size', 'developers', 'team_exp', 'manager_exp', 'complexity', 'reliability',
                    'num_requirements', 'functional_reqs', 'non_functional_reqs', 'entities',
                    'transactions', 'time_months', 'points_non_adjust', 'schema'
                ]
            
            # Chuẩn bị đặc trưng đầu vào
            input_features = {}
            
            # Đặt giá trị mặc định cho các đặc trưng bắt buộc
            default_values = {
                'size': 5.0,                   # Mặc định 5 KLOC
                'developers': 3,               # 3 người
                'team_exp': 3,                 # Trung bình
                'manager_exp': 3,              # Trung bình
                'complexity': 1.0,             # Trung bình
                'reliability': 1.0,            # Trung bình
                'num_requirements': 10,        # 10 yêu cầu
                'functional_reqs': 6,          # 6 yêu cầu chức năng
                'non_functional_reqs': 4,      # 4 yêu cầu phi chức năng
                'entities': 5,                 # 5 thực thể dữ liệu
                'transactions': 10,            # 10 giao dịch
                'time_months': 6.0,            # 6 tháng
                'points_non_adjust': 100,      # 100 điểm chức năng chưa điều chỉnh
                'adjustment': 1.0,             # Hệ số điều chỉnh
                'kloc_per_dev': 1.67,          # 5 KLOC / 3 devs
                'kloc_per_month': 0.83,        # 5 KLOC / 6 tháng
                'fp_per_month': 16.67,         # 100 FP / 6 tháng
                'fp_per_dev': 33.33,           # 100 FP / 3 devs
                'schema': 1,                   # Mặc định là FP (0: LOC, 1: FP, 2: UCP)
                'has_security_requirements': 0, # Boolean chuyển thành 0/1
                'has_performance_requirements': 0,
                'has_interface_requirements': 0,
                'has_data_requirements': 0,
                'text_complexity': 1.5,        # Độ phức tạp văn bản mặc định
                'num_technologies': 2          # Số công nghệ mặc định
            }
            
            # Chuyển đổi boolean thành số (0/1)
            bool_features = ['has_security_requirements', 'has_performance_requirements', 
                           'has_interface_requirements', 'has_data_requirements']
            for feature in bool_features:
                if feature in features:
                    if isinstance(features[feature], bool):
                        features[feature] = 1 if features[feature] else 0
            
            # Điền các giá trị từ đặc trưng đã cung cấp
            for feature in required_features:
                if feature in features:
                    value = features[feature]
                    # Kiểm tra và đảm bảo giá trị hợp lệ
                    if isinstance(value, (int, float)) and not np.isnan(value) and not np.isinf(value):
                        input_features[feature] = value
                    else:
                        input_features[feature] = default_values.get(feature, 0.0)
                else:
                    input_features[feature] = default_values.get(feature, 0.0)
            
            # Tính toán các đặc trưng dẫn xuất
            # 1. Các đặc trưng liên quan đến kích thước và đội ngũ
            size = input_features.get('size', default_values['size'])
            developers = max(1, input_features.get('developers', default_values['developers']))  # Tối thiểu 1 developer
            time_months = max(1, input_features.get('time_months', default_values['time_months']))  # Tối thiểu 1 tháng
            
            # KLOC per developer
            input_features['kloc_per_dev'] = size / developers
            
            # KLOC per month
            input_features['kloc_per_month'] = size / time_months
            
            # 2. Các đặc trưng liên quan đến điểm chức năng
            points = input_features.get('points_non_adjust', default_values['points_non_adjust'])
            
            # Function points per month
            input_features['fp_per_month'] = points / time_months
            
            # Function points per developer
            input_features['fp_per_dev'] = points / developers
            
            # 3. Các đặc trưng dẫn xuất khác
            # Tỷ lệ yêu cầu chức năng/phi chức năng
            func_reqs = input_features.get('functional_reqs', default_values['functional_reqs'])
            non_func_reqs = input_features.get('non_functional_reqs', default_values['non_functional_reqs'])
            if 'func_nonfunc_ratio' in required_features:
                input_features['func_nonfunc_ratio'] = func_reqs / max(1, non_func_reqs)
                
            # Độ phức tạp * kích thước (đo lường độ phức tạp tổng thể)
            if 'complexity_size' in required_features:
                input_features['complexity_size'] = input_features.get('complexity', 1.0) * size
                
            # Đảm bảo các trường boolean được chuyển thành số
            for bool_feature in bool_features:
                if bool_feature in input_features and isinstance(input_features[bool_feature], bool):
                    input_features[bool_feature] = 1 if input_features[bool_feature] else 0
            
            # Đảm bảo rằng tất cả các giá trị đều hợp lệ
            for key, value in input_features.items():
                if not isinstance(value, (int, float)) or np.isnan(value) or np.isinf(value):
                    input_features[key] = default_values.get(key, 0.0)
            
            # Tạo danh sách đặc trưng theo thứ tự phù hợp với mô hình
            # Kiểm tra xem mô hình cần bao nhiêu đặc trưng
            expected_features_count = 14  # Mặc định 14 đặc trưng, dựa theo thông báo lỗi
            if hasattr(model, 'n_features_in_'):
                expected_features_count = model.n_features_in_
            elif hasattr(model, 'feature_names_in_'):
                expected_features_count = len(model.feature_names_in_)
            
            # Danh sách các đặc trưng cốt lõi phổ biến
            core_features = [
                'size', 'developers', 'team_exp', 'manager_exp', 'complexity', 'reliability',
                'num_requirements', 'functional_reqs', 'non_functional_reqs', 'entities',
                'transactions', 'time_months', 'points_non_adjust', 'schema'
            ]
            
            # Đặc trưng bổ sung cho các mô hình với nhiều đặc trưng hơn
            extended_features = [
                'adjustment', 'kloc_per_dev', 'kloc_per_month', 'fp_per_month', 'fp_per_dev', 
                'has_security_requirements', 'has_performance_requirements', 'has_interface_requirements', 
                'has_data_requirements', 'text_complexity', 'num_technologies'
            ]
                
            if hasattr(self, 'feature_info'):
                # Sử dụng thứ tự từ feature_info.json nếu có
                ordered_features = self.feature_info.get('numeric_features', []) + self.feature_info.get('categorical_features', [])
                
                # Đảm bảo độ dài phù hợp với số đặc trưng mô hình cần
                if len(ordered_features) < expected_features_count:
                    # Thiếu đặc trưng, bổ sung thêm từ core_features và extended_features
                    all_possible_features = core_features + extended_features
                    missing_features = [f for f in all_possible_features if f not in ordered_features]
                    ordered_features.extend(missing_features[:expected_features_count - len(ordered_features)])
                elif len(ordered_features) > expected_features_count:
                    # Thừa đặc trưng, cắt bớt
                    ordered_features = ordered_features[:expected_features_count]
            else:
                # Nếu không có feature_info, xây dựng danh sách dựa trên số lượng đặc trưng cần thiết
                if expected_features_count <= len(core_features):
                    ordered_features = core_features[:expected_features_count]
                else:
                    ordered_features = core_features + extended_features[:expected_features_count - len(core_features)]
            
            # Tạo mảng numpy với các đặc trưng đã được sắp xếp
            X = np.array([[input_features.get(feature, default_values.get(feature, 0.0)) for feature in ordered_features]])
            
            # Kiểm tra số lượng đặc trưng
            expected_features = getattr(model, 'n_features_in_', None)
            if expected_features is None and hasattr(model, 'feature_names_in_'):
                expected_features = len(model.feature_names_in_)
                
            if expected_features is not None and X.shape[1] != expected_features:
                print(f"Warning: Model expects {expected_features} features, got {X.shape[1]}. Adjusting...")
                # Nếu thiếu đặc trưng, thêm các đặc trưng với giá trị mặc định
                if X.shape[1] < expected_features:
                    # Tạo một mảng đầy đủ với giá trị mặc định và điền giá trị thực tế vào
                    full_X = np.ones((1, expected_features)) * 0.5  # Giá trị mặc định tốt hơn là 0.5
                    full_X[:, :X.shape[1]] = X  # Điền giá trị thực tế vào vị trí tương ứng
                    X = full_X
                # Nếu thừa đặc trưng, cắt bớt
                else:
                    X = X[:, :expected_features]
            
            # Áp dụng preprocessor nếu có
            try:
                if hasattr(self, 'preprocessor'):
                    try:
                        # Kiểm tra xem preprocessor có phù hợp với đặc trưng đầu vào không
                        n_features_expected_by_preprocessor = None
                        if hasattr(self.preprocessor, 'n_features_in_'):
                            n_features_expected_by_preprocessor = self.preprocessor.n_features_in_
                        elif hasattr(self.preprocessor, 'feature_names_in_'):
                            n_features_expected_by_preprocessor = len(self.preprocessor.feature_names_in_)
                        
                        # Điều chỉnh số lượng đặc trưng nếu cần
                        if n_features_expected_by_preprocessor is not None and X.shape[1] != n_features_expected_by_preprocessor:
                            print(f"Preprocessor expects {n_features_expected_by_preprocessor} features, got {X.shape[1]}. Adjusting for preprocessor...")
                            if X.shape[1] < n_features_expected_by_preprocessor:
                                # Nếu thiếu đặc trưng, thêm các đặc trưng với giá trị mặc định
                                prep_X = np.ones((1, n_features_expected_by_preprocessor)) * 0.5
                                prep_X[:, :X.shape[1]] = X
                                X_for_preprocessor = prep_X
                            else:
                                # Nếu thừa đặc trưng, cắt bớt
                                X_for_preprocessor = X[:, :n_features_expected_by_preprocessor]
                        else:
                            X_for_preprocessor = X
                        
                        # Áp dụng preprocessor
                        X_transformed = self.preprocessor.transform(X_for_preprocessor)
                        effort = model.predict(X_transformed)[0]
                    except Exception as e:
                        print(f"Error applying preprocessor: {e}")
                        # Nếu preprocessor thất bại, thử dự đoán trực tiếp với đặc trưng gốc
                        effort = model.predict(X)[0]
                else:
                    effort = model.predict(X)[0]
            except Exception as e:
                print(f"Error during prediction: {e}")
                # Tính toán dự đoán dự phòng dựa trên kích thước và độ phức tạp
                size = features.get('size', 5.0)
                complexity_factor = features.get('complexity', 1.0)
                # Công thức dự phòng thông minh hơn
                effort = size * (2.0 + complexity_factor * 0.5)
            
            # Xử lý trường hợp logarithmic transform
            if hasattr(self, 'model_config') and self.model_config.get('log_transform', False):
                try:
                    effort = np.exp(effort)
                except:
                    pass
            
            # Đảm bảo kết quả hợp lý
            if effort <= 0 or np.isnan(effort) or np.isinf(effort):
                size = features.get('size', 5.0)
                effort = size * 2.5  # Ước tính thô: 2.5 PM/KLOC
            
            return float(effort)
            
        except Exception as e:
            print(f"Error estimating with ML model: {e}")
            size = features.get('size', 5.0)
            return size * 2.5  # Ước tính thô: 2.5 PM/KLOC

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
