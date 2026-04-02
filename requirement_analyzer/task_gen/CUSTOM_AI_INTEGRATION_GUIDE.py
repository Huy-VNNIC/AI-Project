"""
CUSTOM AI INTEGRATION GUIDE
How to integrate YOUR trained AI model with the test generation pipeline
"""

# ============================================================================
# 📖 WHAT YOU HAVE NOW
# ============================================================================

"""
✅ Complete LLM-Free AI test generation pipeline:

requirement_analyzer/task_gen/
├── structured_intent.py           → Data models for extraction output
├── requirement_extractor.py        → Interface for your AI model
├── test_generation_pipeline.py     → Main pipeline (NO external APIs)
├── deduplication_engine.py         → Remove duplicate test cases
├── example_usage.py                → Usage examples
└── INTEGRATION_GUIDE.md            ← You are here

Pipeline Flow:
  Your Requirements
        ↓
  [Your AI Model] ← Implement RequirementExtractor
        ↓
  StructuredIntent (JSON-like)
        ↓
  Domain-Specific Test Generator
        ↓
  Raw Test Cases
        ↓
  Deduplication Engine
        ↓
  ✅ Final Unique Test Cases

KEY: No external API calls needed! You build it all.
"""

# ============================================================================
# 🔧 STEP 1: Understand the Interface (requirement_extractor.py)
# ============================================================================

"""
Your AI model must implement RequirementExtractor abstract class:

class RequirementExtractor(ABC):
    @abstractmethod
    def extract(self, requirement_text: str) -> StructuredIntent:
        # Takes: "Khách hàng phải đặt phòng hotel..."
        # Returns: StructuredIntent(
        #     domain=DomainType.HOTEL_MANAGEMENT,
        #     primary_entity=Entity(name="booking", ...),
        #     primary_action=Action(verb="create", ...),
        #     constraints=[...],
        #     security_concerns=[...],
        #     ...
        # )

The StructuredIntent is just JSON-like data structure:
{
    "domain": "hotel_management",
    "primary_entity": {
        "name": "booking",
        "description": "Hotel booking reservation",
        "attributes": ["guest_name", "dates", "room_type"]
    },
    "primary_action": {
        "verb": "create",
        "target": "booking"
    },
    "constraints": [
        {
            "name": "date_range",
            "description": "Check-out must be after check-in",
            "values": ["2026-04-15", "2026-04-18"]
        }
    ],
    "security_concerns": [
        {
            "concern_type": "authentication",
            "severity": "high",
            "description": "User must be authenticated"
        }
    ]
}
"""

# ============================================================================
# 🎯 STEP 2: Create Your Custom Extractor
# ============================================================================

