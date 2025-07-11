#!/usr/bin/env python3
"""
Các mô hình ước lượng nỗ lực phần mềm khác nhau
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from abc import ABC, abstractmethod

class EstimationModel(ABC):
    """Lớp cơ sở trừu tượng cho các mô hình ước lượng"""
    
    @abstractmethod
    def estimate_effort(self, project_data):
        """
        Ước lượng nỗ lực dựa trên dữ liệu dự án
        
        Args:
            project_data (dict): Thông tin dự án
            
        Returns:
            dict: Kết quả ước lượng bao gồm effort, độ tin cậy và thông tin khác
        """
        pass
    
    def estimate(self, project_data):
        """
        Phương thức tương thích để gọi estimate_effort
        
        Args:
            project_data (dict): Thông tin dự án
            
        Returns:
            dict: Kết quả ước lượng
        """
        return self.estimate_effort(project_data)
    
    @property
    @abstractmethod
    def model_name(self):
        """Tên của mô hình"""
        pass
    
    @property
    @abstractmethod
    def input_features(self):
        """Danh sách các đặc trưng đầu vào mà mô hình cần"""
        pass
    
    def suitability_score(self, project_data):
        """
        Tính điểm phù hợp của mô hình với dự án cụ thể
        
        Args:
            project_data (dict): Thông tin dự án
            
        Returns:
            float: Điểm phù hợp từ 0-1, càng cao càng phù hợp
        """
        # Mặc định trả về 0.5, các lớp con sẽ ghi đè
        return 0.5

class COCOMOII(EstimationModel):
    """Mô hình COCOMO II"""
    
    def __init__(self, model_path=None):
        """
        Khởi tạo mô hình COCOMO II
        
        Args:
            model_path (str, optional): Đường dẫn đến mô hình đã huấn luyện
        """
        self.A = 2.94  # Hằng số COCOMO II mặc định
        self.B = 1.0997  # Hằng số mũ kích thước
        self._model_name = "COCOMO II"
        self._input_features = [
            "size", "reliability", "complexity", "reuse", "documentation",
            "team_experience", "language_experience", "tool_experience",
            "schedule_constraint"
        ]
        
        # Nếu có đường dẫn mô hình ML, sẽ tải mô hình
        if model_path:
            try:
                import joblib
                self.ml_model = joblib.load(model_path)
                self.use_ml = True
                print(f"Đã tải mô hình COCOMO II ML từ {model_path}")
            except Exception as e:
                print(f"Không thể tải mô hình ML: {str(e)}")
                self.use_ml = False
        else:
            self.use_ml = False
    
    @property
    def model_name(self):
        return self._model_name
    
    @property
    def input_features(self):
        return self._input_features
    
    def estimate_effort(self, project_data):
        """
        Ước lượng nỗ lực sử dụng COCOMO II
        
        Args:
            project_data (dict): Thông tin dự án
            
        Returns:
            dict: Kết quả ước lượng
        """
        # Kiểm tra dữ liệu đầu vào
        if "size" not in project_data:
            raise ValueError("Cần có thông tin kích thước (size) để ước lượng COCOMO II")
        
        size = project_data.get("size", 0)  # KLOC
        
        # Đảm bảo size hợp lệ
        if size <= 0:
            # Sử dụng giá trị mặc định thay vì báo lỗi
            size = 10  # Giá trị KLOC mặc định
            print(f"Warning: Invalid size value ({project_data.get('size')}). Using default size of 10 KLOC.")
        
        if self.use_ml and hasattr(self, 'ml_model'):
            # Sử dụng mô hình ML nếu có
            features = self._extract_features(project_data)
            effort_pm = self.ml_model.predict([features])[0]
            confidence = 0.8  # Giả định độ tin cậy cao hơn với ML
        else:
            # Sử dụng công thức COCOMO II truyền thống
            ems = self._calculate_effort_multipliers(project_data)
            effort_pm = self.A * (size ** self.B) * ems
            confidence = 0.7
        
        # Đảm bảo effort hợp lệ
        if effort_pm <= 0 or not np.isfinite(effort_pm):
            print(f"Warning: Invalid effort calculation for COCOMO II. Using default effort.")
            effort_pm = size * 3  # Giá trị mặc định: 3 người-tháng/KLOC
        
        # Tính thời gian và team size
        time_months = 3.67 * (effort_pm ** 0.28) if effort_pm > 0 else 1.0
        team_size = effort_pm / time_months if time_months > 0 else 1.0
        
        return {
            "effort_pm": effort_pm,
            "time_months": time_months,
            "team_size": team_size,
            "confidence": confidence,
            "model": self.model_name
        }
    
    def _calculate_effort_multipliers(self, project_data):
        """Tính các hệ số nhân nỗ lực dựa trên dữ liệu dự án"""
        # Giá trị mặc định
        reliability = project_data.get("reliability", 1.0)
        complexity = project_data.get("complexity", 1.0)
        reuse = project_data.get("reuse", 1.0)
        documentation = project_data.get("documentation", 1.0)
        team_exp = project_data.get("team_experience", 1.0)
        
        # Tính tổng các hệ số nhân
        em_product = reliability * complexity * reuse * documentation * team_exp
        
        return em_product
    
    def _extract_features(self, project_data):
        """Trích xuất đặc trưng cho mô hình ML"""
        features = []
        for feature in self.input_features:
            features.append(project_data.get(feature, 0))
        return features
    
    def suitability_score(self, project_data):
        """Tính điểm phù hợp của COCOMO II với dự án"""
        size = project_data.get("size", 0)
        methodology = project_data.get("methodology", "").lower()
        
        # COCOMO II phù hợp với dự án lớn và phương pháp truyền thống
        size_score = min(1.0, size / 50)  # Càng lớn càng tốt, tối đa ở 50 KLOC
        
        methodology_score = 0.8 if methodology in ["waterfall", "traditional", ""] else 0.4
        
        return 0.6 * size_score + 0.4 * methodology_score

class FunctionPoints(EstimationModel):
    """Mô hình Function Points Analysis (FPA)"""
    
    def __init__(self):
        self._model_name = "Function Points"
        self._input_features = [
            "external_inputs", "external_outputs", "external_inquiries",
            "internal_files", "external_files", "complexity_adjustment"
        ]
    
    @property
    def model_name(self):
        return self._model_name
    
    @property
    def input_features(self):
        return self._input_features
    
    def estimate_effort(self, project_data):
        """
        Ước lượng nỗ lực sử dụng Function Points
        
        Args:
            project_data (dict): Thông tin dự án
            
        Returns:
            dict: Kết quả ước lượng
        """
        # Kiểm tra nếu có function_points trực tiếp
        if "function_points" in project_data:
            # Sử dụng function_points trực tiếp và bỏ qua việc tính toán chi tiết
            ufp = project_data["function_points"]
            # Tạo các thành phần mặc định nếu chưa có
            if "external_inputs" not in project_data:
                project_data["external_inputs"] = ufp * 0.3
            if "external_outputs" not in project_data:
                project_data["external_outputs"] = ufp * 0.25
            if "external_inquiries" not in project_data:
                project_data["external_inquiries"] = ufp * 0.2
            if "internal_files" not in project_data:
                project_data["internal_files"] = ufp * 0.15
            if "external_files" not in project_data:
                project_data["external_files"] = ufp * 0.1
        
        # Map các thành phần thay thế nếu có
        if "input" in project_data and "external_inputs" not in project_data:
            project_data["external_inputs"] = project_data["input"]
        if "output" in project_data and "external_outputs" not in project_data:
            project_data["external_outputs"] = project_data["output"]
        if "inquiry" in project_data and "external_inquiries" not in project_data:
            project_data["external_inquiries"] = project_data["inquiry"]
        if "file" in project_data and "internal_files" not in project_data:
            project_data["internal_files"] = project_data["file"]
        if "interface" in project_data and "external_files" not in project_data:
            project_data["external_files"] = project_data["interface"]
        
        # Kiểm tra dữ liệu đầu vào tối thiểu
        required_features = ["external_inputs", "external_outputs", "external_inquiries",
                          "internal_files", "external_files"]
        
        for feature in required_features:
            if feature not in project_data:
                project_data[feature] = 0  # Đặt giá trị mặc định là 0 thay vì báo lỗi
        
        # Trọng số mặc định cho các thành phần
        weights = {
            "external_inputs": 4,     # Đầu vào bên ngoài
            "external_outputs": 5,    # Đầu ra bên ngoài
            "external_inquiries": 4,  # Truy vấn bên ngoài
            "internal_files": 10,     # Tệp logic nội bộ
            "external_files": 7       # Tệp giao diện bên ngoài
        }
        
        # Tính toán UFP (Unadjusted Function Points)
        ufp = 0
        for feature in weights:
            count = project_data.get(feature, 0)
            weight = weights[feature]
            ufp += count * weight
        
        # Áp dụng hệ số điều chỉnh
        vaf = project_data.get("complexity_adjustment", 1.0)  # Value Adjustment Factor
        fp = ufp * vaf
        
        # Ước lượng nỗ lực (giả sử 1 FP = 8 giờ làm việc)
        hours_per_fp = project_data.get("hours_per_fp", 8)
        effort_hours = fp * hours_per_fp
        effort_pm = effort_hours / 160  # Giả sử 160 giờ/tháng
        
        # Ước lượng thời gian và team size
        time_months = 3.0 * (effort_pm ** 0.33) if effort_pm > 0 else 1.0  # Ước lượng dựa trên kinh nghiệm
        team_size = effort_pm / time_months if time_months > 0 else 1.0
        
        return {
            "unadjusted_fp": ufp,
            "adjusted_fp": fp,
            "effort_hours": effort_hours,
            "effort_pm": effort_pm,
            "time_months": time_months,
            "team_size": team_size,
            "confidence": 0.75,
            "model": self.model_name
        }
    
    def suitability_score(self, project_data):
        """Tính điểm phù hợp của FPA với dự án"""
        # FPA phù hợp với dự án có định nghĩa chức năng rõ ràng
        if all(f in project_data for f in self.input_features):
            return 0.9  # Rất phù hợp nếu có đầy đủ thông tin
        
        size = project_data.get("size", 0)
        methodology = project_data.get("methodology", "").lower()
        
        # FPA phù hợp với dự án vừa và nhỏ
        size_score = 1.0 if size < 50 else (0.5 if size < 100 else 0.3)
        
        # FPA phù hợp với cả phương pháp truyền thống và Agile
        methodology_score = 0.7
        if methodology in ["waterfall", "traditional"]:
            methodology_score = 0.8
        elif methodology in ["agile", "scrum", "kanban"]:
            methodology_score = 0.6
        
        return 0.6 * size_score + 0.4 * methodology_score

class UseCasePoints(EstimationModel):
    """Mô hình Use Case Points (UCP)"""
    
    def __init__(self):
        self._model_name = "Use Case Points"
        self._input_features = [
            "simple_actors", "average_actors", "complex_actors",
            "simple_use_cases", "average_use_cases", "complex_use_cases",
            "technical_factors", "environmental_factors"
        ]
    
    @property
    def model_name(self):
        return self._model_name
    
    @property
    def input_features(self):
        return self._input_features
    
    def estimate_effort(self, project_data):
        """
        Ước lượng nỗ lực sử dụng Use Case Points
        
        Args:
            project_data (dict): Thông tin dự án
            
        Returns:
            dict: Kết quả ước lượng
        """
        # Trọng số cho các loại actor
        actor_weights = {
            "simple_actors": 1,      # Simple - Giao diện API
            "average_actors": 2,     # Average - Giao diện người dùng thông qua giao thức
            "complex_actors": 3      # Complex - Giao diện người dùng đồ họa
        }
        
        # Trọng số cho các loại use case
        uc_weights = {
            "simple_use_cases": 5,    # Simple - ≤ 3 giao dịch
            "average_use_cases": 10,  # Average - 4-7 giao dịch
            "complex_use_cases": 15   # Complex - > 7 giao dịch
        }
        
        # Tính Unadjusted Actor Weight (UAW)
        uaw = sum(project_data.get(actor, 0) * weight 
                 for actor, weight in actor_weights.items())
        
        # Tính Unadjusted Use Case Weight (UUCW)
        uucw = sum(project_data.get(uc, 0) * weight 
                  for uc, weight in uc_weights.items())
        
        # Tính Unadjusted Use Case Points (UUCP)
        uucp = uaw + uucw
        
        # Áp dụng các hệ số điều chỉnh
        tcf = project_data.get("technical_factors", 1.0)  # Technical Complexity Factor
        ecf = project_data.get("environmental_factors", 1.0)  # Environmental Complexity Factor
        
        # Tính Use Case Points (UCP)
        ucp = uucp * tcf * ecf
        
        # Ước lượng nỗ lực (giả sử 20 giờ/UCP - trung bình trong ngành)
        hours_per_ucp = project_data.get("hours_per_ucp", 20)
        effort_hours = ucp * hours_per_ucp
        effort_pm = effort_hours / 160  # Giả sử 160 giờ/tháng
        
        # Ước lượng thời gian và team size
        time_months = 3.0 * (effort_pm ** 0.33) if effort_pm > 0 else 1.0  # Ước lượng dựa trên kinh nghiệm
        team_size = effort_pm / time_months if time_months > 0 else 1.0
        
        return {
            "uaw": uaw,
            "uucw": uucw,
            "uucp": uucp,
            "ucp": ucp,
            "effort_hours": effort_hours,
            "effort_pm": effort_pm,
            "time_months": time_months,
            "team_size": team_size,
            "confidence": 0.7,
            "model": self.model_name
        }
    
    def suitability_score(self, project_data):
        """Tính điểm phù hợp của UCP với dự án"""
        # UCP phù hợp với dự án có use case rõ ràng
        use_case_defined = all(f in project_data for f in [
            "simple_use_cases", "average_use_cases", "complex_use_cases"
        ])
        
        if use_case_defined:
            return 0.85
        
        methodology = project_data.get("methodology", "").lower()
        has_requirements = project_data.get("has_requirements", False)
        
        # UCP phù hợp với phương pháp truyền thống hơn là Agile
        methodology_score = 0.8 if methodology in ["waterfall", "traditional", "rup"] else 0.5
        
        # UCP cần có yêu cầu được định nghĩa rõ ràng
        req_score = 0.9 if has_requirements else 0.3
        
        return 0.4 * methodology_score + 0.6 * req_score

class PlanningPoker(EstimationModel):
    """Mô hình Planning Poker từ phương pháp Agile"""
    
    def __init__(self):
        self._model_name = "Planning Poker"
        self._input_features = [
            "story_points", "velocity", "team_size", "sprint_length",
            "task_complexity", "task_uncertainty"
        ]
    
    @property
    def model_name(self):
        return self._model_name
    
    @property
    def input_features(self):
        return self._input_features
    
    def estimate_effort(self, project_data):
        """
        Ước lượng nỗ lực sử dụng Planning Poker
        
        Args:
            project_data (dict): Thông tin dự án
            
        Returns:
            dict: Kết quả ước lượng
        """
        # Kiểm tra dữ liệu đầu vào
        if "story_points" not in project_data:
            raise ValueError("Cần có thông tin story points để ước lượng theo Planning Poker")
        
        story_points = project_data.get("story_points", 0)
        velocity = project_data.get("velocity", 0)  # Story points/sprint
        
        if velocity <= 0:
            # Nếu không có velocity, ước tính dựa trên team size
            team_size = project_data.get("team_size", 5)
            velocity = team_size * 8  # Giả sử mỗi thành viên làm 8 story points/sprint
        
        # Tính số sprint cần thiết
        sprints_needed = story_points / velocity if velocity > 0 else story_points / 8  # Default velocity of 8 if not provided
        
        # Tính thời gian (tháng)
        sprint_length_weeks = project_data.get("sprint_length", 2)
        time_months = sprints_needed * (sprint_length_weeks / 4.33)  # 4.33 tuần/tháng
        
        # Tính effort (người-tháng)
        team_size = project_data.get("team_size", 5)
        effort_pm = time_months * team_size
        
        # Điều chỉnh dựa trên độ phức tạp và không chắc chắn
        complexity_factor = project_data.get("task_complexity", 1.0)
        uncertainty_factor = project_data.get("task_uncertainty", 1.0)
        
        adjusted_effort_pm = effort_pm * complexity_factor * uncertainty_factor
        
        # Tính lại thời gian sau điều chỉnh
        adjusted_time_months = 3.0 * (adjusted_effort_pm ** 0.33) if adjusted_effort_pm > 0 else 1.0
        adjusted_team_size = adjusted_effort_pm / adjusted_time_months if adjusted_time_months > 0 else team_size
        
        return {
            "story_points": story_points,
            "velocity": velocity,
            "sprints_needed": sprints_needed,
            "effort_pm": adjusted_effort_pm,
            "time_months": adjusted_time_months,
            "team_size": adjusted_team_size,
            "confidence": 0.75 * (1 / uncertainty_factor),  # Độ tin cậy giảm khi độ không chắc chắn tăng
            "model": self.model_name
        }
    
    def suitability_score(self, project_data):
        """Tính điểm phù hợp của Planning Poker với dự án"""
        methodology = project_data.get("methodology", "").lower()
        has_velocity = "velocity" in project_data and project_data["velocity"] > 0
        has_story_points = "story_points" in project_data and project_data["story_points"] > 0
        
        # Planning Poker chỉ phù hợp với phương pháp Agile
        if methodology not in ["agile", "scrum", "kanban", "xp"]:
            return 0.2
        
        # Cần có story points
        if not has_story_points:
            return 0.3
        
        # Tốt nhất là có cả velocity
        if has_velocity:
            return 0.95
        
        return 0.7
