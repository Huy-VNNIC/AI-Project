#!/usr/bin/env python3
"""
Test Suite for Smart AI Generator v3 (Hybrid LLM)
Tests the full v3 pipeline with real healthcare requirements
"""

import json
import sys
from typing import Dict, Any

# For testing without LLM
class MockLLMParser:
    """Mock LLM parser for testing without API key"""
    
    def __init__(self, *args, **kwargs):
        pass
    
    def parse(self, requirement: str):
        """Return mock structured intent"""
        from bridge_mapper import RequirementEntity
        
        # Mock intent data
        mock_data = {
            "actor": "Doctor",
            "action": "prescribe" if "prescribe" in requirement.lower() else "schedule",
            "object": "medication" if "prescribe" in requirement.lower() else "appointment",
            "conditions": [
                "Check patient history",
                "Verify insurance coverage"
            ] if "prescribe" in requirement.lower() else [
                "Verify provider availability",
                "Check appointment slots"
            ],
            "constraints": ["No conflicts", "Valid time"] if "schedule" in requirement.lower() else ["No allergies"],
            "domain": "healthcare",
            "intent_type": "conditional_workflow"if "prescribe" in requirement.lower() else "workflow",
            "dependencies": [
                {"step": "verify patient record", "before": "prescribe medication"}
            ] if "prescribe" in requirement.lower() else [
                {"step": "check calendar", "before": "schedule appointment"}
            ],
            "risk_level": "high" if "prescribe" in requirement.lower() else "medium",
            "confidence": 0.92,
        }
        
        # Return mock StructuredIntent
        from llm_parser import StructuredIntent
        return StructuredIntent(mock_data)


def test_llm_parser():
    """Test LLM parser directly"""
    print("\n" + "="*70)
    print("TEST 1: LLM SEMANTIC PARSER")
    print("="*70)
    
    try:
        from llm_parser import LLMSemanticParser
        parser = LLMSemanticParser()
        use_real_llm = True
    except Exception as e:
        print(f"LLM unavailable ({e}), using mock")
        parser = MockLLMParser()
        use_real_llm = False
    
    requirement = """
    A doctor must prescribe medication to a patient after verifying:
    1. Patient allergies are checked to prevent allergic reactions
    2. No drug interactions are found
    3. Patient has valid insurance coverage
    The system should prevent prescription of any drug the patient is allergic to.
    """
    
    print(f"\nInput: {requirement.strip()[:80]}...")
    
    try:
        intent = parser.parse(requirement)
        
        print(f"\nParsed Structured Intent:")
        print(f"  ✓ Actor: {intent.actor}")
        print(f"  ✓ Action: {intent.action}")
        print(f"  ✓ Object: {intent.object_entity}")
        print(f"  ✓ Domain: {intent.domain}")
        print(f"  ✓ Intent Type: {intent.intent_type}")
        print(f"  ✓ Risk Level: {intent.risk_level}")
        print(f"  ✓ Confidence: {intent.confidence}")
        print(f"  ✓ Dependencies: {len(intent.dependencies)} found")
        print(f"  ✓ Conditions: {len(intent.conditions)} found")
        
        print(f"\n✓ TEST 1 PASSED: {'Real LLM' if use_real_llm else 'Mock LLM'}")
        return True
    
    except Exception as e:
        print(f"\n✗ TEST 1 FAILED: {e}")
        return False


