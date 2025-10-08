"""
Utility script for downloading NLTK data and configuring model paths
"""
import nltk
import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("package_setup")

def download_packages():
    """
    Downloads required NLTK packages and configures model paths
    """
    # Set NLTK data path from environment variable or use default
    nltk_data_dir = os.environ.get("NLTK_DATA", os.path.expanduser("~/nltk_data"))
    logger.info(f"Using NLTK data directory: {nltk_data_dir}")
    
    # Ensure the directory exists with proper permissions
    try:
        os.makedirs(nltk_data_dir, exist_ok=True)
    except PermissionError:
        logger.warning(f"Permission denied to create {nltk_data_dir}, using alternate location")
        nltk_data_dir = os.path.join(os.path.dirname(__file__), "nltk_data")
        os.makedirs(nltk_data_dir, exist_ok=True)
    
    nltk.data.path.append(nltk_data_dir)
    
    # Configure model paths
    setup_model_paths()
    
    # Download NLTK data
    packages = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger', 'punkt_tab', 'omw-1.4', 'vader_lexicon', 'maxent_ne_chunker', 'words']
    for package in packages:
        try:
            nltk.download(package, quiet=True, download_dir=nltk_data_dir)
            logger.info(f"Downloaded NLTK package: {package}")
        except Exception as e:
            logger.error(f"Error downloading package {package}: {e}")
    
    # Verify spaCy models
    logger.info("Verifying spaCy models...")
    try:
        import spacy
        import importlib
        
        # Check if spaCy model is available
        try:
            # Try to load model
            nlp = spacy.load("en_core_web_sm")
            logger.info(f"spaCy model 'en_core_web_sm' loaded successfully (version: {spacy.__version__})")
        except OSError:
            # If not available, try to download it
            logger.info("spaCy model not found, downloading...")
            try:
                import subprocess
                subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], 
                              check=True)
                logger.info("spaCy model downloaded successfully")
            except subprocess.SubprocessError as se:
                logger.error(f"Failed to download spaCy model via subprocess: {se}")
                # Try alternative method
                try:
                    import spacy.cli
                    spacy.cli.download("en_core_web_sm")
                    logger.info("spaCy model downloaded via spacy.cli")
                except Exception as e2:
                    logger.error(f"All attempts to download spaCy model failed: {e2}")
    except ImportError:
        logger.warning("spaCy not installed. Some features may not work properly.")
    except Exception as e:
        logger.error(f"Error verifying spaCy models: {e}")
    
def setup_model_paths():
    """
    Set up model paths and verify model files exist
    """
    # Determine model directory paths
    current_dir = Path(__file__).parent
    app_dir = current_dir / "app"
    models_dir = app_dir / "models"
    
    # Set MODEL_DIR environment variable if not already set
    if "MODEL_DIR" not in os.environ:
        os.environ["MODEL_DIR"] = str(models_dir)
        logger.info(f"MODEL_DIR set to: {models_dir}")
    
    # Check if models directory exists
    if not models_dir.exists():
        logger.warning(f"Models directory not found at {models_dir}. Creating directory.")
        os.makedirs(models_dir, exist_ok=True)
    
    # Check for critical model files
    critical_files = [
        "neural_network_model.h5",
        "nn_model.h5", 
        "feature_list.txt",
        "param_indices.json",
        "req_effort_connector.h5"
    ]
    
    cocomo_dir = models_dir / "cocomo_ii_extended"
    if not cocomo_dir.exists():
        logger.warning(f"COCOMO II models directory not found at {cocomo_dir}. Creating directory.")
        os.makedirs(cocomo_dir, exist_ok=True)
    
    missing_files = []
    for file in critical_files:
        if not (models_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        logger.warning(f"Missing model files: {', '.join(missing_files)}")
    else:
        logger.info("All critical model files found.")
    
    return models_dir

if __name__ == "__main__":
    download_packages()
