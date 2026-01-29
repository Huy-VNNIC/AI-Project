"""
Script to download required NLTK packages on startup
Run this script when deploying to Hugging Face
"""

import nltk
import os
import spacy

def download_packages():
    """Download required packages for the application"""
    print("Downloading NLTK packages...")
    
    # Download NLTK packages
    for package in ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']:
        try:
            nltk.download(package, quiet=True)
            print(f"Successfully downloaded NLTK package: {package}")
        except Exception as e:
            print(f"Error downloading NLTK package {package}: {e}")
    
    # Verify spaCy models
    print("Verifying spaCy models...")
    try:
        if not spacy.util.is_package("en_core_web_sm"):
            print("spaCy model not found, downloading...")
            os.system("python -m spacy download en_core_web_sm")
        else:
            print("spaCy model already installed")
    except Exception as e:
        print(f"Error verifying spaCy models: {e}")
    
    print("Package download process complete!")

if __name__ == "__main__":
    download_packages()