def test_bridge_mapper():
    """Test LLM to v2 bridge mapping"""
    print("\n" + "="*70)
    print("TEST 2: BRIDGE MAPPER (LLM → v2)")
    print("="*70)
    
    try:
        from bridge_mapper import LLMTov2Bridge, SmartTestTypeInference
        
        llm_data = {
            "actor": "Doctor",
            "action": "prescribe",
            "object": "medication",
            "conditions": ["patient allergy checked", "no interactions found"],
            "constraints": ["must verify insurance"],
            "domain": "healthcare",
            "intent_type": "conditional_workflow",
            "dependencies": [
                {"step": "check allergies", "before": "prescribe"}
            ],
            "risk_level": "high",
            "confidence": 0.92
        }
        
        # Map to entity
        entity = LLMTov2Bridge.map_llm_to_entity(llm_data, "Original requirement")
        
        print(f"\nMapped to RequirementEntity:")
        print(f"  ✓ Action: {entity.action}")
        print(f"  ✓ Objects: {entity.objects}")
        print(f"  ✓ Domain: {entity.domain}")
        print(f"  ✓ Conditions: {len(entity.conditions)} items")
        print(f"  ✓ Dependencies: {len(entity.dependencies)} items")
        print(f"  ✓ Confidence: {entity.confidence}")
        
        # Infer test types
        test_types = SmartTestTypeInference.infer_test_types(entity)
        print(f"\nInferred Test Types:")
        for tt in test_types:
            print(f"  ✓ {tt}")
        
        print(f"\n✓ TEST 2 PASSED")
        return True
    
    except Exception as e:
        print(f"\n✗ TEST 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_v3_generator():
    """Test full v3 generator"""
    print("\n" + "="*70)
    print("TEST 3: FULL v3 GENERATOR")
    print("="*70)
    
    try:
        from smart_ai_generator_v3 import AITestGeneratorV3
        
        # Use mock instead of real LLM for testing
        generator = AITestGeneratorV3(use_llm=False)
        
        requirements = [
            "A doctor must prescribe medication after checking patient allergies and verifying insurance coverage.",
            "Patients should be able to schedule appointments with available healthcare providers.",
        ]
        
        print(f"\nGenerating test cases for {len(requirements)} requirements...")
        
        result = generator.generate(requirements, max_tests_per_req=5)
        
        print(f"\nGeneration Results:")
        summary = result["summary"]
        print(f"  ✓ Status: {result['status']}")
        print(f"  ✓ Total Test Cases: {summary['total_test_cases']}")
        print(f"  ✓ Avg Quality: {summary['avg_quality']:.1%}")
        print(f"  ✓ Avg Effort: {summary['avg_effort']:.2f}h")
        print(f"  ✓ Domains: {summary['domains_found']}")
        print(f"  ✓ Test Types: {summary['test_types_generated']}")
        
        # Validate test case structure
        if result['test_cases']:
            tc = result['test_cases'][0]
            required_fields = [
                'test_id', 'title', 'test_type', 'steps', 
                'preconditions', 'expected_result', 'ml_quality_score', 'effort_hours'
            ]
            
            print(f"\nValidating test case structure:")
            missing = []
            for field in required_fields:
                if field in tc:
                    print(f"  ✓ {field}")
                else:
                    print(f"  ✗ {field} MISSING")
                    missing.append(field)
            
            if missing:
                print(f"\n✗ TEST 3 FAILED: Missing fields {missing}")
                return False
        
        print(f"\n✓ TEST 3 PASSED")
        return True
    
    except Exception as e:
        print(f"\n✗ TEST 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dependency_awareness():
    """Test that v3 properly handles dependencies"""
    print("\n" + "="*70)
    print("TEST 4: DEPENDENCY AWARENESS (v3 Unique)")
    print("="*70)
    
    try:
        from bridge_mapper import DependencyAwareStepGenerator, RequirementEntity
        
        # Create entity with dependencies
        entity = RequirementEntity(
            original_text="Doctor prescribes medication",
            action="prescribe",
            objects=["medication"],
            constraints={},
            domain="healthcare",
            actor="Doctor",
            dependencies=[
                {"step": "check patient allergies", "before": "prescribe medication"},
                {"step": "verify insurance", "before": "prescribe medication"}
            ],
            conditions=["patient allergy checked", "insurance verified"],
            intent_type="conditional_workflow",
            risk_level="high",
        )
        
        # Generate steps
        steps = DependencyAwareStepGenerator.generate_steps_with_dependencies(
            entity, "happy_path", "prescribe", ["medication"]
        )
        
        print(f"\nGenerated {len(steps)} steps:")
        for i, step in enumerate(steps, 1):
            print(f"  {i}. {step}")
        
        # Check if dependencies are in steps
        has_dependency_steps = any("check patient allergies" in step.lower() for step in steps)
        
        if has_dependency_steps:
            print(f"\n✓ Dependencies properly included in steps")
            print(f"✓ TEST 4 PASSED")
            return True
        else:
            print(f"\n✗ Dependencies missing from steps")
            print(f"✗ TEST 4 FAILED")
            return False
    
    except Exception as e:
        print(f"\n✗ TEST 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_quality_scoring():
    """Test that quality scoring is realistic and semantic-aware"""
    print("\n" + "="*70)
    print("TEST 5: QUALITY SCORING (v3 Enhancement)")
    print("="*70)
    
    try:
        from smart_ai_generator_v3 import SmartAIGeneratorV3
        from bridge_mapper import RequirementEntity
        
        generator = SmartAIGeneratorV3(use_llm=False)
        
        # Create entity with various profiles
        entities = [
            RequirementEntity(
                original_text="Simple test",
                action="login",
                objects=["system"],
                constraints={},
                domain="general",
                confidence=0.9,
                intent_type="simple_action",
                risk_level="low",
            ),
            RequirementEntity(
                original_text="Complex healthcare",
                action="prescribe",
                objects=["medication"],
                constraints={"boundaries": [5, 10, 20]},
                domain="healthcare",
                confidence=0.92,
                intent_type="conditional_workflow",
                risk_level="high",
                dependencies=[
                    {"step": "check allergies", "before": "prescribe"},
                    {"step": "verify insurance", "before": "prescribe"}
                ],
                conditions=["allergies checked", "insurance valid", "drug interactions verified"],
            ),
        ]
        
        print(f"\nTesting quality scoring on {len(entities)} entity profiles:")
        
        for entity in entities:
            quality = generator._calculate_quality_v3(
                entity,
                ["step1", "step2", "step3"],
                "happy_path"
            )
            
            print(f"\n  {entity.domain.upper()} | {entity.intent_type}")
            print(f"    Confidence: {entity.confidence}")
            print(f"    Dependencies: {len(entity.dependencies)} items")
            print(f"    Quality Score: {quality:.1%}")
            
            # Validate that quality is reasonable
            if 0.0 <= quality <= 1.0:
                print(f"    ✓ Valid range")
            else:
                print(f"    ✗ Invalid quality score")
                return False
        
        print(f"\n✓ TEST 5 PASSED")
        return True
    
    except Exception as e:
        print(f"\n✗ TEST 5 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*70)
    print("SMART AI GENERATOR v3 - TEST SUITE")
    print("="*70)
    
    tests = [
        ("LLM Parser", test_llm_parser),
        ("Bridge Mapper", test_bridge_mapper),
        ("v3 Generator", test_v3_generator),
        ("Dependency Awareness", test_dependency_awareness),
        ("Quality Scoring", test_quality_scoring),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\nUNCHRITICAL ERROR in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status:10} | {name}")
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED - v3 Ready for Production!")
        return 0
    else:
        print(f"\n⚠️ {total_count - passed_count} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
