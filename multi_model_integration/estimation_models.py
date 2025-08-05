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
        try:
            # Đảm bảo size có giá trị hợp lệ
            if "size" not in project_data or not isinstance(project_data.get("size"), (int, float)) or project_data.get("size", 0) <= 0:
                # Thử lấy size từ các tham số khác
                if "kloc" in project_data:
                    size = float(project_data["kloc"])
                elif "loc" in project_data:
                    size = float(project_data["loc"]) / 1000  # Chuyển LOC thành KLOC
                else:
                    # Ước lượng size từ các thông tin khác
                    fp = project_data.get("function_points", 0) or project_data.get("points_non_adjust", 0)
                    if fp > 0:
                        # Ước lượng KLOC từ Function Points (giả sử 1 FP ~ 100 LOC)
                        size = fp * 0.1  # 0.1 KLOC/FP
                    else:
                        # Giá trị mặc định hợp lý
                        size = 5.0  # 5 KLOC
                        print(f"Added default size={size} KLOC for COCOMO II model")
            else:
                size = float(project_data.get("size"))
            
            # Đảm bảo size nằm trong khoảng hợp lý
            size = max(0.5, min(size, 1000))  # Giới hạn từ 0.5 đến 1000 KLOC
            
            if self.use_ml and hasattr(self, 'ml_model'):
                # Sử dụng mô hình ML nếu có
                try:
                    features = self._extract_features(project_data)
                    effort_pm = self.ml_model.predict([features])[0]
                    confidence = 0.8  # Giả định độ tin cậy cao hơn với ML
                except Exception as e:
                    print(f"ML model failed: {e}. Falling back to standard COCOMO II.")
                    # Sử dụng phương pháp truyền thống nếu ML thất bại
                    ems = self._calculate_effort_multipliers(project_data)
                    effort_pm = self.A * (size ** self.B) * ems
                    confidence = 0.7
            else:
                # Sử dụng công thức COCOMO II truyền thống
                ems = self._calculate_effort_multipliers(project_data)
                effort_pm = self.A * (size ** self.B) * ems
                
                # Điều chỉnh giá trị dựa trên kích thước
                if size < 1.0:  # Dự án nhỏ
                    effort_pm = effort_pm * 0.8  # Giảm nỗ lực do ít overhead
                elif size > 50.0:  # Dự án rất lớn
                    effort_pm = effort_pm * 1.1  # Tăng nỗ lực do độ phức tạp
                
                confidence = 0.7
                
            # Đảm bảo effort hợp lệ
            if effort_pm <= 0 or not np.isfinite(effort_pm):
                print(f"Warning: Invalid effort calculation for COCOMO II. Using estimation based on project size.")
                effort_pm = size * 2.5  # Giá trị ước tính: 2.5 người-tháng/KLOC
            
            # Tính thời gian và team size
            time_months = 3.67 * (effort_pm ** 0.28) if effort_pm > 0 else 1.0
            team_size = effort_pm / time_months if time_months > 0 else 1.0
            
            # Đảm bảo các giá trị đầu ra hợp lý
            effort_pm = round(max(1.0, effort_pm), 2)
            time_months = round(max(1.0, time_months), 1)
            team_size = round(max(1.0, team_size), 1)
            
            return {
                "effort_pm": effort_pm,
                "time_months": time_months,
                "team_size": team_size,
                "confidence": confidence,
                "model": self.model_name
            }
        except Exception as e:
            print(f"Error in COCOMO II estimation: {str(e)}")
            # Trả về giá trị mặc định an toàn dựa trên kích thước dự án (nếu có)
            try:
                size = float(project_data.get("size", 5.0))
            except:
                size = 5.0
                
            # Đảm bảo size hợp lệ
            size = max(0.5, min(size, 1000))
                
            # Ước lượng thô dựa trên kích thước
            effort_pm = size * 2.5
            time_months = max(1.0, 3.0 * (effort_pm ** 0.25))
            team_size = max(1.0, effort_pm / time_months)
            
            return {
                "effort_pm": round(effort_pm, 2),
                "time_months": round(time_months, 1),
                "team_size": round(team_size, 1),
                "confidence": 0.5,
                "model": self.model_name
            }
    
    def _calculate_effort_multipliers(self, project_data):
        """Tính các hệ số nhân nỗ lực dựa trên dữ liệu dự án"""
        try:
            # Kiểm tra và thiết lập giá trị mặc định cho các tham số quan trọng
            # Các tham số được dùng trong tính toán hệ số nỗ lực

            # Thiết lập các giá trị mặc định nếu không có hoặc giá trị không hợp lệ
            default_values = {
                # Các hệ số quy mô (Scale Factors)
                "precedentedness": 1.0,
                "development_flexibility": 1.0, 
                "architecture_risk": 1.0,
                "team_cohesion": 1.0,
                "process_maturity": 1.0,
                
                # Các hệ số nhân nỗ lực (Effort Multipliers)
                "reliability": 1.0,
                "database_size": 1.0,
                "complexity": 1.0,
                "reuse": 0.0,
                "documentation": 1.0,
                
                # Ràng buộc
                "time_constraint": 1.0,
                "storage_constraint": 1.0,
                "platform_volatility": 1.0,
                
                # Nhân sự
                "analyst_capability": 1.0,
                "programmer_capability": 1.0,
                "personnel_continuity": 1.0,
                
                # Kinh nghiệm
                "team_experience": 1.0,
                "language_experience": 1.0,
                "tool_experience": 1.0,
                "personnel_capability": 1.0,
                "personnel_experience": 1.0
            }
            
            # Ánh xạ một số tham số tương đương
            param_mappings = {
                "team_exp": "team_experience",
                "manager_exp": "personnel_capability",
                "reliability_req": "reliability"
            }
            
            # Tạo bản sao của project_data để không ảnh hưởng đến dữ liệu gốc
            data = {**project_data}
            
            # Áp dụng ánh xạ tham số
            for src, dest in param_mappings.items():
                if src in data and dest not in data:
                    data[dest] = data[src]
            
            # Thiết lập các giá trị mặc định cho tham số còn thiếu
            params = {}
            for param, default in default_values.items():
                value = data.get(param, default)
                # Đảm bảo giá trị hợp lệ
                if not isinstance(value, (int, float)) or np.isnan(value) or np.isinf(value):
                    value = default
                params[param] = value
            
            # Nếu có đánh giá độ phức tạp từ phân tích yêu cầu, áp dụng vào complexity
            if "text_complexity" in data:
                text_complexity = data.get("text_complexity", 1.0)
                # Chuyển đổi text_complexity (1.0-3.0) thành complexity (0.7-1.3)
                if text_complexity > 1.0:
                    complexity_factor = 0.7 + (text_complexity - 1.0) / 2.0 * 0.6
                    params["complexity"] = max(params["complexity"], min(complexity_factor, 1.3))
            
            # Điều chỉnh các hệ số dựa trên thông tin bổ sung
            if data.get("has_security_requirements", False):
                params["reliability"] *= 1.1
            
            if data.get("has_performance_requirements", False):
                params["time_constraint"] *= 1.1
            
            if data.get("has_interface_requirements", False):
                params["complexity"] *= 1.05
            
            if data.get("has_data_requirements", False):
                params["database_size"] *= 1.1
            
            # Kiểm tra điều chỉnh hệ số phức tạp nếu cần
            if params["complexity"] > 1.3:
                # Dự án rất phức tạp, điều chỉnh các hệ số khác
                params["reliability"] *= 1.1
                params["time_constraint"] *= 1.1
            
            # Đảm bảo giới hạn hợp lý cho các hệ số
            for key in params:
                if key != "reuse":  # reuse có thể là 0
                    params[key] = max(0.7, min(params[key], 1.5))
            
            # Tính tổng các hệ số nhân
            em_product = (params["reliability"] * params["database_size"] * params["complexity"] * 
                         (1.0 + 0.01 * params["reuse"]) * params["documentation"] * 
                         params["time_constraint"] * params["storage_constraint"] * params["platform_volatility"] * 
                         params["analyst_capability"] * params["programmer_capability"] * params["personnel_continuity"] * 
                         params["team_experience"] * params["language_experience"] * params["tool_experience"])
            
            # Đảm bảo giá trị hợp lệ
            if em_product <= 0 or not np.isfinite(em_product):
                return 1.0
            
            # Giới hạn em_product trong khoảng hợp lý
            em_product = max(0.5, min(em_product, 2.0))
            
            return em_product
        except Exception as e:
            print(f"Error calculating effort multipliers: {str(e)}")
            return 1.0  # Giá trị mặc định an toàn
    
    def _extract_features(self, project_data):
        """Trích xuất đặc trưng cho mô hình ML"""
        try:
            features = []
            for feature in self.input_features:
                # Thiết lập giá trị mặc định hợp lý cho từng đặc trưng
                if feature == "size":
                    default = 5.0
                elif feature in ["reuse"]:
                    default = 0.0
                else:
                    default = 1.0
                
                # Lấy giá trị từ dữ liệu dự án hoặc sử dụng giá trị mặc định
                value = project_data.get(feature, default)
                
                # Đảm bảo giá trị hợp lệ
                if not isinstance(value, (int, float)) or np.isnan(value) or np.isinf(value):
                    value = default
                
                features.append(value)
                
            return features
        except Exception as e:
            print(f"Error extracting features: {str(e)}")
            # Trả về danh sách đặc trưng mặc định
            return [5.0, 1.0, 1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    
    def suitability_score(self, project_data):
        """Tính điểm phù hợp của COCOMO II với dự án"""
        try:
            size = project_data.get("size", 0)
            methodology = project_data.get("methodology", "").lower()
            
            # COCOMO II phù hợp với dự án lớn và phương pháp truyền thống
            size_score = min(1.0, size / 50)  # Càng lớn càng tốt, tối đa ở 50 KLOC
            
            methodology_score = 0.8 if methodology in ["waterfall", "traditional", ""] else 0.4
            
            return 0.6 * size_score + 0.4 * methodology_score
        except Exception as e:
            print(f"Error calculating suitability score: {str(e)}")
            return 0.5  # Giá trị mặc định

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
        try:
            # Tạo bản sao để không làm thay đổi dữ liệu gốc
            data = dict(project_data)
            
            # Kiểm tra nếu có function_points hoặc points_non_adjust trực tiếp
            ufp = None
            if "function_points" in data:
                ufp = float(data["function_points"])
            elif "points_non_adjust" in data:
                ufp = float(data["points_non_adjust"])
                
            # Nếu đã có ufp, sử dụng nó làm cơ sở để ước lượng các thành phần khác nếu cần
            if ufp is not None:
                # Tạo các thành phần mặc định nếu chưa có
                if "external_inputs" not in data:
                    data["external_inputs"] = max(1, int(ufp * 0.3))
                if "external_outputs" not in data:
                    data["external_outputs"] = max(1, int(ufp * 0.25))
                if "external_inquiries" not in data:
                    data["external_inquiries"] = max(1, int(ufp * 0.2))
                if "internal_files" not in data:
                    data["internal_files"] = max(1, int(ufp * 0.15))
                if "external_files" not in data:
                    data["external_files"] = max(1, int(ufp * 0.1))
            
            # Map các thành phần thay thế nếu có
            alternative_mappings = {
                "input": "external_inputs",
                "output": "external_outputs",
                "inquiry": "external_inquiries",
                "file": "internal_files",
                "interface": "external_files",
                
                "external_input": "external_inputs",
                "external_output": "external_outputs",
                "query": "external_inquiries",
                "logical_file": "internal_files",
                "interface_file": "external_files"
            }
            
            for alt_name, std_name in alternative_mappings.items():
                if alt_name in data and std_name not in data:
                    data[std_name] = data[alt_name]
            
            # Đảm bảo tất cả các thành phần có giá trị hợp lệ
            required_features = ["external_inputs", "external_outputs", "external_inquiries",
                                "internal_files", "external_files"]
            
            # Ước tính giá trị mặc định dựa trên số yêu cầu hoặc kích thước
            default_base = max(1, min(20, int(data.get("num_requirements", 10) / 2)))
            
            # Thiết lập giá trị mặc định khác nhau cho từng loại
            default_values = {
                "external_inputs": max(1, int(default_base * 1.2)),
                "external_outputs": max(1, int(default_base * 1.0)),
                "external_inquiries": max(1, int(default_base * 0.8)),
                "internal_files": max(1, int(default_base * 0.6)),
                "external_files": max(1, int(default_base * 0.4))
            }
            
            # Thiết lập giá trị mặc định cho các thành phần còn thiếu
            for feature in required_features:
                if feature not in data or not isinstance(data[feature], (int, float)) or data[feature] < 1:
                    data[feature] = default_values[feature]
                    print(f"Added default {feature}={default_values[feature]} for Function Points model")
            
            # Kiểm tra nếu cần thiết lập complexity_adjustment
            if "complexity_adjustment" not in data:
                # Lấy từ các thông tin khác nếu có
                if "complexity" in data:
                    # Chuyển đổi từ thang đo complexity (0.7-1.3) sang VAF (0.65-1.35)
                    complexity = data["complexity"]
                    data["complexity_adjustment"] = 0.65 + (complexity - 0.7) * 0.7 / 0.6
                elif "text_complexity" in data:
                    # Chuyển đổi từ thang đo text_complexity (1.0-3.0) sang VAF (0.65-1.35)
                    text_complexity = data["text_complexity"]
                    data["complexity_adjustment"] = 0.65 + (text_complexity - 1.0) * 0.7 / 2.0
                else:
                    # Giá trị mặc định
                    data["complexity_adjustment"] = 1.0
                    print("Added default complexity_adjustment=1.0 for Function Points model")
            
            # Đảm bảo complexity_adjustment nằm trong khoảng hợp lý
            data["complexity_adjustment"] = max(0.65, min(float(data["complexity_adjustment"]), 1.35))
            
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
                count = float(data.get(feature, 0))
                weight = weights[feature]
                ufp += count * weight
            
            # Đảm bảo ufp có giá trị tối thiểu
            ufp = max(20.0, ufp)
            
            # Áp dụng hệ số điều chỉnh
            vaf = float(data.get("complexity_adjustment", 1.0))  # Value Adjustment Factor
            fp = ufp * vaf
            
            # Ước lượng nỗ lực (giả sử 1 FP = 8 giờ làm việc)
            # Điều chỉnh giờ/FP dựa trên ngôn ngữ lập trình
            language = data.get("language", "").lower()
            
            # Bảng chuyển đổi ngôn ngữ sang giờ/FP
            language_hours = {
                "c": 8,
                "c++": 8, 
                "c#": 7,
                "java": 7,
                "python": 6,
                "ruby": 6,
                "php": 6,
                "javascript": 6,
                "typescript": 6.5,
                "go": 7,
                "swift": 7,
                "kotlin": 7,
                "rust": 8.5,
                "assembly": 10,
                "cobol": 9,
                "fortran": 9,
                "perl": 6.5,
                "visual basic": 7
            }
            
            # Tìm giá trị giờ/FP phù hợp nhất
            hours_per_fp = language_hours.get(language, 8)
            
            # Kiểm tra nếu có technologies, điều chỉnh giờ/FP
            if "technologies" in data and isinstance(data["technologies"], list):
                techs = [tech.lower() for tech in data["technologies"]]
                
                # Kiểm tra các công nghệ hiện đại
                modern_techs = ["react", "angular", "vue", "flutter", "django", "spring", "node.js", "express"]
                if any(tech in techs for tech in modern_techs):
                    hours_per_fp *= 0.9  # Giảm 10% thời gian với công nghệ hiện đại
                
                # Kiểm tra các công nghệ phức tạp
                complex_techs = ["machine learning", "ai", "blockchain", "microservices"]
                if any(tech in techs for tech in complex_techs):
                    hours_per_fp *= 1.2  # Tăng 20% thời gian với công nghệ phức tạp
            
            # Cho phép ghi đè giờ/FP nếu được chỉ định trực tiếp
            if "hours_per_fp" in data:
                try:
                    hours_per_fp = float(data["hours_per_fp"])
                except:
                    pass
            
            # Giới hạn giờ/FP trong khoảng hợp lý
            hours_per_fp = max(4.0, min(hours_per_fp, 12.0))
            
            # Tính toán nỗ lực
            effort_hours = fp * hours_per_fp
            effort_pm = effort_hours / 160.0  # Giả sử 160 giờ/tháng
            
            # Ước lượng thời gian và team size
            time_months = 2.5 * (effort_pm ** 0.35) if effort_pm > 0 else 1.0
            team_size = effort_pm / time_months if time_months > 0 else 1.0
            
            # Làm tròn và đảm bảo giá trị hợp lý
            effort_pm = round(max(0.5, effort_pm), 2)  # Ít nhất 0.5 người-tháng
            time_months = round(max(1.0, time_months), 2)  # Ít nhất 1 tháng
            team_size = round(max(1.0, team_size), 1)  # Ít nhất 1 người
        
        except Exception as e:
            print(f"Error in Function Points estimation: {str(e)}")
            # Xác định giá trị dựa trên kích thước (nếu có)
            try:
                size = float(project_data.get("size", 5.0))
                # Ước lượng FP từ KLOC
                ufp = size * 10  # Giả sử 10 FP/KLOC
                fp = ufp * 1.0
            except:
                # Giá trị mặc định nếu không có kích thước
                ufp = 40.0
                fp = 40.0
            
            effort_hours = fp * 8.0
            effort_pm = effort_hours / 160.0
            time_months = 2.0
            team_size = 1.0
        
        return {
            "unadjusted_fp": round(ufp, 2),
            "adjusted_fp": round(fp, 2),
            "effort_hours": round(effort_hours, 2),
            "effort_pm": effort_pm,
            "time_months": time_months,
            "team_size": team_size,
            "confidence": 0.75,
            "model": self.model_name
        }
    
    def suitability_score(self, project_data):
        """Tính điểm phù hợp của FPA với dự án"""
        try:
            # FPA phù hợp với dự án có định nghĩa chức năng rõ ràng
            if all(f in project_data for f in self.input_features):
                return 0.9  # Rất phù hợp nếu có đầy đủ thông tin
            
            # Đối với các dự án có requirements rõ ràng
            if "num_requirements" in project_data and project_data["num_requirements"] > 5:
                return 0.8
            
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
        except Exception as e:
            print(f"Error calculating FP suitability score: {str(e)}")
            return 0.6  # Giá trị mặc định

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
