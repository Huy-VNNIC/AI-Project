"""
Enhanced Test Generator
Generates domain-specific test cases from StructuredIntent
(NOT generic template-based)
"""

from typing import List, Dict, Any
import json
from datetime import datetime


class EnhancedTestGenerator:
    """
    Generate test cases from structured intent
    
    Key difference from generic pipeline:
    - Input: StructuredIntent (rich, domain-aware)
    - Output: Domain-specific test cases (no generic templates)
    """
    
    def __init__(self):
        self.test_counter = 0
    """Single test execution step"""
    order: int
    action: str                     # What to do
    expected_result: str            # What should happen
    actor: str = "tester"
    tool: str = "manual"
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TestCase:
    """Complete, production-ready test case"""
    test_id: str                    # TC-HM-001 (UNIQUE)
    requirement_id: str             # REQ-HM-001
    title: str                      # Clear, descriptive
    description: str                # One sentence purpose
    test_type: TestType
    priority: str                   # CRITICAL, HIGH, MEDIUM, LOW
    
    # **CRITICAL SECTION** - These make test cases actionable
    preconditions: List[str]        # What must be true first
    test_data: Dict[str, Any]       # Actual test data values
    steps: List[TestStep]           # Numbered steps
    expected_result: str            # What success looks like
    postconditions: List[str]       # Cleanup/final state
    
    # Metadata
    requirement_trace: str          # Links back to source
    domain: str
    effort_hours: float
    ml_quality_score: float         # 0.0-1.0
    
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "test_id": self.test_id,
            "requirement_id": self.requirement_id,
            "title": self.title,
            "description": self.description,
            "test_type": self.test_type.value,
            "priority": self.priority,
            "preconditions": self.preconditions,
            "test_data": self.test_data,
            "steps": [s.to_dict() for s in self.steps],
            "expected_result": self.expected_result,
            "postconditions": self.postconditions,
            "requirement_trace": self.requirement_trace,
            "domain": self.domain,
            "effort_hours": self.effort_hours,
            "ml_quality_score": self.ml_quality_score,
            "created_at": self.created_at
        }
    
    def __repr__(self) -> str:
        return f"""
╔════════════════════════════════════════════════════════╗
║ TEST CASE: {self.test_id}
║ Title: {self.title}
╠════════════════════════════════════════════════════════╣
║ Type: {self.test_type.value} | Priority: {self.priority}
║ Requirement: {self.requirement_trace}
╠════════════════════════════════════════════════════════╣
║ PRECONDITIONS:
{chr(10).join(f'║   • {pc}' for pc in self.preconditions)}
╠════════════════════════════════════════════════════════╣
║ TEST DATA:
{chr(10).join(f'║   • {k}: {v}' for k, v in self.test_data.items())}
╠════════════════════════════════════════════════════════╣
║ STEPS:
{chr(10).join(f'║   {s.order}. {s.action}' for s in self.steps)}
║   → Expected: {self.expected_result}
╠════════════════════════════════════════════════════════╣
║ POSTCONDITIONS:
{chr(10).join(f'║   • {pc}' for pc in self.postconditions)}
╚════════════════════════════════════════════════════════╝
"""


