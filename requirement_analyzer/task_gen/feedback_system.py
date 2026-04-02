"""
Feedback System - Collects data for continuous learning
Stores feedback to improve model over time
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class FeedbackEntry:
    """User feedback on generated test cases"""
    test_case_id: str
    requirement_id: str
    scenario_type: str
    user_feedback: str  # "good" | "needs_improvement" | "bad"
    test_execution_result: str  # "pass" | "fail" | "not_executed"
    defects_found: int  # Number of defects this test caught
    coverage_rating: int  # 1-5: Does it cover the requirement well?
    clarity_rating: int  # 1-5: Are steps clear?
    effort_accuracy: int  # 1-5: Was effort estimate accurate?
    comments: str = ""
    rating: int = 3  # Overall 1-5 rating
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "test_case_id": self.test_case_id,
            "requirement_id": self.requirement_id,
            "scenario_type": self.scenario_type,
            "user_feedback": self.user_feedback,
            "test_execution_result": self.test_execution_result,
            "defects_found": self.defects_found,
            "coverage_rating": self.coverage_rating,
            "clarity_rating": self.clarity_rating,
            "effort_accuracy": self.effort_accuracy,
            "comments": self.comments,
            "rating": self.rating,
            "timestamp": self.timestamp,
        }


class FeedbackCollector:
    """Collects and stores feedback for model improvement"""
    
    def __init__(self, feedback_dir: str = "data/feedback"):
        self.feedback_dir = Path(feedback_dir)
        self.feedback_dir.mkdir(parents=True, exist_ok=True)
        self.feedback_file = self.feedback_dir / "feedback_log.jsonl"
    
    def submit_feedback(self, feedback: FeedbackEntry) -> bool:
        """Submit feedback entry"""
        try:
            # Append to JSONL file
            with open(self.feedback_file, "a") as f:
                f.write(json.dumps(feedback.to_dict()) + "\n")
            
            print(f"✅ Feedback saved for {feedback.test_case_id}")
            return True
        
        except Exception as e:
            print(f"❌ Error saving feedback: {e}")
            return False
    
    def load_all_feedback(self) -> List[FeedbackEntry]:
        """Load all feedback entries"""
        feedback_list = []
        
        if not self.feedback_file.exists():
            return feedback_list
        
        with open(self.feedback_file, "r") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    feedback_list.append(FeedbackEntry(**data))
        
        return feedback_list
    
    def get_stats(self) -> Dict[str, Any]:
        """Get feedback statistics"""
        feedback_list = self.load_all_feedback()
        
        if not feedback_list:
            return {
                "total_feedback": 0,
                "avg_rating": 0,
                "good_ratio": 0,
                "by_scenario_type": {}
            }
        
        good_count = sum(1 for f in feedback_list if f.user_feedback == "good")
        
        # Group by scenario type
        by_type = {}
        for f in feedback_list:
            if f.scenario_type not in by_type:
                by_type[f.scenario_type] = []
            by_type[f.scenario_type].append(f.rating)
        
        avg_by_type = {
            scenario: sum(ratings) / len(ratings)
            for scenario, ratings in by_type.items()
        }
        
        return {
            "total_feedback": len(feedback_list),
            "avg_rating": round(sum(f.rating for f in feedback_list) / len(feedback_list), 2),
            "good_ratio": round(good_count / len(feedback_list), 2),
            "bad_count": sum(1 for f in feedback_list if f.user_feedback == "bad"),
            "avg_defects_found": round(sum(f.defects_found for f in feedback_list) / len(feedback_list), 2),
            "avg_coverage_rating": round(sum(f.coverage_rating for f in feedback_list) / len(feedback_list), 2),
            "avg_clarity_rating": round(sum(f.clarity_rating for f in feedback_list) / len(feedback_list), 2),
            "avg_effort_accuracy": round(sum(f.effort_accuracy for f in feedback_list) / len(feedback_list), 2),
            "by_scenario_type": avg_by_type,
        }


class LearningSystem:
    """Uses feedback to improve generation quality"""
    
    def __init__(self, feedback_file: str = "data/feedback/feedback_log.jsonl"):
        self.feedback_file = Path(feedback_file)
        self.feedback_file.parent.mkdir(parents=True, exist_ok=True)
    
    def load_training_data(self) -> List[Dict[str, Any]]:
        """Load all feedback as training data"""
        training_data = []
        
        if not self.feedback_file.exists():
            return training_data
        
        with open(self.feedback_file, "r") as f:
            for line in f:
                if line.strip():
                    training_data.append(json.loads(line))
        
        return training_data
    
    def analyze_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in feedback to improve scoring"""
        feedback_data = self.load_training_data()
        
        if not feedback_data:
            return {
                "message": "No feedback data yet",
                "recommendations": [
                    "Generate and test more test cases",
                    "Collect user feedback",
                    "System will learn and improve"
                ]
            }
        
        # Analyze by scenario type
        by_type = {}
        for entry in feedback_data:
            stype = entry["scenario_type"]
            if stype not in by_type:
                by_type[stype] = {"good": 0, "bad": 0, "total": 0}
            by_type[stype]["total"] += 1
            if entry["user_feedback"] == "good":
                by_type[stype]["good"] += 1
            elif entry["user_feedback"] == "bad":
                by_type[stype]["bad"] += 1
        
        # Calculate success rates
        success_rates = {}
        for stype, stats in by_type.items():
            if stats["total"] > 0:
                success_rates[stype] = round(stats["good"] / stats["total"], 2)
        
        # Find weaknesses
        weaknesses = [stype for stype, rate in success_rates.items() if rate < 0.7]
        strengths = [stype for stype, rate in success_rates.items() if rate > 0.85]
        
        return {
            "total_feedback_entries": len(feedback_data),
            "scenario_success_rates": success_rates,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": [
                f"Improve quality of {', '.join(weaknesses)}" if weaknesses else "All scenario types performing well!",
                f"Continue focusing on {', '.join(strengths)}" if strengths else "",
            ]
        }
    
    def suggest_improvements(self) -> List[str]:
        """Suggest system improvements based on feedback"""
        analysis = self.analyze_patterns()
        
        suggestions = [
            "✅ Collect more feedback to train the system",
            "✅ Focus on low-performing scenario types",
            "✅ Review test cases marked as 'bad'",
        ]
        
        if "weaknesses" in analysis and analysis["weaknesses"]:
            suggestions.append(f"🔴 Improve: {', '.join(analysis['weaknesses'])}")
        
        if "strengths" in analysis and analysis["strengths"]:
            suggestions.append(f"🟢 Maintain: {', '.join(analysis['strengths'])}")
        
        return suggestions


