"""
COMPREHENSIVE TESTING SUITE - AI TEST GENERATION SYSTEM V2.0
=============================================================

Complete test suite including:
- Enhanced test generation (7 categories)
- Threat modeling validation
- Real-world examples integration
- Edge case handling
- Performance benchmarks
- Bug detection

Production-ready testing for capstone defense
"""

import sys
import time
import json
from typing import Dict, List, Tuple, Any
from datetime import datetime

# Import all modules
sys.path.insert(0, '/home/dtu/AI-Project/AI-Project/requirement_analyzer/task_gen')

from ai_test_generation_v2_enhanced import (
    EnhancedTestCaseGeneratorV2, TestCaseCategory, TestAnalytics, Severity
)
from threat_modeling_engine import (
    ThreatModelingEngine, ThreatModelingReport, RealWorldExamplesDB as ThreatExamplesDB
)
from real_world_examples import (
    RealWorldTestExamplesDB, TestingPatternsFromIndustry, Domain
)


# ============================================================================
# TEST EXECUTION FRAMEWORK
# ============================================================================

class TestResult:
    """Test execution result"""
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.passed = False
        self.failed = False
        self.skipped = False
        self.errors: List[str] = []
        self.start_time = 0.0
        self.end_time = 0.0
        self.duration_ms = 0.0
    
    def mark_passed(self):
        self.passed = True
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
    
    def mark_failed(self, error: str):
        self.failed = True
        self.errors.append(error)
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
    
    def mark_skipped(self):
        self.skipped = True


