"""
Semantic Extraction Module
Core NLP: Dependency parsing to extract actor/action/object/conditions
"""

from typing import Dict, List, Optional, Any
import re
from config import CONDITIONAL_KEYWORDS, EXPECTED_KEYWORDS


class SemanticExtractor:
    """Extract semantic structure from requirement sentences using spaCy"""
    
    def __init__(self, spacy_model: str = "en_core_web_sm"):
        """
        Initialize spaCy NLP pipeline
        
        Args:
            spacy_model: SpaCy model name
        """
        try:
            import spacy
        except ImportError:
            raise ImportError("spaCy not installed. Run: pip install spacy")
        
        try:
            self.nlp = spacy.load(spacy_model)
        except OSError:
            raise RuntimeError(f"SpaCy model '{spacy_model}' not found. "
                             f"Download it: python -m spacy download {spacy_model}")
    
    def extract_actor(self, doc) -> Optional[str]:
        """
        Extract subject (actor) from dependency tree
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            Actor name or None
        """
        for token in doc:
            # nsubj = nominative subject
            if token.dep_ == "nsubj":
                return token.lemma_.lower()
            # nsubjpass = passive subject
            elif token.dep_ == "nsubjpass":
                return token.lemma_.lower()
        
        return None
    
    def extract_action(self, doc) -> Optional[str]:
        """
        Extract main action (verb) from dependency tree
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            Action verb or None
        """
        for token in doc:
            # ROOT is the main verb
            if token.dep_ == "ROOT" and token.pos_ in ("VERB", "AUX"):
                return token.lemma_.lower()
        
        # Fallback: find any verb
        for token in doc:
            if token.pos_ == "VERB":
                return token.lemma_.lower()
        
        return None
    
    def extract_objects(self, doc) -> List[str]:
        """
        Extract objects/entities from dependency tree
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            List of objects
        """
        objects = []
        
        for token in doc:
            # dobj = direct object
            if token.dep_ == "dobj":
                objects.append(token.lemma_.lower())
            # pobj = prepositional object
            elif token.dep_ == "pobj":
                objects.append(token.lemma_.lower())
            # attr = attribute (for "is" sentences)
            elif token.dep_ == "attr":
                objects.append(token.lemma_.lower())
        
        return objects
    
    def extract_conditions(self, doc) -> List[Dict[str, str]]:
        """
        Extract conditional clauses (IF/WHEN/UNLESS/PROVIDED)
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            List of condition dicts
        """
        conditions = []
        text_lower = doc.text.lower()
        
        for keyword in CONDITIONAL_KEYWORDS:
            if keyword in text_lower:
                # Extract clause after keyword
                pattern = rf"{keyword}\s+([^,;.]+)"
                matches = re.finditer(pattern, text_lower)
                
                for match in matches:
                    condition_text = match.group(1).strip()
                    conditions.append({
                        "keyword": keyword,
                        "condition": condition_text
                    })
        
        return conditions
    
    def extract_expected_results(self, doc) -> List[str]:
        """
        Extract expected results from sentence
        Look for: "should", "must", "will", "displays", "shows", etc.
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            List of expected results
        """
        results = []
        text = doc.text
        
        # Pattern: "should/must/will + verb"
        pattern = r"(?:should|must|will|shall)\s+(\w+)"
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            results.append(match.group(0).lower())
        
        # Pattern: "displays/shows/returns + object"
        pattern = r"(?:displays|shows|returns|sends|creates)\s+(?:the\s+)?(\w+)"
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            results.append(match.group(0).lower())
        
        return results
    
    def detect_requirement_type(self, doc, conditions: List[Dict]) -> str:
        """
        Detect requirement type:
        - functional: normal behavior
        - conditional: IF/WHEN
        - security: authentication/authorization/validation
        
        Args:
            doc: spaCy Doc object
            conditions: Extracted conditions
            
        Returns:
            Requirement type
        """
        text_lower = doc.text.lower()
        
        # Check for security keywords
        security_keywords = ["login", "authenticate", "authorize", "encrypt", 
                           "validate", "verify", "password", "permission", "access"]
        if any(kw in text_lower for kw in security_keywords):
            return "security"
        
        # Check for conditional
        if conditions:
            return "conditional"
        
        return "functional"
    
    def detect_inputs(self, doc) -> List[str]:
        """
        Detect input fields mentioned in requirement
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            List of input field names
        """
        inputs = []
        common_inputs = {
            "email", "password", "username", "name", "phone", "age",
            "date", "quantity", "amount", "price", "title", "description",
            "url", "address", "city", "country", "zip", "postcode"
        }
        
        text_lower = doc.text.lower()
        
        for inp in common_inputs:
            if inp in text_lower:
                inputs.append(inp)
        
        return list(set(inputs))  # Remove duplicates
    
    def extract(self, sentence: str) -> Dict[str, Any]:
        """
        Main extraction method - extract all semantic information
        
        Args:
            sentence: Single requirement sentence
            
        Returns:
            Dict with extracted semantic structure
        """
        # Process with spaCy
        doc = self.nlp(sentence)
        
        # Extract components
        actor = self.extract_actor(doc) or "system"
        action = self.extract_action(doc) or "process"
        objects = self.extract_objects(doc)
        conditions = self.extract_conditions(doc)
        expected_results = self.extract_expected_results(doc)
        inputs = self.detect_inputs(doc)
        req_type = self.detect_requirement_type(doc, conditions)
        
        return {
            "original_text": sentence,
            "actor": actor,
            "action": action,
            "objects": objects,
            "inputs": inputs,
            "conditions": conditions,
            "expected_results": expected_results or [action],
            "type": req_type,
            "raw_dep_tree": [(token.text, token.pos_, token.dep_) for token in doc],
        }


# Demo
if __name__ == "__main__":
    extractor = SemanticExtractor()
    
    test_sentences = [
        "User enters email and password",
        "If password is valid, system displays success message",
        "Admin can delete user accounts",
    ]
    
    for sent in test_sentences:
        print(f"\n📝 Sentence: {sent}")
        result = extractor.extract(sent)
        print(f"  Actor: {result['actor']}")
        print(f"  Action: {result['action']}")
        print(f"  Objects: {result['objects']}")
        print(f"  Inputs: {result['inputs']}")
        print(f"  Type: {result['type']}")
