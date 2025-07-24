#!/usr/bin/env python3
"""
Minimal API for testing the effort estimation service
"""

from flask import Flask, request, jsonify

# Initialize Flask app
app = Flask(__name__)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "Service is running"}), 200

@app.route('/api/estimate', methods=['POST'])
def estimate_effort():
    """Minimal effort estimation endpoint"""
    try:
        data = request.json
        
        # Validate input
        if not data or 'requirements' not in data:
            return jsonify({"error": "Missing requirements text"}), 400
        
        requirements_text = data['requirements']
        num_requirements = len(requirements_text.split('.'))
        
        # Simple estimation formula
        effort_months = num_requirements * 0.5
        
        return jsonify({
            "requirements_count": num_requirements,
            "estimated_effort": {
                "person_months": round(effort_months, 2),
                "person_days": round(effort_months * 22, 2),
                "confidence": 0.8
            },
            "complexity_factors": {
                "technical_complexity": 0.7,
                "size": 0.5
            }
        }), 200
        
    except Exception as e:
        print(f"Error in effort estimation endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/team', methods=['POST'])
def suggest_team():
    """Minimal team suggestion endpoint"""
    try:
        data = request.json
        
        # Validate input
        if not data or 'requirements' not in data:
            return jsonify({"error": "Missing requirements text"}), 400
        
        requirements_text = data['requirements']
        num_requirements = len(requirements_text.split('.'))
        
        # Simple team suggestion
        team = {
            "backend_developers": 2,
            "frontend_developers": 2,
            "qa_engineers": 1,
            "devops_engineers": 1,
            "project_manager": 1
        }
        
        return jsonify({
            "team_composition": team,
            "total_team_size": sum(team.values()),
            "estimated_duration_months": round(num_requirements * 0.5 / sum(team.values()), 2)
        }), 200
        
    except Exception as e:
        print(f"Error in team suggestion endpoint: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Starting minimal API server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
