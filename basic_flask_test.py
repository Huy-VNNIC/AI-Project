#!/usr/bin/env python3
"""
Basic Flask server test
"""

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "Basic Flask server is running"}), 200

if __name__ == "__main__":
    print("Starting basic Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
