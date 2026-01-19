"""
Template-based Task Generator (Mode 1)
Generate structured tasks from requirements using templates + NLP
"""
import re
import uuid
from typing import List, Dict, Optional
from dataclasses import dataclass
import spacy
from pathlib import Path
import logging

from .schemas import GeneratedTask, TaskSource
from .segmenter import Sentence

logger = logging.getLogger(__name__)


class TaskTemplateGenerator:
    """
    Template-based task generator
    Uses NLP parsing + templates to generate tasks
    """
    
    def __init__(self):
        # Load spaCy for dependency parsing
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("✓ Loaded spaCy model for parsing")
        except OSError:
            logger.warning("⚠️  spaCy model not found, using rule-based generation")
            self.nlp = None
        
        # Define templates by requirement type
        self.templates = self._init_templates()
    
    def _init_templates(self) -> Dict[str, Dict[str, any]]:
        """Initialize task templates by type"""
        return {
            'functional': {
                'title_template': 'Implement {action} for {object}',
                'description_template': 'The system needs to {action} {object} {condition}.',
                'ac_templates': [
                    'User can {action} {object} successfully',
                    'System validates input data before {action}',
                    'System provides appropriate feedback on {action} completion',
                    'Error handling is implemented for edge cases'
                ]
            },
            'security': {
                'title_template': 'Secure {object} {action}',
                'description_template': 'Implement security measures to {action} {object} {condition}.',
                'ac_templates': [
                    'Data is encrypted in transit and at rest',
                    'Role-based access control is enforced',
                    'Authentication is required before {action}',
                    'Audit logging captures all {action} operations',
                    'Security vulnerabilities are addressed'
                ]
            },
            'interface': {
                'title_template': 'Design {object} UI for {action}',
                'description_template': 'Create user interface to {action} {object} {condition}.',
                'ac_templates': [
                    'UI displays {object} clearly and accurately',
                    'Form validation provides immediate feedback',
                    'UI is responsive across devices',
                    'Accessibility standards (WCAG) are met',
                    'User can {action} {object} intuitively'
                ]
            },
            'data': {
                'title_template': 'Implement {object} data management',
                'description_template': 'Setup data storage and management for {object} to support {action} {condition}.',
                'ac_templates': [
                    'Database schema supports {object} storage',
                    'CRUD operations are implemented for {object}',
                    'Data integrity constraints are enforced',
                    'Indexing optimizes query performance',
                    'Data backup and recovery procedures are in place'
                ]
            },
            'performance': {
                'title_template': 'Optimize {object} {action} performance',
                'description_template': 'Improve performance of {action} {object} {condition}.',
                'ac_templates': [
                    'Response time is under 2 seconds',
                    'System handles concurrent requests efficiently',
                    'Resource usage is optimized',
                    'Performance benchmarks are met',
                    'Load testing confirms scalability'
                ]
            },
            'integration': {
                'title_template': 'Integrate {object} with {action}',
                'description_template': 'Setup integration to {action} {object} {condition}.',
                'ac_templates': [
                    'API endpoints are properly configured',
                    'Data mapping between systems is correct',
                    'Error handling covers integration failures',
                    'Integration testing passes successfully',
                    'Documentation covers integration setup'
                ]
            },
            'default': {
                'title_template': '{action} {object}',
                'description_template': 'Implement functionality to {action} {object} {condition}.',
                'ac_templates': [
                    'Functionality works as described',
                    'Edge cases are handled appropriately',
                    'Code follows project standards',
                    'Unit tests achieve 80%+ coverage',
                    'Documentation is updated'
                ]
            }
        }
    
    def generate(
        self,
        sentence: Sentence,
        labels: Dict[str, any],
        epic_name: Optional[str] = None
    ) -> GeneratedTask:
        """
        Generate a task from a requirement sentence
        
        Args:
            sentence: Sentence object with requirement text
            labels: Dict with type, priority, domain, role, confidence
            epic_name: Optional epic/module name
        
        Returns:
            GeneratedTask object
        """
        # Parse sentence to extract components
        components = self._parse_sentence(sentence.text)
        
        # Get template for type
        req_type = labels.get('type', 'functional')
        template = self.templates.get(req_type, self.templates['default'])
        
        # Generate title
        title = self._generate_title(template, components, req_type)
        
        # Generate description
        description = self._generate_description(template, components, sentence, labels)
        
        # Generate acceptance criteria
        acceptance_criteria = self._generate_acceptance_criteria(
            template, components, labels, sentence.text
        )
        
        # Create task source metadata
        source = TaskSource(
            sentence=sentence.text,
            section=sentence.section,
            doc_offset=[sentence.offset_start, sentence.offset_end],
            line_number=sentence.line_number
        )
        
        # Build task
        task = GeneratedTask(
            task_id=str(uuid.uuid4()),
            epic=epic_name,
            title=title,
            description=description,
            acceptance_criteria=acceptance_criteria,
            type=labels.get('type', 'functional'),
            priority=labels.get('priority', 'Medium'),
            domain=labels.get('domain', 'general'),
            role=labels.get('role', 'Backend'),
            confidence=labels.get('confidence', 0.7),
            source=source
        )
        
        return task
    
    def _parse_sentence(self, text: str) -> Dict[str, str]:
        """
        Parse sentence to extract action, object, condition
        
        Returns dict with keys: action, object, condition
        """
        components = {
            'action': '',
            'object': '',
            'condition': ''
        }
        
        if self.nlp:
            # Use spaCy for parsing
            doc = self.nlp(text)
            
            # Extract main verb (action)
            verbs = [token for token in doc if token.pos_ == 'VERB']
            if verbs:
                # Prefer modal + verb construction
                for i, token in enumerate(doc):
                    if token.lemma_ in ['must', 'shall', 'should', 'will', 'need', 'has', 'can']:
                        if i + 1 < len(doc) and doc[i + 1].pos_ == 'VERB':
                            components['action'] = doc[i + 1].lemma_
                            break
                
                if not components['action']:
                    components['action'] = verbs[0].lemma_
            
            # Extract direct object (what is being acted upon)
            for token in doc:
                if token.dep_ in ['dobj', 'pobj'] and token.pos_ in ['NOUN', 'PROPN']:
                    # Get noun phrase
                    np = self._get_noun_phrase(token)
                    components['object'] = np
                    break
            
            # Extract condition (when/where/how)
            condition_deps = ['prep', 'advcl', 'advmod']
            condition_tokens = [token for token in doc if token.dep_ in condition_deps]
            if condition_tokens:
                # Get subtree
                condition_parts = []
                for token in condition_tokens:
                    subtree = list(token.subtree)
                    condition_parts.extend([t.text for t in subtree])
                if condition_parts:
                    components['condition'] = ' '.join(condition_parts[:10])  # limit length
        
        else:
            # Fallback: rule-based extraction
            components = self._rule_based_parse(text)
        
        # Cleanup and defaults
        if not components['action']:
            components['action'] = self._extract_action_fallback(text)
        
        if not components['object']:
            components['object'] = self._extract_object_fallback(text)
        
        if not components['condition']:
            components['condition'] = ''
        
        return components
    
    def _get_noun_phrase(self, token) -> str:
        """Extract full noun phrase from token"""
        # Get compound nouns and modifiers
        phrase_tokens = []
        
        # Add left children (modifiers)
        for child in token.children:
            if child.dep_ in ['compound', 'amod', 'det']:
                phrase_tokens.append(child.text)
        
        # Add head noun
        phrase_tokens.append(token.text)
        
        # Add right children (post-modifiers)
        for child in token.children:
            if child.dep_ in ['prep', 'relcl']:
                phrase_tokens.append(child.text)
        
        return ' '.join(phrase_tokens)
    
    def _rule_based_parse(self, text: str) -> Dict[str, str]:
        """Fallback rule-based parsing"""
        components = {
            'action': '',
            'object': '',
            'condition': ''
        }
        
        # Extract action (verb after modal)
        modal_pattern = r'\b(must|shall|should|will|need to|has to|can)\s+(\w+)'
        match = re.search(modal_pattern, text, re.IGNORECASE)
        if match:
            components['action'] = match.group(2)
        
        # Extract object (common nouns)
        object_pattern = r'\b(user|system|application|interface|data|report|order|payment|account|product|service|information|record|file|document)s?\b'
        match = re.search(object_pattern, text, re.IGNORECASE)
        if match:
            components['object'] = match.group(1)
        
        # Extract condition (after when/while/during/before/after)
        condition_pattern = r'\b(when|while|during|before|after|for)\s+([^.]+)'
        match = re.search(condition_pattern, text, re.IGNORECASE)
        if match:
            components['condition'] = match.group(2).strip()
        
        return components
    
    def _extract_action_fallback(self, text: str) -> str:
        """Extract action using common verbs"""
        common_actions = [
            'manage', 'create', 'update', 'delete', 'display', 'process',
            'validate', 'authenticate', 'authorize', 'generate', 'calculate',
            'store', 'retrieve', 'send', 'receive', 'track', 'monitor',
            'support', 'enable', 'allow', 'provide', 'handle', 'integrate'
        ]
        
        text_lower = text.lower()
        for action in common_actions:
            if action in text_lower:
                return action
        
        return 'implement'
    
    def _extract_object_fallback(self, text: str) -> str:
        """Extract object using common nouns"""
        common_objects = [
            'user', 'system', 'data', 'report', 'interface', 'application',
            'order', 'payment', 'account', 'product', 'service', 'information',
            'record', 'file', 'document', 'transaction', 'inventory', 'content'
        ]
        
        text_lower = text.lower()
        for obj in common_objects:
            if obj in text_lower:
                return obj
        
        return 'functionality'
    
    def _generate_title(
        self,
        template: Dict,
        components: Dict[str, str],
        req_type: str
    ) -> str:
        """Generate task title"""
        title_template = template['title_template']
        
        try:
            title = title_template.format(**components)
            # Cleanup
            title = re.sub(r'\s+', ' ', title).strip()
            # Capitalize first letter
            title = title[0].upper() + title[1:] if title else 'Implement requirement'
            # Limit length
            if len(title) > 100:
                title = title[:97] + '...'
            return title
        except KeyError:
            # Fallback
            action = components.get('action', 'implement')
            obj = components.get('object', 'functionality')
            return f"{action.capitalize()} {obj}"
    
    def _generate_description(
        self,
        template: Dict,
        components: Dict[str, str],
        sentence: Sentence,
        labels: Dict
    ) -> str:
        """Generate task description"""
        desc_template = template['description_template']
        
        try:
            description = desc_template.format(**components)
            description = re.sub(r'\s+', ' ', description).strip()
        except KeyError:
            description = sentence.text
        
        # Add context from section
        if sentence.section and sentence.section != "Document":
            description += f"\n\n**Context**: {sentence.section}"
        
        # Add requirement type and domain
        description += f"\n\n**Type**: {labels.get('type', 'functional')}"
        description += f"\n**Domain**: {labels.get('domain', 'general')}"
        
        return description
    
    def _generate_acceptance_criteria(
        self,
        template: Dict,
        components: Dict[str, str],
        labels: Dict,
        original_text: str
    ) -> List[str]:
        """Generate acceptance criteria"""
        ac_templates = template.get('ac_templates', [])
        
        acceptance_criteria = []
        
        for ac_template in ac_templates[:5]:  # limit to 5 AC
            try:
                ac = ac_template.format(**components)
                ac = re.sub(r'\s+', ' ', ac).strip()
                if ac and ac not in acceptance_criteria:
                    acceptance_criteria.append(ac)
            except KeyError:
                continue
        
        # Always add requirement verification AC
        acceptance_criteria.append(f"Requirement is verified: '{original_text[:80]}...'")
        
        # Add testing AC based on role
        role = labels.get('role', 'Backend')
        if role == 'Frontend':
            acceptance_criteria.append("UI/UX testing passes")
        elif role == 'Backend':
            acceptance_criteria.append("Integration tests pass")
        elif role == 'Security':
            acceptance_criteria.append("Security scan passes with no critical issues")
        
        return acceptance_criteria[:7]  # max 7 AC
    
    def generate_batch(
        self,
        sentences: List[Sentence],
        labels_list: List[Dict[str, any]],
        epic_name: Optional[str] = None
    ) -> List[GeneratedTask]:
        """Generate tasks for a batch of sentences"""
        tasks = []
        
        for sentence, labels in zip(sentences, labels_list):
            try:
                task = self.generate(sentence, labels, epic_name)
                tasks.append(task)
            except Exception as e:
                logger.error(f"Error generating task for sentence: {e}")
                continue
        
        return tasks


# Singleton
_generator = None

def get_generator() -> TaskTemplateGenerator:
    """Get singleton generator"""
    global _generator
    if _generator is None:
        _generator = TaskTemplateGenerator()
    return _generator
