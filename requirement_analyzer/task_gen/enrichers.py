"""
Enrichers - Multi-class classifiers for type/priority/domain/role
"""
import joblib
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging
import re

logger = logging.getLogger(__name__)


class LabelEnricher:
    """Multi-class classifier for a specific label"""
    
    def __init__(self, label_name: str, model_dir: Path):
        self.label_name = label_name
        self.model_dir = Path(model_dir)
        self.vectorizer = None
        self.model = None
        self.classes = []
        self.loaded = False
    
    def load(self) -> bool:
        """Load trained model"""
        try:
            vec_path = self.model_dir / f'{self.label_name}_vectorizer.joblib'
            model_path = self.model_dir / f'{self.label_name}_model.joblib'
            classes_path = self.model_dir / f'{self.label_name}_classes.json'
            
            if not all(p.exists() for p in [vec_path, model_path, classes_path]):
                logger.warning(f"{self.label_name} enricher models not found in {self.model_dir}")
                return False
            
            self.vectorizer = joblib.load(vec_path)
            self.model = joblib.load(model_path)
            
            with open(classes_path, 'r') as f:
                self.classes = json.load(f)
            
            self.loaded = True
            logger.info(f"✓ Loaded {self.label_name} enricher ({len(self.classes)} classes)")
            return True
            
        except Exception as e:
            logger.error(f"Error loading {self.label_name} enricher: {e}")
            return False
    
    def predict(
        self,
        texts: List[str],
        return_proba: bool = True
    ) -> List[Tuple[str, float]]:
        """
        Predict labels for texts
        
        Returns:
            List of (label, confidence) tuples
        """
        if not self.loaded:
            if not self.load():
                # Return defaults
                default_label = self._get_default_label()
                return [(default_label, 0.5) for _ in texts]
        
        try:
            # Vectorize
            X = self.vectorizer.transform(texts)
            
            # Predict
            predictions = self.model.predict(X)
            
            if return_proba:
                # Get probabilities
                probas = self.model.predict_proba(X)
                # Get max probability for predicted class
                confidences = probas.max(axis=1)
            else:
                confidences = [1.0] * len(texts)
            
            return list(zip(predictions, confidences))
            
        except Exception as e:
            logger.error(f"Error predicting {self.label_name}: {e}")
            default_label = self._get_default_label()
            return [(default_label, 0.5) for _ in texts]
    
    def predict_single(self, text: str) -> Tuple[str, float]:
        """Predict single text"""
        result = self.predict([text])
        return result[0]
    
    def _get_default_label(self) -> str:
        """Get default label if model fails"""
        defaults = {
            'type': 'functional',
            'priority': 'Medium',
            'domain': 'general'
        }
        return defaults.get(self.label_name, 'unknown')


class RoleAssigner:
    """
    Rule-based role assignment
    Can be upgraded to ML model later when we have labeled data
    """
    
    def __init__(self):
        # Keyword patterns for role detection
        self.role_patterns = {
            'Frontend': [
                r'\bui\b', r'\buser interface\b', r'\bgui\b', r'\bweb\b', r'\bmobile\b',
                r'\bscreen\b', r'\bpage\b', r'\bform\b', r'\bdialog\b', r'\bmenu\b',
                r'\bbutton\b', r'\bfield\b', r'\bview\b', r'\bdashboard\b',
                r'\bdisplay\b', r'\brender\b', r'\binteract\b', r'\bresponsive\b',
                r'\breact\b', r'\bangular\b', r'\bvue\b', r'\bhtml\b', r'\bcss\b'
            ],
            'Backend': [
                r'\bapi\b', r'\bserver\b', r'\bservice\b', r'\bauth', r'\bdatabase\b',
                r'\bdb\b', r'\bquery\b', r'\bsql\b', r'\bcrud\b', r'\bcache\b',
                r'\bprocess\b', r'\bcalculate\b', r'\bvalidate\b', r'\bgenerate\b',
                r'\bstore\b', r'\bretrieve\b', r'\bupdate\b', r'\bdelete\b',
                r'\blogic\b', r'\bbusiness rule\b', r'\bworkflow\b', r'\bpipeline\b'
            ],
            'Data': [
                r'\bdata\b', r'\bdatabase\b', r'\btable\b', r'\bschema\b', r'\bindex\b',
                r'\bmigration\b', r'\betl\b', r'\bwarehouse\b', r'\bdataset\b',
                r'\breport', r'\banalytics\b', r'\bmetrics\b', r'\bstatistics\b',
                r'\baggregat', r'\bquery optimiz'
            ],
            'Security': [
                r'\bsecur', r'\bauth', r'\bencrypt', r'\bpermission\b', r'\baccess control\b',
                r'\blogin\b', r'\blogout\b', r'\bpassword\b', r'\btoken\b', r'\bjwt\b',
                r'\boauth\b', r'\bsso\b', r'\brole\b', r'\bprivilege\b',
                r'\bprotect\b', r'\bfirewall\b', r'\bssl\b', r'\btls\b', r'\bhttps\b',
                r'\bvulnerability\b', r'\bthreat\b', r'\battack\b', r'\baudit\b'
            ],
            'QA': [
                r'\btest', r'\bvalidat', r'\bverif', r'\bcheck\b', r'\bassert\b',
                r'\bquality\b', r'\bqa\b', r'\bautomation\b', r'\bunit test\b',
                r'\bintegration test\b', r'\bregression\b', r'\bbug\b', r'\bdefect\b'
            ],
            'DevOps': [
                r'\bdeploy', r'\bci/cd\b', r'\bjenkins\b', r'\bdocker\b', r'\bkubernetes\b',
                r'\bcontainer\b', r'\bpipeline\b', r'\binfrastructure\b', r'\bmonitoring\b',
                r'\bscaling\b', r'\bload balanc', r'\bcloud\b', r'\baws\b', r'\bazure\b',
                r'\bgcp\b', r'\bk8s\b', r'\bgit\b'
            ]
        }
        
        # Compile patterns
        self.compiled_patterns = {
            role: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            for role, patterns in self.role_patterns.items()
        }
    
    def assign(self, text: str, req_type: Optional[str] = None) -> str:
        """
        Assign role based on text content and requirement type
        
        Args:
            text: Requirement text
            req_type: Requirement type (functional, security, interface, data, etc.)
        
        Returns:
            Role name
        """
        text_lower = text.lower()
        
        # Score each role based on keyword matches
        scores = {}
        for role, patterns in self.compiled_patterns.items():
            score = sum(1 for pattern in patterns if pattern.search(text_lower))
            if score > 0:
                scores[role] = score
        
        # Type-based hints
        type_role_hints = {
            'interface': 'Frontend',
            'ui': 'Frontend',
            'data': 'Data',
            'database': 'Data',
            'security': 'Security',
            'performance': 'DevOps',
            'deployment': 'DevOps'
        }
        
        if req_type:
            type_lower = req_type.lower()
            for key, role in type_role_hints.items():
                if key in type_lower:
                    scores[role] = scores.get(role, 0) + 2  # bonus for type match
        
        # Get role with highest score
        if scores:
            best_role = max(scores.items(), key=lambda x: x[1])[0]
            return best_role
        
        # Default fallback
        return 'Backend'
    
    def assign_batch(
        self,
        texts: List[str],
        req_types: Optional[List[str]] = None
    ) -> List[str]:
        """Assign roles for a batch of texts"""
        if req_types is None:
            req_types = [None] * len(texts)
        
        return [self.assign(text, req_type) for text, req_type in zip(texts, req_types)]


