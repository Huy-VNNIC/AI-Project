"""
Requirement Structuring Module
Build JSON schema from normalized extracted data
"""

from typing import Dict, Any, List
from dataclasses import dataclass, asdict, field
from datetime import datetime


@dataclass
class Condition:
    """Represents a condition in requirement"""
    keyword: str  # if, when, unless, provided
    condition_text: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Input:
    """Represents an input field"""
    name: str
    type_: str  # email, password, text, number, date, etc.
    required: bool = True
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "type": self.type_,
            "required": self.required
        }


@dataclass
class StructuredRequirement:
    """Structured requirement representation"""
    requirement_id: str
    original_text: str
    actor: str  # user, system, admin
    action: str  # normalized verb
    objects: List[str] = field(default_factory=list)
    inputs: List[Input] = field(default_factory=list)
    conditions: List[Condition] = field(default_factory=list)
    expected_results: List[str] = field(default_factory=list)
    type_: str = "functional"  # functional, conditional, security
    domain: str = "general"  # hotel, banking, ecommerce, healthcare, general
    priority: str = "medium"  # low, medium, high, critical
    status: str = "ready"  # ready, needs_review, ambiguous
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirement_id": self.requirement_id,
            "original_text": self.original_text,
            "actor": self.actor,
            "action": self.action,
            "objects": self.objects,
            "inputs": [inp.to_dict() for inp in self.inputs],
            "conditions": [cond.to_dict() for cond in self.conditions],
            "expected_results": self.expected_results,
            "type": self.type_,
            "domain": self.domain,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at,
        }


class RequirementStructurer:
    """Convert normalized data to structured requirement"""
    
    def __init__(self):
        """Initialize structurer"""
        pass
    
    @staticmethod
    def infer_priority(requirement: Dict[str, Any]) -> str:
        """
        Infer priority based on keywords
        
        Args:
            requirement: Normalized requirement dict
            
        Returns:
            Priority level
        """
        text_lower = requirement["original_text"].lower()
        
        # Critical keywords
        if any(kw in text_lower for kw in ["must", "critical", "security", "authentication"]):
            return "critical"
        # High priority
        elif any(kw in text_lower for kw in ["should", "important", "validation"]):
            return "high"
        # Low priority
        elif any(kw in text_lower for kw in ["optional", "nice to have", "may"]):
            return "low"
        
        return "medium"
    
    @staticmethod
    def infer_status(requirement: Dict[str, Any]) -> str:
        """
        Infer status (ready, needs_review, ambiguous)
        
        Args:
            requirement: Normalized requirement dict
            
        Returns:
            Status
        """
        # If very vague, mark for review
        if len(requirement["original_text"]) < 15:
            return "needs_review"
        
        # If multiple conditions, might be ambiguous
        if len(requirement.get("conditions", [])) > 2:
            return "ambiguous"
        
        return "ready"
    
    def structure(
        self,
        requirement_id: str,
        requirement: Dict[str, Any]
    ) -> StructuredRequirement:
        """
        Convert normalized requirement to structured format
        
        Args:
            requirement_id: Requirement ID
            requirement: Normalized requirement dict
            
        Returns:
            StructuredRequirement object
        """
        # Build inputs
        inputs = [
            Input(
                name=inp,
                type_=requirement.get("input_types", {}).get(inp, "text"),
                required=True
            )
            for inp in requirement.get("inputs", [])
        ]
        
        # Build conditions
        conditions = [
            Condition(
                keyword=cond["keyword"],
                condition_text=cond["condition"]
            )
            for cond in requirement.get("conditions", [])
        ]
        
        # Infer priority and status
        priority = self.infer_priority(requirement)
        status = self.infer_status(requirement)
        
        return StructuredRequirement(
            requirement_id=requirement_id,
            original_text=requirement["original_text"],
            actor=requirement["actor"],
            action=requirement["action"],
            objects=requirement.get("objects", []),
            inputs=inputs,
            conditions=conditions,
            expected_results=requirement.get("expected_results", []),
            type_=requirement["type"],
            domain=requirement["domain"],
            priority=priority,
            status=status,
        )
    
    def structure_batch(
        self,
        requirements: List[Dict[str, Any]]
    ) -> List[StructuredRequirement]:
        """
        Structure multiple requirements
        
        Args:
            requirements: List of normalized requirement dicts
            
        Returns:
            List of StructuredRequirement objects
        """
        structured = []
        for idx, req in enumerate(requirements, 1):
            req_id = f"REQ-{idx:03d}"
            structured.append(self.structure(req_id, req))
        
        return structured


# Demo
if __name__ == "__main__":
    from dataclasses import asdict
    
    structurer = RequirementStructurer()
    
    test_normalized = {
        "original_text": "Authentication system must validate user email and password before login",
        "actor": "system",
        "action": "validate",
        "objects": ["email", "password"],
        "inputs": ["email", "password"],
        "input_types": {"email": "email", "password": "password"},
        "conditions": [],
        "expected_results": ["login allowed"],
        "type": "security",
        "domain": "general"
    }
    
    req = structurer.structure("REQ-001", test_normalized)
    
    print("🔧 Structured Requirement:")
    print(f"  ID: {req.requirement_id}")
    print(f"  Actor: {req.actor}")
    print(f"  Action: {req.action}")
    print(f"  Priority: {req.priority}")
    print(f"  Status: {req.status}")
    print(f"  Domain: {req.domain}")
