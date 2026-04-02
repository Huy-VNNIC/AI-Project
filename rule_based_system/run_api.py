#!/usr/bin/env python3
"""
FastAPI wrapper for Rule-Based Test Generator with correct imports.
This runs on port 8001.
"""

import sys
import os

# Fix imports for rule_based_system
rule_based_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, rule_based_dir)
os.chdir(rule_based_dir)

# Now import the app
from main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
