"""
Structured Intent Model for Requirement Extraction
Represents parsed requirement as structured data (independent of LLM)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class DomainType(Enum):
    """Supported domains"""
    HOTEL_MANAGEMENT = "hotel_management"
    BANKING = "banking"
    ECOMMERCE = "ecommerce"
    HEALTHCARE = "healthcare"
    GENERAL = "general"


class IntentType(Enum):
    """Types of requirement intent"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    SEARCH = "search"
    VALIDATE = "validate"
    AUTHENTICATE = "authenticate"
    AUTHORIZE = "authorize"
    NOTIFY = "notify"


@dataclass
class Constraint:
    """Single constraint from requirement"""
    name: str
    description: str
    constraint_type: str  # "date_range", "numeric", "enum", "pattern", etc
    values: List[str] = field(default_factory=list)


@dataclass
class SecurityConcern:
    """Security-related concern detected in requirement"""
    concern_type: str  # "authentication", "authorization", "data_privacy", "encryption"
    description: str
    severity: str  # "critical", "high", "medium", "low"
    test_cases_needed: List[str] = field(default_factory=list)


@dataclass
class Entity:
    """Main entity being acted upon"""
    name: str  # e.g., "booking", "customer", "invoice"
    description: str
    attributes: List[str] = field(default_factory=list)
    relationships: List[str] = field(default_factory=list)


@dataclass
class Action:
    """Action being performed"""
    verb: str  # e.g., "create", "cancel", "update"
    target: str  # entity name
    description: str
    preconditions: List[str] = field(default_factory=list)
    postconditions: List[str] = field(default_factory=list)


@dataclass
class StructuredIntent:
    """
    Extracted and structured representation of a requirement
    This is the OUTPUT of requirement extraction
    Independent of which LLM/AI model is used
    """
    # Basic info
    requirement_id: str
    original_text: str
    domain: DomainType
    
    # Main components
    primary_entity: Entity
    primary_action: Action
    secondary_entities: List[Entity] = field(default_factory=list)
    secondary_actions: List[Action] = field(default_factory=list)
    
    # Constraints & rules
    constraints: List[Constraint] = field(default_factory=list)
    business_rules: List[str] = field(default_factory=list)
    
    # Security & compliance
    security_concerns: List[SecurityConcern] = field(default_factory=list)
    compliance_requirements: List[str] = field(default_factory=list)
    
    # Metadata
    confidence_score: float = 0.8  # How confident extraction is
    source_language: str = "vi"  # Vietnamese by default
    extracted_at: str = ""
    extraction_model: str = "custom_ai"  # User's AI model name
    
    # Additional context
    workflow_steps: List[str] = field(default_factory=list)
    error_scenarios: List[str] = field(default_factory=list)
    edge_cases: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization"""
        return {
            "requirement_id": self.requirement_id,
            "original_text": self.original_text,
            "domain": self.domain.value,
            "primary_entity": {
                "name": self.primary_entity.name,
                "description": self.primary_entity.description,
                "attributes": self.primary_entity.attributes,
                "relationships": self.primary_entity.relationships,
            },
            "primary_action": {
                "verb": self.primary_action.verb,
                "target": self.primary_action.target,
                "description": self.primary_action.description,
                "preconditions": self.primary_action.preconditions,
                "postconditions": self.primary_action.postconditions,
            },
            "constraints": [
                {
                    "name": c.name,
                    "description": c.description,
                    "type": c.constraint_type,
                    "values": c.values,
                }
                for c in self.constraints
            ],
            "security_concerns": [
                {
                    "type": sc.concern_type,
                    "description": sc.description,
                    "severity": sc.severity,
                    "test_cases_needed": sc.test_cases_needed,
                }
                for sc in self.security_concerns
            ],
            "business_rules": self.business_rules,
            "compliance_requirements": self.compliance_requirements,
            "workflow_steps": self.workflow_steps,
            "error_scenarios": self.error_scenarios,
            "edge_cases": self.edge_cases,
            "confidence_score": self.confidence_score,
            "extraction_model": self.extraction_model,
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "StructuredIntent":
        """Create from dict (for deserialization)"""
        # This is helper - your extraction model will populate directly
        pass
