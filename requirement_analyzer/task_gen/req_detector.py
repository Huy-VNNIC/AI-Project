"""
Requirement Detector - inference module
Load trained model và detect requirements từ sentences
"""
import joblib
import numpy as np
from pathlib import Path
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class RequirementDetector:
    """Detect whether a sentence is a requirement"""
    
    def __init__(self, model_dir: Path):
        self.model_dir = Path(model_dir)
        self.vectorizer = None
        self.model = None
        self.loaded = False
    
    def load(self):
        """Load trained models"""
        try:
            vec_path = self.model_dir / 'requirement_detector_vectorizer.joblib'
            model_path = self.model_dir / 'requirement_detector_model.joblib'
            
            if not vec_path.exists() or not model_path.exists():
                logger.warning(f"Requirement detector models not found in {self.model_dir}")
                return False
            
            self.vectorizer = joblib.load(vec_path)
            self.model = joblib.load(model_path)
            self.loaded = True
            
            logger.info(f"✓ Loaded requirement detector from {self.model_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading requirement detector: {e}")
            return False
    
    def detect(
        self,
        texts: List[str],
        threshold: float = 0.5,
        return_proba: bool = True
    ) -> List[Tuple[bool, float]]:
        """
        Detect requirements from list of texts
        
        Args:
            texts: List of text strings
            threshold: Probability threshold for classification
            return_proba: Whether to return probabilities
        
        Returns:
            List of (is_requirement, confidence) tuples
        """
        if not self.loaded:
            logger.warning("Model not loaded, attempting to load...")
            if not self.load():
                # Return default: all are requirements with low confidence
                return [(True, 0.5) for _ in texts]
        
        try:
            # Vectorize
            X = self.vectorizer.transform(texts)
            
            # Predict probabilities
            probas = self.model.predict_proba(X)
            
            # Extract probability of class 1 (is_requirement)
            req_probas = probas[:, 1]
            
            # Apply threshold
            predictions = req_probas >= threshold
            
            if return_proba:
                return list(zip(predictions, req_probas))
            else:
                return list(zip(predictions, [1.0 if p else 0.0 for p in predictions]))
                
        except Exception as e:
            logger.error(f"Error during detection: {e}")
            return [(True, 0.5) for _ in texts]
    
    def detect_single(self, text: str, threshold: float = 0.5) -> Tuple[bool, float]:
        """Detect single text"""
        result = self.detect([text], threshold=threshold)
        return result[0]
    
    def get_top_features(self, text: str, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Get top features contributing to classification
        Useful for debugging/explainability
        """
        if not self.loaded:
            return []
        
        try:
            # Get feature names
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Transform text
            X = self.vectorizer.transform([text])
            
            # Get feature weights (for logistic regression)
            if hasattr(self.model, 'coef_'):
                weights = self.model.coef_[0]
            else:
                # For calibrated models, get base estimator
                if hasattr(self.model, 'base_estimator'):
                    weights = self.model.base_estimator.coef_[0]
                else:
                    return []
            
            # Get non-zero features in this text
            non_zero = X.nonzero()[1]
            
            # Get scores for non-zero features
            scores = [(feature_names[i], weights[i] * X[0, i]) for i in non_zero]
            
            # Sort by absolute value
            scores.sort(key=lambda x: abs(x[1]), reverse=True)
            
            return scores[:top_n]
            
        except Exception as e:
            logger.error(f"Error getting top features: {e}")
            return []


# Singleton instance
_detector = None
_detector_model_dir = None

def get_detector(model_dir: Path = None) -> RequirementDetector:
    """Get singleton detector instance"""
    global _detector, _detector_model_dir
    
    if model_dir is None:
        # Default path
        from pathlib import Path
        import sys
        project_root = Path(__file__).parent.parent.parent
        model_dir = project_root / 'models' / 'task_gen'
    
    # Reload if model dir changed
    if _detector is None or _detector_model_dir != model_dir:
        _detector = RequirementDetector(model_dir)
        _detector.load()
        _detector_model_dir = model_dir
    
    return _detector
