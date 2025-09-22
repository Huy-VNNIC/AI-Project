"""
Extract features from requirement text for feedback-based retraining

This module extracts features from requirement text provided as feedback
to enable model retraining with actual effort data.
"""

import re
import os
import pandas as pd
import numpy as np
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='feature_extraction.log'
)
logger = logging.getLogger('feedback_feature_extractor')

# Ensure NLTK resources are downloaded
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

def count_words(text):
    """Count the number of words in the text"""
    if not text:
        return 0
    words = word_tokenize(text)
    return len(words)

def count_unique_words(text):
    """Count the number of unique words in the text"""
    if not text:
        return 0
    words = word_tokenize(text.lower())
    return len(set(words))

def count_sentences(text):
    """Count the number of sentences in the text"""
    if not text:
        return 0
    sentences = sent_tokenize(text)
    return len(sentences)

def calculate_avg_sentence_length(text):
    """Calculate the average sentence length in words"""
    if not text:
        return 0
    sentences = sent_tokenize(text)
    if not sentences:
        return 0
    word_counts = [len(word_tokenize(sentence)) for sentence in sentences]
    return sum(word_counts) / len(word_counts)

def count_technical_terms(text):
    """Count technical terms in the text"""
    if not text:
        return 0
    
    # Example technical terms - expand this list as needed
    technical_terms = [
        'api', 'interface', 'database', 'server', 'client', 'endpoint', 
        'authentication', 'authorization', 'encryption', 'security',
        'algorithm', 'function', 'method', 'class', 'object', 'integration',
        'sync', 'async', 'frontend', 'backend', 'middleware', 'service',
        'component', 'module', 'library', 'framework', 'responsive', 'cache',
        'optimization', 'performance', 'scale', 'load', 'testing', 'deployment',
        'continuous integration', 'continuous deployment', 'ci/cd', 'docker',
        'kubernetes', 'container', 'microservice', 'cloud', 'saas', 'paas', 'iaas',
        'architecture', 'design pattern', 'websocket', 'api gateway', 'orm',
        'rest', 'graphql', 'oauth', 'jwt', 'token', 'session', 'cookie'
    ]
    
    text_lower = text.lower()
    count = sum(1 for term in technical_terms if term in text_lower)
    return count

def count_action_verbs(text):
    """Count action verbs in the text"""
    if not text:
        return 0
    
    # Example action verbs - expand this list as needed
    action_verbs = [
        'implement', 'develop', 'create', 'design', 'build', 'integrate', 
        'test', 'validate', 'deploy', 'configure', 'modify', 'update',
        'enhance', 'optimize', 'refactor', 'migrate', 'support', 'provide',
        'maintain', 'monitor', 'analyze', 'assess', 'evaluate', 'improve',
        'secure', 'backup', 'restore', 'generate', 'process', 'transform',
        'convert', 'extract', 'load', 'visualize', 'display', 'render'
    ]
    
    text_lower = text.lower()
    tokens = word_tokenize(text_lower)
    count = sum(1 for token in tokens if token in action_verbs)
    return count

def extract_features_from_text(text):
    """Extract all relevant features from requirement text"""
    if not text:
        return {}
    
    features = {}
    
    try:
        # Basic text statistics
        features['word_count'] = count_words(text)
        features['unique_word_count'] = count_unique_words(text)
        features['sentence_count'] = count_sentences(text)
        features['avg_sentence_length'] = calculate_avg_sentence_length(text)
        
        # Complexity indicators
        features['technical_term_count'] = count_technical_terms(text)
        features['action_verb_count'] = count_action_verbs(text)
        
        # Advanced features
        stop_words = set(stopwords.words('english'))
        words = word_tokenize(text.lower())
        content_words = [w for w in words if w.isalnum() and w not in stop_words]
        
        features['content_word_count'] = len(content_words)
        features['content_density'] = len(content_words) / max(1, features['word_count'])
        
        # UI related indicators
        ui_terms = ['screen', 'page', 'form', 'button', 'field', 'input', 'display',
                   'layout', 'interface', 'view', 'dashboard', 'report', 'chart', 'graph']
        features['ui_term_count'] = sum(1 for term in ui_terms if term in text.lower())
        
        # Data processing indicators
        data_terms = ['database', 'data', 'record', 'file', 'storage', 'table', 'column', 
                     'query', 'export', 'import', 'format', 'schema', 'model']
        features['data_term_count'] = sum(1 for term in data_terms if term in text.lower())
        
        # Integration indicators
        integration_terms = ['api', 'integration', 'connect', 'external', 'third-party',
                           'service', 'endpoint', 'request', 'response']
        features['integration_term_count'] = sum(1 for term in integration_terms if term in text.lower())
        
    except Exception as e:
        logger.error(f"Error extracting features: {e}")
        return {}
    
    return features

def process_requirement_text(text):
    """Process a single requirement text and return features"""
    features = extract_features_from_text(text)
    return features

if __name__ == "__main__":
    # Test with a sample requirement
    sample_text = """
    Implement a user authentication system with login and registration functionality.
    The system should support email verification and password reset features.
    Users should be able to update their profile information including name, email, and profile picture.
    The interface should be responsive and work on mobile devices.
    """
    
    features = process_requirement_text(sample_text)
    print("Extracted features:")
    for key, value in features.items():
        print(f"{key}: {value}")
