#!/usr/bin/env python3
"""
Simplified API for testing the effort estimation functionality
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add the project directory to the path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    from requirement_analyzer.ml_requirement_analyzer import MLRequirementAnalyzer
    print("Successfully imported MLRequirementAnalyzer")
except Exception as e:
    print(f"Error importing MLRequirementAnalyzer: {e}")
    sys.exit(1)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the analyzer
analyzer = MLRequirementAnalyzer()
print("MLRequirementAnalyzer initialized")

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

if __name__ == "__main__":
    print("Starting simplified API server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
