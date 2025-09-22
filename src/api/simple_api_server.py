#!/usr/bin/env python3
"""
Simplified API for testing the effort estimation functionality
with feedback and self-improvement capabilities
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import json
import logging

# Add the project directory to the path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='api_server.log'
)
logger = logging.getLogger('api_server')

try:
    from src.analyzer.ml_requirement_analyzer import MLRequirementAnalyzer
    print("Successfully imported MLRequirementAnalyzer")
    
    # Import feedback related modules
    from src.feedback.feedback_api import register_feedback_api
    print("Successfully imported feedback modules")
except Exception as e:
    print(f"Error importing required modules: {e}")
    logger.error(f"Error importing required modules: {e}")
    sys.exit(1)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the analyzer
analyzer = MLRequirementAnalyzer()
print("MLRequirementAnalyzer initialized")

# Register feedback API routes
register_feedback_api(app)
print("Feedback API routes registered")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "Service is running"}), 200

@app.route('/api/analyze', methods=['POST'])
def analyze_requirements():
    """Analyze requirements text"""
    try:
        data = request.json
        
        # Validate input
        if not data or 'requirements' not in data:
            return jsonify({"error": "Missing requirements text"}), 400
        
        requirements_text = data['requirements']
        
        # Analyze requirements
        analysis = analyzer.analyze_requirements_document(requirements_text)
        
        # Return features
        return jsonify({
            "requirements_count": len(analysis['requirements']),
            "features": analysis['ml_features']
        }), 200
        
    except Exception as e:
        print(f"Error in requirements analysis endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/estimate', methods=['POST'])
def estimate_effort():
    """Estimate effort based on requirements text"""
    try:
        data = request.json
        
        # Validate input
        if not data or 'requirements' not in data:
            return jsonify({"error": "Missing requirements text"}), 400
        
        requirements_text = data['requirements']
        
        # Analyze requirements
        analysis = analyzer.analyze_requirements_document(requirements_text)
        
        # Use simple estimation formula (for demo purposes)
        # In a real system, this would use proper ML models
        features = analysis['ml_features']
        num_requirements = features.get('num_requirements', 0)
        complexity = features.get('complexity', 0)
        size_kloc = features.get('size_kloc', 0)
        
        # Simple effort formula
        effort_months = (num_requirements * 0.5) + (complexity * 5) + (size_kloc * 10)
        
        return jsonify({
            "requirements_count": num_requirements,
            "estimated_effort": {
                "person_months": round(effort_months, 2),
                "person_days": round(effort_months * 22, 2),  # Assuming 22 working days per month
                "confidence": 0.8
            },
            "complexity_factors": {
                "technical_complexity": complexity,
                "size": size_kloc
            }
        }), 200
        
    except Exception as e:
        print(f"Error in effort estimation endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/team', methods=['POST'])
def suggest_team():
    """Suggest team composition based on requirements"""
    try:
        data = request.json
        
        # Validate input
        if not data or 'requirements' not in data:
            return jsonify({"error": "Missing requirements text"}), 400
        
        requirements_text = data['requirements']
        
        # Analyze requirements
        analysis = analyzer.analyze_requirements_document(requirements_text)
        
        # Extract technologies (for demo purposes)
        features = analysis['ml_features']
        num_requirements = features.get('num_requirements', 0)
        
        # Simple team suggestion based on detected technologies
        team = {
            "backend_developers": 2,
            "frontend_developers": 2,
            "qa_engineers": 1,
            "devops_engineers": 1,
            "project_manager": 1
        }
        
        # Adjust based on project size
        if num_requirements > 10:
            team["backend_developers"] += 1
            team["frontend_developers"] += 1
            team["qa_engineers"] += 1
        
        return jsonify({
            "team_composition": team,
            "total_team_size": sum(team.values()),
            "estimated_duration_months": round((num_requirements * 0.5) / sum(team.values()), 2)
        }), 200
        
    except Exception as e:
        print(f"Error in team suggestion endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/feedback-overview', methods=['GET'])
def feedback_overview():
    """Provide an overview of collected feedback and model improvements"""
    try:
        from src.feedback.feedback_collector import get_feedback_statistics
        
        stats = get_feedback_statistics()
        
        # Add some additional insights
        insights = []
        
        if stats['total_feedback'] > 0:
            if stats['avg_estimation_error'] > 25:
                insights.append("High estimation error detected. Models may need improvement.")
            elif stats['avg_estimation_error'] < 10:
                insights.append("Low estimation error. Models are performing well.")
                
            insights.append(f"Collected feedback from {stats['total_feedback']} projects/tasks.")
            
            if 'last_feedback' in stats and stats['last_feedback']:
                insights.append(f"Last feedback received on {stats['last_feedback'][:10]}.")
        else:
            insights.append("No feedback data collected yet.")
        
        return jsonify({
            "statistics": stats,
            "insights": insights,
            "models": {
                "retrained": os.path.exists(os.path.join("models", "retrained")),
                "last_training": get_last_training_date()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in feedback overview endpoint: {e}")
        return jsonify({"error": str(e)}), 500

def get_last_training_date():
    """Get the date of the last model retraining"""
    try:
        history_file = os.path.join("models", "retrained", "training_history.json")
        
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
                if history:
                    return history[-1].get('datetime', 'Unknown')
        
        return None
    except Exception:
        return None

if __name__ == "__main__":
    print("Starting simplified API server with feedback capabilities...")
    print("Available API endpoints:")
    print(" - /api/health - Health check")
    print(" - /api/analyze - Analyze requirements")
    print(" - /api/estimate - Estimate effort")
    print(" - /api/team - Suggest team composition")
    print(" - /api/feedback - Submit feedback on actual effort")
    print(" - /api/feedback/stats - Get feedback statistics")
    print(" - /api/feedback-overview - Get feedback overview and insights")
    app.run(debug=True, host='0.0.0.0', port=5000)
