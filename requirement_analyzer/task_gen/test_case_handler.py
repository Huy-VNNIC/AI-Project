"""
Step 5 Integration: Test Case Handler
=====================================

Integrates AI Test Case Generation into V2 Pipeline.
Generates comprehensive test cases from:
- Tasks
- User Stories  
- Acceptance Criteria
- Requirements

NOW WITH CUSTOM AI: Uses AIIntelligentTestGenerator for smart requirement analysis!
Connects to FastAPI endpoints for full 7-step pipeline.
"""

import logging
from typing import List, Dict, Any, Optional
from requirement_analyzer.task_gen.test_case_generator import (
    TestCaseGenerator,
    TestCaseFromAcceptanceCriteria,
    TestCase
)

logger = logging.getLogger("test_case_handler")

# Import Custom AI Test Generator
try:
    from requirement_analyzer.task_gen.ai_intelligent_test_generator import AIIntelligentTestGenerator
    AI_AVAILABLE = True
    logger.info("✓ Custom AI Test Generator loaded")
except ImportError as e:
    AI_AVAILABLE = False
    logger.warning(f"⚠ Custom AI not available: {e}")


class TestCaseHandler:
    """Handler for integrating test case generation into API pipeline"""
    
    def __init__(self, use_ai: bool = True):
        """
        Initialize test case handler
        
        Args:
            use_ai: If True, use custom AI generator for requirement analysis.
                   If False, use template-based generator.
        """
        self.generator = TestCaseGenerator()
        self.use_ai = use_ai and AI_AVAILABLE
        
        if self.use_ai:
            try:
                self.ai_generator = AIIntelligentTestGenerator()
                logger.info("✓ Using Custom AI for test case generation")
            except Exception as e:
                logger.warning(f"⚠ Failed to initialize AI generator: {e}")
                self.use_ai = False
        else:
            logger.info("✓ Using template-based test case generation")
    
    def generate_ai_test_cases_from_requirements(self, 
                                                requirement_text: str) -> Dict[str, Any]:
        """
        Generate test cases directly from requirement text using CUSTOM AI.
        
        This uses the intelligent AI analyzer that understands:
        - Requirements deeply (NLP)
        - Test scenarios automatically
        - Edge cases intelligently
        - Generates specific, meaningful tests
        
        Args:
            requirement_text: Requirement description text
            
        Returns:
            Dictionary with AI-generated test cases and analysis
        """
        if not self.use_ai:
            logger.warning("⚠ AI not available, falling back to template-based generation")
            return self._generate_test_cases_fallback(requirement_text)
        
        try:
            logger.info(f"🤖 [AI] Analyzing requirement: {requirement_text[:80]}...")
            
            # Use Custom AI to generate test cases
            result = self.ai_generator.generate_test_cases(requirement_text)
            
            if result.get("status") == "success":
                logger.info(f"✅ [AI] Generated {result['summary']['total_test_cases']} test cases")
                logger.info(f"   - Avg Confidence: {result['summary']['avg_confidence']}")
                logger.info(f"   - Analysis: {len(result['analysis']['entities'])} entities found")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ [AI] Error in AI generation: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"AI generation failed: {str(e)}",
                "test_cases": [],
                "summary": {"total_test_cases": 0}
            }
    
    def _generate_test_cases_fallback(self, requirement_text: str) -> Dict[str, Any]:
        """Fallback to simple template-based generation"""
        # Simple heuristic-based generation
        return {
            "status": "success",
            "requirement": requirement_text,
            "test_cases": [
                {
                    "test_id": "T-001",
                    "title": "Happy Path Test",
                    "description": f"Test normal scenario: {requirement_text[:100]}",
                    "test_type": "Unit",
                    "priority": "High",
                    "steps": [
                        {"step": "1", "action": "Execute the requirement"},
                        {"step": "2", "action": "Verify expected result"}
                    ],
                    "expected_result": "Requirement is satisfied",
                    "ai_confidence": 0.6
                }
            ],
            "summary": {
                "total_test_cases": 1,
                "by_type": {"Unit": 1},
                "by_priority": {"High": 1},
                "avg_confidence": 0.6
            }
        }
    
    def generate_test_cases_from_pipeline(self, 
                                         api_v2_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate test cases from V2 API output (tasks, user stories, ACs)
        
        Uses AI if available to enhance test generation quality.
        
        Args:
            api_v2_output: Output from api_v2_handler containing:
                - tasks: List of generated tasks
                - user_stories: List of user stories
                - acceptance_criteria: List of acceptance criteria
                
        Returns:
            Dictionary with:
                - test_cases: List of generated test cases
                - summary: Test case statistics
                - by_type: Breakdown by test type
                - test_coverage: Coverage metrics
        """
        try:
            # Extract data from API output
            tasks = api_v2_output.get('tasks', [])
            user_stories = api_v2_output.get('user_stories', [])
            acceptance_criteria = api_v2_output.get('acceptance_criteria', [])
            
            logger.info(f"Generating test cases for {len(tasks)} tasks...")
            
            # If we have requirement text at top level and AI is available, use AI first
            if self.use_ai and 'requirement_text' in api_v2_output:
                requirement_text = api_v2_output['requirement_text']
                logger.info("📊 Using AI-enhanced test generation")
                ai_result = self.generate_ai_test_cases_from_requirements(requirement_text)
                
                if ai_result.get("status") == "success":
                    return ai_result
            
            # Otherwise, use template-based generation for tasks
            logger.info("📊 Using template-based test generation")
            # Generate test cases
            test_cases = self.generator.generate_test_cases(
                tasks=tasks,
                user_stories=user_stories,
                acceptance_criteria=acceptance_criteria
            )
            
            # Calculate statistics
            summary = self._calculate_summary(test_cases)
            breakdown = self._breakdown_by_type(test_cases)
            coverage = self._calculate_coverage(test_cases, tasks)
            
            logger.info(f"Generated {len(test_cases)} test cases")
            
            return {
                "status": "success",
                "test_cases": [tc.to_dict() for tc in test_cases],
                "total_test_cases": len(test_cases),
                "summary": summary,
                "breakdown_by_type": breakdown,
                "test_coverage": coverage,
                "quality_metrics": {
                    "test_case_count": len(test_cases),
                    "coverage_percentage": coverage.get('coverage_percentage', 0),
                    "automation_rate": coverage.get('automation_rate', 0),
                    "adequacy_score": self._calculate_adequacy_score(test_cases, tasks)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating test cases: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Error generating test cases: {str(e)}",
                "test_cases": [],
                "total_test_cases": 0
            }
    
    def generate_test_cases_from_acceptance_criteria(self,
                                                      acceptance_criteria: List[Dict[str, str]],
                                                      task_id: str) -> List[Dict[str, Any]]:
        """
        Generate test cases directly from acceptance criteria
        
        Args:
            acceptance_criteria: List of AC objects with given/when/then
            task_id: Associated task ID
            
        Returns:
            List of test case dictionaries
        """
        test_cases = []
        
        for i, ac in enumerate(acceptance_criteria):
            test_id = f"AC-TC-{task_id.split('-')[-1]}-{i+1:03d}"
            
            test_case = TestCaseFromAcceptanceCriteria.create_from_ac(
                ac=ac,
                task_id=task_id,
                test_id=test_id
            )
            
            test_cases.append(test_case.to_dict())
        
        return test_cases
    
    def _calculate_summary(self, test_cases: List[TestCase]) -> Dict[str, Any]:
        """Calculate test case summary statistics"""
        if not test_cases:
            return {
                "total": 0,
                "by_priority": {},
                "by_type": {},
                "automated_count": 0,
                "manual_count": 0
            }
        
        summary = {
            "total": len(test_cases),
            "by_priority": {},
            "by_type": {},
            "automated_count": 0,
            "manual_count": 0
        }
        
        # Count by priority
        for tc in test_cases:
            priority = tc.priority or "Medium"
            summary["by_priority"][priority] = summary["by_priority"].get(priority, 0) + 1
            
            # Count automation
            if tc.automation_level == "Automated":
                summary["automated_count"] += 1
            else:
                summary["manual_count"] += 1
        
        return summary
    
    def _breakdown_by_type(self, test_cases: List[TestCase]) -> Dict[str, int]:
        """Breakdown test cases by type"""
        breakdown = {}
        
        for tc in test_cases:
            test_type = tc.test_type.value
            breakdown[test_type] = breakdown.get(test_type, 0) + 1
        
        return breakdown
    
    def _calculate_coverage(self, test_cases: List[TestCase], tasks: List[Dict]) -> Dict[str, Any]:
        """Calculate test coverage metrics"""
        if not tasks:
            return {
                "coverage_percentage": 0,
                "covered_tasks": 0,
                "uncovered_tasks": 0,
                "automation_rate": 0,
                "test_case_per_task": 0
            }
        
        # Count covered tasks
        covered_task_ids = set()
        for tc in test_cases:
            if tc.task_id:
                covered_task_ids.add(tc.task_id)
        
        covered_count = len(covered_task_ids)
        total_tasks = len(tasks)
        
        coverage_percentage = (covered_count / total_tasks * 100) if total_tasks > 0 else 0
        
        # Calculate automation rate
        automated = sum(1 for tc in test_cases if tc.automation_level == "Automated")
        automation_rate = (automated / len(test_cases) * 100) if test_cases else 0
        
        # Test cases per task
        test_case_per_task = len(test_cases) / total_tasks if total_tasks > 0 else 0
        
        return {
            "coverage_percentage": round(coverage_percentage, 2),
            "covered_tasks": covered_count,
            "uncovered_tasks": total_tasks - covered_count,
            "automation_rate": round(automation_rate, 2),
            "test_case_per_task": round(test_case_per_task, 2)
        }
    
    def _calculate_adequacy_score(self, test_cases: List[TestCase], tasks: List[Dict]) -> float:
        """
        Calculate test adequacy score (0-100)
        
        Factors:
        - Coverage (40%): How many tasks are covered
        - Test types (30%): Variety of test types
        - Automation (20%): Percentage automated
        - Complexity (10%): Tests for complex scenarios
        """
        if not test_cases or not tasks:
            return 0.0
        
        # Coverage score (40%)
        covered = len(set(tc.task_id for tc in test_cases if tc.task_id))
        coverage_score = min(100, (covered / len(tasks)) * 100) * 0.4
        
        # Test type variety (30%)
        test_type_count = len(set(tc.test_type for tc in test_cases))
        max_types = 7  # We have 7 test types
        type_score = min(100, (test_type_count / max_types) * 100) * 0.3
        
        # Automation score (20%)
        automated = sum(1 for tc in test_cases if tc.automation_level == "Automated")
        automation_score = (automated / len(test_cases)) * 100 * 0.2
        
        # Complexity score (10%) - security + performance + boundary tests
        complex_types = ["Security", "Performance", "Boundary Value"]
        complex_count = sum(1 for tc in test_cases if tc.test_type.value in complex_types)
        complexity_score = min(100, (complex_count / max(1, len(test_cases) / 3)) * 100) * 0.1
        
        total_score = coverage_score + type_score + automation_score + complexity_score
        
        return round(total_score, 2)

    def export_test_cases_to_pytest(self, test_cases: List[Dict[str, Any]]) -> str:
        """
        Export test cases to pytest format
        
        Args:
            test_cases: List of test case dictionaries
            
        Returns:
            Python code string with pytest tests
        """
        code = '''"""
Auto-generated pytest test suite from AI Test Case Generator
============================================================
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


'''
        
        # Group by task
        by_task = {}
        for tc in test_cases:
            task_id = tc.get('task_id', 'UNKNOWN')
            if task_id not in by_task:
                by_task[task_id] = []
            by_task[task_id].append(tc)
        
        # Generate test class for each task
        for task_id, tcs in by_task.items():
            class_name = f"Test{task_id.replace('-', '_')}"
            code += f"\nclass {class_name}:\n"
            code += f'    """Test cases for {task_id}"""\n\n'
            
            for tc in tcs:
                test_name = f"test_{tc['title'].lower().replace(' ', '_')[:50]}"
                code += f'    def {test_name}(self):\n'
                code += f'        """{tc["description"]}\n\n'
                code += f'        {tc["expected_result"]}\n'
                code += f'        """\n'
                code += f'        # Arrange\n'
                code += f'        # TODO: Set up test data\n\n'
                code += f'        # Act\n'
                code += f'        # TODO: Execute the action\n\n'
                code += f'        # Assert\n'
                code += f'        # TODO: Verify the results\n'
                code += f'        assert True  # Replace with actual assertion\n\n'
        
        return code
    
    def export_test_cases_to_csv(self, test_cases: List[Dict[str, Any]]) -> str:
        """
        Export test cases to CSV format
        
        Args:
            test_cases: List of test case dictionaries
            
        Returns:
            CSV formatted string
        """
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                'test_id', 'title', 'test_type', 'task_id', 'priority',
                'status', 'automation_level', 'description', 'expected_result'
            ]
        )
        
        writer.writeheader()
        
        for tc in test_cases:
            writer.writerow({
                'test_id': tc.get('test_id'),
                'title': tc.get('title'),
                'test_type': tc.get('test_type'),
                'task_id': tc.get('task_id'),
                'priority': tc.get('priority'),
                'status': tc.get('status'),
                'automation_level': tc.get('automation_level'),
                'description': tc.get('description'),
                'expected_result': tc.get('expected_result')
            })
        
        return output.getvalue()
    
    def export_test_cases_to_junit(self, test_cases: List[Dict[str, Any]]) -> str:
        """
        Export test cases to JUnit / TestNG format XML
        
        Args:
            test_cases: List of test case dictionaries
            
        Returns:
            XML formatted string
        """
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<testcases>\n'
        
        for tc in test_cases:
            xml += f'  <testcase name="{tc.get("test_id")}" classname="{tc.get("task_id")}">\n'
            xml += f'    <properties>\n'
            xml += f'      <property name="type" value="{tc.get("test_type")}"/>\n'
            xml += f'      <property name="priority" value="{tc.get("priority")}"/>\n'
            xml += f'      <property name="automation" value="{tc.get("automation_level")}"/>\n'
            xml += f'    </properties>\n'
            xml += f'    <description>{tc.get("description")}</description>\n'
            xml += f'    <expected-result>{tc.get("expected_result")}</expected-result>\n'
            xml += f'  </testcase>\n'
        
        xml += '</testcases>\n'
        
        return xml