"""
TEMPLATE CODE (requirement_analyzer/task_gen/your_extractor.py):

from requirement_extractor import RequirementExtractor
from structured_intent import (
    StructuredIntent, DomainType, Entity, Action,
    Constraint, SecurityConcern
)


class YourAIExtractor(RequirementExtractor):
    def __init__(self, model_path: str):
        # Load your trained model
        # self.model = load_model(model_path)
        # self.tokenizer = load_tokenizer()
        # self.vocab = load_vocab()
        pass
    
    def extract(self, requirement_text: str) -> StructuredIntent:
        # 1. Preprocess text
        preprocessed = self._preprocess(requirement_text)
        
        # 2. Tokenize (handle Vietnamese properly!)
        tokens = self._tokenize(preprocessed)
        
        # 3. Pass through your AI model
        output = self.model.predict(tokens)  # ← Your model here
        
        # 4. Parse output to extract components
        domain = self._extract_domain(output)
        entity = self._extract_entity(output)
        action = self._extract_action(output)
        constraints = self._extract_constraints(output)
        security = self._extract_security(output)
        
        # 5. Build StructuredIntent
        intent = StructuredIntent(
            requirement_id="REQ-TEMP",
            original_text=requirement_text,
            domain=domain,
            primary_entity=entity,
            primary_action=action,
            constraints=constraints,
            security_concerns=security,
            confidence_score=output.get("confidence", 0.8),
            extraction_model="your_model_name",
        )
        
        return intent
    
    def extract_batch(self, requirements: List[str]) -> List[StructuredIntent]:
        # Implement efficient batch processing
        # (might use batching in your model for speed)
        return [self.extract(req) for req in requirements]
    
    def _preprocess(self, text: str) -> str:
        # Remove extra whitespace, normalize Vietnamese
        # Handle special characters
        return text.strip().lower()
    
    def _tokenize(self, text: str) -> List[str]:
        # CRITICAL: Handle Vietnamese tokenization properly!
        # Options:
        # 1. underthesea (Vietnamese NLP)
        # 2. pyvi (Vietnamese tokenizer)
        # 3. Your custom tokenizer
        # 4. Character-level tokens
        
        # Example: using underthesea for Vietnamese
        from underthesea import word_tokenize
        return word_tokenize(text)
    
    def _extract_domain(self, output) -> DomainType:
        domain_str = output.get("domain", "general")
        domain_map = {
            "hotel_management": DomainType.HOTEL_MANAGEMENT,
            "banking": DomainType.BANKING,
            "ecommerce": DomainType.ECOMMERCE,
            "healthcare": DomainType.HEALTHCARE,
            "general": DomainType.GENERAL,
        }
        return domain_map.get(domain_str, DomainType.GENERAL)
    
    def _extract_entity(self, output) -> Entity:
        entity_data = output.get("entity", {})
        return Entity(
            name=entity_data.get("name", "resource"),
            description=entity_data.get("description", ""),
            attributes=entity_data.get("attributes", []),
            relationships=entity_data.get("relationships", [])
        )
    
    def _extract_action(self, output) -> Action:
        action_data = output.get("action", {})
        return Action(
            verb=action_data.get("verb", "perform"),
            target=action_data.get("target", "entity"),
            description=action_data.get("description", ""),
            preconditions=action_data.get("preconditions", []),
            postconditions=action_data.get("postconditions", [])
        )
    
    def _extract_constraints(self, output) -> List[Constraint]:
        constraints_data = output.get("constraints", [])
        constraints = []
        for c in constraints_data:
            constraints.append(Constraint(
                name=c.get("name", ""),
                description=c.get("description", ""),
                constraint_type=c.get("type", "unknown"),
                values=c.get("values", [])
            ))
        return constraints
    
    def _extract_security(self, output) -> List[SecurityConcern]:
        security_data = output.get("security_concerns", [])
        concerns = []
        for s in security_data:
            concerns.append(SecurityConcern(
                concern_type=s.get("type", ""),
                description=s.get("description", ""),
                severity=s.get("severity", "medium"),
                test_cases_needed=[]
            ))
        return concerns
"""

# ============================================================================
# 💻 STEP 3: Example Integration
# ============================================================================

"""
Once you have YourAIExtractor, use it in the pipeline:

from test_generation_pipeline import TestGenerationPipeline
from your_extractor import YourAIExtractor

# Initialize your AI model
extractor = YourAIExtractor(model_path="/path/to/your/model")

# Create pipeline with your extractor
pipeline = TestGenerationPipeline(extractor=extractor)

# Process requirements
requirements = [
    "Khách hàng phải đặt phòng hotel với ngày hợp lệ",
    "Hệ thống phải kiểm tra tính khả dụng",
    "Người dùng phải xác thực bằng OTP",
]

result = pipeline.process_requirements(
    requirements,
    auto_deduplicate=True,
    verbose=True
)

# Get results
test_cases = result["test_cases"]
summary = result["summary"]

print(f"✅ Generated {len(test_cases)} unique test cases")
print(f"✅ Summary: {summary}")

# Export to JSON
import json
with open("test_cases.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
"""

# ============================================================================
# 🎯 STEP 4: What Your AI Model Should Output
# ============================================================================

"""
Your AI model can structure output in many ways:
1. JSON dict
2. Named tuple
3. Custom class
4. List of values

Key is that _extract_* methods parse it into StructuredIntent.

MINIMAL OUTPUT (enough to work):
{
    "domain": "hotel_management",
    "entity": {"name": "booking"},
    "action": {"verb": "create"},
}

COMPLETE OUTPUT (optimal):
{
    "domain": "hotel_management",
    "entity": {
        "name": "booking",
        "description": "Hotel room reservation",
        "attributes": ["guest_name", "check_in_date", "check_out_date", "room_type"],
        "relationships": ["guest", "room", "payment"]
    },
    "action": {
        "verb": "create",
        "target": "booking",
        "description": "Customer books a room",
        "preconditions": ["user_logged_in", "room_available"],
        "postconditions": ["booking_created", "confirmation_sent"]
    },
    "constraints": [
        {
            "name": "date_constraint",
            "description": "Check-out must be after check-in",
            "type": "date_range",
            "values": ["2026-04-15", "2026-04-18"]
        },
        {
            "name": "capacity_constraint",
            "description": "Room capacity must be <= booked guests",
            "type": "numeric",
            "values": ["1", "10"]
        }
    ],
    "security_concerns": [
        {
            "type": "authentication",
            "severity": "high",
            "description": "Only authenticated users can book"
        },
        {
            "type": "authorization",
            "severity": "medium",
            "description": "Users can only modify their own bookings"
        }
    ],
    "confidence": 0.92
}
"""

