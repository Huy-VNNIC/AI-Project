"""
EXAMPLE: How to use the LLM-free AI test generation pipeline
Shows how to integrate YOUR custom AI model
"""

from typing import List
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_generation_pipeline import TestGenerationPipeline, create_pipeline
from requirement_extractor import RequirementExtractor, MockRequirementExtractor
from structured_intent import (
    StructuredIntent, DomainType, Entity, Action, 
    Constraint, SecurityConcern
)


# ============================================================================
# EXAMPLE 1: Using with your custom AI model
# ============================================================================

class YourCustomAIExtractor(RequirementExtractor):
    """
    TEMPLATE: Replace this with YOUR actual AI model
    
    Your AI model should:
    1. Take requirement text as input
    2. Extract: domain, entities, actions, constraints, security concerns
    3. Return StructuredIntent
    
    Example: Use your pretrained model that outputs JSON structured data
    """
    
    def __init__(self, model_path: str = None):
        """Initialize with your trained AI model"""
        self.model_path = model_path
        # Load your model here
        # self.model = load_your_model(model_path)
    
    def extract(self, requirement_text: str) -> StructuredIntent:
        """
        YOUR IMPLEMENTATION HERE
        
        Steps:
        1. Tokenize requirement_text
        2. Pass through your AI model
        3. Parse output
        4. Build StructuredIntent
        5. Return
        """
        
        # PLACEHOLDER EXAMPLE (replace with your actual model)
        # Your model should output something like:
        # {
        #   "domain": "hotel_management",
        #   "entity": "booking",
        #   "action": "create",
        #   "constraints": [...],
        #   "security_concerns": [...]
        # }
        
        # For now, using mock fallback
        from requirement_extractor import MockRequirementExtractor
        mock = MockRequirementExtractor()
        return mock.extract(requirement_text)
    
    def extract_batch(self, requirements: List[str]) -> List[StructuredIntent]:
        """Extract multiple requirements efficiently"""
        return [self.extract(req) for req in requirements]


# ============================================================================
# EXAMPLE 2: Test with real hotel management requirements
# ============================================================================

def example_hotel_management():
    """Test with hotel management domain"""
    print("\n" + "="*70)
    print("EXAMPLE: Hotel Management Requirements")
    print("="*70)
    
    requirements = [
        "Khách hàng phải đặt phòng với ngày nhận phòng và ngày trả phòng hợp lệ",
        "Hệ thống phải kiểm tra tính khả dụng của phòng trước khi xác nhận đặt phòng",
        "Khách hàng phải cung cấp thông tin thanh toán để hoàn tất đặt phòng",
        "Hệ thống phải gửi email xác nhận sau khi đặt phòng thành công",
        "Chỉ nhân viên có quyền quản lý phòng mới được phép xóa đặt phòng",
    ]
    
    # Create pipeline with mock extractor (replace with your AI)
    pipeline = create_pipeline()
    
    # Process requirements
    result = pipeline.process_requirements(requirements, auto_deduplicate=True, verbose=True)
    
    # Print results
    print("\n📋 GENERATED TEST CASES:")
    for tc in result["test_cases"][:5]:  # Show first 5
        print(f"\n  {tc['test_id']}: {tc['title']}")
        print(f"    Type: {tc['test_type']} | Priority: {tc['priority']}")
        print(f"    Quality: {tc['ml_quality_score']:.0%}")
    
    if len(result["test_cases"]) > 5:
        print(f"\n  ... and {len(result['test_cases']) - 5} more test cases")
    
    return result


# ============================================================================
# EXAMPLE 3: Test with banking requirements
# ============================================================================

def example_banking():
    """Test with banking domain"""
    print("\n" + "="*70)
    print("EXAMPLE: Banking Requirements")
    print("="*70)
    
    requirements = [
        "Người dùng phải xác thực bằng OTP trước khi chuyển khoản",
        "Hệ thống phải kiểm tra hạn mức giao dịch hàng ngày",
        "Tất cả giao dịch phải được ghi nhật ký để kiểm toán",
        "Tài khoản bị khóa sau 5 lần nhập sai mật khẩu",
    ]
    
    pipeline = create_pipeline()
    result = pipeline.process_requirements(requirements, auto_deduplicate=True, verbose=True)
    
    print(f"\n✅ Generated {len(result['test_cases'])} test cases")
    print(f"✅ Summary: {result['summary']['unique_tests_final']} unique tests after deduplication")
    
    return result


# ============================================================================
# EXAMPLE 4: Custom extractor with your AI model
# ============================================================================

def example_with_custom_model():
    """
    This is how you would integrate YOUR trained AI model
    """
    print("\n" + "="*70)
    print("EXAMPLE: Using Your Custom AI Model")
    print("="*70)
    
    # STEP 1: Create instance of your custom extractor
    # (replace with path to your actual trained model)
    # custom_extractor = YourCustomAIExtractor(model_path="/path/to/your/model")
    
    # For demo, using mock
    custom_extractor = MockRequirementExtractor()
    
    # STEP 2: Create pipeline with your extractor
    pipeline = TestGenerationPipeline(extractor=custom_extractor)
    
    # STEP 3: Process requirements
    requirements = [
        "User must authenticate before accessing data",
        "System should handle 1000 concurrent requests",
    ]
    
    result = pipeline.process_requirements(
        requirements,
        auto_deduplicate=True,
        verbose=True
    )
    
    print(f"\n✅ Custom model extracted and generated tests successfully!")
    return result


# ============================================================================
# EXAMPLE 5: Export results to JSON
# ============================================================================

def export_results(result, filename="test_cases.json"):
    """Export generated test cases to JSON"""
    import json
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Exported to {filename}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "🎯 "*35)
    print("TEST GENERATION PIPELINE - NO EXTERNAL APIs")
    print("Build with your own AI model")
    print("🎯 "*35)
    
    # Run examples
    print("\n\n1️⃣  Hotel Management Example")
    result_hotel = example_hotel_management()
    
    print("\n\n2️⃣  Banking Example")
    result_banking = example_banking()
    
    print("\n\n3️⃣  Custom Model Example")
    result_custom = example_with_custom_model()
    
    # Display summary
    print("\n" + "="*70)
    print("📊 FINAL SUMMARY")
    print("="*70)
    print(f"✅ Hotel: {result_hotel['summary']['unique_tests_final']} tests")
    print(f"✅ Banking: {result_banking['summary']['unique_tests_final']} tests")
    print(f"✅ Custom: {result_custom['summary']['unique_tests_final']} tests")
    print("\n✅ All examples completed successfully!")
    print("\n🎯 NEXT STEPS:")
    print("1. Implement your custom RequirementExtractor (with your AI model)")
    print("2. Replace MockRequirementExtractor in pipeline")
    print("3. Test with your requirements")
    print("4. Fine-tune domain-specific generators")
    print("=" * 70)
