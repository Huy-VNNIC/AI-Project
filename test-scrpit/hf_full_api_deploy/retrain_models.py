#!/usr/bin/env python3
"""
Module to retrain ML models with current feature set
"""

import os
import sys
import numpy as np
import pandas as pd
import joblib
import logging
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("model_retraining.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("ModelRetraining")

def get_sample_data():
    """
    Generate sample data with current feature set for retraining
    
    Returns:
        tuple: X (features) and y (target) datasets
    """
    # Create sample data with the current 9 features
    data = []
    
    # Generate sample projects with varying complexity
    for _ in range(100):
        # Basic project features
        size = np.random.uniform(0.5, 50.0)  # KLOC
        complexity = np.random.uniform(0.7, 1.5)
        reliability = np.random.uniform(0.8, 1.2)
        num_requirements = np.random.randint(5, 50)
        functional_reqs = np.random.randint(3, 30)
        non_functional_reqs = np.random.randint(2, 20)
        has_security = np.random.choice([0, 1])
        has_performance = np.random.choice([0, 1])
        num_technologies = np.random.randint(1, 10)
        
        # Calculate effort based on a simple formula (for sample generation)
        # This should be replaced with actual historical data when available
        base_effort = size * complexity * reliability
        
        # Add variation based on other factors
        effort_variation = (1 + (num_requirements / 50) + 
                           (functional_reqs / 40) + 
                           (non_functional_reqs / 30) +
                           (has_security * 0.2) +
                           (has_performance * 0.15) +
                           (num_technologies / 20))
        
        effort = base_effort * effort_variation
        
        # Add to dataset
        data.append([size, complexity, reliability, num_requirements, 
                    functional_reqs, non_functional_reqs, has_security, 
                    has_performance, num_technologies, effort])
    
    # Convert to DataFrame
    df = pd.DataFrame(data, columns=[
        'size', 'complexity', 'reliability', 'num_requirements', 
        'functional_reqs', 'non_functional_reqs', 'has_security_requirements', 
        'has_performance_requirements', 'num_technologies', 'effort'
    ])
    
    # Split into features and target
    X = df.drop('effort', axis=1)
    y = df['effort']
    
    return X, y

def retrain_models(output_dir='models'):
    """
    Retrain ML models with current feature set and save them
    
    Args:
        output_dir (str): Directory to save retrained models
    """
    logger.info("Starting model retraining process")
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Created output directory: {output_dir}")
    
    # Get sample data with current feature set
    X, y = get_sample_data()
    logger.info(f"Generated sample data with {X.shape[1]} features and {len(X)} samples")
    
    # Split into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Define preprocessor
    numeric_features = list(X.columns)
    
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features)
        ]
    )
    
    # Train and save models
    models = {
        'Linear_Regression': Pipeline([
            ('preprocessor', preprocessor),
            ('regressor', LinearRegression())
        ]),
        'Decision_Tree': Pipeline([
            ('preprocessor', preprocessor),
            ('regressor', DecisionTreeRegressor(random_state=42))
        ]),
        'Random_Forest': Pipeline([
            ('preprocessor', preprocessor),
            ('regressor', RandomForestRegressor(random_state=42))
        ]),
        'Gradient_Boosting': Pipeline([
            ('preprocessor', preprocessor),
            ('regressor', GradientBoostingRegressor(random_state=42))
        ])
    }
    
    # Train and save each model
    for name, model in models.items():
        logger.info(f"Training {name} model...")
        model.fit(X_train, y_train)
        
        # Evaluate on test set
        score = model.score(X_test, y_test)
        logger.info(f"{name} R² score: {score:.4f}")
        
        # Save model
        joblib.dump(model, os.path.join(output_dir, f"{name.lower()}_model.pkl"))
        logger.info(f"Saved {name} model to {output_dir}")
    
    # Save feature list for reference
    feature_list = list(X.columns)
    with open(os.path.join(output_dir, 'feature_list.txt'), 'w') as f:
        f.write('\n'.join(feature_list))
    logger.info(f"Saved feature list to {output_dir}/feature_list.txt")
    
    logger.info("Model retraining completed successfully")

if __name__ == "__main__":
    retrain_models()
