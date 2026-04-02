"""
Normalization Module
Lemmatization, synonym mapping, actor normalization
"""

from typing import Dict, Any, List
from config import SYNONYM_MAP, DOMAIN_KEYWORDS


class Normalizer:
    """Normalize extracted semantic data"""
    
    def __init__(self):
        """Initialize normalizer with mapping configs"""
        self.synonym_map = SYNONYM_MAP
        self.domain_keywords = DOMAIN_KEYWORDS
    
    def normalize_action(self, action: str) -> str:
        """
        Normalize action verb (lemmatize if needed, apply synonyms)
        
        Args:
            action: Action verb
            
        Returns:
            Normalized action
        """
        action_lower = action.lower()
        
        # Check synonym map
        if action_lower in self.synonym_map:
            return self.synonym_map[action_lower]
        
        return action_lower
    
    def normalize_actor(self, actor: str) -> str:
        """
        Normalize actor (who performs action)
        
        Args:
            actor: Actor name
            
        Returns:
            Normalized actor
        """
        actor_lower = actor.lower()
        
        # Normalize system/app references
        system_keywords = ["system", "application", "app", "platform", "software"]
        if actor_lower in system_keywords:
            return "system"
        
        # Normalize user references
        user_keywords = ["user", "users", "student", "customer", "admin", "administrator"]
        if actor_lower in user_keywords:
            return "user"
        
        return actor_lower
    
    def normalize_object(self, obj: str) -> str:
        """
        Normalize object (what the action is performed on)
        
        Args:
            obj: Object name
            
        Returns:
            Normalized object
        """
        obj_lower = obj.lower()
        
        # Common object normalizations
        if obj_lower in ("msg", "message", "message"):
            return "message"
        if obj_lower in ("acct", "account", "user account"):
            return "account"
        if obj_lower in ("pwd", "passwd", "password"):
            return "password"
        if obj_lower in ("db", "database", "data store"):
            return "database"
        
        return obj_lower
    
    def detect_domain(self, requirement: Dict[str, Any]) -> str:
        """
        Detect domain (hotel, banking, ecommerce, healthcare, general)
        Based on keywords in requirement
        
        Args:
            requirement: Extracted requirement dict
            
        Returns:
            Domain name
        """
        text = requirement["original_text"].lower()
        
        # Score each domain
        domain_scores = {}
        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                domain_scores[domain] = score
        
        # Return highest scoring domain
        if domain_scores:
            return max(domain_scores, key=domain_scores.get)
        
        return "general"
    
    def extract_input_type(self, input_name: str) -> str:
        """
        Classify input field type
        
        Args:
            input_name: Input field name
            
        Returns:
            Input type (text, email, password, number, date, etc.)
        """
        input_lower = input_name.lower()
        
        # Email
        if "email" in input_lower or "mail" in input_lower:
            return "email"
        # Password
        if "password" in input_lower or "pwd" in input_lower or "passwd" in input_lower:
            return "password"
        # Phone
        if "phone" in input_lower or "tel" in input_lower or "mobile" in input_lower:
            return "phone"
        # Age
        if "age" in input_lower:
            return "age"
        # Date
        if "date" in input_lower or "when" in input_lower or "time" in input_lower:
            return "date"
        # Number/Quantity
        if "quantity" in input_lower or "amount" in input_lower or "number" in input_lower:
            return "number"
        # URL
        if "url" in input_lower or "link" in input_lower:
            return "url"
        # Default: text
        return "text"
    
    def normalize(self, requirement: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main normalization pipeline
        
        Args:
            requirement: Extracted requirement dict
            
        Returns:
            Normalized requirement dict
        """
        normalized = requirement.copy()
        
        # Normalize actor
        normalized["actor"] = self.normalize_actor(requirement["actor"])
        
        # Normalize action
        normalized["action"] = self.normalize_action(requirement["action"])
        
        # Normalize objects
        normalized["objects"] = [
            self.normalize_object(obj) for obj in requirement["objects"]
        ]
        
        # Input types
        normalized["input_types"] = {
            inp: self.extract_input_type(inp) 
            for inp in requirement["inputs"]
        }
        
        # Detect domain
        normalized["domain"] = self.detect_domain(requirement)
        
        return normalized


# Demo
if __name__ == "__main__":
    normalizer = Normalizer()
    
    test_req = {
        "original_text": "User signs in with email and password",
        "actor": "user",
        "action": "sign in",
        "objects": ["email", "password"],
        "inputs": ["email", "password"],
        "conditions": [],
        "type": "functional"
    }
    
    result = normalizer.normalize(test_req)
    
    print("📊 Normalization Result:")
    print(f"  Actor: {result['actor']}")
    print(f"  Action: {result['action']}")
    print(f"  Domain: {result['domain']}")
    print(f"  Input Types: {result['input_types']}")
