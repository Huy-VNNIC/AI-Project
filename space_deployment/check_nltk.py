"""
Utility to check NLTK data installation
"""
import os
import sys
import nltk

def check_nltk_data():
    """
    Check if NLTK data is properly installed and configure paths
    """
    # Check NLTK_DATA environment variable
    nltk_data_dir = os.environ.get("NLTK_DATA")
    if nltk_data_dir:
        print(f"NLTK_DATA environment variable is set to: {nltk_data_dir}")
        nltk.data.path.insert(0, nltk_data_dir)
    
    # Add additional search paths
    home_nltk = os.path.expanduser("~/nltk_data")
    app_nltk = os.path.join(os.path.dirname(__file__), "nltk_data")
    
    for path in [home_nltk, app_nltk, "/home/appuser/nltk_data"]:
        if path not in nltk.data.path:
            nltk.data.path.append(path)
    
    # Check if punkt is available
    print("NLTK data search paths:", nltk.data.path)
    
    try:
        nltk.data.find('tokenizers/punkt')
        print("✓ NLTK punkt tokenizer is available")
        return True
    except LookupError:
        print("✗ NLTK punkt tokenizer is NOT available")
        print("Attempting to download to current directory...")
        try:
            nltk.download('punkt', download_dir=app_nltk)
            return True
        except:
            print("Failed to download NLTK data")
            return False

if __name__ == "__main__":
    check_nltk_data()