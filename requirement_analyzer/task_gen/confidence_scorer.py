"""
Confidence Scorer - Real, explainable confidence scoring for test cases
Phase 4 of AI Test Case Generator v2
"""

from typing import Dict, Tuple, List
from dataclasses import dataclass
from requirement_analyzer.task_gen.test_case_builder import TestCase
from requirement_analyzer.task_gen.requirement_parser import RequirementObject, ActionType


@dataclass
class ConfidenceBreakdown:
    """Detailed confidence score breakdown"""

    total_score: float  # 0.0 - 1.0
    nlp_score: float  # Parse confidence
    coverage_score: float  # Test coverage
    domain_score: float  # Domain knowledge
    trace_score: float  # Traceability
    completeness_score: float  # Test structure completeness
    weights: Dict[str, float]  # Component weights
    explanation: str  # Human-readable explanation

    def __repr__(self):
        return f"""
╔══════════════════════════════════════════════════════════════╗
║ CONFIDENCE SCORE BREAKDOWN
╠══════════════════════════════════════════════════════════════╣
║ OVERALL SCORE: {self.total_score:.1%} ({'EXCELLENT' if self.total_score >= 0.85 else 'GOOD' if self.total_score >= 0.75 else 'FAIR' if self.total_score >= 0.60 else 'POOR'})
╠══════════════════════════════════════════════════════════════╣
║ COMPONENT SCORES:
║   NLP Parse Confidence:     {self.nlp_score:.1%} (weight: {self.weights.get('nlp', 0.0):.0%})
║   Test Coverage:           {self.coverage_score:.1%} (weight: {self.weights.get('coverage', 0.0):.0%})
║   Domain Knowledge:        {self.domain_score:.1%} (weight: {self.weights.get('domain', 0.0):.0%})
║   Traceability:           {self.trace_score:.1%} (weight: {self.weights.get('trace', 0.0):.0%})
║   Completeness:           {self.completeness_score:.1%} (weight: {self.weights.get('completeness', 0.0):.0%})
╠══════════════════════════════════════════════════════════════╣
║ EXPLANATION:
║   {self.explanation}
╚══════════════════════════════════════════════════════════════╝
"""


