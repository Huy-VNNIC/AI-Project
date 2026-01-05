"""
Script to train and export machine learning models for software effort estimation
"""

import os
import sys
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import argparse
import logging
from ml_requirement_analyzer import MLRequirementAnalyzer
from model_integration import ModelTrainer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("model_training.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("ModelTraining")

def train_requirement_classifier(requirement_datasets, output_dir='models'):
    """
    Train requirement classifier models using the provided datasets
    
    Args:
        requirement_datasets (list): List of paths to requirement datasets
        output_dir (str): Directory to save trained models
    """
    logger.info(f"Training requirement classifier using {len(requirement_datasets)} datasets")
    
    # Create the requirement analyzer
    analyzer = MLRequirementAnalyzer()
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Train relevance model
    try:
        logger.info("Training relevance classifier...")
        relevance_model = analyzer.train_relevance_model(requirement_datasets)
        logger.info("Relevance classifier training completed")
        
        # Save model
        model_path = os.path.join(output_dir, 'relevance_model.pkl')
        joblib.dump(relevance_model, model_path)
        logger.info(f"Relevance model saved to {model_path}")
    except Exception as e:
        logger.error(f"Error training relevance classifier: {e}")
    
    # Train requirement type model
    try:
        logger.info("Training requirement type classifier...")
        req_type_model = analyzer.train_requirement_type_model(requirement_datasets)
        logger.info("Requirement type classifier training completed")
        
        # Save model
        model_path = os.path.join(output_dir, 'req_type_model.pkl')
        joblib.dump(req_type_model, model_path)
        logger.info(f"Requirement type model saved to {model_path}")
    except Exception as e:
        logger.error(f"Error training requirement type classifier: {e}")

def train_effort_estimation_models(effort_datasets, output_dir='models'):
    """
    Train effort estimation models using the provided datasets
    
    Args:
        effort_datasets (list): List of paths to effort estimation datasets
        output_dir (str): Directory to save trained models
    """
    logger.info(f"Training effort estimation models using {len(effort_datasets)} datasets")
    
    # Initialize model trainer
    trainer = ModelTrainer(save_dir=output_dir)
    
    # Process each dataset
    for dataset_path in effort_datasets:
        try:
            logger.info(f"Processing dataset: {dataset_path}")
            
            # Train all models on this dataset
            models = trainer.train_all_models(dataset_path)
            
            logger.info(f"Successfully trained {len(models)} models on {dataset_path}")
            
            # Evaluate models
            metrics = trainer.evaluate_models(dataset_path)
            
            # Log evaluation results
            logger.info(f"Model evaluation results for {dataset_path}:")
            for model_name, model_metrics in metrics.items():
                logger.info(f"  {model_name}:")
                for metric_name, metric_value in model_metrics.items():
                    logger.info(f"    {metric_name}: {metric_value:.4f}")
        except Exception as e:
            logger.error(f"Error processing dataset {dataset_path}: {e}")

def prepare_requirement_datasets():
    """
    Prepare a list of requirement datasets
    
    Returns:
        list: Paths to requirement datasets
    """
    # Look for requirement datasets in the standard location
    req_dataset_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Requirment_dataset')
    
    if not os.path.exists(req_dataset_dir):
        logger.warning(f"Requirement dataset directory not found: {req_dataset_dir}")
        return []
    
    # Find all ARFF and CSV files
    req_datasets = []
    
    for filename in os.listdir(req_dataset_dir):
        if filename.endswith('.arff') or filename.endswith('.csv'):
            req_datasets.append(os.path.join(req_dataset_dir, filename))
    
    logger.info(f"Found {len(req_datasets)} requirement datasets")
    return req_datasets

def prepare_effort_datasets():
    """
    Prepare a list of effort estimation datasets
    
    Returns:
        list: Paths to effort estimation datasets
    """
    # Look for effort estimation datasets in standard locations
    dataset_dirs = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'datasets'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Software-estimation-datasets'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'processed_data')
    ]
    
    effort_datasets = []
    
    for dataset_dir in dataset_dirs:
        if os.path.exists(dataset_dir):
            for filename in os.listdir(dataset_dir):
                if filename.endswith('.csv') or filename.endswith('.xlsx'):
                    effort_datasets.append(os.path.join(dataset_dir, filename))
    
    logger.info(f"Found {len(effort_datasets)} effort estimation datasets")
    return effort_datasets

def main():
    """
    Main function to train and export models
    """
    parser = argparse.ArgumentParser(description='Train and export machine learning models for software effort estimation')
    parser.add_argument('--output-dir', type=str, default='models',
                        help='Directory to save trained models')
    parser.add_argument('--req-datasets', type=str, nargs='+',
                        help='Paths to requirement datasets')
    parser.add_argument('--effort-datasets', type=str, nargs='+',
                        help='Paths to effort estimation datasets')
    parser.add_argument('--skip-req-models', action='store_true',
                        help='Skip training requirement classifier models')
    parser.add_argument('--skip-effort-models', action='store_true',
                        help='Skip training effort estimation models')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # Train requirement classifier models
    if not args.skip_req_models:
        req_datasets = args.req_datasets if args.req_datasets else prepare_requirement_datasets()
        
        if req_datasets:
            train_requirement_classifier(req_datasets, args.output_dir)
        else:
            logger.warning("No requirement datasets found. Skipping requirement classifier training.")
    
    # Train effort estimation models
    if not args.skip_effort_models:
        effort_datasets = args.effort_datasets if args.effort_datasets else prepare_effort_datasets()
        
        if effort_datasets:
            train_effort_estimation_models(effort_datasets, args.output_dir)
        else:
            logger.warning("No effort estimation datasets found. Skipping effort model training.")
    
    logger.info("Model training and export completed")

if __name__ == '__main__':
    main()
