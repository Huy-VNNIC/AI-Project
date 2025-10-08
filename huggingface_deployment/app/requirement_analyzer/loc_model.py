"""Module chứa các mô hình ước lượng dựa trên LOC (Lines of Code)"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib

class LOCModel:
    """
    Mô hình ước lượng nỗ lực dựa trên LOC (Lines of Code)
    """
    def __init__(self, model_type="linear"):
        """
        Khởi tạo mô hình LOC
        
        Args:
            model_type (str): Loại mô hình ('linear', 'random_forest')
        """
        self.model_type = model_type
        self.model = None
        self.scaler = None
        self.trained = False
        
    def train(self, data_path=None):
        """
        Huấn luyện mô hình từ dữ liệu
        
        Args:
            data_path (str): Đường dẫn đến file dữ liệu
        """
        if data_path is None:
            # Sử dụng đường dẫn mặc định
            base_dir = Path(__file__).parent.parent
            data_path = os.path.join(base_dir, "processed_data", "loc_based.csv")
        
        try:
            # Đọc dữ liệu
            df = pd.read_csv(data_path)
            
            # Chuẩn bị dữ liệu
            X = df[["kloc"]].values
            y = df["effort_pm"].values
            
            # Chuẩn hóa dữ liệu
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Khởi tạo và huấn luyện mô hình
            if self.model_type == "linear":
                self.model = LinearRegression()
            else:
                self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            
            self.model.fit(X_scaled, y)
            self.trained = True
            
            return True
        except Exception as e:
            print(f"Error training LOC model: {e}")
            return False
    
    def override_estimate(self, effort_value, confidence=None):
        """
        Ghi đè kết quả ước lượng với giá trị tùy chỉnh
        
        Args:
            effort_value (float): Giá trị nỗ lực tùy chỉnh
            confidence (float, optional): Độ tin cậy của ước lượng
            
        Returns:
            None
        """
        self._override_value = float(effort_value)
        self._override_confidence = float(confidence or (78.0 if self.model_type == "linear" else 82.0))
    
    def estimate(self, params):
        """
        Ước lượng nỗ lực từ thông số LOC
        
        Args:
            params (dict): Các tham số với kloc là bắt buộc
            
        Returns:
            dict: Kết quả ước lượng với nỗ lực và độ tin cậy
        """
        try:
            # Kiểm tra nếu có giá trị ghi đè
            if hasattr(self, '_override_value'):
                return {"estimate": self._override_value, "confidence": self._override_confidence}
            
            # Kiểm tra mô hình đã được huấn luyện chưa
            if not self.trained:
                self.train()
            
            # Lấy giá trị KLOC
            if 'kloc' in params:
                kloc = float(params['kloc'])
            elif 'loc' in params:
                kloc = float(params['loc']) / 1000
            else:
                kloc = 5.0  # Giá trị mặc định
            
            # Kiểm tra giá trị hợp lệ
            if kloc <= 0:
                kloc = 0.1  # Giá trị nhỏ nhất
            
            # Lấy thêm các yếu tố ảnh hưởng
            complexity = float(params.get('complexity', 1.0))
            developers = float(params.get('developers', 3.0))
            experience = float(params.get('experience', 1.0))
            
            # Điều chỉnh KLOC dựa trên độ phức tạp
            adjusted_kloc = kloc * (1.0 + (complexity - 1.0) * 0.2)
            
            # Chuẩn bị đầu vào cho mô hình
            if self.model is not None and self.scaler is not None:
                # Mô hình đã được huấn luyện
                if self.model_type == "linear":
                    # Mô hình tuyến tính chỉ cần KLOC
                    X = np.array([[adjusted_kloc]])
                    X_scaled = self.scaler.transform(X)
                    effort = self.model.predict(X_scaled)[0]
                    
                    # Điều chỉnh theo kinh nghiệm đội
                    effort = effort * (1.0 + (1.0 - experience) * 0.3)
                else:
                    # Mô hình Random Forest - có thể sử dụng nhiều đặc điểm hơn
                    X = np.array([[adjusted_kloc, complexity, developers, experience]])
                    
                    # Chỉ sử dụng đặc điểm đầu tiên (KLOC) với scaler
                    X_scaled = np.zeros_like(X)
                    X_scaled[:, 0:1] = self.scaler.transform(X[:, 0:1])
                    X_scaled[:, 1:] = X[:, 1:]  # Các đặc điểm khác giữ nguyên
                    
                    effort = self.model.predict(X_scaled)[0]
            else:
                # Sử dụng công thức động nếu không có mô hình
                # COCOMO mở rộng: E = a * (KLOC)^b * EAF
                if self.model_type == "linear":
                    a, b = 2.4, 1.05
                else:
                    # Random Forest thường có hiệu suất cao hơn
                    a, b = 2.8, 1.08
                
                # Hệ số điều chỉnh nỗ lực
                eaf = (complexity * 1.3) / (experience * 0.9 + 0.1) / (developers ** 0.1)
                
                # Tính toán nỗ lực
                effort = a * (adjusted_kloc ** b) * eaf
            
            # Đảm bảo kết quả luôn dương và thực tế
            effort = max(0.5, min(effort, adjusted_kloc * 5))  # Giới hạn nỗ lực hợp lý
            
            # Xác định độ tin cậy dựa trên loại mô hình và chất lượng dữ liệu
            confidence = 78.0 if self.model_type == "linear" else 82.0
            
            # Điều chỉnh độ tin cậy dựa trên mức độ KLOC
            if kloc < 1.0:  # Dự án nhỏ
                confidence -= 3.0
            elif kloc > 50.0:  # Dự án rất lớn
                confidence -= 5.0
                
            # Điều chỉnh độ tin cậy dựa trên kinh nghiệm
            confidence += (experience - 1.0) * 5.0
                
            # Giới hạn độ tin cậy
            confidence = max(60.0, min(90.0, confidence))
            
            return {"estimate": float(effort), "confidence": confidence}
        except Exception as e:
            print(f"Error estimating with LOC model: {e}")
            
            # Sử dụng công thức động nếu có lỗi
            try:
                kloc = params.get('kloc', 5.0)
                if 'loc' in params and 'kloc' not in params:
                    kloc = float(params['loc']) / 1000
                
                complexity = float(params.get('complexity', 1.0))
                developers = float(params.get('developers', 3.0))
                experience = float(params.get('experience', 1.0))
                
                # Hệ số cho từng loại mô hình
                if self.model_type == "linear":
                    a, b = 2.4, 1.05
                else:
                    a, b = 2.8, 1.08
                
                # Hệ số điều chỉnh nỗ lực
                eaf = (complexity * 1.3) / (experience * 0.9 + 0.1) / (developers ** 0.1)
                
                # Tính toán nỗ lực
                effort = a * (kloc ** b) * eaf
                
                # Tính độ tin cậy
                confidence = 75.0 if self.model_type == "linear" else 78.0
                
                # Điều chỉnh độ tin cậy
                confidence = max(65.0, min(85.0, confidence))
                
                return {"estimate": max(0.5, min(effort, kloc * 5)), "confidence": confidence}
            except:
                # Nếu tất cả đều thất bại, sử dụng công thức đơn giản nhất
                kloc = params.get('kloc', 5.0)
                if 'loc' in params and 'kloc' not in params:
                    kloc = float(params['loc']) / 1000
                estimate = 2.4 * (kloc ** 1.05)
                return {"estimate": estimate, "confidence": 70.0}
    
    def save(self, path):
        """
        Lưu mô hình đã huấn luyện
        
        Args:
            path (str): Đường dẫn để lưu mô hình
        """
        if not self.trained or self.model is None:
            print("No trained model to save.")
            return False
        
        try:
            # Tạo thư mục nếu chưa tồn tại
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Lưu mô hình
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'model_type': self.model_type,
                'trained': self.trained
            }
            joblib.dump(model_data, path)
            return True
        except Exception as e:
            print(f"Error saving LOC model: {e}")
            return False
    
    def load(self, path):
        """
        Tải mô hình đã huấn luyện
        
        Args:
            path (str): Đường dẫn đến file mô hình
        """
        try:
            model_data = joblib.load(path)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.model_type = model_data['model_type']
            self.trained = model_data['trained']
            return True
        except Exception as e:
            print(f"Error loading LOC model: {e}")
            return False

def train_loc_models(base_path=None):
    """
    Huấn luyện và lưu các mô hình LOC
    
    Args:
        base_path (str): Thư mục để lưu mô hình
    """
    if base_path is None:
        base_path = os.path.join(Path(__file__).parent.parent, "models", "loc_models")
    
    # Tạo thư mục nếu chưa tồn tại
    os.makedirs(base_path, exist_ok=True)
    
    # Huấn luyện và lưu mô hình tuyến tính
    linear_model = LOCModel(model_type="linear")
    if linear_model.train():
        linear_model.save(os.path.join(base_path, "loc_linear.joblib"))
    
    # Huấn luyện và lưu mô hình Random Forest
    rf_model = LOCModel(model_type="random_forest")
    if rf_model.train():
        rf_model.save(os.path.join(base_path, "loc_rf.joblib"))
    
    print(f"LOC models trained and saved to {base_path}")

if __name__ == "__main__":
    train_loc_models()