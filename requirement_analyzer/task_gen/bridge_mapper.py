"""
Bridge Mapper: LLM Semantic Parser → v2 AI Test Generator
Maps structured intent JSON from LLM to v2's RequirementEntity format
"""

from typing import Dict, List, Tuple, Any
from dataclasses import dataclass


@dataclass
class RequirementEntity:
    """Enhanced requirement entity that works with both v2 parser and LLM input"""
    original_text: str
    action: str
    objects: List[str]
    constraints: Dict[str, Any]
    domain: str
    is_security: bool = False
    
    # Enhanced fields from LLM semantic parser
    actor: str = None
    conditions: List[str] = None
    dependencies: List[Dict[str, str]] = None
    intent_type: str = None
    risk_level: str = None
    confidence: float = 0.85
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = []
        if self.dependencies is None:
            self.dependencies = []
        if self.intent_type is None:
            self.intent_type = "simple_action"
        if self.risk_level is None:
            self.risk_level = "medium"


class LLMTov2Bridge:
    """
    Maps LLM structured intent to v2 entity format
    Keeps v2 engine unchanged, just feeds it better input
    """
    
    @staticmethod
    def map_llm_to_entity(llm_data: Dict[str, Any], original_text: str) -> RequirementEntity:
        """
        Convert LLM structured intent to v2 RequirementEntity
        
        Args:
            llm_data: Structured intent from LLMSemanticParser
            original_text: Original requirement text
            
        Returns:
            RequirementEntity compatible with v2 engine
        """
        return RequirementEntity(
            original_text=original_text,
            action=llm_data.get("action", "process"),
            objects=[llm_data.get("object", "resource")],
            constraints=_extract_constraints_from_llm(llm_data),
            domain=llm_data.get("domain", "general"),
            is_security=_detect_security(llm_data),
            
            # LLM-specific enhanced fields
            actor=llm_data.get("actor", "User"),
            conditions=llm_data.get("conditions", []),
            dependencies=llm_data.get("dependencies", []),
            intent_type=llm_data.get("intent_type", "simple_action"),
            risk_level=llm_data.get("risk_level", "medium"),
            confidence=llm_data.get("confidence", 0.85),
        )
    
    @staticmethod
    def merge_v2_and_llm(v2_parsed: Dict[str, Any], llm_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge v2's parser output with LLM data (if using both)
        LLM data takes priority for structured fields
        
        Args:
            v2_parsed: Output from v2's SmartRequirementParser
            llm_data: Output from LLMSemanticParser
            
        Returns:
            Merged dict with best of both
        """
        merged = v2_parsed.copy()
        
        # LLM provides better:
        # - action (semantic understanding)
        # - domain (higher confidence)
        # - constraints (explicit vs pattern-based)
        merged["action"] = llm_data.get("action", v2_parsed.get("action"))
        merged["domain"] = llm_data.get("domain", v2_parsed.get("domain"))
        merged["is_security"] = llm_data.get("risk_level") == "high" or v2_parsed.get("is_security")
        
        # Add LLM-specific enrichment
        merged["llm_intent_type"] = llm_data.get("intent_type")
        merged["llm_dependencies"] = llm_data.get("dependencies", [])
        merged["llm_conditions"] = llm_data.get("conditions", [])
        merged["llm_confidence"] = llm_data.get("confidence", 0.0)
        
        return merged


def _extract_constraints_from_llm(llm_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract constraint structure from LLM data"""
    constraints = {}
    
    # Extract boundaries from conditions if numeric
    conditions = llm_data.get("conditions", [])
    boundaries = []
    for condition in conditions:
        import re
        nums = re.findall(r'\d+', condition)
        if nums:
            boundaries.extend([int(n) for n in nums])
    
    if boundaries:
        constraints["boundaries"] = boundaries
    
    # Extract explicit constraints
    explicit_constraints = llm_data.get("constraints", [])
    if explicit_constraints:
        constraints["explicit"] = explicit_constraints
    
    # Detect constraint type based on conditions
    all_conditions = " ".join(conditions).lower()
    if "before" in all_conditions or "first" in all_conditions:
        constraints["type"] = "prerequisite"
    elif "prevent" in all_conditions or "block" in all_conditions:
        constraints["type"] = "prevention"
    elif "within" in all_conditions or "before" in all_conditions:
        constraints["type"] = "deadline"
    
    return constraints


def _detect_security(llm_data: Dict[str, Any]) -> bool:
    """Detect if requirement has security implications"""
    risk_level = llm_data.get("risk_level", "low")
    if risk_level == "high":
        return True
    
    intent_type = llm_data.get("intent_type", "")
    if "security" in intent_type.lower():
        return True
    
    conditions = " ".join(llm_data.get("conditions", [])).lower()
    security_keywords = ["unauthorized", "prevent", "block", "protect", "secure", "authenticate"]
    return any(kw in conditions for kw in security_keywords)


# ============================================================================
# DEPENDENCY-AWARE STEP GENERATOR
# ============================================================================

class DependencyAwareStepGenerator:
    """
    Generate test steps with awareness of workflow dependencies
    This is the KEY upgrade for v3 - test cases understand prerequisites
    """
    
    @staticmethod
    def generate_steps_with_dependencies(
        entity: RequirementEntity,
        test_type: str,
        action: str,
        objects: List[str]
    ) -> List[str]:
        """
        Generate steps that respect dependencies and workflow
        
        Args:
            entity: RequirementEntity with LLM-enriched data
            test_type: Type of test (happy_path, negative, etc)
            action: Action being tested
            objects: Objects being acted upon
            
        Returns:
            List of test steps with proper ordering
        """
        steps = []
        
        # CRITICAL: Handle dependencies FIRST
        if entity.dependencies:
            for dep in entity.dependencies:
                prerequisite = dep.get("step", "")
                if prerequisite:
                    steps.append(f"Precondition: {prerequisite}")
                    steps.append(f"Verify: {prerequisite} is completed")
        
        # Handle conditions as prerequisites
        if entity.conditions:
            for condition in entity.conditions:
                if len(steps) < 3:  # Don't add too many prerequisites
                    steps.append(f"Verify condition: {condition}")
        
        # MAIN: Action step (depends on test type)
        main_object = objects[0] if objects else "resource"
        
        if test_type == "happy_path":
            steps.append(f"Execute: {entity.actor or 'User'} {action}s {main_object}")
            steps.append(f"Confirm: {action} completed successfully")
        
        elif test_type == "negative":
            steps.append(f"Attempt: {entity.actor or 'User'} {action}s {main_object} with invalid input")
            steps.append(f"Verify: System rejects the {action}")
            steps.append(f"Confirm: Appropriate error message is shown")
        
        elif test_type == "security":
            steps.append(f"Attempt: Unauthorized user {action}s {main_object}")
            steps.append(f"Verify: System blocks unauthorized {action}")
            steps.append(f"Confirm: Audit log records the attempt")
        
        elif test_type == "boundary_value":
            steps.append(f"Input: {main_object} with boundary values")
            steps.append(f"Execute: {action}")
            steps.append(f"Verify: System handles boundary correctly")
        
        elif test_type == "edge_case":
            steps.append(f"Input: {main_object} with extreme/unusual values")
            steps.append(f"Execute: {action}")
            steps.append(f"Verify: System handles edge case gracefully")
        
        # Postcondition step
        steps.append(f"Validate: All postconditions met")
        
        return steps


class SmartTestTypeInference:
    """
    Infer test types based on LLM intent understanding
    Replaces hardcoded loops with intelligent logic
    """
    
    @staticmethod
    def infer_test_types(entity: RequirementEntity) -> List[str]:
        """
        Intelligently determine which test types to generate
        
        Args:
            entity: RequirementEntity with semantic understanding
            
        Returns:
            List of test type strings
        """
        types = ["happy_path"]  # Always include happy path
        
        # Infer from intent type
        intent_type = entity.intent_type or ""
        
        if intent_type in ["security", "conditional_workflow"]:
            types.append("negative")
            types.append("security")
        
        if intent_type == "conditional_workflow":
            types.append("edge_case")
        
        # Infer from conditions (prerequisites = more negative cases)
        if entity.conditions and len(entity.conditions) > 1:
            types.append("negative")
        
        # Infer from constraints
        if entity.constraints.get("boundaries"):
            types.append("boundary_value")
        
        # Infer from domain + risk level
        if entity.domain in ["healthcare", "banking"] and entity.risk_level == "high":
            types.append("security")
        
        # Infer from dependencies (workflow = edge cases matter)
        if entity.dependencies and len(entity.dependencies) > 0:
            types.append("edge_case")
        
        # Remove duplicates while preserving order
        seen = set()
        return [t for t in types if not (t in seen or seen.add(t))]


# Example usage
if __name__ == "__main__":
    # Example LLM output
    llm_output = {
        "actor": "Doctor",
        "action": "prescribe",
        "object": "medication",
        "conditions": [
            "patient allergy must be checked",
            "no drug interactions found"
        ],
        "constraints": [
            "must verify insurance"
        ],
        "domain": "healthcare",
        "intent_type": "conditional_workflow",
        "dependencies": [
            {"step": "check patient allergies", "before": "prescribe medication"},
            {"step": "verify insurance coverage", "before": "prescribe medication"}
        ],
        "risk_level": "high",
        "confidence": 0.92
    }
    
    # Map to v2 entity
    entity = LLMTov2Bridge.map_llm_to_entity(llm_output, "Original requirement text here")
    
    print("=== Mapped Entity ===")
    print(f"Actor: {entity.actor}")
    print(f"Action: {entity.action}")
    print(f"Objects: {entity.objects}")
    print(f"Domain: {entity.domain}")
    print(f"Intent Type: {entity.intent_type}")
    print(f"Dependencies: {entity.dependencies}")
    print(f"Conditions: {entity.conditions}")
    
    # Infer test types
    test_types = SmartTestTypeInference.infer_test_types(entity)
    print(f"\n=== Inferred Test Types ===")
    print(f"Test Types: {test_types}")
    
    # Generate steps with dependency awareness
    print(f"\n=== Steps with Dependencies ===")
    for test_type in test_types[:2]:  # Show first 2
        steps = DependencyAwareStepGenerator.generate_steps_with_dependencies(
            entity, test_type, entity.action, entity.objects
        )
        print(f"\n{test_type.upper()} Steps:")
        for i, step in enumerate(steps, 1):
            print(f"  {i}. {step}")
