"""
Pure ML Test Case Generator V3 - Orchestrator
No API required - fully self-contained AI system
Integrates: Parser → Generator → Feedback → Learning
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from requirement_analyzer.task_gen.llm_parser_pure import PureMLParser, ParsedRequirement
from requirement_analyzer.task_gen.llm_test_generator_pure import PureMLTestGenerator, TestCaseML
from requirement_analyzer.task_gen.feedback_system import FeedbackCollector, FeedbackEntry, LearningSystem


class PureMLTestCaseGeneratorV3:
    """
    Complete AI test case generation pipeline (pure, no API)
    
    Architecture:
    Requirement → Parser (spaCy) → Generator (ML-scored) → Test Cases
                                                          ↓
                                                    Feedback Loop
                                                          ↓
                                                    Learning System
    """
    
    def __init__(self):
        self.parser = PureMLParser()
        self.generator = PureMLTestGenerator()
        self.feedback_collector = FeedbackCollector()
        self.learning_system = LearningSystem()
        self.generation_history = []
    
    def generate(
        self,
        requirements: List[str],
        max_test_cases: int = 10,
        use_feedback: bool = True
    ) -> Dict[str, Any]:
        """
        Main generation pipeline
        
        Args:
            requirements: List of requirement texts
            max_test_cases: Maximum test cases to generate
            use_feedback: Use learning system insights
        
        Returns:
            Dict with test_cases, summary, learning_insights
        """
        
        print(f"\n🧠 PURE ML TEST CASE GENERATOR V3")
        print(f"━" * 80)
        print(f"📥 Input: {len(requirements)} requirements")
        print(f"⚙️ Mode: Pure ML (no external API)")
        print(f"🎓 Learning: {'Enabled' if use_feedback else 'Disabled'}")
        print(f"━" * 80)
        
        result = self.generator.generate(requirements, max_test_cases)
        
        # Add learning insights if enabled
        if use_feedback:
            learning_insights = self._get_learning_insights()
            result["learning_insights"] = learning_insights
            
            # Apply learned adjustments
            result["test_cases"] = self._apply_learning_adjustments(
                result["test_cases"],
                learning_insights
            )
        
        # Store in history
        self.generation_history.append({
            "timestamp": datetime.now().isoformat(),
            "requirements_count": len(requirements),
            "test_cases_count": len(result["test_cases"]),
            "summary": result["summary"]
        })
        
        return result
    
    def _get_learning_insights(self) -> Dict[str, Any]:
        """Get insights from feedback system"""
        insights = {
            "feedback_stats": self.feedback_collector.get_stats(),
            "learning_analysis": self.learning_system.analyze_patterns(),
            "improvement_suggestions": self.learning_system.suggest_improvements()
        }
        return insights
    
    def _apply_learning_adjustments(
        self,
        test_cases: List[Dict[str, Any]],
        insights: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Apply learned adjustments to test cases
        (Boost quality of good scenario types, improve poor ones)
        """
        learning = insights["learning_analysis"]
        
        if "scenario_success_rates" not in learning:
            return test_cases
        
        success_rates = learning["scenario_success_rates"]
        
        # Adjust quality scores based on learned success rates
        updated_cases = []
        for tc in test_cases:
            stype = tc["scenario_type"]
            success_rate = success_rates.get(stype, 0.5)
            
            # Boost quality for high-performing types
            if success_rate > 0.85:
                tc["ml_quality_score"] = min(1.0, tc["ml_quality_score"] * 1.1)
            elif success_rate < 0.7:
                # Keep as is - needs improvement
                tc["ml_quality_score"] = max(0.3, tc["ml_quality_score"] * 0.9)
            
            updated_cases.append(tc)
        
        return updated_cases
    
    def submit_feedback(
        self,
        test_case_id: str,
        requirement_id: str,
        scenario_type: str,
        user_feedback: str,  # "good" | "bad" | "needs_improvement"
        test_execution_result: str,  # "pass" | "fail"
        defects_found: int = 0,
        coverage_rating: int = 3,
        clarity_rating: int = 3,
        effort_accuracy: int = 3,
        comments: str = ""
    ) -> bool:
        """
        Submit feedback on generated test case
        System learns from this feedback
        """
        feedback = FeedbackEntry(
            test_case_id=test_case_id,
            requirement_id=requirement_id,
            scenario_type=scenario_type,
            user_feedback=user_feedback,
            test_execution_result=test_execution_result,
            defects_found=defects_found,
            coverage_rating=coverage_rating,
            clarity_rating=clarity_rating,
            effort_accuracy=effort_accuracy,
            comments=comments,
            rating=self._calculate_rating(
                user_feedback, defects_found, coverage_rating
            )
        )
        
        return self.feedback_collector.submit_feedback(feedback)
    
    def _calculate_rating(self, feedback: str, defects: int, coverage: int) -> int:
        """Calculate overall rating from components"""
        if feedback == "good" and defects > 0 and coverage >= 4:
            return 5
        elif feedback == "good":
            return 4
        elif feedback == "needs_improvement":
            return 3
        else:  # bad
            return 1
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        feedback_stats = self.feedback_collector.get_stats()
        learning_analysis = self.learning_system.analyze_patterns()
        
        return {
            "generation": {
                "total_generations": len(self.generation_history),
                "latest": self.generation_history[-1] if self.generation_history else None
            },
            "feedback": feedback_stats,
            "learning": learning_analysis,
            "system_health": self._calculate_system_health(feedback_stats, learning_analysis)
        }
    
    def _calculate_system_health(self, feedback_stats: Dict, learning: Dict) -> Dict[str, Any]:
        """Calculate system health score"""
        if feedback_stats["total_feedback"] == 0:
            return {
                "status": "INITIALIZING",
                "score": 0.0,
                "message": "Collect more feedback to improve"
            }
        
        good_ratio = feedback_stats.get("good_ratio", 0)
        
        if good_ratio >= 0.85:
            status = "EXCELLENT"
        elif good_ratio >= 0.70:
            status = "GOOD"
        elif good_ratio >= 0.50:
            status = "FAIR"
        else:
            status = "NEEDS_IMPROVEMENT"
        
        return {
            "status": status,
            "score": round(good_ratio, 2),
            "message": f"{good_ratio:.0%} of test cases rated good"
        }


