"""
Effort Estimation Engine v2 - Professional Grade
Provides production-ready effort estimation with explainability and confidence scoring
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import math


class EffortCategory(Enum):
    """Effort categories for easy classification"""
    QUICK = "quick"           # < 15 min
    LIGHT = "light"           # 15-30 min
    MEDIUM = "medium"         # 30-60 min
    HEAVY = "heavy"           # 60-120 min
    VERY_HEAVY = "very_heavy" # 120-240 min
    EPIC = "epic"             # > 240 min


@dataclass
class EffortFactors:
    """All factors contributing to effort estimation"""
    base_time: int = 10  # minutes
    step_count: int = 0
    step_complexity: int = 0  # additional minutes
    api_dependencies: int = 0
    data_complexity: str = "simple"  # simple, medium, complex
    test_type: str = "happy_path"
    domain: str = "general"
    risk_level: str = "MEDIUM"
    setup_minutes: int = 0
    external_dependencies: List[str] = field(default_factory=list)
    requires_mock_data: bool = False
    requires_database_setup: bool = False
    concurrent_risk: bool = False  # Race conditions, timing issues


@dataclass
class EffortBreakdown:
    """Detailed breakdown of effort components"""
    base_execution: int  # min
    step_complexity: int  # min
    domain_setup: int  # min
    api_integration: int  # min
    data_preparation: int  # min
    mocking_setup: int = 0  # min
    additional_validation: int = 0  # min
    
    def total(self) -> int:
        """Get total effort in minutes"""
        return (
            self.base_execution +
            self.step_complexity +
            self.domain_setup +
            self.api_integration +
            self.data_preparation +
            self.mocking_setup +
            self.additional_validation
        )


@dataclass
class EffortExplanation:
    """Human-readable explanation of effort estimate"""
    summary: str
    factors: List[str]
    breakdown_description: Dict[str, str]
    recommendations: List[str] = field(default_factory=list)


@dataclass
class EffortConfidence:
    """Confidence factors for the estimate"""
    overall_confidence: float  # 0.0-1.0
    data_availability: float = 0.8
    api_stability: float = 0.8
    step_clarity: float = 0.8
    domain_knowledge_coverage: float = 0.7
    external_dependency_risk: float = 0.9
    
    def get_confidence_factors(self) -> Dict[str, float]:
        """Return all confidence factors"""
        return {
            "data_availability": self.data_availability,
            "api_stability": self.api_stability,
            "step_clarity": self.step_clarity,
            "domain_knowledge_coverage": self.domain_knowledge_coverage,
            "external_dependency_risk": self.external_dependency_risk,
        }


@dataclass
class EffortEstimate:
    """Complete effort estimate with all details"""
    estimated_minutes: int
    estimated_hours: float
    confidence: EffortConfidence
    category: EffortCategory
    breakdown: EffortBreakdown
    explanation: EffortExplanation
    automation_feasibility: float = 0.7  # 0.0-1.0
    manual_portion_percent: int = 30  # %
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response"""
        return {
            "estimated_minutes": self.estimated_minutes,
            "estimated_hours": self.estimated_hours,
            "estimated_hours_readable": f"{self.estimated_hours:.1f}h",
            "confidence": {
                "overall": round(self.confidence.overall_confidence, 3),
                "factors": self.confidence.get_confidence_factors(),
            },
            "category": self.category.value,
            "breakdown": {
                "base_execution_min": self.breakdown.base_execution,
                "step_complexity_min": self.breakdown.step_complexity,
                "domain_setup_min": self.breakdown.domain_setup,
                "api_integration_min": self.breakdown.api_integration,
                "data_preparation_min": self.breakdown.data_preparation,
                "mocking_setup_min": self.breakdown.mocking_setup,
                "validation_min": self.breakdown.additional_validation,
                "total_min": self.breakdown.total(),
            },
            "explanation": {
                "summary": self.explanation.summary,
                "factors": self.explanation.factors,
                "breakdown_description": self.explanation.breakdown_description,
                "recommendations": self.explanation.recommendations,
            },
            "automation": {
                "feasibility_percent": round(self.automation_feasibility * 100),
                "manual_portion_percent": self.manual_portion_percent,
            },
        }