class EnrichmentPipeline:
    """
    Complete enrichment pipeline:
    - Type classification
    - Priority classification
    - Domain classification
    - Role assignment
    """
    
    def __init__(self, model_dir: Path):
        self.model_dir = Path(model_dir)
        
        # Initialize enrichers
        self.type_enricher = LabelEnricher('type', model_dir)
        self.priority_enricher = LabelEnricher('priority', model_dir)
        self.domain_enricher = LabelEnricher('domain', model_dir)
        self.role_assigner = RoleAssigner()
        
        self.loaded = False
    
    def load(self) -> bool:
        """Load all models"""
        success = True
        success &= self.type_enricher.load()
        success &= self.priority_enricher.load()
        success &= self.domain_enricher.load()
        
        self.loaded = success
        return success
    
    def enrich(
        self,
        texts: List[str]
    ) -> List[Dict[str, any]]:
        """
        Enrich texts with all labels
        
        Returns:
            List of dicts with keys: type, priority, domain, role, confidence
        """
        if not self.loaded:
            self.load()
        
        # Predict all labels
        types_conf = self.type_enricher.predict(texts)
        priorities_conf = self.priority_enricher.predict(texts)
        domains_conf = self.domain_enricher.predict(texts)
        
        # Extract labels and confidences
        types, type_confs = zip(*types_conf) if types_conf else ([], [])
        priorities, priority_confs = zip(*priorities_conf) if priorities_conf else ([], [])
        domains, domain_confs = zip(*domains_conf) if domains_conf else ([], [])
        
        # Assign roles
        roles = self.role_assigner.assign_batch(texts, list(types))
        
        # Combine results
        results = []
        for i in range(len(texts)):
            # Overall confidence is min of all classifiers
            confidence = min(type_confs[i], priority_confs[i], domain_confs[i])
            
            results.append({
                'type': types[i],
                'type_confidence': type_confs[i],
                'priority': priorities[i],
                'priority_confidence': priority_confs[i],
                'domain': domains[i],
                'domain_confidence': domain_confs[i],
                'role': roles[i],
                'confidence': confidence
            })
        
        return results
    
    def enrich_single(self, text: str) -> Dict[str, any]:
        """Enrich single text"""
        result = self.enrich([text])
        return result[0] if result else {}


# Singleton
_enrichment_pipeline = None
_enrichment_model_dir = None

def get_enrichment_pipeline(model_dir: Path = None) -> EnrichmentPipeline:
    """Get singleton enrichment pipeline"""
    global _enrichment_pipeline, _enrichment_model_dir
    
    if model_dir is None:
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent
        model_dir = project_root / 'models' / 'task_gen'
    
    if _enrichment_pipeline is None or _enrichment_model_dir != model_dir:
        _enrichment_pipeline = EnrichmentPipeline(model_dir)
        _enrichment_pipeline.load()
        _enrichment_model_dir = model_dir
    
    return _enrichment_pipeline