class RequirementParser:
    """Parse requirements into Actor-Action-Object-Condition"""
    
    def __init__(self):
        self.action_keywords = {
            "book": ["book", "schedule", "reserve", "arrange", "đặt", "sắp xếp"],
            "view": ["view", "see", "display", "check", "xem", "hiển thị"],
            "verify": ["verify", "validate", "check", "confirm", "kiểm tra", "xác minh"],
            "access": ["access", "enter", "login", "authenticate", "truy cập", "đăng nhập"],
            "create": ["create", "generate", "make", "add", "tạo", "thêm", "mở"],
            "update": ["update", "modify", "change", "edit", "cập nhật", "chỉnh sửa"],
            "delete": ["delete", "remove", "cancel", "xóa", "hủy", "khóa"],
            "prevent": ["prevent", "block", "deny", "stop", "ngăn chặn", "chặn"],
            "transfer": ["transfer", "send", "move", "chuyển", "gửi"],
            "authenticate": ["authenticate", "verify", "xác thực", "kiểm tra"],
            "support": ["support", "hỗ trợ", "cho phép"],
        }
        
        self.actors = {
            "patient": ["patient", "user", "bệnh nhân", "người dùng"],
            "doctor": ["doctor", "physician", "bác sĩ", "y tế"],
            "customer": ["customer", "khách hàng", "client"],
            "admin": ["admin", "administrator", "hành chính", "quản lý"],
            "system": ["system", "application", "app", "hệ thống", "ứng dụng"],
        }
        
        # Banking-specific objects
        self.banking_objects = [
            "tài khoản", "account", "transfer", "chuyển khoản",
            "card", "thẻ", "payment", "thanh toán", "transaction", "giao dịch",
            "loan", "khoản vay", "deposit", "tiền gửi", "investment", "đầu tư",
            "statement", "sao kê", "interest", "lãi suất"
        ]
    
    def parse(self, requirement_text: str) -> RequirementElement:
        """Parse requirement into Actor-Action-Object-Condition"""
        text = requirement_text.lower()
        
        # Extract components
        actor = self._extract_actor(text)
        action = self._extract_action(text)
        obj = self._extract_object(text)
        conditions = self._extract_conditions(text)
        domain = self._detect_domain(text)
        priority = self._detect_priority(text)
        
        return RequirementElement(
            actor=actor,
            action=action,
            object_entity=obj,
            conditions=conditions,
            priority=priority,
            domain=domain,
            original_text=requirement_text
        )
    
    def _extract_actor(self, text: str) -> str:
        for normalized, keywords in self.actors.items():
            for kw in keywords:
                if kw in text:
                    return normalized.capitalize()
        return "User"
    
    def _extract_action(self, text: str) -> str:
        for normalized, keywords in self.action_keywords.items():
            for kw in keywords:
                if kw in text:
                    return normalized
        return "perform"
    
    def _extract_object(self, text: str) -> str:
        # Check banking objects first
        for obj in self.banking_objects:
            if obj in text:
                return obj
        
        # Fallback to generic objects
        objects = ["appointment", "record", "medication", "prescription", "booking", "access", 
                  "payment", "data", "lịch khám", "hồ sơ", "thuốc", "dữ liệu"]
        for obj in objects:
            if obj in text or obj.split()[0] in text:
                return obj
        return "resource"
    
    def _extract_conditions(self, text: str) -> List[str]:
        conditions = []
        # Look for constraint keywords
        if "within" in text or "within" in text or "trước" in text:
            conditions.append("Time constraint")
        if "prevent" in text or "not allow" in text or "ngăn" in text:
            conditions.append("Negative constraint")
        if "only" in text or "must be" in text or "chỉ" in text:
            conditions.append("Conditional access")
        return conditions if conditions else ["Default condition"]
    
    def _detect_domain(self, text: str) -> str:
        if any(w in text for w in ["patient", "doctor", "medication", "bệnh", "thuốc"]):
            return "healthcare"
        if any(w in text for w in ["booking", "appointment", "hotel", "room", "đặt", "phòng"]):
            return "booking"
        if any(w in text for w in ["tài khoản", "ngân hàng", "chuyển khoản", "thẻ", "khoản vay", "lãi suất", "ekyc", "napas", "otp"]):
            return "banking"
        if any(w in text for w in ["payment", "transaction", "money", "thanh toán"]):
            return "payment"
        return "general"
    
    def _detect_priority(self, text: str) -> str:
        if any(w in text for w in ["must", "critical", "essential", "phải", "quan trọng"]):
            return "HIGH"
        if any(w in text for w in ["should", "important", "nên", "cần"]):
            return "MEDIUM"
        return "LOW"


class UniqueIDGenerator:
    """Generate unique, deterministic test IDs (prevents duplicates)"""
    
    def __init__(self):
        self.used_ids: Set[str] = set()
        self.id_counter: Dict[str, int] = {}
    
    def generate(self, domain: str, requirement_text: str, test_type: str) -> str:
        """
        Generate unique test ID
        Format: TC-{DOMAIN}-{TYPE}-{COUNTER:03d}
        Example: TC-HMS-HAPPY-001, TC-HMS-SEC-002
        """
        # Create domain prefix (first 3 letters)
        domain_prefix = domain[:3].upper()
        
        # Create type suffix (first 4 letters)
        type_suffix = test_type[:4].upper()
        
        # Get counter for this domain-type combo
        key = f"{domain_prefix}-{type_suffix}"
        if key not in self.id_counter:
            self.id_counter[key] = 1
        else:
            self.id_counter[key] += 1
        
        test_id = f"TC-{key}-{str(self.id_counter[key]).zfill(3)}"
        
        # Ensure uniqueness
        if test_id in self.used_ids:
            self.id_counter[key] += 1
            test_id = f"TC-{key}-{str(self.id_counter[key]).zfill(3)}"
        
        self.used_ids.add(test_id)
        return test_id
    
    def reset(self):
        """Reset counter (use for new generation batch)"""
        self.used_ids.clear()
        self.id_counter.clear()