class EffortValidator:
    """Validates effort estimates for reasonableness"""
    
    MIN_EFFORT = 5  # minutes
    MAX_EFFORT = 480  # 8 hours
    
    def validate(self, estimate: int) -> Tuple[bool, Optional[str]]:
        """
        Validate effort estimate is reasonable
        Returns: (is_valid, error_message)
        """
        if estimate < self.MIN_EFFORT:
            return False, f"Effort too low ({estimate}min < {self.MIN_EFFORT}min minimum)"
        
        if estimate > self.MAX_EFFORT:
            return False, f"Effort too high ({estimate}min > {self.MAX_EFFORT}min maximum)"
        
        return True, None


class EffortExplainer:
    """Generates human-readable explanations"""
    
    def explain(self, factors: EffortFactors, breakdown: EffortBreakdown) -> EffortExplanation:
        """Generate detailed explanation"""
        
        summary = self._generate_summary(factors, breakdown)
        factor_explanations = self._explain_factors(factors, breakdown)
        breakdown_desc = self._explain_breakdown(factors, breakdown)
        recommendations = self._generate_recommendations(factors, breakdown)
        
        return EffortExplanation(
            summary=summary,
            factors=factor_explanations,
            breakdown_description=breakdown_desc,
            recommendations=recommendations,
        )
    
    def _generate_summary(self, factors: EffortFactors, breakdown: EffortBreakdown) -> str:
        """One-line summary"""
        total_min = breakdown.total()
        test_type = factors.test_type.replace("_", " ").title()
        
        if total_min < 15:
            pace = "Quick"
        elif total_min < 30:
            pace = "Light"
        elif total_min < 60:
            pace = "Moderate"
        elif total_min < 120:
            pace = "Substantial"
        else:
            pace = "Complex"
        
        domain_str = f" {factors.domain}" if factors.domain != "general" else ""
        
        return f"{pace} {test_type} test case{domain_str} requiring {int(total_min/60)}h {total_min%60}min"
    
    def _explain_factors(self, factors: EffortFactors, breakdown: EffortBreakdown) -> List[str]:
        """Explain each contributing factor"""
        explanations = []
        
        # Base execution
        explanations.append(
            f"Base execution time: {breakdown.base_execution} min (standard test run)"
        )
        
        # Steps
        if breakdown.step_complexity > 0:
            explanations.append(
                f"Step complexity: {breakdown.step_complexity} min "
                f"({factors.step_count} steps with decision points)"
            )
        
        # Domain setup
        if breakdown.domain_setup > 0:
            explanations.append(
                f"{factors.domain.capitalize()} setup: {breakdown.domain_setup} min "
                f"(domain-specific data & environment preparation)"
            )
        
        # API integration
        if breakdown.api_integration > 0:
            api_count = factors.api_dependencies
            explanations.append(
                f"API integration: {breakdown.api_integration} min "
                f"({api_count} API call{'s' if api_count > 1 else ''} + mock setup)"
            )
        
        # Data preparation
        if breakdown.data_preparation > 0:
            data_type = factors.data_complexity.capitalize()
            explanations.append(
                f"Data preparation: {breakdown.data_preparation} min "
                f"({data_type} data complexity - {factors.step_count} scenarios)"
            )
        
        # Mocking
        if breakdown.mocking_setup > 0:
            explanations.append(
                f"Mock setup: {breakdown.mocking_setup} min (external services stubbing)"
            )
        
        # Validation
        if breakdown.additional_validation > 0:
            explanations.append(
                f"Additional validation: {breakdown.additional_validation} min "
                f"({factors.risk_level} risk level requires extra verification)"
            )
        
        return explanations
    
    def _explain_breakdown(self, factors: EffortFactors, breakdown: EffortBreakdown) -> Dict[str, str]:
        """Explain effort breakdown percentages"""
        total = breakdown.total()
        if total == 0:
            return {}
        
        return {
            f"execution ({breakdown.base_execution * 100 // total}%)": "Running test steps",
            f"complexity ({breakdown.step_complexity * 100 // total}%)": "Handling test logic",
            f"setup ({breakdown.domain_setup * 100 // total}%)": "Environment preparation",
            f"integration ({breakdown.api_integration * 100 // total}%)": "API/external services",
            f"data ({breakdown.data_preparation * 100 // total}%)": "Test data creation",
        }
    
    def _generate_recommendations(self, factors: EffortFactors, breakdown: EffortBreakdown) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        total = breakdown.total()
        
        # Setup time is high?
        if breakdown.domain_setup > total * 0.3:
            recommendations.append(
                f"Setup takes {breakdown.domain_setup}min - consider creating reusable fixtures"
            )
        
        # Many API calls?
        if factors.api_dependencies > 2:
            recommendations.append(
                f"{factors.api_dependencies} APIs detected - use middleware mocks for faster execution"
            )
        
        # Complex data?
        if factors.data_complexity == "complex":
            recommendations.append(
                "Complex data setup - consider parameterized test data generation"
            )
        
        # High risk?
        if factors.risk_level == "CRITICAL":
            recommendations.append(
                "Critical risk level - schedule additional peer review time"
            )
        
        # Concurrent issues?
        if factors.concurrent_risk:
            recommendations.append(
                "Concurrent access risk detected - add timing buffers to test"
            )
        
        return recommendations


