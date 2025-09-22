"""
Model Retraining Module

This module handles retraining models with collected feedback data
to improve estimation accuracy over time.
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from src.feedback.feedback_collector import load_existing_feedback
import preprocess_new_data as preprocessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='model_retraining.log'
)
logger = logging.getLogger('model_retraining')

MODELS_DIR = "models"
RETRAINED_MODELS_DIR = os.path.join(MODELS_DIR, "retrained")
TRAINING_HISTORY_FILE = os.path.join(RETRAINED_MODELS_DIR, "training_history.json")
ORIGINAL_DATASET_PATH = "datasets/processed_data/combined_features.csv"

def ensure_dirs():
    """Ensure necessary directories exist"""
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)
    
    if not os.path.exists(RETRAINED_MODELS_DIR):
        os.makedirs(RETRAINED_MODELS_DIR)
        logger.info(f"Created directory for retrained models at {RETRAINED_MODELS_DIR}")

def load_original_data():
    """Load the original dataset used for initial model training"""
    try:
        if os.path.exists(ORIGINAL_DATASET_PATH):
            return pd.read_csv(ORIGINAL_DATASET_PATH)
        else:
            logger.warning(f"Original dataset not found at {ORIGINAL_DATASET_PATH}")
            return None
    except Exception as e:
        logger.error(f"Error loading original dataset: {e}")
        return None

def combine_datasets(original_df, feedback_df):
    """Combine original dataset with feedback data"""
    if original_df is None:
        logger.warning("No original dataset available, using only feedback data")
        return preprocess_feedback_data(feedback_df)
    
    if feedback_df.empty:
        logger.warning("No feedback data available, using only original dataset")
        return original_df
    
    # Process feedback data to match original dataset format
    processed_feedback = preprocess_feedback_data(feedback_df)
    
    # Combine datasets
    combined_df = pd.concat([original_df, processed_feedback], ignore_index=True)
    logger.info(f"Combined dataset with {len(original_df)} original samples and {len(processed_feedback)} feedback samples")
    
    return combined_df

def preprocess_feedback_data(feedback_df):
    """
    Process feedback data to extract features compatible with the model
    
    This function converts raw feedback data into feature vectors that can be 
    used for model training, matching the format of the original dataset.
    """
    if feedback_df.empty:
        return pd.DataFrame()
    
    # Create a DataFrame to hold processed data
    processed_data = []
    
    for _, row in feedback_df.iterrows():
        try:
            # Use the requirement text to extract features
            requirement_text = row['requirement_text']
            features = {}
            
            # If features were stored in the feedback, use those
            if row['features'] and row['features'] != '{}':
                try:
                    features = json.loads(row['features'])
                except:
                    # If stored features can't be parsed, extract them from text
                    features = preprocessor.extract_features_from_text(requirement_text)
            else:
                # Extract features from requirement text
                features = preprocessor.extract_features_from_text(requirement_text)
            
            # Create a record with features and actual effort
            record = {
                'actual_effort': row['actual_effort'],
                'effort_unit': row['effort_unit']
            }
            
            # Add all extracted features
            record.update(features)
            
            processed_data.append(record)
            
        except Exception as e:
            logger.error(f"Error processing feedback entry: {e}")
            continue
    
    if not processed_data:
        return pd.DataFrame()
        
    # Convert to DataFrame
    processed_df = pd.DataFrame(processed_data)
    
    # Normalize effort units if needed
    # This assumes effort is normalized to PERSON_MONTH in the original dataset
    processed_df = normalize_effort_units(processed_df)
    
    # Rename the target column to match the original dataset
    if 'actual_effort' in processed_df.columns:
        processed_df.rename(columns={'actual_effort': 'effort'}, inplace=True)
    
    return processed_df

def normalize_effort_units(df):
    """Normalize different effort units to a common scale"""
    if 'effort_unit' not in df.columns:
        return df
    
    result = df.copy()
    
    # Conversion factors (example values - adjust based on your organization's standards)
    hours_per_day = 8
    days_per_month = 20
    
    # Apply conversions
    for idx, row in result.iterrows():
        effort = row['actual_effort'] if 'actual_effort' in result.columns else row['effort']
        unit = row['effort_unit']
        
        if unit == 'HOUR':
            normalized_effort = effort / (hours_per_day * days_per_month)
        elif unit == 'DAY':
            normalized_effort = effort / days_per_month
        else:  # Assume PERSON_MONTH
            normalized_effort = effort
            
        if 'actual_effort' in result.columns:
            result.at[idx, 'actual_effort'] = normalized_effort
        else:
            result.at[idx, 'effort'] = normalized_effort
    
    return result

def train_and_evaluate_models(training_data):
    """Train and evaluate models on the combined dataset"""
    if training_data is None or training_data.empty:
        logger.error("No training data available")
        return None, None
    
    # Prepare features and target
    try:
        # Check if 'effort' column exists in the dataset
        if 'effort' not in training_data.columns:
            logger.error("No 'effort' column found in training data")
            return None, None
            
        # Drop non-feature columns
        X = training_data.drop(['effort'], axis=1)
        if 'effort_unit' in X.columns:
            X = X.drop(['effort_unit'], axis=1)
        
        y = training_data['effort']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Initialize models
        models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'ridge': Ridge(alpha=1.0, random_state=42)
        }
        
        # Training results
        results = {}
        trained_models = {}
        
        # Train and evaluate each model
        for name, model in models.items():
            # Train
            model.fit(X_train, y_train)
            trained_models[name] = model
            
            # Predict
            y_pred = model.predict(X_test)
            
            # Evaluate
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            results[name] = {
                'mse': mse,
                'rmse': rmse,
                'mae': mae,
                'r2': r2,
                'feature_importances': get_feature_importance(model, X) if hasattr(model, 'feature_importances_') else None
            }
            
            logger.info(f"Trained {name}: RMSE={rmse:.4f}, MAE={mae:.4f}, R²={r2:.4f}")
        
        return trained_models, results
        
    except Exception as e:
        logger.error(f"Error during model training: {e}")
        return None, None

def get_feature_importance(model, X):
    """Get feature importances if available"""
    if hasattr(model, 'feature_importances_'):
        return {feature: importance for feature, importance in zip(X.columns, model.feature_importances_)}
    return None

def save_models(models, results):
    """Save trained models and results"""
    ensure_dirs()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if not models:
        logger.error("No models to save")
        return False
    
    try:
        # Save each model
        for name, model in models.items():
            model_path = os.path.join(RETRAINED_MODELS_DIR, f"{name}_{timestamp}.pkl")
            joblib.dump(model, model_path)
            logger.info(f"Saved {name} model to {model_path}")
            
            # Also save as the latest version
            latest_path = os.path.join(RETRAINED_MODELS_DIR, f"{name}_latest.pkl")
            joblib.dump(model, latest_path)
            logger.info(f"Saved {name} model as latest version")
        
        # Load training history or create new
        history = []
        if os.path.exists(TRAINING_HISTORY_FILE):
            try:
                with open(TRAINING_HISTORY_FILE, 'r') as f:
                    history = json.load(f)
            except:
                history = []
        
        # Add new training event to history
        history.append({
            'timestamp': timestamp,
            'datetime': datetime.now().isoformat(),
            'results': results,
            'samples_count': results.get('training_samples', 0)
        })
        
        # Save updated history
        with open(TRAINING_HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
        
        logger.info("Saved training history")
        return True
        
    except Exception as e:
        logger.error(f"Error saving models: {e}")
        return False

def retrain_models():
    """Main function to retrain models with feedback data"""
    logger.info("Starting model retraining process")
    
    # Load feedback data
    feedback_df = load_existing_feedback()
    
    if feedback_df.empty:
        logger.warning("No feedback data available for retraining")
        return False
    
    logger.info(f"Loaded {len(feedback_df)} feedback entries")
    
    # Load original dataset
    original_df = load_original_data()
    if original_df is not None:
        logger.info(f"Loaded original dataset with {len(original_df)} samples")
    
    # Combine datasets
    combined_df = combine_datasets(original_df, feedback_df)
    logger.info(f"Combined dataset has {len(combined_df)} samples")
    
    # Train models
    models, results = train_and_evaluate_models(combined_df)
    
    if not models or not results:
        logger.error("Model training failed")
        return False
    
    # Add sample count to results
    results['training_samples'] = len(combined_df)
    
    # Save models
    success = save_models(models, results)
    
    if success:
        logger.info("Model retraining completed successfully")
        return True
    else:
        logger.error("Failed to save retrained models")
        return False

if __name__ == "__main__":
    # Run retraining
    retrain_models()
