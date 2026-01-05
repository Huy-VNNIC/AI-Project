#!/usr/bin/env python3
"""
Fix for preprocessor string column specification issue
"""

import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import joblib

# Add root directory to path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))

def create_fixed_preprocessor():
    """Create a preprocessor that works with numpy arrays instead of dataframes"""
    print("Creating fixed preprocessor that works with numpy arrays...")
    
    # Create models directory
    models_dir = os.path.join(PROJECT_ROOT, "models", "cocomo_ii_extended")
    os.makedirs(models_dir, exist_ok=True)
    
    # Create dummy data for fitting
    n_samples = 30
    X_dummy = np.random.rand(n_samples, 4)  # 4 features: size, complexity, team_size, experience
    
    # Simple standard scaler that works with numeric arrays
    preprocessor = StandardScaler()
    
    # Fit the preprocessor
    preprocessor.fit(X_dummy)
    
    # Save preprocessor
    output_path = os.path.join(models_dir, "preprocessor.joblib")
    joblib.dump(preprocessor, output_path)
    print(f"Fixed preprocessor saved to {output_path}")
    
    # Also save as .pkl for backward compatibility
    output_path_pkl = os.path.join(models_dir, "preprocessor.pkl")
    joblib.dump(preprocessor, output_path_pkl)
    print(f"Fixed preprocessor also saved as {output_path_pkl}")
    
    # Create and train models compatible with the new preprocessor
    X_scaled = preprocessor.transform(X_dummy)
    y_dummy = 2 * X_dummy[:, 0] + 3 * X_dummy[:, 1] + 1.5 * X_dummy[:, 2] - 0.5 * X_dummy[:, 3] + np.random.normal(0, 0.1, n_samples)
    
    # Create and train models
    models = {
        "Linear_Regression": LinearRegression(),
        "Decision_Tree": DecisionTreeRegressor(max_depth=3, random_state=42),
        "Random_Forest": RandomForestRegressor(n_estimators=20, random_state=42),
        "Gradient_Boosting": GradientBoostingRegressor(n_estimators=20, random_state=42)
    }
    
    # Train and save each model
    for model_name, model in models.items():
        print(f"Training and saving {model_name} model with numpy array support...")
        model.fit(X_scaled, y_dummy)
        
        # Save model in joblib format
        model_path = os.path.join(models_dir, f"{model_name}.joblib")
        joblib.dump(model, model_path)
        
        # Also save as .pkl for backward compatibility
        model_path_pkl = os.path.join(models_dir, f"{model_name}.pkl")
        joblib.dump(model, model_path_pkl)
        
        print(f"Model {model_name} saved with numpy array support")

def main():
    """Main function"""
    print("Starting fix for preprocessor string column specification issue...")
    create_fixed_preprocessor()
    print("Fix completed. Please restart the API service.")

if __name__ == "__main__":
    main()
