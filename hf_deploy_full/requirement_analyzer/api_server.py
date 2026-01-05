"""
REST API for software effort estimation service
"""

import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from effort_estimation_service import EffortEstimationService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api_server.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("EstimationAPI")

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the effort estimation service
try:
    estimation_service = EffortEstimationService(models_dir='models')
    logger.info("Effort Estimation Service initialized successfully")
except Exception as e:
    logger.error(f"Error initializing Effort Estimation Service: {e}")
    raise

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({"status": "ok", "message": "Service is running"}), 200

@app.route('/api/estimate', methods=['POST'])
def estimate_effort():
    """
    Estimate effort based on requirements text
    """
    try:
        data = request.json
        
        # Validate input
        if not data or 'requirements' not in data:
            return jsonify({"error": "Missing requirements text"}), 400
        
        requirements_text = data['requirements']
        estimation_method = data.get('method', 'auto')
        unit = data.get('unit', 'person_months')
        
        # Get estimation
        result = estimation_service.estimate_effort(
            requirements_text=requirements_text,
            estimation_method=estimation_method,
            unit=unit
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in effort estimation endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/team', methods=['POST'])
def suggest_team():
    """
    Suggest team composition based on requirements
    """
    try:
        data = request.json
        
        # Validate input
        if not data or 'requirements' not in data:
            return jsonify({"error": "Missing requirements text"}), 400
        
        requirements_text = data['requirements']
        
        # Get team suggestion
        result = estimation_service.suggest_team_composition(requirements_text)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in team suggestion endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/breakdown', methods=['POST'])
def get_effort_breakdown():
    """
    Get effort breakdown by phase and component
    """
    try:
        data = request.json
        
        # Validate input
        if not data or 'requirements' not in data:
            return jsonify({"error": "Missing requirements text"}), 400
        
        requirements_text = data['requirements']
        
        # Get effort breakdown
        result = estimation_service.generate_effort_breakdown(requirements_text)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in effort breakdown endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/report', methods=['POST'])
def get_estimation_report():
    """
    Get comprehensive estimation report
    """
    try:
        data = request.json
        
        # Validate input
        if not data or 'requirements' not in data:
            return jsonify({"error": "Missing requirements text"}), 400
        
        requirements_text = data['requirements']
        project_name = data.get('project_name', 'Software Project')
        
        # Get estimation report
        result = estimation_service.generate_estimation_report(
            requirements_text=requirements_text,
            project_name=project_name
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in estimation report endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_requirements():
    """
    Analyze requirements text
    """
    try:
        data = request.json
        
        # Validate input
        if not data or 'requirements' not in data:
            return jsonify({"error": "Missing requirements text"}), 400
        
        requirements_text = data['requirements']
        
        # Analyze requirements
        result = estimation_service.analyzer.analyze_requirements_document(requirements_text)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in requirements analysis endpoint: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
