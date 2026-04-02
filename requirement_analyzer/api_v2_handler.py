"""
V2 Task Generation Handler
==========================

Integrates V2 Pipeline into FastAPI endpoints.
Provides proper User Stories, Task Decomposition, and Acceptance Criteria.

Features:
- Noise filtering (removes intro/description text)
- Functional vs Non-functional classification
- Proper Agile User Story format
- Task decomposition into subtasks
- Specific Given/When/Then acceptance criteria
- INVEST scoring
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

from requirement_analyzer.task_gen.schemas_v2 import Requirement, RequirementType
from requirement_analyzer.task_gen.pipeline_v2 import V2Pipeline
from requirement_analyzer.task_gen.req_detector import get_detector

logger = logging.getLogger("requirement_analyzer.api_v2")


class V2TaskGenerator:
    """V2 Task generator with full pipeline integration"""
    
    def __init__(self):
        """Initialize V2 task generator"""
        self.pipeline = V2Pipeline()
        self.detector = self._load_detector()
        
    def _load_detector(self):
        """Load requirement detector"""
        try:
            from requirement_analyzer.task_gen.req_detector import get_detector
            return get_detector()
        except Exception as e:
            logger.warning(f"Could not load requirement detector: {e}")
            return None
    
    def generate_from_text(self, text: str, language: str = "vi") -> Dict[str, Any]:
        """
        Generate tasks from requirement text using V2 pipeline
        
        Args:
            text: Requirement text
            language: Text language (vi, en)
            
        Returns:
            Dictionary with tasks, stats, quality metrics, and reasoning
        """
        # Stage 1: Clean & extract requirements
        requirements = self._extract_and_clean_requirements(text, language)
        
        if not requirements:
            return {
                "status": "success",
                "tasks": [],
                "total_tasks": 0,
                "functional_requirements": 0,
                "non_functional_requirements": 0,
                "noise_filtered": 0,
                "message": "No valid requirements found after filtering",
                "reasoning": "Empty input after noise filtering"
            }
        
        # Stage 2: Process through V2 pipeline
        tasks_output = self._process_requirements(requirements)
        
        # Stage 3: Add Explainable AI reasoning
        tasks_output = self._add_explainability(tasks_output)
        
        return tasks_output
    
    def _extract_and_clean_requirements(
        self,
        text: str,
        language: str
    ) -> List[Requirement]:
        """
        Extract and clean requirements from text.
        Filters out noise (intro, descriptions, section headers).
        
        Args:
            text: Raw requirement text
            language: Language code
            
        Returns:
            List of cleaned Requirement objects
        """
        
        # Split into lines
        lines = text.strip().split('\n')
        
        # Filter noise
        filtered_lines = []
        noise_count = 0
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip if it's a noise pattern (intro, headers, descriptions)
            if self._is_noise(line):
                noise_count += 1
                continue
            
            # Skip if too short
            if len(line.split()) < 3:
                noise_count += 1
                continue
            
            filtered_lines.append(line)
        
        logger.info(f"Filtered {noise_count} noise lines, kept {len(filtered_lines)} requirement lines")
        
        # Convert to Requirement objects
        requirements = []
        
        for idx, line in enumerate(filtered_lines, 1):
            try:
                req = Requirement(
                    requirement_id=f"REQ-{idx}",
                    original_text=line,
                    language=language,
                    domain=self._detect_domain(line),
                    confidence=0.8
                )
                requirements.append(req)
            except Exception as e:
                logger.warning(f"Could not create requirement from line '{line[:50]}': {e}")
                continue
        
        return requirements
    
    def _is_noise(self, line: str) -> bool:
        """
        Determine if a line is noise (not a real requirement)
        
        Noise patterns:
        - Intro/header text ("Giới thiệu", "Tài liệu", "Introduction")
        - Module/section headers
        - Numbering only ("2.1", "2.2")
        - Markdown headers
        """
        line_lower = line.lower()
        
        # Intro/description patterns
        noise_patterns = [
            # Vietnamese
            "giới thiệu", "tài liệu", "mô tả", "hướng dẫn",
            "các yêu cầu", "mục đích", "phạm vi", "đối tượng",
            "tổng quan", "cấu trúc", "nội dung",
            # English
            "introduction", "overview", "document", "description",
            "purpose", "scope", "objective", "structure",
            # Generic
            "##", "###", "---", "===", "***",
        ]
        
        for pattern in noise_patterns:
            if pattern in line_lower:
                return True
        
        # Check if line is mostly numbering/headers
        # e.g., "2.1 Module Đăng ký" → keep the actual requirement
        # but "2.1" alone → noise
        if len(line) < 20 and line.replace(".", "").replace(" ", "").isdigit():
            return True
        
        # Check if it ends with colon (section header)
        if line.endswith(":"):
            return True
        
        return False
    
    def _detect_domain(self, requirement_text: str) -> str:
        """Detect domain from requirement text"""
        text_lower = requirement_text.lower()
        
        domains = {
            "Healthcare": ["bệnh viện", "bệnh nhân", "bác sĩ", "y tế", "khám bệnh", "medical", "hospital", "patient"],
            "Hospital/Medicine": ["phẫu thuật", "mổ", "doctor", "physician", "nurse", "điều dưỡng"],
            "Pharmacy": ["thuốc", "nhà thuốc", "pharmacy", "medication"],
            "Laboratory": ["xét nghiệm", "lab", "laboratory", "test"],
            "Payment/Billing": ["viện phí", "thanh toán", "payment", "billing", "invoice", "hóa đơn"],
            "Booking/Reservation": ["đặt", "booking", "reservation", "khách sạn", "hotel"],
            "Hotel": ["khách sạn", "phòng", "hotel", "room"],
        }
        
        for domain, keywords in domains.items():
            if any(kw in text_lower for kw in keywords):
                return domain
        
        return "General"
    
    def _detect_requirement_type(self, requirement_text: str) -> RequirementType:
        """Detect if requirement is functional or non-functional"""
        text_lower = requirement_text.lower()
        
        # NFR patterns
        nfr_keywords = {
            "Performance": ["hiệu suất", "nhanh", "tốc độ", "thời gian phản hồi", "response time", "performance"],
            "Security": ["bảo mật", "mã hóa", "phân quyền", "xác thực", "security", "encryption", "authorization"],
            "Reliability": ["ổn định", "sẵn sàng", "uptime", "không lỗi", "availability", "reliability"],
            "Scalability": ["mở rộng", "scale", "tăng trưởng", "scalability"],
            "Usability": ["dễ dùng", "thân thiện", "trực quan", "usability", "user-friendly"],
            "Maintainability": ["bảo trì", "dễ bảo trì", "maintainability"],
        }
        
        for nfr_type, keywords in nfr_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return RequirementType.NON_FUNCTIONAL
        
        # Functional requirement - default
        return RequirementType.FUNCTIONAL
    
    def _process_requirements(
        self,
        requirements: List[Requirement]
    ) -> Dict[str, Any]:
        """
        Process requirements through V2 pipeline
        
        Args:
            requirements: List of extracted requirements
            
        Returns:
            Formatted task output
        """
        tasks = []
        functional_count = 0
        nfr_count = 0
        
        for requirement in requirements:
            try:
                # Detect requirement type
                req_type = self._detect_requirement_type(requirement.original_text)
                if req_type == RequirementType.NON_FUNCTIONAL:
                    nfr_count += 1
                else:
                    functional_count += 1
                
                # Process through V2 pipeline
                v2_output = self.pipeline.process_single_requirement(requirement)
                
                # Convert V2 output to task format
                task = self._convert_v2_to_task(v2_output)
                tasks.append(task)
                
            except Exception as e:
                logger.error(f"Error processing {requirement.requirement_id}: {e}")
                # Add basic task as fallback
                task = self._create_fallback_task(requirement)
                tasks.append(task)
        
        return {
            "status": "success",
            "tasks": tasks,
            "total_tasks": len(tasks),
            "functional_requirements": functional_count,
            "non_functional_requirements": nfr_count,
            "summary": self._generate_summary(tasks, functional_count, nfr_count)
        }
    
    def _convert_v2_to_task(self, v2_output) -> Dict[str, Any]:
        """
        Convert V2 pipeline output to task format
        
        Args:
            v2_output: RequirementV2Output from pipeline
            
        Returns:
            Task dictionary for frontend
        """
        # Extract refinement (has proper user story and AC)
        refinement = v2_output.refinement
        slicing = v2_output.slicing
        
        # Build user stories from slices and stories
        user_stories = []
        for slice_obj in slicing.slices:
            for story in slice_obj.stories:
                # Get ACs referenced by this story
                story_acs = [
                    ac for ac in refinement.acceptance_criteria
                    if ac.ac_id in story.acceptance_criteria_refs
                ]
                
                us_dict = {
                    "id": story.story_id,
                    "title": story.title,
                    "user_story": story.user_story,  # Proper "As a... I want... So that..."
                    "domain": v2_output.domain,
                    "status": "ready",
                    "story_points": story.invest_score.total // 5 or 3,  # Convert to story points
                    "priority": story.invest_score.valuable and "High" or "Medium",  # Derive from INVEST
                    "acceptance_criteria": [
                        {
                            "id": ac.ac_id,
                            "given": ac.given,
                            "when": ac.when,
                            "then": ac.then,
                            "priority": ac.priority.name
                        }
                        for ac in story_acs
                    ],
                    "subtasks": [
                        {
                            "id": subtask.task_id,
                            "title": subtask.title,
                            "description": subtask.description,
                            "role": subtask.role.name if hasattr(subtask.role, 'name') else str(subtask.role),
                            "priority": subtask.priority,
                            "days_estimated": (subtask.estimate_hours or 8) / 8  # Convert hours to days
                        }
                        for subtask in story.subtasks
                    ],
                    "nfrs": refinement.non_functional_requirements or [],
                    "risk_level": "MEDIUM",  # Default risk
                    "invest_score": {
                        "independent": story.invest_score.independent,
                        "negotiable": story.invest_score.negotiable,
                        "valuable": story.invest_score.valuable,
                        "estimable": story.invest_score.estimable,
                        "small": story.invest_score.small,
                        "testable": story.invest_score.testable,
                        "total": story.invest_score.total
                    }
                }
                user_stories.append(us_dict)
        
        # If no slices, create default task from refinement
        if not user_stories:
            user_stories = [self._create_default_user_story(refinement, v2_output.domain)]
        
        return {
            "requirement_id": v2_output.requirement_id,
            "original_requirement": v2_output.original_requirement,
            "type": refinement.user_story.split()[0] if refinement.user_story else "Feature",
            "domain": v2_output.domain,
            "quality_score": v2_output.quality_metrics.overall_quality if hasattr(v2_output.quality_metrics, 'overall_quality') else 0.5,
            "user_stories": user_stories,
            "gaps": [
                {
                    "id": gap.gap_id,
                    "description": gap.description,
                    "severity": gap.severity.name if hasattr(gap.severity, 'name') else str(gap.severity),
                    "type": gap.type.name if hasattr(gap.type, 'name') else str(gap.type),
                    "question": gap.question,
                    "suggestion": gap.suggestion
                }
                for gap in (v2_output.gap_report.gaps if v2_output.gap_report else [])
            ],
            "traceability": {
                "source": v2_output.traceability.requirement_to_stories[0] if v2_output.traceability else None,
                "coverage": len(user_stories) / max(1, len(user_stories))
            }
        }
    
    def _create_default_user_story(self, refinement, domain: str) -> Dict[str, Any]:
        """Create default user story from refinement"""
        return {
            "id": refinement.requirement_id,
            "title": refinement.title,
            "user_story": refinement.user_story,
            "domain": domain,
            "status": "ready",
            "story_points": 5,
            "priority": "Medium",
            "acceptance_criteria": [
                {
                    "id": ac.ac_id,
                    "given": ac.given,
                    "when": ac.when,
                    "then": ac.then,
                    "priority": ac.priority.name
                }
                for ac in refinement.acceptance_criteria
            ],
            "subtasks": [],
            "nfrs": refinement.non_functional_requirements or [],
            "risk_level": "MEDIUM",
            "invest_score": {
                "independent": True,
                "negotiable": True,
                "valuable": True,
                "estimable": True,
                "small": True,
                "testable": True,
                "total": 25
            }
        }
    
    def _create_fallback_task(self, requirement: Requirement) -> Dict[str, Any]:
        """Create fallback task if pipeline fails"""
        req_type = self._detect_requirement_type(requirement.original_text)
        
        return {
            "requirement_id": requirement.requirement_id,
            "original_requirement": requirement.original_text,
            "type": req_type.name,
            "domain": requirement.domain or "General",
            "quality_score": 0.3,
            "user_stories": [
                {
                    "id": requirement.requirement_id,
                    "title": requirement.original_text[:50],
                    "user_story": requirement.original_text,
                    "domain": requirement.domain or "General",
                    "story_points": 5,
                    "priority": "Medium",
                    "subtasks": [],
                    "acceptance_criteria": []
                }
            ],
            "gaps": [],
            "error": "Failed to fully process through V2 pipeline"
        }
    
    def _add_explainability(self, tasks_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add explainability/reasoning to output (XAI - Explainable AI)
        
        Helps defend decisions:
        - Why decompose into 5 stories?
        - Why classify as NFR?
        - Why flag as gap?
        """
        tasks = tasks_output.get("tasks", [])
        
        # Add explanation for each task
        for task in tasks:
            # Explain why decomposed
            num_stories = len(task.get("user_stories", []))
            if num_stories > 1:
                task["decomposition_reasoning"] = self._explain_decomposition(
                    task.get("original_requirement", ""),
                    num_stories
                )
            
            # Explain gaps
            gaps = task.get("gaps", [])
            for gap in gaps:
                gap["reasoning"] = self._explain_gap(gap)
            
            # Add user story reasoning
            for story in task.get("user_stories", []):
                story["why_this_story"] = self._explain_user_story_purpose(story)
        
        # Add overall methodology explanation
        tasks_output["methodology"] = {
            "approach": "V2 Agile Requirements Pipeline",
            "stages": [
                "Stage 1: Requirement Refinement (Vietnamese → Clean Agile Format)",
                "Stage 2: Gap Analysis (Missing requirements detection)",
                "Stage 3: Smart Decomposition (Requirements → User Stories → Tasks)",
                "Stage 4: Quality Evaluation (INVEST scoring)"
            ],
            "rationale": "Simulates AI-powered Agile workflow for better requirements engineering"
        }
        
        return tasks_output
    
    def _explain_decomposition(self, requirement: str, num_stories: int) -> Dict[str, str]:
        """Explain why requirement was decomposed into multiple stories"""
        text_lower = requirement.lower()
        
        reasons = []
        
        # Check for workflow complexity
        if any(kw in text_lower for kw in ["phải", "quản lý", "thực hiện"]):
            reasons.append("happy_path: Happy path scenario")
        
        # Check for edge cases
        if any(kw in text_lower for kw in ["lỗi", "ngoại lệ", "validate", "validation"]):
            reasons.append("edge_cases: Edge case handling")
        
        # Check for security/permissions
        if any(kw in text_lower for kw in ["bảo mật", "phân quyền", "admin", "role"]):
            reasons.append("security: Security & permissions")
        
        # Check for performance/data
        if any(kw in text_lower for kw in ["lưu", "lưu trữ", "xử lý", "dữ liệu"]):
            reasons.append("persistence: Data persistence & integration")
        
        # Check for performance/scalability
        if any(kw in text_lower for kw in ["500", "nhanh", "hiệu suất", "concurrent"]):
            reasons.append("performance: Performance & scalability")
        
        if not reasons:
            reasons = [
                "happy_path: Happy path scenario",
                "edge_cases: Edge case handling",
                "security: Security considerations",
                "persistence: Data handling",
                "performance: Performance optimization"
            ]
        
        return {
            "summary": f"Decomposed into {num_stories} stories to address multiple aspects",
            "aspects": reasons[:num_stories],
            "agile_principle": "Stories should be independent and handle different user perspectives"
        }
    
    def _explain_user_story_purpose(self, story: Dict) -> str:
        """Explain the purpose of each user story"""
        title = story.get("title", "").lower()
        
        if "happy" in title or "path" in title:
            return "Covers the main success scenario with proper data flow"
        elif "edge" in title or "exception" in title:
            return "Handles error conditions and edge cases"
        elif "permission" in title or "security" in title or "access" in title:
            return "Ensures proper access control and security requirements"
        elif "persist" in title or "data" in title or "integration" in title:
            return "Manages data storage, retrieval, and system integration"
        elif "performance" in title or "load" in title or "scale" in title:
            return "Ensures system meets performance and scalability requirements"
        else:
            return "Addresses a specific aspect of the requirement"
    
    def _explain_gap(self, gap: Dict) -> Dict[str, str]:
        """Explain why something is detected as a gap"""
        gap_type = gap.get("type", "unknown").lower()
        
        explanations = {
            "missing_actor": "Requirement doesn't specify WHO uses the feature",
            "missing_permission": "No clarity on access control requirements",
            "missing_validation": "No validation rules or constraints defined",
            "missing_error_handling": "Error scenarios not addressed",
            "missing_nfr": "Non-functional requirements (performance, security) missing",
            "missing_security": "Security considerations not mentioned",
            "contradiction": "Conflicting requirements detected",
            "ambiguity": "Requirement wording is unclear or ambiguous"
        }
        
        return {
            "why_its_a_gap": explanations.get(gap_type, "Requirement aspect needs clarification"),
            "detection_method": "Rule-based pattern matching + semantic analysis",
            "severity_explanation": f"{gap.get('severity', 'MEDIUM')} impact on system design"
        }
    
    def _generate_summary(
        self,
        tasks: List[Dict],
        functional_count: int,
        nfr_count: int
    ) -> Dict[str, Any]:
        """Generate summary statistics"""
        total_stories = sum(len(t.get("user_stories", [])) for t in tasks)
        total_subtasks = sum(
            sum(len(s.get("subtasks", [])) for s in t.get("user_stories", []))
            for t in tasks
        )
        
        return {
            "total_requirements": len(tasks),
            "functional_requirements": functional_count,
            "non_functional_requirements": nfr_count,
            "total_user_stories": total_stories,
            "total_subtasks": total_subtasks,
            "average_quality_score": sum(t.get("quality_score", 0.5) for t in tasks) / len(tasks) if tasks else 0
        }
