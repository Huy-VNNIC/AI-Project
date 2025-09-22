#!/usr/bin/env python3
"""
COCOMO II API Module

Module này cung cấp API đơn giản để sử dụng các mô hình COCOMO II đã huấn luyện
trong các ứng dụng backend.
"""

import os
import json
import numpy as np
import pandas as pd
import joblib
from typing import Dict, Union, List, Optional, Any, Tuple

class CocomoIIAPI:
    """
    API cho mô hình COCOMO II
    """
    def __init__(self, model_dir: str = './models/cocomo_ii_extended'):
        """
        Khởi tạo API với đường dẫn đến thư mục chứa các mô hình

        Args:
            model_dir: Đường dẫn đến thư mục chứa các mô hình
        """
        self.model_dir = model_dir
        self.models = {}
        self.preprocessor = None
        self.config = None
        self.features = []
        self.log_transform = True
        
        # Tải các mô hình và cấu hình
        self._load_models()
    
    def _load_models(self) -> None:
        """Tải các mô hình và cấu hình từ thư mục"""
        # Kiểm tra thư mục model
        if not os.path.exists(self.model_dir):
            raise FileNotFoundError(f"Không tìm thấy thư mục mô hình: {self.model_dir}")
        
        # Tải cấu hình
        config_path = os.path.join(self.model_dir, "config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            
            self.log_transform = self.config.get('log_transform', True)
            model_names = self.config.get('models', [])
            
            # Tải danh sách đặc trưng từ config
            if 'feature_names' in self.config:
                self.features = self.config['feature_names']
            else:
                # Tải từ feature_info.json nếu có
                feature_info_path = os.path.join(self.model_dir, "feature_info.json")
                if os.path.exists(feature_info_path):
                    with open(feature_info_path, 'r') as f:
                        feature_info = json.load(f)
                        numeric_features = feature_info.get('numeric_features', [])
                        categorical_features = feature_info.get('categorical_features', [])
                        self.features = numeric_features + categorical_features
                else:
                    # Mặc định nếu không tìm thấy thông tin đặc trưng
                    self.features = [
                        'size', 'kloc', 'fp', 'ucp', 'developers', 'time_months',
                        'manager_exp', 'team_exp', 'adjustment', 'transactions',
                        'entities', 'points_non_adjust', 'schema'
                    ]
            
            print(f"Loaded {len(self.features)} features: {self.features}")
            
            # Tải preprocessor
            preprocessor_path = os.path.join(self.model_dir, "preprocessor.pkl")
            if os.path.exists(preprocessor_path):
                try:
                    self.preprocessor = joblib.load(preprocessor_path)
                    print("Đã tải preprocessor thành công")
                except Exception as e:
                    print(f"Lỗi khi tải preprocessor: {str(e)}")
                    self.preprocessor = None
            else:
                print(f"Không tìm thấy file preprocessor: {preprocessor_path}")
                self.preprocessor = None
            
            # Tải các mô hình
            for name in model_names:
                model_path = os.path.join(self.model_dir, f"{name}.pkl")
                if os.path.exists(model_path):
                    self.models[name] = joblib.load(model_path)
                    print(f"Đã tải mô hình {name}")
                else:
                    print(f"Không tìm thấy mô hình {name} tại {model_path}")
            
            if not self.models:
                raise ValueError("Không tìm thấy mô hình nào trong thư mục")
        else:
            raise FileNotFoundError(f"Không tìm thấy file cấu hình: {config_path}")
    
    def get_available_models(self) -> List[str]:
        """
        Lấy danh sách các mô hình có sẵn

        Returns:
            Danh sách tên các mô hình có sẵn
        """
        return list(self.models.keys())
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Lấy thông tin về các mô hình

        Returns:
            Dictionary chứa thông tin về các mô hình
        """
        if self.config:
            return {
                'models': self.get_available_models(),
                'features': self.features,
                'evaluation': self.config.get('evaluation', []),
                'timestamp': self.config.get('timestamp', '')
            }
        return {'models': self.get_available_models()}
    
    def _prepare_input(self, 
                       schema: str, 
                       size: float, 
                       extra_features: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Chuẩn bị dữ liệu đầu vào cho mô hình

        Args:
            schema: Loại schema ('LOC', 'FP', hoặc 'UCP')
            size: Kích thước (KLOC, FP, hoặc UCP)
            extra_features: Các đặc trưng bổ sung (tùy chọn)

        Returns:
            DataFrame chứa dữ liệu đầu vào đã chuẩn bị
        """
        # Tạo dữ liệu cơ bản với tất cả các đặc trưng mặc định là 0
        data = {feature: 0.0 for feature in self.features}
        
        # Đặt giá trị size
        data['size'] = size
        
        # Thiết lập giá trị cho schema (dưới dạng categorical)
        data['schema'] = schema.upper()
        
        # Thêm các đặc trưng cụ thể theo schema
        if schema.upper() == 'LOC':
            data['kloc'] = size
            # Ước tính các tỷ lệ dựa trên size
            data['kloc_per_month'] = size / 10  # Giả định 10 tháng
            data['kloc_per_dev'] = size / 5     # Giả định 5 dev
        elif schema.upper() == 'FP':
            data['fp'] = size
            # Ước tính các tỷ lệ dựa trên size
            data['fp_per_month'] = size / 10    # Giả định 10 tháng
            data['fp_per_dev'] = size / 5       # Giả định 5 dev
            data['points_non_adjust'] = size    # Giả định points non-adjusted = FP
            # Ước tính số entities và transactions
            data['entities'] = size / 10        # Giả định số entities
            data['transactions'] = size / 5     # Giả định số transactions
        elif schema.upper() == 'UCP':
            data['ucp'] = size
            # Ước tính các tỷ lệ dựa trên size (UCP)
        else:
            raise ValueError("schema phải là 'LOC', 'FP', hoặc 'UCP'")
        
        # Thiết lập các giá trị mặc định hợp lý cho các đặc trưng khác
        data['developers'] = 5            # Giả định số developers mặc định
        data['time_months'] = 10          # Giả định thời gian mặc định
        data['manager_exp'] = 5           # Giả định kinh nghiệm quản lý
        data['team_exp'] = 3              # Giả định kinh nghiệm đội
        data['adjustment'] = 1.0          # Giả định hệ số điều chỉnh mặc định
        
        # Thêm các đặc trưng bổ sung nếu có
        if extra_features:
            for key, value in extra_features.items():
                if key in data:
                    data[key] = value
        
        # Tạo DataFrame
        df = pd.DataFrame([data])
        
        # Đảm bảo tất cả các cột cần thiết đều có và đúng thứ tự
        # Tạo DataFrame mới với các cột theo đúng thứ tự trong self.features
        result_df = pd.DataFrame()
        for feature in self.features:
            result_df[feature] = df[feature] if feature in df.columns else 0.0
        
        return result_df
    
    def predict(self, 
                schema: str, 
                size: float, 
                model_name: Optional[str] = None, 
                extra_features: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Dự đoán effort, thời gian và số nhà phát triển dựa trên kích thước

        Args:
            schema: Loại schema ('LOC', 'FP', hoặc 'UCP')
            size: Kích thước (KLOC, FP, hoặc UCP)
            model_name: Tên mô hình để sử dụng (nếu không cung cấp, sẽ sử dụng mô hình tốt nhất)
            extra_features: Các đặc trưng bổ sung (tùy chọn)

        Returns:
            Dictionary chứa kết quả dự đoán
        """
        # Chuẩn bị dữ liệu đầu vào
        input_data = self._prepare_input(schema, size, extra_features)
        
        # Xác định mô hình để sử dụng
        if model_name is None:
            # Sử dụng Random Forest nếu có, nếu không thì sử dụng mô hình đầu tiên
            if 'Random_Forest' in self.models:
                model_name = 'Random_Forest'
            else:
                model_name = list(self.models.keys())[0]
        
        if model_name not in self.models:
            raise ValueError(f"Không tìm thấy mô hình '{model_name}'. Các mô hình có sẵn: {self.get_available_models()}")
        
        # Lấy mô hình
        model = self.models[model_name]
        
        # In thông tin debug để kiểm tra đầu vào
        print(f"Input data shape: {input_data.shape}")
        print(f"Input data columns: {input_data.columns.tolist()}")
        
        # Áp dụng preprocessor nếu có
        if self.preprocessor:
            try:
                input_data_transformed = self.preprocessor.transform(input_data)
                # Dự đoán effort
                effort_pred = model.predict(input_data_transformed)[0]
            except Exception as e:
                print(f"Lỗi khi tiền xử lý hoặc dự đoán: {str(e)}")
                # Dự đoán effort trực tiếp từ dữ liệu đầu vào
                effort_pred = model.predict(input_data)[0]
        else:
            # Dự đoán effort
            effort_pred = model.predict(input_data)[0]
        
        # Chuyển đổi ngược nếu đã áp dụng biến đổi logarithmic
        if self.log_transform:
            effort_pm = np.expm1(effort_pred)
        else:
            effort_pm = effort_pred
        
        # Dự đoán thời gian (tháng)
        time_months = 3.67 * (effort_pm ** 0.28)
        
        # Dự đoán số nhà phát triển
        developers = np.ceil(effort_pm / time_months)
        
        # Tính toán chi phí (giả định $5000 mỗi người-tháng)
        cost = effort_pm * 5000
        
        return {
            'input': {
                'schema': schema,
                'size': size,
                'model_name': model_name
            },
            'predictions': {
                'effort_pm': float(effort_pm),
                'time_months': float(time_months),
                'developers': int(developers),
                'cost_usd': float(cost)
            },
            'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def batch_predict(self, 
                     inputs: List[Dict[str, Any]], 
                     model_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Thực hiện dự đoán hàng loạt cho nhiều đầu vào

        Args:
            inputs: Danh sách các đầu vào, mỗi đầu vào là một dictionary với các khóa 'schema', 'size' và tùy chọn 'extra_features'
            model_name: Tên mô hình để sử dụng (nếu không cung cấp, sẽ sử dụng mô hình tốt nhất)

        Returns:
            Danh sách các kết quả dự đoán
        """
        results = []
        for input_data in inputs:
            schema = input_data.get('schema')
            size = input_data.get('size')
            extra_features = input_data.get('extra_features')
            
            if not schema or not size:
                results.append({'error': 'Thiếu schema hoặc size'})
                continue
            
            try:
                result = self.predict(schema, size, model_name, extra_features)
                results.append(result)
            except Exception as e:
                results.append({'error': str(e)})
        
        return results

# Sử dụng API
if __name__ == "__main__":
    # Kiểm tra xem thư mục mô hình có tồn tại hay không
    model_dir = './models/cocomo_ii_extended'
    if not os.path.exists(model_dir):
        print(f"Thư mục mô hình không tồn tại: {model_dir}")
        print("Vui lòng chạy script train_and_export_models.py trước để tạo các mô hình.")
        exit(1)
    
    try:
        # Khởi tạo API
        api = CocomoIIAPI()
        
        # In thông tin mô hình
        model_info = api.get_model_info()
        print("\nThông tin các mô hình:")
        print(f"  - Các mô hình có sẵn: {', '.join(model_info['models'])}")
        print(f"  - Các đặc trưng được sử dụng: {', '.join(model_info['features'])}")
        
        # Ví dụ dự đoán
        print("\nVí dụ dự đoán:")
        
        # Dự đoán với KLOC
        result_loc = api.predict('LOC', 10)
        print("\n1. Dự đoán với 10 KLOC:")
        print(f"  - Effort: {result_loc['predictions']['effort_pm']:.2f} người-tháng")
        print(f"  - Thời gian: {result_loc['predictions']['time_months']:.2f} tháng")
        print(f"  - Số nhà phát triển: {result_loc['predictions']['developers']} người")
        print(f"  - Chi phí ước tính: ${result_loc['predictions']['cost_usd']:.2f}")
        
        # Dự đoán với Function Points
        result_fp = api.predict('FP', 500)
        print("\n2. Dự đoán với 500 Function Points:")
        print(f"  - Effort: {result_fp['predictions']['effort_pm']:.2f} người-tháng")
        print(f"  - Thời gian: {result_fp['predictions']['time_months']:.2f} tháng")
        print(f"  - Số nhà phát triển: {result_fp['predictions']['developers']} người")
        print(f"  - Chi phí ước tính: ${result_fp['predictions']['cost_usd']:.2f}")
        
        # Dự đoán với Use Case Points
        result_ucp = api.predict('UCP', 300)
        print("\n3. Dự đoán với 300 Use Case Points:")
        print(f"  - Effort: {result_ucp['predictions']['effort_pm']:.2f} người-tháng")
        print(f"  - Thời gian: {result_ucp['predictions']['time_months']:.2f} tháng")
        print(f"  - Số nhà phát triển: {result_ucp['predictions']['developers']} người")
        print(f"  - Chi phí ước tính: ${result_ucp['predictions']['cost_usd']:.2f}")
        
        # Dự đoán với các đặc trưng bổ sung
        extra_features = {
            'sector': 'Banking',
            'language': 'Java',
            'methodology': 'Agile',
            'applicationtype': 'Business Application'
        }
        result_extra = api.predict('UCP', 300, extra_features=extra_features)
        print("\n4. Dự đoán với đặc trưng bổ sung:")
        print(f"  - Effort: {result_extra['predictions']['effort_pm']:.2f} người-tháng")
        print(f"  - Thời gian: {result_extra['predictions']['time_months']:.2f} tháng")
        print(f"  - Số nhà phát triển: {result_extra['predictions']['developers']} người")
        print(f"  - Chi phí ước tính: ${result_extra['predictions']['cost_usd']:.2f}")
        
        print("\nAPI sẵn sàng để sử dụng trong backend.")
    except Exception as e:
        print(f"Lỗi khi khởi tạo API: {str(e)}")
