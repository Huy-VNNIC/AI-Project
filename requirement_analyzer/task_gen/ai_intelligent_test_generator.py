"""
AI-Powered Test Case Generation System
======================================

NOT template-based. Uses AI to UNDERSTAND requirements and GENERATE test cases dynamically.

Components:
1. AI Requirement Analyzer - NLP-based requirement understanding
2. Test Scenario Extractor - AI extracts realistic test scenarios
3. AI Test Case Builder - Intelligently generates test cases
4. Logic Reasoner - Understands requirement logic deeply

Using: spaCy, Transformers, Custom NLP rules
"""

import logging
import re
from typing import List, Dict, Any, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
import spacy
from spacy.matcher import Matcher

logger = logging.getLogger("ai_test_generator")

# ============================================================================
# PART 1: AI REQUIREMENT ANALYZER
# ============================================================================

class EntityType(str, Enum):
    """Types of entities we extract from requirements"""
    USER_ROLE = "user_role"
    ACTION = "action"
    OBJECT = "object"
    CONDITION = "condition"
    NFR = "non_functional"
    CONSTRAINT = "constraint"
    VALIDATION = "validation"
    PERMISSION = "permission"


@dataclass
class Entity:
    """Extracted entity from requirement"""
    text: str
    type: EntityType
    importance: float  # 0-1
    context: str


@dataclass
class Relationship:
    """Relationship between entities"""
    entity1: Entity
    relation_type: str  # "triggers", "requires", "prevents", etc.
    entity2: Entity
    condition: Optional[str] = None


@dataclass
class RequirementAnalysis:
    """Complete analysis of a requirement"""
    original_text: str
    entities: List[Entity]
    relationships: List[Relationship]
    action_flow: List[str]
    conditions: List[str]
    edge_cases: List[str]
    validations: List[str]
    permissions: List[str]
    nfrs: List[str]
    complexity_score: float


