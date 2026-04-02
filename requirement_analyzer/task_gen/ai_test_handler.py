"""
AI Test Generation Handler - Integration Layer
================================================

Integrates AI test generator with existing task generation pipeline.
Connects to database, handles storage, provides API interface.
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("ai_test_handler")

try:
    from .ai_intelligent_test_generator import AIIntelligentTestGenerator
except ImportError:
    logger.warning("Could not import ai_intelligent_test_generator")
    AIIntelligentTestGenerator = None


class AITestGenerationHandler:
    """
    Handles AI test generation workflow.
    
    Responsibilities:
    - Generate test cases using AI
    - Store results
    - Track AI confidence and reasoning
    - Export test cases in various formats
    """
    
    def __init__(self, storage_dir: Optional[str] = None):
        """Initialize handler"""
        self.generator = AIIntelligentTestGenerator() if AIIntelligentTestGenerator else None
        self.storage_dir = Path(storage_dir) if storage_dir else Path("./ai_test_results")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"✓ AI Test Handler initialized. Storage: {self.storage_dir}")
    
    def generate_tests_for_task(self, task_id: str, task_description: str, 
                               acceptance_criteria: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate test cases for a task using AI.
        
        Args:
            task_id: Task identifier
            task_description: Task/requirement text
            acceptance_criteria: Optional AC for additional context
        
        Returns:
            Dict with generated test cases and analysis
        """
        
        if not self.generator:
            logger.error("AI Generator not initialized")
            return {"status": "error", "message": "AI Generator not available"}
        
        try:
            logger.info(f"[{task_id}] Starting AI test generation...")
            
            # Combine task description with AC if available
            full_requirement = task_description
            if acceptance_criteria:
                full_requirement += f"\n\nAcceptance Criteria:\n{acceptance_criteria}"
            
            # Generate tests using AI
            result = self.generator.generate_test_cases(full_requirement)
            
            # Add metadata
            result["task_id"] = task_id
            result["generated_at"] = datetime.now().isoformat()
            result["acceptance_criteria"] = acceptance_criteria
            
            # Store result
            self._store_result(task_id, result)
            
            logger.info(f"[{task_id}] ✓ Generated {result['summary']['total_test_cases']} test cases")
            
            return result
            
        except Exception as e:
            logger.error(f"[{task_id}] Error during test generation: {e}")
            return {
                "status": "error",
                "task_id": task_id,
                "message": str(e),
                "error_type": type(e).__name__
            }
    
    def generate_tests_for_multiple_tasks(self, tasks: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Generate test cases for multiple tasks.
        
        Args:
            tasks: List of {'task_id': '...', 'description': '...', 'ac': '...'}
        
        Returns:
            List of results
        """
        results = []
        
        logger.info(f"[BATCH] Starting batch test generation for {len(tasks)} tasks...")
        
        for task in tasks:
            result = self.generate_tests_for_task(
                task_id=task.get("task_id"),
                task_description=task.get("description"),
                acceptance_criteria=task.get("ac")
            )
            results.append(result)
        
        logger.info(f"[BATCH] ✓ Batch generation complete. Processed {len(tasks)} tasks")
        
        return results
    
    def _store_result(self, task_id: str, result: Dict[str, Any]):
        """Store generation result to disk"""
        
        # Sanitize task_id for file path
        safe_task_id = "".join(c if c.isalnum() or c in '-_' else '_' for c in task_id)
        output_file = self.storage_dir / f"{safe_task_id}_test_generation.json"
        
        try:
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            
            logger.debug(f"Stored result: {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to store result: {e}")
    
    def load_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Load previously generated result"""
        
        output_file = self.storage_dir / f"{task_id}_test_generation.json"
        
        if not output_file.exists():
            return None
        
        try:
            with open(output_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load result: {e}")
            return None
    
    def export_tests_as_pytest(self, result: Dict[str, Any]) -> str:
        """
        Export generated tests as pytest code.
        
        Args:
            result: Generation result from generate_tests_for_task
        
        Returns:
            Python code string (pytest format)
        """
        
        task_id = result.get("task_id", "test_task")
        test_cases = result.get("test_cases", [])
        
        code_lines = [
            f'"""',
            f'Auto-generated tests for task: {task_id}',
            f'Generated by: AI Intelligent Test Generator',
            f'Generated at: {result.get("generated_at", "unknown")}',
            f'"""',
            f'',
            f'import pytest',
            f'',
            f'# Task: {result.get("requirement", "")[:80]}',
            f'# Requirement Complexity: {result.get("analysis", {}).get("complexity", 0)}',
            f'# AI Generated {len(test_cases)} test cases:',
            f'',
        ]
        
        for tc in test_cases:
            # Generate function name
            func_name = f"test_{task_id}_{tc.get('test_id', '').lower().replace('-', '_')}"
            
            # Generate test function
            code_lines.append(f'def {func_name}():')
            code_lines.append(f'    """')
            code_lines.append(f'    {tc.get("title", "Test")}')
            code_lines.append(f'    Type: {tc.get("type", "Unit")}')
            code_lines.append(f'    Priority: {tc.get("priority", "Medium")}')
            code_lines.append(f'    Why: {tc.get("why_generated", "")[:70]}')
            code_lines.append(f'    AI Confidence: {tc.get("ai_confidence", 0)}')
            code_lines.append(f'    """')
            
            # Add setup
            code_lines.append(f'    # Setup/Preconditions')
            for prec in tc.get("preconditions", []):
                code_lines.append(f'    # - {prec}')
            
            # Add steps and assertions
            steps = tc.get("steps", [])
            for step in steps:
                code_lines.append(f'    # Step {step.get("step_number", 1)}: {step.get("action", "")}')
            
            code_lines.append(f'    # Expected: {tc.get("expected_result", "")}')
            
            # Add placeholder assertion
            code_lines.append(f'    # TODO: Implement test logic')
            code_lines.append(f'    assert True  # Placeholder')
            code_lines.append(f'')
        
        return '\n'.join(code_lines)
    
    def export_tests_as_gherkin(self, result: Dict[str, Any]) -> str:
        """
        Export generated tests as Gherkin/BDD scenarios.
        
        Args:
            result: Generation result
        
        Returns:
            Gherkin feature file content
        """
        
        task_id = result.get("task_id", "feature")
        scenarios = result.get("scenarios", [])
        
        feature_lines = [
            f'Feature: {result.get("requirement", "Feature")[:80]}',
            f'  # Generated by: AI Intelligent Test Generator',
            f'  # Task ID: {task_id}',
            f'  # Scenarios: {len(scenarios)}',
            f'',
        ]
        
        for scenario in scenarios:
            feature_lines.append(f'  Scenario: {scenario.get("name", "Scenario")}')
            feature_lines.append(f'    # Type: {scenario.get("type", "Unknown")}')
            feature_lines.append(f'    # Importance: {scenario.get("importance", 0.5)}')
            feature_lines.append(f'    Given some initial condition')
            feature_lines.append(f'    When user performs action')
            feature_lines.append(f'    Then verify expected result')
            feature_lines.append(f'')
        
        return '\n'.join(feature_lines)
    
    def get_summary_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary report from multiple results.
        
        Args:
            results: List of generation results
        
        Returns:
            Summary report
        """
        
        total_tests = 0
        by_type = {}
        by_priority = {}
        confidence_scores = []
        
        for result in results:
            if result.get("status") == "error":
                continue
            
            summary = result.get("summary", {})
            total_tests += summary.get("total_test_cases", 0)
            
            # Count by type
            for test_type, count in summary.get("by_type", {}).items():
                by_type[test_type] = by_type.get(test_type, 0) + count
            
            # Count by priority
            for priority, count in summary.get("by_priority", {}).items():
                by_priority[priority] = by_priority.get(priority, 0) + count
            
            # Collect confidence scores
            avg_conf = summary.get("avg_confidence", 0)
            if avg_conf:
                confidence_scores.append(avg_conf)
        
        return {
            "total_tasks_processed": len(results),
            "total_test_cases_generated": total_tests,
            "distribution_by_type": by_type,
            "distribution_by_priority": by_priority,
            "average_ai_confidence": round(sum(confidence_scores) / len(confidence_scores), 2) if confidence_scores else 0,
            "high_confidence_rate": len([c for c in confidence_scores if c >= 0.8]) / len(confidence_scores) if confidence_scores else 0
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def generate_tests_for_requirement(requirement_text: str) -> Dict[str, Any]:
    """Simple function to generate tests for a requirement"""
    handler = AITestGenerationHandler()
    return handler.generate_tests_for_task(
        task_id="requirement",
        task_description=requirement_text
    )


def demonstrate_ai_generation():
    """Demonstrate AI-based test generation with sample requirements"""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )
    
    # Sample requirements
    requirements = [
        "User must be able to upload a CSV file with patient medical records. The system should validate the file format and reject files larger than 50MB. Upon successful upload, the system must parse the CSV and store records in database.",
        
        "An administrator should be able to generate a monthly report of system usage metrics. The report should include number of tasks completed, average completion time, and user activity. The report must be generated within 30 seconds.",
        
        "The system must implement role-based access control. Users with 'doctor' role can view patient records, users with 'admin' role can manage other users. Unauthorized access attempts should be logged.",
    ]
    
    handler = AITestGenerationHandler()
    
    print("\n" + "="*80)
    print("AI INTELLIGENT TEST GENERATION DEMONSTRATION")
    print("="*80)
    
    results = []
    
    for i, requirement in enumerate(requirements, 1):
        print(f"\n{'='*80}")
        print(f"Requirement {i}:")
        print(f"{'='*80}")
        print(requirement)
        
        result = handler.generate_tests_for_task(
            task_id=f"requirement_{i}",
            task_description=requirement
        )
        
        results.append(result)
        
        # Print analysis
        print(f"\n📊 ANALYSIS:")
        analysis = result.get("analysis", {})
        print(f"   Entities: {len(analysis.get('entities', []))}")
        print(f"   Relationships: {len(analysis.get('relationships', []))}")
        print(f"   Conditions: {len(analysis.get('conditions', []))}")
        print(f"   Complexity Score: {analysis.get('complexity', 0):.2f}")
        
        # Print scenarios
        print(f"\n📋 TEST SCENARIOS ({len(result.get('scenarios', []))}):")
        for scenario in result.get("scenarios", [])[:3]:  # Show first 3
            print(f"   • {scenario['name']} ({scenario['type']})")
        
        # Print test cases summary
        summary = result.get("summary", {})
        print(f"\n🧪 TEST CASES GENERATED: {summary.get('total_test_cases', 0)}")
        print(f"   By Type: {summary.get('by_type', {})}")
        print(f"   By Priority: {summary.get('by_priority', {})}")
        print(f"   Avg AI Confidence: {summary.get('avg_confidence', 0):.2f}")
    
    # Print overall summary
    print(f"\n{'='*80}")
    print("OVERALL SUMMARY")
    print(f"{'='*80}")
    
    overall = handler.get_summary_report(results)
    print(f"Total Tasks Processed: {overall['total_tasks_processed']}")
    print(f"Total Test Cases Generated: {overall['total_test_cases_generated']}")
    print(f"Average AI Confidence: {overall['average_ai_confidence']:.2f}")
    print(f"High Confidence Rate (≥0.8): {overall['high_confidence_rate']:.1%}")
    
    print(f"\n✓ Demonstration complete!")


if __name__ == "__main__":
    demonstrate_ai_generation()
