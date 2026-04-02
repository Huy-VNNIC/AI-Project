"""
AI Test Case Generator v2 Orchestrator
Orchestrates all phases: Parser → Scenario → Builder → Scorer + Domain KB
"""

from typing import List, Dict, Any
from dataclasses import dataclass
import hashlib
import json
from requirement_analyzer.task_gen.requirement_parser import RequirementParser, RequirementObject
from requirement_analyzer.task_gen.scenario_generator import ScenarioGenerator
from requirement_analyzer.task_gen.test_case_builder import TestCaseBuilder, TestCase
from requirement_analyzer.task_gen.confidence_scorer import ConfidenceScorer, ConfidenceBreakdown
from requirement_analyzer.task_gen.healthcare_domain import HealthcareDomainKB


@dataclass
class GeneratedTestSuite:
    """Complete test suite for a set of requirements"""

    requirements: List[RequirementObject]
    test_cases: List[TestCase]
    confidence_scores: List[ConfidenceBreakdown]
    summary: Dict[str, Any]


class AITestCaseGeneratorV2:
    """
    Complete AI Test Case Generator v2
    Production-ready test case generation from requirements
    """

    def __init__(self):
        self.parser = RequirementParser()
        self.generator = ScenarioGenerator()
        self.builder = TestCaseBuilder()
        self.scorer = ConfidenceScorer()
        self.healthcare_kb = HealthcareDomainKB()

    def generate(
        self,
        requirements: List[str],
        max_test_cases: int = 10,
        confidence_threshold: float = 0.50,
    ) -> Dict[str, Any]:
        """
        Main generation pipeline
        Input: List of requirements
        Output: Test cases + confidence scores + traceability
        """

        results = {
            "status": "success",
            "requirements_count": len(requirements),
            "test_cases": [],
            "summary": {
                "total_test_cases": 0,
                "avg_confidence": 0.0,
                "avg_effort_hours": 0.0,
                "generation_time_ms": 0.0,
                "critical_flows_identified": [],
                "domain_distribution": {},
            },
            "errors": [],
        }

        test_cases_generated = []
        confidences = []
        total_effort = 0.0
        test_case_hashes = set()  # For deduplication

        try:
            for req_idx, requirement_text in enumerate(requirements, 1):
                try:
                    # Phase 1: Parse requirement
                    requirement = self.parser.parse(requirement_text)

                    # QUALITY GATE: Check if requirement is too ambiguous
                    if requirement.parse_confidence < 0.65:
                        results["errors"].append(
                            f"⚠️  SKIPPED (ambiguous): '{requirement_text}' - "
                            f"NLP confidence {requirement.parse_confidence:.1%} < 65%. "
                            f"Please specify: actor, action, and expected behavior clearly."
                        )
                        continue

                    # Check for healthcare critical flows
                    critical_info = self.healthcare_kb.is_critical_flow(
                        requirement_text
                    )
                    if critical_info["is_critical"]:
                        results["summary"]["critical_flows_identified"].append(
                            {
                                "requirement": requirement_text,
                                "flow_type": critical_info["flow"]["description"],
                                "risk_level": critical_info["risk_level"],
                            }
                        )

                    # Update domain distribution
                    domain = requirement.domain
                    results["summary"]["domain_distribution"][domain] = (
                        results["summary"]["domain_distribution"].get(domain, 0) + 1
                    )

                    req_id = f"REQ-{requirement.domain[:2].upper()}-{str(req_idx).zfill(3)}"

                    # Phase 2: Generate scenarios
                    scenarios = self.generator.generate_scenarios(requirement)

                    # Phase 3: Build test cases
                    for scenario_idx, scenario in enumerate(scenarios):
                        if len(test_cases_generated) >= max_test_cases:
                            break

                        tc = self.builder.build_test_case(requirement, scenario, req_id)

                        # Phase 4: Score confidence
                        confidence = self.scorer.calculate_confidence(requirement, tc)

                        # Filter by confidence threshold
                        if confidence.total_score >= confidence_threshold:
                            # DEDUPLICATION: Hash test case steps content
                            steps_content = json.dumps(
                                [(s.action, s.expected) for s in tc.steps],
                                sort_keys=True
                            )
                            content_hash = hashlib.md5(steps_content.encode()).hexdigest()
                            
                            if content_hash not in test_case_hashes:
                                test_case_hashes.add(content_hash)
                                test_cases_generated.append(tc)
                                confidences.append(confidence)
                                total_effort += tc.estimated_effort_hours
                            else:
                                # Duplicate test case detected - skip it
                                pass

                except Exception as e:
                    results["errors"].append(
                        f"Error processing requirement '{requirement_text}': {str(e)}"
                    )
                    continue

            # Build output
            results["test_cases"] = [
                self._format_test_case(tc, conf)
                for tc, conf in zip(test_cases_generated, confidences)
            ]

            # Update summary
            if test_cases_generated:
                results["summary"]["total_test_cases"] = len(test_cases_generated)
                results["summary"]["avg_confidence"] = (
                    sum(c.total_score for c in confidences) / len(confidences)
                )
                results["summary"]["avg_effort_hours"] = round(
                    total_effort / len(test_cases_generated), 2
                )

        except Exception as e:
            results["status"] = "error"
            results["errors"].append(f"Critical error: {str(e)}")

        return results

    def _format_test_case(self, test_case: TestCase, confidence: ConfidenceBreakdown) -> Dict:
        """Format test case for JSON response"""
        result = {
            "id": test_case.id,
            "requirement_id": test_case.requirement_id,
            "title": test_case.title,
            "description": test_case.description,
            "scenario_type": test_case.scenario_type,
            "priority": test_case.priority,
            "risk_level": test_case.risk_level,
            "domain_specific": test_case.domain_specific,
            "estimated_effort_hours": test_case.estimated_effort_hours,
            "preconditions": test_case.preconditions,
            "test_data": test_case.test_data,
            "steps": [
                {
                    "order": s.order,
                    "action": s.action,
                    "expected": s.expected,
                    "actor": s.actor,
                    "tool": s.tool,
                }
                for s in test_case.steps
            ],
            "expected_result": test_case.expected_result,
            "postconditions": test_case.postconditions,
            "traceability": {
                "source_requirement": test_case.trace_info["source_requirement"],
                "requirement_id": test_case.trace_info["requirement_id"],
                "mapped_fields": {
                    "actor": test_case.trace_info["actor"],
                    "action": test_case.trace_info["action"],
                    "object": test_case.trace_info["object"],
                },
                "constraints": test_case.trace_info["constraints"],
            },
            "confidence": {
                "overall_score": round(confidence.total_score, 3),
                "score_percentage": f"{confidence.total_score:.1%}",
                "components": {
                    "nlp_parsing": round(confidence.nlp_score, 3),
                    "test_coverage": round(confidence.coverage_score, 3),
                    "domain_knowledge": round(confidence.domain_score, 3),
                    "traceability": round(confidence.trace_score, 3),
                    "completeness": round(confidence.completeness_score, 3),
                },
                "explanation": confidence.explanation,
            },
        }
        
        # Include detailed effort breakdown if available
        if test_case.effort_estimate:
            result["effort"] = test_case.effort_estimate.to_dict()
        
        return result