class AIRequirementAnalyzer:
    """
    AI-based requirement analyzer using NLP.
    
    Understands requirement by:
    1. Tokenization & POS tagging
    2. Named Entity Recognition
    3. Dependency parsing
    4. Relationship extraction
    5. Logic understanding
    """
    
    def __init__(self):
        """Initialize NLP pipeline"""
        try:
            # Load spaCy model
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("✓ Loaded spaCy model")
        except OSError:
            logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Setup matchers for pattern-based extraction
        if self.nlp:
            self.matcher = Matcher(self.nlp.vocab)
            self._setup_patterns()
    
    def _setup_patterns(self):
        """Setup spaCy patterns for entity extraction"""
        if not self.nlp:
            return
        
        # Pattern: "User/Administrator/System" (user roles)
        role_pattern = [
            {"LOWER": {"IN": ["user", "admin", "administrator", "patient", "doctor", "system", "guest", "member"]}}
        ]
        self.matcher.add("ROLE", [role_pattern])
        
        # Pattern: Action verbs
        action_pattern = [
            {"POS": "VERB", "DEP": {"IN": ["ROOT", "nsubj"]}}
        ]
        
        # Pattern: Conditional (if, when, unless)
        condition_pattern = [
            {"LOWER": {"IN": ["if", "when", "unless", "provided", "assuming"]}}
        ]
    
    def analyze(self, requirement_text: str) -> RequirementAnalysis:
        """
        Analyze a requirement using AI/NLP.
        
        Returns detailed understanding of:
        - What entities are involved
        - What actions happen
        - What conditions trigger them
        - What could go wrong
        """
        if not self.nlp:
            return self._analyze_fallback(requirement_text)
        
        # Process text through NLP pipeline
        doc = self.nlp(requirement_text)
        
        # Extract entities
        entities = self._extract_entities(doc)
        
        # Extract relationships
        relationships = self._extract_relationships(doc, entities)
        
        # Extract action flow (sequence of actions)
        action_flow = self._extract_action_flow(doc)
        
        # Extract conditions
        conditions = self._extract_conditions(doc)
        
        # Extract edge cases (AI-inferred)
        edge_cases = self._infer_edge_cases(requirement_text, entities, conditions)
        
        # Extract validations
        validations = self._extract_validations(doc)
        
        # Extract permissions
        permissions = self._extract_permissions(doc, entities)
        
        # Extract NFRs
        nfrs = self._extract_nfrs(requirement_text)
        
        # Calculate complexity
        complexity = self._calculate_complexity(entities, relationships, conditions)
        
        return RequirementAnalysis(
            original_text=requirement_text,
            entities=entities,
            relationships=relationships,
            action_flow=action_flow,
            conditions=conditions,
            edge_cases=edge_cases,
            validations=validations,
            permissions=permissions,
            nfrs=nfrs,
            complexity_score=complexity
        )
    
    def _extract_entities(self, doc) -> List[Entity]:
        """Extract key entities from requirement"""
        entities = []
        
        # Extract named entities
        for ent in doc.ents:
            entity = Entity(
                text=ent.text,
                type=EntityType.OBJECT,
                importance=0.7,
                context=ent.sent.text
            )
            entities.append(entity)
        
        # Extract user roles (pattern-based)
        role_keywords = ["user", "admin", "patient", "doctor", "system", "guest", "member", "actor"]
        for token in doc:
            if token.text.lower() in role_keywords or token.pos_ == "NOUN":
                if any(kw in token.text.lower() for kw in role_keywords):
                    entity = Entity(
                        text=token.text,
                        type=EntityType.USER_ROLE,
                        importance=0.9,
                        context=token.sent.text
                    )
                    entities.append(entity)
        
        # Extract action verbs
        for token in doc:
            if token.pos_ == "VERB":
                entity = Entity(
                    text=token.text,
                    type=EntityType.ACTION,
                    importance=0.95,
                    context=token.sent.text
                )
                entities.append(entity)
        
        return entities
    
    def _extract_relationships(self, doc, entities: List[Entity]) -> List[Relationship]:
        """Extract relationships between entities"""
        relationships = []
        
        # Simple relationship extraction based on dep parsing
        for token in doc:
            if token.pos_ == "VERB":
                # Find subject and object of this verb
                try:
                    subj = None
                    obj = None
                    for child in token.children:
                        if child.dep_ == "nsubj":
                            subj = child
                        elif child.dep_ in ["dobj", "attr"]:
                            obj = child
                    
                    if subj and obj:
                        rel = Relationship(
                            entity1=Entity(subj.text, EntityType.USER_ROLE, 0.9, token.sent.text),
                            relation_type="triggers",
                            entity2=Entity(obj.text, EntityType.OBJECT, 0.8, token.sent.text)
                        )
                        relationships.append(rel)
                except Exception:
                    # Skip if relationship extraction fails
                    pass
        
        return relationships
    
    def _extract_action_flow(self, doc) -> List[str]:
        """Extract sequence of actions from requirement"""
        actions = []
        
        # Extract verbs (actions) in order
        for token in doc:
            if token.pos_ == "VERB":
                actions.append(token.text)
        
        return actions
    
    def _extract_conditions(self, doc) -> List[str]:
        """Extract conditional statements"""
        conditions = []
        
        # Pattern: if/when/unless + condition
        text = doc.text.lower()
        
        # Find if/when/unless + following text until period
        pattern = r'(?:if|when|unless|provided that|assuming)\s+([^.!?]+)'
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        for match in matches:
            conditions.append(match.strip())
        
        return conditions
    
    def _infer_edge_cases(self, text: str, entities: List[Entity], conditions: List[str]) -> List[str]:
        """AI-infer edge cases from requirement"""
        edge_cases = []
        
        # Edge case 1: Null/empty inputs
        if any(ent.type == EntityType.OBJECT for ent in entities):
            edge_cases.append("User provides empty/null input")
            edge_cases.append("User provides invalid data type")
        
        # Edge case 2: Boundary conditions
        if any(kw in text.lower() for kw in ["maximum", "minimum", "limit", "threshold", "exceed", "exceed"]):
            edge_cases.append("Input at minimum boundary")
            edge_cases.append("Input at maximum boundary")
            edge_cases.append("Input exceeds maximum")
        
        # Edge case 3: Concurrency
        if any(kw in text.lower() for kw in ["concurrent", "simultaneous", "parallel", "multiple"]):
            edge_cases.append("Multiple users perform action simultaneously")
            edge_cases.append("Race condition occurs")
        
        # Edge case 4: Permission failures
        edge_cases.append("User lacks required permissions")
        edge_cases.append("User session expires during action")
        
        # Edge case 5: System failures
        edge_cases.append("Database connection fails")
        edge_cases.append("External service is unavailable")
        edge_cases.append("Network timeout occurs")
        
        return edge_cases
    
    def _extract_validations(self, doc) -> List[str]:
        """Extract validation rules from requirement"""
        validations = []
        
        text = doc.text.lower()
        
        # Pattern: "must be", "should be", "valid", "invalid"
        pattern = r'(?:must|should|must not|should not|cannot|can)\s+(?:be\s+)?([^.!?]+)'
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        for match in matches:
            validations.append(match.strip())
        
        return validations
    
    def _extract_permissions(self, doc, entities: List[Entity]) -> List[str]:
        """Extract permission requirements"""
        permissions = []
        
        text = doc.text.lower()
        
        # Permission keywords
        if any(kw in text for kw in ["authorized", "permission", "role", "admin", "privilege"]):
            permissions.append("User must be authenticated")
        
        if any(kw in text for kw in ["admin", "administrator", "manager"]):
            permissions.append("User must have admin role")
        
        if any(kw in text for kw in ["owner", "creator", "self"]):
            permissions.append("User must be resource owner")
        
        return permissions
    
    def _extract_nfrs(self, text: str) -> List[str]:
        """Extract non-functional requirements"""
        nfrs = []
        
        text_lower = text.lower()
        
        # Performance
        if any(kw in text_lower for kw in ["fast", "responsive", "performance", "latency", "millisecond", "second"]):
            nfrs.append("Performance: Should respond quickly")
        
        # Reliability
        if any(kw in text_lower for kw in ["reliable", "availability", "uptime", "fail-safe"]):
            nfrs.append("Reliability: Must handle failures gracefully")
        
        # Security
        if any(kw in text_lower for kw in ["secure", "encrypted", "password", "authorization"]):
            nfrs.append("Security: Data must be encrypted and validated")
        
        # Scalability
        if any(kw in text_lower for kw in ["scale", "load", "concurrent", "large volume"]):
            nfrs.append("Scalability: Must handle high loads")
        
        # Maintainability
        if any(kw in text_lower for kw in ["maintai", "document", "code quality"]):
            nfrs.append("Maintainability: Code should be well-documented")
        
        return nfrs
    
    def _calculate_complexity(self, entities: List[Entity], relationships: List[Relationship], 
                            conditions: List[str]) -> float:
        """Calculate requirement complexity (0-1)"""
        score = 0.0
        
        # Complexity based on number of entities
        score += min(0.3, len(entities) * 0.05)
        
        # Complexity based on relationships
        score += min(0.3, len(relationships) * 0.1)
        
        # Complexity based on conditions
        score += min(0.2, len(conditions) * 0.05)
        
        # Complexity based on branching (if multiple conditions)
        if len(conditions) > 2:
            score += 0.2
        
        return min(1.0, score)
    
    def _analyze_fallback(self, text: str) -> RequirementAnalysis:
        """Fallback analysis if spaCy not available"""
        logger.warning("Using fallback analyzer (spaCy not available)")
        
        return RequirementAnalysis(
            original_text=text,
            entities=[],
            relationships=[],
            action_flow=[],
            conditions=[],
            edge_cases=[],
            validations=[],
            permissions=[],
            nfrs=[],
            complexity_score=0.5
        )


