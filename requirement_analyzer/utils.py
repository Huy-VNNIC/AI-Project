"""
Utility functions for the requirement analyzer API
"""

import re
from typing import Dict, Any

def preprocess_text_for_estimation(text: str) -> str:
    """
    Preprocess text to improve estimation quality:
    - Remove duplicate whitespaces
    - Normalize line breaks
    - Ensure proper section breaks
    - Extract LOC estimates if present more accurately
    """
    # Remove excessive whitespace and normalize line breaks
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Ensure headings are properly formatted for better section detection
    text = re.sub(r'([A-Za-z]+):\s*\n', r'\1:\n', text)
    
    # Better LOC extraction from text like "estimated at X lines of code" or "X LOC"
    loc_patterns = [
        r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:k|K)?\s*(?:lines of code|LOC)',
        r'code\s*size:?\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:k|K)?\s*(?:lines|LOC)',
        r'estimated\s*(?:at|to be)?\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:k|K)?\s*(?:lines of code|LOC)'
    ]
    
    for pattern in loc_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # If we find a LOC estimate, make it more prominent for the analyzer
            loc_value = match.group(1)
            # Clean up commas in numbers
            loc_value = loc_value.replace(',', '')
            
            # Check if it contains "k" or "K" suffix
            k_match = re.search(r'(\d+(?:\.\d+)?)\s*[kK]', match.group(0))
            if k_match:
                loc_value = str(float(k_match.group(1)) * 1000)
                
            # Add a clear marker for the LOC estimator
            text += f"\n\nExpected Size:\nEstimated code size: {loc_value} lines of code\n"
            break
    
    return text

def improve_confidence_level(result: Dict[str, Any], text: str) -> Dict[str, Any]:
    """
    Improve the confidence level of the estimation based on the quality 
    and quantity of the requirement text
    """
    if "estimation" not in result:
        return result
    
    # Default values
    current_confidence = result["estimation"].get("confidence_level", "Low")
    
    # Factors that improve confidence
    factors = {
        "text_length": len(text) > 1000,  # Longer text is generally more informative
        "has_loc_estimate": bool(re.search(r'\d+\s*(?:k|K)?\s*(?:lines of code|LOC)', text, re.IGNORECASE)),
        "has_sections": len(re.findall(r'\n\s*[A-Z][A-Za-z\s]+:?\s*\n', text)) > 3,
        "has_features": "features" in result.get("analysis", {}) and len(result["analysis"]["features"]) > 5,
        "has_requirements": "requirements" in result.get("analysis", {}) and len(result["analysis"]["requirements"]) > 5,
        "model_agreement": False  # Will calculate below
    }
    
    # Check if models broadly agree with each other
    if "model_estimates" in result["estimation"]:
        estimates = []
        for key, value in result["estimation"]["model_estimates"].items():
            # Get the actual estimate value
            if isinstance(value, dict):
                # New format: value is a dict with 'effort' key
                if "effort" in value:
                    estimates.append(value["effort"])
                # Old format: value is a dict with 'estimate' key
                elif "estimate" in value:
                    estimates.append(value["estimate"])
            elif isinstance(value, (int, float)):
                estimates.append(value)
                
        if estimates:
            # Calculate standard deviation relative to mean
            if len(estimates) > 1:
                import statistics
                mean = statistics.mean(estimates)
                if mean > 0:
                    stdev = statistics.stdev(estimates)
                    relative_stdev = stdev / mean
                    # If relative standard deviation is low, models agree
                    factors["model_agreement"] = relative_stdev < 0.5
    
    # Count positive factors
    positive_factors = sum(1 for factor in factors.values() if factor)
    
    # Adjust confidence level
    if positive_factors >= 5:
        new_confidence = "High"
    elif positive_factors >= 3:
        new_confidence = "Medium"
    else:
        new_confidence = "Low"
        
    # Update confidence level
    result["estimation"]["confidence_level"] = new_confidence
    
    # Add explanation about confidence factors
    confidence_explanation = {
        "confidence_factors": factors,
        "confidence_explanation": f"Confidence is {new_confidence} based on {positive_factors} positive factors out of {len(factors)}"
    }
    
    if "analysis" not in result:
        result["analysis"] = {}
        
    result["analysis"]["confidence"] = confidence_explanation
    
    return result