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
# Vietnamese diacritics for language detection
VI_DIACRITICS = set("ăâđêôơưáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ")
VI_KEYWORDS = {'hệ thống', 'phải', 'cần', 'cho phép', 'đảm bảo', 'thực hiện', 'người dùng'}

def is_vietnamese(text: str) -> bool:
    """Detect if text is Vietnamese"""
    if not text:
        return False
    text_lower = text.lower()
    # Check for diacritics
    has_diacritics = any(ch in VI_DIACRITICS for ch in text)
    # Check for Vietnamese keywords
    has_keywords = any(kw in text_lower for kw in VI_KEYWORDS)
    return has_diacritics or has_keywords

class TaskPostProcessor:
    """Post-process generated tasks"""
    
    def __init__(
        self,
        similarity_threshold: float = 0.85,
        min_task_length: int = 10
    ):
        self.similarity_threshold = similarity_threshold
        self.min_task_length = min_task_length
        # Use char n-gram for multilingual dedup (Vietnamese + English)
        # Analyzer='char_wb' works better than word-based for Vietnamese
        self.vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), max_features=2000)
    
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
        """Check if task should be split into implementation subtasks"""
        # Always split functional requirements into Backend/Frontend/Test subtasks
        # This increases task count 3x for better backlog granularity
        if task.type == 'functional':
            # Split if title suggests UI + backend work
            title_lower = task.title.lower()
            
            # Vietnamese keywords for complex features
            vn_ui_keywords = ['giao diện', 'hiển thị', 'cho phép', 'nhập', 'form', 'màn hình']
            vn_backend_keywords = ['hệ thống', 'xử lý', 'lưu trữ', 'quản lý', 'tính toán', 'kiểm tra']
            
            # English keywords
            en_ui_keywords = ['display', 'show', 'form', 'input', 'ui', 'interface', 'view']
            en_backend_keywords = ['system', 'process', 'store', 'manage', 'calculate', 'validate']
            
            # Check if task involves both UI and backend
            is_vn = is_vietnamese(task.title)
            if is_vn:
                has_ui = any(kw in title_lower for kw in vn_ui_keywords)
                has_backend = any(kw in title_lower for kw in vn_backend_keywords)
            else:
                has_ui = any(kw in title_lower for kw in en_ui_keywords)
                has_backend = any(kw in title_lower for kw in en_backend_keywords)
            
            # Split if it's a medium-high priority functional task (worth breaking down)
            if task.priority in ['Medium', 'High'] and len(task.title) > 20:
                return True
            
            # Split if clearly involves multiple layers
            if has_ui or has_backend:
                return True
        
        # Check for multiple "and" in title
        and_count = task.title.lower().count(' and ') + task.title.lower().count(' và ')
        if and_count >= 2:
            return True
        
        # Check for very long description
        if len(task.description) > 500:
            return True
        
        return False
    
    def _split_task(self, task: GeneratedTask) -> List[GeneratedTask]:
        """Split a complex task into implementation subtasks (Backend, Frontend, Testing)"""
        is_vn = is_vietnamese(task.title)
        
        # Generate 3 subtasks for each functional requirement
        subtasks = []
        
        # 1. Backend Implementation Task
        backend_title = self._generate_subtask_title(task.title, 'backend', is_vn)
        backend_desc = self._generate_subtask_description(task.description, 'backend', is_vn)
        backend_ac = self._generate_subtask_ac(task.acceptance_criteria, 'backend', is_vn)
        
        backend_task = GeneratedTask(
            epic=task.epic,
            module=task.module,
            title=backend_title,
            description=backend_desc,
            acceptance_criteria=backend_ac,
            type='functional',
            priority=task.priority,
            domain=task.domain,
            role='Backend',
            confidence=task.confidence,
            source=task.source
        )
        subtasks.append(backend_task)
        
        # 2. Frontend Implementation Task
        frontend_title = self._generate_subtask_title(task.title, 'frontend', is_vn)
        frontend_desc = self._generate_subtask_description(task.description, 'frontend', is_vn)
        frontend_ac = self._generate_subtask_ac(task.acceptance_criteria, 'frontend', is_vn)
        
        frontend_task = GeneratedTask(
            epic=task.epic,
            module=task.module,
            title=frontend_title,
            description=frontend_desc,
            acceptance_criteria=frontend_ac,
            type='functional',
            priority=task.priority if task.priority == 'High' else 'Medium',  # Lower priority slightly
            domain=task.domain,
            role='Frontend',
            confidence=task.confidence,
            source=task.source
        )
        subtasks.append(frontend_task)
        
        # 3. Testing Task
        test_title = self._generate_subtask_title(task.title, 'testing', is_vn)
        test_desc = self._generate_subtask_description(task.description, 'testing', is_vn)
        test_ac = self._generate_subtask_ac(task.acceptance_criteria, 'testing', is_vn)
        
        test_task = GeneratedTask(
            epic=task.epic,
            module=task.module,
            title=test_title,
            description=test_desc,
            acceptance_criteria=test_ac,
            type='testing',
            priority='Medium',  # Testing usually medium priority
            domain=task.domain,
            role='QA',
            confidence=task.confidence * 0.95,
            source=task.source
        )
        subtasks.append(test_task)
        
        logger.debug(f"Split '{task.title[:50]}...' into {len(subtasks)} subtasks (Backend/Frontend/Testing)")
        return subtasks
    
    def _generate_subtask_title(self, original_title: str, task_type: str, is_vietnamese: bool) -> str:
        """Generate subtask title based on type"""
        # Clean up original title
        title = original_title[:80] if len(original_title) > 80 else original_title
        
        if is_vietnamese:
            prefixes = {
                'backend': '[Backend] API - ',
                'frontend': '[Frontend] UI - ',
                'testing': '[Testing] Kiểm thử - '
            }
        else:
            prefixes = {
                'backend': '[Backend] API - ',
                'frontend': '[Frontend] UI - ',
                'testing': '[Testing] Test - '
            }
        
        return prefixes.get(task_type, '') + title
    
    def _generate_subtask_description(self, original_desc: str, task_type: str, is_vietnamese: bool) -> str:
        """Generate subtask description based on type"""
        if is_vietnamese:
            templates = {
                'backend': f"Xây dựng API backend cho chức năng này.\n\nYêu cầu gốc: {original_desc[:200]}...",
                'frontend': f"Xây dựng giao diện người dùng cho chức năng này.\n\nYêu cầu gốc: {original_desc[:200]}...",
                'testing': f"Viết test cases và kiểm thử chức năng này.\n\nYêu cầu gốc: {original_desc[:200]}..."
            }
        else:
            templates = {
                'backend': f"Implement backend API for this feature.\n\nOriginal requirement: {original_desc[:200]}...",
                'frontend': f"Implement frontend UI for this feature.\n\nOriginal requirement: {original_desc[:200]}...",
                'testing': f"Write test cases and validate this feature.\n\nOriginal requirement: {original_desc[:200]}..."
            }
        
        return templates.get(task_type, original_desc)
    
    def _generate_subtask_ac(self, original_ac: List[str], task_type: str, is_vietnamese: bool) -> List[str]:
        """Generate acceptance criteria based on subtask type"""
        if is_vietnamese:
            ac_templates = {
                'backend': [
                    'API endpoint được implement đầy đủ',
                    'Input validation hoạt động chính xác',
                    'Error handling đúng theo spec',
                    'Unit tests đạt coverage >= 80%'
                ],
                'frontend': [
                    'UI components được implement theo design',
                    'Form validation hoạt động đúng',
                    'Responsive trên mobile và desktop',
                    'Accessibility standards được đáp ứng'
                ],
                'testing': [
                    'Test cases cover tất cả scenarios chính',
                    'Integration tests pass',
                    'Bug regression tests được thêm',
                    'Test documentation đầy đủ'
                ]
            }
        else:
            ac_templates = {
                'backend': [
                    'API endpoint fully implemented',
                    'Input validation works correctly',
                    'Error handling follows spec',
                    'Unit tests achieve >= 80% coverage'
                ],
                'frontend': [
                    'UI components match design',
                    'Form validation works properly',
                    'Responsive on mobile and desktop',
                    'Accessibility standards met'
                ],
                'testing': [
                    'Test cases cover main scenarios',
                    'Integration tests pass',
                    'Bug regression tests added',
                    'Test documentation complete'
                ]
            }
        
        return ac_templates.get(task_type, original_ac[:3])
    
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
    
    def filter_low_quality(self, tasks: List[GeneratedTask], enable_quality_filter: bool = True) -> List[GeneratedTask]:
        """Filter out low-quality tasks (Vietnamese-aware)"""
        if not enable_quality_filter:
            logger.info("Quality filter disabled, keeping all tasks")
            return tasks
        
        filtered = []
        
        for task in tasks:
            # Detect if task is Vietnamese
            task_text = f"{task.title} {task.description}"
            is_vn = is_vietnamese(task_text)
            
            # Filter WCAG criteria from non-interface tasks
            if task.type.lower() != 'interface':
                original_count = len(task.acceptance_criteria)
                task.acceptance_criteria = [
                    ac for ac in task.acceptance_criteria 
                    if 'WCAG' not in ac and 'accessibility' not in ac.lower()
                ]
                if len(task.acceptance_criteria) < original_count:
                    logger.debug(f"Removed {original_count - len(task.acceptance_criteria)} WCAG criteria from {task.type} task")
            
            # Vietnamese: more lenient filtering
            if is_vn:
                # Only filter if title is empty or too short (< 3 words)
                if not task.title or len(task.title.split()) < 3:
                    logger.debug(f"Filtered out too short Vietnamese title: '{task.title}'")
                    continue
                # Lower confidence threshold for VN (models trained on English)
                if task.confidence < 0.15:
                    logger.debug(f"Filtered out very low confidence VN task: '{task.title}' (conf={task.confidence:.2f})")
                    continue
            else:
                # English: standard filtering
                # Check minimum length
                if len(task.title) < self.min_task_length:
                    logger.debug(f"Filtered out short title: '{task.title}'")
                    continue
                
                # Check confidence threshold
                if task.confidence < 0.3:
                    logger.debug(f"Filtered out low confidence task: '{task.title}' (conf={task.confidence:.2f})")
                    continue
            
            # Check for placeholder text (both EN and VN)
            if 'unknown' in task.title.lower() or 'unknown' in task.description.lower():
                logger.debug(f"Filtered out placeholder task: '{task.title}'")
                continue
            
            filtered.append(task)
        
        logger.info(f"Filtered {len(tasks) - len(filtered)} low-quality tasks")
        
        return filtered
    
    def process(self, tasks: List[GeneratedTask], enable_quality_filter: bool = True, enable_deduplication: bool = True) -> List[GeneratedTask]:
        """
        Run full post-processing pipeline
        
        1. Filter low quality
        2. Deduplicate exact matches
        3. Split complex tasks
        4. Merge related tasks
        """
        logger.info(f"Post-processing {len(tasks)} tasks...")
        
        # 1. Filter
        tasks = self.filter_low_quality(tasks, enable_quality_filter=enable_quality_filter)
        
        # 2. Deduplicate
        if enable_deduplication:
            tasks = self.deduplicate(tasks)
        else:
            logger.info("Deduplication disabled")
        
        # 3. Split functional tasks into Backend/Frontend/Testing subtasks (increases task count 3x)
        logger.info(f"Splitting {len(tasks)} complex tasks into implementation subtasks...")
        tasks = self.split_complex_tasks(tasks)
        logger.info(f"After splitting: {len(tasks)} tasks")
        
        # 4. Merge (optional - reduces task count, disabled for now to maximize task generation)
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
