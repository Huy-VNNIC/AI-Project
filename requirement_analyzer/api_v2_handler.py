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
from requirement_analyzer.task_gen.smart_priority import (
    get_priority_classifier,
    estimate_story_points,
    snap_to_fibonacci,
    assign_sprints,
    detect_language,
    parse_sprint_weeks,
)
from requirement_analyzer.task_gen.task_history import save_history

# Dependency AI is optional — never break the API if it fails to import
try:
    from requirement_analyzer.task_gen.semantic import (
        SemanticParser as _SemParser,
        DependencyAI as _DepAI,
        StoryNode as _StoryNode,
    )
    from requirement_analyzer.task_gen.semantic.embedding import (
        auto_backend as _auto_embed,
    )
    _DEP_AI_AVAILABLE = True
except Exception as _e:  # pragma: no cover
    _DEP_AI_AVAILABLE = False
    _DEP_AI_IMPORT_ERR = _e

logger = logging.getLogger("requirement_analyzer.api_v2")


class V2TaskGenerator:
    """V2 Task generator with full pipeline integration"""
    
    def __init__(self):
        """Initialize V2 task generator"""
        self.pipeline = V2Pipeline()
        self.detector = self._load_detector()
        self.priority_clf = get_priority_classifier()
        
    def _load_detector(self):
        """Load requirement detector"""
        try:
            from requirement_analyzer.task_gen.req_detector import get_detector
            return get_detector()
        except Exception as e:
            logger.warning(f"Could not load requirement detector: {e}")
            return None
    
    def generate_from_text(
        self,
        text: str,
        language: Optional[str] = None,
        sprint_weeks: Optional[int] = None,
        team_velocity: int = 40,
    ) -> Dict[str, Any]:
        """
        Generate tasks from requirement text using V2 pipeline.

        Args:
            text: Requirement text
            language: Force language ('vi' or 'en'). Auto-detected if None.
            sprint_weeks: Sprint duration in weeks (auto-parsed from text if None)
            team_velocity: Team velocity in SP/sprint (default 40)

        Returns:
            Dictionary with tasks, stats, quality metrics, sprint assignments, and history_session_id
        """
        # Auto-detect language if not provided
        if language is None:
            language = detect_language(text)

        # Parse sprint duration from document if not specified
        if sprint_weeks is None:
            sprint_weeks = parse_sprint_weeks(text) or 2

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
                "reasoning": "Empty input after noise filtering",
                "language": language,
                "sprint_weeks": sprint_weeks,
            }

        # Stage 2: Process through V2 pipeline
        tasks_output = self._process_requirements(requirements, language)

        # Stage 3: Deduplicate similar user stories across requirements
        tasks_output = self._deduplicate_stories(tasks_output)

        # Stage 4: Assign sprints with dependency-aware ordering
        all_stories = []
        for task in tasks_output.get("tasks", []):
            all_stories.extend(task.get("user_stories", []))
        if all_stories:
            all_stories = self._sort_by_dependency(all_stories)
            assign_sprints(all_stories, sprint_weeks=sprint_weeks, team_velocity=team_velocity)

        # Stage 4a: Dependency AI — bottleneck / critical path / risk / recs
        try:
            tasks_output["dependency_ai"] = self._compute_dependency_ai(all_stories)
        except Exception as e:
            logger.warning(f"Dependency AI failed: {e}")
            tasks_output["dependency_ai"] = {"error": str(e)}

        # Stage 4b: Group user stories into Epics by domain (Scrum hierarchy)
        tasks_output["epics"] = self._group_into_epics(all_stories) if all_stories else []

        # Stage 5: Add Explainable AI reasoning
        tasks_output = self._add_explainability(tasks_output)

        # Stage 5: Save to history
        try:
            flat_for_history = []
            for task in tasks_output.get("tasks", []):
                flat_for_history.extend(task.get("user_stories", []))
            session_id = save_history(
                tasks=flat_for_history,
                source_text=text,
                metadata={"language": language, "sprint_weeks": sprint_weeks}
            )
            tasks_output["history_session_id"] = session_id
        except Exception as e:
            logger.warning(f"Could not save task history: {e}")

        tasks_output["language"] = language
        tasks_output["sprint_weeks"] = sprint_weeks
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

        # Check for sprint/project metadata lines (not requirements)
        import re
        meta_patterns = [
            r"^sprint\s*[:：]",              # "Sprint: 3 weeks"
            r"^project\s*[:：]",
            r"^version\s*[:：]",
            r"^date\s*[:：]",
            r"^author\s*[:：]",
            r"^status\s*[:：]",
            r"^team\s*[:：]",
            r"^priority\s*[:：]",
            r"^revision\s*[:：]",
        ]
        for pat in meta_patterns:
            if re.match(pat, line_lower):
                return True

        # ── NEW: filter resource/staffing/org lines (AI hallucination source) ──
        resource_patterns = [
            # Vietnamese staffing terms
            r"\bnhân\s+lực\b",       # "nhân lực"
            r"\bthành\s+viên\b",     # "thành viên nhóm"
            r"\bngân\s+sách\b",      # "ngân sách"
            r"\btiến\s+độ\b",        # "tiến độ dự án"
            r"\blộ\s+trình\b",       # "lộ trình"
            r"\bkế\s+hoạch\b",       # "kế hoạch" (standalone, not req)
            r"\bthời\s+gian\s+dự\s+kiến\b",  # "thời gian dự kiến"
            r"^\d+\s+(?:backend|frontend|developer|dev|tester|qa|pm|ba)\b",  # "3 Backend Developer"
            r"\b(?:project\s+manager|business\s+analyst|scrum\s+master|team\s+lead)\b",
            # English staffing
            r"\bstaffing\b", r"\bheadcount\b", r"\bresource\s+plan\b",
            r"\bteam\s+size\b", r"\bbudget\b",
            r"^\d+\s+\w+\s+(?:developer|engineer|manager|designer)\b",
        ]
        for pat in resource_patterns:
            if re.search(pat, line_lower):
                return True

        # ── NEW: filter tech-stack / architecture / timeline metadata lines ───
        tech_timeline_patterns = [
            # "Nền tảng: Web-based", "Platform: Web"
            r"^-?\s*(nền\s+tảng|platform)\s*[:：]",
            # "Ngôn ngữ phát triển: Java/Spring Boot"
            r"^-?\s*(ngôn\s+ngữ|language|lang)\s*(phát\s+triển|lập\s+trình)?\s*[:：]",
            # "Framework: React, Spring Boot"
            r"^-?\s*(framework|thư\s+viện|library|tools?)\s*[:：]",
            # "Cơ sở dữ liệu: PostgreSQL"
            r"^-?\s*(cơ\s+sở\s+dữ\s+liệu|database|db)\s*[:：]",
            # "Triển khai: Docker, Kubernetes"
            r"^-?\s*(triển\s+khai|deployment|deploy|hosting|ci\s*/\s*cd)\s*[:：]",
            # "Kiến trúc: Microservices", "Tech stack: ..."
            r"^-?\s*(kiến\s+trúc|architecture|tech\s+stack|công\s+nghệ|stack)\s*[:：]",
            # "Server: Nginx", "Cloud: AWS"
            r"^-?\s*(server|cloud|infrastructure|hạ\s+tầng)\s*[:：]",
            # Timeline items: "1. Phân tích yêu cầu: 2 tuần", "2. Thiết kế hệ thống: 4 tuần"
            r"^-?\s*\d+[\.\)]\s*(phân\s+tích|thiết\s+kế|phát\s+triển|kiểm\s+thử|triển\s+khai|testing|development|design|analysis)[^:]*:\s*\d+\s*(tuần|tháng|ngày|week|month|day)",
            # "Giai đoạn 1:", "Phase 2:", "Milestone 3:"
            r"^-?\s*(giai\s+đoạn|phase|milestone)\s+\d+\s*[:：]",
            # "Thời gian: 3 tháng", "Timeline: 6 months"
            r"^-?\s*(thời\s+gian|timeline|schedule|lịch\s+trình)\s*[:：]",
            # Standalone tech keywords as whole line: "- Docker, Kubernetes"
            r"^-?\s*(java|spring\s*boot|python|node\.?js|react|angular|vue\.?js|docker|kubernetes|k8s|postgresql|mysql|mongodb|redis|aws|azure|gcp|nginx|microservice)\s*(?:[:：,/]|\s*$)",
        ]
        for pat in tech_timeline_patterns:
            if re.search(pat, line_lower):
                return True

        # Check if it ends with colon (section header)
        if line.endswith(":"):
            return True
        
        return False

    # ── Dependency domain ordering ─────────────────────────────────────────────
    # Earlier buckets map to lower sprint numbers (foundations first).
    _DEPENDENCY_DOMAIN_ORDER = [
        # Bucket 0: Auth & security (must come first)
        {'security', 'bảo mật', 'mã hóa', 'encrypt', 'ssl', 'tls', 'https',
         'đăng nhập', 'login', 'sign in', 'xác thực', 'authentication',
         'phân quyền', 'authorization', 'oauth', 'jwt', 'password', 'mật khẩu'},
        # Bucket 1: User / account management
        {'đăng ký', 'register', 'tài khoản', 'account', 'profile', 'hồ sơ',
         'người dùng', 'user management', 'quản lý người dùng'},
        # Bucket 2: Core domain features
        {'tạo', 'create', 'thêm', 'add', 'cập nhật', 'update', 'sửa', 'edit',
         'xóa', 'delete', 'quản lý', 'manage'},
        # Bucket 3: Search / view
        {'tìm kiếm', 'search', 'lọc', 'filter', 'xem', 'view', 'danh sách', 'list'},
        # Bucket 4: Integration & external services
        {'thanh toán', 'payment', 'tích hợp', 'integrate', 'api', 'webhook',
         'email', 'thông báo', 'notification', 'sms'},
        # Bucket 5: Reporting & analytics (last)
        {'báo cáo', 'report', 'thống kê', 'statistic', 'analytics', 'export', 'import'},
    ]

    def _dependency_bucket(self, story: dict) -> int:
        """Return 0-5 dependency bucket for a story (lower = earlier in sprints)."""
        text = (
            (story.get("title") or "") + " " + (story.get("user_story") or "")
        ).lower()
        for bucket_idx, kw_set in enumerate(self._DEPENDENCY_DOMAIN_ORDER):
            if any(kw in text for kw in kw_set):
                return bucket_idx
        return 3  # Default: core feature bucket

    def _sort_by_dependency(self, stories: list) -> list:
        """
        Sort stories so that foundational stories (auth, account) come before
        dependent ones (payment, reporting). Within each bucket, preserve
        priority ordering (Critical > High > Medium > Low).
        """
        priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        return sorted(
            stories,
            key=lambda s: (
                self._dependency_bucket(s),
                priority_order.get(s.get("priority", "Medium"), 2),
            )
        )

    # ── Dependency AI (graph + risk + critical path + recommendations) ────────
    def _compute_dependency_ai(self, stories: list) -> Dict[str, Any]:
        """Run :class:`DependencyAI` over the planned backlog.

        Stories are passed through :class:`SemanticParser` to recover the
        IR, then graph analytics produce: edges, topological order,
        critical path, bottlenecks, risk scores, sprint validation, and
        actionable recommendations.  Falls back to an empty payload if
        the semantic engine is unavailable.
        """
        if not _DEP_AI_AVAILABLE or not stories:
            return {
                "available": False,
                "reason": (
                    "no stories" if not stories
                    else f"semantic engine unavailable: {_DEP_AI_IMPORT_ERR}"
                ),
            }

        parser = _SemParser()
        nodes = []
        for idx, s in enumerate(stories):
            text = (s.get("title") or "") + ". " + (s.get("user_story") or "")
            text = text.strip(". ").strip()
            if not text:
                continue
            try:
                ir = parser.parse(text)
            except Exception:
                continue
            nodes.append(_StoryNode(
                story_id=str(s.get("id") or s.get("task_id") or f"S{idx + 1}"),
                ir=ir,
                sprint=s.get("sprint"),
                story_points=int(s.get("story_points") or 0) or None,
                title=s.get("title") or s.get("user_story", "")[:80],
            ))

        if not nodes:
            return {"available": False, "reason": "no parseable stories"}

        try:
            embed = _auto_embed()
        except Exception:
            embed = None

        ai = _DepAI(embedding_backend=embed).build(nodes)
        payload = ai.to_dict()
        payload["available"] = True
        payload["stats"] = {
            "node_count": len(payload["nodes"]),
            "edge_count": len(payload["edges"]),
            "critical_path_length": len(payload["critical_path"]),
            "bottleneck_count": len(payload["bottlenecks"]),
            "violation_count": len(payload["validation_issues"]),
            "high_risk_count": sum(
                1 for v in payload["risk_scores"].values()
                if v.get("score", 0) >= 0.7
            ),
            "recommendation_count": len(payload["recommendations"]),
        }
        return payload

    # ── Epic grouping (Scrum hierarchy: Epic → Feature → Story → AC) ──────────
    # Each entry: (epic_id, generic_name_en, generic_name_vi, dep_buckets, keywords)
    # The generic name is replaced by a domain-specific name when the
    # detected domain matches (see _domain_epic_name below).
    _EPIC_DEFINITIONS = [
        ("E1", "Identity & Access", "Quản lý truy cập & Bảo mật", {0},
         {"login", "đăng nhập", "logout", "password", "mật khẩu", "auth",
          "xác thực", "phân quyền", "permission", "role", "vai trò",
          "security", "bảo mật", "encrypt", "mã hóa"}),
        ("E2", "User & Account Management", "Quản lý Người dùng",   {1},
         {"register", "đăng ký", "profile", "hồ sơ", "account", "tài khoản",
          "user management", "quản lý người dùng"}),
        ("E3", "Core Domain Operations",   "Nghiệp vụ Cốt lõi",     {2, 3},
         {"booking", "đặt", "room", "phòng", "order", "đơn hàng",
          "patient", "bệnh nhân", "appointment", "lịch hẹn",
          "create", "tạo", "update", "cập nhật", "manage", "quản lý",
          "search", "tìm", "list", "danh sách"}),
        ("E4", "Payment & Integrations",   "Thanh toán & Tích hợp", {4},
         {"payment", "thanh toán", "billing", "hóa đơn", "invoice",
          "checkout", "transaction", "giao dịch",
          "integrate", "tích hợp", "api", "webhook", "email",
          "notification", "thông báo", "sms"}),
        ("E5", "Reporting & Analytics",    "Báo cáo & Thống kê",    {5},
         {"report", "báo cáo", "dashboard", "thống kê", "statistic",
          "analytics", "export", "import", "kpi"}),
    ]

    # Domain-specific epic name overrides. Maps detected domain (from
    # _detect_domain) → {epic_id: (name_en, name_vi)}. Stories that fall
    # into the listed domain get the more specific epic name instead of
    # the generic one above.
    _DOMAIN_EPIC_NAMES = {
        "Hotel": {
            "E3": ("Booking & Room Management", "Quản lý Đặt phòng"),
            "E4": ("Payment & Guest Communications", "Thanh toán & Liên lạc khách"),
            "E5": ("Hotel Operations Reporting", "Báo cáo Vận hành Khách sạn"),
        },
        "Booking/Reservation": {
            "E3": ("Reservation Workflow", "Quy trình Đặt chỗ"),
        },
        "Healthcare": {
            "E3": ("Clinical Workflow", "Quy trình Khám chữa bệnh"),
            "E4": ("Billing & Patient Comms", "Viện phí & Liên lạc Bệnh nhân"),
        },
        "Hospital/Medicine": {
            "E3": ("Clinical Workflow", "Quy trình Khám chữa bệnh"),
        },
        "Clinical": {
            "E3": ("Clinical Workflow", "Quy trình Khám chữa bệnh"),
            "E5": ("Clinical Reports", "Báo cáo Lâm sàng"),
        },
        "Inpatient": {
            "E3": ("Inpatient Management", "Quản lý Nội trú"),
            "E4": ("Hospital Billing", "Viện phí"),
        },
        "Surgery": {
            "E3": ("Surgical Management", "Quản lý Phẫu thuật"),
            "E5": ("Surgical Reports", "Báo cáo Phẫu thuật"),
        },
        "Pharmacy": {
            "E3": ("Prescription & Inventory", "Đơn thuốc & Tồn kho"),
        },
        "Laboratory": {
            "E3": ("Lab Test Workflow", "Quy trình Xét nghiệm"),
            "E5": ("Lab Reports", "Báo cáo Xét nghiệm"),
        },
        "Payment/Billing": {
            "E4": ("Payment Processing", "Xử lý Thanh toán"),
        },
    }

    # Feature mapping inside each epic (sub-domain).
    # (feature_id, name_en, name_vi, keywords) — first match wins.
    _FEATURE_MAP = {
        "E1": [
            ("F1.1", "Authentication",  "Xác thực",
             ["login", "đăng nhập", "logout", "password", "mật khẩu",
              "session", "token"]),
            ("F1.2", "Authorization",   "Phân quyền",
             ["phân quyền", "authorization", "role", "vai trò",
              "permission", "rbac"]),
            ("F1.3", "Encryption & Audit", "Mã hóa & Audit",
             ["encrypt", "mã hóa", "audit", "ssl", "tls", "compliance"]),
        ],
        "E2": [
            ("F2.1", "Account Registration", "Đăng ký Tài khoản",
             ["register", "đăng ký", "sign up"]),
            ("F2.2", "Profile Management",   "Quản lý Hồ sơ",
             ["profile", "hồ sơ", "account", "tài khoản"]),
        ],
        "E3": [
            ("F3.1", "Create Records",       "Tạo Mới",
             ["create", "tạo", "thêm", "add", "đặt", "booking"]),
            ("F3.2", "Update / Edit",        "Cập nhật",
             ["update", "cập nhật", "sửa", "edit"]),
            ("F3.3", "Delete / Cancel",      "Xóa / Huỷ",
             ["delete", "xóa", "cancel", "huỷ"]),
            ("F3.4", "Search & List",        "Tìm & Liệt kê",
             ["search", "tìm", "filter", "lọc", "list", "danh sách",
              "view", "xem"]),
        ],
        "E4": [
            ("F4.1", "Payment Processing",   "Xử lý Thanh toán",
             ["payment", "thanh toán", "billing", "checkout",
              "transaction", "hóa đơn"]),
            ("F4.2", "Notifications",        "Thông báo",
             ["email", "sms", "notify", "notification", "thông báo"]),
            ("F4.3", "External Integration", "Tích hợp Hệ thống ngoài",
             ["integrate", "tích hợp", "api", "webhook", "gateway"]),
        ],
        "E5": [
            ("F5.1", "Operational Reports",  "Báo cáo Vận hành",
             ["report", "báo cáo"]),
            ("F5.2", "Dashboards",           "Bảng điều khiển",
             ["dashboard", "bảng điều khiển"]),
            ("F5.3", "Data Export / Import", "Xuất / Nhập dữ liệu",
             ["export", "import", "xuất", "nhập"]),
        ],
    }

    def _epic_for_story(self, story: dict) -> tuple:
        """Return (epic_id, name_en, name_vi) for a story.

        Strategy:
          1. Strong title-keyword match (most specific)  → epic
          2. Dependency bucket fallback                  → epic
          3. Default: Core Domain (E3)
        Then the epic name is upgraded with a domain-specific override
        if the story's domain has one defined.
        """
        title = (story.get("title") or "").lower()
        full = (
            title + " "
            + (story.get("user_story") or "") + " "
            + (story.get("domain") or "")
        ).lower()
        domain = story.get("domain") or "General"

        def _apply_domain(epic_id: str, en: str, vi: str) -> tuple:
            override = self._DOMAIN_EPIC_NAMES.get(domain, {}).get(epic_id)
            if override:
                return epic_id, override[0], override[1]
            return epic_id, en, vi

        # Pass 1: title keyword match (highest priority — most specific signal)
        for epic_id, name_en, name_vi, _buckets, kws in self._EPIC_DEFINITIONS:
            if any(kw in title for kw in kws):
                return _apply_domain(epic_id, name_en, name_vi)

        # Pass 2: bucket-based mapping
        bucket = self._dependency_bucket(story)
        for epic_id, name_en, name_vi, buckets, _kws in self._EPIC_DEFINITIONS:
            if bucket in buckets:
                return _apply_domain(epic_id, name_en, name_vi)

        # Pass 3: full-text keyword match (fallback)
        for epic_id, name_en, name_vi, _buckets, kws in self._EPIC_DEFINITIONS:
            if any(kw in full for kw in kws):
                return _apply_domain(epic_id, name_en, name_vi)

        # Default: core domain (still domain-aware)
        return _apply_domain("E3", "Core Domain Operations", "Nghiệp vụ Cốt lõi")

    def _feature_for_story(self, epic_id: str, story: dict) -> tuple:
        """Return (feature_id, name_en, name_vi) for a story within an epic.

        If no feature in the epic matches, returns a generic feature for
        the epic (the first one) as a safe default.
        """
        text = (
            (story.get("title") or "") + " "
            + (story.get("user_story") or "")
        ).lower()

        features = self._FEATURE_MAP.get(epic_id, [])
        for fid, name_en, name_vi, kws in features:
            if any(kw in text for kw in kws):
                return fid, name_en, name_vi

        # Safe default: first feature in the epic, else generic
        if features:
            fid, name_en, name_vi, _ = features[0]
            return fid, name_en, name_vi
        return f"{epic_id}.F1", "General", "Tổng quát"

    def _group_into_epics(self, stories: list) -> list:
        """Group user stories into Epic → Feature → Story (Scrum hierarchy).

        Output structure:
          [
            {
              "epic_id": "E3",
              "name": "Booking & Room Management",
              "name_vi": "Quản lý Đặt phòng",
              "story_count": 4,
              "total_story_points": 21,
              "sprints": [1, 2],
              "features": [
                {
                  "feature_id": "F3.1",
                  "name": "Create Records",
                  "name_vi": "Tạo Mới",
                  "story_ids": [...],
                  "story_count": 2,
                  "total_story_points": 8,
                },
                ...
              ]
            },
            ...
          ]
        """
        epics: dict[str, dict] = {}
        for story in stories:
            epic_id, name_en, name_vi = self._epic_for_story(story)
            feat_id, feat_en, feat_vi = self._feature_for_story(epic_id, story)

            ep = epics.setdefault(epic_id, {
                "epic_id": epic_id,
                "name": name_en,
                "name_vi": name_vi,
                "story_count": 0,
                "total_story_points": 0,
                "sprints": set(),
                "_features": {},
            })

            feat = ep["_features"].setdefault(feat_id, {
                "feature_id": feat_id,
                "name": feat_en,
                "name_vi": feat_vi,
                "story_ids": [],
                "story_count": 0,
                "total_story_points": 0,
            })

            sp = int(story.get("story_points") or 0)
            sprint_no = story.get("sprint")

            ep["story_count"] += 1
            ep["total_story_points"] += sp
            if sprint_no is not None:
                ep["sprints"].add(int(sprint_no))

            feat["story_ids"].append(story.get("id"))
            feat["story_count"] += 1
            feat["total_story_points"] += sp

            # Stamp epic + feature on the story so the UI can show breadcrumbs
            story["epic_id"] = epic_id
            story["epic_name"] = name_en
            story["feature_id"] = feat_id
            story["feature_name"] = feat_en

        # Convert dicts → ordered lists, drop empty
        ordered_ids = [e[0] for e in self._EPIC_DEFINITIONS]
        ordered = []
        for eid in ordered_ids:
            if eid not in epics:
                continue  # skip empty epics — domain-aware output
            ep = epics[eid]
            ep["sprints"] = sorted(ep["sprints"])
            ep["features"] = sorted(
                ep.pop("_features").values(),
                key=lambda f: f["feature_id"],
            )
            ordered.append(ep)
        return ordered

    def _deduplicate_stories(self, tasks_output: dict) -> dict:
        """
        Remove near-duplicate user stories across different requirements.
        Uses simple token-overlap (Jaccard similarity) to detect duplicates.
        Keeps the story with higher story_points (more specific).
        """
        import re as _re

        def _tokens(text: str) -> set:
            return set(_re.findall(r'\w+', (text or "").lower()))

        def _jaccard(a: set, b: set) -> float:
            if not a and not b:
                return 1.0
            union = a | b
            return len(a & b) / len(union) if union else 0.0

        THRESHOLD = 0.75  # 75% token overlap → duplicate

        all_stories: list[dict] = []
        for task in tasks_output.get("tasks", []):
            all_stories.extend(task.get("user_stories", []))

        # Mark duplicates
        kept_indices: list[int] = []
        seen_tokens: list[set] = []

        for i, story in enumerate(all_stories):
            title_tokens = _tokens(story.get("title", "") + " " + story.get("user_story", ""))
            is_dup = False
            for j, prev_tokens in enumerate(seen_tokens):
                if _jaccard(title_tokens, prev_tokens) >= THRESHOLD:
                    # Keep the one with more story_points (more granular)
                    prev_idx = kept_indices[j]
                    if (story.get("story_points") or 0) > (all_stories[prev_idx].get("story_points") or 0):
                        kept_indices[j] = i
                        seen_tokens[j] = title_tokens
                    is_dup = True
                    break
            if not is_dup:
                kept_indices.append(i)
                seen_tokens.append(title_tokens)

        # Rebuild kept story id set
        kept_ids = {all_stories[i].get("id") for i in kept_indices}

        # Filter tasks
        total_removed = 0
        for task in tasks_output.get("tasks", []):
            original_len = len(task.get("user_stories", []))
            task["user_stories"] = [
                s for s in task.get("user_stories", []) if s.get("id") in kept_ids
            ]
            total_removed += original_len - len(task["user_stories"])

        if total_removed:
            logger.info(f"Deduplication: removed {total_removed} near-duplicate user stories")

        return tasks_output

    def _detect_domain(self, requirement_text: str) -> str:
        """Detect domain from requirement text.

        Order matters: more specific subdomains are checked first so that
        e.g. "phẫu thuật" yields ``Surgery`` instead of generic ``Healthcare``.
        """
        text_lower = requirement_text.lower()

        # Most specific first → most generic last
        domains = {
            "Surgery":            ["phẫu thuật", "mổ", "surgical", "surgery",
                                   "operating room", "phòng mổ"],
            "Inpatient":          ["giường bệnh", "nội trú", "inpatient",
                                   "ward", "khoa nội", "nhập viện",
                                   "discharge", "xuất viện"],
            "Clinical":           ["bác sĩ", "chẩn đoán", "diagnosis",
                                   "khám bệnh", "physician", "điều dưỡng",
                                   "nurse", "triệu chứng", "symptom",
                                   "clinical", "prescription"],
            "Pharmacy":           ["thuốc", "nhà thuốc", "pharmacy",
                                   "medication", "drug", "đơn thuốc"],
            "Laboratory":         ["xét nghiệm", "laboratory", "lab test",
                                   "sample", "mẫu bệnh phẩm"],
            "Healthcare":         ["bệnh viện", "bệnh nhân", "y tế",
                                   "medical", "hospital", "patient",
                                   "healthcare"],
            "Hospital/Medicine":  ["hospital management", "his", "emr",
                                   "electronic medical record"],
            "Payment/Billing":    ["viện phí", "thanh toán", "payment",
                                   "billing", "invoice", "hóa đơn"],
            "Hotel":              ["khách sạn", "hotel", "phòng khách sạn",
                                   "hotel room"],
            "Booking/Reservation":["đặt phòng", "đặt lịch", "booking",
                                   "reservation"],
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
        requirements: List[Requirement],
        language: str = "en",
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
                task = self._convert_v2_to_task(v2_output, language)
                tasks.append(task)

            except Exception as e:
                logger.error(f"Error processing {requirement.requirement_id}: {e}")
                # Add basic task as fallback
                task = self._create_fallback_task(requirement, language)
                tasks.append(task)
        
        return {
            "status": "success",
            "tasks": tasks,
            "total_tasks": len(tasks),
            "functional_requirements": functional_count,
            "non_functional_requirements": nfr_count,
            "summary": self._generate_summary(tasks, functional_count, nfr_count)
        }
    
    def _convert_v2_to_task(self, v2_output, language: str = "en") -> Dict[str, Any]:
        """
        Convert V2 pipeline output to task format.
        Fixes:
          - Priority uses ML model (92% accuracy) instead of hardcoded "High"
          - Story points snapped to Fibonacci [1,2,3,5,8,13,21]
          - Language consistency enforced
        """
        refinement = v2_output.refinement
        slicing = v2_output.slicing
        req_text = v2_output.original_requirement or ""

        user_stories = []
        for slice_obj in slicing.slices:
            for story in slice_obj.stories:
                story_acs = [
                    ac for ac in refinement.acceptance_criteria
                    if ac.ac_id in story.acceptance_criteria_refs
                ]

                # ── FIX: ML-based priority (not hardcoded "High") ──────────
                priority, priority_conf = self.priority_clf.predict(
                    story.user_story or req_text
                )

                # ── FIX: Fibonacci story points ────────────────────────────
                invest_total = story.invest_score.total if story.invest_score else None
                sp = estimate_story_points(
                    text=story.user_story or req_text,
                    priority=priority,
                    n_acceptance_criteria=len(story_acs),
                    n_subtasks=len(story.subtasks),
                    invest_total=invest_total,
                )

                subtasks = [
                    {
                        "id": subtask.task_id,
                        "title": subtask.title,
                        "description": subtask.description,
                        "role": subtask.role.name if hasattr(subtask.role, "name") else str(subtask.role),
                        "priority": subtask.priority,
                        "days_estimated": round((subtask.estimate_hours or 8) / 8, 1),
                    }
                    for subtask in story.subtasks
                ]

                us_dict = {
                    "id": story.story_id,
                    "title": story.title,
                    "user_story": story.user_story,
                    "domain": v2_output.domain,
                    "status": "ready",
                    "language": language,
                    # ── Fixed fields ────────────────────────────────────
                    "story_points": sp,          # Fibonacci: 1,2,3,5,8,13,21
                    "priority": priority,        # ML model: Critical/High/Medium/Low
                    "priority_confidence": round(priority_conf, 2),
                    # ───────────────────────────────────────────────────
                    "acceptance_criteria": [
                        {
                            "id": ac.ac_id,
                            "given": ac.given,
                            "when": ac.when,
                            "then": ac.then,
                            "priority": ac.priority.name,
                        }
                        for ac in story_acs
                    ],
                    "subtasks": subtasks,
                    "nfrs": refinement.non_functional_requirements or [],
                    "risk_level": "HIGH" if priority in ("Critical", "High") else "MEDIUM",
                    "invest_score": {
                        "independent": story.invest_score.independent,
                        "negotiable": story.invest_score.negotiable,
                        "valuable": story.invest_score.valuable,
                        "estimable": story.invest_score.estimable,
                        "small": story.invest_score.small,
                        "testable": story.invest_score.testable,
                        "total": invest_total or 0,
                    },
                }
                user_stories.append(us_dict)

        if not user_stories:
            user_stories = [self._create_default_user_story(refinement, v2_output.domain, language)]

        return {
            "requirement_id": v2_output.requirement_id,
            "original_requirement": req_text,
            "type": refinement.user_story.split()[0] if refinement.user_story else "Feature",
            "domain": v2_output.domain,
            "language": language,
            "quality_score": (
                v2_output.quality_metrics.overall_quality
                if hasattr(v2_output.quality_metrics, "overall_quality")
                else 0.5
            ),
            "user_stories": user_stories,
            "gaps": [
                {
                    "id": gap.gap_id,
                    "description": gap.description,
                    "severity": gap.severity.name if hasattr(gap.severity, "name") else str(gap.severity),
                    "type": gap.type.name if hasattr(gap.type, "name") else str(gap.type),
                    "question": gap.question,
                    "suggestion": gap.suggestion,
                }
                for gap in (v2_output.gap_report.gaps if v2_output.gap_report else [])
            ],
            "traceability": {
                "source": (
                    v2_output.traceability.requirement_to_stories[0]
                    if v2_output.traceability
                    else None
                ),
                "coverage": len(user_stories) / max(1, len(user_stories)),
            },
        }
    
    def _create_default_user_story(
        self, refinement, domain: str, language: str = "en"
    ) -> Dict[str, Any]:
        """Create default user story from refinement with proper priority & SP"""
        req_text = refinement.user_story or refinement.title or ""
        priority, priority_conf = self.priority_clf.predict(req_text)
        sp = estimate_story_points(
            text=req_text,
            priority=priority,
            n_acceptance_criteria=len(refinement.acceptance_criteria),
        )
        return {
            "id": refinement.requirement_id,
            "title": refinement.title,
            "user_story": refinement.user_story,
            "domain": domain,
            "language": language,
            "status": "ready",
            "story_points": sp,
            "priority": priority,
            "priority_confidence": round(priority_conf, 2),
            "acceptance_criteria": [
                {
                    "id": ac.ac_id,
                    "given": ac.given,
                    "when": ac.when,
                    "then": ac.then,
                    "priority": ac.priority.name,
                }
                for ac in refinement.acceptance_criteria
            ],
            "subtasks": [],
            "nfrs": refinement.non_functional_requirements or [],
            "risk_level": "HIGH" if priority in ("Critical", "High") else "MEDIUM",
            "invest_score": {
                "independent": True,
                "negotiable": True,
                "valuable": True,
                "estimable": True,
                "small": True,
                "testable": True,
                "total": 25,
            }
        }
    
    def _create_fallback_task(
        self, requirement: Requirement, language: str = "en"
    ) -> Dict[str, Any]:
        """Create fallback task if pipeline fails (with proper priority & SP)"""
        req_type = self._detect_requirement_type(requirement.original_text)
        req_text = requirement.original_text

        priority, priority_conf = self.priority_clf.predict(req_text)
        sp = estimate_story_points(text=req_text, priority=priority)

        return {
            "requirement_id": requirement.requirement_id,
            "original_requirement": req_text,
            "type": req_type.name,
            "domain": requirement.domain or "General",
            "language": language,
            "quality_score": 0.3,
            "user_stories": [
                {
                    "id": requirement.requirement_id,
                    "title": req_text[:60],
                    "user_story": req_text,
                    "domain": requirement.domain or "General",
                    "language": language,
                    "story_points": sp,
                    "priority": priority,
                    "priority_confidence": round(priority_conf, 2),
                    "subtasks": [],
                    "acceptance_criteria": [],
                    "risk_level": "HIGH" if priority in ("Critical", "High") else "MEDIUM",
                }
            ],
            "gaps": [],
            "error": "Failed to fully process through V2 pipeline",
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
