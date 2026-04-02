"""
API Integration - Smart AI Test Generator v2 (REAL Implementation)
Adapter between test generation system and FastAPI endpoints

Now uses AITestGenerator v2 with TRUE smart features:
- Real Vietnamese + English parsing
- Dynamic entity extraction (no templates)
- Real effort calculation (not hardcoded)
- Real quality scoring (not fake 50%)
- Domain-specific test generation
- Security-aware test type selection
"""

from typing import List, Dict, Any, Optional
import json
from datetime import datetime
from requirement_analyzer.task_gen.smart_ai_generator_v2 import AITestGenerator


class PureMLAPIAdapter:
    """Adapter between Smart AI Test Generator and FastAPI"""
    
    def __init__(self):
        self.generator = AITestGenerator()
    
    def generate_test_cases(
        self,
        requirements_text: str,
        max_tests: int = 10,
        confidence_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Generate production-grade test cases from requirements using Smart AI
        
        Features:
        ✅ Deep NLP requirement parsing (regex patterns)
        ✅ Unique ID generation (no duplicates)
        ✅ Complete test structure (preconditions, steps, expected results)
        ✅ Multiple test types (happy path, boundary, edge cases, security...)
        ✅ DYNAMIC test data generation (extracted from requirement content)
        ✅ DYNAMIC step generation (built from analyzed entities)
        ✅ Domain detection (from actual requirement keywords)
        ✅ Truly adaptive - each requirement generates UNIQUE test cases
        
        Args:
            requirements_text: Raw requirements (multiline text)
            max_tests: Maximum test cases to generate
            confidence_threshold: Minimum quality score (0-1)
        
        Returns:
            API response with truly intelligent, dynamically-built test cases
        """
        
        # Parse requirements into list
        req_list = [
            r.strip() for r in requirements_text.split('\n') 
            if r.strip() and not r.startswith('#')
        ]
        
        if not req_list:
            return {
                "status": "error",
                "message": "No valid requirements provided",
                "test_cases": [],
                "summary": {}
            }
        
        try:
            # Generate using Smart AI Test Generator (true dynamic building, not templates)
            results = self.generator.generate(req_list, max_tests=max_tests)
            
            # Filter by quality threshold
            filtered_cases = [
                tc for tc in results["test_cases"]
                if tc.get("ml_quality_score", 0) >= confidence_threshold
            ]
            
            # Build response
            return {
                "status": "success",
                "test_cases": filtered_cases,
                "summary": {
                    "total_test_cases": len(filtered_cases),
                    "avg_quality_score": results["summary"].get("avg_quality_score", 0),
                    "avg_effort_hours": results["summary"].get("avg_effort_hours", 0),
                    "test_types": results["summary"].get("test_type_distribution", {}),
                    "requirements_processed": len(req_list),
                    "timestamp": datetime.now().isoformat(),
                    "system": "Smart AI Test Generator v2 (Real Implementation)",
                    "features": [
                        "Vietnamese + English parsing",
                        "Dynamic entity extraction",
                        "Real effort calculation",
                        "Real quality scoring",
                        "Domain detection",
                        "Security-aware tests",
                        "Multiple test types",
                        "Unique ID generation"
                    ]
                },
                "errors": results.get("errors", [])
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "test_cases": [],
                "summary": {},
                "errors": [str(e)]
            }
    
    def submit_feedback(
        self,
        test_case_id: str,
        requirement_id: str,
        scenario_type: str,
        user_feedback: str,
        test_execution_result: str,
        defects_found: int = 0,
        coverage_rating: int = 3,
        clarity_rating: int = 3,
        effort_accuracy: int = 3,
        comments: str = ""
    ) -> Dict[str, Any]:
        """
        Submit user feedback on test case
        
        Returns:
            {status, message, learning_insights}
        """
        
        try:
            success = self.generator.submit_feedback(
                test_case_id=test_case_id,
                requirement_id=requirement_id,
                scenario_type=scenario_type,
                user_feedback=user_feedback,
                test_execution_result=test_execution_result,
                defects_found=defects_found,
                coverage_rating=coverage_rating,
                clarity_rating=clarity_rating,
                effort_accuracy=effort_accuracy,
                comments=comments
            )
            
            if success:
                # Get updated system stats
                stats = self.generator.get_system_stats()
                learning_data = stats.get("learning", {})
                return {
                    "status": "success",
                    "message": "Feedback submitted successfully",
                    "system_health": stats["system_health"],
                    "feedback_stats": stats["feedback"],
                    "learning_improvements": {
                        "recommendation": learning_data.get("recommendations", ["No recommendations yet"])[0] if learning_data.get("recommendations") else "Continue collecting feedback",
                        "next_focus": learning_data.get("weaknesses", ["Well-balanced system"])[0] if learning_data.get("weaknesses") else "Well-balanced system"
                    }
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to save feedback",
                    "system_health": None
                }
        
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "system_health": None
            }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics and learning insights"""
        try:
            stats = self.generator.get_system_stats()
            return {
                "status": "success",
                "stats": {
                    "generations": stats["generation"],
                    "feedback": stats["feedback"],
                    "learning": stats["learning"],
                    "system_health": stats["system_health"]
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get AI learning insights for display"""
        try:
            stats = self.generator.get_system_stats()
            learning = stats["learning"]
            
            return {
                "status": "success",
                "insights": {
                    "total_feedback": learning.get("total_feedback_entries", 0),
                    "success_rates": learning.get("scenario_success_rates", {}),
                    "strengths": learning.get("strengths", []),
                    "weaknesses": learning.get("weaknesses", []),
                    "recommendations": learning.get("recommendations", []),
                    "system_health": stats["system_health"]
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }


# Demo
if __name__ == "__main__":
    print("🧠 PURE ML API ADAPTER DEMO\n")
    print("=" * 80)
    
    adapter = PureMLAPIAdapter()
    
    # Demo 1: Generate test cases
    print("\n1️⃣ DEMO: Generate Test Cases\n")
    requirements = """
    The system must allow patients to schedule appointments up to 30 days in advance.
    The system shall prevent unauthorized access to patient medical records.
    Doctors can prescribe medications only if patient allergies are verified.
    """
    
    results = adapter.generate_test_cases(requirements, max_tests=6)
    print(f"Status: {results['status']}")
    print(f"Generated: {results['summary']['total_test_cases']} test cases")
    print(f"Quality: {results['summary']['avg_quality_score']:.1%}")
    print(f"System: {results['summary'].get('system', 'Unknown')}")
    
    # Show first test case
    if results['test_cases']:
        tc = results['test_cases'][0]
        print(f"\n📋 Sample Test Case:")
        print(f"   {tc['id']}: {tc['title']}")
        print(f"   Type: {tc['scenario_type']}")
        print(f"   Quality: {tc['ml_quality_score']:.1%}")
        print(f"   Effort: {tc['estimated_effort_minutes']}m")
    
    # Demo 2: Submit feedback
    print("\n\n2️⃣ DEMO: Submit Feedback\n")
    if results['test_cases']:
        tc = results['test_cases'][0]
        feedback = adapter.submit_feedback(
            test_case_id=tc['id'],
            requirement_id=tc['requirement_id'],
            scenario_type=tc['scenario_type'],
            user_feedback="good",
            test_execution_result="pass",
            defects_found=1,
            coverage_rating=5,
            clarity_rating=5,
            effort_accuracy=4,
            comments="Excellent test, found real issue"
        )
        print(f"Feedback Status: {feedback['status']}")
        if feedback['status'] == 'success':
            print(f"System Health: {feedback['system_health']['status']}")
            print(f"Score: {feedback['system_health']['score']:.0%}")
    
    # Demo 3: Get learning insights
    print("\n\n3️⃣ DEMO: AI Learning Insights\n")
    insights = adapter.get_learning_insights()
    if insights['status'] == 'success':
        data = insights['insights']
        print(f"Total Feedback: {data['total_feedback']}")
        print(f"Scenario Success Rates: {data['success_rates']}")
        print(f"Recommendations: {data['recommendations']}")
    
    print("\n" + "=" * 80)
    print("✅ API Adapter Ready for Integration!")
    print("=" * 80)