class TestDataGenerator:
    """Generate realistic, domain-specific test data"""
    
    def __init__(self):
        self.hotel_test_data = {
            "valid_dates": {"check_in": "2026-04-15", "check_out": "2026-04-18"},
            "boundary_dates": {"check_in": "2026-04-01", "check_out": "2026-04-02"},  # 1 day
            "edge_dates": {"check_in": "2026-05-01", "check_out": "2026-05-31"},  # 30 days
            "invalid_dates": {"check_in": "2026-03-01", "check_out": "2026-03-02"},  # past
            "valid_room": {"type": "Deluxe", "capacity": 2, "price": 150},
            "invalid_room": {"type": "Invalid", "capacity": 0, "price": -100},
            "valid_guest": {"name": "John Doe", "email": "john@example.com", "phone": "+84123456789"},
            "invalid_guest": {"name": "", "email": "invalid", "phone": ""},
        }
        
        self.healthcare_test_data = {
            "valid_patient": {"id": "P001", "name": "Nguyễn Văn A", "age": 35, "dob": "1990-01-15"},
            "valid_doctor": {"id": "D001", "name": "Dr. Trần Thị B", "specialty": "Cardiology"},
            "valid_appointment": {"date": "2026-04-15", "time": "09:00", "duration": 30},
            "boundary_appointment": {"date": "2026-04-01", "time": "00:00", "duration": 1},
            "medication": {"name": "Aspirin", "dosage": "500mg", "frequency": "twice daily"},
            "allergy": {"allergy_type": "Penicillin", "severity": "severe"},
        }
        
        self.payment_test_data = {
            "valid_card": {"number": "4111111111111111", "expiry": "12/25", "cvv": "123"},
            "invalid_card": {"number": "1234567890123456", "expiry": "01/20", "cvv": "000"},
            "valid_amount": {"amount": 100.50, "currency": "USD"},
            "boundary_amount": {"amount": 0.01, "currency": "USD"},
            "edge_amount": {"amount": 999999.99, "currency": "USD"},
        }
        
        self.banking_test_data = {
            "valid_customer": {"id": "CUS001", "name": "Nguyễn Văn A", "email": "customer@bank.com", "phone": "+84912345678"},
            "valid_account": {"account_number": "0123456789", "type": "saving", "balance": 5000000, "currency": "VND"},
            "valid_transfer": {"from_account": "0123456789", "to_account": "9876543210", "amount": 500000, "description": "Payment"},
            "boundary_transfer": {"amount": 100, "limit": 50000000},  # Daily limit
            "invalid_transfer": {"from_account": "invalid", "to_account": "invalid", "amount": -100},
            "otp_code": {"valid": "123456", "expired": "000000", "invalid": "abc"},
            "card": {"number": "4111111111111111", "expiry": "12/25", "cvv": "123", "status": "active"},
        }
    
    def generate(self, domain: str, test_type: str) -> Dict[str, Any]:
        """Generate appropriate test data based on domain and test type"""
        if domain == "booking" or "hotel" in domain.lower():
            return self._generate_hotel_data(test_type)
        elif domain == "healthcare":
            return self._generate_healthcare_data(test_type)
        elif domain == "banking":
            return self._generate_banking_data(test_type)
        elif domain == "payment":
            return self._generate_payment_data(test_type)
        return {"default": "test_value"}
    
    def _generate_hotel_data(self, test_type: str) -> Dict[str, Any]:
        if test_type == TestType.HAPPY_PATH.value:
            return {
                **self.hotel_test_data["valid_guest"],
                **self.hotel_test_data["valid_dates"],
                **self.hotel_test_data["valid_room"],
                "status": "confirmed",
            }
        elif test_type == TestType.BOUNDARY_VALUE.value:
            return {
                **self.hotel_test_data["valid_guest"],
                **self.hotel_test_data["boundary_dates"],
                "rooms": 1,
                "nights": 1,
            }
        elif test_type == TestType.EDGE_CASE.value:
            return {
                **self.hotel_test_data["valid_guest"],
                **self.hotel_test_data["edge_dates"],
                "rooms": 10,
                "nights": 30,
            }
        elif test_type == TestType.NEGATIVE.value:
            return {
                **self.hotel_test_data["invalid_guest"],
                **self.hotel_test_data["invalid_dates"],
            }
        elif test_type == TestType.SECURITY.value:
            return {
                "sql_injection_attempt": "admin' OR '1'='1",
                "xss_attempt": "<script>alert('xss')</script>",
                "auth_bypass": "token=invalid&force=true",
            }
        return {}
    
    def _generate_healthcare_data(self, test_type: str) -> Dict[str, Any]:
        if test_type == TestType.HAPPY_PATH.value:
            return {
                **self.healthcare_test_data["valid_patient"],
                **self.healthcare_test_data["valid_appointment"],
                "risk_level": "low",
            }
        elif test_type == TestType.SECURITY.value:
            return {
                **self.healthcare_test_data["valid_patient"],
                "hipaa_breach_attempt": True,
                "unauthorized_access": "different_patient_id",
            }
        return {}
    
    def _generate_banking_data(self, test_type: str) -> Dict[str, Any]:
        if test_type == TestType.HAPPY_PATH.value:
            return {
                **self.banking_test_data["valid_customer"],
                **self.banking_test_data["valid_account"],
                **self.banking_test_data["valid_transfer"],
            }
        elif test_type == TestType.BOUNDARY_VALUE.value:
            return {
                **self.banking_test_data["valid_customer"],
                **self.banking_test_data["boundary_transfer"],
            }
        elif test_type == TestType.NEGATIVE.value:
            return self.banking_test_data["invalid_transfer"]
        elif test_type == TestType.SECURITY.value:
            return {
                "sql_injection": "' OR '1'='1",
                "xss_attempt": "<script>alert('xss')</script>",
                "auth_bypass": "admin_override=true",
                "fraud_attempt": "duplicate_transaction=true",
            }
        return self.banking_test_data["valid_customer"]
    
    def _generate_payment_data(self, test_type: str) -> Dict[str, Any]:
        if test_type == TestType.HAPPY_PATH.value:
            return self.payment_test_data["valid_card"] | self.payment_test_data["valid_amount"]
        elif test_type == TestType.BOUNDARY_VALUE.value:
            return self.payment_test_data["valid_card"] | self.payment_test_data["boundary_amount"]
        return {}


