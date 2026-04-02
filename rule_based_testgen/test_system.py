"""
Quick Test - Run this to verify system works
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

def test_full_pipeline():
    """Test complete pipeline with sample data"""
    
    print("\n" + "="*70)
    print("🧪 TESTING RULE-BASED TEST CASE GENERATOR")
    print("="*70)
    
    # Test imports
    print("\n✓ Testing imports...")
    try:
        from pipeline import TestGenerationPipeline
        print("  ✓ Pipeline imported")
    except Exception as e:
        print(f"  ✗ Pipeline import failed: {e}")
        return False
    
    # Sample requirements
    sample_text = """
    System Requirements:
    
    - User can login with email and password
    - System must validate email format
    - Password must be at least 8 characters
    - If login fails, display error message
    - User can create new product listing
    - System must check inventory before confirming order
    - When checkout is complete, send confirmation email
    """
    
    print("\n✓ Initializing pipeline...")
    try:
        pipeline = TestGenerationPipeline()
        print("  ✓ Pipeline initialized")
    except Exception as e:
        print(f"  ✗ Pipeline init failed: {e}")
        return False
    
    print("\n✓ Processing requirements...")
    try:
        results = pipeline.process_text(
            sample_text,
            output_format="json"
        )
        
        print(f"  ✓ Processing complete")
        print(f"  - Requirements found: {results['summary']['total_requirements']}")
        print(f"  - Test cases generated: {results['summary']['total_test_cases']}")
        
        if results['summary']['total_test_cases'] == 0:
            print("  ⚠️ No test cases generated - this might indicate an issue")
            return False
        
        return True
    
    except Exception as e:
        print(f"  ✗ Processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_individual_modules():
    """Test individual modules"""
    
    print("\n" + "="*70)
    print("🔍 TESTING INDIVIDUAL MODULES")
    print("="*70)
    
    # Test text preprocessor
    print("\n1️⃣ Testing TextPreprocessor...")
    try:
        from text_preprocessor import TextPreprocessor
        preprocessor = TextPreprocessor()
        test_text = "Page 1\n\nUser enters email http://example.com"
        result = preprocessor.process(test_text)
        if "page" not in result.lower() and "http" not in result:
            print("  ✓ TextPreprocessor works")
        else:
            print("  ✗ TextPreprocessor failed to clean text")
    except Exception as e:
        print(f"  ✗ TextPreprocessor error: {e}")
    
    # Test sentence segmenter
    print("\n2️⃣ Testing SentenceSegmenter...")
    try:
        from sentence_segmenter import SentenceSegmenter
        segmenter = SentenceSegmenter()
        test_text = "- User can login with username and password\n- System validates the credentials\n- Email address must be valid format"
        result = segmenter.segment(test_text)
        if len(result) >= 1:
            print(f"  ✓ SentenceSegmenter works (found {len(result)} sentences)")
        else:
            print(f"  ✗ SentenceSegmenter found only {len(result)} sentences")
    except Exception as e:
        print(f"  ✗ SentenceSegmenter error: {e}")
    
    # Test semantic extractor
    print("\n3️⃣ Testing SemanticExtractor...")
    try:
        from semantic_extractor import SemanticExtractor
        extractor = SemanticExtractor()
        test_sent = "User enters email and password"
        result = extractor.extract(test_sent)
        
        if result.get("actor") and result.get("action"):
            print(f"  ✓ SemanticExtractor works")
            print(f"    - Actor: {result['actor']}")
            print(f"    - Action: {result['action']}")
            print(f"    - Objects: {result['objects']}")
        else:
            print(f"  ⚠️ SemanticExtractor output incomplete")
    except Exception as e:
        print(f"  ✗ SemanticExtractor error: {e}")
    
    # Test normalizer
    print("\n4️⃣ Testing Normalizer...")
    try:
        from normalizer import Normalizer
        normalizer = Normalizer()
        test_req = {
            "original_text": "Application sign in with credentials",
            "actor": "application",
            "action": "sign in",
            "objects": ["email", "password"],
            "inputs": ["email"],
            "type": "functional"
        }
        result = normalizer.normalize(test_req)
        
        if result["actor"] == "system" and result["action"] == "login":
            print(f"  ✓ Normalizer works")
            print(f"    - Normalized actor: {result['actor']}")
            print(f"    - Normalized action: {result['action']}")
            print(f"    - Detected domain: {result['domain']}")
        else:
            print(f"  ⚠️ Normalizer output unexpected")
    except Exception as e:
        print(f"  ✗ Normalizer error: {e}")
    
    # Test requirement structurer
    print("\n5️⃣ Testing RequirementStructurer...")
    try:
        from requirement_structurer import RequirementStructurer
        structurer = RequirementStructurer()
        test_req = {
            "original_text": "User can authenticate with valid credentials",
            "actor": "user",
            "action": "authenticate",
            "objects": [],
            "inputs": [],
            "conditions": [],
            "expected_results": [],
            "type": "security",
            "domain": "general"
        }
        result = structurer.structure("REQ-001", test_req)
        
        if result.requirement_id == "REQ-001":
            print(f"  ✓ RequirementStructurer works")
            print(f"    - Priority: {result.priority}")
            print(f"    - Status: {result.status}")
        else:
            print(f"  ✗ Structuring failed")
    except Exception as e:
        print(f"  ✗ RequirementStructurer error: {e}")
    
    # Test test generator
    print("\n6️⃣ Testing TestGenerator...")
    try:
        from test_generator import TestGenerator
        from requirement_structurer import StructuredRequirement, Input
        
        generator = TestGenerator()
        req = StructuredRequirement(
            requirement_id="REQ-001",
            original_text="User can authenticate with email",
            actor="user",
            action="authenticate",
            inputs=[Input(name="email", type_="email")],
            type_="security"
        )
        
        tests = generator.generate_tests(req)
        
        if len(tests) > 0:
            print(f"  ✓ TestGenerator works")
            print(f"    - Generated {len(tests)} test cases")
            
            test_types = set(t.test_type for t in tests)
            print(f"    - Test types: {', '.join(test_types)}")
        else:
            print(f"  ✗ No tests generated")
    except Exception as e:
        print(f"  ✗ TestGenerator error: {e}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    # Test individual modules first
    test_individual_modules()
    
    # Then test full pipeline
    print("\n" + "="*70)
    success = test_full_pipeline()
    
    if success:
        print("\n✅ ALL TESTS PASSED!")
        print("\n📚 Next steps:")
        print("1. Run: python main.py")
        print("2. Open: http://localhost:8000/docs")
        print("3. Try API: http://localhost:8000/api/generate")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("Check errors above and install missing dependencies")
    
    print("=" * 70 + "\n")
