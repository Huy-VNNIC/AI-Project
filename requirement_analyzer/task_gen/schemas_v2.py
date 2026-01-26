"""
V2 Pydantic Schemas for Requirements Engineering Pipeline
==========================================================

This module defines the data models for the V2 Requirements Engineering pipeline:
- Requirement extraction and normalization
- Refinement (User Stories + Acceptance Criteria)
- Gap Detection (Missing/Contradictory/Ambiguous)
- Smart Slicing (Epic → Stories → Subtasks)
- Quality Gates and Traceability
"""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum
from datetime import datetime


# ============================================================================
# Enums
# ============================================================================

class SeverityLevel(str, Enum):
    """Severity levels for gaps and issues"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class RequirementType(str, Enum):
    """Types of requirements"""
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    CONSTRAINT = "constraint"
    ASSUMPTION = "assumption"


class GapType(str, Enum):
    """Types of gaps detected in requirements"""
    MISSING_ACTOR = "missing_actor"
    MISSING_OBJECT = "missing_object"
    MISSING_CONSTRAINT = "missing_constraint"
    MISSING_ERROR_HANDLING = "missing_error_handling"
    MISSING_PERMISSION = "missing_permission"
    MISSING_NFR = "missing_nfr"
    CONTRADICTION = "contradiction"
    AMBIGUITY = "ambiguity"
    MISSING_INTEGRATION = "missing_integration"
    MISSING_SECURITY = "missing_security"
    MISSING_DATA_VALIDATION = "missing_data_validation"


class SliceRationale(str, Enum):
    """Rationale for creating a story slice"""
    WORKFLOW = "workflow"  # Happy path / alternative flows
    DATA = "data"  # Different data entities
    RISK = "risk"  # High-risk scenarios
    PLATFORM = "platform"  # Different platforms (web/mobile)
    ROLE = "role"  # Different user roles
    INTEGRATION = "integration"  # External system integration


class TaskRole(str, Enum):
    """Roles for task assignment"""
    BACKEND = "Backend"
    FRONTEND = "Frontend"
    QA = "QA"
    DEVOPS = "DevOps"
    SECURITY = "Security"
    UNKNOWN = "Unknown"


# ============================================================================
# Stage 0: Requirement Input
# ============================================================================

class Requirement(BaseModel):
    """Raw requirement extracted from document"""
    requirement_id: str = Field(..., description="Unique identifier")
    original_text: str = Field(..., min_length=10, description="Original Vietnamese/English text")
    domain: Optional[str] = Field(None, description="Domain classification (hotel, ecommerce, etc)")
    language: Literal["vi", "en"] = Field("vi", description="Language detected")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Detection confidence")
    source_file: Optional[str] = None
    line_number: Optional[int] = None
    
    @field_validator('original_text')
    @classmethod
    def validate_not_heading(cls, v):
        """Reject headings and intro paragraphs"""
        headings = ['tài liệu này mô tả', 'giới thiệu', 'mục tiêu dự án', 'phạm vi']
        if any(h in v.lower() for h in headings):
            raise ValueError(f"Requirement appears to be a heading/intro: {v[:50]}")
        return v


# ============================================================================
# Stage 1: Refinement Output
# ============================================================================

class AcceptanceCriterion(BaseModel):
    """Single acceptance criterion in Given/When/Then format"""
    ac_id: str = Field(..., description="AC identifier (AC1, AC2, ...)")
    given: str = Field(..., min_length=5, description="Given context")
    when: str = Field(..., min_length=5, description="When action")
    then: str = Field(..., min_length=5, description="Then expected result")
    priority: SeverityLevel = Field(SeverityLevel.MEDIUM, description="AC priority")


class RefinementOutput(BaseModel):
    """Refined requirement with user story and structured AC"""
    requirement_id: str
    title: str = Field(..., min_length=5, max_length=200, description="Concise title")
    user_story: str = Field(..., description="As a... I want... so that...")
    acceptance_criteria: List[AcceptanceCriterion] = Field(
        ..., min_items=1, max_items=10, description="3-8 AC items recommended"
    )
    assumptions: List[str] = Field(default_factory=list, description="Assumptions made")
    constraints: List[str] = Field(default_factory=list, description="Technical/business constraints")
    non_functional_requirements: List[str] = Field(default_factory=list, description="NFRs extracted")
    changes_summary: str = Field("", description="What was refined/clarified")
    
    @field_validator('user_story')
    @classmethod
    def validate_user_story_format(cls, v):
        """Ensure user story follows proper format"""
        required_parts = ['as a', 'i want', 'so that', 'là một', 'tôi muốn']
        v_lower = v.lower()
        has_english = any(part in v_lower for part in ['as a', 'i want', 'so that'])
        has_vietnamese = any(part in v_lower for part in ['là một', 'tôi muốn'])
        if not (has_english or has_vietnamese):
            raise ValueError(f"User story must contain proper format")
        return v
    
    @field_validator('acceptance_criteria')
    @classmethod
    def validate_ac_count(cls, v):
        """Warn if AC count is not in recommended range"""
        if len(v) < 3:
            print(f"⚠️ Warning: Only {len(v)} AC items (recommended: 3-8)")
        elif len(v) > 8:
            print(f"⚠️ Warning: {len(v)} AC items (recommended: 3-8, consider splitting)")
        return v


# ============================================================================
# Stage 2: Gap Detection
# ============================================================================

class Gap(BaseModel):
    """Detected gap or issue in requirement"""
    gap_id: str = Field(..., description="Gap identifier")
    type: GapType = Field(..., description="Type of gap")
    severity: SeverityLevel = Field(..., description="Impact severity")
    description: str = Field(..., min_length=10, description="Gap description")
    question: str = Field(..., description="Question to ask Product Owner")
    suggestion: str = Field(..., description="Suggested resolution")
    detected_by: Literal["rule", "llm", "hybrid"] = Field("rule", description="Detection method")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Detection confidence")


class GapReport(BaseModel):
    """Complete gap analysis report"""
    requirement_id: str
    gaps: List[Gap] = Field(default_factory=list, description="Detected gaps")
    total_gaps: int = Field(0, description="Total gap count")
    critical_count: int = Field(0, description="Critical gaps")
    high_count: int = Field(0, description="High severity gaps")
    medium_count: int = Field(0, description="Medium severity gaps")
    low_count: int = Field(0, description="Low severity gaps")
    requires_clarification: bool = Field(False, description="Needs PO review")
    
    @model_validator(mode='after')
    def calculate_counts(self):
        """Auto-calculate gap counts and flag"""
        gaps = self.gaps
        self.total_gaps = len(gaps)
        self.critical_count = sum(1 for g in gaps if g.severity == SeverityLevel.CRITICAL)
        self.high_count = sum(1 for g in gaps if g.severity == SeverityLevel.HIGH)
        self.medium_count = sum(1 for g in gaps if g.severity == SeverityLevel.MEDIUM)
        self.low_count = sum(1 for g in gaps if g.severity == SeverityLevel.LOW)
        self.requires_clarification = (self.critical_count > 0 or self.high_count > 1)
        return self


# ============================================================================
# Stage 3: Smart Slicing + INVEST Scoring
# ============================================================================

class INVESTScore(BaseModel):
    """INVEST scoring for user stories"""
    independent: int = Field(..., ge=1, le=5, description="Can be done independently")
    negotiable: int = Field(..., ge=1, le=5, description="Open for discussion")
    valuable: int = Field(..., ge=1, le=5, description="Delivers value")
    estimable: int = Field(..., ge=1, le=5, description="Can be estimated")
    small: int = Field(..., ge=1, le=5, description="Small enough")
    testable: int = Field(..., ge=1, le=5, description="Can be tested")
    total: int = Field(0, ge=6, le=30, description="Total score")
    warnings: List[str] = Field(default_factory=list, description="INVEST warnings")
    
    @model_validator(mode='after')
    def calculate_total_and_warnings(self):
        """Calculate total and generate warnings"""
        scores = [
            self.independent,
            self.negotiable,
            self.valuable,
            self.estimable,
            self.small,
            self.testable
        ]
        self.total = sum(scores)
        
        warnings = []
        if self.independent < 3:
            warnings.append("Story has dependencies - consider splitting or reordering")
        if self.small < 3:
            warnings.append("Story too large - consider vertical slicing")
        if self.estimable < 3:
            warnings.append("Story unclear - needs more refinement")
        if self.testable < 3:
            warnings.append("Story lacks testability - add more specific AC")
        
        self.warnings = warnings
        return self


class Subtask(BaseModel):
    """Individual subtask (implementation unit)"""
    task_id: str = Field(..., description="Task identifier")
    title: str = Field(..., min_length=5, description="Task title")
    description: str = Field("", description="Task description")
    role: TaskRole = Field(..., description="Assigned role")
    type: RequirementType = Field(RequirementType.FUNCTIONAL, description="Task type")
    priority: str = Field("Medium", description="Priority level")
    estimate_hours: Optional[float] = Field(None, ge=0, description="Estimated hours")
    acceptance_criteria_refs: List[str] = Field(default_factory=list, description="Referenced AC IDs")


class UserStory(BaseModel):
    """User story with subtasks"""
    story_id: str = Field(..., description="Story identifier")
    title: str = Field(..., min_length=5, description="Story title")
    user_story: str = Field(..., description="Full user story text")
    acceptance_criteria_refs: List[str] = Field(..., description="Referenced AC IDs from refinement")
    subtasks: List[Subtask] = Field(..., min_items=1, description="Backend/Frontend/QA subtasks")
    invest_score: INVESTScore = Field(..., description="INVEST scoring")
    estimate_total_hours: Optional[float] = Field(None, description="Total estimated hours")


class Slice(BaseModel):
    """Story slice with rationale"""
    slice_id: str = Field(..., description="Slice identifier (S1, S2, ...)")
    rationale: SliceRationale = Field(..., description="Why this slice")
    description: str = Field(..., description="Slice description")
    stories: List[UserStory] = Field(..., min_items=1, description="Stories in this slice")
    warnings: List[str] = Field(default_factory=list, description="Slice warnings")
    priority_order: int = Field(1, ge=1, description="Implementation order")


class SlicingOutput(BaseModel):
    """Complete slicing output"""
    requirement_id: str
    slices: List[Slice] = Field(..., min_items=1, max_items=10, description="Story slices")
    total_stories: int = Field(0, description="Total user stories")
    total_subtasks: int = Field(0, description="Total subtasks")
    
    @model_validator(mode='after')
    def calculate_totals(self):
        """Calculate story and subtask counts"""
        slices = self.slices
        total_stories = sum(len(slice_obj.stories) for slice_obj in slices)
        total_subtasks = sum(
            len(story.subtasks) 
            for slice_obj in slices 
            for story in slice_obj.stories
        )
        self.total_stories = total_stories
        self.total_subtasks = total_subtasks
        return self


# ============================================================================
# Stage 4: Complete V2 Output
# ============================================================================

class Traceability(BaseModel):
    """Traceability links between artifacts"""
    requirement_to_stories: List[str] = Field(default_factory=list, description="req_id -> story_ids")
    story_to_tasks: List[str] = Field(default_factory=list, description="story_id -> task_ids")
    gaps_to_stories: List[str] = Field(default_factory=list, description="gap_id -> story_ids")


class QualityMetrics(BaseModel):
    """Quality metrics for the output"""
    schema_valid: bool = True
    refinement_score: float = Field(0.0, ge=0.0, le=1.0, description="Refinement quality")
    gap_coverage: float = Field(0.0, ge=0.0, le=1.0, description="Gap detection coverage")
    invest_avg_score: float = Field(0.0, ge=0.0, le=30.0, description="Average INVEST score")
    processing_time_seconds: float = Field(0.0, ge=0.0, description="Total processing time")


class RequirementV2Output(BaseModel):
    """Complete V2 output for a single requirement"""
    requirement_id: str
    original_requirement: str
    domain: str
    language: str
    
    # Stage outputs
    refinement: RefinementOutput
    gap_report: GapReport
    slicing: SlicingOutput
    traceability: Traceability
    quality_metrics: QualityMetrics
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    version: str = "2.0"


class BatchV2Output(BaseModel):
    """Batch processing output for multiple requirements"""
    requirements: List[RequirementV2Output]
    total_requirements: int
    total_stories: int
    total_subtasks: int
    total_gaps: int
    avg_invest_score: float
    processing_time_seconds: float
    summary: Dict[str, Any] = Field(default_factory=dict)