class EnhancedTestCaseBuilder:
    """Build production-grade test cases"""
    
    def __init__(self):
        self.id_generator = UniqueIDGenerator()
        self.test_data_gen = TestDataGenerator()
        self.parser = RequirementParser()
    
    def build(
        self,
        requirement_text: str,
        test_type: TestType,
        max_steps: int = 6
    ) -> TestCase:
        """Build a complete, actionable test case"""
        
        # Parse requirement
        req = self.parser.parse(requirement_text)
        
        # Generate unique ID
        test_id = self.id_generator.generate(req.domain, requirement_text, test_type.value)
        
        # Generate test data
        test_data = self.test_data_gen.generate(req.domain, test_type.value)
        
        # Generate title and description
        title = self._generate_title(req, test_type)
        description = self._generate_description(req, test_type)
        
        # Generate steps
        steps = self._generate_steps(req, test_type, test_data)
        
        # Generate expected result
        expected_result = self._generate_expected_result(req, test_type)
        
        # Generate preconditions and postconditions
        preconditions = self._generate_preconditions(req, test_type)
        postconditions = self._generate_postconditions(test_type)
        
        return TestCase(
            test_id=test_id,
            requirement_id=f"REQ-{req.domain[:3].upper()}-001",
            title=title,
            description=description,
            test_type=test_type,
            priority=req.priority,
            preconditions=preconditions,
            test_data=test_data,
            steps=steps,
            expected_result=expected_result,
            postconditions=postconditions,
            requirement_trace=f"{req.actor} {req.action} {req.object_entity}",
            domain=req.domain,
            effort_hours=self._estimate_effort(test_type, len(steps)),
            ml_quality_score=self._calculate_quality_score(req, test_type, steps),
        )
    
    def _generate_title(self, req: RequirementElement, test_type: TestType) -> str:
        """Generate clear, descriptive test title"""
        titles = {
            TestType.HAPPY_PATH: f"{req.actor} successfully {req.action}s {req.object_entity}",
            TestType.BOUNDARY_VALUE: f"Boundary test - {req.object_entity} at limit",
            TestType.NEGATIVE: f"Error handling - {req.actor} {req.action} with invalid {req.object_entity}",
            TestType.EDGE_CASE: f"Edge case - {req.action} with extreme {req.object_entity} values",
            TestType.SECURITY: f"Security test - Verify {req.object_entity} authorization",
            TestType.PERFORMANCE: f"Performance test - {req.actor} {req.action} under load",
            TestType.DATA_VALIDATION: f"Data validation - {req.object_entity} input constraints",
            TestType.EQUIVALENCE: f"Equivalence partition - Valid {req.object_entity}",
            TestType.INTEGRATION: f"Integration - {req.action} {req.object_entity} with dependent systems",
        }
        return titles.get(test_type, f"Test {req.action} {req.object_entity}")
    
    def _generate_description(self, req: RequirementElement, test_type: TestType) -> str:
        """Generate one-sentence test purpose"""
        purposes = {
            TestType.HAPPY_PATH: f"Verify {req.action} works correctly under normal conditions",
            TestType.BOUNDARY_VALUE: f"Verify {req.action} works at constraint boundaries",
            TestType.NEGATIVE: f"Verify system handles {req.action} errors gracefully",
            TestType.EDGE_CASE: f"Verify {req.action} handles edge cases correctly",
            TestType.SECURITY: f"Verify {req.object_entity} is protected from unauthorized access",
            TestType.PERFORMANCE: f"Verify {req.action} performs acceptably under load",
        }
        return purposes.get(test_type, f"Test {req.action} functionality")
    
    def _generate_steps(self, req: RequirementElement, test_type: TestType, test_data: Dict) -> List[TestStep]:
        """Generate realistic, numbered test steps"""
        base_steps = []
        
        if test_type == TestType.HAPPY_PATH:
            base_steps = [
                TestStep(1, "Login as valid user", "User authenticated successfully"),
                TestStep(2, f"Navigate to {req.action} {req.object_entity}", f"{req.action} form displayed"),
                TestStep(3, f"Enter valid {req.object_entity} data", "Data accepted without errors"),
                TestStep(4, f"Submit {req.action} request", f"Request processed successfully"),
                TestStep(5, "Verify confirmation message", "Success message displayed"),
                TestStep(6, f"Verify {req.object_entity} created/updated", "Data persisted correctly"),
            ]
        
        elif test_type == TestType.NEGATIVE:
            base_steps = [
                TestStep(1, "Login as valid user", "User authenticated"),
                TestStep(2, f"Attempt {req.action} with invalid {req.object_entity}", "Form displays error"),
                TestStep(3, "Verify error message is descriptive", "Clear error description shown"),
                TestStep(4, "Verify data not persisted", f"{req.object_entity} not created"),
            ]
        
        elif test_type == TestType.SECURITY:
            base_steps = [
                TestStep(1, "Attempt SQL injection attack", "Attack blocked or sanitized"),
                TestStep(2, "Attempt unauthorized access", "Access denied"),
                TestStep(3, "Verify audit log recorded", "Attempt logged"),
            ]
        
        elif test_type == TestType.BOUNDARY_VALUE:
            base_steps = [
                TestStep(1, f"Enter {req.object_entity} at minimum boundary", "Accepted or rejected based on spec"),
                TestStep(2, f"Enter {req.object_entity} at maximum boundary", "Accepted or rejected based on spec"),
                TestStep(3, "Verify correct behavior at boundaries", "System behaves as specified"),
            ]
        
        return base_steps
    
    def _generate_expected_result(self, req: RequirementElement, test_type: TestType) -> str:
        """Generate clear expected outcome"""
        results = {
            TestType.HAPPY_PATH: f"{req.actor} successfully completes {req.action} operation",
            TestType.NEGATIVE: "System rejects invalid input with clear error message",
            TestType.SECURITY: "System denies unauthorized attempts and logs the event",
            TestType.BOUNDARY_VALUE: "System correctly handles values at prescribed limits",
        }
        return results.get(test_type, "Operation completes as specified")
    
    def _generate_preconditions(self, req: RequirementElement, test_type: TestType) -> List[str]:
        """Generate prerequisites for test"""
        preconditions = [
            f"User logged in as {req.actor.lower() if req.actor != 'System' else 'valid actor'}",
            f"Required {req.domain} data exists in system",
            "System is in stable state",
        ]
        
        if test_type == TestType.SECURITY:
            preconditions.append("Security policies enforced")
        
        return preconditions
    
    def _generate_postconditions(self, test_type: TestType) -> List[str]:
        """Generate cleanup after test"""
        if test_type == TestType.HAPPY_PATH:
            return ["Test data cleaned up", "System returned to initial state"]
        return ["Test data cleaned up"]
    
    def _estimate_effort(self, test_type: TestType, step_count: int) -> float:
        """Estimate execution time in hours"""
        base_effort = {
            TestType.HAPPY_PATH: 0.5,
            TestType.NEGATIVE: 0.5,
            TestType.BOUNDARY_VALUE: 0.75,
            TestType.SECURITY: 1.5,
            TestType.PERFORMANCE: 2.0,
        }
        hours = base_effort.get(test_type, 0.5)
        return hours + (step_count * 0.1)
    
    def _calculate_quality_score(self, req: RequirementElement, test_type: TestType, steps: List[TestStep]) -> float:
        """Calculate ML quality score (0-1)"""
        score = 0.75  # base
        
        # More steps = better (traces through full flow)
        score += min(0.15, len(steps) * 0.02)
        
        # Certain types are higher quality
        quality_types = {
            TestType.HAPPY_PATH: 0.95,
            TestType.SECURITY: 0.90,
            TestType.BOUNDARY_VALUE: 0.85,
        }
        score = quality_types.get(test_type, score)
        
        return min(1.0, score)


