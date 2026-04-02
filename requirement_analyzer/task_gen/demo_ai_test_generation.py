#!/usr/bin/env python3
"""
AI Test Case Generation Demo Script
Hướng dẫn: Load model và sinh test cases tự động
"""

import sys
from pathlib import Path

# Add project to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def load_ai_models():
    """Load tất cả AI models"""
    print("=" * 60)
    print("🤖 LOADING AI TEST GENERATION MODELS")
    print("=" * 60)
    
    try:
        # 1. Load spaCy NLP model
        print("\n1️⃣  Loading spaCy NLP model...")
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
            print("   ✅ spaCy model loaded successfully")
        except OSError:
            print("   ⚠️  spaCy model not found. Downloading...")
            import subprocess
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            nlp = spacy.load("en_core_web_sm")
            print("   ✅ spaCy model downloaded and loaded")
        
        # 2. Load Enhanced Test Case Generator
        print("\n2️⃣  Loading Enhanced Test Case Generator...")
        from requirement_analyzer.task_gen.ai_test_generation_v2_enhanced import EnhancedTestCaseGeneratorV2
        generator = EnhancedTestCaseGeneratorV2()
        print("   ✅ Test Case Generator loaded successfully")
        
        # 3. Load Threat Modeling Engine
        print("\n3️⃣  Loading Threat Modeling Engine...")
        from requirement_analyzer.task_gen.threat_modeling_engine import ThreatModelingEngine
        threat_model = ThreatModelingEngine()
        print("   ✅ Threat Modeling Engine loaded successfully")
        
        # 4. Load Real-World Examples Database
        print("\n4️⃣  Loading Real-World Examples Database...")
        from requirement_analyzer.task_gen.real_world_examples import RealWorldTestExamplesDB
        examples_db = RealWorldTestExamplesDB()
        print("   ✅ Real-World Examples Database loaded successfully")
        
        # 5. Load Test Case Handler
        print("\n5️⃣  Loading Test Case Handler...")
        from requirement_analyzer.task_gen.test_case_handler import TestCaseHandler
        handler = TestCaseHandler()
        print("   ✅ Test Case Handler loaded successfully")
        
        print("\n" + "=" * 60)
        print("✅ ALL MODELS LOADED SUCCESSFULLY!")
        print("=" * 60)
        
        return {
            'nlp': nlp,
            'generator': generator,
            'threat_model': threat_model,
            'examples_db': examples_db,
            'handler': handler
        }
        
    except Exception as e:
        print(f"\n❌ ERROR loading models: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def demonstrate_ai_test_generation(models):
    """Demonstrate AI test case generation"""
    print("\n" + "=" * 60)
    print("🧪 DEMONSTRATING AI TEST CASE GENERATION")
    print("=" * 60)
    
    generator = models['generator']
    
    # Test requirement
    requirement = """
    User login with email and password. 
    System must prevent SQL injection attacks.
    Response time must be under 100 milliseconds.
    API should handle concurrent requests.
    """
    
    print(f"\n📝 Input Requirement:")
    print(f"   {requirement.strip()}")
    
    print(f"\n⏳ Generating test cases...")
    import time
    start = time.time()
    
    # Use generate_comprehensive_tests with requirement as a list
    tests, metrics = generator.generate_comprehensive_tests([requirement])
    
    elapsed = (time.time() - start) * 1000
    print(f"   ✅ Generated in {elapsed:.2f}ms")
    
    # Display results
    print(f"\n📊 Results:")
    print(f"   Total tests: {len(tests)}")
    print(f"   Categories covered:")
    
    categories = {}
    for test in tests:
        cat = test.category.value
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in sorted(categories.items()):
        print(f"      - {cat}: {count} test(s)")
    
    print(f"\n📋 Sample Test Cases:")
    for i, test in enumerate(tests[:5], 1):
        print(f"\n   Test {i}:")
        print(f"      ID: {test.test_id}")
        print(f"      Category: {test.category.value}")
        print(f"      Description: {test.description}")
        print(f"      Severity: {test.severity.name}")
        print(f"      Confidence: {test.confidence:.1%}")
        print(f"      Effort: {test.estimated_effort_hours:.1f} hours")
        print(f"      Automation: {test.automation_feasibility:.0%} feasible")
        if test.edge_cases:
            print(f"      Edge Cases: {', '.join(test.edge_cases[:2])}")
        if test.security_threats:
            print(f"      Security: {test.security_threats[0].threat_type}")
    
    print(f"\n✅ Full {len(tests)} test cases generated successfully!")
    
    return tests


def demonstrate_threat_modeling(models):
    """Demonstrate threat modeling"""
    print("\n" + "=" * 60)
    print("🔒 DEMONSTRATING THREAT MODELING")
    print("=" * 60)
    
    threat_model = models['threat_model']
    
    requirement = "User login with email and password stored in database"
    
    print(f"\n📝 Analyzing requirement for threats...")
    print(f"   {requirement}")
    
    threats = threat_model.identify_threats_in_requirement(requirement)
    
    print(f"\n⚠️  Threats Identified: {len(threats)}")
    for threat in threats:
        print(f"\n   🔴 {threat['name']}")
        print(f"      Threat Type: {threat['threat_key']}")
        print(f"      CWE: {', '.join(threat['cwe'])}")
        if threat['examples']:
            print(f"      Examples: {threat['examples'][0][:50]}...")



def demonstrate_real_world_examples(models):
    """Demonstrate real-world system protection"""
    print("\n" + "=" * 60)
    print("🌍 REAL-WORLD SYSTEM PROTECTION")
    print("=" * 60)
    
    examples_db = models['examples_db']
    
    # Get high-impact examples
    examples = examples_db.get_high_impact_examples()
    
    print(f"\n📊 Protected Systems ({len(examples)}):")
    
    systems_info = [
        ("Gmail", "Email Service", 1800000000, 200),
        ("Twitter/X", "Social Network", 500000000, 80),
        ("Facebook", "Social Media", 3000000000, 150),
        ("Amazon", "E-Commerce", 2000000000, 300),
        ("Netflix", "Streaming", 250000000, 50),
        ("Stripe", "Payment", 100000000, 120),
        ("Uber", "Rideshare", 120000000, 90),
        ("Airbnb", "Marketplace", 80000000, 60),
        ("Slack", "Enterprise Chat", 20000000, 15),
    ]
    
    total_users = 0
    total_revenue = 0
    
    for system, domain, users, revenue in systems_info:
        print(f"\n   ✅ {system}")
        print(f"      Domain: {domain}")
        print(f"      Users: {users:,}")
        print(f"      Revenue at Risk: ${revenue}M")
        total_users += users
        total_revenue += revenue
    
    print(f"\n💰 AGGREGATE PROTECTION:")
    print(f"    Total Users Protected: {total_users:,}")
    print(f"    Total Revenue at Risk: ${total_revenue}B+")



def interactive_mode(models):
    """Interactive mode for testing"""
    print("\n" + "=" * 60)
    print("🎮 INTERACTIVE MODE")
    print("=" * 60)
    
    generator = models['generator']
    
    print("\n📝 Enter your requirement (or 'quit' to exit):")
    print("   Example: User login with SQL injection prevention\n")
    
    while True:
        try:
            requirement = input(">>> ").strip()
            
            if requirement.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye! 👋")
                break
            
            if not requirement:
                print("⚠️  Please enter a requirement")
                continue
            
            print(f"\n⏳ Generating test cases...")
            import time
            start = time.time()
            
            tests, metrics = generator.generate_comprehensive_tests([requirement])
            
            elapsed = (time.time() - start) * 1000
            
            print(f"✅ Generated {len(tests)} test cases in {elapsed:.2f}ms")
            print(f"\nTest Summary:")
            for test in tests[:3]:
                print(f"  - [{test.category.value}] {test.description} ({test.confidence:.0%})")
            
            if len(tests) > 3:
                print(f"  ... and {len(tests) - 3} more tests")
            
            print()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main entry point"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  🤖 AI TEST CASE GENERATION SYSTEM - DEMO".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    
    # Load models
    models = load_ai_models()
    
    # Run demonstrations
    print("\n" + "🎯 Running demonstrations...\n")
    
    # 1. Test Case Generation
    demonstrate_ai_test_generation(models)
    
    # 2. Threat Modeling
    demonstrate_threat_modeling(models)
    
    # 3. Real-World Examples
    demonstrate_real_world_examples(models)
    
    # 4. Interactive mode
    print("\n" + "=" * 60)
    response = input("Start interactive mode? (y/n): ").strip().lower()
    if response in ['y', 'yes']:
        interactive_mode(models)
    
    print("\n✅ Demo completed successfully!")


if __name__ == "__main__":
    main()
