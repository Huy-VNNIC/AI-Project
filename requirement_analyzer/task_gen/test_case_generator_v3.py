"""
AI Test Case Generator v3 - PRODUCTION GRADE
Smart, actionable test case generation from requirements
Tier 1: Essential improvements for production quality
"""

from typing import List, Dict, Any
from dataclasses import dataclass
import hashlib
import json
from requirement_analyzer.task_gen.requirement_parser import RequirementParser
from requirement_analyzer.task_gen.test_case_builder_production import ProductionTestCaseBuilder


@dataclass
class TestGenerationResult:
    """Result of test generation"""
    requirement_text: str
    requirement_id: str
    test_cases: List[Dict[str, Any]]
    quality_flags: List[str] = None
    is_actionable: bool = True
    generation_quality_score: float = 0.0


class AITestCaseGeneratorV3:
    """
    Production-Grade Test Case Generator
    
    Key Improvements over v2:
    ✓ Concrete test data (not generic)
    ✓ Real input/output pairs (not templates)
    ✓ Boundary value analysis with actual tests
    ✓ State machine test generation
    ✓ Requirement quality validation
    ✓ Smart deduplication by logic
    ✓ Actionable, usable test cases
    """

    def __init__(self):
        self.parser = RequirementParser()
        self.builder = ProductionTestCaseBuilder()
        self.test_history = {}  # Track generated tests to avoid duplication

    def generate(
        self,
        requirements: List[str],
        max_test_cases_per_req: int = 8,
        enable_quality_validation: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate production-grade test cases from requirements
        
        Returns:
            {
                "status": "success" | "warning" | "error",
                "requirements_analyzed": N,
                "total_test_cases_generated": M,
                "results": [
                    {
                        "requirement_id": "REQ-001",
                        "requirement_text": "...",
                        "test_cases": [...],
                        "quality_issues": [...],
                        "is_actionable": true/false,
                    }
                ],
                "summary": {
                    "total_requirements": N,
                    "actionable_requirements": M,
                    "ambiguous_requirements": K,
                    "total_test_cases": T,
                    "avg_test_quality": 0.XX,
                    "coverage_metrics": {...}
                }
            }
        """

        results = {
            "status": "success",
            "timestamp": None,
            "requirements_analyzed": len(requirements),
            "results": [],
            "summary": {
                "total_requirements": len(requirements),
                "actionable_requirements": 0,
                "ambiguous_requirements": 0,
                "flagged_for_clarification": 0,
                "total_test_cases_generated": 0,
                "avg_test_quality_score": 0.0,
                "test_cases_by_type": {},
                "requirements_quality_issues": [],
            },
            "errors": [],
        }

        all_test_cases = []
        quality_scores = []
        ambiguous_count = 0

        try:
            for req_idx, requirement_text in enumerate(requirements, 1):
                try:
                    # Parse requirement
                    requirement = self.parser.parse(requirement_text)
                    req_id = f"REQ-{requirement.domain[:2].upper()}-{str(req_idx).zfill(3)}"

                    # Generate test cases using production builder
                    test_cases = self.builder.generate_test_cases_smart(
                        requirement,
                        req_id,
                        max_test_cases_per_req,
                    )

                    # Check if requirement is ambiguous
                    is_ambiguous = any(tc.get("status") == "⚠️  UNCLEAR_REQUIREMENT" for tc in test_cases)

                    if is_ambiguous:
                        ambiguous_count += 1
                        results["summary"]["ambiguous_requirements"] += 1
                        # Flag for clarification but still include
                        results["summary"]["requirements_quality_issues"].append({
                            "requirement_id": req_id,
                            "text": requirement_text,
                            "issues": test_cases[0].get("message", "Ambiguous"),
                        })

                    # Track test cases
                    for tc in test_cases:
                        if tc.get("type") != "requirement_quality_check":
                            all_test_cases.append(tc)
                            quality_scores.append(tc.get("confidence", 0.0))

                            # Count by type
                            tc_type = tc.get("type", "unknown")
                            results["summary"]["test_cases_by_type"][tc_type] = (
                                results["summary"]["test_cases_by_type"].get(tc_type, 0) + 1
                            )

                    # Mark as actionable
                    is_actionable = not is_ambiguous
                    if is_actionable:
                        results["summary"]["actionable_requirements"] += 1

                    # Add to results
                    results["results"].append({
                        "requirement_id": req_id,
                        "requirement_text": requirement_text,
                        "test_cases": test_cases,
                        "is_actionable": is_actionable,
                        "quality_issues": [] if not is_ambiguous else ["Requirement is ambiguous"],
                    })

                except Exception as e:
                    results["errors"].append(f"Error processing requirement '{requirement_text}': {str(e)}")
                    continue

            # Final summary
            results["summary"]["total_test_cases_generated"] = len(all_test_cases)
            results["summary"]["flagged_for_clarification"] = ambiguous_count

            if quality_scores:
                results["summary"]["avg_test_quality_score"] = sum(quality_scores) / len(quality_scores)

            # Set status based on ambiguities
            if ambiguous_count > len(requirements) * 0.3:  # More than 30% ambiguous
                results["status"] = "warning"
                results["summary"]["warning"] = f"{ambiguous_count} out of {len(requirements)} requirements are ambiguous"

        except Exception as e:
            results["status"] = "error"
            results["errors"].append(f"Critical error in test generation: {str(e)}")

        return results

    def generate_brief(
        self,
        requirements: List[str],
        max_test_cases: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Generate test cases and return flat list (for API responses)
        """
        full_result = self.generate(requirements, max_test_cases_per_req=8)

        # Flatten results
        test_cases = []
        for req_result in full_result.get("results", []):
            test_cases.extend(req_result.get("test_cases", []))

        return test_cases[:max_test_cases]


# Standalone function for easy integration
def generate_test_cases_production(
    requirements: List[str],
    max_tests: int = 50,
) -> Dict[str, Any]:
    """
    Quick function to generate production-grade test cases
    
    Args:
        requirements: List of requirement text strings
        max_tests: Maximum test cases to generate
        
    Returns:
        Dictionary with test cases and metadata
    """
    generator = AITestCaseGeneratorV3()
    return generator.generate(requirements, max_test_cases_per_req=8)


# Demo/Testing
if __name__ == "__main__":
    from requirement_analyzer.file_util import RequirementFileParser

    # Test requirements
    test_requirements = [
        "Hệ thống phải cho phép bệnh nhân đặt lịch khám trước 30 ngày không được vượt quá",
        "Hệ thống phải kiểm tra dị ứng trước khi kê đơn thuốc",
        "Bác sĩ phải có thể xem kết quả xét nghiệm",
        "Hệ thống phải nhanh",  # This should be flagged as ambiguous
    ]

    print("=" * 80)
    print("AI TEST CASE GENERATOR v3 - PRODUCTION GRADE")
    print("=" * 80)

    generator = AITestCaseGeneratorV3()
    results = generator.generate(test_requirements)

    print(f"\n🎯 Results:")
    print(f"  Total requirements: {results['summary']['total_requirements']}")
    print(f"  Actionable: {results['summary']['actionable_requirements']}")
    print(f"  Ambiguous (flagged): {results['summary']['ambiguous_requirements']}")
    print(f"  Total test cases: {results['summary']['total_test_cases_generated']}")
    print(f"  Avg quality: {results['summary']['avg_test_quality_score']:.1%}")

    print(f"\n📊 Test cases by type:")
    for tc_type, count in results['summary']['test_cases_by_type'].items():
        print(f"  {tc_type}: {count}")

    print(f"\n⚠️  Quality Issues ({len(results['summary']['requirements_quality_issues'])} flags):")
    for issue in results['summary']['requirements_quality_issues']:
        print(f"  [{issue['requirement_id']}] {issue['text'][:60]}...")
        print(f"    → {issue['issues'][:100]}...")

    # Show first requirement's test cases
    if results['results']:
        first_req = results['results'][0]
        print(f"\n✅ Example: Requirement {first_req['requirement_id']}")
        print(f"  Test: {first_req['requirement_text'][:60]}...")
        print(f"  Generated {len(first_req['test_cases'])} test cases:")
        for tc in first_req['test_cases'][:2]:
            print(f"    - {tc['id']}: {tc['title'][:50]}... (confidence: {tc.get('confidence', 'N/A')})")