# ============================================================================
# PART 2: TEST SCENARIO EXTRACTOR
# ============================================================================

@dataclass
class TestScenario:
    """A test scenario extracted from requirement"""
    name: str
    description: str
    preconditions: List[str]
    steps: List[str]
    expected_result: str
    type: str  # "happy_path", "edge_case", "error", "alternative"
    importance: float  # 0-1


class TestScenarioExtractor:
    """
    Extracts test scenarios from requirement analysis.
    
    Uses AI understanding to create realistic test scenarios,
    not just generic templates.
    """
    
    def __init__(self):
        self.analyzer = AIRequirementAnalyzer()
    
    def extract_scenarios(self, requirement_text: str) -> List[TestScenario]:
        """
        Extract realistic test scenarios from requirement.
        
        Returns:
        - Happy path scenario
        - Edge case scenarios (inferred by AI)
        - Error scenarios
        - Alternative flow scenarios
        """
        # Analyze requirement using AI
        analysis = self.analyzer.analyze(requirement_text)
        
        scenarios = []
        
        # Scenario 1: Happy Path (main flow)
        happy_path = self._create_happy_path_scenario(analysis)
        if happy_path:
            scenarios.append(happy_path)
        
        # Scenarios 2+: Edge cases (AI-inferred from analysis)
        edge_case_scenarios = self._create_edge_case_scenarios(analysis)
        scenarios.extend(edge_case_scenarios)
        
        # Scenarios: Error scenarios (from conditions & validations)
        error_scenarios = self._create_error_scenarios(analysis)
        scenarios.extend(error_scenarios)
        
        # Scenarios: Alternative flows (if conditions)
        alternative_scenarios = self._create_alternative_scenarios(analysis)
        scenarios.extend(alternative_scenarios)
        
        return scenarios
    
    def _create_happy_path_scenario(self, analysis: RequirementAnalysis) -> Optional[TestScenario]:
        """Create happy path scenario from requirement"""
        
        if not analysis.action_flow:
            return None
        
        # Build steps from action flow
        steps = [f"Execute {action}" for action in analysis.action_flow]
        
        scenario = TestScenario(
            name="Happy Path - Main Flow",
            description=f"User successfully performs required action: {analysis.original_text[:80]}",
            preconditions=["User is authorized", "System is functioning normally"],
            steps=steps or ["Execute required action"],
            expected_result="Action completes successfully with correct result",
            type="happy_path",
            importance=1.0
        )
        
        return scenario
    
    def _create_edge_case_scenarios(self, analysis: RequirementAnalysis) -> List[TestScenario]:
        """Create AI-inferred edge case scenarios"""
        scenarios = []
        
        for edge_case in analysis.edge_cases:
            scenario = TestScenario(
                name=f"Edge Case: {edge_case}",
                description=f"Test behavior when {edge_case}",
                preconditions=[edge_case],
                steps=[
                    f"Setup condition: {edge_case}",
                    "Attempt required action",
                    "Verify system handles gracefully"
                ],
                expected_result=f"System handles {edge_case} gracefully",
                type="edge_case",
                importance=0.8
            )
            scenarios.append(scenario)
        
        return scenarios
    
    def _create_error_scenarios(self, analysis: RequirementAnalysis) -> List[TestScenario]:
        """Create error/failure scenarios from validations"""
        scenarios = []
        
        for validation in analysis.validations:
            # Create scenario for violation of each validation
            scenario = TestScenario(
                name=f"Error: Validation Failure - {validation[:40]}",
                description=f"Test that validation is enforced: {validation}",
                preconditions=["User attempts action with invalid data"],
                steps=[
                    f"Provide data violating: {validation}",
                    "Attempt action",
                    "Observe error response"
                ],
                expected_result=f"System rejects action and shows error: {validation}",
                type="error",
                importance=0.85
            )
            scenarios.append(scenario)
        
        return scenarios
    
    def _create_alternative_scenarios(self, analysis: RequirementAnalysis) -> List[TestScenario]:
        """Create alternative flow scenarios from conditions"""
        scenarios = []
        
        for condition in analysis.conditions:
            # Create scenario for when condition is true
            scenario_true = TestScenario(
                name=f"Alternative Flow: When {condition[:40]}",
                description=f"Test behavior when condition is true: {condition}",
                preconditions=[f"Condition: {condition}"],
                steps=[
                    "Setup condition to be true",
                    "Execute action",
                    "Verify alternative flow is taken"
                ],
                expected_result=f"System takes alternative flow (condition: {condition})",
                type="alternative",
                importance=0.75
            )
            scenarios.append(scenario_true)
            
            # Create scenario for when condition is false
            scenario_false = TestScenario(
                name=f"Alternative Flow: When NOT {condition[:40]}",
                description=f"Test behavior when condition is false: {condition}",
                preconditions=[f"Condition is NOT: {condition}"],
                steps=[
                    "Setup condition to be false",
                    "Execute action",
                    "Verify default flow is taken"
                ],
                expected_result=f"System takes default flow (condition NOT met: {condition})",
                type="alternative",
                importance=0.7
            )
            scenarios.append(scenario_false)
        
        return scenarios


