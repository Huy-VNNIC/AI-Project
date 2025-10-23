
import os
import json
from pathlib import Path

class ModelWeightManager:
    """
    Quản lý trọng số cho việc tích hợp các mô hình ước lượng
    """
    
    def __init__(self):
        """Khởi tạo ModelWeightManager"""
        self.weights = {}
        self.complexity_factors = {}
        self.size_scaling = {}
        self._load_weights()
    
    def _load_weights(self):
        """Tải trọng số từ file cấu hình"""
        weight_path = os.path.join(Path(__file__).parent.parent, "models", "integration_weights.json")
        if os.path.exists(weight_path):
            try:
                with open(weight_path, "r") as f:
                    config = json.load(f)
                self.weights = config.get("model_weights", {})
                self.complexity_factors = config.get("complexity_factors", {})
                self.size_scaling = config.get("size_scaling", {})
                print("Loaded model integration weights successfully")
            except Exception as e:
                print(f"Error loading model weights: {e}")
                self._set_default_weights()
        else:
            print("Weight configuration file not found, using defaults")
            self._set_default_weights()
    
    def _set_default_weights(self):
        """Thiết lập trọng số mặc định nếu không thể tải từ file"""
        self.weights = {
            "cocomo": 2.0,         
            "function_points": 1.5, 
            "use_case_points": 1.8, 
            "loc_linear": 1.2,      
            "loc_random_forest": 1.3, 
            "ml_Linear_Regression": 0.8, 
            "ml_Decision_Tree": 0.9,    
            "ml_Random_Forest": 1.0,    
            "ml_Gradient_Boosting": 1.0 
        }
        self.complexity_factors = {
            "low": 0.8,
            "medium": 1.0,
            "high": 1.5,
            "very_high": 2.0
        }
        self.size_scaling = {
            "small": 1.0,      # < 10 KLOC
            "medium": 1.2,     # 10-50 KLOC
            "large": 1.5,      # 50-100 KLOC
            "very_large": 1.8  # > 100 KLOC
        }
    
    def get_model_weight(self, model_name):
        """
        Lấy trọng số cho một mô hình cụ thể
        
        Args:
            model_name (str): Tên mô hình
            
        Returns:
            float: Trọng số mô hình
        """
        # Xử lý các trường hợp đặc biệt cho mô hình ML
        if model_name.startswith("ml_"):
            base_name = model_name[3:]  # Remove 'ml_' prefix
            return self.weights.get(model_name, self.weights.get(f"ml_{base_name}", 1.0))
        return self.weights.get(model_name, 1.0)
    
    def get_complexity_factor(self, complexity):
        """
        Lấy hệ số điều chỉnh dựa trên độ phức tạp
        
        Args:
            complexity (float or str): Độ phức tạp
            
        Returns:
            float: Hệ số điều chỉnh
        """
        if isinstance(complexity, str):
            return self.complexity_factors.get(complexity.lower(), 1.0)
        
        # Chuyển đổi độ phức tạp số thành chuỗi
        if complexity >= 2.0:
            return self.complexity_factors.get("very_high", 2.0)
        elif complexity >= 1.5:
            return self.complexity_factors.get("high", 1.5)
        elif complexity >= 1.0:
            return self.complexity_factors.get("medium", 1.0)
        else:
            return self.complexity_factors.get("low", 0.8)
    
    def get_size_scaling(self, kloc):
        """
        Lấy hệ số điều chỉnh dựa trên kích thước dự án
        
        Args:
            kloc (float): Kích thước dự án tính bằng KLOC
            
        Returns:
            float: Hệ số điều chỉnh
        """
        if kloc >= 100:
            return self.size_scaling.get("very_large", 1.8)
        elif kloc >= 50:
            return self.size_scaling.get("large", 1.5)
        elif kloc >= 10:
            return self.size_scaling.get("medium", 1.2)
        else:
            return self.size_scaling.get("small", 1.0)

# Singleton instance
weight_manager = ModelWeightManager()

def apply_weight_factors(estimates, project_data=None):
    """
    Áp dụng các hệ số trọng số vào các ước lượng
    
    Args:
        estimates (dict): Các ước lượng từ các mô hình khác nhau
        project_data (dict, optional): Dữ liệu dự án
        
    Returns:
        dict: Các ước lượng đã được điều chỉnh
    """
    adjusted_estimates = {}
    
    # Mặc định nếu không có dữ liệu dự án
    if project_data is None:
        project_data = {}
    
    # Lấy kích thước dự án nếu có
    kloc = 0
    if 'kloc' in project_data:
        kloc = float(project_data['kloc'])
    elif 'loc' in project_data:
        kloc = float(project_data['loc']) / 1000
    elif 'size' in project_data:
        kloc = float(project_data['size'])
    
    # Lấy độ phức tạp nếu có
    complexity = project_data.get('complexity', 1.0)
    
    # Hệ số điều chỉnh theo kích thước
    size_factor = weight_manager.get_size_scaling(kloc)
    
    # Hệ số điều chỉnh theo độ phức tạp
    complexity_factor = weight_manager.get_complexity_factor(complexity)
    
    for model_name, estimate in estimates.items():
        # Lấy trọng số của mô hình
        weight = weight_manager.get_model_weight(model_name)
        
        # Áp dụng các hệ số điều chỉnh
        adjusted_value = estimate * weight * size_factor * complexity_factor
        
        adjusted_estimates[model_name] = adjusted_value
    
    return adjusted_estimates
