"""
🧠 AI Learning System - Maps feedback to learning signals
Implements intelligent test case ranking based on user feedback

Features:
- Convert feedback → learning signals
- Store test case vectors for pattern matching
- Ranking system (Best → Weak)
- Improvement metrics tracking
"""

import json
import hashlib
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Tuple
from pathlib import Path
import statistics
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class LearningSignal:
    """Converts feedback into ML learning signal"""
    feedback_id: str
    test_case_id: str
    test_title: str
    test_type: str
    
    # Feedback converted to signals
    quality_signal: float      # -1.0 (bad) to +1.0 (good)
    clarity_signal: float      # -1.0 to +1.0
    coverage_signal: float     # -1.0 to +1.0
    
    # Pattern vectors (for future ML training)
    pattern_vector: Dict[str, float]  # {pattern_name: score}
    
    # Metadata
    timestamp: str
    confidence: float  # How confident is this signal? 0-1


@dataclass
class TestCaseRanking:
    """Ranking score for a test case"""
    test_id: str
    title: str
    test_type: str
    
    # Ranking components
    quality_score: float        # Original AI quality
    learned_quality: float      # Learned quality from feedback
    feedback_count: int         # How many user feedbacks
    positive_ratio: float       # % positive feedback
    ranking_score: float        # Final ranking (0-1)
    
    # Trend
    improvement_trend: str      # "improving", "stable", "declining"
    last_updated: str


