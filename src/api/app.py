"""
Main application file for Hugging Face deployment
"""

import os
from flask import Flask, request, jsonify, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
import sys
from pathlib import Path

# Add project directory to path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

# Import project modules
from feedback_api import register_feedback_api
from feedback_collector import get_feedback_statistics
import cocomo_ii_predictor
import feedback_feature_extractor

# Import requirement analyzer modules
from requirement_analyzer.analyzer import RequirementAnalyzer
from requirement_analyzer.estimator import EffortEstimator
from requirement_analyzer.api import app as req_analyzer_app

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ai_estimation_service")

# Create the Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Register the feedback API
register_feedback_api(app)

@app.route('/')
def home():
    """Home page route, can serve a simple UI or documentation"""
    stats = get_feedback_statistics()
    return render_template('index.html', stats=stats)

@app.route('/requirement-analyzer')
def requirement_analyzer():
    """Redirect to requirement analyzer UI"""
    return """
    <html>
        <head>
            <meta http-equiv="refresh" content="0;url=/requirement-analyzer/ui" />
            <title>Redirecting to Requirement Analyzer</title>
        </head>
        <body>
            <p>Redirecting to Requirement Analyzer...</p>
            <p><a href="/requirement-analyzer/ui">Click here if you are not redirected.</a></p>
        </body>
    </html>
    """

@app.route('/api/estimate', methods=['POST'])
def estimate_effort():
    """API endpoint to estimate effort based on requirements"""
    try:
        data = request.get_json()
        requirement_text = data.get('requirement_text')
        
        if not requirement_text:
            return jsonify({
                "success": False,
                "error": "No requirement text provided"
            }), 400
            
        # Extract features
        features = feedback_feature_extractor.extract_features_from_text(requirement_text)
        
        # Get predictions from multiple models
        predictions = cocomo_ii_predictor.predict_effort(features)
        
        return jsonify({
            "success": True,
            "predictions": predictions,
            "requirement_text": requirement_text
        })
        
    except Exception as e:
        logger.error(f"Error in estimation: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "ok"}), 200

# Import package downloader
from packages import download_packages

# Mount the requirement analyzer FastAPI app as a sub-application
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from fastapi.middleware.wsgi import WSGIMiddleware

# Function to create the application
def create_app():
    # Download required packages
    download_packages()
    
    # Mount the FastAPI app to a specific path
    fastapi_app = WSGIMiddleware(req_analyzer_app)
    application = DispatcherMiddleware(app, {
        '/requirement-analyzer/ui': fastapi_app
    })
    
    return application

if __name__ == "__main__":
    # Create the combined application
    application = create_app()
    
    # Start the server
    port = int(os.environ.get("PORT", 7860))
    
    # For Hugging Face deployment
    if os.environ.get('SPACE_HOST'):
        run_simple('0.0.0.0', port, application, use_reloader=False)
    else:
        # For local development
        run_simple('0.0.0.0', port, application, use_reloader=True)
