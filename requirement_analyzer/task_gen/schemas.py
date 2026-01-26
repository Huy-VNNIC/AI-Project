"""
Task Generation Module - Pydantic Schemas
Define chuẩn output format cho tasks
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


class TaskSource(BaseModel):
    """Metadata về nguồn gốc của task"""
    sentence: str = Field(..., description="Original requirement sentence")
    section: Optional[str] = Field(None, description="Section header if available")
    doc_offset: Optional[List[int]] = Field(None, description="Character offset [start, end] in document")
    line_number: Optional[int] = Field(None, description="Line number in document")


class GeneratedTask(BaseModel):
    """Schema chuẩn cho một task được sinh ra"""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique task ID")
    epic: Optional[str] = Field(None, description="Epic/Module name")
    module: Optional[str] = Field(None, description="Sub-module name")
    title: str = Field(..., description="Task title (action-oriented)")
    description: str = Field(..., description="Detailed task description")
    acceptance_criteria: List[str] = Field(default_factory=list, description="List of acceptance criteria")
    
    # Labels
    type: str = Field("functional", description="Type: functional, security, interface, data, performance, etc.")
    priority: str = Field("Medium", description="Priority: Low, Medium, High")
    domain: str = Field("general", description="Domain: ecommerce, iot, healthcare, education, finance, general")
    role: str = Field("Backend", description="Role: Backend, Frontend, QA, DevOps, BA, Security, etc.")
    labels: List[str] = Field(default_factory=list, description="Additional tags/labels")
    
    # Estimation
    story_points: Optional[int] = Field(None, description="Fibonacci story points: 1,2,3,5,8,13,21")
    estimated_hours: Optional[float] = Field(None, description="Estimated hours")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence score [0-1]")
    complexity: Optional[str] = Field(None, description="Complexity: Simple, Medium, Complex")
    
    # Source tracking
    source: Optional[TaskSource] = Field(None, description="Source requirement metadata")
    
    # Dependencies (optional)
    dependencies: List[str] = Field(default_factory=list, description="List of task IDs this depends on")
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generator_version: str = Field("1.0.0", description="Task generator version")
    
    @validator('priority')
    def validate_priority(cls, v):
        valid = ['Low', 'Medium', 'High', 'Critical']
        if v not in valid:
            return 'Medium'
        return v
    
    @validator('story_points')
    def validate_story_points(cls, v):
        if v is None:
            return v
        valid_points = [1, 2, 3, 5, 8, 13, 21, 34]
        if v not in valid_points:
            # Map to nearest Fibonacci
            for i, p in enumerate(valid_points):
                if v <= p:
                    return p
            return 21
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TaskGenerationRequest(BaseModel):
    """Request model for task generation API"""
    text: str = Field(..., description="Requirement document text")
    max_tasks: int = Field(50, ge=1, le=500, description="Maximum number of tasks to generate")
    mode: str = Field("template", description="Generation mode: template, rag, finetune")
    include_story_points: bool = Field(True, description="Whether to estimate story points")
    domain_hint: Optional[str] = Field(None, description="Domain hint if known")
    epic_name: Optional[str] = Field(None, description="Epic/project name")
    requirement_threshold: Optional[float] = Field(0.5, ge=0.0, le=1.0, description="Requirement detection threshold")


class TaskGenerationResponse(BaseModel):
    """Response model for task generation API"""
    tasks: List[GeneratedTask] = Field(..., description="List of generated tasks")
    total_tasks: int = Field(..., description="Total number of tasks generated")
    
    # Aggregated stats
    stats: Dict[str, Any] = Field(default_factory=dict, description="Statistics about generated tasks")
    
    # Metadata
    processing_time: float = Field(..., description="Processing time in seconds")
    generator_version: str = Field("1.0.0")
    mode: str = Field("template")
    
    # Optional estimation
    total_story_points: Optional[int] = Field(None)
    estimated_duration_days: Optional[float] = Field(None)
    
    @validator('stats', pre=True, always=True)
    def compute_stats(cls, v, values):
        if 'tasks' not in values:
            return v
        
        tasks = values['tasks']
        stats = {
            'type_distribution': {},
            'priority_distribution': {},
            'domain_distribution': {},
            'role_distribution': {},
            'avg_confidence': 0.0,
            'total_story_points': 0
        }
        
        for task in tasks:
            # Count distributions
            stats['type_distribution'][task.type] = stats['type_distribution'].get(task.type, 0) + 1
            stats['priority_distribution'][task.priority] = stats['priority_distribution'].get(task.priority, 0) + 1
            stats['domain_distribution'][task.domain] = stats['domain_distribution'].get(task.domain, 0) + 1
            stats['role_distribution'][task.role] = stats['role_distribution'].get(task.role, 0) + 1
            
            # Sum story points
            if task.story_points:
                stats['total_story_points'] += task.story_points
        
        # Average confidence
        if tasks:
            stats['avg_confidence'] = sum(t.confidence for t in tasks) / len(tasks)
        
        return stats


class TaskFeedback(BaseModel):
    """Feedback on a generated task (for learning loop)"""
    task_id: str
    accepted: bool = Field(..., description="Whether task was accepted by user")
    edited_task: Optional[GeneratedTask] = Field(None, description="User's edited version")
    comment: Optional[str] = Field(None, description="User feedback comment")
    time_spent_seconds: Optional[int] = Field(None, description="Time user spent reviewing/editing")
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