class ConfidenceScorer:
    """Calculate real, explainable confidence scores"""

    def __init__(self):
        # Default weights (can be customized)
        self.weights = {
            "nlp": 0.20,  # How well we parsed the requirement
            "coverage": 0.25,  # How well test covers scenarios
            "domain": 0.20,  # Domain-specific knowledge applied
            "trace": 0.20,  # Traceability to requirement
            "completeness": 0.15,  # Test structure completeness
        }

        # Healthcare high-risk keywords
        self.healthcare_critical = [
            "allergy",
            "dị ứng",
            "drug_interaction",
            "tương tác",
            "insurance",
            "bảo hiểm",
            "safety",
            "an toàn",
            "hipaa",
            "compliance",
            "tuân thủ",
        ]

    def calculate_confidence(
        self,
        requirement: RequirementObject,
        test_case: TestCase,
    ) -> ConfidenceBreakdown:
        """
        Calculate comprehensive confidence score
        Based on: NLP confidence, coverage, domain, traceability, completeness
        """

        # Component 1: NLP Parse Confidence (from requirement parser)
        nlp_score = requirement.parse_confidence

        # Component 2: Test Coverage Score
        coverage_score = self._calculate_coverage_score(test_case)

        # Component 3: Domain Knowledge Score
        domain_score = self._calculate_domain_score(requirement, test_case)

        # Component 4: Traceability Score
        trace_score = self._calculate_traceability_score(requirement, test_case)

        # Component 5: Completeness Score
        completeness_score = self._calculate_completeness_score(test_case)

        # Calculate weighted total
        total_score = (
            nlp_score * self.weights["nlp"]
            + coverage_score * self.weights["coverage"]
            + domain_score * self.weights["domain"]
            + trace_score * self.weights["trace"]
            + completeness_score * self.weights["completeness"]
        )

        # Cap at 1.0
        total_score = min(max(total_score, 0.0), 1.0)

        # Generate explanation
        explanation = self._generate_explanation(
            nlp_score,
            coverage_score,
            domain_score,
            trace_score,
            completeness_score,
            total_score,
            requirement,
            test_case,
        )

        return ConfidenceBreakdown(
            total_score=total_score,
            nlp_score=nlp_score,
            coverage_score=coverage_score,
            domain_score=domain_score,
            trace_score=trace_score,
            completeness_score=completeness_score,
            weights=self.weights,
            explanation=explanation,
        )

    def _calculate_coverage_score(self, test_case: TestCase) -> float:
        """
        Coverage Score: How well does test cover requirement scenarios?
        Factors:
        - Number of test steps (more detailed = better coverage)
        - Preconditions specified
        - Test data diversity
        - Expected result clarity
        """
        score = 0.5

        # Factor 1: Test steps (0.0 - 0.25)
        step_count = len(test_case.steps)
        score += min(step_count / 8 * 0.25, 0.25)  # Max at 8 steps

        # Factor 2: Preconditions (0.0 - 0.15)
        precond_count = len(test_case.preconditions)
        score += min(precond_count / 4 * 0.15, 0.15)  # Max at 4 preconditions

        # Factor 3: Test data specificity (0.0 - 0.15)
        test_data_filled = len([v for v in test_case.test_data.values() if v])
        score += min(test_data_filled / 5 * 0.15, 0.15)

        # Factor 4: Expected result detail (0.0 - 0.10)
        expected_lines = len(test_case.expected_result.split("\n"))
        score += min(expected_lines / 3 * 0.10, 0.10)

        return min(max(score, 0.0), 1.0)

    def _calculate_domain_score(self, requirement: RequirementObject, test_case: TestCase) -> float:
        """
        Domain Score: How much domain-specific knowledge is applied?
        Factors:
        - Domain specificity (generic vs domain-aware)
        - Critical flows addressed
        - Risk level consideration
        - Constraint handling
        """
        score = 0.5

        # Factor 1: Domain specificity
        if test_case.domain_specific:
            score += 0.20
        else:
            score += 0.05

        # Factor 2: Healthcare-specific
        if requirement.domain == "healthcare":
            original_text_lower = requirement.original_text.lower()

            # Check for critical healthcare flows
            is_critical = any(
                keyword in original_text_lower for keyword in self.healthcare_critical
            )

            if is_critical:
                # Critical flow test should have strong domain coverage
                if test_case.risk_level == "HIGH":
                    score += 0.20
                else:
                    score += 0.10
            else:
                score += 0.05

        # Factor 3: Constraint handling
        constraint_count = len(requirement.constraints)
        if constraint_count > 0:
            score += min(constraint_count / 3 * 0.15, 0.15)

        # Factor 4: Risk level alignment
        if test_case.risk_level == requirement.risk_level:
            score += 0.10

        return min(max(score, 0.0), 1.0)

    def _calculate_traceability_score(self, requirement: RequirementObject, test_case: TestCase) -> float:
        """
        Traceability Score: How well is test traceable back to requirement?
        Factors:
        - Requirement ID linked
        - Source requirement captured
        - Actor/Action/Object mapped
        - Constraint coverage
        """
        score = 0.5

        trace_info = test_case.trace_info

        # Factor 1: Requirement ID present
        if trace_info.get("requirement_id") and trace_info.get("source_requirement"):
            score += 0.25
        else:
            score -= 0.10

        # Factor 2: Actor/Action/Object explicitly mapped
        mapped_fields = [
            "actor",
            "action",
            "object",
        ]
        mapped_count = sum(1 for field in mapped_fields if trace_info.get(field))
        score += mapped_count / 3 * 0.25

        # Factor 3: Constraints explicitly referenced
        constraints = trace_info.get("constraints", [])
        if constraints:
            score += 0.15
        else:
            score += 0.05

        # Factor 4: Test title clarity
        title_has_action = any(
            verb in test_case.title.lower()
            for verb in ["create", "delete", "update", "read", "book", "schedule"]
        )
        if title_has_action:
            score += 0.10

        return min(max(score, 0.0), 1.0)

    def _calculate_completeness_score(self, test_case: TestCase) -> float:
        """
        Completeness Score: How complete/well-structured is the test case?
        Factors:
        - All fields populated
        - Steps are detailed
        - Preconditions/postconditions present
        - Test data provided
        """
        score = 0.5

        # Factor 1: All main fields present
        required_fields = [
            test_case.id,
            test_case.title,
            test_case.expected_result,
        ]
        filled_fields = sum(1 for field in required_fields if field)
        score += filled_fields / len(required_fields) * 0.20

        # Factor 2: Steps detail
        steps_with_expected = sum(
            1 for step in test_case.steps if step.expected and step.action
        )
        if test_case.steps:
            score += min(steps_with_expected / len(test_case.steps), 1.0) * 0.20

        # Factor 3: Pre/postconditions
        has_precond = len(test_case.preconditions) > 0
        has_postcond = len(test_case.postconditions) > 0
        score += (0.15 if has_precond else 0.05) + (0.15 if has_postcond else 0.05)

        # Factor 4: Test data quantity & specificity
        test_data_count = len([v for v in test_case.test_data.values() if v])
        score += min(test_data_count / 4 * 0.15, 0.15)

        # Factor 5: Effort estimation
        if test_case.estimated_effort_hours > 0:
            score += 0.10

        return min(max(score, 0.0), 1.0)

    def _generate_explanation(
        self,
        nlp_score: float,
        coverage_score: float,
        domain_score: float,
        trace_score: float,
        completeness_score: float,
        total_score: float,
        requirement: RequirementObject,
        test_case: TestCase,
    ) -> str:
        """Generate human-readable explanation of confidence score"""

        explanations = []

        # NLP explanation
        if nlp_score > 0.8:
            explanations.append(
                f"✓ Requirement parsed with high clarity (NLP: {nlp_score:.0%})"
            )
        elif nlp_score > 0.6:
            explanations.append(
                f"~ Requirement has some ambiguity (NLP: {nlp_score:.0%})"
            )
        else:
            explanations.append(
                f"✗ Requirement parsing has limitations (NLP: {nlp_score:.0%})"
            )

        # Coverage explanation
        step_count = len(test_case.steps)
        if coverage_score > 0.8:
            explanations.append(
                f"✓ Test has comprehensive coverage ({step_count} detailed steps)"
            )
        else:
            explanations.append(f"~ Test has basic coverage ({step_count} steps)")

        # Domain explanation
        if test_case.domain_specific and requirement.domain != "general":
            explanations.append(
                f"✓ Domain-specific testing applied ({requirement.domain})"
            )
            if requirement.risk_level == "HIGH":
                explanations.append(
                    f"✓ Critical requirement - enhanced testing for {requirement.risk_level} risk"
                )
        else:
            explanations.append("~ Generic testing approach")

        # Traceability explanation
        if trace_score > 0.85:
            explanations.append(
                f"✓ Strong traceability to requirement {test_case.requirement_id}"
            )
        else:
            explanations.append(
                f"~ Moderate traceability to requirement {test_case.requirement_id}"
            )

        # Completeness explanation
        if completeness_score > 0.85:
            explanations.append("✓ Test case structure complete and well-defined")
        elif completeness_score > 0.65:
            explanations.append("~ Test case could be more detailed")
        else:
            explanations.append("✗ Test case missing important details")

        # Overall assessment
        if total_score >= 0.85:
            explanations.append(
                f"\n🎯 OVERALL: High-confidence test case, ready for execution"
            )
        elif total_score >= 0.70:
            explanations.append(f"\n👍 OVERALL: Good test case, minor improvements suggested")
        elif total_score >= 0.55:
            explanations.append(f"\n⚠️  OVERALL: Test case acceptable but needs review")
        else:
            explanations.append(f"\n❌ OVERALL: Test case needs significant rework")

        return "\n".join(explanations)


# Test
if __name__ == "__main__":
    from requirement_parser import RequirementParser
    from scenario_generator import ScenarioGenerator
    from test_case_builder import TestCaseBuilder

    parser = RequirementParser()
    generator = ScenarioGenerator()
    builder = TestCaseBuilder()
    scorer = ConfidenceScorer()

    requirement = parser.parse(
        "Hệ thống phải cho phép đặt lịch khám trước 30 ngày có kiểm tra tương tác thuốc"
    )
    scenarios = generator.generate_scenarios(requirement)

    print("=" * 70)
    print("CONFIDENCE SCORING DEMO")
    print("=" * 70)

    for i, scenario in enumerate(scenarios[:2], 1):
        tc = builder.build_test_case(requirement, scenario, f"REQ-HC-001")
        confidence = scorer.calculate_confidence(requirement, tc)

        print(f"\n{i}. Test Case: {tc.title}")
        print(confidence)
