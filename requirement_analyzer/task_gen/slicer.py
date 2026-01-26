"""
V2 Smart Slicer + INVEST Scoring
=================================

Slices requirements into stories using multiple strategies:
- Workflow slicing (happy path vs edge cases)
- Data slicing (different entities)
- Risk slicing (high-risk scenarios)
- Role slicing (different user roles)

Scores stories using INVEST criteria.
"""
from typing import List, Dict
from requirement_analyzer.task_gen.schemas_v2 import (
    RefinementOutput,
    Slice,
    UserStory,
    Subtask,
    INVESTScore,
    SliceRationale,
    TaskRole,
    RequirementType,
    SlicingOutput
)


class SmartSlicer:
    """Slices requirements into user stories with INVEST scoring"""
    
    def __init__(self):
        """Initialize slicer"""
        self.story_counter = 0
        self.task_counter = 0
    
    def slice_requirement(self, refinement: RefinementOutput) -> SlicingOutput:
        """
        Slice a refined requirement into user stories
        
        Args:
            refinement: Refined requirement output
            
        Returns:
            SlicingOutput with slices, stories, subtasks
        """
        self.story_counter = 0
        self.task_counter = 0
        
        slices = []
        
        # Determine slicing strategy
        strategies = self._determine_strategies(refinement)
        
        for idx, strategy in enumerate(strategies, 1):
            slice_obj = self._create_slice(refinement, strategy, idx)
            slices.append(slice_obj)
        
        return SlicingOutput(
            requirement_id=refinement.requirement_id,
            slices=slices
        )
    
    def _determine_strategies(self, refinement: RefinementOutput) -> List[SliceRationale]:
        """Determine which slicing strategies to use"""
        strategies = []
        text_lower = refinement.user_story.lower()
        
        # Always start with workflow (happy path)
        strategies.append(SliceRationale.WORKFLOW)
        
        # Check for multiple actors/roles
        actor_keywords = ['quản lý', 'nhân viên', 'khách hàng', 'admin', 'user']
        actor_count = sum(1 for kw in actor_keywords if kw in text_lower)
        if actor_count > 1:
            strategies.append(SliceRationale.ROLE)
        
        # Check for multiple data entities
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
        
        # Default: use workflow + data if nothing else
        if len(strategies) == 1:
            strategies.append(SliceRationale.DATA)
        
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
    
    def _create_data_story(self, refinement: RefinementOutput, operation: str) -> UserStory:
        """Create story for data operation (CRUD)"""
        self.story_counter += 1
        story_id = f"{refinement.requirement_id}_ST{self.story_counter:02d}"
        
        operation_vi = {
            "create": "tạo mới",
            "read": "xem/tra cứu",
            "update": "cập nhật",
            "delete": "xóa"
        }
        
        title = f"{refinement.title} - {operation_vi[operation].title()}"
        user_story = refinement.user_story.replace("muốn", f"muốn {operation_vi[operation]}")
        
        ac_refs = [ac.ac_id for ac in refinement.acceptance_criteria[:2]]
        
        subtasks = self._generate_subtasks(
            refinement,
            story_id,
            operation_vi[operation].title(),
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
        """Create story for high-risk scenario"""
        self.story_counter += 1
        story_id = f"{refinement.requirement_id}_ST{self.story_counter:02d}"
        
        title = f"{refinement.title} - Security & Risk Mitigation"
        user_story = refinement.user_story + " với đảm bảo bảo mật và xử lý rủi ro"
        
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
        
        role_vi = {"admin": "Quản trị viên", "user": "Người dùng"}
        
        title = f"{refinement.title} - {role_vi.get(role, role)}"
        user_story = refinement.user_story.replace("một", f"một {role_vi.get(role, role)}")
        
        ac_refs = [ac.ac_id for ac in refinement.acceptance_criteria[:2]]
        
        subtasks = self._generate_subtasks(
            refinement,
            story_id,
            role_vi.get(role, role),
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
        user_story = refinement.user_story + " thông qua tích hợp hệ thống ngoài"
        
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
