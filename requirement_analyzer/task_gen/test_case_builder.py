"""
Test Case Builder - Build structured, actionable test cases from scenarios
Phase 3 of AI Test Case Generator v2
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from requirement_analyzer.task_gen.requirement_parser import RequirementObject
from requirement_analyzer.task_gen.scenario_generator import TestScenario, ScenarioType
from requirement_analyzer.task_gen.effort_estimator import EffortEstimationEngine, EffortEstimate


@dataclass
class TestStep:
    """Individual test step"""

    order: int
    action: str  # What to do
    expected: str  # What should happen
    actor: str = "tester"  # Who performs
    tool: str = "manual"  # How to perform


@dataclass
class TestCase:
    """Complete, traceable test case"""

    id: str  # TC-DOMAIN-001
    requirement_id: str  # REQ-APT-001
    title: str
    description: str
    scenario_type: str
    priority: str
    risk_level: str
    preconditions: List[str]
    test_data: Dict[str, Any]
    steps: List[TestStep]
    expected_result: str
    postconditions: List[str]
    trace_info: Dict[str, Any]  # Traceability info
    domain_specific: bool = False
    estimated_effort_hours: float = 0.0
    effort_estimate: Optional[EffortEstimate] = None  # Full effort estimate with breakdown

    def to_dict(self):
        """Convert to dictionary"""
        result = {
            "id": self.id,
            "requirement_id": self.requirement_id,
            "title": self.title,
            "description": self.description,
            "scenario_type": self.scenario_type,
            "priority": self.priority,
            "risk_level": self.risk_level,
            "preconditions": self.preconditions,
            "test_data": self.test_data,
            "steps": [
                {
                    "order": s.order,
                    "action": s.action,
                    "expected": s.expected,
                    "actor": s.actor,
                    "tool": s.tool,
                }
                for s in self.steps
            ],
            "expected_result": self.expected_result,
            "postconditions": self.postconditions,
            "trace_info": self.trace_info,
            "domain_specific": self.domain_specific,
            "estimated_effort_hours": self.estimated_effort_hours,
        }
        
        # Include detailed effort estimate if available
        if self.effort_estimate:
            result["effort"] = self.effort_estimate.to_dict()
        
        return result

    def __repr__(self):
        return f"""
╔════════════════════════════════════════════════════════════════╗
║ TEST CASE: {self.id} - {self.title}
╠════════════════════════════════════════════════════════════════╣
║ Requirement: {self.requirement_id}
║ Type: {self.scenario_type} | Priority: {self.priority} | Risk: {self.risk_level}
║ Effort: {self.estimated_effort_hours}h
╠════════════════════════════════════════════════════════════════╣
║ PRECONDITIONS:
"""
        + "\n".join([f"║   • {pc}" for pc in self.preconditions])
        + f"""
╠════════════════════════════════════════════════════════════════╣
║ TEST DATA:
"""
        + "\n".join([f"║   • {k}: {v}" for k, v in self.test_data.items()])
        + f"""
╠════════════════════════════════════════════════════════════════╣
║ STEPS:
"""
        + "\n".join([f"║   Step {s.order}: {s.action}" for s in self.steps])
        + f"""
╠════════════════════════════════════════════════════════════════╣
║ EXPECTED RESULT:
║   {self.expected_result}
╠════════════════════════════════════════════════════════════════╣
║ POSTCONDITIONS:
"""
        + "\n".join([f"║   • {pc}" for pc in self.postconditions])
        + f"""
