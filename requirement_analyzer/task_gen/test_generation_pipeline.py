"""
LLM-Free AI Test Generation Pipeline
Integrates: Requirement Extraction → Structured Intent → Smart Test Generation → Deduplication
"""

from typing import List, Dict, Any, Optional
import json
from datetime import datetime

# Import components
from .structured_intent import StructuredIntent, DomainType, Entity, Action
from .requirement_extractor import RequirementExtractor, MockRequirementExtractor
from .deduplication_engine import TestCaseDeduplicator


class TestGenerationPipeline:
    """
    Complete pipeline without external LLM APIs
    
    Pipeline:
    Requirement (text) →[Your AI Model]→ StructuredIntent → Domain-Specific Tests → Deduplication
    """
    
    def __init__(self, extractor: Optional[RequirementExtractor] = None):
        """
        Initialize pipeline
        
        Args:
            extractor: Your custom RequirementExtractor implementation
                      If None, uses mock fallback
        """
        self.extractor = extractor or MockRequirementExtractor()
        self.deduplicator = TestCaseDeduplicator(similarity_threshold=0.85)
        self.stats = {
            "requirements_processed": 0,
            "test_cases_generated": 0,
            "test_cases_deduplicated": 0,
            "avg_confidence": 0.0,
        }
    
    def process_requirements(
        self,
        requirements: List[str],
        auto_deduplicate: bool = True,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Process multiple requirements end-to-end
        
        Args:
            requirements: List of requirement texts
            auto_deduplicate: Whether to remove duplicates
            verbose: Print progress
            
        Returns:
            Dict with:
            - status: "success" / "partial" / "failed"
            - test_cases: List of generated test cases
            - summary: Statistics and metrics
        """
        if verbose:
            print("\n" + "=" * 70)
            print("🚀 TEST GENERATION PIPELINE (NO EXTERNAL API)")
            print("=" * 70)
        
        all_test_cases = []
        intents = []
        
        # Step 1: Extract intents
        if verbose:
            print(f"\n📊 Step 1: Extracting structured intent from {len(requirements)} requirements...")
        
        for idx, req_text in enumerate(requirements, 1):
            try:
                intent = self.extractor.extract(req_text)
                intent.requirement_id = f"REQ-{idx:03d}"
                intents.append(intent)
                
                if verbose:
                    print(f"   [{idx}] ✅ {intent.domain.value} | Confidence: {intent.confidence_score:.1%}")
                
            except Exception as e:
                if verbose:
                    print(f"   [{idx}] ❌ Error: {e}")
        
        self.stats["requirements_processed"] = len(intents)
        
        # Step 2: Generate tests from intents
        if verbose:
            print(f"\n🧪 Step 2: Generating domain-specific tests...")
        
        for intent in intents:
            try:
                tests = self._generate_tests_from_intent(intent)
                all_test_cases.extend(tests)
                
                if verbose:
                    print(f"   ✅ {intent.requirement_id}: {len(tests)} tests generated")
                
            except Exception as e:
                if verbose:
                    print(f"   ❌ {intent.requirement_id}: {e}")
        
        self.stats["test_cases_generated"] = len(all_test_cases)
        
        # Step 3: Deduplicate
        if auto_deduplicate and verbose:
            print(f"\n🎯 Step 3: Deduplicating {len(all_test_cases)} test cases...")
        
        if auto_deduplicate:
            all_test_cases = self.deduplicator.deduplicate(all_test_cases)
            self.stats["test_cases_deduplicated"] = self.stats["test_cases_generated"] - len(all_test_cases)
        
        # Step 4: Summary
        if verbose:
            print(f"\n📈 SUMMARY:")
            print(f"   Requirements processed: {self.stats['requirements_processed']}")
            print(f"   Tests generated: {self.stats['test_cases_generated']}")
            print(f"   Tests deduplicated: {self.stats['test_cases_deduplicated']}")
            print(f"   Final unique tests: {len(all_test_cases)}")
            print("=" * 70 + "\n")
        
        return {
            "status": "success" if all_test_cases else "no_tests",
            "test_cases": all_test_cases,
            "summary": {
                "requirements_processed": self.stats["requirements_processed"],
                "test_cases_generated": self.stats["test_cases_generated"],
                "test_cases_deduplicated": self.stats["test_cases_deduplicated"],
                "unique_tests_final": len(all_test_cases),
                "intents_extracted": len(intents),
            },
            "generated_at": datetime.now().isoformat(),
        }
    
    def _generate_tests_from_intent(self, intent: StructuredIntent) -> List[Dict[str, Any]]:
        """Generate test cases from a single StructuredIntent"""
        tests = []
        
        # Generate tests based on domain
        if intent.domain == DomainType.HOTEL_MANAGEMENT:
            tests = self._hotel_management_tests(intent)
        elif intent.domain == DomainType.BANKING:
            tests = self._banking_tests(intent)
        elif intent.domain == DomainType.ECOMMERCE:
            tests = self._ecommerce_tests(intent)
        elif intent.domain == DomainType.HEALTHCARE:
            tests = self._healthcare_tests(intent)
        else:
            tests = self._generic_tests(intent)
        
        # Add security tests
        if intent.security_concerns:
            tests.extend(self._security_tests(intent))
        
        return tests
    
    def _hotel_management_tests(self, intent: StructuredIntent) -> List[Dict[str, Any]]:
        """Hotel management domain tests"""
        tests = []
        entity = intent.primary_entity.name
        action = intent.primary_action.verb
        
        # Test 1: Happy path - successful booking
        tests.append({
            "test_id": f"TC-HOTEL-HAPP-{self._next_id()}",
            "requirement_id": intent.requirement_id,
            "title": f"Successfully create new {entity} booking with all required information",
            "description": f"User can create a new booking with room type, check-in/out dates, and customer information",
            "test_type": "happy_path",
            "priority": "HIGH",
            "steps": [
                "Log in to system",
                "Navigate to booking creation",
                "Select room type (Single, Double, Suite, etc.)",
                "Enter check-in date",
                "Enter check-out date",
                "Enter customer information (name, phone, email)",
                "Review reservation summary",
                "Confirm booking",
            ],
            "expected_result": "Booking created successfully with confirmation number",
            "domain": intent.domain.value,
            "effort_hours": 0.5,
            "ml_quality_score": 0.88,
        })
        
        # Test 2: Availability checking
        tests.append({
            "test_id": f"TC-HOTEL-FUNC-{self._next_id()}",
            "requirement_id": intent.requirement_id,
            "title": "Verify room availability is correctly checked by type and dates",
            "description": "System must show accurate availability status for different room types on selected dates",
            "test_type": "functional",
            "priority": "HIGH",
            "steps": [
                "Search for available rooms",
                "Select date range",
                "Filter by room type",
                "Check availability status",
            ],
            "expected_result": "Only available rooms are displayed with correct capacity and amenities",
            "domain": intent.domain.value,
            "effort_hours": 0.4,
            "ml_quality_score": 0.85,
        })
        
        # Test 3: Negative test - invalid dates
        tests.append({
            "test_id": f"TC-HOTEL-NEGA-{self._next_id()}",
            "requirement_id": intent.requirement_id,
            "title": "Reject booking with check-out date before check-in date",
            "description": "System prevents invalid date range bookings",
            "test_type": "negative",
            "priority": "HIGH",
            "steps": [
                "Initiate booking",
                "Enter check-in: 2026-04-15",
                "Enter check-out: 2026-04-10",
                "Attempt to confirm",
            ],
            "expected_result": "Booking rejected with error: 'Check-out must be after check-in'",
            "domain": intent.domain.value,
            "effort_hours": 0.2,
            "ml_quality_score": 0.82,
        })
        
        # Test 4: Cancel booking
        tests.append({
            "test_id": f"TC-HOTEL-HAPP-{self._next_id()}",
            "requirement_id": intent.requirement_id,
            "title": "Successfully cancel an existing booking",
            "description": "User can cancel a confirmed booking",
            "test_type": "happy_path",
            "priority": "MEDIUM",
            "steps": [
                "Log in to account",
                "Navigate to 'My Bookings'",
                "Select a confirmed booking",
                "Click 'Cancel Booking'",
                "Confirm cancellation",
            ],
            "expected_result": "Booking cancelled, refund initiated, confirmation email sent",
            "domain": intent.domain.value,
            "effort_hours": 0.3,
            "ml_quality_score": 0.83,
        })
        
        # Test 5: Edit booking
        tests.append({
            "test_id": f"TC-HOTEL-HAPP-{self._next_id()}",
            "requirement_id": intent.requirement_id,
            "title": "Successfully modify an existing booking",
            "description": "User can edit check-in/out dates or room type",
            "test_type": "happy_path",
            "priority": "MEDIUM",
            "steps": [
                "Log in to account",
                "Go to 'My Bookings'",
                "Select booking to modify",
                "Edit check-in date",
                "Edit check-out date",
                "Save changes",
            ],
            "expected_result": "Booking updated, new total price calculated, confirmation sent",
            "domain": intent.domain.value,
            "effort_hours": 0.4,
            "ml_quality_score": 0.84,
        })
        
        # Test 6: Data validation
        tests.append({
            "test_id": f"TC-HOTEL-EDGE-{self._next_id()}",
            "requirement_id": intent.requirement_id,
            "title": "Validate customer information fields are required",
            "description": "All mandatory customer fields must be filled before booking",
            "test_type": "edge_case",
            "priority": "HIGH",
            "steps": [
                "Start booking process",
                "Skip entering customer name",
                "Attempt to confirm",
            ],
            "expected_result": "Form validation error: 'Customer name is required'",
            "domain": intent.domain.value,
            "effort_hours": 0.25,
            "ml_quality_score": 0.80,
        })
        
        return tests
    
    def _banking_tests(self, intent: StructuredIntent) -> List[Dict[str, Any]]:
        """Banking domain tests"""
        tests = []
        action = intent.primary_action.verb
        
        tests.append({
            "test_id": f"TC-BANK-HAPP-{self._next_id()}",
            "requirement_id": intent.requirement_id,
            "title": f"Successfully {action} with OTP verification",
            "description": "User can complete transaction with valid OTP",
            "test_type": "happy_path",
            "priority": "CRITICAL",
            "steps": [
                "Initiate transaction",
                "Receive OTP code",
                "Enter OTP",
                "Confirm transaction",
            ],
            "expected_result": "Transaction completed successfully",
            "domain": intent.domain.value,
            "effort_hours": 0.75,
            "ml_quality_score": 0.90,
        })
        
        tests.append({
            "test_id": f"TC-BANK-SEC-{self._next_id()}",
            "requirement_id": intent.requirement_id,
            "title": "Prevent unauthorized transaction without OTP",
            "description": "System requires OTP for any money transfer",
            "test_type": "security",
            "priority": "CRITICAL",
            "steps": [
                "Attempt transaction",
                "Skip OTP step",
            ],
            "expected_result": "Transaction blocked, OTP required",
            "domain": intent.domain.value,
            "effort_hours": 1.0,
            "ml_quality_score": 0.95,
        })
        
        return tests
    
    def _ecommerce_tests(self, intent: StructuredIntent) -> List[Dict[str, Any]]:
        """E-commerce domain tests"""
        tests = []
        
        tests.append({
            "test_id": f"TC-ECOM-HAPP-{self._next_id()}",
            "requirement_id": intent.requirement_id,
            "title": "Complete purchase and checkout",
            "description": "Customer successfully purchases product",
            "test_type": "happy_path",
            "priority": "HIGH",
            "steps": [
                "Search for product",
                "Add to cart",
                "Proceed to checkout",
                "Enter shipping address",
                "Complete payment",
            ],
            "expected_result": "Order confirmed, receipt sent",
            "domain": intent.domain.value,
            "effort_hours": 0.6,
            "ml_quality_score": 0.82,
        })
        
        return tests
    
    def _healthcare_tests(self, intent: StructuredIntent) -> List[Dict[str, Any]]:
        """Healthcare domain tests"""
        tests = []
        
        tests.append({
            "test_id": f"TC-HEALTH-HAPP-{self._next_id()}",
            "requirement_id": intent.requirement_id,
            "title": "Schedule medical appointment",
            "description": "Patient successfully books doctor appointment",
            "test_type": "happy_path",
            "priority": "HIGH",
            "steps": [
                "Select doctor/specialty",
                "Choose time slot",
                "Confirm appointment",
            ],
            "expected_result": "Appointment confirmed, reminder sent",
            "domain": intent.domain.value,
            "effort_hours": 0.5,
            "ml_quality_score": 0.84,
        })
        
        # Healthcare security
        tests.append({
            "test_id": f"TC-HEALTH-SEC-{self._next_id()}",
            "requirement_id": intent.requirement_id,
            "title": "Protect patient data privacy",
            "description": "Ensure patient records not accessible to unauthorized users",
            "test_type": "security",
            "priority": "CRITICAL",
            "steps": [
                "Login as different patient",
                "Try to access other patient records",
            ],
            "expected_result": "Access denied, patient data protected",
            "domain": intent.domain.value,
            "effort_hours": 1.0,
            "ml_quality_score": 0.92,
        })
        
        return tests
    
    def _generic_tests(self, intent: StructuredIntent) -> List[Dict[str, Any]]:
        """Fallback generic tests"""
        tests = []
        
        tests.append({
            "test_id": f"TC-GEN-HAPP-{self._next_id()}",
            "requirement_id": intent.requirement_id,
            "title": f"Successfully {intent.primary_action.verb} {intent.primary_entity.name}",
            "description": f"User can {intent.primary_action.verb} with valid input",
            "test_type": "happy_path",
            "priority": "MEDIUM",
            "steps": [
                "Access system",
                f"Perform {intent.primary_action.verb} action",
                "Verify success",
            ],
            "expected_result": "Action completed successfully",
            "domain": intent.domain.value,
            "effort_hours": 0.5,
            "ml_quality_score": 0.70,
        })
        
        return tests
    
    def _security_tests(self, intent: StructuredIntent) -> List[Dict[str, Any]]:
        """Generate security-specific tests from detected concerns"""
        tests = []
        
        for concern in intent.security_concerns:
            tests.append({
                "test_id": f"TC-{intent.domain.value[:3].upper()}-SEC-{self._next_id()}",
                "requirement_id": intent.requirement_id,
                "title": f"Security: {concern.concern_type.replace('_', ' ').title()}",
                "description": concern.description,
                "test_type": "security",
                "priority": "CRITICAL" if concern.severity == "critical" else "HIGH",
                "steps": [
                    f"Attempt exploitation for {concern.concern_type}",
                    "Verify system prevents breach",
                ],
                "expected_result": "Attack prevented, system remains secure",
                "domain": intent.domain.value,
                "effort_hours": 1.0,
                "ml_quality_score": 0.92,
            })
        
        return tests
    
    _id_counter = 0
    
    def _next_id(self) -> str:
        self._id_counter += 1
        return f"{self._id_counter:03d}"


# For backward compatibility
def create_pipeline(extractor: Optional[RequirementExtractor] = None) -> TestGenerationPipeline:
    """Factory function to create pipeline"""
    return TestGenerationPipeline(extractor)
