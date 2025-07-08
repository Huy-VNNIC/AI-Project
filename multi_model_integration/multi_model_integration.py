#!/usr/bin/env python3
"""
Mô hình tích hợp đa mô hình ước lượng nỗ lực phần mềm
"""

import numpy as np
try:
    # When imported as a package
    from .estimation_models import COCOMOII, FunctionPoints, UseCasePoints, PlanningPoker
except ImportError:
    # When run directly
    from estimation_models import COCOMOII, FunctionPoints, UseCasePoints, PlanningPoker

class MultiModelIntegration:
    """
    Lớp tích hợp đa mô hình ước lượng nỗ lực phần mềm
    """
    
    def __init__(self, models=None):
        """
        Khởi tạo mô hình tích hợp
        
        Args:
            models (list, optional): Danh sách các mô hình cần tích hợp
        """
        self.models = models or [
            COCOMOII(),
            FunctionPoints(),
            UseCasePoints(),
            PlanningPoker()
        ]
        
        self.integration_methods = {
            "weighted_average": self._weighted_average,
            "best_model": self._best_model,
            "stacking": self._stacking,
            "bayesian_average": self._bayesian_average
        }
    
    def estimate(self, project_data, method="weighted_average"):
        """
        Ước lượng nỗ lực sử dụng tích hợp đa mô hình
        
        Args:
            project_data (dict): Thông tin dự án
            method (str): Phương pháp tích hợp (weighted_average, best_model, stacking, bayesian_average)
            
        Returns:
            dict: Kết quả ước lượng tích hợp
        """
        if method not in self.integration_methods:
            raise ValueError(f"Phương pháp {method} không được hỗ trợ. Các phương pháp có sẵn: {list(self.integration_methods.keys())}")
        
        # Thực hiện ước lượng từ từng mô hình
        model_results = []
        for model in self.models:
            try:
                # Check if we have enough data for this model
                suitability = model.suitability_score(project_data)
                
                # Skip models with very low suitability
                if suitability < 0.2:
                    print(f"Skipping {model.model_name} due to low suitability: {suitability:.2f}")
                    continue
                
                # If model is FunctionPoints, ensure we have the necessary adjustment factor
                if model.model_name == "Function Points" and "complexity_adjustment" not in project_data:
                    project_data["complexity_adjustment"] = 1.0
                    print(f"Added default complexity_adjustment=1.0 for Function Points model")
                
                # If model is COCOMO II, add default values for missing fields
                if model.model_name == "COCOMO II":
                    if "team_experience" not in project_data:
                        project_data["team_experience"] = 1.0
                    if "schedule_constraint" not in project_data:
                        project_data["schedule_constraint"] = 1.0
                    print(f"Added default values for COCOMO II model")
                
                result = model.estimate_effort(project_data)
                result["suitability"] = suitability
                model_results.append(result)
                print(f"Model {model.model_name}: Effort = {result['effort_pm']:.2f} person-months, Confidence = {result['confidence']:.2f}, Suitability = {suitability:.2f}")
            except Exception as e:
                print(f"Lỗi khi ước lượng với mô hình {model.model_name}: {str(e)}")
        
        if not model_results:
            raise ValueError("Không có mô hình nào có thể ước lượng với dữ liệu đã cho")
        
        # Thực hiện tích hợp theo phương pháp được chọn
        integration_method = self.integration_methods[method]
        result = integration_method(model_results, project_data)
        
        return result
    
    def _weighted_average(self, model_results, project_data):
        """
        Tích hợp dựa trên trung bình có trọng số của các kết quả
        
        Args:
            model_results (list): Danh sách kết quả từ các mô hình
            project_data (dict): Thông tin dự án
            
        Returns:
            dict: Kết quả tích hợp
        """
        total_weight = 0
        weighted_effort = 0
        weighted_time = 0
        weighted_team_size = 0
        
        for result in model_results:
            # Trọng số là tích của độ tin cậy và độ phù hợp
            weight = result["confidence"] * result["suitability"]
            weighted_effort += result["effort_pm"] * weight
            weighted_time += result["time_months"] * weight
            weighted_team_size += result.get("team_size", 0) * weight
            total_weight += weight
        
        if total_weight == 0:
            # Nếu tổng trọng số = 0, sử dụng trung bình đơn giản
            weighted_effort = sum(r["effort_pm"] for r in model_results) / len(model_results)
            weighted_time = sum(r["time_months"] for r in model_results) / len(model_results)
            weighted_team_size = sum(r.get("team_size", 0) for r in model_results) / len(model_results)
        else:
            weighted_effort /= total_weight
            weighted_time /= total_weight
            weighted_team_size /= total_weight
        
        # Tạo danh sách đóng góp của từng mô hình
        contributions = []
        for result in model_results:
            weight = result["confidence"] * result["suitability"]
            contribution = (weight / total_weight) if total_weight > 0 else (1 / len(model_results))
            contributions.append({
                "model": result["model"],
                "effort_pm": result["effort_pm"],
                "contribution": contribution,
                "weight": weight
            })
        
        return {
            "effort_pm": weighted_effort,
            "time_months": weighted_time,
            "team_size": weighted_team_size,
            "method": "weighted_average",
            "model_contributions": contributions,
            "confidence": sum(r["confidence"] * r["suitability"] for r in model_results) / sum(r["suitability"] for r in model_results) if sum(r["suitability"] for r in model_results) > 0 else 0.5
        }
    
    def _best_model(self, model_results, project_data):
        """
        Chọn kết quả từ mô hình tốt nhất (có độ phù hợp cao nhất)
        
        Args:
            model_results (list): Danh sách kết quả từ các mô hình
            project_data (dict): Thông tin dự án
            
        Returns:
            dict: Kết quả từ mô hình tốt nhất
        """
        # Sắp xếp theo độ phù hợp giảm dần
        sorted_results = sorted(model_results, key=lambda r: r["suitability"], reverse=True)
        best_result = sorted_results[0]
        
        # Thêm thông tin về mô hình tốt nhất
        result = {
            "effort_pm": best_result["effort_pm"],
            "time_months": best_result["time_months"],
            "team_size": best_result.get("team_size", 0),
            "method": "best_model",
            "best_model": best_result["model"],
            "confidence": best_result["confidence"],
            "suitability": best_result["suitability"],
            "all_models": [{"model": r["model"], "suitability": r["suitability"]} for r in sorted_results]
        }
        
        return result
    
    def _stacking(self, model_results, project_data):
        """
        Tích hợp dựa trên phương pháp stacking (meta-model)
        Lưu ý: Phương pháp này yêu cầu có mô hình meta đã được huấn luyện trước
        
        Args:
            model_results (list): Danh sách kết quả từ các mô hình
            project_data (dict): Thông tin dự án
            
        Returns:
            dict: Kết quả tích hợp
        """
        # Trong một triển khai thực tế, sẽ cần một meta-model đã được huấn luyện
        # Ở đây, chúng ta sẽ mô phỏng bằng cách sử dụng trung bình có trọng số nâng cao
        
        # Trích xuất các kết quả dự đoán
        predictions = np.array([r["effort_pm"] for r in model_results])
        confidences = np.array([r["confidence"] for r in model_results])
        suitabilities = np.array([r["suitability"] for r in model_results])
        
        # Tính trọng số dựa trên khoảng cách đến giá trị trung bình
        mean_prediction = np.mean(predictions)
        distances = 1.0 / (1.0 + np.abs(predictions - mean_prediction))
        
        # Kết hợp các trọng số
        weights = distances * confidences * suitabilities
        weights = weights / np.sum(weights) if np.sum(weights) > 0 else np.ones_like(weights) / len(weights)
        
        # Dự đoán cuối cùng
        final_effort = np.sum(predictions * weights)
        
        # Tính thời gian và team size
        time_months = 3.67 * (final_effort ** 0.28)
        team_size = final_effort / time_months
        
        # Tạo danh sách đóng góp của từng mô hình
        contributions = []
        for i, result in enumerate(model_results):
            contributions.append({
                "model": result["model"],
                "effort_pm": result["effort_pm"],
                "contribution": weights[i],
                "weight": weights[i]
            })
        
        return {
            "effort_pm": final_effort,
            "time_months": time_months,
            "team_size": team_size,
            "method": "stacking",
            "model_contributions": contributions,
            "confidence": np.sum(confidences * weights)
        }
    
    def _bayesian_average(self, model_results, project_data):
        """
        Tích hợp dựa trên trung bình Bayesian
        
        Args:
            model_results (list): Danh sách kết quả từ các mô hình
            project_data (dict): Thông tin dự án
            
        Returns:
            dict: Kết quả tích hợp
        """
        # Giả định prior (dựa trên kinh nghiệm trước đó)
        prior_mean = 10.0  # Giả định trung bình prior
        prior_strength = 2.0  # Độ mạnh của prior (tương đương với số lượng quan sát)
        
        total_strength = prior_strength
        weighted_sum = prior_mean * prior_strength
        
        for result in model_results:
            # Độ mạnh của mỗi mô hình dựa trên độ tin cậy và độ phù hợp
            model_strength = result["confidence"] * result["suitability"] * 10
            weighted_sum += result["effort_pm"] * model_strength
            total_strength += model_strength
        
        # Tính giá trị posterior
        posterior_mean = weighted_sum / total_strength
        
        # Tính thời gian và team size
        time_months = 3.67 * (posterior_mean ** 0.28)
        team_size = posterior_mean / time_months
        
        # Tạo danh sách đóng góp của từng mô hình
        contributions = []
        for result in model_results:
            model_strength = result["confidence"] * result["suitability"] * 10
            contribution = model_strength / total_strength
            contributions.append({
                "model": result["model"],
                "effort_pm": result["effort_pm"],
                "contribution": contribution,
                "weight": model_strength
            })
        
        # Thêm đóng góp của prior
        contributions.append({
            "model": "Prior",
            "effort_pm": prior_mean,
            "contribution": prior_strength / total_strength,
            "weight": prior_strength
        })
        
        return {
            "effort_pm": posterior_mean,
            "time_months": time_months,
            "team_size": team_size,
            "method": "bayesian_average",
            "model_contributions": contributions,
            "confidence": 0.8  # Bayesian thường có độ tin cậy cao hơn
        }