╠════════════════════════════════════════════════════════════════╣
║ TRACE to Requirement:
║   Requirement: {self.trace_info.get('source_requirement', 'N/A')}
║   Actor: {self.trace_info.get('actor', 'N/A')}
║   Action: {self.trace_info.get('action', 'N/A')}
║   Object: {self.trace_info.get('object', 'N/A')}
╚════════════════════════════════════════════════════════════════╝
"""


class TestCaseBuilder:
    """Build structured test cases from scenarios"""

    def __init__(self):
        self.case_counter = {}  # Track ID generation: {domain: count}
        self.effort_engine = EffortEstimationEngine()  # Use new professional-grade estimator
        self.healthcare_entities = {
            "Patient": ["patient_id", "name", "allergies", "insurance"],
            "Doctor": ["doctor_id", "specialty", "license"],
            "Appointment": ["date", "time", "doctor_id", "reason"],
            "Prescription": ["drug_id", "dosage", "frequency", "interaction_check"],
        }

    def build_test_case(
        self,
        requirement: RequirementObject,
        scenario: TestScenario,
        requirement_id: str,
    ) -> TestCase:
        """
        Build a complete test case from requirement + scenario
        """
        # Generate unique ID
        domain = requirement.domain[:4].upper()
        test_id = self._generate_test_id(domain, requirement.object_entity)

        # Build title
        title = self._build_title(requirement, scenario)

        # Build preconditions
        preconditions = self._build_preconditions(requirement, scenario)

        # Build steps with expected results
        steps = self._build_steps(requirement, scenario)

        # Build expected result
        expected_result = self._build_expected_result(requirement, scenario)

        # Build postconditions
        postconditions = self._build_postconditions(requirement, scenario)

        # Build traceability
        trace_info = {
            "source_requirement": requirement.original_text,
            "requirement_id": requirement_id,
            "actor": requirement.actor,
            "action": requirement.action,
            "object": requirement.object_entity,
            "constraints": [str(c) for c in requirement.constraints],
            "domain": requirement.domain,
        }

        # Create temporary test case object for effort estimation
        temp_test_case = TestCase(
            id=test_id,
            requirement_id=requirement_id,
            title=title,
            description=scenario.description,
            scenario_type=scenario.scenario_type.value,
            priority=scenario.priority,
            risk_level=scenario.risk_level,
            preconditions=preconditions,
            test_data=scenario.test_data,
            steps=steps,
            expected_result=expected_result,
            postconditions=postconditions,
            trace_info=trace_info,
            domain_specific=scenario.domain_specific,
            estimated_effort_hours=0.0,  # Placeholder
        )
        
        # Estimate effort using professional engine
        effort_estimate = self.effort_engine.estimate(temp_test_case)
        
        # Create final test case with effort details
        return TestCase(
            id=test_id,
            requirement_id=requirement_id,
            title=title,
            description=scenario.description,
            scenario_type=scenario.scenario_type.value,
            priority=scenario.priority,
            risk_level=scenario.risk_level,
            preconditions=preconditions,
            test_data=scenario.test_data,
            steps=steps,
            expected_result=expected_result,
            postconditions=postconditions,
            trace_info=trace_info,
            domain_specific=scenario.domain_specific,
            estimated_effort_hours=effort_estimate.estimated_hours,
            effort_estimate=effort_estimate,
        )

    def _generate_test_id(self, domain: str, entity: str) -> str:
        """Generate unique test case ID: TC-DOMAIN-ENTITY-###"""
        entity_short = entity[:3].upper()
        key = f"{domain}-{entity_short}"

        if key not in self.case_counter:
            self.case_counter[key] = 0

        self.case_counter[key] += 1
        return f"TC-{key}-{str(self.case_counter[key]).zfill(3)}"

    def _build_title(self, requirement: RequirementObject, scenario: TestScenario) -> str:
        """Build descriptive title"""
        scenario_desc = scenario.scenario_type.value.replace("_", " ").title()
        return f"{scenario_desc}: {requirement.action} {requirement.object_entity}"

    def _build_preconditions(
        self,
        requirement: RequirementObject,
        scenario: TestScenario,
    ) -> List[str]:
        """Build preconditions based on requirement + scenario"""
        preconditions = []

        # Domain-specific auth
        if requirement.domain in ["healthcare", "banking"]:
            preconditions.append(f"{requirement.actor} is authenticated")
            preconditions.append(f"{requirement.actor} has required permissions")

        # Entity prerequisites
        if "create" in requirement.action.lower():
            preconditions.append(f"{requirement.object_entity} entity is initialized")
        if "update" in requirement.action.lower():
            preconditions.append(f"{requirement.object_entity} exists in system")
        if "delete" in requirement.action.lower():
            preconditions.append(f"{requirement.object_entity} is not in use")

        # Data prerequisites
        if "valid_data" in scenario.test_data.get("validity", ""):
            preconditions.append("All required data fields are valid")
        if scenario.scenario_type == ScenarioType.SECURITY:
            preconditions.append("Security checks are enabled")

        # Healthcare-specific
        if requirement.domain == "healthcare":
            preconditions.extend(
                [
                    "Patient has active healthcare record",
                    "No critical allergies or conflicts",
                    "Insurance coverage verified",
                ]
            )

        return preconditions or ["System is in ready state"]

    def _build_steps(self, requirement: RequirementObject, scenario: TestScenario) -> List[TestStep]:
        """Build actionable test steps"""
        steps = []

        # Step 1: Setup/precondition setup
        steps.append(
            TestStep(
                order=1,
                action=f"Open system/application",
                expected=f"Application loads successfully",
                actor="tester",
                tool="browser",
            )
        )

        # Step 2: Login/Authentication
        if requirement.domain in ["healthcare", "banking"]:
            steps.append(
                TestStep(
                    order=len(steps) + 1,
                    action=f"Authenticate as {requirement.actor}",
                    expected=f"{requirement.actor} login successful",
                    actor="tester",
                    tool="manual",
                )
            )

        # Step 3: Navigate to feature
        steps.append(
            TestStep(
                order=len(steps) + 1,
                action=f"Navigate to {requirement.object_entity} feature",
                expected=f"{requirement.object_entity} UI loads",
                actor="tester",
                tool="browser",
            )
        )

        # Step 4: Input test data
        if scenario.test_data:
            data_str = ", ".join([f"{k}={v}" for k, v in list(scenario.test_data.items())[:3]])
            steps.append(
                TestStep(
                    order=len(steps) + 1,
                    action=f"Enter test data: {data_str}",
                    expected="Data fields populated correctly",
                    actor="tester",
                    tool="manual",
                )
            )

        # Step 5: Perform action
        steps.append(
            TestStep(
                order=len(steps) + 1,
                action=f"Execute '{requirement.action}' on {requirement.object_entity}",
                expected=f"System processes {requirement.action}",
                actor="tester",
                tool="system",
            )
        )

        # Step 6: Verify result (scenario-specific)
        if scenario.scenario_type == ScenarioType.SECURITY:
            steps.append(
                TestStep(
                    order=len(steps) + 1,
                    action="Verify security check executed",
                    expected="Security validation passed",
                    actor="tester",
                    tool="system",
                )
            )

        # Step 7: Confirm outcome
        steps.append(
            TestStep(
                order=len(steps) + 1,
                action="Check system output/database state",
                expected="State matches expected result",
                actor="tester",
                tool="system",
            )
        )

        return steps

    def _build_expected_result(self, requirement: RequirementObject, scenario: TestScenario) -> str:
        """Build clear expected result"""
        if scenario.scenario_type == ScenarioType.HAPPY_PATH:
            return (
                f"✓ {requirement.object_entity} {requirement.action}ed successfully\n"
                f"✓ Confirmation message displayed\n"
                f"✓ Data persisted in database"
            )

        elif scenario.scenario_type == ScenarioType.BOUNDARY_VALUE:
            boundary = scenario.test_data.get("boundary_value", "N/A")
            return (
                f"✓ System correctly handles boundary value: {boundary}\n"
                f"✓ Validation rules applied\n"
                f"✓ State transition correct"
            )

        elif scenario.scenario_type == ScenarioType.NEGATIVE:
            return (
                f"✓ System rejects operation\n"
                f"✓ Error message displayed\n"
                f"✓ No data corruption or side effects\n"
                f"✓ System in consistent state"
            )

        elif scenario.scenario_type == ScenarioType.SECURITY:
            return (
                f"✓ Security check passed/blocked as expected\n"
                f"✓ Audit log recorded\n"
                f"✓ No unauthorized access\n"
                f"✓ Sensitive data protected"
            )

        else:
            return f"✓ {requirement.object_entity} operation completed as specified"

    def _build_postconditions(self, requirement: RequirementObject, scenario: TestScenario) -> List[str]:
        """Build postconditions - system state after test"""
        postconditions = []

        # Data postconditions
        if "create" in requirement.action.lower():
            postconditions.append(f"{requirement.object_entity} record created in database")
        if "update" in requirement.action.lower():
            postconditions.append(f"{requirement.object_entity} record updated with new values")
        if "delete" in requirement.action.lower():
            postconditions.append(f"{requirement.object_entity} record removed from database")

        # Logging/audit
        if requirement.domain in ["healthcare", "banking"]:
            postconditions.append("Action logged in audit trail")

        # Cache/state
        postconditions.append("System in consistent state")
        postconditions.append("Memory/resources cleaned up")

        return postconditions or ["System in ready state for next test"]


# Test
if __name__ == "__main__":
    from requirement_parser import RequirementParser
    from scenario_generator import ScenarioGenerator

    parser = RequirementParser()
    generator = ScenarioGenerator()
    builder = TestCaseBuilder()

    requirement = parser.parse("Hệ thống phải cho phép đặt lịch khám trước 30 ngày không được vượt quá")
    scenarios = generator.generate_scenarios(requirement)

    print(f"Building {len(scenarios)} test cases...\n")

    test_cases = []
    for i, scenario in enumerate(scenarios[:3], 1):  # Build first 3
        tc = builder.build_test_case(requirement, scenario, f"REQ-APT-001")
        test_cases.append(tc)
        print(tc)
        print("\n")

    print(f"✅ Built {len(test_cases)} test cases")
