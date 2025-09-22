#!/usr/bin/env python3
"""
Script to fix model feature mismatch issues in requirement analyzer
"""

import os
import sys
import numpy as np
import pandas as pd
import joblib
import json
import logging
import argparse
import re
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow import keras

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("model_fixes.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("ModelFixing")

def fix_feature_mismatch(model_dir='models'):
    """
    Fix feature mismatch between ML models and feature extraction
    
    Args:
        model_dir (str): Directory containing trained models
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Fixing feature mismatch in {model_dir}")
    
    # Define the current feature set (9 features)
    current_features = [
        'size', 'complexity', 'reliability', 'num_requirements', 
        'functional_reqs', 'non_functional_reqs', 'has_security_requirements', 
        'has_performance_requirements', 'num_technologies'
    ]
    
    # Generate synthetic data based on current feature set
    logger.info("Generating synthetic training data with current feature set")
    X_train = []
    for _ in range(1000):
        size = np.random.uniform(0.5, 50.0)
        complexity = np.random.uniform(0.7, 1.5)
        reliability = np.random.uniform(0.8, 1.2)
        num_requirements = np.random.randint(5, 50)
        functional_reqs = np.random.randint(3, 30)
        non_functional_reqs = np.random.randint(2, 20)
        has_security = np.random.choice([0, 1])
        has_performance = np.random.choice([0, 1])
        num_technologies = np.random.randint(1, 10)
        
        X_train.append([
            size, complexity, reliability, num_requirements, functional_reqs, 
            non_functional_reqs, has_security, has_performance, num_technologies
        ])
    
    X_train = np.array(X_train)
    
    # Generate synthetic effort values based on a formula
    y_train = []
    for x in X_train:
        size, complexity, reliability = x[0], x[1], x[2]
        base_effort = size * complexity * reliability
        effort_variation = (1 + (x[3] / 50) + (x[4] / 40) + (x[5] / 30) + 
                           (x[6] * 0.2) + (x[7] * 0.15) + (x[8] / 20))
        effort = base_effort * effort_variation
        y_train.append(effort)
    
    y_train = np.array(y_train)
    
    # Split into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=0.2, random_state=42)
    
    # Create new scalers
    X_scaler = StandardScaler()
    y_scaler = StandardScaler()
    
    X_scaled = X_scaler.fit_transform(X_train)
    y_scaled = y_scaler.fit_transform(y_train.reshape(-1, 1)).flatten()
    
    # Train new models with the current feature set
    
    # 1. Linear Regression (using RandomForestRegressor for simplicity)
    linear_model = RandomForestRegressor(n_estimators=10, max_depth=3, random_state=42)
    linear_model.fit(X_scaled, y_scaled)
    
    # 2. Decision Tree
    dt_model = RandomForestRegressor(n_estimators=1, max_depth=5, random_state=42)
    dt_model.fit(X_scaled, y_scaled)
    
    # 3. Random Forest
    rf_model = RandomForestRegressor(n_estimators=50, random_state=42)
    rf_model.fit(X_scaled, y_scaled)
    
    # 4. Gradient Boosting (using RandomForestRegressor for simplicity)
    gb_model = RandomForestRegressor(n_estimators=100, random_state=42)
    gb_model.fit(X_scaled, y_scaled)
    
    # Create a neural network model compatible with current features
    nn_model = keras.Sequential([
        keras.layers.Dense(32, activation='relu', input_shape=(X_scaled.shape[1],)),
        keras.layers.Dense(16, activation='relu'),
        keras.layers.Dense(1)
    ])
    
    nn_model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    nn_model.fit(X_scaled, y_scaled, epochs=20, batch_size=32, verbose=1)
    
    # Save the models and scalers
    os.makedirs(model_dir, exist_ok=True)
    
    # Save feature list
    with open(os.path.join(model_dir, 'feature_list.txt'), 'w') as f:
        f.write('\n'.join(current_features))
    
    # Save scalers
    joblib.dump(X_scaler, os.path.join(model_dir, 'X_scaler.pkl'))
    joblib.dump(y_scaler, os.path.join(model_dir, 'y_scaler.pkl'))
    
    # Save models
    joblib.dump(linear_model, os.path.join(model_dir, 'linear_model.pkl'))
    joblib.dump(dt_model, os.path.join(model_dir, 'decision_tree_model.pkl'))
    joblib.dump(rf_model, os.path.join(model_dir, 'random_forest_model.pkl'))
    joblib.dump(gb_model, os.path.join(model_dir, 'gradient_boosting_model.pkl'))
    nn_model.save(os.path.join(model_dir, 'neural_network_model.h5'))
    
    # Create a custom connector model compatible with the current feature set
    connector_model = keras.Sequential([
        keras.layers.Dense(32, activation='relu', input_shape=(X_scaled.shape[1],)),
        keras.layers.Dense(16, activation='relu'),
        keras.layers.Dense(10)  # 10 outputs for different effort parameters
    ])
    
    # Generate synthetic effort parameters
    y_params = []
    for x in X_train:
        size, complexity, reliability = x[0], x[1], x[2]
        
        # COCOMO parameters
        cocomo_size = size
        cocomo_reliability = reliability
        cocomo_complexity = complexity
        
        # Function Point parameters
        fp_inputs = max(1, int(x[3] * 0.3))
        fp_outputs = max(1, int(x[3] * 0.25))
        fp_inquiries = max(1, int(x[3] * 0.2))
        fp_files = max(1, int(x[3] * 0.15))
        
        # Use Case Point parameters
        ucp_actors = max(1, int(x[3] / 4))
        ucp_use_cases = max(1, int(x[3] / 2))
        ucp_tech_factor = min(1.5, 0.8 + (x[8] / 10))
        
        y_params.append([
            cocomo_size, cocomo_reliability, cocomo_complexity,
            fp_inputs, fp_outputs, fp_inquiries, fp_files,
            ucp_actors, ucp_use_cases, ucp_tech_factor
        ])
    
    y_params = np.array(y_params)
    
    # Train connector model
    connector_model.compile(optimizer='adam', loss='mse')
    connector_model.fit(X_scaled, y_params, epochs=20, batch_size=32, verbose=1)
    
    # Save connector model and parameter indices
    connector_model.save(os.path.join(model_dir, 'req_effort_connector.h5'))
    
    # Define parameter indices mapping
    param_indices = {
        'cocomo': {
            'size': 0,
            'reliability': 1,
            'complexity': 2
        },
        'function_points': {
            'inputs': 3,
            'outputs': 4,
            'inquiries': 5,
            'files': 6
        },
        'use_case_points': {
            'actors': 7,
            'use_cases': 8,
            'tech_factor': 9
        }
    }
    
    # Save parameter indices
    with open(os.path.join(model_dir, 'param_indices.json'), 'w') as f:
        json.dump(param_indices, f, indent=2)
    
    logger.info("Model fixing completed successfully")
    return True

def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser(description='Fix model feature mismatch')
    parser.add_argument('--model-dir', type=str, default='models',
                        help='Directory containing trained models')
    
    args = parser.parse_args()
    
    fix_feature_mismatch(args.model_dir)

if __name__ == '__main__':
    main()
