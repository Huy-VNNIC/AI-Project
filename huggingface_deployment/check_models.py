"""
Test script to verify model loading and paths
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("model_check")

def check_model_paths():
    """
    Check if model paths are correctly configured and models can be loaded
    """
    # Get model directory from environment or use default
    model_dir = os.environ.get("MODEL_DIR", None)
    if not model_dir:
        app_dir = Path(__file__).parent
        model_dir = app_dir / "app" / "models"
        os.environ["MODEL_DIR"] = str(model_dir)
    
    logger.info(f"Using MODEL_DIR: {model_dir}")
    
    # Check if critical model files exist
    model_files = [
        "neural_network_model.h5",
        "nn_model.h5",
        "feature_list.txt",
        "param_indices.json", 
        "req_effort_connector.h5"
    ]
    
    cocomo_models = [
        "cocomo_ii_extended/Random_Forest.joblib",
        "cocomo_ii_extended/Decision_Tree.joblib",
        "cocomo_ii_extended/Gradient_Boosting.joblib",
        "cocomo_ii_extended/Linear_Regression.joblib",
        "cocomo_ii_extended/preprocessor.joblib"
    ]
    
    missing_files = []
    
    # Check main model files
    for file in model_files:
        file_path = Path(model_dir) / file
        if not file_path.exists():
            missing_files.append(str(file_path))
            logger.warning(f"Missing model file: {file_path}")
        else:
            logger.info(f"Found model file: {file_path}")
    
    # Check COCOMO model files
    for file in cocomo_models:
        file_path = Path(model_dir) / file
        if not file_path.exists():
            missing_files.append(str(file_path))
            logger.warning(f"Missing COCOMO model file: {file_path}")
        else:
            logger.info(f"Found COCOMO model file: {file_path}")
    
    # Return results
    if missing_files:
        logger.error(f"Missing {len(missing_files)} model files")
        return False, missing_files
    else:
        logger.info("All model files are present")
        return True, []
    
def test_load_models():
    """
    Test loading models to verify they can be properly loaded
    """
    try:
        # Try importing required modules
        import tensorflow as tf
        import joblib
        import json
        
        # Get model directory
        model_dir = os.environ.get("MODEL_DIR")
        if not model_dir:
            logger.error("MODEL_DIR environment variable not set")
            return False
        
        # Try loading neural network model
        try:
            nn_model_path = Path(model_dir) / "nn_model.h5"
            if nn_model_path.exists():
                model = tf.keras.models.load_model(str(nn_model_path))
                logger.info(f"Successfully loaded neural network model from {nn_model_path}")
        except Exception as e:
            logger.error(f"Error loading neural network model: {str(e)}")
            return False
        
        # Try loading random forest model
        try:
            rf_model_path = Path(model_dir) / "cocomo_ii_extended" / "Random_Forest.joblib"
            if rf_model_path.exists():
                rf_model = joblib.load(rf_model_path)
                logger.info(f"Successfully loaded Random Forest model from {rf_model_path}")
        except Exception as e:
            logger.error(f"Error loading Random Forest model: {str(e)}")
            return False
            
        # Try loading param indices
        try:
            param_path = Path(model_dir) / "param_indices.json"
            if param_path.exists():
                with open(param_path, 'r') as f:
                    param_indices = json.load(f)
                logger.info(f"Successfully loaded parameter indices from {param_path}")
        except Exception as e:
            logger.error(f"Error loading parameter indices: {str(e)}")
            return False
            
        return True
            
    except Exception as e:
        logger.error(f"Error during model loading test: {str(e)}")
        return False
        
if __name__ == "__main__":
    logger.info("Running model checks...")
    success, missing_files = check_model_paths()
    
    if success:
        logger.info("All model files found.")
        if test_load_models():
            logger.info("Models loaded successfully!")
            sys.exit(0)
        else:
            logger.error("Error loading models.")
            sys.exit(1)
    else:
        logger.error(f"Missing model files: {', '.join(missing_files)}")
        sys.exit(1)