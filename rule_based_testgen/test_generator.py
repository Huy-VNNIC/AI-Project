"""
Test Case Generation Module
Rule engine that generates positive, negative, edge case, and security tests
"""

from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from config import BOUNDARY_VALUES, SECURITY_ACTIONS


@dataclass
class TestCase:
    """Represents a single test case"""
    test_id: str
    requirement_id: str
    title: str
    description: str
    preconditions: List[str]
    steps: List[str]
    expected_result: str
    test_type: str  # positive, negative, edge_case, security, performance
    priority: str  # low, medium, high, critical
    domain: str
    automation_hint: str = ""
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TestGenerator:
    """Generate test cases from structured requirements using rules"""
    
    def __init__(self):
        """Initialize test generator"""
        self.test_counter = 0
    
    def _next_test_id(self, req_id: str, test_type: str) -> str:
        """
        Generate unique test ID
        Format: REQ-001-POSITIVE-001
        
        Args:
            req_id: Requirement ID
            test_type: Test type abbreviation
            
        Returns:
            Unique test ID
        """
        self.test_counter += 1
        type_abbr = {
            "positive": "POS",
            "negative": "NEG",
            "edge_case": "EDGE",
            "security": "SEC",
            "performance": "PERF",
        }.get(test_type, "TST")
        
        return f"{req_id}-{type_abbr}-{self.test_counter:03d}"
    
    def generate_positive_test(self, req: 'StructuredRequirement') -> TestCase:
        """
        Generate happy path test case
        
        Args:
            req: Structured requirement
            
        Returns:
            Positive test case
        """
        actor = "User" if req.actor == "user" else req.actor.capitalize()
        action = req.action.capitalize()
        
        # Build steps
        steps = [
            f"{actor} opens the application",
            f"{actor} navigates to {req.action} section",
        ]
        
        # Add input steps
        for inp in req.inputs:
            steps.append(f"{actor} enters valid {inp.name}")
        
        # Add submission
        steps.append(f"{actor} submits the form/request")
        
        return TestCase(
            test_id=self._next_test_id(req.requirement_id, "positive"),
            requirement_id=req.requirement_id,
            title=f"Successfully {action} with valid inputs",
            description=f"Verify that {req.actor} can successfully {req.action}",
            preconditions=[f"{req.actor} is logged in" if req.actor == "user" else "System is running"],
            steps=steps,
            expected_result=f"✓ {' and '.join(req.expected_results) if req.expected_results else f'{action} completed successfully'}",
            test_type="positive",
            priority=req.priority,
            domain=req.domain,
        )
    
    def generate_negative_tests(self, req: 'StructuredRequirement') -> List[TestCase]:
        """
        Generate negative test cases (invalid inputs)
        
        Args:
            req: Structured requirement
            
        Returns:
            List of negative test cases
        """
        tests = []
        
        # For each input, generate invalid input test
        for inp in req.inputs:
            actor = "User" if req.actor == "user" else req.actor.capitalize()
            
            steps = [
                f"{actor} opens the application",
                f"{actor} navigates to {req.action} section",
            ]
            
            # Add invalid input steps
            for other_inp in req.inputs:
                if other_inp.name == inp.name:
                    steps.append(f"{actor} enters INVALID {inp.name}")
                else:
                    steps.append(f"{actor} enters valid {other_inp.name}")
            
            steps.append(f"{actor} submits the form/request")
            
            tests.append(TestCase(
                test_id=self._next_test_id(req.requirement_id, "negative"),
                requirement_id=req.requirement_id,
                title=f"Reject {req.action} with invalid {inp.name}",
                description=f"Verify system rejects invalid {inp.name}",
                preconditions=[f"{req.actor} is logged in"],
                steps=steps,
                expected_result=f"✗ Operation fails with error message about {inp.name}",
                test_type="negative",
                priority=req.priority,
                domain=req.domain,
            ))
            
            # Empty field test
            steps_empty = [
                f"{actor} opens the application",
                f"{actor} navigates to {req.action} section",
            ]
            
            for other_inp in req.inputs:
                if other_inp.name == inp.name:
                    steps_empty.append(f"{actor} leaves {inp.name} empty")
                else:
                    steps_empty.append(f"{actor} enters valid {other_inp.name}")
            
            steps_empty.append(f"{actor} submits the form/request")
            
            tests.append(TestCase(
                test_id=self._next_test_id(req.requirement_id, "negative"),
                requirement_id=req.requirement_id,
                title=f"Reject {req.action} with empty {inp.name}",
                description=f"Verify system requires {inp.name}",
                preconditions=[f"{req.actor} is logged in"],
                steps=steps_empty,
                expected_result=f"✗ Validation error: {inp.name} is required",
                test_type="negative",
                priority="high",
                domain=req.domain,
            ))
        
        return tests
    
    def generate_edge_case_tests(self, req: 'StructuredRequirement') -> List[TestCase]:
        """
        Generate edge case tests (boundary values, special cases)
        
        Args:
            req: Structured requirement
            
        Returns:
            List of edge case tests
        """
        tests = []
        
        for inp in req.inputs:
            inp_type = inp.type_
            actor = "User" if req.actor == "user" else req.actor.capitalize()
            
            # Get boundary values for this input type
            boundaries = BOUNDARY_VALUES.get(inp_type, [])
            
            for boundary_val in boundaries[:2]:  # Limit to 2 boundary tests per input
                steps = [
                    f"{actor} opens the application",
                    f"{actor} navigates to {req.action} section",
                ]
                
                for other_inp in req.inputs:
                    if other_inp.name == inp.name:
                        steps.append(f"{actor} enters {inp_type} value: {boundary_val}")
                    else:
                        steps.append(f"{actor} enters valid {other_inp.name}")
                
                steps.append(f"{actor} submits the form/request")
                
                tests.append(TestCase(
                    test_id=self._next_test_id(req.requirement_id, "edge_case"),
                    requirement_id=req.requirement_id,
                    title=f"Handle edge case: {inp_type}={boundary_val}",
                    description=f"Verify system handles boundary value for {inp.name}",
                    preconditions=[f"{req.actor} is logged in"],
                    steps=steps,
                    expected_result="System handles gracefully (accept or reject with clear message)",
                    test_type="edge_case",
                    priority="medium",
                    domain=req.domain,
                ))
        
        return tests
    
    def generate_security_tests(self, req: 'StructuredRequirement') -> List[TestCase]:
        """
        Generate security-specific tests
        
        Args:
            req: Structured requirement
            
        Returns:
            List of security tests
        """
        tests = []
        
        # Only generate if requirement is security-related
        if req.type_ != "security":
            return tests
        
        actor = "User" if req.actor == "user" else req.actor.capitalize()
        
        # Test 1: Unauthorized access
        tests.append(TestCase(
            test_id=self._next_test_id(req.requirement_id, "security"),
            requirement_id=req.requirement_id,
            title=f"Reject unauthorized {req.action}",
            description="Verify system denies access to unauthenticated requests",
            preconditions=[f"{req.actor} is NOT logged in"],
            steps=[
                f"Unauthenticated {req.actor} attempts to {req.action}",
                "Attempt to bypass authentication"
            ],
            expected_result="✗ Access denied, redirected to login or 401 Unauthorized",
            test_type="security",
            priority="critical",
            domain=req.domain,
        ))
        
        # Test 2: SQL Injection / Input sanitization
        tests.append(TestCase(
            test_id=self._next_test_id(req.requirement_id, "security"),
            requirement_id=req.requirement_id,
            title=f"Sanitize SQL injection in {req.action}",
            description="Verify system sanitizes malicious input",
            preconditions=[f"{req.actor} is logged in"],
            steps=[
                f"{actor} enters SQL injection payload: ' OR '1'='1",
                f"{actor} submits the form"
            ],
            expected_result="✗ Payload is escaped/rejected, operation fails safely",
            test_type="security",
            priority="critical",
            domain=req.domain,
        ))
        
        # Test 3: Permission check
        tests.append(TestCase(
            test_id=self._next_test_id(req.requirement_id, "security"),
            requirement_id=req.requirement_id,
            title=f"Verify permission control for {req.action}",
            description="Verify only authorized users can perform action",
            preconditions=["User with limited role is logged in"],
            steps=[
                "Limited user attempts restricted action",
                "Verify user lacks required permissions"
            ],
            expected_result="✗ Operation denied due to insufficient permissions",
            test_type="security",
            priority="high",
            domain=req.domain,
        ))
        
        return tests
    
    def generate_tests(self, req: 'StructuredRequirement') -> List[TestCase]:
        """
        Main test generation method
        Generate all test types for a requirement
        
        Args:
            req: Structured requirement
            
        Returns:
            List of all generated test cases
        """
        tests = []
        
        # Always generate positive test
        tests.append(self.generate_positive_test(req))
        
        # Generate negative tests (invalid inputs)
        tests.extend(self.generate_negative_tests(req))
        
        # Generate edge case tests
        tests.extend(self.generate_edge_case_tests(req))
        
        # Generate security tests if applicable
        if req.type_ == "security":
            tests.extend(self.generate_security_tests(req))
        
        return tests
    
    def generate_batch(self, requirements: List['StructuredRequirement']) -> List[TestCase]:
        """
        Generate tests for multiple requirements
        
        Args:
            requirements: List of structured requirements
            
        Returns:
            All generated test cases
        """
        all_tests = []
        for req in requirements:
            all_tests.extend(self.generate_tests(req))
        return all_tests


# Demo
if __name__ == "__main__":
    from requirement_structurer import StructuredRequirement, Input
    
    # Create sample requirement
    sample_req = StructuredRequirement(
        requirement_id="REQ-001",
        original_text="User must authenticate with email and password",
        actor="user",
        action="authenticate",
        objects=["email", "password"],
        inputs=[
            Input(name="email", type_="email"),
            Input(name="password", type_="password"),
        ],
        type_="security",
        domain="general",
        priority="critical",
    )
    
    generator = TestGenerator()
    tests = generator.generate_tests(sample_req)
    
    print(f"Generated {len(tests)} test cases:")
    for test in tests:
        print(f"  - {test.test_id}: {test.title} ({test.test_type})")
