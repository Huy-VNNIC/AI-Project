#!/usr/bin/env python3
"""
Initialization script for NLTK data
Run this before starting the application
"""

import os
import nltk

# Set NLTK data path
nltk.data.path.append('/usr/local/nltk_data')

def initialize_nltk():
    """Initialize NLTK data if needed"""
    resources = [
        ('tokenizers/punkt', 'punkt'),
        ('corpora/stopwords', 'stopwords'), 
        ('corpora/wordnet', 'wordnet'),
        ('corpora/omw-1.4', 'omw-1.4')
    ]
    
    for path, name in resources:
        try:
            nltk.data.find(path)
            print(f"✓ NLTK resource {name} found")
        except LookupError:
            print(f"✗ NLTK resource {name} not found, attempting download...")
            try:
                nltk.download(name, download_dir='/usr/local/nltk_data')
                print(f"✓ NLTK resource {name} downloaded")
            except Exception as e:
                print(f"✗ Failed to download {name}: {e}")

if __name__ == "__main__":
    initialize_nltk()