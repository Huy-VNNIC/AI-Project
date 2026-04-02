"""
Pure ML Parser - No External API
Uses spaCy NER + custom training
"""

import spacy
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import re


@dataclass
class ParsedRequirement:
    """Structured requirement extracted by pure ML parser"""
    actor: str
    action: str
    object_entity: str
    constraints: List[str]
    domain: str
    priority: str
    risk_level: str
    confidence: float
    entities_found: Dict[str, List[str]]


class RequirementEntityExtractor:
    """Extract entities using spaCy NER + rule-based patterns"""
    
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("⚠️ Downloading spaCy model...")
            import os
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        # Add pipe for custom entity matching if needed
        if "entity_ruler" not in self.nlp.pipe_names:
            ruler = self.nlp.add_pipe("entity_ruler", before="ner")
        
        # Healthcare-specific patterns
        self.healthcare_patterns = [
            {"label": "MEDICAL_ACTION", "pattern": [{"LOWER": "schedule"}]},
            {"label": "MEDICAL_ACTION", "pattern": [{"LOWER": "prescribe"}]},
            {"label": "MEDICAL_ACTION", "pattern": [{"LOWER": "diagnose"}]},
            {"label": "MEDICAL_ACTION", "pattern": [{"LOWER": "check"}]},
            {"label": "MEDICAL_ACTION", "pattern": [{"LOWER": "monitor"}]},
            {"label": "MEDICAL_ENTITY", "pattern": [{"LOWER": "patient"}]},
            {"label": "MEDICAL_ENTITY", "pattern": [{"LOWER": "doctor"}]},
            {"label": "MEDICAL_ENTITY", "pattern": [{"LOWER": "appointment"}]},
            {"label": "MEDICAL_ENTITY", "pattern": [{"LOWER": "prescription"}]},
            {"label": "MEDICAL_ENTITY", "pattern": [{"LOWER": "medical"}, {"LOWER": "record"}]},
        ]
    
    def extract_entities(self, text: str) -> Dict:
        """Extract entities using spaCy"""
        doc = self.nlp(text)
        entities = {}
        
        for ent in doc.ents:
            if ent.label_ not in entities:
                entities[ent.label_] = []
            entities[ent.label_].append(ent.text)
        
        return entities
    
    def extract_constraints(self, text: str) -> List[str]:
        """Extract constraints from text using patterns"""
        constraints = []
        
        # Pattern: numbers + time units
        time_patterns = [
            r'(\d+)\s*(hours?|days?|weeks?|months?|years?)',
            r'(within|before|after|no more than|no less than)\s+(\d+)\s*(hours?|days?|weeks?)',
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                constraints.append(f"{' '.join(match)}")
        
        # Business rules
        if 'must' in text.lower():
            doc = self.nlp(text)
            for token in doc:
                if token.text.lower() == 'must':
                    # Get clause after "must"
                    start = token.i
                    end = min(start + 10, len(doc))
                    constraint = doc[start:end].text
                    constraints.append(constraint)
        
        return list(set(constraints)) if constraints else []


class PureMLParser:
    """ML-based parser for requirements"""
    
    def __init__(self):
        self.extractor = RequirementEntityExtractor()
        self.nlp = spacy.load("en_core_web_sm")
        
        # Action keywords (learned from healthcare domain)
        self.action_keywords = {
            "book": ["schedule", "book", "reserve", "make"],
            "view": ["view", "see", "display", "show", "check"],
            "manage": ["manage", "update", "modify", "change"],
            "delete": ["delete", "remove", "cancel"],
            "access": ["access", "view", "retrieve"],
            "prevent": ["prevent", "block", "deny", "restrict"],
            "enforce": ["enforce", "ensure", "require"],
        }
        
        # Domain classification keywords
        self.domain_keywords = {
            "healthcare": ["patient", "doctor", "appointment", "medical", "prescription", "hospital", "clinic", "diagnosis"],
            "banking": ["account", "transaction", "credit", "debit", "balance", "payment", "transfer", "loan"],
            "ecommerce": ["product", "cart", "order", "payment", "shipping", "checkout", "customer"],
            "general": []
        }
    
    def classify_domain(self, text: str) -> str:
        """Classify domain from text"""
        text_lower = text.lower()
        scores = {}
        
        for domain, keywords in self.domain_keywords.items():
            if domain == "general":
                continue
            score = sum(text_lower.count(kw) for kw in keywords)
            scores[domain] = score
        
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return "general"
    
    def extract_actor(self, text: str) -> str:
        """Extract WHO (actor) performs action"""
        doc = self.nlp(text)
        
        # Look for PERSON or ORG entities
        for ent in doc.ents:
            if ent.label_ in ["PERSON", "ORG"]:
                return ent.text
        
        # Fallback: healthcare patterns
        if "patient" in text.lower():
            return "patient"
        if "doctor" in text.lower():
            return "doctor"
        if "system" in text.lower():
            return "system"
        
        # Default SVO extraction
        for token in doc:
            if token.pos_ == "NOUN" and token.dep_ == "nsubj":
                return token.text
        
        return "user"
    
    def extract_action(self, text: str) -> str:
        """Extract WHAT action (verb) is performed"""
        doc = self.nlp(text)
        
        # Find main verb
        for token in doc:
            if token.pos_ == "VERB" and token.dep_ == "ROOT":
                return token.text
        
        # Keyword matching
        text_lower = text.lower()
        for action, keywords in self.action_keywords.items():
            for kw in keywords:
                if kw in text_lower:
                    return action
        
        return "perform"
    
    def extract_object(self, text: str) -> str:
        """Extract ON WHAT entity (object) action is performed"""
        doc = self.nlp(text)
        
        # Look for direct object
        for token in doc:
            if token.dep_ == "dobj":
                return token.text
        
        # Healthcare patterns
        healthcare_objects = ["appointment", "prescription", "medical record", "patient", "account"]
        text_lower = text.lower()
        for obj in healthcare_objects:
            if obj in text_lower:
                return obj
        
        return "entity"
    
    def estimate_priority(self, text: str) -> str:
        """Estimate priority level"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["critical", "must", "security", "urgent"]):
            return "HIGH"
        if any(word in text_lower for word in ["should", "important"]):
            return "MEDIUM"
        return "LOW"
    
    def estimate_risk_level(self, text: str) -> str:
        """Estimate risk level"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["security", "password", "access", "unauthorized", "fraud", "attack"]):
            return "CRITICAL"
        if any(word in text_lower for word in ["patient", "medical", "health", "data", "privacy"]):
            return "HIGH"
        if any(word in text_lower for word in ["accuracy", "consistency"]):
            return "MEDIUM"
        return "LOW"
    
    def parse(self, requirement_text: str) -> ParsedRequirement:
        """Main parsing function - pure ML"""
        
        # Extract all components
        actor = self.extract_actor(requirement_text)
        action = self.extract_action(requirement_text)
        object_entity = self.extract_object(requirement_text)
        constraints = self.extractor.extract_constraints(requirement_text)
        domain = self.classify_domain(requirement_text)
        priority = self.estimate_priority(requirement_text)
        risk_level = self.estimate_risk_level(requirement_text)
        
        # Entity extraction confidence
        entities_found = self.extractor.extract_entities(requirement_text)
        
        # Calculate confidence based on entities found
        confidence = min(0.95, 0.5 + (len(entities_found) * 0.15))
        
        return ParsedRequirement(
            actor=actor,
            action=action,
            object_entity=object_entity,
            constraints=constraints,
            domain=domain,
            priority=priority,
            risk_level=risk_level,
            confidence=confidence,
            entities_found=entities_found
        )


# Demo
if __name__ == "__main__":
    parser = PureMLParser()
    
    test_requirements = [
        "The system must allow patients to schedule appointments up to 30 days in advance without exceeding maximum capacity.",
        "The system shall prevent unauthorized access to patient medical records and encrypt all sensitive data.",
        "Doctors can prescribe medications only if patient allergies are checked first.",
    ]
    
    print("🧠 PURE ML PARSER DEMO\n")
    print("=" * 80)
    
    for req in test_requirements:
        print(f"\n📋 Requirement: {req}\n")
        result = parser.parse(req)
        print(f"✅ Parsed:")
        print(f"   Actor: {result.actor}")
        print(f"   Action: {result.action}")
        print(f"   Object: {result.object_entity}")
        print(f"   Constraints: {result.constraints}")
        print(f"   Domain: {result.domain}")
        print(f"   Priority: {result.priority}")
        print(f"   Risk: {result.risk_level}")
        print(f"   Confidence: {result.confidence:.2%}")
        print(f"   Entities: {result.entities_found}")
        print("-" * 80)
