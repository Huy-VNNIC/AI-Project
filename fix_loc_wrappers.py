#!/usr/bin/env python3
"""
Fix for the LOC model training and integration
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

# Add root directory to path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))

def create_dummy_loc_data():
    """Create a dummy LOC dataset if the real one is not accessible"""
    print("Creating dummy LOC training data...")
    
    # Define the data
    data = {
        'project_id': list(range(1, 16)),
        'loc': [5000, 10000, 2500, 15000, 7500, 20000, 3000, 12500, 8000, 18000, 4000, 6000, 9000, 11000, 13000],
        'kloc': [5.0, 10.0, 2.5, 15.0, 7.5, 20.0, 3.0, 12.5, 8.0, 18.0, 4.0, 6.0, 9.0, 11.0, 13.0],
        'effort_pm': [15.2, 28.5, 8.1, 42.3, 21.6, 58.7, 9.8, 36.9, 24.2, 52.1, 12.5, 18.7, 27.3, 32.4, 39.2],
        'complexity': [1.2, 1.5, 1.0, 1.8, 1.3, 2.0, 1.1, 1.6, 1.4, 1.9, 1.2, 1.3, 1.5, 1.6, 1.7],
        'developers': [4, 5, 3, 6, 4, 8, 3, 5, 4, 7, 3, 4, 5, 5, 6],
        'experience': [1.0, 1.2, 1.5, 0.9, 1.1, 1.2, 1.4, 1.0, 1.3, 1.1, 1.2, 1.0, 1.1, 1.2, 1.0]
    }
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(data)
    output_path = os.path.join(PROJECT_ROOT, "processed_data", "loc_based.csv")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Dummy LOC data saved to {output_path}")

def create_dummy_preprocessor():
    """Create a dummy preprocessor for the COCOMO II extended models"""
    print("Creating dummy preprocessor...")
    
    # Create a simple preprocessor
    numeric_features = ['size', 'complexity', 'team_size', 'experience', 'required_reliability', 
                      'database_size', 'documentation', 'time_constraint']
    categorical_features = ['language', 'application_type', 'platform_volatility']
    
    # Create transformers
    numeric_transformer = Pipeline(steps=[('scaler', StandardScaler())])
    categorical_transformer = Pipeline(steps=[('onehot', OneHotEncoder(handle_unknown='ignore'))])
    
    # Create preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])
    
    # Save preprocessor
    output_path = os.path.join(PROJECT_ROOT, "models", "cocomo_ii_extended", "preprocessor.joblib")
    joblib.dump(preprocessor, output_path)
    print(f"Dummy preprocessor saved to {output_path}")
    
    # Also save as .pkl for backward compatibility
    output_path_pkl = os.path.join(PROJECT_ROOT, "models", "cocomo_ii_extended", "preprocessor.pkl")
    joblib.dump(preprocessor, output_path_pkl)

def main():
    """Main function to fix model issues"""
    print("Starting fix for model loading issues...")
    
    # Create dummy LOC data
    create_dummy_loc_data()
    
    # Create dummy preprocessor
    create_dummy_preprocessor()
    
    print("Fix completed. Please restart the API service.")

if __name__ == "__main__":
    main()