class EffortEstimationEngine:
    """
    Production-grade effort estimation engine
    Multi-factor analysis with explainability
    """
    
    def __init__(self):
        self.validator = EffortValidator()
        self.explainer = EffortExplainer()
    
    def estimate(self, test_case) -> EffortEstimate:
        """
        Estimate effort for a test case
        Args:
            test_case: TestCase object from test_case_builder
        Returns:
            EffortEstimate with full breakdown
        """
        
        # Extract factors from test case
        factors = self._extract_factors(test_case)
        
        # Calculate effort breakdown
        breakdown = self._calculate_breakdown(factors)
        
        # Validate
        is_valid, error = self.validator.validate(breakdown.total())
        if not is_valid:
            # Cap if out of range
            capped_total = max(
                self.validator.MIN_EFFORT,
                min(self.validator.MAX_EFFORT, breakdown.total())
            )
            breakdown = self._adjust_breakdown(breakdown, capped_total, factors)
        
        # Convert to hours
        hours = round(breakdown.total() / 60, 2)
        
        # Calculate category
        category = self._categorize(breakdown.total())
        
        # Calculate confidence
        confidence = self._assess_confidence(factors, breakdown, test_case)
        
        # Generate explanation
        explanation = self.explainer.explain(factors, breakdown)
        
        # Automation feasibility
        automation_pct = self._assess_automation(factors, test_case)
        manual_pct = int((1.0 - automation_pct) * 100)
        
        return EffortEstimate(
            estimated_minutes=breakdown.total(),
            estimated_hours=hours,
            confidence=confidence,
            category=category,
            breakdown=breakdown,
            explanation=explanation,
            automation_feasibility=automation_pct,
            manual_portion_percent=manual_pct,
        )
    
    def _extract_factors(self, test_case) -> EffortFactors:
        """Extract effort factors from test case"""
        
        # Step complexity (min per step varies)
        step_base = 5
        step_with_decision = 10
        step_with_validation = 12
        
        step_complexity = 0
        api_count = 0
        
        for step in test_case.steps:
            action_lower = step.action.lower()
            
            # Detect APIs
            if any(kw in action_lower for kw in ["api", "verify", "check", "insurance", "allergy", "validate"]):
                api_count += 1
                step_complexity += step_with_validation
            elif "expected" in action_lower or "decision" in action_lower:
                step_complexity += step_with_decision
            else:
                step_complexity += step_base
        
        # Data complexity
        test_data_count = len(test_case.test_data)
        if test_data_count > 10:
            data_complexity = "complex"
        elif test_data_count > 5:
            data_complexity = "medium"
        else:
            data_complexity = "simple"
        
        # Setup minutes
        setup_minutes = 0
        requires_db = False
        requires_mock_data = False
        
        # Determine domain from test case (default to general if not specified)
        domain = getattr(test_case, 'domain', 'general')
        
        if domain == "healthcare":
            setup_minutes += 20
            requires_db = True
            requires_mock_data = True
        elif domain == "banking":
            setup_minutes += 15
            requires_mock_data = True
        else:
            setup_minutes += 5
        
        # Check for concurrent risk
        concurrent_risk = any(
            kw in test_case.title.lower()
            for kw in ["concurrent", "race", "parallel", "simultaneous"]
        )
        
        # External dependencies
        external_deps = []
        if api_count > 0:
            external_deps.append(f"{api_count} APIs")
        if requires_db:
            external_deps.append("Database")
        if requires_mock_data:
            external_deps.append("Mock data")
        
        return EffortFactors(
            base_time=10,
            step_count=len(test_case.steps),
            step_complexity=step_complexity,
            api_dependencies=api_count,
            data_complexity=data_complexity,
            test_type=test_case.scenario_type,
            domain=domain,
            risk_level=test_case.risk_level,
            setup_minutes=setup_minutes,
            external_dependencies=external_deps,
            requires_mock_data=requires_mock_data,
            requires_database_setup=requires_db,
            concurrent_risk=concurrent_risk,
        )
    
    def _calculate_breakdown(self, factors: EffortFactors) -> EffortBreakdown:
        """Calculate detailed effort breakdown"""
        
        # Base execution
        base_exec = factors.base_time
        
        # Step complexity
        step_complexity = factors.step_complexity
        
        # Domain setup
        domain_setup = factors.setup_minutes
        
        # API integration
        api_integration = factors.api_dependencies * 10
        if factors.api_dependencies >= 3:
            api_integration += 10  # Compound complexity
        
        # Data preparation
        data_prep = 0
        if factors.data_complexity == "simple":
            data_prep = 5
        elif factors.data_complexity == "medium":
            data_prep = 15
        else:  # complex
            data_prep = 25
        
        # Mocking setup
        mocking = 0
        if factors.requires_mock_data:
            mocking = 10
        
        # Additional validation
        additional_val = 0
        if factors.risk_level == "CRITICAL":
            additional_val = 15
        elif factors.risk_level == "HIGH":
            additional_val = 10
        
        if factors.concurrent_risk:
            additional_val += 10
        
        # Apply test type multiplier to total
        # But calculate breakdown first
        breakdown = EffortBreakdown(
            base_execution=base_exec,
            step_complexity=step_complexity,
            domain_setup=domain_setup,
            api_integration=api_integration,
            data_preparation=data_prep,
            mocking_setup=mocking,
            additional_validation=additional_val,
        )
        
        return breakdown
    
    def _adjust_breakdown(self, breakdown: EffortBreakdown, target_total: int, factors: EffortFactors) -> EffortBreakdown:
        """Proportionally adjust breakdown to match target"""
        current_total = breakdown.total()
        if current_total == 0:
            return breakdown
        
        ratio = target_total / current_total
        
        return EffortBreakdown(
            base_execution=int(breakdown.base_execution * ratio),
            step_complexity=int(breakdown.step_complexity * ratio),
            domain_setup=int(breakdown.domain_setup * ratio),
            api_integration=int(breakdown.api_integration * ratio),
            data_preparation=int(breakdown.data_preparation * ratio),
            mocking_setup=int(breakdown.mocking_setup * ratio),
            additional_validation=int(breakdown.additional_validation * ratio),
        )
    
    def _categorize(self, minutes: int) -> EffortCategory:
        """Categorize effort level"""
        if minutes < 15:
            return EffortCategory.QUICK
        elif minutes < 30:
            return EffortCategory.LIGHT
        elif minutes < 60:
            return EffortCategory.MEDIUM
        elif minutes < 120:
            return EffortCategory.HEAVY
        elif minutes < 240:
            return EffortCategory.VERY_HEAVY
        else:
            return EffortCategory.EPIC
    
    def _assess_confidence(self, factors: EffortFactors, breakdown: EffortBreakdown, test_case) -> EffortConfidence:
        """Assess confidence in the estimate"""
        
        # Base confidence
        data_avail = 0.8
        api_stability = 0.85
        step_clarity = 0.9
        domain_knowledge = 0.7
        ext_dep_risk = 0.9
        
        # Adjust by factors
        if factors.data_complexity == "simple":
            data_avail = 0.95
        elif factors.data_complexity == "complex":
            data_avail = 0.6
        
        if factors.api_dependencies == 0:
            api_stability = 1.0
        elif factors.api_dependencies > 2:
            api_stability = 0.7
        
        if len(test_case.steps) > 10:
            step_clarity = 0.75
        elif len(test_case.steps) < 5:
            step_clarity = 0.95
        
        if factors.domain == "healthcare":
            domain_knowledge = 0.85
        elif factors.domain == "general":
            domain_knowledge = 0.6
        
        if len(factors.external_dependencies) > 2:
            ext_dep_risk = 0.7
        
        # Overall = geometric mean
        overall = (
            data_avail * api_stability * step_clarity * 
            domain_knowledge * ext_dep_risk
        ) ** (1/5)
        
        return EffortConfidence(
            overall_confidence=overall,
            data_availability=data_avail,
            api_stability=api_stability,
            step_clarity=step_clarity,
            domain_knowledge_coverage=domain_knowledge,
            external_dependency_risk=ext_dep_risk,
        )
    
    def _assess_automation(self, factors: EffortFactors, test_case) -> float:
        """Assess automation feasibility (0.0-1.0)"""
        
        automation = 0.5  # base
        
        # UI tests harder to automate
        if "ui" in test_case.description.lower():
            automation = 0.3
        # API tests very automatable
        elif "api" in test_case.description.lower():
            automation = 0.95
        # Integration tests moderate
        elif "integration" in test_case.scenario_type.lower():
            automation = 0.7
        # Security tests hard
        elif test_case.risk_level == "CRITICAL":
            automation = 0.4
        
        # Increase if few external deps
        if len(factors.external_dependencies) == 0:
            automation += 0.15
        # Decrease if many deps
        elif len(factors.external_dependencies) > 2:
            automation -= 0.15
        
        return max(0.0, min(1.0, automation))


