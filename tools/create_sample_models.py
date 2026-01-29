#!/usr/bin/env python3
"""
Script to create placeholder models for demonstration
"""

import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

def create_sample_data():
    """Create a small sample dataset"""
    # Create a small dataset for demonstration
    features = np.random.rand(100, 10)
    target = 5 * features[:, 0] + 3 * features[:, 1] + np.random.randn(100) * 0.5
    
    # Create a DataFrame
    columns = [f'feature_{i}' for i in range(10)]
    df = pd.DataFrame(features, columns=columns)
    df['effort'] = target
    
    return df

def create_sample_models(models_dir='models'):
    """Create sample models for demonstration"""
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
    
    print(f"Creating sample models in {models_dir}")
    
    # Create sample dataset
    df = create_sample_data()
    X = df.drop('effort', axis=1).values
    y = df['effort'].values
    
    # Create Random Forest model
    rf_model = RandomForestRegressor(n_estimators=10, random_state=42)
    rf_model.fit(X, y)
    joblib.dump(rf_model, os.path.join(models_dir, 'rf_model.pkl'))
    print("Created random forest model")
    
    # Create XGBoost-like model (using RandomForest as a substitute)
    xgb_model = RandomForestRegressor(n_estimators=10, random_state=42)
    xgb_model.fit(X, y)
    joblib.dump(xgb_model, os.path.join(models_dir, 'xgb_model.pkl'))
    print("Created XGBoost-like model")
    
    # Create Linear Regression model
    linear_model = RandomForestRegressor(n_estimators=1, max_depth=1, random_state=42)
    linear_model.fit(X, y)
    joblib.dump(linear_model, os.path.join(models_dir, 'linear_model.pkl'))
    print("Created linear regression model")
    
    # Create SVR model
    svr_model = RandomForestRegressor(n_estimators=5, random_state=42)
    svr_model.fit(X, y)
    joblib.dump(svr_model, os.path.join(models_dir, 'svr_model.pkl'))
    print("Created SVR model")
    
    # Create Neural Network model
    nn_model = Sequential([
        Dense(64, activation='relu', input_shape=(10,)),
        Dense(32, activation='relu'),
        Dense(1)
    ])
    nn_model.compile(optimizer='adam', loss='mse')
    nn_model.fit(X, y, epochs=5, verbose=0)
    nn_model.save(os.path.join(models_dir, 'nn_model.h5'))
    print("Created neural network model")
    
    # Create Meta model
    meta_model = RandomForestRegressor(n_estimators=5, random_state=42)
    meta_features = np.random.rand(100, 5)  # Meta features
    meta_model.fit(meta_features, y)
    joblib.dump(meta_model, os.path.join(models_dir, 'meta_model.pkl'))
    print("Created meta model")
    
    # Create requirement classifier models
    req_classifier = RandomForestRegressor(n_estimators=5, random_state=42)
    req_features = np.random.rand(100, 10)
    req_labels = np.random.randint(0, 3, 100)
    req_classifier.fit(req_features, req_labels)
    
    joblib.dump(req_classifier, os.path.join(models_dir, 'relevance_model.pkl'))
    joblib.dump(req_classifier, os.path.join(models_dir, 'req_type_model.pkl'))
    print("Created requirement classifier models")
    
    # Create label map
    label_map = {
        'functional': 0,
        'non-functional': 1,
        'constraint': 2
    }
    joblib.dump(label_map, os.path.join(models_dir, 'label_map.pkl'))
    print("Created label map")
    
    print("All sample models created successfully")

if __name__ == "__main__":
    create_sample_models()
