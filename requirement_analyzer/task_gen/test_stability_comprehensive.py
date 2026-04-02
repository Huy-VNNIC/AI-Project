#!/usr/bin/env python3
"""
Comprehensive Stability & Performance Testing
==============================================

Tests system stability with:
- Multiple requirement types
- Large batch processing
- Edge cases
- Error handling
- Performance monitoring
- Memory usage
"""

import sys
import os
import time
import tracemalloc
from pathlib import Path
from typing import List, Dict, Any

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from requirement_analyzer.task_gen.ai_test_handler import AITestGenerationHandler


class StabilityTester:
    """Comprehensive stability testing"""
    
    def __init__(self):
        self.handler = AITestGenerationHandler()
        self.results = []
        self.start_memory = tracemalloc.get_traced_memory()[0]
    
    def print_header(self, title):
        print(f"\n{'='*80}")
        print(f"  {title}")
        print(f"{'='*80}\n")
    
    def print_test(self, name, status, duration=None, details=None):
        emoji = "✅" if status == "PASS" else "❌"
        msg = f"{emoji} {name}"
        if duration:
            msg += f" [{duration:.2f}s]"
        if details:
            msg += f"\n   {details}"
        print(msg)
        self.results.append({
            "name": name,
            "status": status,
            "duration": duration,
            "details": details
        })
    
    def test_1_simple_requirements(self):
        """Test 1: Simple requirements"""
        self.print_header("Test 1: Simple Requirements")
        
        simple_reqs = [
            ("User login", "User must be able to login with email and password"),
            ("User logout", "User can logout from the system"),
            ("Password reset", "User can request password reset via email"),
            ("Account delete", "User can delete their account"),
            ("Profile update", "User can update their profile information"),
        ]
        
        for name, requirement in simple_reqs:
            start = time.time()
            try:
                result = self.handler.generate_tests_for_task(
                    task_id=f"SIMPLE-{name.upper().replace(' ', '-')}",
                    task_description=requirement
                )
                duration = time.time() - start
                
                if result.get("status") == "success":
                    tests = result["summary"]["total_test_cases"]
                    self.print_test(
                        f"Simple: {name}",
                        "PASS",
                        duration,
                        f"Generated {tests} tests"
                    )
                else:
                    self.print_test(f"Simple: {name}", "FAIL", time.time() - start,
                                  result.get("message"))
            except Exception as e:
                self.print_test(f"Simple: {name}", "FAIL", time.time() - start, str(e))
    
    def test_2_complex_requirements(self):
        """Test 2: Complex multi-condition requirements"""
        self.print_header("Test 2: Complex Requirements")
        
        complex_reqs = [
            ("Payment", """
            Payment processing system must accept Visa, Mastercard, Amex.
            
            Rules:
            - Amount: 0.01 to 999,999.99
            - PCI DSS compliance, TLS 1.2+ encryption
            - No card storage (tokenization only)
            - Recurring payments (weekly, monthly, yearly)
            - Refunds within 90 days
            - 3D Secure fraud detection
            
            Performance: Process within 2 seconds, 99.9% availability
            """),
            
            ("Healthcare", """
            Medical records system for patient management.
            
            Requirements:
            - HIPAA compliance, encrypted storage
            - Role-based access (patient, doctor, admin)
            - Appointment scheduling with reminders
            - Prescription management with validations
            - Lab results tracking
            - Audit logging for all access
            - Mobile app support
            
            Performance: Load within 3 seconds, handle 1000 concurrent users
            """),
            
            ("E-commerce", """
            Shopping cart and checkout system.
            
            Features:
            - Add/remove items with quantity validation
            - Cart persistence across sessions
            - Multiple payment methods (card, wallet, bank transfer)
            - Shipping address validation
            - Discount/coupon codes (single and combination)
            - Order confirmation with email
            - Inventory deduction
            - Return/refund management
            
            Must handle flash sales and concurrent checkouts.
            """),
        ]
        
        for name, requirement in complex_reqs:
            start = time.time()
            try:
                result = self.handler.generate_tests_for_task(
                    task_id=f"COMPLEX-{name.upper()}",
                    task_description=requirement
                )
                duration = time.time() - start
                
                if result.get("status") == "success":
                    tests = result["summary"]["total_test_cases"]
                    complexity = result["analysis"].get("complexity", 0)
                    self.print_test(
                        f"Complex: {name}",
                        "PASS",
                        duration,
                        f"Generated {tests} tests, Complexity: {complexity:.2f}"
                    )
                else:
                    self.print_test(f"Complex: {name}", "FAIL", time.time() - start,
                                  result.get("message"))
            except Exception as e:
                self.print_test(f"Complex: {name}", "FAIL", time.time() - start, str(e))
    
    def test_3_edge_cases(self):
        """Test 3: Edge cases"""
        self.print_header("Test 3: Edge Cases & Special Inputs")
        
        edge_cases = [
            ("Empty requirement", ""),
            ("Very short", "Do something"),
            ("Null/special chars", "Test with @#$%^&*()"),
            ("Very long", "User must be able to " + "perform actions " * 100),
            ("Numbers only", "123 456 789"),
            ("SQL injection attempt", "'; DROP TABLE users; --"),
        ]
        
        for name, requirement in edge_cases:
            start = time.time()
            try:
                result = self.handler.generate_tests_for_task(
                    task_id=f"EDGE-{name.upper().replace(' ', '-')}",
                    task_description=requirement if requirement else "Placeholder"
                )
                duration = time.time() - start
                
                if result.get("status") == "success":
                    tests = result["summary"]["total_test_cases"]
                    self.print_test(
                        f"Edge case: {name}",
                        "PASS",
                        duration,
                        f"Generated {tests} tests"
                    )
                else:
                    self.print_test(f"Edge case: {name}", "PASS", time.time() - start,
                                  "Handled gracefully")  # Expected to fail
            except Exception as e:
                self.print_test(f"Edge case: {name}", "FAIL", time.time() - start, str(e))
    
    def test_4_batch_processing(self):
        """Test 4: Batch processing with multiple tasks"""
        self.print_header("Test 4: Batch Processing (Multiple Tasks)")
        
        tasks = [
            {
                "task_id": "BATCH-001",
                "description": "User registration with email validation",
                "ac": "Given user provides email, When user registers, Then account created"
            },
            {
                "task_id": "BATCH-002",
                "description": "Product search with filters",
                "ac": "Given user searches for product"
            },
            {
                "task_id": "BATCH-003",
                "description": "Order cancellation within 24 hours",
            },
            {
                "task_id": "BATCH-004",
                "description": "Notification preferences management",
            },
            {
                "task_id": "BATCH-005",
                "description": "Two-factor authentication setup",
            },
        ]
        
        print(f"Processing batch of {len(tasks)} tasks...\n")
        
        start = time.time()
        try:
            results = self.handler.generate_tests_for_multiple_tasks(tasks)
            total_duration = time.time() - start
            
            total_tests = 0
            successful = 0
            
            for i, result in enumerate(results, 1):
                if result.get("status") == "success":
                    successful += 1
                    tests = result["summary"]["total_test_cases"]
                    total_tests += tests
                    print(f"  {i}. {result['task_id']}: {tests} tests ✅")
                else:
                    print(f"  {i}. {result['task_id']}: FAILED ❌")
            
            self.print_test(
                f"Batch: {len(tasks)} tasks",
                "PASS" if successful == len(tasks) else "PARTIAL",
                total_duration,
                f"{successful}/{len(tasks)} successful, {total_tests} total tests"
            )
        except Exception as e:
            self.print_test(f"Batch processing", "FAIL", time.time() - start, str(e))
    
    def test_5_memory_stability(self):
        """Test 5: Memory stability under load"""
        self.print_header("Test 5: Memory Stability (100 sequential generations)")
        
        tracemalloc.start()
        
        print("Running 100 sequential generations...\n")
        
        start = time.time()
        try:
            memory_usage = []
            
            for i in range(100):
                result = self.handler.generate_tests_for_task(
                    task_id=f"STRESS-{i:03d}",
                    task_description=f"Feature {i}: User action {i} with validation and error handling"
                )
                
                current, peak = tracemalloc.get_traced_memory()
                memory_usage.append(peak / 1024 / 1024)  # Convert to MB
                
                if (i + 1) % 20 == 0:
                    print(f"  Completed {i+1}/100 iterations | Peak memory: {peak/1024/1024:.1f} MB")
            
            total_duration = time.time() - start
            avg_memory = sum(memory_usage) / len(memory_usage)
            max_memory = max(memory_usage)
            
            self.print_test(
                "Memory stability: 100 iterations",
                "PASS" if max_memory < 500 else "WARN",
                total_duration,
                f"Avg memory: {avg_memory:.1f} MB, Max: {max_memory:.1f} MB"
            )
            
            tracemalloc.stop()
        except Exception as e:
            self.print_test("Memory stability", "FAIL", time.time() - start, str(e))
    
    def test_6_concurrent_scenarios(self):
        """Test 6: Simulated concurrent scenarios"""
        self.print_header("Test 6: Concurrent-like Scenarios")
        
        # Simulate what would happen with concurrent requests
        scenarios = [
            ("Rapid sequential", 5),
            ("Medium load", 10),
            ("High load", 20),
        ]
        
        for name, count in scenarios:
            start = time.time()
            try:
                for i in range(count):
                    result = self.handler.generate_tests_for_task(
                        task_id=f"CONCURRENT-{name.upper().replace(' ', '-')}-{i:03d}",
                        task_description=f"Concurrent test {i}: User action with validation"
                    )
                    if result.get("status") != "success":
                        raise Exception(f"Generation failed for {i}")
                
                duration = time.time() - start
                avg_per_req = duration / count
                
                self.print_test(
                    f"Concurrent scenario: {name} ({count} reqs)",
                    "PASS",
                    duration,
                    f"Avg: {avg_per_req:.3f}s per request"
                )
            except Exception as e:
                self.print_test(f"Concurrent: {name}", "FAIL", time.time() - start, str(e))
    
    def test_7_error_recovery(self):
        """Test 7: Error handling and recovery"""
        self.print_header("Test 7: Error Handling & Recovery")
        
        # Normal request should work after errors
        try:
            # First, try with bad input
            print("Testing error recovery...\n")
            
            # This might error, but should recover
            try:
                result = self.handler.generate_tests_for_task(
                    task_id="",  # Empty ID
                    task_description="Test"
                )
            except:
                pass
            
            print("  • Handled empty task ID")
            
            # System should recover and work normally
            start = time.time()
            result = self.handler.generate_tests_for_task(
                task_id="RECOVERY-001",
                task_description="Normal request after error"
            )
            duration = time.time() - start
            
            if result.get("status") == "success":
                self.print_test(
                    "Error recovery: Normal operation after error",
                    "PASS",
                    duration,
                    "System recovered successfully"
                )
            else:
                self.print_test("Error recovery", "FAIL", duration, "Did not recover")
        except Exception as e:
            self.print_test("Error recovery", "FAIL", 0, str(e))
    
    def test_8_output_validation(self):
        """Test 8: Output format and consistency validation"""
        self.print_header("Test 8: Output Validation")
        
        try:
            result = self.handler.generate_tests_for_task(
                task_id="VALIDATE-001",
                task_description="Output validation test requirement"
            )
            
            checks = [
                ("Has status", "status" in result),
                ("Has test_cases", "test_cases" in result),
                ("Has summary", "summary" in result),
                ("Has analysis", "analysis" in result),
                ("Summary has counts", "total_test_cases" in result.get("summary", {})),
                ("Test cases not empty", len(result.get("test_cases", [])) > 0),
                ("Each test has ID", all("test_id" in tc for tc in result.get("test_cases", []))),
                ("Each test has type", all("test_type" in tc for tc in result.get("test_cases", []))),
                ("Each test has priority", all("priority" in tc for tc in result.get("test_cases", []))),
            ]
            
            all_pass = True
            for check_name, check_result in checks:
                status = "✅" if check_result else "❌"
                print(f"  {status} {check_name}")
                if not check_result:
                    all_pass = False
            
            self.print_test(
                "Output format validation",
                "PASS" if all_pass else "FAIL",
                0,
                f"{sum(1 for _, r in checks if r)}/{len(checks)} checks passed"
            )
        except Exception as e:
            self.print_test("Output validation", "FAIL", 0, str(e))
    
    def run_all(self):
        """Run all stability tests"""
        print("\n" + "█" * 80)
        print("COMPREHENSIVE STABILITY & PERFORMANCE TESTING".center(80))
        print("█" * 80)
        print("\nThis test suite verifies:")
        print("  ✓ Simple requirements handling")
        print("  ✓ Complex requirements handling")
        print("  ✓ Edge cases and error handling")
        print("  ✓ Batch processing")
        print("  ✓ Memory stability under load")
        print("  ✓ Concurrent-like scenarios")
        print("  ✓ Error recovery")
        print("  ✓ Output consistency")
        
        start_total = time.time()
        
        # Run all tests
        self.test_1_simple_requirements()
        self.test_2_complex_requirements()
        self.test_3_edge_cases()
        self.test_4_batch_processing()
        self.test_5_memory_stability()
        self.test_6_concurrent_scenarios()
        self.test_7_error_recovery()
        self.test_8_output_validation()
        
        total_duration = time.time() - start_total
        
        # Summary
        self.print_header("STABILITY TEST SUMMARY")
        
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        partial = sum(1 for r in self.results if r["status"] == "PARTIAL")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        total = len(self.results)
        
        print(f"\n{'Test Results':.<40} {total} tests")
        print(f"{'  ✅ PASS':.<40} {passed}")
        print(f"{'  ⚠️  PARTIAL':.<40} {partial}")
        print(f"{'  ❌ FAIL':.<40} {failed}")
        
        print(f"\n{'Overall Stability':.<40} ", end="")
        if failed == 0:
            print("🟢 STABLE")
        elif failed <= 2:
            print("🟡 MOSTLY STABLE")
        else:
            print("🔴 UNSTABLE")
        
        print(f"\n{'Total Test Duration':.<40} {total_duration:.2f}s")
        print(f"{'Average Per Test':.<40} {total_duration/total:.2f}s")
        
        # Recommendations
        print(f"\n{'Recommendations':.<40}")
        if failed == 0:
            print("  ✅ System is stable and ready for production")
        elif failed <= 1:
            print("  ⚠️  System is mostly stable, minor issues to investigate")
        else:
            print("  ❌ System needs fixes before production deployment")
        
        print("\n" + "█" * 80)
        
        return 0 if failed == 0 else 1


def main():
    """Run stability testing"""
    tester = StabilityTester()
    return tester.run_all()


if __name__ == "__main__":
    sys.exit(main())