class EnhancedTestGenerator:
    """Main enhanced test case generator"""
    
    def __init__(self):
        self.builder = EnhancedTestCaseBuilder()
    
    def generate(self, requirements: List[str], max_tests: int = 50) -> Dict[str, Any]:
        """Generate test suite from requirements"""
        
        test_cases = []
        errors = []
        test_count = 0
        
        for req_text in requirements:
            if test_count >= max_tests:
                break
            
            try:
                # For each requirement, generate multiple test types
                test_types_to_generate = [
                    TestType.HAPPY_PATH,
                    TestType.NEGATIVE,
                    TestType.BOUNDARY_VALUE,
                    TestType.SECURITY,
                    TestType.EDGE_CASE,
                ]
                
                for test_type in test_types_to_generate:
                    if test_count >= max_tests:
                        break
                    
                    try:
                        tc = self.builder.build(req_text, test_type)
                        test_cases.append(tc)
                        test_count += 1
                    except Exception as e:
                        errors.append(f"Error building {test_type.value} for requirement: {str(e)}")
            
            except Exception as e:
                errors.append(f"Error processing requirement: {req_text[:50]}... - {str(e)}")
        
        # Calculate summary
        avg_quality = sum(tc.ml_quality_score for tc in test_cases) / len(test_cases) if test_cases else 0
        avg_effort = sum(tc.effort_hours for tc in test_cases) / len(test_cases) if test_cases else 0
        
        return {
            "status": "success" if test_cases else "error",
            "test_cases": [tc.to_dict() for tc in test_cases],
            "summary": {
                "total_test_cases": len(test_cases),
                "avg_quality_score": round(avg_quality, 3),
                "avg_effort_hours": round(avg_effort, 2),
                "test_type_distribution": self._calculate_distribution(test_cases),
                "generation_timestamp": datetime.now().isoformat(),
            },
            "errors": errors
        }
    
    def _calculate_distribution(self, test_cases: List[TestCase]) -> Dict[str, int]:
        """Calculate distribution of test types"""
        dist = {}
        for tc in test_cases:
            dist[tc.test_type.value] = dist.get(tc.test_type.value, 0) + 1
        return dist


# Demo
if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 ENHANCED TEST CASE GENERATOR - DEMO")
    print("="*80 + "\n")
    
    requirements = [
        "Patient can book appointments up to 30 days in advance",
        "System must prevent unauthorized access to medical records",
        "Doctor can view patient medication history",
    ]
    
    generator = EnhancedTestGenerator()
    results = generator.generate(requirements, max_tests=15)
    
    print(f"✅ Generated {results['summary']['total_test_cases']} test cases")
    print(f"📊 Avg Quality: {results['summary']['avg_quality_score']:.2%}")
    print(f"⏱️  Avg Effort: {results['summary']['avg_effort_hours']:.2f}h")
    print(f"\nTest Type Distribution: {results['summary']['test_type_distribution']}\n")
    
    # Show first test case
    if results["test_cases"]:
        first_tc = results["test_cases"][0]
        print("Sample Test Case:")
        print(f"  ID: {first_tc['test_id']}")
        print(f"  Title: {first_tc['title']}")
        print(f"  Type: {first_tc['test_type']}")
        print(f"  Steps: {len(first_tc['steps'])} steps")
        print(f"  Quality: {first_tc['ml_quality_score']:.0%}")
        print(f"  Effort: {first_tc['effort_hours']:.1f}h")