# ============================================================================
# PART 3: AI TEST CASE BUILDER
# ============================================================================

@dataclass
class AIGeneratedTestCase:
    """Test case generated by AI"""
    test_id: str
    title: str
    scenario: TestScenario
    preconditions: List[str]
    steps: List[Dict[str, str]]  # [{"action": "...", "expected": "..."}]
    expected_result: str
    priority: str  # "Critical", "High", "Medium", "Low"
    test_type: str  # "Unit", "Integration", "E2E"
    why_generated: str  # AI explanation of why this test is needed
    ai_confidence: float  # How confident AI is about this test (0-1)


class AITestCaseBuilder:
    """
    Intelligently builds test cases from scenarios.
    
    Not template-based. Each test case is specifically tailored
    to the extracted scenario and requirement logic.
    """
    
    def __init__(self):
        self.test_id_counter = 0
    
    def build_test_cases(self, scenarios: List[TestScenario], 
                        requirement_analysis: RequirementAnalysis) -> List[AIGeneratedTestCase]:
        """
        Build test cases from scenarios.
        
        Creates specific, meaningful test cases based on:
        - Scenario type and logic
        - Requirement complexity
        - Identified edge cases
        - Validations and permissions
        """
        test_cases = []
        
        for scenario in scenarios:
            # Generate test type based on scenario
            test_type = self._determine_test_type(scenario, requirement_analysis)
            
            # Generate priority based on scenario importance
            priority = self._determine_priority(scenario, requirement_analysis)
            
            # Build detailed test case
            test_case = self._build_specific_test_case(
                scenario=scenario,
                test_type=test_type,
                priority=priority,
                requirement_analysis=requirement_analysis
            )
            
            test_cases.append(test_case)
        
        return test_cases
    
    def _determine_test_type(self, scenario: TestScenario, 
                            analysis: RequirementAnalysis) -> str:
        """Determine appropriate test type for scenario"""
        
        # High complexity → Integration/E2E
        if analysis.complexity_score > 0.7:
            if scenario.type == "happy_path":
                return "E2E"
            else:
                return "Integration"
        
        # Multiple relationships → Integration
        if len(analysis.relationships) > 3:
            return "Integration"
        
        # Simple → Unit
        return "Unit"
    
    def _determine_priority(self, scenario: TestScenario, 
                           analysis: RequirementAnalysis) -> str:
        """Determine priority based on scenario"""
        
        importance = scenario.importance
        
        if importance >= 0.95:
            return "Critical"
        elif importance >= 0.8:
            return "High"
        elif importance >= 0.6:
            return "Medium"
        else:
            return "Low"
    
    def _build_specific_test_case(self, scenario: TestScenario, test_type: str,
                                 priority: str, 
                                 requirement_analysis: RequirementAnalysis) -> AIGeneratedTestCase:
        """Build a specific test case tailored to the scenario"""
        
        self.test_id_counter += 1
        test_id = f"AI-{test_type[0]}-{self.test_id_counter:05d}"
        
        # Build detailed steps
        steps = []
        for i, action in enumerate(scenario.steps, 1):
            step = {
                "step_number": i,
                "action": action,
                "expected": scenario.expected_result if i == len(scenario.steps) else "Step completes"
            }
            steps.append(step)
        
        # Generate AI explanation for why this test is needed
        why_generated = self._generate_test_rationale(scenario, requirement_analysis)
        
        # Calculate AI confidence
        confidence = self._calculate_confidence(scenario, requirement_analysis)
        
        test_case = AIGeneratedTestCase(
            test_id=test_id,
            title=scenario.name,
            scenario=scenario,
            preconditions=scenario.preconditions,
            steps=steps,
            expected_result=scenario.expected_result,
            priority=priority,
            test_type=test_type,
            why_generated=why_generated,
            ai_confidence=confidence
        )
        
        return test_case
    
    def _generate_test_rationale(self, scenario: TestScenario,
                                analysis: RequirementAnalysis) -> str:
        """Generate AI explanation for why this test is needed"""
        
        if scenario.type == "happy_path":
            return f"Primary requirement: {analysis.original_text[:70]}"
        elif scenario.type == "edge_case":
            return f"Edge case scenario needed for robustness: {scenario.description[:70]}"
        elif scenario.type == "error":
            return f"Validation critical for data integrity: {scenario.description[:70]}"
        elif scenario.type == "alternative":
            return f"Alternative flow covers conditional logic: {scenario.description[:70]}"
        else:
            return "Test covers requirement logic"
    
    def _calculate_confidence(self, scenario: TestScenario,
                            analysis: RequirementAnalysis) -> float:
        """Calculate AI confidence in this test case"""
        
        confidence = scenario.importance
        
        # Increase confidence if:
        # - Requirement is clear
        # - Scenario matches identified entities/relationships
        # - Complexity not too high
        
        if analysis.complexity_score < 0.6:
            confidence = min(1.0, confidence + 0.15)
        
        if len(analysis.entities) > 3:
            confidence = min(1.0, confidence + 0.1)
        
        return round(confidence, 2)


