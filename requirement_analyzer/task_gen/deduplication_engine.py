"""
Test Case Deduplication Engine
Removes duplicate/similar test cases intelligently
"""

from typing import List, Dict, Any, Set, Tuple
from difflib import SequenceMatcher
import json


class TestCaseDeduplicator:
    """
    Removes duplicate and near-duplicate test cases
    Uses semantic similarity instead of just string matching
    """
    
    def __init__(self, similarity_threshold: float = 0.85):
        """
        Args:
            similarity_threshold: If similarity > this, consider duplicate (0.0-1.0)
                                 Default 0.85 = 85% similar
        """
        self.similarity_threshold = similarity_threshold
    
    def deduplicate(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicates from test case list
        
        Args:
            test_cases: List of test case dicts
            
        Returns:
            Deduplicated list (keeps first occurrence, removes later duplicates)
        """
        if not test_cases:
            return []
        
        # Track which indices to keep
        keep_indices: Set[int] = set()
        keep_indices.add(0)  # Always keep first
        
        # Compare each test case to previous kept ones
        for i in range(1, len(test_cases)):
            current_tc = test_cases[i]
            is_duplicate = False
            
            # Check against all kept ones
            for j in keep_indices:
                kept_tc = test_cases[j]
                
                # Calculate similarity
                similarity = self._calculate_similarity(current_tc, kept_tc)
                
                if similarity > self.similarity_threshold:
                    # This is a duplicate of kept_tc[j]
                    is_duplicate = True
                    print(f"   ⚠️  Removing duplicate: {current_tc.get('test_id', 'N/A')} "
                          f"(similar to {kept_tc.get('test_id', 'N/A')}, {similarity:.2f})")
                    break
            
            if not is_duplicate:
                keep_indices.add(i)
        
        # Return only kept test cases
        result = [test_cases[i] for i in sorted(keep_indices)]
        removed = len(test_cases) - len(result)
        
        if removed > 0:
            print(f"\n✅ Deduplication: Removed {removed} duplicates, "
                  f"kept {len(result)}/{len(test_cases)} unique tests")
        
        return result
    
    def _calculate_similarity(self, tc1: Dict[str, Any], tc2: Dict[str, Any]) -> float:
        """
        Calculate semantic similarity between two test cases
        Considers: title, description, steps, expected_result
        
        Returns: Similarity score 0.0-1.0
        """
        similarities = []
        
        # Compare titles
        title1 = str(tc1.get("title", "")).lower()
        title2 = str(tc2.get("title", "")).lower()
        title_sim = self._string_similarity(title1, title2)
        similarities.append(title_sim * 0.4)  # 40% weight
        
        # Compare descriptions
        desc1 = str(tc1.get("description", "")).lower()
        desc2 = str(tc2.get("description", "")).lower()
        desc_sim = self._string_similarity(desc1, desc2)
        similarities.append(desc_sim * 0.3)  # 30% weight
        
        # Compare test types
        type1 = str(tc1.get("test_type", "")).lower()
        type2 = str(tc2.get("test_type", "")).lower()
        type_sim = 1.0 if type1 == type2 else 0.0
        similarities.append(type_sim * 0.15)  # 15% weight
        
        # Compare steps (most important for functionality)
        steps1 = tc1.get("steps", [])
        steps2 = tc2.get("steps", [])
        steps_sim = self._steps_similarity(steps1, steps2)
        similarities.append(steps_sim * 0.15)  # 15% weight
        
        # Overall similarity (weighted average)
        overall = sum(similarities)
        return overall
    
    @staticmethod
    def _string_similarity(str1: str, str2: str) -> float:
        """Calculate string similarity using SequenceMatcher (0.0-1.0)"""
        if not str1 or not str2:
            return 0.0
        
        matcher = SequenceMatcher(None, str1, str2)
        return matcher.ratio()
    
    @staticmethod
    def _steps_similarity(steps1: List[str], steps2: List[str]) -> float:
        """Calculate similarity between test step lists"""
        if not steps1 or not steps2:
            return 0.0
        
        # If different number of steps, probably different tests
        if len(steps1) != len(steps2):
            return 0.0
        
        # Compare each step
        similarities = []
        for s1, s2 in zip(steps1, steps2):
            sim = SequenceMatcher(None, s1.lower(), s2.lower()).ratio()
            similarities.append(sim)
        
        # Average similarity
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def get_duplicate_groups(self, test_cases: List[Dict[str, Any]]) -> List[List[int]]:
        """
        Group similar test cases together
        Useful for analysis/reporting
        
        Returns:
            List of groups, where each group is indices of similar tests
        """
        groups = []
        used = set()
        
        for i in range(len(test_cases)):
            if i in used:
                continue
            
            group = [i]
            used.add(i)
            
            # Find all similar tests
            for j in range(i + 1, len(test_cases)):
                if j in used:
                    continue
                
                similarity = self._calculate_similarity(test_cases[i], test_cases[j])
                if similarity > self.similarity_threshold:
                    group.append(j)
                    used.add(j)
            
            if len(group) > 1:  # Only track duplicates
                groups.append(group)
        
        return groups
    
    def report_duplicates(self, test_cases: List[Dict[str, Any]]) -> str:
        """Generate human-readable duplicate report"""
        groups = self.get_duplicate_groups(test_cases)
        
        if not groups:
            return "✅ No duplicates detected!"
        
        report = f"⚠️  Found {len(groups)} duplicate groups:\n\n"
        
        for group_idx, group in enumerate(groups, 1):
            report += f"Group {group_idx}:\n"
            for idx in group:
                tc = test_cases[idx]
                report += f"  - {tc.get('test_id', 'N/A')}: {tc.get('title', 'N/A')[:60]}\n"
            report += "\n"
        
        return report


class TestCaseNormalizer:
    """
    Normalize test cases before comparison
    (e.g., normalize whitespace, capitalization, wording variants)
    """
    
    @staticmethod
    def normalize(test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize a test case for comparison"""
        normalized = test_case.copy()
        
        # Normalize text fields
        for key in ["title", "description", "expected_result"]:
            if key in normalized:
                normalized[key] = TestCaseNormalizer._normalize_text(normalized[key])
        
        # Normalize steps
        if "steps" in normalized:
            normalized["steps"] = [
                TestCaseNormalizer._normalize_text(step)
                for step in normalized["steps"]
            ]
        
        return normalized
    
    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize text: whitespace, lowercase, punctuation"""
        if not isinstance(text, str):
            return text
        
        # Lowercase
        text = text.lower()
        
        # Normalize whitespace
        text = " ".join(text.split())
        
        # Remove trailing punctuation
        text = text.rstrip(".,!?;:")
        
        return text
