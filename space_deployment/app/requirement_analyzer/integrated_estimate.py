"""
Phương thức tích hợp các mô hình ước lượng nỗ lực
"""

def integrated_estimate(self, text_input, advanced_params=None):
    """
    Tích hợp ước lượng từ tất cả các mô hình
    
    Args:
        text_input (str): Văn bản yêu cầu đầu vào
        advanced_params (dict, optional): Các tham số nâng cao từ người dùng
        
    Returns:
        dict: Kết quả ước lượng tích hợp
    """
    try:
        # Phân tích văn bản và trích xuất các tham số
        extracted_params = self.analyzer.extract_parameters(text_input)
        
        # Kết hợp các tham số nâng cao từ người dùng nếu có
        if advanced_params:
            extracted_params.update(advanced_params)
        
        # Thực hiện ước lượng LOC động nếu mô hình LOC được kích hoạt
        if 'loc_linear' in self.base_models:
            linear_est = self._dynamic_loc_estimate(extracted_params['loc_linear'], 'linear')
            self.base_models['loc_linear'].override_estimate(
                linear_est, min(85, 60 + 5 * (extracted_params['loc_linear'].get('experience', 1.0)))
            )
            
        if 'loc_random_forest' in self.base_models:
            rf_est = self._dynamic_loc_estimate(extracted_params['loc_random_forest'], 'random_forest')
            self.base_models['loc_random_forest'].override_estimate(
                rf_est, min(90, 65 + 5 * (extracted_params['loc_random_forest'].get('experience', 1.0)))
            )
        
        # Ước lượng từ các mô hình cơ sở
        base_estimates = {}
        for model_name, model_instance in self.base_models.items():
            try:
                base_estimates[model_name] = model_instance.estimate(extracted_params)
            except Exception as e:
                print(f"Error in {model_name} estimation: {e}")
                base_estimates[model_name] = {"estimate": 5.0, "confidence": 30.0}
        
        # Ước lượng từ các mô hình nâng cao nếu được kích hoạt
        if self.use_advanced_models:
            for model_name, model_instance in self.advanced_models.items():
                try:
                    base_estimates[model_name] = model_instance.estimate(text_input, extracted_params)
                except Exception as e:
                    print(f"Error in {model_name} estimation: {e}")
                    base_estimates[model_name] = {"estimate": 7.0, "confidence": 40.0}
        
        # Lấy giá trị ước lượng và độ tin cậy
        estimates = {model: data["estimate"] for model, data in base_estimates.items()}
        confidences = {model: data["confidence"] for model, data in base_estimates.items()}
        
        # Tính toán độ tin cậy tổng thể
        overall_confidence = self._calculate_confidence_level(list(estimates.values()))
        
        # Kết hợp tất cả các ước lượng với độ tin cậy tương ứng
        weighted_estimates = {}
        total_weight = 0
        
        for model, estimate in estimates.items():
            conf = confidences[model]
            weight = conf / 100.0
            weighted_estimates[model] = estimate * weight
            total_weight += weight
        
        # Tính ước lượng tích hợp
        integrated_estimate = sum(weighted_estimates.values()) / max(1e-6, total_weight)
        
        # Chuẩn bị kết quả chi tiết
        return {
            "integrated_estimate": round(integrated_estimate, 2),
            "confidence_level": round(overall_confidence, 2),
            "model_estimates": {model: {"estimate": round(est, 2), "confidence": round(confidences[model], 2)}
                              for model, est in estimates.items()},
            "extracted_parameters": extracted_params
        }
        
    except Exception as e:
        print(f"Error in integrated estimate: {e}")
        return {
            "integrated_estimate": 5.0,
            "confidence_level": 30.0,
            "model_estimates": {"fallback": {"estimate": 5.0, "confidence": 30.0}},
            "error": str(e)
        }