# ============================================================================
# 🔍 STEP 5: Handle Vietnamese Text Properly
# ============================================================================

"""
CRITICAL: Vietnamese text tokenization

Your current system has broken Vietnamese parsing.
Your new AI MUST handle:
- "đặt phòng" (book room) → entity="booking"
- "khách hàng" (customer) → actor="customer"
- "xác thực" (authenticate) → action="authenticate"
- "OTP" → security concept

RECOMMENDED LIBRARIES:
1. underthesea (best for Vietnamese)
   pip install underthesea
   from underthesea import word_tokenize, ner, sentiment
   tokens = word_tokenize("Khách hàng phải đặt phòng")
   # → ["Khách hàng", "phải", "đặt", "phòng"]
   
2. pyvi (lightweight)
   pip install pyvi
   from pyvi import ViTokenizer
   tokens = ViTokenizer.tokenize("Khách hàng phải đặt phòng")
   # → "Khách_hàng phải đặt_phòng"

3. Your own rules
   Build Vietnamese domain vocabulary:
   {
       "đặt phòng": "booking",
       "khách hàng": "customer",
       "xác thực": "authenticate",
       "OTP": "otp_verification",
       ...
   }
"""

# ============================================================================
# 📊 STEP 6: Testing Your Integration
# ============================================================================

"""
Test your custom extractor with these requirements:

HOTEL DOMAIN:
- "Khách hàng phải đặt phòng với ngày nhận và ngày trả hợp lệ"
- "Hệ thống phải kiểm tra tính khả dụng của phòng trước khi xác nhận"
- "Chỉ nhân viên có quyền quản lý phòng mới được phép xóa đặt phòng"

BANKING DOMAIN:
- "Người dùng phải xác thực bằng OTP trước khi chuyển khoản"
- "Hệ thống phải kiểm tra hạn mức giao dịch hàng ngày"
- "Tất cả giao dịch phải được ghi nhật ký để kiểm toán"

EXPECTED RESULTS:
✅ Correct domain detection
✅ Appropriate entity extraction
✅ Proper action identification
✅ Security concerns identified
✅ Confidence > 0.75
✅ No broken Vietnamese text in output
"""

# ============================================================================
# 🚀 STEP 7: Production Deployment
# ============================================================================

"""
Once your YourAIExtractor is ready:

1. Place in: requirement_analyzer/task_gen/your_extractor.py

2. Modify example_usage.py:
   from your_extractor import YourAIExtractor
   extractor = YourAIExtractor(model_path="...")
   pipeline = TestGenerationPipeline(extractor=extractor)

3. Run API:
   python -m requirement_analyzer.api
   
4. Then test through API:
   curl -X POST http://localhost:8000/api/v1/tests/generate \
     -H "Content-Type: application/json" \
     -d '{
       "requirements": ["Khách hàng phải đặt phòng..."],
       "version": "v4_enhanced"
     }'

5. Results will have:
   ✅ Unique test IDs (TC-HOTEL-HAPP-001, not TC-UNKNOWN)
   ✅ Real quality scores (0.85+, not hardcoded 0.5)
   ✅ Domain-specific tests (not generic "manage resource")
   ✅ No duplicates after deduplication
   ✅ Proper Vietnamese handling
"""

# ============================================================================
# 📝 SUMMARY CHECKLIST
# ============================================================================

"""
✅ Understand the pipeline flow
✅ Read structured_intent.py (data models)
✅ Read requirement_extractor.py (interface)
✅ Create your ExtractorImpl(RequirementExtractor)
✅ Implement extract() method with YOUR AI
✅ Test with sample requirements
✅ Integrate into pipeline
✅ Verify output format
✅ Deploy and test through API
✅ Optimize for Vietnamese text

🎉 You now have a production-ready, NO-EXTERNAL-API test generation system!
"""
