"""
Healthcare Domain Knowledge Base
Extracted healthcare-specific rules, entities, risks, and test strategies
Phase 5 of AI Test Case Generator v2
"""

from typing import Dict, List, Set
from enum import Enum


class RiskLevel(Enum):
    CRITICAL = "CRITICAL"  # Patient safety at risk
    HIGH = "HIGH"  # Compliance or data security
    MEDIUM = "MEDIUM"  # Process or data integrity
    LOW = "LOW"  # UI/UX or minor functionality


class HealthcareCriticalFlow(Enum):
    ALLERGY_DETECTION = "allergy_detection"
    DRUG_INTERACTION = "drug_interaction"
    INSURANCE_VERIFICATION = "insurance_verification"
    HIPAA_COMPLIANCE = "hipaa_compliance"
    PATIENT_SAFETY = "patient_safety"
    PRESCRIPTION_VALIDATION = "prescription_validation"


class HealthcareEntity(Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    PRESCRIPTION = "prescription"
    APPOINTMENT = "appointment"
    ALLERGY = "allergy"
    MEDICATION = "medication"
    INSURANCE = "insurance"
    RECORD = "medical_record"


class HealthcareDomainKB:
    """
    Healthcare Domain Knowledge Base
    Contains healthcare-specific rules, risks, and test strategies
    """

    def __init__(self):
        # Critical flows that MUST be tested thoroughly
        self.critical_flows = {
            HealthcareCriticalFlow.ALLERGY_DETECTION: {
                "description": "Detect patient allergies before medication",
                "risk_level": RiskLevel.CRITICAL,
                "keywords": ["allergy", "dị ứng", "reaction", "phản ứng", "sensitivity"],
                "test_multiplier": 3,  # Test 3x more for this
                "required_test_types": [
                    "boundary_value",
                    "negative",
                    "security",
                ],
                "example_tests": [
                    "Allergy NOT detected when system disabled",
                    "Multiple allergies cross-check",
                    "Allergy in different language variations",
                    "Severity levels (mild, moderate, severe)",
                ],
            },
            HealthcareCriticalFlow.DRUG_INTERACTION: {
                "description": "Check drug interactions with current medications",
                "risk_level": RiskLevel.CRITICAL,
                "keywords": ["interaction", "tương tác", "contraindication", "chống chỉ định"],
                "test_multiplier": 3,
                "required_test_types": ["boundary_value", "negative", "security"],
                "example_tests": [
                    "Known interaction pair detected",
                    "Partial name match for drugs",
                    "Multiple drug interactions (3+ drugs)",
                    "Interaction with different dosages",
                    "Time of interaction (cumulative effect)",
                ],
            },
            HealthcareCriticalFlow.INSURANCE_VERIFICATION: {
                "description": "Verify patient insurance coverage",
                "risk_level": RiskLevel.HIGH,
                "keywords": ["insurance", "bảo hiểm", "coverage", "coverage", "claim"],
                "test_multiplier": 2.5,
                "required_test_types": ["boundary_value", "negative"],
                "example_tests": [
                    "Policy active vs expired",
                    "Coverage amount validation",
                    "Pre-authorization required",
                    "Out-of-pocket calculations",
                ],
            },
            HealthcareCriticalFlow.HIPAA_COMPLIANCE: {
                "description": "Ensure HIPAA privacy protection",
                "risk_level": RiskLevel.HIGH,
                "keywords": ["privacy", "bảo mật", "hipaa", "compliance", "tuân thủ"],
                "test_multiplier": 2.5,
                "required_test_types": ["security", "negative"],
                "example_tests": [
                    "Unauthorized access blocked",
                    "Patient data masked in logs",
                    "Audit trail logged",
                    "Encryption of sensitive data",
                    "Data retention policies",
                ],
            },
            HealthcareCriticalFlow.PATIENT_SAFETY: {
                "description": "General patient safety checks",
                "risk_level": RiskLevel.CRITICAL,
                "keywords": ["safety", "an toàn", "risk", "nguy hiểm", "adverse"],
                "test_multiplier": 3,
                "required_test_types": ["boundary_value", "negative", "security"],
                "example_tests": [
                    "Dosage limits exceeded",
                    "Age-based restrictions (pediatric)",
                    "Pregnancy contraindications",
                    "Renal/hepatic impairment considerations",
                ],
            },
            HealthcareCriticalFlow.PRESCRIPTION_VALIDATION: {
                "description": "Validate prescription details",
                "risk_level": RiskLevel.CRITICAL,
                "keywords": ["prescription", "đơn thuốc", "prescribe", "dosage", "liều lượng"],
                "test_multiplier": 2.5,
                "required_test_types": ["boundary_value", "negative"],
                "example_tests": [
                    "Invalid dosage",
                    "Wrong frequency",
                    "Quantity limits",
                    "Duration limits",
                    "Drug class restrictions",
                ],
            },
        }

        # Healthcare entities and their attributes
        self.entities = {
            HealthcareEntity.PATIENT: {
                "critical_attributes": [
                    "patient_id",
                    "age",
                    "gender",
                    "allergies",
                    "current_medications",
                    "insurance_id",
                    "medical_history",
                ],
                "validation_rules": [
                    "patient_id must be unique",
                    "age must be between 0-150",
                    "gender must be valid",
                    "allergies must be checked against medical DB",
                ],
            },
            HealthcareEntity.DOCTOR: {
                "critical_attributes": [
                    "doctor_id",
                    "license_number",
                    "specialty",
                    "available_hours",
                    "qualifications",
                ],
                "validation_rules": [
                    "license_number must be valid",
                    "specialty must be from approved list",
                    "available_hours must be within working hours",
                ],
            },
            HealthcareEntity.MEDICATION: {
                "critical_attributes": [
                    "drug_id",
                    "drug_name",
                    "active_ingredient",
                    "dosage",
                    "frequency",
                    "contraindications",
                    "interactions",
                ],
                "validation_rules": [
                    "drug_id must be valid FDA ID",
                    "dosage must be within therapeutic range",
                    "interactions must be cross-checked",
                ],
            },
            HealthcareEntity.APPOINTMENT: {
                "critical_attributes": [
                    "appointment_id",
                    "patient_id",
                    "doctor_id",
                    "appointment_date",
                    "appointment_time",
                    "appointment_type",
                    "status",
                ],
                "validation_rules": [
                    "date must be in future",
                    "date must be within 30 days (if applicable)",
                    "doctor must be available",
                    "patient must not have conflicts",
                ],
            },
            HealthcareEntity.ALLERGY: {
                "critical_attributes": [
                    "allergy_id",
                    "patient_id",
                    "allergen",
                    "reaction_type",
                    "severity",
                    "reported_date",
                ],
                "validation_rules": [
                    "allergen must be valid",
                    "severity must be (mild|moderate|severe)",
                    "reaction must be documented",
                ],
            },
        }

        # Healthcare-specific test data
        self.test_data_templates = {
            "healthy_patient": {
                "patient_id": "PAT_H001",
                "name": "Nguyễn Văn A",
                "age": 35,
                "gender": "M",
                "allergies": [],
                "current_medications": [],
                "insurance_status": "active",
            },
            "patient_with_allergy": {
                "patient_id": "PAT_AL001",
                "name": "Trần Thị B",
                "age": 45,
                "gender": "F",
                "allergies": ["Penicillin (severe)"],
                "current_medications": ["Aspirin 100mg daily"],
                "insurance_status": "active",
            },
            "patient_with_conflicts": {
                "patient_id": "PAT_CF001",
                "name": "Hoàng Văn C",
                "age": 28,
                "gender": "M",
                "allergies": ["Sulfonamide (moderate)"],
                "current_medications": ["Warfarin", "Metformin 1000mg"],
                "insurance_status": "active",
            },
            "high_risk_patient": {
                "patient_id": "PAT_HR001",
                "name": "Võ Thị D",
                "age": 72,
                "gender": "F",
                "allergies": ["ACE Inhibitors", "NSAIDs"],
                "current_medications": [
                    "Lisinopril",
                    "Atorvastatin",
                    "Metoprolol",
                ],
                "insurance_status": "expired",
            },
        }

        # Known drug interactions (sample database)
        self.known_interactions = {
            "Warfarin": [
                "Aspirin",
                "NSAIDs",
                "Antibiotics (certain types)",
            ],
            "Metformin": [
                "Contrast dye",
                "Some diuretics",
            ],
            "ACE_Inhibitors": [
                "Potassium supplements",
                "NSAIDs",
            ],
            "Penicillin": [
                "Methotrexate",
            ],
        }

        # Healthcare test strategies
        self.test_strategies = {
            "allergy_testing": [
                "Test with patient having no allergies",
                "Test with patient having single allergy",
                "Test with patient having multiple allergies",
                "Test with similar named allergens (e.g., Penicillin vs Amoxicillin)",
                "Test when allergy system is down (should fail safely)",
                "Test with different severity levels",
            ],
            "drug_interaction_testing": [
                "Test known interaction pair (e.g., Warfarin + Aspirin)",
                "Test non-interacting pair",
                "Test 3+ drugs for interactions",
                "Test with generic names vs brand names",
                "Test interaction database consistency",
                "Test when interaction check is disabled",
            ],
            "insurance_testing": [
                "Test with active insurance",
                "Test with expired insurance",
                "Test with coverage limits",
                "Test with unauthorized user",
                "Test pre-authorization requirements",
                "Test claim submission",
            ],
            "appointment_scheduling": [
                "Test appointment within allowed range",
                "Test appointment at boundary (30 days)",
                "Test appointment beyond allowed range",
                "Test appointment on doctor's available time",
                "Test conflicting appointments",
                "Test concurrent bookings (race condition)",
            ],
        }

    def is_critical_flow(self, requirement_text: str) -> Dict:
        """Check if requirement involves critical healthcare flow"""
        requirement_lower = requirement_text.lower()

        for critical_flow in self.critical_flows.values():
            for keyword in critical_flow["keywords"]:
                if keyword in requirement_lower:
                    return {
                        "is_critical": True,
                        "flow": critical_flow,
                        "risk_level": critical_flow["risk_level"].value,
                        "test_multiplier": critical_flow["test_multiplier"],
                    }

        return {
            "is_critical": False,
            "flow": None,
            "risk_level": "MEDIUM",
            "test_multiplier": 1.0,
        }

    def get_test_multiplier(self, requirement_text: str) -> float:
        """Get test case generation multiplier for requirement"""
        critical_info = self.is_critical_flow(requirement_text)
        return critical_info.get("test_multiplier", 1.0)

    def get_required_test_types(self, requirement_text: str) -> List[str]:
        """Get required test types for requirement"""
        critical_info = self.is_critical_flow(requirement_text)
        if critical_info["is_critical"]:
            return critical_info["flow"]["required_test_types"]
        return ["happy_path", "negative", "boundary_value"]

    def get_test_strategies(self, critical_flow_type: str) -> List[str]:
        """Get recommended test strategies for flow type"""
        if critical_flow_type == "allergy_detection":
            return self.test_strategies.get("allergy_testing", [])
        if critical_flow_type == "drug_interaction":
            return self.test_strategies.get("drug_interaction_testing", [])
        if critical_flow_type == "insurance_verification":
            return self.test_strategies.get("insurance_testing", [])
        if critical_flow_type == "appointment_scheduling":
            return self.test_strategies.get("appointment_scheduling", [])
        return []

    def validate_test_data(self, entity_type: str, test_data: Dict) -> Dict:
        """Validate test data against healthcare rules"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
        }

        entity = self.entities.get(HealthcareEntity[entity_type.upper()])
        if not entity:
            return validation_result

        # Check required attributes
        required = entity.get("critical_attributes", [])
        missing = [attr for attr in required if attr not in test_data]
        if missing:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Missing critical attributes: {missing}")

        # Check validation rules (simplified)
        rules = entity.get("validation_rules", [])
        if entity_type.upper() == "PATIENT":
            age = test_data.get("age")
            if age and (age < 0 or age > 150):
                validation_result["errors"].append(f"Invalid age: {age}")
                validation_result["valid"] = False

        return validation_result


# Test
if __name__ == "__main__":
    kb = HealthcareDomainKB()

    print("=" * 70)
    print("HEALTHCARE DOMAIN KNOWLEDGE BASE")
    print("=" * 70)

    # Test 1: Check critical flows
    test_requirement = "Hệ thống phải cảnh báo dị ứng thuốc khi tiếp nhận đơn thuốc mới"
    critical = kb.is_critical_flow(test_requirement)
    print(f"\nRequirement: {test_requirement}")
    print(f"Critical Flow: {critical}")

    # Test 2: Get test multiplier
    multiplier = kb.get_test_multiplier(test_requirement)
    print(f"Test Multiplier: {multiplier}x")

    # Test 3: Get test strategies
    print("\nTest Strategies for Allergy Detection:")
    strategies = kb.get_test_strategies("allergy_detection")
    for i, strategy in enumerate(strategies, 1):
        print(f"  {i}. {strategy}")

    # Test 4: Validate test data
    print("\nValidating patient test data:")
    test_patient = kb.test_data_templates["patient_with_allergy"]
    validation = kb.validate_test_data("patient", test_patient)
    print(f"Valid: {validation['valid']}")
    if validation["errors"]:
        print(f"Errors: {validation['errors']}")

    print("\n" + "=" * 70)