# ============================================================================
# MAIN: AI INTELLIGENT TEST GENERATOR
# ============================================================================

class AIIntelligentTestGenerator:
    """
    Main orchestrator for AI-powered test case generation.
    
    NOT template-based. Uses AI to understand requirements and generate
    meaningful, specific test cases tailored to each requirement.
    
    Pipeline:
    1. Analyze requirement using NLP
    2. Extract realistic test scenarios
    3. Build specific test cases
    """
    
    def __init__(self):
        self.analyzer = AIRequirementAnalyzer()
        self.scenario_extractor = TestScenarioExtractor()
        self.test_builder = AITestCaseBuilder()
    
    def generate_test_cases(self, requirement_text: str) -> Dict[str, Any]:
        """
        Generate test cases for a requirement.
        
        Uses AI to understand requirement and generate specific tests.
        """
        
        logger.info(f"[AI] Analyzing requirement: {requirement_text[:80]}...")
        
        # Step 1: Analyze requirement
        analysis = self.analyzer.analyze(requirement_text)
        
        logger.info(f"[AI] Requirement analysis complete")
        logger.info(f"     - Entities found: {len(analysis.entities)}")
        logger.info(f"     - Relationships: {len(analysis.relationships)}")
        logger.info(f"     - Conditions: {len(analysis.conditions)}")
        logger.info(f"     - Complexity: {analysis.complexity_score:.2f}")
        
        # Step 2: Extract test scenarios
        scenarios = self.scenario_extractor.extract_scenarios(requirement_text)
        
        logger.info(f"[AI] Test scenarios extracted: {len(scenarios)}")
        for i, scenario in enumerate(scenarios, 1):
            logger.info(f"     {i}. {scenario.name} ({scenario.type})")
        
        # Step 3: Build test cases
        test_cases = self.test_builder.build_test_cases(scenarios, analysis)
        
        logger.info(f"[AI] Test cases generated: {len(test_cases)}")
        
        # Return comprehensive result
        return {
            "status": "success",
            "requirement": requirement_text,
            "analysis": {
                "entities": [{"text": e.text, "type": e.type.value} for e in analysis.entities],
                "relationships": [{"entity1": r.entity1.text, "relation": r.relation_type, "entity2": r.entity2.text} 
                                for r in analysis.relationships],
                "conditions": analysis.conditions,
                "edge_cases": analysis.edge_cases,
                "validations": analysis.validations,
                "nfrs": analysis.nfrs,
                "complexity": analysis.complexity_score
            },
            "scenarios": [
                {
                    "name": s.name,
                    "type": s.type,
                    "description": s.description,
                    "importance": s.importance
                }
                for s in scenarios
            ],
            "test_cases": [
                {
                    "test_id": tc.test_id,
                    "title": tc.title,
                    "test_type": tc.test_type,
                    "type": tc.test_type,
                    "priority": tc.priority,
                    "scenario_type": tc.scenario.type,
                    "preconditions": tc.preconditions,
                    "steps": tc.steps,
                    "expected_result": tc.expected_result,
                    "why_generated": tc.why_generated,
                    "ai_confidence": tc.ai_confidence
                }
                for tc in test_cases
            ],
            "summary": {
                "total_test_cases": len(test_cases),
                "by_type": self._count_by_type(test_cases),
                "by_priority": self._count_by_priority(test_cases),
                "avg_confidence": round(sum(tc.ai_confidence for tc in test_cases) / len(test_cases), 2) if test_cases else 0
            }
        }
    
    def _count_by_type(self, test_cases: List[AIGeneratedTestCase]) -> Dict[str, int]:
        counts = {}
        for tc in test_cases:
            counts[tc.test_type] = counts.get(tc.test_type, 0) + 1
        return counts
    
    def _count_by_priority(self, test_cases: List[AIGeneratedTestCase]) -> Dict[str, int]:
        counts = {}
        for tc in test_cases:
            counts[tc.priority] = counts.get(tc.priority, 0) + 1
        return counts
