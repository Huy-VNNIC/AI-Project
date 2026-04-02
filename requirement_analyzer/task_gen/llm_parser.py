"""
LLM Semantic Parser for v3 Hybrid AI System
Extracts structured intent from requirements using Claude API
"""

import json
import os
from typing import Dict, List, Any
import anthropic


class StructuredIntent:
    """Data class for LLM-extracted structured intent"""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
    
    @property
    def actor(self) -> str:
        return self.data.get("actor", "User")
    
    @property
    def action(self) -> str:
        return self.data.get("action", "perform action")
    
    @property
    def object_entity(self) -> str:
        return self.data.get("object", "system")
    
    @property
    def conditions(self) -> List[str]:
        return self.data.get("conditions", [])
    
    @property
    def constraints(self) -> List[str]:
        return self.data.get("constraints", [])
    
    @property
    def domain(self) -> str:
        return self.data.get("domain", "general")
    
    @property
    def intent_type(self) -> str:
        return self.data.get("intent_type", "simple_action")
    
    @property
    def dependencies(self) -> List[Dict[str, str]]:
        return self.data.get("dependencies", [])
    
    @property
    def risk_level(self) -> str:
        return self.data.get("risk_level", "medium")
    
    @property
    def confidence(self) -> float:
        return self.data.get("confidence", 0.85)
    
    def to_dict(self) -> Dict[str, Any]:
        return self.data


class LLMSemanticParser:
    """
    Extracts structured intent from requirements using Claude LLM
    
    This parser replaces regex-based parsing with semantic understanding.
    Returns rich structured data that powers better test generation.
    """
    
    LLM_PROMPT = """You are an expert QA Test Analyst specializing in test case generation.

Your task: Extract structured intent from software requirements.

Return ONLY valid JSON (no explanation, no markdown) with these fields:
{
  "actor": "WHO performs the action (e.g., 'Doctor', 'Patient', 'System', 'Admin')",
  "action": "WHAT action is performed (verb, e.g., 'prescribe', 'login', 'verify')",
  "object": "ON WHAT is the action performed (noun, e.g., 'medication', 'patient record')",
  "conditions": ["LIST of preconditions that must be true before action"],
  "constraints": ["LIST of constraints/rules that limit the action"],
  "domain": "DOMAIN mapped from keywords (healthcare|banking|ecommerce|telecommunications|general)",
  "intent_type": "TYPE of requirement (simple_action|validation|security|workflow|conditional_workflow)",
  "dependencies": [{"step": "prerequisite action", "before": "main action"}],
  "risk_level": "RISK if violated (low|medium|high)",
  "confidence": 0.0-1.0 confidence score in extraction
}

IMPORTANT RULES:
- Extract EXACT semantics, not paraphrasing
- For healthcare: look for patient safety, data privacy, drug interactions
- For banking: look for fraud, authorization, data integrity
- For ecommerce: look for inventory, payment, delivery tracking
- Identify workflow dependencies: what must happen BEFORE main action
- Identify conditional workflows: IF-THEN patterns
- Rate risk_level based on domain and action (prescribe = high, search = low)
- Be conservative with confidence: 0.85+ only if very clear extraction

Requirement:
\"\"\"{requirement}\"\"\"

RESPOND WITH JSON ONLY."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize LLM parser
        
        Args:
            api_key: Claude API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found. "
                "Please set ANTHROPIC_API_KEY environment variable."
            )
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"
    
    def parse(self, requirement: str) -> StructuredIntent:
        """
        Parse requirement using LLM to extract structured intent
        
        Args:
            requirement: Raw requirement text
            
        Returns:
            StructuredIntent object with extracted data
            
        Raises:
            ValueError: If LLM response is invalid JSON
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": self.LLM_PROMPT.format(requirement=requirement)
                    }
                ],
                temperature=0.2  # Low temperature for consistency
            )
            
            content = response.content[0].text.strip()
            
            # Try to extract JSON from response
            # Sometimes LLM wraps in markdown code blocks
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content
            
            data = json.loads(json_str)
            
            # Validate required fields
            required_fields = ["actor", "action", "object", "domain", "intent_type"]
            for field in required_fields:
                if field not in data:
                    data[field] = self._get_default(field)
            
            return StructuredIntent(data)
        
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM returned invalid JSON: {e}")
        except anthropic.APIError as e:
            raise ValueError(f"Claude API error: {e}")
    
    @staticmethod
    def _get_default(field: str) -> Any:
        """Get default value for missing field"""
        defaults = {
            "actor": "User",
            "action": "perform action",
            "object": "system",
            "conditions": [],
            "constraints": [],
            "domain": "general",
            "intent_type": "simple_action",
            "dependencies": [],
            "risk_level": "medium",
            "confidence": 0.5
        }
        return defaults.get(field)


# Example usage and testing
if __name__ == "__main__":
    parser = LLMSemanticParser()
    
    # Test with healthcare requirement
    requirement = """
    Doctor must prescribe medication to patient after verifying:
    1. Patient allergies are checked
    2. No drug interactions are found
    3. Patient has valid insurance
    The system should prevent prescription of any drug the patient is allergic to.
    """
    
    print("Parsing healthcare requirement...")
    intent = parser.parse(requirement)
    
    print("\n=== EXTRACTED STRUCTURED INTENT ===")
    print(json.dumps(intent.to_dict(), indent=2))
    
    print("\n=== KEY FIELDS ===")
    print(f"Actor: {intent.actor}")
    print(f"Action: {intent.action}")
    print(f"Object: {intent.object_entity}")
    print(f"Domain: {intent.domain}")
    print(f"Intent Type: {intent.intent_type}")
    print(f"Risk Level: {intent.risk_level}")
    print(f"Confidence: {intent.confidence}")
    print(f"Dependencies: {intent.dependencies}")
    print(f"Conditions: {intent.conditions}")
