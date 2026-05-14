"""
V2 Smart Slicer + INVEST Scoring (Scrum-aligned)
=================================================

PHILOSOPHY (Refactored 2026-04):
--------------------------------
A user story = ONE unit of user value. We do NOT split a single requirement
into separate "Happy Path / Edge Case / Security / Role" stories — those are
**Acceptance Criteria** inside the single story (per Scrum / INVEST).

This module produces:
  - exactly ONE consolidated UserStory per requirement
  - all relevant scenarios merged into the story's Acceptance Criteria list
  - Backend / Frontend / QA subtasks (one of each) under that story
  - INVEST score for the story

The previous behaviour (multiple slices per requirement) caused fragmentation:
1 requirement → 6 stories → 21 sprints. With consolidation:
1 requirement → 1 story → realistic sprint count (4-6 for an MVP).
"""
from typing import List, Dict
from requirement_analyzer.task_gen.schemas_v2 import (
    RefinementOutput,
    Slice,
    UserStory,
    Subtask,
    INVESTScore,
    SliceRationale,
    SeverityLevel,
    AcceptanceCriterion,
    TaskRole,
    RequirementType,
    SlicingOutput
)


class SmartSlicer:
    """Slices requirements into user stories with INVEST scoring.

    Default mode: CONSOLIDATED — one story per requirement (Scrum standard).
    Set ``legacy_split=True`` to restore the old multi-slice behaviour.
    """

    def __init__(self, legacy_split: bool = False):
        """Initialize slicer.

        Args:
            legacy_split: If True, use the old behaviour that produces
                multiple stories per requirement (Happy Path / Edge / etc.).
                Default False (Scrum-aligned).
        """
        self.story_counter = 0
        self.task_counter = 0
        self.legacy_split = legacy_split

    def slice_requirement(self, refinement: RefinementOutput) -> SlicingOutput:
        """Slice a refined requirement into user stories.

        Default: ONE consolidated story per requirement, with all
        scenarios captured as Acceptance Criteria.
        """
        self.story_counter = 0
        self.task_counter = 0

        if self.legacy_split:
            # Old behaviour (kept for backward compatibility / A-B testing)
            slices = []
            strategies = self._determine_strategies(refinement)
            for idx, strategy in enumerate(strategies, 1):
                slices.append(self._create_slice(refinement, strategy, idx))
            return SlicingOutput(
                requirement_id=refinement.requirement_id,
                slices=slices,
            )

        # NEW: consolidated single-story output
        story = self._create_consolidated_story(refinement)
        slice_obj = Slice(
            slice_id="S1",
            rationale=SliceRationale.WORKFLOW,
            description="Consolidated user story (value-based, INVEST-compliant)",
            stories=[story],
            warnings=self._check_slice_warnings([story]),
            priority_order=1,
        )
        return SlicingOutput(
            requirement_id=refinement.requirement_id,
            slices=[slice_obj],
        )

    # ── Consolidated story builder ─────────────────────────────────────────────
    def _create_consolidated_story(self, refinement: RefinementOutput) -> UserStory:
        """Create ONE story per requirement with ALL scenarios as AC.

        Scenarios that previously became separate stories are now AC entries:
          - Happy path (always)
          - Edge cases / validation (if risky / data ops)
          - Security / authorization (if NFR or sensitive op)
          - Rollback / error recovery (if payment / delete)
          - Role variants (if multi-actor)
        """
        self.story_counter += 1
        story_id = f"{refinement.requirement_id}_ST{self.story_counter:02d}"

        # Start from the AC list produced by the refiner.
        all_ac = list(refinement.acceptance_criteria)

        # Synthesise additional AC entries for important scenarios that the
        # refiner may have missed. We keep the total reasonable (<= 10).
        synthetic = self._synthesize_missing_ac(refinement, existing_ids={
            ac.ac_id for ac in all_ac
        })
        if synthetic:
            all_ac.extend(synthetic)
            # IMPORTANT: also push synthetic AC into the refinement object so
            # downstream converters (api_v2_handler._convert_v2_to_task) can
            # find them when filtering by ac_id. Without this, the synthetic
            # AC are silently dropped from the API response.
            try:
                refinement.acceptance_criteria.extend(synthetic)
            except Exception:
                # Pydantic v2 list is mutable; this should always work,
                # but stay defensive.
                pass

        # Cap AC list to keep the story estimable (max 10 per Pydantic schema).
        all_ac = all_ac[:10]

        ac_refs = [ac.ac_id for ac in all_ac]

        subtasks = self._generate_subtasks(
            refinement,
            story_id,
            "Implementation",
            ac_refs,
        )

        invest = self._calculate_invest_score(refinement, subtasks, "consolidated")

        return UserStory(
            story_id=story_id,
            title=refinement.title,
            user_story=refinement.user_story,
            acceptance_criteria_refs=ac_refs,
            subtasks=subtasks,
            invest_score=invest,
            estimate_total_hours=sum(t.estimate_hours or 0 for t in subtasks),
        )

    def _synthesize_missing_ac(
        self,
        refinement: RefinementOutput,
        existing_ids: set,
    ) -> List[AcceptanceCriterion]:
        """Generate synthetic AC entries for scenarios the refiner may have missed.

        These are flags so the team has explicit DoD coverage even when the
        original requirement is terse. They use generic phrasing so they
        survive validation but make the scope visible.
        """
        text_lower = (refinement.user_story or "").lower()
        synth: List[AcceptanceCriterion] = []
        is_en = not any(m in text_lower for m in ["tôi muốn", "là một", "người dùng"])

        def _next_id(prefix: str = "AC") -> str:
            n = len(refinement.acceptance_criteria) + len(synth) + 1
            cid = f"{prefix}{n}"
            while cid in existing_ids:
                n += 1
                cid = f"{prefix}{n}"
            existing_ids.add(cid)
            return cid

        # Edge case / validation
        if any(kw in text_lower for kw in [
            "validate", "kiểm tra", "input", "form", "create", "tạo",
            "update", "cập nhật", "register", "đăng ký",
        ]):
            synth.append(AcceptanceCriterion(
                ac_id=_next_id(),
                given=("Given invalid or incomplete input data"
                       if is_en else "Cho dữ liệu đầu vào không hợp lệ hoặc thiếu"),
                when=("When the user submits the request"
                      if is_en else "Khi người dùng gửi yêu cầu"),
                then=("Then the system rejects it with a clear validation message"
                      if is_en else "Thì hệ thống từ chối và hiển thị thông báo lỗi rõ ràng"),
                priority=SeverityLevel.HIGH,
            ))

        # Security / authorization
        if any(kw in text_lower for kw in [
            "thanh toán", "payment", "đăng nhập", "login", "admin",
            "quản trị", "phân quyền", "security", "bảo mật",
            "xóa", "delete", "approve", "phê duyệt",
        ]):
            synth.append(AcceptanceCriterion(
                ac_id=_next_id(),
                given=("Given an unauthenticated or unauthorized user"
                       if is_en else "Cho một người dùng chưa đăng nhập hoặc không có quyền"),
                when=("When they attempt this action"
                      if is_en else "Khi họ cố thực hiện hành động này"),
                then=("Then the system blocks access and logs the attempt"
                      if is_en else "Thì hệ thống chặn truy cập và ghi log"),
                priority=SeverityLevel.CRITICAL,
            ))

        # Rollback / error recovery for transactional operations
        if any(kw in text_lower for kw in [
            "thanh toán", "payment", "transaction", "giao dịch",
            "transfer", "chuyển khoản",
        ]):
            synth.append(AcceptanceCriterion(
                ac_id=_next_id(),
                given=("Given a transient external failure during the operation"
                       if is_en else "Cho lỗi tạm thời từ hệ thống bên ngoài trong quá trình xử lý"),
                when=("When the operation cannot complete"
                      if is_en else "Khi không thể hoàn tất giao dịch"),
                then=("Then the system rolls back changes and the user can retry safely"
                      if is_en else "Thì hệ thống rollback và người dùng có thể thử lại an toàn"),
                priority=SeverityLevel.HIGH,
            ))

        return synth
    
    # ── NFR keyword sets ────────────────────────────────────────────────────────
    # Only INFRA-level security keywords trigger NFR classification.
    # Authentication / RBAC features are FUNCTIONAL — keep them out of this set.
    _NFR_SECURITY_KWS = {
        'ssl', 'tls', 'https', 'mã hóa', 'encrypt', 'firewall',
        'audit log', 'penetration', 'vulnerability', 'cybersecurity',
        'data breach', 'bảo mật dữ liệu', 'data encryption',
        'oauth', 'jwt',
    }
    _NFR_PERFORMANCE_KWS = {
        'hiệu suất', 'performance', 'tốc độ', 'latency', 'response time',
        'thời gian phản hồi', 'throughput', 'uptime', 'availability', 'sẵn sàng',
        'scalab', 'mở rộng', 'load', 'concurrent', 'caching', 'cache',
    }
    _NFR_COMPLIANCE_KWS = {
        'gdpr', 'hipaa', 'pci', 'iso', 'compliance', 'tuân thủ', 'quy định',
        'audit', 'regulation', 'policy', 'standard',
    }

    def _is_nfr_requirement(self, refinement: RefinementOutput) -> bool:
        """
        Return True when this refinement represents a non-functional requirement.
        Checks user story text AND any NFR strings already extracted.
        """
        text = refinement.user_story.lower()
        # Also check the NFR list extracted during refinement
        nfr_text = " ".join(refinement.non_functional_requirements or []).lower()
        combined = text + " " + nfr_text

        for kw_set in (self._NFR_SECURITY_KWS, self._NFR_PERFORMANCE_KWS, self._NFR_COMPLIANCE_KWS):
            if any(kw in combined for kw in kw_set):
                return True
        return False

    def _determine_strategies(self, refinement: RefinementOutput) -> List[SliceRationale]:
        """Determine which slicing strategies to use"""
        strategies = []
        text_lower = refinement.user_story.lower()

        # ── NFR requirements: implementation story + risk/verification story ──
        # Skip CRUD entirely for security/performance/compliance requirements.
        if self._is_nfr_requirement(refinement):
            strategies.append(SliceRationale.WORKFLOW)   # implementation
            strategies.append(SliceRationale.RISK)       # verification / testing
            return strategies

        # Always start with workflow (happy path)
        strategies.append(SliceRationale.WORKFLOW)
        
        # Check for multiple actors/roles
        actor_keywords = ['quản lý', 'nhân viên', 'khách hàng', 'admin', 'user']
        actor_count = sum(1 for kw in actor_keywords if kw in text_lower)
        if actor_count > 1:
            strategies.append(SliceRationale.ROLE)
        
        # Check for multiple data entities (only for functional requirements)
        data_keywords = ['phòng', 'đặt phòng', 'khách hàng', 'hóa đơn', 'thanh toán']
        data_count = sum(1 for kw in data_keywords if kw in text_lower)
        if data_count > 1:
            strategies.append(SliceRationale.DATA)
        
        # Check for risky operations
        risk_keywords = ['xóa', 'phê duyệt', 'thanh toán', 'chuyển khoản', 'delete', 'approve']
        if any(kw in text_lower for kw in risk_keywords):
            strategies.append(SliceRationale.RISK)
        
        # Check for integration
        if any(kw in text_lower for kw in ['api', 'tích hợp', 'integration']):
            strategies.append(SliceRationale.INTEGRATION)
        
        # Default fallback: only add DATA if requirement clearly references CRUD entities.
        # Do NOT add RISK as a generic catch-all — that causes Security & Risk story spam.
        if len(strategies) == 1:
            crud_signals = [
                'tạo', 'create', 'thêm', 'add', 'cập nhật', 'update', 'sửa', 'edit',
                'xóa', 'delete', 'xem', 'view', 'danh sách', 'list', 'search', 'tìm',
                'đăng ký', 'register', 'lưu', 'save'
            ]
            if any(kw in text_lower for kw in crud_signals):
                strategies.append(SliceRationale.DATA)
            # No fallback RISK: non-CRUD non-risky features get a single WORKFLOW story.
        
        return strategies[:3]  # Max 3 slices to keep manageable
    
    def _create_slice(
        self,
        refinement: RefinementOutput,
        rationale: SliceRationale,
        priority: int
    ) -> Slice:
        """Create a slice with stories"""
        stories = []
        
        if rationale == SliceRationale.WORKFLOW:
            # Happy path + edge cases
            stories.append(self._create_happy_path_story(refinement))
            stories.append(self._create_edge_case_story(refinement))
        
        elif rationale == SliceRationale.DATA:
            # Different data operations
            stories.append(self._create_data_story(refinement, "create"))
            stories.append(self._create_data_story(refinement, "read"))
            stories.append(self._create_data_story(refinement, "update"))
        
        elif rationale == SliceRationale.RISK:
            # High-risk scenarios
            stories.append(self._create_risk_story(refinement))
        
        elif rationale == SliceRationale.ROLE:
            # Different roles
            stories.append(self._create_role_story(refinement, "admin"))
            stories.append(self._create_role_story(refinement, "user"))
        
        elif rationale == SliceRationale.INTEGRATION:
            # Integration story
            stories.append(self._create_integration_story(refinement))
        
        else:
            # Default: single story
            stories.append(self._create_generic_story(refinement))
        
        # Generate warnings
        warnings = self._check_slice_warnings(stories)
        
        # Description
        description = self._generate_slice_description(rationale, len(stories))
        
        return Slice(
            slice_id=f"S{priority}",
            rationale=rationale,
            description=description,
            stories=stories,
            warnings=warnings,
            priority_order=priority
        )
    
    def _create_happy_path_story(self, refinement: RefinementOutput) -> UserStory:
        """Create story for happy path"""
        self.story_counter += 1
        story_id = f"{refinement.requirement_id}_ST{self.story_counter:02d}"
        
        # Use first 2-3 AC for happy path
        ac_refs = [ac.ac_id for ac in refinement.acceptance_criteria[:3]]
        
        # Generate subtasks
        subtasks = self._generate_subtasks(
            refinement,
            story_id,
            "Happy Path",
            ac_refs
        )
        
        # INVEST score
        invest = self._calculate_invest_score(refinement, subtasks, "happy_path")
        
        return UserStory(
            story_id=story_id,
            title=f"{refinement.title} - Happy Path",
            user_story=refinement.user_story,
            acceptance_criteria_refs=ac_refs,
            subtasks=subtasks,
            invest_score=invest,
            estimate_total_hours=sum(t.estimate_hours or 0 for t in subtasks)
        )
    
    def _create_edge_case_story(self, refinement: RefinementOutput) -> UserStory:
        """Create story for edge cases"""
        self.story_counter += 1
        story_id = f"{refinement.requirement_id}_ST{self.story_counter:02d}"
        
        # Use remaining AC for edge cases
        ac_refs = [ac.ac_id for ac in refinement.acceptance_criteria[3:]]
        if not ac_refs:
            ac_refs = [refinement.acceptance_criteria[0].ac_id]  # Fallback
        
        # Modify user story for edge cases
        user_story = refinement.user_story.replace(
            "tôi muốn",
            "tôi muốn hệ thống xử lý các trường hợp ngoại lệ khi"
        )
        
        subtasks = self._generate_subtasks(
            refinement,
            story_id,
            "Edge Cases",
            ac_refs
        )
        
        invest = self._calculate_invest_score(refinement, subtasks, "edge_case")
        
        return UserStory(
            story_id=story_id,
            title=f"{refinement.title} - Edge Cases & Validation",
            user_story=user_story,
            acceptance_criteria_refs=ac_refs,
            subtasks=subtasks,
            invest_score=invest,
            estimate_total_hours=sum(t.estimate_hours or 0 for t in subtasks)
        )
    
    def _is_english_story(self, refinement: RefinementOutput) -> bool:
        """Detect if the user story is in English."""
        vi_markers = ["tôi muốn", "là một", "để", "người dùng", "hệ thống"]
        us = refinement.user_story.lower()
        return not any(m in us for m in vi_markers)

    def _create_data_story(self, refinement: RefinementOutput, operation: str) -> UserStory:
        """Create story for data operation (CRUD)"""
        self.story_counter += 1
        story_id = f"{refinement.requirement_id}_ST{self.story_counter:02d}"

        is_en = self._is_english_story(refinement)
        if is_en:
            operation_label = {
                "create": "Create",
                "read":   "Read / Search",
                "update": "Update",
                "delete": "Delete"
            }
            op_display = operation_label[operation]
            title = f"{refinement.title} - {op_display}"
            user_story = refinement.user_story.replace("want to", f"want to {op_display.lower()}")
        else:
            operation_vi = {
                "create": "tạo mới",
                "read":   "xem/tra cứu",
                "update": "cập nhật",
                "delete": "xóa"
            }
            op_display = operation_vi[operation].title()
            title = f"{refinement.title} - {op_display}"
            user_story = refinement.user_story.replace("muốn", f"muốn {operation_vi[operation]}")

        ac_refs = [ac.ac_id for ac in refinement.acceptance_criteria[:2]]

        subtasks = self._generate_subtasks(
            refinement,
            story_id,
            op_display,
            ac_refs
        )
        
        invest = self._calculate_invest_score(refinement, subtasks, operation)
        
        return UserStory(
            story_id=story_id,
            title=title,
            user_story=user_story,
            acceptance_criteria_refs=ac_refs,
            subtasks=subtasks,
            invest_score=invest,
            estimate_total_hours=sum(t.estimate_hours or 0 for t in subtasks)
        )
    
    def _create_risk_story(self, refinement: RefinementOutput) -> UserStory:
        """Create story for risk / NFR-verification scenario with context-aware naming"""
        self.story_counter += 1
        story_id = f"{refinement.requirement_id}_ST{self.story_counter:02d}"

        is_en = self._is_english_story(refinement)
        text_lower = refinement.user_story.lower()
        is_nfr = self._is_nfr_requirement(refinement)
        is_perf = any(kw in text_lower for kw in self._NFR_PERFORMANCE_KWS)
        is_payment = any(kw in text_lower for kw in ['thanh toán', 'payment', 'billing', 'invoice', 'hóa đơn'])
        is_delete = any(kw in text_lower for kw in ['xóa', 'delete', 'remove'])

        if is_nfr and is_perf:
            title = f"{refinement.title} - Performance Testing"
            suffix = " with load testing and performance benchmarking" if is_en else " với kiểm tra tải trọng và đo lường hiệu năng"
        elif is_payment or (is_delete and not is_nfr):
            title = f"{refinement.title} - Error Handling & Rollback"
            suffix = " with rollback, idempotency, and failure recovery" if is_en else " với rollback, idempotent và khôi phục khi có lỗi"
        elif is_nfr:
            title = f"{refinement.title} - Security Verification"
            suffix = " with security testing and compliance audit" if is_en else " với kiểm thử bảo mật và xác minh tuân thủ"
        else:
            title = f"{refinement.title} - Edge Cases & Error Handling"
            suffix = " with error handling and edge case coverage" if is_en else " với xử lý lỗi và các trường hợp ngoại lệ"

        user_story = refinement.user_story + suffix
        
        ac_refs = [ac.ac_id for ac in refinement.acceptance_criteria]
        
        subtasks = self._generate_subtasks(
            refinement,
            story_id,
            "Risk Mitigation",
            ac_refs
        )
        
        # Add security subtask
        self.task_counter += 1
        subtasks.append(Subtask(
            task_id=f"{story_id}_T{self.task_counter:02d}",
            title="Security Review & Risk Assessment",
            description="Review security implications and implement safeguards",
            role=TaskRole.SECURITY,
            type=RequirementType.NON_FUNCTIONAL,
            priority="High",
            estimate_hours=4.0,
            acceptance_criteria_refs=ac_refs
        ))
        
        invest = self._calculate_invest_score(refinement, subtasks, "risk")
        
        return UserStory(
            story_id=story_id,
            title=title,
            user_story=user_story,
            acceptance_criteria_refs=ac_refs,
            subtasks=subtasks,
            invest_score=invest,
            estimate_total_hours=sum(t.estimate_hours or 0 for t in subtasks)
        )
    
    def _create_role_story(self, refinement: RefinementOutput, role: str) -> UserStory:
        """Create story for specific role"""
        self.story_counter += 1
        story_id = f"{refinement.requirement_id}_ST{self.story_counter:02d}"
        
        is_en = self._is_english_story(refinement)
        if is_en:
            role_map = {"admin": "Admin", "user": "End User"}
            role_display = role_map.get(role, role)
            title = f"{refinement.title} - {role_display}"
            user_story = refinement.user_story.replace("a user", f"a {role_display.lower()}")
        else:
            role_map = {"admin": "Quản trị viên", "user": "Người dùng"}
            role_display = role_map.get(role, role)
            title = f"{refinement.title} - {role_display}"
            user_story = refinement.user_story.replace("một", f"một {role_display}")

        ac_refs = [ac.ac_id for ac in refinement.acceptance_criteria[:2]]

        subtasks = self._generate_subtasks(
            refinement,
            story_id,
            role_display,
            ac_refs
        )
        
        invest = self._calculate_invest_score(refinement, subtasks, "role")
        
        return UserStory(
            story_id=story_id,
            title=title,
            user_story=user_story,
            acceptance_criteria_refs=ac_refs,
            subtasks=subtasks,
            invest_score=invest,
            estimate_total_hours=sum(t.estimate_hours or 0 for t in subtasks)
        )
    
    def _create_integration_story(self, refinement: RefinementOutput) -> UserStory:
        """Create story for integration"""
        self.story_counter += 1
        story_id = f"{refinement.requirement_id}_ST{self.story_counter:02d}"
        
        title = f"{refinement.title} - External Integration"
        is_en = self._is_english_story(refinement)
        user_story = refinement.user_story + (
            " via external system integration" if is_en
            else " thông qua tích hợp hệ thống ngoài"
        )
        
        ac_refs = [ac.ac_id for ac in refinement.acceptance_criteria]
        
        subtasks = self._generate_subtasks(
            refinement,
            story_id,
            "Integration",
            ac_refs
        )
        
        invest = self._calculate_invest_score(refinement, subtasks, "integration")
        
        return UserStory(
            story_id=story_id,
            title=title,
            user_story=user_story,
            acceptance_criteria_refs=ac_refs,
            subtasks=subtasks,
            invest_score=invest,
            estimate_total_hours=sum(t.estimate_hours or 0 for t in subtasks)
        )
    
    def _create_generic_story(self, refinement: RefinementOutput) -> UserStory:
        """Create generic story"""
        self.story_counter += 1
        story_id = f"{refinement.requirement_id}_ST{self.story_counter:02d}"
        
        ac_refs = [ac.ac_id for ac in refinement.acceptance_criteria]
        
        subtasks = self._generate_subtasks(
            refinement,
            story_id,
            "Implementation",
            ac_refs
        )
        
        invest = self._calculate_invest_score(refinement, subtasks, "generic")
        
        return UserStory(
            story_id=story_id,
            title=refinement.title,
            user_story=refinement.user_story,
            acceptance_criteria_refs=ac_refs,
            subtasks=subtasks,
            invest_score=invest,
            estimate_total_hours=sum(t.estimate_hours or 0 for t in subtasks)
        )
    
    def _generate_subtasks(
        self,
        refinement: RefinementOutput,
        story_id: str,
        context: str,
        ac_refs: List[str]
    ) -> List[Subtask]:
        """Generate Backend/Frontend/QA subtasks (like V1)"""
        subtasks = []
        
        # Backend
        self.task_counter += 1
        subtasks.append(Subtask(
            task_id=f"{story_id}_T{self.task_counter:02d}",
            title=f"[Backend] {context} - API & Business Logic",
            description=f"Implement backend logic for {refinement.title}",
            role=TaskRole.BACKEND,
            type=RequirementType.FUNCTIONAL,
            priority="High",
            estimate_hours=8.0,
            acceptance_criteria_refs=ac_refs
        ))
        
        # Frontend
        self.task_counter += 1
        subtasks.append(Subtask(
            task_id=f"{story_id}_T{self.task_counter:02d}",
            title=f"[Frontend] {context} - UI Implementation",
            description=f"Implement user interface for {refinement.title}",
            role=TaskRole.FRONTEND,
            type=RequirementType.FUNCTIONAL,
            priority="High",
            estimate_hours=6.0,
            acceptance_criteria_refs=ac_refs
        ))
        
        # QA
        self.task_counter += 1
        subtasks.append(Subtask(
            task_id=f"{story_id}_T{self.task_counter:02d}",
            title=f"[QA] {context} - Testing",
            description=f"Test all scenarios for {refinement.title}",
            role=TaskRole.QA,
            type=RequirementType.FUNCTIONAL,
            priority="Medium",
            estimate_hours=4.0,
            acceptance_criteria_refs=ac_refs
        ))
        
        return subtasks
    
    def _calculate_invest_score(
        self,
        refinement: RefinementOutput,
        subtasks: List[Subtask],
        story_type: str
    ) -> INVESTScore:
        """Calculate INVEST score for a story"""
        
        # Independent: Can it be done independently?
        independent = 4  # Default: mostly independent
        if story_type == "edge_case":
            independent = 3  # Depends on happy path
        
        # Negotiable: Open for discussion?
        negotiable = 4  # Most stories are negotiable
        
        # Valuable: Delivers value?
        valuable = 5 if story_type == "happy_path" else 4
        
        # Estimable: Can we estimate?
        estimable = 5 if len(refinement.acceptance_criteria) >= 3 else 3
        
        # Small: Small enough?
        small = 4 if len(subtasks) <= 3 else 2
        
        # Testable: Can we test?
        testable = 5 if len(refinement.acceptance_criteria) >= 2 else 3
        
        return INVESTScore(
            independent=independent,
            negotiable=negotiable,
            valuable=valuable,
            estimable=estimable,
            small=small,
            testable=testable
        )
    
    def _check_slice_warnings(self, stories: List[UserStory]) -> List[str]:
        """Check for slice-level warnings"""
        warnings = []
        
        if len(stories) > 5:
            warnings.append(f"Slice có {len(stories)} stories - có thể quá nhiều, xem xét tách slice")
        
        total_tasks = sum(len(s.subtasks) for s in stories)
        if total_tasks > 15:
            warnings.append(f"Tổng {total_tasks} subtasks - có thể phức tạp, xem xét giảm scope")
        
        # Check INVEST scores
        low_invest_stories = [s.story_id for s in stories if s.invest_score.total < 20]
        if low_invest_stories:
            warnings.append(f"Stories có INVEST thấp: {', '.join(low_invest_stories)}")
        
        return warnings
    
    def _generate_slice_description(self, rationale: SliceRationale, story_count: int) -> str:
        """Generate description for slice"""
        descriptions = {
            SliceRationale.WORKFLOW: f"Workflow slice với {story_count} stories covering happy path và edge cases",
            SliceRationale.DATA: f"Data slice với {story_count} stories cho các operations khác nhau",
            SliceRationale.RISK: f"Risk mitigation slice với {story_count} stories cho high-risk scenarios",
            SliceRationale.ROLE: f"Role-based slice với {story_count} stories cho từng vai trò",
            SliceRationale.INTEGRATION: f"Integration slice với {story_count} stories cho external systems"
        }
        return descriptions.get(rationale, f"Generic slice với {story_count} stories")
