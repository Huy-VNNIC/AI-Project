"""
Feedback API handler for effort estimation models

This module provides API endpoints to collect feedback about actual effort
after projects are completed, enabling model improvement over time.
"""

import os
import sys
import logging
from datetime import datetime
import json
from flask import Blueprint, request, jsonify

# Add project directory to path if needed
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_dir not in sys.path:
    sys.path.append(project_dir)

from feedback_collector import add_feedback, get_feedback_statistics
import feedback_feature_extractor as feature_extractor
import model_retrainer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='feedback_api.log'
)
logger = logging.getLogger('feedback_api')

# Create Blueprint for feedback API
feedback_api = Blueprint('feedback_api', __name__)

@feedback_api.route('/feedback', methods=['POST'])
def submit_feedback():
    """
    API endpoint to submit feedback about actual effort after project completion
    
    Expected payload:
    {
        "project_id": "project123",
        "task_id": "task456",
        "requirement_text": "Implement user authentication system...",
        "estimated_effort": 2.5,
        "actual_effort": 3.0,
        "effort_unit": "PERSON_MONTH",  # One of: "HOUR", "DAY", "PERSON_MONTH"
        "model_used": "random_forest"   # Optional
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = [
            'project_id', 'task_id', 'requirement_text', 
            'estimated_effort', 'actual_effort', 'effort_unit'
        ]
        
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400
        
        # Extract features from requirement text
        features = feature_extractor.extract_features_from_text(data['requirement_text'])
        
        # Store feedback
        success = add_feedback(
            project_id=data['project_id'],
            task_id=data['task_id'],
            requirement_text=data['requirement_text'],
            estimated_effort=float(data['estimated_effort']),
            actual_effort=float(data['actual_effort']),
            effort_unit=data['effort_unit'],
            model_used=data.get('model_used'),
            features=features
        )
        
        if success:
            # Get updated statistics
            stats = get_feedback_statistics()
            
            # Trigger retraining if enough new data
            should_retrain = False
            retraining_result = None
            
            # Check if we have enough feedback for retraining
            # This could be based on a threshold or time since last training
            if stats['total_feedback'] >= 10:  # Adjust threshold as needed
                try:
                    # This would typically be done by a scheduled job,
                    # but for demo purposes we can trigger it here
                    should_retrain = True
                    retraining_result = model_retrainer.retrain_models()
                except Exception as e:
                    logger.error(f"Error during model retraining: {e}")
            
            return jsonify({
                "success": True,
                "message": "Feedback submitted successfully",
                "stats": stats,
                "retraining_triggered": should_retrain,
                "retraining_success": retraining_result
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to save feedback"
            }), 500
            
    except Exception as e:
        logger.error(f"Error processing feedback: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@feedback_api.route('/feedback/stats', methods=['GET'])
def get_stats():
    """API endpoint to get statistics about collected feedback"""
    try:
        stats = get_feedback_statistics()
        return jsonify({
            "success": True,
            "stats": stats
        })
    except Exception as e:
        logger.error(f"Error getting feedback statistics: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Function to register the blueprint with the main app
def register_feedback_api(app):
    """Register the feedback API blueprint with the Flask app"""
    app.register_blueprint(feedback_api, url_prefix='/api')
    logger.info("Feedback API registered")