class AILearningSystem:
    """Core AI learning system - converts feedback to learning signals"""
    
    def __init__(self, db_path: str = 'data/learning.db'):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        logger.info(f"✓ AI Learning System initialized ({db_path})")
    
    def _init_db(self):
        """Initialize learning database"""
        conn = sqlite3.connect(str(self.db_path))
        
        # Learning signals table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS learning_signals (
                id INTEGER PRIMARY KEY,
                feedback_id TEXT UNIQUE,
                test_case_id TEXT,
                test_title TEXT,
                test_type TEXT,
                quality_signal REAL,
                clarity_signal REAL,
                coverage_signal REAL,
                pattern_vector TEXT,
                timestamp TEXT,
                confidence REAL
            )
        ''')
        
        # Test case rankings table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS test_rankings (
                test_id TEXT PRIMARY KEY,
                title TEXT,
                test_type TEXT,
                original_quality REAL,
                learned_quality REAL,
                feedback_count INTEGER,
                positive_ratio REAL,
                ranking_score REAL,
                improvement_trend TEXT,
                last_updated TEXT
            )
        ''')
        
        # Pattern frequency table (for pattern recognition)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS pattern_frequency (
                pattern_name TEXT,
                feedback_type TEXT,
                frequency INTEGER,
                success_rate REAL,
                last_seen TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def convert_feedback_to_signal(
        self, 
        feedback_id: str,
        test_case: Dict[str, Any],
        feedback: Dict[str, Any]
    ) -> LearningSignal:
        """
        Convert user feedback into learning signal
        
        Args:
            feedback_id: Unique feedback ID
            test_case: Original generated test case
            feedback: User feedback {rating: 1-5, comment: str, type: 'good'/'bad'}
        
        Returns:
            LearningSignal with converted values
        """
        
        # Map feedback type → quality signal
        feedback_type = feedback.get('type', 'neutral')
        quality_signal = {
            'good': 0.8,
            'bad': -0.8,
            'neutral': 0.0
        }.get(feedback_type, 0.0)
        
        # Extract clarity from comment (if provided)
        comment = feedback.get('comment', '')
        clarity_signal = self._assess_clarity(comment)
        
        # Extract coverage assessment
        coverage_signal = self._assess_coverage(test_case, comment)
        
        # Generate pattern vector from test case
        pattern_vector = self._generate_pattern_vector(test_case)
        
        # Calculate confidence based on feedback detail
        confidence = self._calculate_confidence(feedback)
        
        signal = LearningSignal(
            feedback_id=feedback_id,
            test_case_id=test_case.get('id', 'unknown'),
            test_title=test_case.get('title', 'Untitled'),
            test_type=test_case.get('type', 'functional'),
            quality_signal=quality_signal,
            clarity_signal=clarity_signal,
            coverage_signal=coverage_signal,
            pattern_vector=pattern_vector,
            timestamp=datetime.now().isoformat(),
            confidence=confidence
        )
        
        return signal
    
    def _assess_clarity(self, comment: str) -> float:
        """Assess test clarity from user comment"""
        if not comment:
            return 0.0
        
        comment_lower = comment.lower()
        clarity_keywords = {
            'clear': 0.3,
            'confusing': -0.3,
            'easy': 0.2,
            'hard': -0.2,
            'well-written': 0.4,
            'poorly written': -0.4,
        }
        
        score = 0.0
        for keyword, value in clarity_keywords.items():
            if keyword in comment_lower:
                score += value
        
        return max(-1.0, min(1.0, score))  # Clamp to [-1, 1]
    
    def _assess_coverage(self, test_case: Dict[str, Any], comment: str) -> float:
        """Assess test coverage from case and comment"""
        score = 0.0
        
        # Test type indicates coverage strength
        coverage_weights = {
            'happy_path': 0.3,
            'edge_case': 0.4,
            'error_case': 0.5,
            'security': 0.6,
            'performance': 0.5,
            'boundary': 0.4,
        }
        
        test_type = test_case.get('type', 'functional').lower()
        score += coverage_weights.get(test_type, 0.2)
        
        # Keywords in comment
        if comment:
            comment_lower = comment.lower()
            if 'cover' in comment_lower or 'coverage' in comment_lower:
                score += 0.3
            if 'missing' in comment_lower or 'missing case' in comment_lower:
                score -= 0.3
        
        return max(-1.0, min(1.0, score))
    
    def _generate_pattern_vector(self, test_case: Dict[str, Any]) -> Dict[str, float]:
        """Generate pattern vector from test case for similarity matching"""
        patterns = {}
        
        # Pattern 1: Test type pattern
        test_type = test_case.get('type', 'functional').lower()
        patterns[f'type_{test_type}'] = 1.0
        
        # Pattern 2: Keywords in title/description
        title = (test_case.get('title', '') + ' ' + test_case.get('description', '')).lower()
        keywords = {
            'validation': 'validation' in title,
            'login': 'login' in title or 'authentication' in title,
            'create': 'create' in title,
            'delete': 'delete' in title,
            'update': 'update' in title,
            'boundary': 'boundary' in title or 'limit' in title,
            'performance': 'performance' in title or 'speed' in title,
            'security': 'security' in title or 'injection' in title,
        }
        
        for keyword, present in keywords.items():
            if present:
                patterns[f'keyword_{keyword}'] = 1.0
        
        # Pattern 3: Effort pattern (quick vs heavy)
        effort = test_case.get('estimated_effort_hours', 0.5)
        if effort < 0.25:
            patterns['effort_quick'] = 1.0
        elif effort < 0.5:
            patterns['effort_light'] = 1.0
        elif effort < 1.0:
            patterns['effort_medium'] = 1.0
        elif effort < 2.0:
            patterns['effort_heavy'] = 1.0
        else:
            patterns['effort_epic'] = 1.0
        
        return patterns
    
    def _calculate_confidence(self, feedback: Dict[str, Any]) -> float:
        """Calculate confidence in this feedback signal"""
        confidence = 0.5  # Base confidence
        
        # More detailed feedback = higher confidence
        if feedback.get('comment'):
            confidence += 0.3
        
        if feedback.get('type'):
            confidence += 0.2
        
        return min(1.0, confidence)
    
    def store_learning_signal(self, signal: LearningSignal):
        """Store learning signal to database"""
        conn = sqlite3.connect(str(self.db_path))
        
        try:
            conn.execute('''
                INSERT OR REPLACE INTO learning_signals
                (feedback_id, test_case_id, test_title, test_type, 
                 quality_signal, clarity_signal, coverage_signal, 
                 pattern_vector, timestamp, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal.feedback_id,
                signal.test_case_id,
                signal.test_title,
                signal.test_type,
                signal.quality_signal,
                signal.clarity_signal,
                signal.coverage_signal,
                json.dumps(signal.pattern_vector),
                signal.timestamp,
                signal.confidence
            ))
            
            conn.commit()
            logger.info(f"✓ Learning signal stored: {signal.feedback_id}")
            
        finally:
            conn.close()
    
    def rank_test_cases(self, test_cases: List[Dict[str, Any]]) -> List[TestCaseRanking]:
        """
        Rank test cases based on original quality + learned feedback
        
        Returns:
            Ranked list (best first)
        """
        conn = sqlite3.connect(str(self.db_path))
        
        rankings = []
        for test_case in test_cases:
            test_id = test_case.get('id', 'unknown')
            
            # Get feedback signals for this test
            cursor = conn.execute('''
                SELECT quality_signal, clarity_signal, coverage_signal, confidence
                FROM learning_signals
                WHERE test_case_id = ?
            ''', (test_id,))
            
            signals = cursor.fetchall()
            
            # Calculate learned quality
            if signals:
                # Weighted average of signals
                total_weight = sum(s[3] for s in signals)  # confidence sum
                weighted_sum = sum(s[0] * s[3] for s in signals)  # quality * confidence
                feedback_count = len(signals)
                positive_ratio = sum(1 for s in signals if s[0] > 0) / feedback_count if feedback_count > 0 else 0.5
                
                learned_quality = weighted_sum / total_weight if total_weight > 0 else 0.5
            else:
                learned_quality = 0.5
                feedback_count = 0
                positive_ratio = 0.5
            
            # Combine original + learned quality
            original_quality = test_case.get('quality_score', 0.7)
            combined_quality = (original_quality * 0.5) + (learned_quality * 0.5)
            
            # Determine improvement trend
            improvement_trend = 'stable'
            if learned_quality > original_quality:
                improvement_trend = 'improving'
            elif learned_quality < original_quality:
                improvement_trend = 'declining'
            
            ranking = TestCaseRanking(
                test_id=test_id,
                title=test_case.get('title', 'Untitled'),
                test_type=test_case.get('type', 'functional'),
                quality_score=original_quality,
                learned_quality=learned_quality,
                feedback_count=feedback_count,
                positive_ratio=positive_ratio,
                ranking_score=combined_quality,
                improvement_trend=improvement_trend,
                last_updated=datetime.now().isoformat()
            )
            
            rankings.append(ranking)
        
        conn.close()
        
        # Sort by ranking score (best first)
        rankings.sort(key=lambda x: x.ranking_score, reverse=True)
        
        return rankings
    
    def get_best_test_cases(self, test_cases: List[Dict[str, Any]], top_n: int = 10) -> List[Dict[str, Any]]:
        """Get top N ranked test cases"""
        rankings = self.rank_test_cases(test_cases)
        
        # Map rankings back to original test cases with ranking info
        ranked_test_cases = []
        for ranking in rankings[:top_n]:
            # Find original test case
            original = next((tc for tc in test_cases if tc.get('id') == ranking.test_id), None)
            if original:
                # Add ranking info
                original['ranking'] = asdict(ranking)
                original['badge'] = self._get_badge(ranking.ranking_score)
                ranked_test_cases.append(original)
        
        return ranked_test_cases
    
    def _get_badge(self, score: float) -> str:
        """Get visual badge for ranking score"""
        if score >= 0.9:
            return '⭐⭐⭐ Excellent'
        elif score >= 0.7:
            return '⭐⭐ Good'
        elif score >= 0.5:
            return '⭐ Fair'
        else:
            return '⚠️ Needs Work'
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get overall learning insights"""
        conn = sqlite3.connect(str(self.db_path))
        
        # Total feedback processed
        cursor = conn.execute('SELECT COUNT(*) FROM learning_signals')
        total_signals = cursor.fetchone()[0]
        
        # Average quality improvement
        cursor = conn.execute('''
            SELECT AVG(quality_signal) FROM learning_signals
            WHERE quality_signal > 0
        ''')
        avg_positive = cursor.fetchone()[0] or 0
        
        cursor = conn.execute('''
            SELECT AVG(quality_signal) FROM learning_signals
            WHERE quality_signal < 0
        ''')
        avg_negative = cursor.fetchone()[0] or 0
        
        # Most common patterns
        cursor = conn.execute('''
            SELECT pattern_vector FROM learning_signals
            ORDER BY timestamp DESC
            LIMIT 10
        ''')
        
        pattern_counts = {}
        for row in cursor.fetchall():
            patterns = json.loads(row[0]) if row[0] else {}
            for pattern in patterns.keys():
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        top_patterns = sorted(
            pattern_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        conn.close()
        
        return {
            'total_signals_processed': total_signals,
            'positive_feedback_avg': round(avg_positive, 3),
            'negative_feedback_avg': round(avg_negative, 3),
            'improvement_rate': round((avg_positive + abs(avg_negative)) / 2, 3),
            'top_patterns': top_patterns,
            'learning_maturity': 'beginner' if total_signals < 10 else 'growing' if total_signals < 50 else 'mature'
        }