# Test
if __name__ == "__main__":
    from test_case_builder import TestCaseBuilder, TestStep, TestCase
    
    # Mock test case
    test_case = TestCase(
        id="TC-APT-001",
        requirement_id="REQ-HC-001",
        title="Book appointment within 30-day window",
        description="Test appointment booking",
        scenario_type="happy_path",
        priority="HIGH",
        risk_level="MEDIUM",
        preconditions=["Patient authenticated"],
        test_data={"doctor": "A", "date": "tomorrow", "time": "10am"},
        steps=[
            TestStep(1, "Navigate to booking", "Page loads"),
            TestStep(2, "Select doctor", "Doctor selected"),
            TestStep(3, "Verify insurance API", "Insurance verified"),
            TestStep(4, "Check allergies API", "Allergies checked"),
            TestStep(5, "Confirm booking", "Booking confirmed"),
        ],
        expected_result="Appointment created",
        postconditions=["Logged in system"],
        trace_info={},
        domain_specific=True,
        estimated_effort_hours=0.5,
    )
    
    engine = EffortEstimationEngine()
    estimate = engine.estimate(test_case)
    
    print("EFFORT ESTIMATION")
    print("=" * 70)
    print(f"Estimate: {estimate.estimated_hours}h ({estimate.estimated_minutes} min)")
    print(f"Category: {estimate.category.value}")
    print(f"Confidence: {estimate.confidence.overall_confidence:.1%}")
    print(f"\nSummary: {estimate.explanation.summary}")
    print("\nFactors:")
    for factor in estimate.explanation.factors:
        print(f"  • {factor}")
    print("\nBreakdown:")
    for comp, desc in estimate.explanation.breakdown_description.items():
        print(f"  {comp}: {desc}")
    if estimate.explanation.recommendations:
        print("\nRecommendations:")
        for rec in estimate.explanation.recommendations:
            print(f"  • {rec}")