# Demo
if __name__ == "__main__":
    generator = AITestCaseGeneratorV2()

    test_requirements = [
        "Hệ thống phải cho phép bệnh nhân đặt lịch khám trước 30 ngày",
        "Hệ thống phải kiểm tra dị ứng before prescribing medication",
        "Bác sĩ phải có thể xem kết quả xét nghiệm",
    ]

    print("=" * 80)
    print("AI TEST CASE GENERATOR v2 - DEMO")
    print("=" * 80)

    results = generator.generate(test_requirements, max_test_cases=10)

    print(f"\n✅ Generated {results['summary']['total_test_cases']} test cases")
    print(
        f"📊 Average Confidence: {results['summary']['avg_confidence']:.1%}"
    )
    print(
        f"⏱️  Average Effort: {results['summary']['avg_effort_hours']}h per case"
    )
    print(
        f"\n🏥 Critical Flows Identified: {len(results['summary']['critical_flows_identified'])}"
    )

    for tc in results["test_cases"][:2]:
        print("\n" + "=" * 80)
        print(f"\nTest Case: {tc['id']} - {tc['title']}")
        print(f"Requirement: {tc['requirement_id']}")
        print(f"Priority: {tc['priority']} | Risk: {tc['risk_level']}")
        print(f"Confidence: {tc['confidence']['score_percentage']} ({tc['confidence']['overall_score']:.3f})")
        print(f"\nExplanation:\n{tc['confidence']['explanation']}")
        print(f"\nSteps ({len(tc['steps'])}):")
        for step in tc["steps"]:
            print(f"  {step['order']}. {step['action']}")
