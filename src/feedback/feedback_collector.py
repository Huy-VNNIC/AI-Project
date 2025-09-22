"""
Feedback Collector Module for Effort Estimation Models

This module handles collecting and storing feedback data about actual effort 
after project completion, which will be used for model retraining.
"""

import os
import json
import pandas as pd
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='feedback_collection.log'
)
logger = logging.getLogger('feedback_collector')

FEEDBACK_DIR = "datasets/feedback"
FEEDBACK_FILE = os.path.join(FEEDBACK_DIR, "feedback_data.csv")

def ensure_feedback_dir():
    """Ensure the feedback directory exists"""
    if not os.path.exists(FEEDBACK_DIR):
        os.makedirs(FEEDBACK_DIR)
        logger.info(f"Created feedback directory at {FEEDBACK_DIR}")

def load_existing_feedback():
    """Load existing feedback data or create a new DataFrame"""
    ensure_feedback_dir()
    
    if os.path.exists(FEEDBACK_FILE):
        try:
            return pd.read_csv(FEEDBACK_FILE)
        except Exception as e:
            logger.error(f"Error loading feedback data: {e}")
            return pd.DataFrame(columns=[
                'project_id', 'task_id', 'requirement_text', 
                'estimated_effort', 'actual_effort', 'effort_unit',
                'model_used', 'features', 'timestamp'
            ])
    else:
        return pd.DataFrame(columns=[
            'project_id', 'task_id', 'requirement_text', 
            'estimated_effort', 'actual_effort', 'effort_unit',
            'model_used', 'features', 'timestamp'
        ])

def save_feedback(feedback_df):
    """Save feedback data to CSV file"""
    ensure_feedback_dir()
    try:
        feedback_df.to_csv(FEEDBACK_FILE, index=False)
        logger.info(f"Saved feedback data to {FEEDBACK_FILE}")
        return True
    except Exception as e:
        logger.error(f"Error saving feedback data: {e}")
        return False

def add_feedback(project_id, task_id, requirement_text, estimated_effort, 
                actual_effort, effort_unit, model_used=None, features=None):
    """
    Add new feedback entry to the collection
    
    Args:
        project_id (str): Project identifier
        task_id (str): Task identifier
        requirement_text (str): The original requirement text
        estimated_effort (float): The estimated effort value
        actual_effort (float): The actual effort reported by user
        effort_unit (str): Unit of effort (HOUR, DAY, PERSON_MONTH)
        model_used (str, optional): Name of the model used for estimation
        features (dict, optional): Features extracted from the requirement
        
    Returns:
        bool: True if feedback was successfully added
    """
    # Load existing feedback
    feedback_df = load_existing_feedback()
    
    # Create new feedback entry
    new_feedback = {
        'project_id': project_id,
        'task_id': task_id,
        'requirement_text': requirement_text,
        'estimated_effort': estimated_effort,
        'actual_effort': actual_effort,
        'effort_unit': effort_unit,
        'model_used': model_used if model_used else 'unknown',
        'features': json.dumps(features) if features else '{}',
        'timestamp': datetime.now().isoformat()
    }
    
    # Add to DataFrame
    feedback_df = feedback_df._append(new_feedback, ignore_index=True)
    
    # Save updated feedback
    success = save_feedback(feedback_df)
    
    if success:
        logger.info(f"Added feedback for task {task_id} in project {project_id}")
    
    return success

def get_feedback_statistics():
    """Get statistics about collected feedback"""
    feedback_df = load_existing_feedback()
    
    if feedback_df.empty:
        return {
            "total_feedback": 0,
            "avg_estimation_error": 0,
            "last_feedback": None
        }
    
    # Calculate error metrics
    feedback_df['error'] = feedback_df['estimated_effort'] - feedback_df['actual_effort']
    feedback_df['error_percent'] = (feedback_df['error'] / feedback_df['actual_effort']) * 100
    
    stats = {
        "total_feedback": len(feedback_df),
        "avg_estimation_error": feedback_df['error_percent'].mean(),
        "median_error": feedback_df['error_percent'].median(),
        "last_feedback": feedback_df['timestamp'].max()
    }
    
    return stats

if __name__ == "__main__":
    # Simple test
    ensure_feedback_dir()
    print(f"Feedback directory: {FEEDBACK_DIR}")
    df = load_existing_feedback()
    print(f"Current feedback entries: {len(df)}")
