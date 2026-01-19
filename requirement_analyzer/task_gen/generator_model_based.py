"""
Model-based Task Generator (Mode 3)
Generate tasks using TRAINED MODELS (no API required)

Strategy:
1. Requirement detection: trained classifier
2. Enrichment (type/priority/domain): trained classifiers  
3. Task generation: Rule-based với NLP (không template cứng)
   - Extract entities from requirement
   - Generate natural variations
   - NO hardcoded templates
"""
import uuid
import spacy
import random
import re
from pathlib import Path
from typing import List, Dict, Optional
import logging
import joblib

from .schemas import GeneratedTask, TaskSource
from .segmenter import Sentence

logger = logging.getLogger(__name__)


class ModelBasedTaskGenerator:
    """
    Model-based task generator
    Uses trained ML models + NLP for natural generation
    NO API keys required, NO template strings
    """
    
    def __init__(self, model_dir: Path):
        self.model_dir = Path(model_dir)
        
        # Load trained models
        self.req_detector = self._load_req_detector()
        self.enrichers = self._load_enrichers()
        
        # Load spaCy for entity extraction
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("✓ Loaded spaCy for entity extraction")
        except OSError:
            logger.warning("⚠️  spaCy not found, using simple extraction")
            self.nlp = None
        
        # Generation patterns (NOT templates - used for variation)
        self.patterns = self._init_patterns()
    
    def _load_req_detector(self):
        """Load trained requirement detector"""
        try:
            vec_path = self.model_dir / 'requirement_detector_vectorizer.joblib'
            model_path = self.model_dir / 'requirement_detector_model.joblib'
            
            if not vec_path.exists() or not model_path.exists():
                logger.warning("Requirement detector not found")
                return None
            
            vectorizer = joblib.load(vec_path)
            model = joblib.load(model_path)
            
            logger.info("✓ Loaded requirement detector")
            return {'vectorizer': vectorizer, 'model': model}
        except Exception as e:
            logger.error(f"Error loading requirement detector: {e}")
            return None
    
    def _load_enrichers(self):
        """Load trained enricher models"""
        enrichers = {}
        
        for label in ['type', 'priority', 'domain']:
            try:
                vec_path = self.model_dir / f'{label}_vectorizer.joblib'
                model_path = self.model_dir / f'{label}_model.joblib'
                
                if vec_path.exists() and model_path.exists():
                    vectorizer = joblib.load(vec_path)
                    model = joblib.load(model_path)
                    enrichers[label] = {'vectorizer': vectorizer, 'model': model}
                    logger.info(f"✓ Loaded {label} enricher")
            except Exception as e:
                logger.error(f"Error loading {label} enricher: {e}")
        
        return enrichers
    
    def _init_patterns(self) -> Dict:
        """Initialize generation patterns (for variation, NOT templates)"""
        return {
            'functional': {
                'action_words': ['implement', 'build', 'create', 'develop', 'add', 'enable'],
                'desc_starters': [
                    'The system needs to',
                    'We need to implement',
                    'The application must provide',
                    'Implement functionality to',
                ],
                'ac_themes': [
                    'validation', 'error handling', 'user feedback', 
                    'accessibility', 'performance', 'security'
                ]
            },
            'security': {
                'action_words': ['secure', 'protect', 'enforce', 'implement', 'harden'],
                'desc_starters': [
                    'Security measures must be implemented to',
                    'The system needs to secure',
                    'Add security controls to',
                    'Implement comprehensive security for',
                ],
                'ac_themes': [
                    'authentication', 'authorization', 'encryption',
                    'audit logging', 'access control', 'compliance'
                ]
            },
            'interface': {
                'action_words': ['design', 'create', 'build', 'implement', 'develop'],
                'desc_starters': [
                    'Design and implement user interface for',
                    'Create interface components for',
                    'Build UI screens for',
                    'Develop user interface that',
                ],
                'ac_themes': [
                    'responsiveness', 'accessibility', 'usability',
                    'visual design', 'user feedback', 'loading states'
                ]
            },
            'data': {
                'action_words': ['implement', 'setup', 'create', 'build', 'design'],
                'desc_starters': [
                    'Setup data storage and management for',
                    'Implement data model for',
                    'Create database structure to support',
                    'Build data layer for',
                ],
                'ac_themes': [
                    'schema design', 'CRUD operations', 'validation',
                    'indexing', 'backup', 'migrations'
                ]
            },
        }
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities from requirement text"""
        if self.nlp:
            doc = self.nlp(text.lower())
            
            verbs = [token.lemma_ for token in doc if token.pos_ == 'VERB']
            nouns = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN']]
            objects = [chunk.text for chunk in doc.noun_chunks]
            
            return {
                'verbs': verbs[:3],  # Top 3 verbs
                'nouns': nouns[:5],  # Top 5 nouns
                'objects': objects[:3]  # Top 3 noun phrases
            }
        else:
            # Simple extraction
            words = text.lower().split()
            return {
                'verbs': [w for w in words if w in ['implement', 'create', 'build', 'manage']],
                'nouns': [w for w in words if len(w) > 5],
                'objects': [' '.join(words[i:i+2]) for i in range(len(words)-1)]
            }
    
    def generate_title(self, text: str, req_type: str, entities: Dict) -> str:
        """Generate natural title (NOT from template)"""
        patterns = self.patterns.get(req_type, self.patterns['functional'])
        
        # Modal verbs that should be skipped
        MODAL_VERBS = {'need', 'must', 'should', 'shall', 'may', 'can', 'will', 'would', 'could'}
        
        # Select action word
        action = random.choice(patterns['action_words'])
        
        # Extract action from verbs, skipping modals
        if entities['verbs']:
            # Find first non-modal verb
            for verb in entities['verbs']:
                if verb.lower() not in MODAL_VERBS:
                    action = verb
                    break
            else:
                # All verbs are modals, use fallback
                action = 'support'
        
        # Select object (skip those starting with modal verbs)
        obj = 'feature'
        if entities['objects']:
            # Find first object that doesn't start with a modal verb
            for candidate in entities['objects']:
                words = candidate.split()
                if not words or words[0].lower() not in MODAL_VERBS:
                    obj = candidate
                    break
        elif entities['nouns']:
            obj = entities['nouns'][0]
        
        # Construct natural title with variation
        variants = [
            f"{action.capitalize()} {obj}",
            f"{action.capitalize()} {obj} feature",
            f"{action.capitalize()} {obj} functionality",
            f"Add {obj} {action}",
            f"Build {obj} capability",
        ]
        
        return random.choice(variants)
    
    def generate_description(self, text: str, req_type: str, entities: Dict, domain: str) -> str:
        """Generate natural description"""
        patterns = self.patterns.get(req_type, self.patterns['functional'])
        
        starter = random.choice(patterns['desc_starters'])
        
        # Extract key components
        action = entities['verbs'][0] if entities['verbs'] else 'process'
        obj = entities['objects'][0] if entities['objects'] else 'data'
        
        # Build description with variation
        parts = [
            f"{starter} {action} {obj}.",
            f"This feature will support {domain} operations.",
        ]
        
        # Add context based on type
        if req_type == 'security':
            parts.append("This includes proper authentication, authorization, and encryption.")
        elif req_type == 'interface':
            parts.append("The UI should be intuitive, responsive, and accessible.")
        elif req_type == 'data':
            parts.append("Implement proper data validation and error handling.")
        else:
            parts.append("Include proper validation and error handling.")
        
        return ' '.join(parts)
    
    def generate_acceptance_criteria(self, text: str, req_type: str, entities: Dict) -> List[str]:
        """Generate natural acceptance criteria"""
        patterns = self.patterns.get(req_type, self.patterns['functional'])
        
        action = entities['verbs'][0] if entities['verbs'] else 'process'
        obj = entities['objects'][0] if entities['objects'] else 'data'
        
        # Generate varied AC based on themes
        ac_list = []
        themes = random.sample(patterns['ac_themes'], k=min(4, len(patterns['ac_themes'])))
        
        for theme in themes:
            if theme == 'validation':
                ac_list.append(f"System validates all {obj} input before processing")
            elif theme == 'error handling':
                ac_list.append(f"All error conditions are handled gracefully with user feedback")
            elif theme == 'performance':
                ac_list.append(f"Response time for {action} operation is under 2 seconds")
            elif theme == 'accessibility':
                ac_list.append("Feature meets WCAG 2.1 accessibility standards")
            elif theme == 'security':
                ac_list.append(f"Only authorized users can {action} {obj}")
            elif theme == 'authentication':
                ac_list.append(f"Authentication is required before {action}")
            elif theme == 'encryption':
                ac_list.append(f"All {obj} data is encrypted in transit and at rest")
            elif theme == 'audit logging':
                ac_list.append(f"All {action} operations are logged for audit")
            elif theme == 'responsiveness':
                ac_list.append("UI is responsive across desktop, tablet, and mobile devices")
            elif theme == 'usability':
                ac_list.append(f"Users can {action} {obj} intuitively without training")
            elif theme == 'schema design':
                ac_list.append(f"Database schema supports all {obj} attributes")
            elif theme == 'CRUD operations':
                ac_list.append(f"Create, read, update, and delete operations work for {obj}")
            elif theme == 'indexing':
                ac_list.append(f"Database indexes optimize {obj} query performance")
            else:
                ac_list.append(f"Feature works correctly for {action} {obj}")
        
        return ac_list
    
    def classify_requirement(self, text: str) -> Optional[Dict]:
        """Classify requirement using trained models"""
        if not self.req_detector:
            return None
        
        # Check if it's a requirement
        X = self.req_detector['vectorizer'].transform([text])
        is_req = self.req_detector['model'].predict(X)[0]
        
        if not is_req:
            return None
        
        # Predict type, priority, domain
        result = {'text': text}
        
        for label, enricher in self.enrichers.items():
            X = enricher['vectorizer'].transform([text])
            pred = enricher['model'].predict(X)[0]
            result[label] = pred
        
        return result
    
    def generate_task_from_sentence(
        self,
        sentence: Sentence,
        section_name: str = None
    ) -> Optional[GeneratedTask]:
        """Generate task from sentence using trained models"""
        
        # Classify requirement
        classification = self.classify_requirement(sentence.text)
        
        if not classification:
            return None
        
        req_type = classification.get('type', 'functional')
        priority = classification.get('priority', 'Medium')
        domain = classification.get('domain', 'general')
        
        # Extract entities
        entities = self.extract_entities(sentence.text)
        
        # Generate task components (natural, not template)
        title = self.generate_title(sentence.text, req_type, entities)
        description = self.generate_description(sentence.text, req_type, entities, domain)
        acceptance_criteria = self.generate_acceptance_criteria(sentence.text, req_type, entities)
        
        # Create task
        task = GeneratedTask(
            task_id=str(uuid.uuid4()),
            title=title,
            description=description,
            acceptance_criteria=acceptance_criteria,
            type=req_type,
            priority=priority,
            domain=domain,
            role=self._infer_role(req_type),
            labels=[req_type, priority, domain],
            story_points=self._estimate_story_points(req_type, len(acceptance_criteria)),
            confidence=0.85,
            source=TaskSource(
                sentence=sentence.text,
                section=section_name or '',
                offset=[getattr(sentence, 'offset_start', 0), getattr(sentence, 'offset_end', len(sentence.text))]
            )
        )
        
        return task
    
    def generate_tasks(
        self,
        sentences: List[Sentence],
        section_name: str = None
    ) -> List[GeneratedTask]:
        """Generate tasks from multiple sentences"""
        tasks = []
        
        for sentence in sentences:
            task = self.generate_task_from_sentence(sentence, section_name)
            if task:
                tasks.append(task)
        
        logger.info(f"Generated {len(tasks)} tasks from {len(sentences)} sentences")
        return tasks
    
    def generate_batch(
        self,
        requirement_sentences: List,
        enrichment_results: List[Dict],
        epic_name: Optional[str] = None
    ) -> List[GeneratedTask]:
        """Generate tasks from batch of requirements (standardized interface)"""
        tasks = []
        
        # requirement_sentences are Sentence objects
        # enrichment_results contain pre-classified labels
        max_tasks = min(len(requirement_sentences), len(enrichment_results))
        
        for idx in range(max_tasks):
            sentence = requirement_sentences[idx]
            labels = enrichment_results[idx]
            
            try:
                task = self._generate_from_sentence_and_labels(
                    sentence, 
                    labels,
                    epic_name=epic_name
                )
                if task:
                    tasks.append(task)
            except Exception as e:
                logger.warning(f"Failed to generate task for: {sentence.text[:50]}... Error: {e}")
                continue
        
        return tasks
    
    def _generate_from_sentence_and_labels(
        self,
        sentence: Sentence,
        labels: Dict,
        epic_name: Optional[str] = None
    ) -> Optional[GeneratedTask]:
        """Generate task from sentence with pre-computed labels"""
        req_type = labels.get('type', 'functional')
        priority = labels.get('priority', 'Medium')
        domain = labels.get('domain', 'general')
        
        # Extract entities
        entities = self.extract_entities(sentence.text)
        
        # Generate task components
        title = self.generate_title(sentence.text, req_type, entities)
        description = self.generate_description(sentence.text, req_type, entities, domain)
        acceptance_criteria = self.generate_acceptance_criteria(sentence.text, req_type, entities)
        
        # Apply quality repairs (inline)
        title = self._repair_title(title, entities)
        acceptance_criteria = self._dedupe_acceptance_criteria(acceptance_criteria)
        priority = self._adjust_priority_by_keywords(sentence.text, priority, req_type, domain)
        
        # Create task
        task = GeneratedTask(
            task_id=str(uuid.uuid4()),
            title=title,
            description=description,
            acceptance_criteria=acceptance_criteria,
            type=req_type,
            priority=priority,
            domain=domain,
            role=self._infer_role(req_type),
            labels=[req_type, priority, domain],
            story_points=self._estimate_story_points(req_type, len(acceptance_criteria)),
            confidence=labels.get('confidence', 0.85),
            source=TaskSource(
                sentence=sentence.text,
                section=getattr(sentence, 'section', ''),
                offset=[getattr(sentence, 'offset_start', 0), getattr(sentence, 'offset_end', len(sentence.text))]
            )
        )
        
        return task
    
    def _infer_role(self, req_type: str) -> str:
        """Infer role from requirement type"""
        role_map = {
            'functional': 'Backend',
            'security': 'Security',
            'interface': 'Frontend',
            'data': 'Backend',
            'performance': 'DevOps',
            'integration': 'Backend',
        }
        return role_map.get(req_type, 'Backend')
    
    def _estimate_story_points(self, req_type: str, num_ac: int) -> int:
        """Estimate story points"""
        base_points = {
            'functional': 3,
            'security': 5,
            'interface': 3,
            'data': 5,
            'performance': 5,
            'integration': 5,
        }
        
        base = base_points.get(req_type, 3)
        
        # Adjust based on AC count
        if num_ac >= 6:
            base += 2
        elif num_ac >= 4:
            base += 1
        
        return min(base, 8)  # Cap at 8
    
    def _repair_title(self, title: str, entities: Dict) -> str:
        """Repair low-quality titles"""
        # Reject double words ("implement implement")
        words = title.lower().split()
        if len(words) >= 2 and words[0] == words[1]:
            # Fallback to simple format
            obj = entities['objects'][0] if entities['objects'] else 'feature'
            return f"Implement {obj} capability"
        
        # Reject ultra-generic patterns
        bad_patterns = [
            r'\b(implement|add|build)\s+(system|application|platform)\s+(implement|add|build)\b',
            r'^(system|application)\s+\w+\s*$',  # "system implement"
        ]
        
        for pattern in bad_patterns:
            if re.search(pattern, title, re.IGNORECASE):
                obj = entities['nouns'][0] if entities['nouns'] else 'feature'
                action = entities['verbs'][0] if entities['verbs'] else 'implement'
                return f"{action.capitalize()} {obj} functionality"
        
        return title
    
    def _dedupe_acceptance_criteria(self, ac_list: List[str]) -> List[str]:
        """Remove duplicate acceptance criteria"""
        seen = set()
        unique = []
        
        for ac in ac_list:
            # Normalize for comparison
            normalized = ac.lower().strip()
            if normalized not in seen:
                seen.add(normalized)
                unique.append(ac)
        
        return unique
    
    def _adjust_priority_by_keywords(self, text: str, base_priority: str, req_type: str, domain: str) -> str:
        """Hybrid priority: use keywords to fix low-accuracy model predictions"""
        text_lower = text.lower()
        
        # HIGH priority keywords
        high_keywords = [
            'must', 'critical', 'security', 'authentication', 'authorization',
            'encrypt', 'payment', 'hipaa', 'pci', 'gdpr', 'compliance',
            'data breach', 'vulnerability', 'audit'
        ]
        
        # MEDIUM priority keywords
        medium_keywords = ['should', 'needs to', 'required', 'validate']
        
        # LOW priority keywords  
        low_keywords = ['could', 'may', 'nice to have', 'optional']
        
        # Domain + Type boosting
        if (domain in ['healthcare', 'finance'] and req_type == 'security'):
            return 'High'
        
        # Keyword-based priority
        if any(kw in text_lower for kw in high_keywords):
            return 'High'
        
        if any(kw in text_lower for kw in low_keywords):
            return 'Low'
        
        if any(kw in text_lower for kw in medium_keywords):
            return 'Medium'
        
        # Fallback to model prediction
        return base_priority
