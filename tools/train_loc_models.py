#!/usr/bin/env python3
"""
Huấn luyện mô hình LOC từ dữ liệu
"""

import os
import sys
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
from pathlib import Path

# Thêm thư mục gốc vào sys.path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from requirement_analyzer.loc_model import LOCModel

def load_data():
    """
    Tải dữ liệu LOC từ file CSV
    
    Returns:
        pd.DataFrame: Dữ liệu đã tải
    """
    data_path = os.path.join(PROJECT_ROOT, "processed_data", "loc_based.csv")
    
    if not os.path.exists(data_path):
        print(f"Data file not found: {data_path}")
        return None
    
    try:
        df = pd.read_csv(data_path)
        print(f"Loaded {len(df)} records from {data_path}")
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def main():
    """Hàm chính để huấn luyện và lưu mô hình"""
    print("Starting LOC model training...")
    
    # Tạo thư mục để lưu mô hình
    output_dir = os.path.join(PROJECT_ROOT, "models", "loc_models")
    os.makedirs(output_dir, exist_ok=True)
    
    # Tải dữ liệu
    df = load_data()
    if df is None:
        print("No data available for training. Exiting.")
        return
    
    # Huấn luyện mô hình Linear
    print("Training LOC Linear model...")
    loc_linear = LOCModel(model_type="linear")
    if loc_linear.train():
        loc_linear_path = os.path.join(output_dir, "loc_linear.joblib")
        loc_linear.save(loc_linear_path)
        print(f"LOC Linear model saved to {loc_linear_path}")
    
    # Huấn luyện mô hình Random Forest
    print("Training LOC Random Forest model...")
    loc_rf = LOCModel(model_type="random_forest")
    if loc_rf.train():
        loc_rf_path = os.path.join(output_dir, "loc_rf.joblib")
        loc_rf.save(loc_rf_path)
        print(f"LOC Random Forest model saved to {loc_rf_path}")
    
    print("LOC model training completed.")

if __name__ == "__main__":
    main()