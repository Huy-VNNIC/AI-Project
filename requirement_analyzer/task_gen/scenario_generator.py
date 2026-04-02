"""
Test Scenario Generator - Generate test scenarios using BVA, Equivalence Partitioning
Phase 2 of AI Test Case Generator v2
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum
from requirement_analyzer.task_gen.requirement_parser import RequirementObject, Constraint, ActionType


class ScenarioType(Enum):
    HAPPY_PATH = "happy_path"
    BOUNDARY_VALUE = "boundary_value"
    EQUIVALENCE_PARTITION = "equivalence_partition"
    NEGATIVE = "negative"
    SECURITY = "security"
    PERFORMANCE = "performance"
    INTEGRATION = "integration"


@dataclass
class TestScenario:
    """Represents a test scenario"""

    scenario_type: ScenarioType
    title: str
    description: str
    test_data: Dict[str, Any]
    expected_behavior: str
    priority: str = "MEDIUM"
    risk_level: str = "LOW"
    domain_specific: bool = False
    coverage: float = 0.0  # How well it covers the requirement

    def __repr__(self):
        return f"""
Scenario: {self.title}
Type: {self.scenario_type.value}
Description: {self.description}
Test Data: {self.test_data}
Expected: {self.expected_behavior}
Priority: {self.priority} | Risk: {self.risk_level}
"""


class ScenarioGenerator:
    """Generate test scenarios from structured requirement"""

    def __init__(self):
        self.healthcare_critical_flows = {
            "allergy_detection": ["allergy", "dị ứng", "reaction", "phản ứng"],
            "drug_interaction": ["interaction", "tương tác", "contraindication", "chống chỉ định"],
            "insurance_verification": ["insurance", "bảo hiểm", "coverage", "verify"],
            "hipaa_compliance": ["privacy", "bảo mật", "hipaa", "confidential"],
            "patient_safety": ["safety", "an toàn", "risk", "nguy hiểm"],
        }

    def generate_scenarios(self, requirement: RequirementObject) -> List[TestScenario]:
        """
        Generate comprehensive test scenarios for a requirement
        1. Happy path
        2. Boundary value analysis (BVA)
        3. Equivalence partitioning
        4. Negative cases
        5. Security/domain-specific cases
        """
        scenarios = []

        # 1. Happy path (main flow)
        scenarios.append(self._generate_happy_path(requirement))

        # 2. Boundary value analysis (BVA)
        if requirement.constraints:
            scenarios.extend(self._generate_bva_scenarios(requirement))

        # 3. Equivalence partitioning
        scenarios.extend(self._generate_equivalence_scenarios(requirement))

        # 4. Negative/error scenarios
        scenarios.extend(self._generate_negative_scenarios(requirement))

        # 5. Security & domain-specific
        if requirement.domain in ["healthcare", "banking"]:
            scenarios.extend(self._generate_security_scenarios(requirement))

        return scenarios

    def _generate_happy_path(self, requirement: RequirementObject) -> TestScenario:
        """Happy path - all conditions met, ideal case"""
        test_data = self._generate_happy_path_data(requirement)

        return TestScenario(
            scenario_type=ScenarioType.HAPPY_PATH,
            title=f"Happy Path: {requirement.action} {requirement.object_entity}",
            description=f"All preconditions met, {requirement.object_entity} should {requirement.action} successfully",
            test_data=test_data,
            expected_behavior=f"{requirement.object_entity} operation completed successfully",
            priority=requirement.priority,
            risk_level="LOW",
            domain_specific=False,
            coverage=0.85,
        )

    def _generate_happy_path_data(self, req: RequirementObject) -> Dict:
        """Generate test data for happy path"""
        data = {}

        # Healthcare-specific
        if req.domain == "healthcare":
            data = {
                "actor": "patient_001",
                "actor_identity": "valid_authenticated",
                "patient_allergies": "none",
                "medications": "none_conflicting",
                "insurance_status": "active",
                "date": "valid_future_date",
                "status": "pending",
            }

        # Booking-specific
        if req.action_type == ActionType.CREATE:
            data.update({
                "status": "created",
                "timestamp": "current_time",
                "confirmation": "success",
            })

        # Banking-specific
        if req.domain == "banking":
            data = {
                "account_status": "active",
                "balance": 1000.0,
                "amount": 100.0,
                "transaction_limit": "not_exceeded",
                "authentication": "verified",
            }

        return data or {"status": "valid"}

    def _generate_bva_scenarios(self, requirement: RequirementObject) -> List[TestScenario]:
        """Boundary Value Analysis - test at boundaries"""
        scenarios = []

        for constraint in requirement.constraints:
            if "day" in constraint.type or "time" in constraint.type:
                # Extract numeric value
                import re

                numbers = re.findall(r"\d+", constraint.value)
                if numbers:
                    boundary_val = int(numbers[0])

                    # Test at boundary
                    test_cases = [
                        (boundary_val - 1, "just_before_boundary", 0.90),
                        (boundary_val, "at_boundary", 0.95),
                        (boundary_val + 1, "just_after_boundary", 0.90),
                    ]

                    for value, desc, coverage in test_cases:
                        test_data = self._generate_bva_data(requirement, constraint, value)
                        scenarios.append(
                            TestScenario(
                                scenario_type=ScenarioType.BOUNDARY_VALUE,
                                title=f"BVA: {requirement.object_entity} {desc} ({value})",
                                description=f"Test {requirement.object_entity} at boundary condition {desc}",
                                test_data=test_data,
                                expected_behavior=f"Behavior correctness at boundary: {desc}",
                                priority="HIGH" if desc == "at_boundary" else "MEDIUM",
                                risk_level="MEDIUM",
                                domain_specific=False,
                                coverage=coverage,
                            )
                        )

        return scenarios

    def _generate_bva_data(self, req: RequirementObject, constraint: Constraint, value: int) -> Dict:
        """Generate test data for BVA test"""
        data = {
            "base_date": "today",
            "boundary_value": value,
            "constraint_type": constraint.type,
        }

        if req.domain == "healthcare" and req.action_type == ActionType.CREATE:
            data.update({
                "appointment_days_ahead": value,
                "date_valid": "yes",
            })

        return data

    def _generate_equivalence_scenarios(self, requirement: RequirementObject) -> List[TestScenario]:
        """Equivalence Partitioning - partition input domain"""
        scenarios = []

        # Partition by validity
        partitions = [
            ("valid_data", "All data valid", {"validity": "all_valid"}, 0.88),
            ("partial_valid", "Some data invalid", {"validity": "some_invalid"}, 0.75),
            ("all_invalid", "All data invalid", {"validity": "all_invalid"}, 0.80),
        ]

        for partition_name, desc, test_data, coverage in partitions:
            test_data["partition"] = partition_name

            scenarios.append(
                TestScenario(
                    scenario_type=ScenarioType.EQUIVALENCE_PARTITION,
                    title=f"EP: {partition_name}",
                    description=desc,
                    test_data=test_data,
                    expected_behavior=f"Handle {partition_name} correctly",
                    priority="MEDIUM",
                    risk_level="LOW" if "valid" in partition_name else "MEDIUM",
                    domain_specific=False,
                    coverage=coverage,
                )
            )

        return scenarios

    def _generate_negative_scenarios(self, requirement: RequirementObject) -> List[TestScenario]:
        """Negative scenarios - error conditions"""
        scenarios = []

        negative_cases = [
            ("invalid_actor", "Invalid/unauthenticated actor", {"actor_status": "invalid"}),
            ("missing_data", "Required data missing", {"required_field": "missing"}),
            ("constraint_violation", "Violates constraint", {"constraint_met": "no"}),
            ("state_conflict", "Invalid state transition", {"current_state": "invalid"}),
            ("duplicate", "Duplicate operation", {"duplicate_check": "exists"}),
        ]

        for case_type, desc, test_data in negative_cases:
            scenarios.append(
                TestScenario(
                    scenario_type=ScenarioType.NEGATIVE,
                    title=f"Negative: {case_type}",
                    description=desc,
                    test_data=test_data,
                    expected_behavior=f"System rejects: {case_type}",
                    priority="HIGH",
                    risk_level="MEDIUM",
                    domain_specific=False,
                    coverage=0.80,
                )
            )

        return scenarios

    def _generate_security_scenarios(self, requirement: RequirementObject) -> List[TestScenario]:
        """Healthcare/Banking specific security scenarios"""
        scenarios = []

        # Check if healthcare domain
        is_healthcare = requirement.domain == "healthcare"

        if is_healthcare:
            security_cases = [
                ("allergy_check", "Allergy detection - critical safety", {"check_type": "allergy"}, "HIGH"),
                (
                    "drug_interaction",
                    "Drug interaction check - medication conflict",
                    {"check_type": "interaction"},
                    "HIGH",
                ),
                ("insurance_verify", "Insurance coverage verification", {"check_type": "insurance"}, "HIGH"),
                ("hipaa_privacy", "HIPAA privacy protection", {"check_type": "privacy"}, "HIGH"),
                ("patient_safety", "Patient safety risk assessment", {"check_type": "safety"}, "HIGH"),
            ]
        else:
            security_cases = [
                ("authentication", "User authentication required", {"auth_required": "yes"}, "HIGH"),
                ("authorization", "User authorization check", {"auth_level": "check"}, "HIGH"),
                ("data_encryption", "Sensitive data encrypted", {"encryption": "required"}, "HIGH"),
                ("audit_logging", "Action audit trail", {"audit": "required"}, "MEDIUM"),
            ]

        for case_name, desc, test_data, priority in security_cases:
            scenarios.append(
                TestScenario(
                    scenario_type=ScenarioType.SECURITY,
                    title=f"Security: {case_name}",
                    description=desc,
                    test_data=test_data,
                    expected_behavior=f"Security check: {case_name}",
                    priority=priority,
                    risk_level="HIGH",
                    domain_specific=True,
                    coverage=0.92,
                )
            )

        return scenarios


# Test
if __name__ == "__main__":
    from requirement_parser import RequirementParser

    parser = RequirementParser()
    generator = ScenarioGenerator()

    requirement = parser.parse("Hệ thống phải cho phép đặt lịch khám trước 30 ngày")
    print("Requirement:", requirement)
    print("\n" + "=" * 80 + "\n")

    scenarios = generator.generate_scenarios(requirement)
    print(f"Generated {len(scenarios)} scenarios:")
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario}")