# Demo with full lifecycle
if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🚀 PURE ML TEST CASE GENERATOR V3 - FULL DEMO")
    print("=" * 80)
    
    generator = PureMLTestCaseGeneratorV3()
    
    # Test requirements
    test_requirements = [
        "The system must allow patients to schedule appointments up to 30 days in advance without exceeding maximum capacity.",
        "The system shall prevent unauthorized access to patient medical records with encryption and audit trails.",
        "Doctors can only prescribe medications after checking patient allergies and drug interactions.",
    ]
    
    # Step 1: Generate test cases
    print("\n📊 STEP 1: Generate Test Cases")
    print("-" * 80)
    results = generator.generate(test_requirements, max_test_cases=8)
    
    print(f"\n✅ Generated {results['summary']['total_test_cases']} test cases")
    print(f"   Avg Quality: {results['summary']['avg_quality_score']:.1%}")
    print(f"   Avg Effort: {results['summary']['avg_effort_minutes']}m")
    
    # Display test cases
    print("\n📋 Generated Test Cases:")
    print("-" * 80)
    for i, tc in enumerate(results['test_cases'][:3], 1):
        print(f"\n{i}. {tc['id']}: {tc['title']}")
        print(f"   Type: {tc['scenario_type']}")
        print(f"   Priority: {tc['priority']} | Risk: {tc['risk_level']}")
        print(f"   Effort: {tc['estimated_effort_minutes']}m | Quality: {tc['ml_quality_score']:.1%}")
    
    # Step 2: Simulate feedback
    print("\n\n📝 STEP 2: Submit Feedback (Simulate User Ratings)")
    print("-" * 80)
    
    # Good feedback
    generator.submit_feedback(
        test_case_id=results['test_cases'][0]['id'],
        requirement_id=results['test_cases'][0]['requirement_id'],
        scenario_type=results['test_cases'][0]['scenario_type'],
        user_feedback="good",
        test_execution_result="pass",
        defects_found=2,
        coverage_rating=5,
        clarity_rating=5,
        effort_accuracy=4,
        comments="Excellent test case, caught real issues"
    )
    print(f"✅ Submitted positive feedback")
    
    # Needs improvement
    generator.submit_feedback(
        test_case_id=results['test_cases'][1]['id'],
        requirement_id=results['test_cases'][1]['requirement_id'],
        scenario_type=results['test_cases'][1]['scenario_type'],
        user_feedback="needs_improvement",
        test_execution_result="fail",
        defects_found=0,
        coverage_rating=2,
        clarity_rating=3,
        effort_accuracy=2,
        comments="Steps were unclear, effort estimate was off"
    )
    print(f"✅ Submitted improvement feedback")
    
    # Step 3: Get system stats
    print("\n\n📊 STEP 3: System Statistics & Learning")
    print("-" * 80)
    stats = generator.get_system_stats()
    
    print(f"\n🔢 Feedback Stats:")
    print(f"   Total Feedback: {stats['feedback']['total_feedback']}")
    print(f"   Good Ratio: {stats['feedback']['good_ratio']:.0%}")
    print(f"   Avg Rating: {stats['feedback']['avg_rating']}/5")
    print(f"   Avg Defects Found: {stats['feedback']['avg_defects_found']}")
    
    print(f"\n🧠 Learning Analysis:")
    print(f"   By Scenario Type:")
    for stype, rate in stats['learning'].get('scenario_success_rates', {}).items():
        status = "✅" if rate > 0.7 else "⚠️"
        print(f"      {status} {stype}: {rate:.0%}")
    
    print(f"\n💪 System Health: {stats['system_health']['status']}")
    print(f"   Score: {stats['system_health']['score']:.0%}")
    print(f"   {stats['system_health']['message']}")
    
    print(f"\n💡 Improvement Suggestions:")
    for suggestion in stats['learning'].get('improvement_suggestions', []):
        print(f"   {suggestion}")
    
    print("\n" + "=" * 80)
    print("✅ PURE ML SYSTEM FULLY OPERATIONAL - No external API required!")
    print("=" * 80)
