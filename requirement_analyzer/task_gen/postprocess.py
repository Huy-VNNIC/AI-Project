"""
Post-processing utilities for generated tasks
- Deduplication
- Task splitting (when one requirement has multiple tasks)
- Task merging (when multiple requirements describe same task)
"""
from typing import List, Set
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging

from .schemas import GeneratedTask

logger = logging.getLogger(__name__)


class TaskPostProcessor:
    """Post-process generated tasks"""
    
    def __init__(
        self,
        similarity_threshold: float = 0.85,
        min_task_length: int = 10
    ):
        self.similarity_threshold = similarity_threshold
        self.min_task_length = min_task_length
        self.vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
    
    def deduplicate(self, tasks: List[GeneratedTask]) -> List[GeneratedTask]:
        """
        Remove duplicate tasks based on text similarity
        Also clean up each task's AC and title
        
        Uses TF-IDF cosine similarity on titles + descriptions
        """
        if len(tasks) <= 1:
            return tasks
        
        logger.info(f"Deduplicating {len(tasks)} tasks (with quality cleanup)...")
        
        # First pass: clean each task internally
        cleaned_tasks = []
        for task in tasks:
            # Dedupe acceptance criteria within task
            unique_ac = self._dedupe_list(task.acceptance_criteria)
            task.acceptance_criteria = unique_ac
            
            # Basic title validation
            if self._is_low_quality_title(task.title):
                logger.debug(f"Low quality title detected: {task.title}")
            
            cleaned_tasks.append(task)
        
        # Second pass: dedupe across tasks
        texts = [f"{task.title} {task.description}" for task in cleaned_tasks]
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            similarity_matrix = cosine_similarity(tfidf_matrix)
        except Exception as e:
            logger.warning(f"Error computing similarity: {e}")
            return cleaned_tasks
        
        # Find duplicates
        to_remove = set()
        
        for i in range(len(tasks)):
            if i in to_remove:
                continue
            
            for j in range(i + 1, len(tasks)):
                if j in to_remove:
                    continue
                
                if similarity_matrix[i, j] >= self.similarity_threshold:
                    # Keep the one with higher confidence
                    if tasks[i].confidence >= tasks[j].confidence:
                        to_remove.add(j)
                    else:
                        to_remove.add(i)
                        break
        
        # Filter out duplicates
        unique_tasks = [task for idx, task in enumerate(tasks) if idx not in to_remove]
        
        logger.info(f"Removed {len(to_remove)} duplicate tasks, {len(unique_tasks)} remaining")
        
        return unique_tasks
    
    def split_complex_tasks(self, tasks: List[GeneratedTask]) -> List[GeneratedTask]:
        """
        Split tasks that contain multiple independent actions
        
        Looks for:
        - "and" conjunctions
        - Multiple acceptance criteria that are independent
        - Very long descriptions
        """
        result_tasks = []
        
        for task in tasks:
            # Check if task should be split
            if self._should_split(task):
                split_tasks = self._split_task(task)
                result_tasks.extend(split_tasks)
                logger.debug(f"Split task '{task.title}' into {len(split_tasks)} subtasks")
            else:
                result_tasks.append(task)
        
        return result_tasks
    
    def _should_split(self, task: GeneratedTask) -> bool:
        """Check if task should be split"""
        # Check for multiple "and" in title
        and_count = task.title.lower().count(' and ')
        if and_count >= 2:
            return True
        
        # Check for very long description
        if len(task.description) > 500:
            return True
        
        # Check for many acceptance criteria (might indicate multiple tasks)
        if len(task.acceptance_criteria) > 10:
            return True
        
        return False
    
    def _split_task(self, task: GeneratedTask) -> List[GeneratedTask]:
        """Split a complex task into subtasks"""
        # Simple heuristic: split on "and" in title
        title_parts = re.split(r'\s+and\s+', task.title, flags=re.IGNORECASE)
        
        if len(title_parts) <= 1:
            return [task]
        
        subtasks = []
        ac_per_subtask = max(1, len(task.acceptance_criteria) // len(title_parts))
        
        for idx, title_part in enumerate(title_parts[:3]):  # max 3 splits
            # Create subtask
            subtask = GeneratedTask(
                epic=task.epic,
                module=task.module,
                title=title_part.strip(),
                description=f"{task.description}\n\n**Note**: This is part {idx+1} of {len(title_parts)} related tasks.",
                acceptance_criteria=task.acceptance_criteria[idx*ac_per_subtask:(idx+1)*ac_per_subtask] or ['Functionality works as expected'],
                type=task.type,
                priority=task.priority,
                domain=task.domain,
                role=task.role,
                confidence=task.confidence * 0.9,  # slightly lower confidence for splits
                source=task.source
            )
            subtasks.append(subtask)
        
        return subtasks
    
    def merge_related_tasks(self, tasks: List[GeneratedTask]) -> List[GeneratedTask]:
        """
        Merge tasks that are very similar but from different sentences
        
        More aggressive than deduplicate - looks for complementary tasks
        """
        if len(tasks) <= 1:
            return tasks
        
        logger.info(f"Checking for mergeable tasks in {len(tasks)} tasks...")
        
        # Group by (type, role, domain) first
        groups = {}
        for task in tasks:
            key = (task.type, task.role, task.domain)
            if key not in groups:
                groups[key] = []
            groups[key].append(task)
        
        result_tasks = []
        
        for key, group_tasks in groups.items():
            if len(group_tasks) == 1:
                result_tasks.extend(group_tasks)
                continue
            
            # Check for mergeable pairs within group
            merged = self._merge_group(group_tasks)
            result_tasks.extend(merged)
        
        logger.info(f"After merging: {len(result_tasks)} tasks")
        
        return result_tasks
    
    def _merge_group(self, tasks: List[GeneratedTask]) -> List[GeneratedTask]:
        """Merge tasks within a group"""
        if len(tasks) <= 1:
            return tasks
        
        # Compute pairwise similarity
        texts = [f"{task.title} {task.description}" for task in tasks]
        
        try:
            tfidf_matrix = self.vectorizer.transform(texts)
            similarity_matrix = cosine_similarity(tfidf_matrix)
        except:
            return tasks
        
        # Find highly similar pairs (0.7 - 0.84 range, not quite duplicates)
        merge_threshold = 0.70
        merged_indices = set()
        result = []
        
        for i in range(len(tasks)):
            if i in merged_indices:
                continue
            
            # Find similar tasks to merge with
            similar = []
            for j in range(i + 1, len(tasks)):
                if j in merged_indices:
                    continue
                
                sim = similarity_matrix[i, j]
                if merge_threshold <= sim < self.similarity_threshold:
                    similar.append(j)
            
            if similar:
                # Merge tasks i with similar tasks
                merged_task = self._merge_tasks([tasks[i]] + [tasks[j] for j in similar])
                result.append(merged_task)
                merged_indices.add(i)
                merged_indices.update(similar)
            else:
                result.append(tasks[i])
                merged_indices.add(i)
        
        return result
    
    def _merge_tasks(self, tasks: List[GeneratedTask]) -> GeneratedTask:
        """Merge multiple tasks into one"""
        # Use first task as base
        base = tasks[0]
        
        # Combine acceptance criteria
        all_ac = []
        seen_ac = set()
        
        for task in tasks:
            for ac in task.acceptance_criteria:
                ac_lower = ac.lower()
                if ac_lower not in seen_ac:
                    all_ac.append(ac)
                    seen_ac.add(ac_lower)
        
        # Enhanced description
        description = base.description
        if len(tasks) > 1:
            description += f"\n\n**Note**: This task consolidates {len(tasks)} related requirements."
        
        # Merged task
        merged = GeneratedTask(
            epic=base.epic,
            module=base.module,
            title=base.title,
            description=description,
            acceptance_criteria=all_ac[:10],  # limit
            type=base.type,
            priority=self._merge_priority([t.priority for t in tasks]),
            domain=base.domain,
            role=base.role,
            confidence=np.mean([t.confidence for t in tasks]),
            source=base.source
        )
        
        return merged
    
    def _merge_priority(self, priorities: List[str]) -> str:
        """Merge priorities - take highest"""
        priority_order = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}
        
        max_priority = 'Medium'
        max_value = 0
        
        for p in priorities:
            value = priority_order.get(p, 2)
            if value > max_value:
                max_value = value
                max_priority = p
        
        return max_priority
    
    def filter_low_quality(self, tasks: List[GeneratedTask]) -> List[GeneratedTask]:
        """Filter out low-quality tasks"""
        filtered = []
        
        for task in tasks:
            # Check minimum length
            if len(task.title) < self.min_task_length:
                logger.debug(f"Filtered out short title: '{task.title}'")
                continue
            
            # Check confidence threshold
            if task.confidence < 0.3:
                logger.debug(f"Filtered out low confidence task: '{task.title}' (conf={task.confidence:.2f})")
                continue
            
            # Check for placeholder text
            if 'unknown' in task.title.lower() or 'unknown' in task.description.lower():
                logger.debug(f"Filtered out placeholder task: '{task.title}'")
                continue
            
            filtered.append(task)
        
        logger.info(f"Filtered {len(tasks) - len(filtered)} low-quality tasks")
        
        return filtered
    
    def process(self, tasks: List[GeneratedTask]) -> List[GeneratedTask]:
        """
        Run full post-processing pipeline
        
        1. Filter low quality
        2. Deduplicate exact matches
        3. Split complex tasks
        4. Merge related tasks
        """
        logger.info(f"Post-processing {len(tasks)} tasks...")
        
        # 1. Filter
        tasks = self.filter_low_quality(tasks)
        
        # 2. Deduplicate
        tasks = self.deduplicate(tasks)
        
        # 3. Split (optional - can create more tasks)
        # tasks = self.split_complex_tasks(tasks)
        
        # 4. Merge (optional - reduces task count)
        # tasks = self.merge_related_tasks(tasks)
        
        logger.info(f"Post-processing complete: {len(tasks)} final tasks")
        
        return tasks
    
    def _dedupe_list(self, items: List[str]) -> List[str]:
        """Remove duplicates from list while preserving order"""
        seen = set()
        result = []
        for item in items:
            normalized = item.lower().strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                result.append(item)
        return result
    
    def _is_low_quality_title(self, title: str) -> bool:
        """Check if title has quality issues"""
        if not title or len(title) < 5:
            return True
        
        # Check for repeated words
        words = title.lower().split()
        if len(words) >= 2 and words[0] == words[1]:
            return True
        
        # Ultra short or generic
        generic_patterns = [
            r'^(implement|add|build)\s*$',
            r'^(system|feature)\s*$'
        ]
        
        for pattern in generic_patterns:
            if re.match(pattern, title, re.IGNORECASE):
                return True
        
        return False


# Singleton
_postprocessor = None

def get_postprocessor(
    similarity_threshold: float = 0.85,
    min_task_length: int = 10
) -> TaskPostProcessor:
    """Get singleton postprocessor"""
    global _postprocessor
    if _postprocessor is None:
        _postprocessor = TaskPostProcessor(similarity_threshold, min_task_length)
    return _postprocessor