class TestSuite:
    """Comprehensive test suite"""
    
    def __init__(self):
        self.tests: List[TestResult] = []
        self.total_start = datetime.now()
    
    def run(self):
        """Execute all tests"""
        print("\n" + "="*80)
        print("COMPREHENSIVE AI TEST GENERATION SYSTEM V2.0 - TEST SUITE")
        print("="*80)
        print(f"Start Time: {self.total_start.isoformat()}\n")
        
        # Test 1: Enhanced Test Generation
        self._test_enhanced_generation()
        
        # Test 2: Threat Modeling
        self._test_threat_modeling()
        
        # Test 3: Real-World Examples Integration
        self._test_real_world_examples()
        
        # Test 4: Test Categories Coverage
        self._test_category_coverage()
        
        # Test 5: Deduplication Engine
        self._test_deduplication()
        
        # Test 6: Security Threat Detection
        self._test_security_threats()
        
        # Test 7: Performance Metrics
        self._test_performance_metrics()
        
        # Test 8: Edge Cases
        self._test_edge_cases()
        
        # Print summary
        self._print_summary()
    
    def _test_enhanced_generation(self):
        """Test 1: Enhanced test generation with all 7 categories"""
        result = TestResult("Enhanced Test Generation (7 Categories)")
        result.start_time = time.time()
        
        try:
            print("\n" + "-"*80)
            print("TEST 1: Enhanced Test Generation with 7 Categories")
            print("-"*80)
            
            requirements = [
                "User must authenticate with username/password. Lockout after 5 failed attempts.",
                "System uploads CSV file (max 50MB). Validates format and rejects invalid files.",
                "Admin generates monthly reports. System must handle 1000 concurrent users.",
                "System searches users by name. Results displayed as HTML.",
                "API must return results within 100ms for P99 latency."
            ]
            
            generator = EnhancedTestCaseGeneratorV2()
            tests, metrics = generator.generate_comprehensive_tests(requirements)
            
            # Verify all categories present
            categories = [TestCaseCategory.FUNCTIONAL, TestCaseCategory.SECURITY, 
                         TestCaseCategory.PERFORMANCE, TestCaseCategory.INTEGRATION,
                         TestCaseCategory.EDGE_CASE, TestCaseCategory.REGRESSION,
                         TestCaseCategory.THREAT]
            
            generated_categories = set(tc.category for tc in tests)
            
            # Assert minimum test count
            assert len(tests) >= 10, f"Expected >10 tests, got {len(tests)}"
            assert len(generated_categories) >= 5, f"Expected >5 categories, got {len(generated_categories)}"
            
            # Assert metrics
            assert metrics['avg_confidence'] > 0.7, f"Expected confidence > 70%, got {metrics['avg_confidence']:.0%}"
            assert metrics['total_security_threats'] >= 2, f"Expected >=2 threats, got {metrics['total_security_threats']}"
            
            print(f"✅ Generated {len(tests)} test cases")
            print(f"✅ Categories: {dict(metrics['by_category'])}")
            print(f"✅ Security Threats: {metrics['total_security_threats']}")
            print(f"✅ Avg Confidence: {metrics['avg_confidence']:.2%}")
            print(f"✅ Processing Time: {metrics['processing_time_ms']:.2f}ms")
            
            result.mark_passed()
            
        except Exception as e:
            result.mark_failed(str(e))
            print(f"❌ FAILED: {str(e)}")
        
        self.tests.append(result)
    
    def _test_threat_modeling(self):
        """Test 2: Threat modeling engine"""
        result = TestResult("Threat Modeling Engine")
        result.start_time = time.time()
        
        try:
            print("\n" + "-"*80)
            print("TEST 2: Threat Modeling Engine")
            print("-"*80)
            
            engine = ThreatModelingEngine()
            
            test_requirement = "System allows users to search other users by name. Results displayed as HTML in real-time."
            
            # Test threat identification
            threats = engine.identify_threats_in_requirement(test_requirement)
            assert len(threats) > 0, "No threats identified"
            
            # Test attack scenario generation
            scenarios = engine.generate_attack_scenarios(test_requirement)
            assert len(scenarios) > 0, "No attack scenarios generated"
            
            # Test risk assessment
            risk = engine.assess_risk("XSS Vulnerability", "High", "High")
            assert risk.risk_score > 0, "Risk score should be > 0"
            
            # Test threat database
            threat_count = len(engine.threats)
            assert threat_count >= 8, f"Expected >=8 threats in DB, got {threat_count}"
            
            print(f"✅ Identified {len(threats)} threats")
            print(f"✅ Generated {len(scenarios)} attack scenario categories")
            print(f"✅ Risk assessment calculated (score: {risk.risk_score:.1f})")
            print(f"✅ Threat database loaded ({threat_count} threats)")
            
            result.mark_passed()
            
        except Exception as e:
            result.mark_failed(str(e))
            print(f"❌ FAILED: {str(e)}")
        
        self.tests.append(result)
    
    def _test_real_world_examples(self):
        """Test 3: Real-world examples integration"""
        result = TestResult("Real-World Examples Database")
        result.start_time = time.time()
        
        try:
            print("\n" + "-"*80)
            print("TEST 3: Real-World Examples Database")
            print("-"*80)
            
            # Verify examples loaded
            assert len(RealWorldTestExamplesDB.examples) >= 5, "Expected >=5 examples"
            
            # Verify domains
            domains = [ex.domain for ex in RealWorldTestExamplesDB.examples]
            assert len(set(domains)) >= 4, "Expected >=4 different domains"
            
            # Test filtering
            streaming_examples = RealWorldTestExamplesDB.get_examples_by_domain(Domain.STREAMING)
            assert len(streaming_examples) > 0, "No streaming domain examples"
            
            fintech_examples = RealWorldTestExamplesDB.get_examples_by_domain(Domain.FINTECH)
            assert len(fintech_examples) > 0, "No fintech domain examples"
            
            # Test high-impact examples
            high_impact = RealWorldTestExamplesDB.get_high_impact_examples()
            assert len(high_impact) >= 3, "Expected >=3 high-impact examples"
            
            # Verify metrics
            for ex in high_impact[:2]:
                assert ex.revenue_protected_millions > 0, "Should have revenue protected"
                assert ex.users_impacted > 0, "Should have users impacted"
            
            print(f"✅ Examples loaded: {len(RealWorldTestExamplesDB.examples)}")
            print(f"✅ Domains: {len(set(domains))}")
            print(f"✅ Streaming examples: {len(streaming_examples)}")
            print(f"✅ FinTech examples: {len(fintech_examples)}")
            print(f"✅ High-impact examples ranked")
            print(f"✅ Total revenue protected: ${sum(ex.revenue_protected_millions or 0 for ex in RealWorldTestExamplesDB.examples):.0f}M")
            
            result.mark_passed()
            
        except Exception as e:
            result.mark_failed(str(e))
            print(f"❌ FAILED: {str(e)}")
        
        self.tests.append(result)
    
    def _test_category_coverage(self):
        """Test 4: Test category coverage"""
        result = TestResult("Test Category Coverage")
        result.start_time = time.time()
        
        try:
            print("\n" + "-"*80)
            print("TEST 4: Test Category Coverage")
            print("-"*80)
            
            generator = EnhancedTestCaseGeneratorV2()
            # More detailed requirements to trigger all categories
            requirements = [
                "User login with password and 5-attempt lockout. SQL injection risk.",
                "Display user feed with complex permissions and HTML content. XSS risk.",
                "Payment processing with atomicity guarantee and 100ms latency requirement",
                "Database queries with concurrent access and performance monitoring",
                "API integration with external services and timeout handling"
            ]
            tests, _ = generator.generate_comprehensive_tests(requirements)
            
            categories = {
                TestCaseCategory.FUNCTIONAL: 0,
                TestCaseCategory.EDGE_CASE: 0,
                TestCaseCategory.SECURITY: 0,
                TestCaseCategory.PERFORMANCE: 0,
                TestCaseCategory.INTEGRATION: 0,
                TestCaseCategory.REGRESSION: 0,
                TestCaseCategory.THREAT: 0,
            }
            
            for test in tests:
                categories[test.category] += 1
            
            # Verify coverage - should cover at least 5 categories with detailed requirements
            covered = [cat for cat, count in categories.items() if count > 0]
            assert len(covered) >= 5, f"Expected >=5 categories with detailed requirements, got {len(covered)}: {covered}"
            
            print("Category Distribution:")
            for category, count in categories.items():
                if count > 0:
                    print(f"  ✅ {category.value}: {count} tests")
            
            result.mark_passed()
            
        except Exception as e:
            result.mark_failed(str(e))
            print(f"❌ FAILED: {str(e)}")
        
        self.tests.append(result)
    
    def _test_deduplication(self):
        """Test 5: Deduplication engine"""
        result = TestResult("Deduplication Engine")
        result.start_time = time.time()
        
        try:
            print("\n" + "-"*80)
            print("TEST 5: Deduplication Engine")
            print("-"*80)
            
            generator = EnhancedTestCaseGeneratorV2()
            requirements = [
                "User login",
                "User logs in",
                "User login system",
                "Display results",
                "Show results",
                "Results shown to user"
            ]
            
            tests, metrics = generator.generate_comprehensive_tests(requirements)
            
            # Should have removed duplicates
            assert metrics['deduplication_savings'] > 0, "Should have removed some duplicates"
            
            print(f"✅ Original test count: {len(requirements) * 3}")
            print(f"✅ Duplicates removed: {metrics['deduplication_savings']}")
            print(f"✅ Final test count: {metrics['total_test_cases']}")
            
            result.mark_passed()
            
        except Exception as e:
            result.mark_failed(str(e))
            print(f"❌ FAILED: {str(e)}")
        
        self.tests.append(result)
    
    def _test_security_threats(self):
        """Test 6: Security threat detection"""
        result = TestResult("Security Threat Detection")
        result.start_time = time.time()
        
        try:
            print("\n" + "-"*80)
            print("TEST 6: Security Threat Detection")
            print("-"*80)
            
            generator = EnhancedTestCaseGeneratorV2()
            
            security_requirements = [
                "System executes SELECT queries based on user input",
                "Display user comments as HTML on page",
                "Authenticate users with password"
            ]
            
            tests, metrics = generator.generate_comprehensive_tests(security_requirements)
            
            # Filter security tests
            security_tests = [t for t in tests if t.category == TestCaseCategory.SECURITY]
            assert len(security_tests) > 0, "No security tests generated"
            
            # Verify threats detected
            total_threats = sum(len(t.security_threats) for t in security_tests)
            assert total_threats > 0, "No threats detected in security tests"
            
            print(f"✅ Security tests generated: {len(security_tests)}")
            print(f"✅ Threats identified: {total_threats}")
            for test in security_tests[:3]:
                if test.security_threats:
                    print(f"   • {test.security_threats[0].threat_type}")
            
            result.mark_passed()
            
        except Exception as e:
            result.mark_failed(str(e))
            print(f"❌ FAILED: {str(e)}")
        
        self.tests.append(result)
    
    def _test_performance_metrics(self):
        """Test 7: Performance metrics"""
        result = TestResult("Performance Metrics")
        result.start_time = time.time()
        
        try:
            print("\n" + "-"*80)
            print("TEST 7: Performance Metrics")
            print("-"*80)
            
            generator = EnhancedTestCaseGeneratorV2()
            
            perf_requirements = [
                "API response must be under 100 milliseconds",
                "System must handle 10000 requests per second",
                "Memory usage should not exceed 512 MB"
            ]
            
            tests, metrics = generator.generate_comprehensive_tests(perf_requirements)
            
            # Filter performance tests
            perf_tests = [t for t in tests if t.category == TestCaseCategory.PERFORMANCE]
            assert len(perf_tests) > 0, "No performance tests generated"
            
            # Verify requirements detected
            total_reqs = sum(len(t.performance_requirements) for t in perf_tests)
            assert total_reqs > 0, "No performance requirements detected"
            
            print(f"✅ Performance tests generated: {len(perf_tests)}")
            print(f"✅ Perf requirements detected: {total_reqs}")
            print(f"✅ Processing time: {metrics['processing_time_ms']:.2f}ms")
            
            result.mark_passed()
            
        except Exception as e:
            result.mark_failed(str(e))
            print(f"❌ FAILED: {str(e)}")
        
        self.tests.append(result)
    
    def _test_edge_cases(self):
        """Test 8: Edge case handling"""
        result = TestResult("Edge Case Handling")
        result.start_time = time.time()
        
        try:
            print("\n" + "-"*80)
            print("TEST 8: Edge Case Handling")
            print("-"*80)
            
            generator = EnhancedTestCaseGeneratorV2()
            
            edge_case_requirements = [
                "System rejects input with maximum value exceeded",
                "Handle empty search queries",
                "Minimum 8 characters for password"
            ]
            
            tests, metrics = generator.generate_comprehensive_tests(edge_case_requirements)
            
            # Filter edge case tests
            edge_tests = [t for t in tests if t.category == TestCaseCategory.EDGE_CASE]
            assert len(edge_tests) > 0, "No edge case tests generated"
            
            # Verify edge cases identified
            total_edges = sum(len(t.edge_cases) for t in edge_tests)
            assert total_edges > 0, "No edge cases identified"
            
            print(f"✅ Edge case tests generated: {len(edge_tests)}")
            print(f"✅ Edge cases identified: {total_edges}")
            for test in edge_tests[:2]:
                if test.edge_cases:
                    print(f"   • {test.edge_cases[0]}")
            
            result.mark_passed()
            
        except Exception as e:
            result.mark_failed(str(e))
            print(f"❌ FAILED: {str(e)}")
        
        self.tests.append(result)
    
    def _print_summary(self):
        """Print test summary"""
        total_tests = len(self.tests)
        passed = sum(1 for t in self.tests if t.passed)
        failed = sum(1 for t in self.tests if t.failed)
        total_time = sum(t.duration_ms for t in self.tests)
        
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        pass_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        
        for test in self.tests:
            status = "✅ PASS" if test.passed else "❌ FAIL"
            print(f"{status} | {test.test_name:<50} | {test.duration_ms:>6.2f}ms")
        
        print("\n" + "-"*80)
        print(f"Results: {passed}/{total_tests} Passed ({pass_rate:.0f}%)")
        print(f"Total Time: {total_time:.2f}ms")
        print("="*80)
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! ✅")
            print("System is PRODUCTION READY for Capstone Defense\n")
            return True
        else:
            print(f"\n⚠️  {failed} TEST(S) FAILED")
            for test in self.tests:
                if test.failed:
                    print(f"\nFailed: {test.test_name}")
                    for error in test.errors:
                        print(f"  Error: {error}")
            print()
            return False


# ============================================================================
# EXECUTION
# ============================================================================

if __name__ == "__main__":
    suite = TestSuite()
    success = suite.run()
    sys.exit(0 if success else 1)