# Demo
if __name__ == "__main__":
    print("📝 FEEDBACK & LEARNING SYSTEM DEMO\n")
    print("=" * 80)
    
    # Create feedback collector
    collector = FeedbackCollector()
    
    # Simulate feedback
    sample_feedbacks = [
        FeedbackEntry(
            test_case_id="TC-HC-001",
            requirement_id="REQ-HC-001",
            scenario_type="happy_path",
            user_feedback="good",
            test_execution_result="pass",
            defects_found=0,
            coverage_rating=5,
            clarity_rating=5,
            effort_accuracy=4,
            rating=5,
            comments="Clear and comprehensive test"
        ),
        FeedbackEntry(
            test_case_id="TC-HC-002",
            requirement_id="REQ-HC-001",
            scenario_type="security",
            user_feedback="good",
            test_execution_result="pass",
            defects_found=1,
            coverage_rating=4,
            clarity_rating=4,
            effort_accuracy=3,
            rating=4,
            comments="Found security issue, good test"
        ),
        FeedbackEntry(
            test_case_id="TC-HC-003",
            requirement_id="REQ-HC-002",
            scenario_type="boundary_value",
            user_feedback="needs_improvement",
            test_execution_result="fail",
            defects_found=0,
            coverage_rating=2,
            clarity_rating=3,
            effort_accuracy=2,
            rating=2,
            comments="Effort estimate was too low"
        ),
    ]
    
    # Submit feedbacks
    print("📥 Submitting feedbacks...\n")
    for feedback in sample_feedbacks:
        collector.submit_feedback(feedback)
    
    # Get stats
    print("\n📊 Feedback Statistics:")
    stats = collector.get_stats()
    for key, value in stats.items():
        if key != "by_scenario_type":
            print(f"   {key}: {value}")
    
    # Analyze patterns
    print("\n🧠 Learning System Analysis:")
    learning = LearningSystem()
    analysis = learning.analyze_patterns()
    
    for key, value in analysis.items():
        if key != "recommendations":
            print(f"   {key}: {value}")
    
    # Suggestions
    print("\n💡 System Improvement Suggestions:")
    suggestions = learning.suggest_improvements()
    for suggestion in suggestions:
        print(f"   {suggestion}")
