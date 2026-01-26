"""
V2 API Endpoints for Requirements Engineering Pipeline
=======================================================

New endpoints that return V2 structured output with:
- Refinement (User Stories + AC)
- Gap Detection
- Smart Slicing
- INVEST Scoring
- Full Traceability

Maintains backward compatibility with V1 endpoints.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, Literal
import logging
import time
import hashlib
import json

from requirement_analyzer.task_gen.pipeline_v2 import V2Pipeline
from requirement_analyzer.task_gen.schemas_v2 import Requirement

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v2/task-generation", tags=["V2 Task Generation"])

# Initialize V2 pipeline
v2_pipeline = V2Pipeline()

# Config
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
ALLOWED_CONTENT_TYPES = ["text/plain", "text/markdown", "application/octet-stream"]


def extract_requirements_from_content(content: str) -> list[Requirement]:
    """Extract requirements from file content"""
    lines = content.split('\n')
    requirements = []
    req_counter = 0
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        # Skip empty, headings, intro
        if not line or line.startswith('#') or len(line) < 20:
            continue
        
        skip_keywords = [
            'tài liệu này', 'giới thiệu', 'mục tiêu', 'phạm vi',
            'this document', 'introduction', 'project goal'
        ]
        if any(kw in line.lower() for kw in skip_keywords):
            continue
        
        # Detect language
        has_vietnamese = any(ord(c) > 127 for c in line)
        language = "vi" if has_vietnamese else "en"
        
        req_counter += 1
        req = Requirement(
            requirement_id=f"REQ{req_counter:03d}",
            original_text=line,
            domain="unknown",
            language=language,
            confidence=0.9,
            line_number=line_num
        )
        requirements.append(req)
    
    return requirements


@router.post("/generate-from-file")
async def generate_v2_from_file(
    file: UploadFile = File(...),
    mode: Literal["batch", "single"] = Query("batch", description="Processing mode"),
    max_requirements: Optional[int] = Query(None, ge=1, le=500, description="Max requirements to process"),
    enable_llm: bool = Query(False, description="Enable LLM for refinement/gaps (future)"),
):
    """
    V2 API: Generate tasks from requirements file with full RE pipeline
    
    Returns:
    - refinement: User Stories with AC
    - gap_report: Detected gaps
    - slicing: Smart slices with INVEST scores
    - tasks: Backend/Frontend/QA subtasks
    - traceability: Full chain
    - quality_metrics: Processing metrics
    """
    request_id = hashlib.md5(f"{time.time()}".encode()).hexdigest()[:8]
    logger.info(f"[{request_id}] V2 API request: {file.filename}")
    
    try:
        # Validate file size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {MAX_FILE_SIZE/(1024*1024):.1f}MB"
            )
        
        # Validate content type
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            logger.warning(f"[{request_id}] Unusual content type: {file.content_type}")
        
        # Decode content
        try:
            content_str = content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=422,
                detail="File must be UTF-8 encoded text"
            )
        
        # Extract requirements
        logger.info(f"[{request_id}] Extracting requirements...")
        requirements = extract_requirements_from_content(content_str)
        
        if not requirements:
            raise HTTPException(
                status_code=422,
                detail="No valid requirements found in file"
            )
        
        # Limit if requested
        if max_requirements:
            requirements = requirements[:max_requirements]
        
        logger.info(f"[{request_id}] Processing {len(requirements)} requirements with V2 pipeline")
        
        # Process with V2 pipeline
        start_time = time.time()
        batch_output = v2_pipeline.process_batch(requirements)
        processing_time = time.time() - start_time
        
        # Build response
        response = {
            "request_id": request_id,
            "version": "2.0",
            "status": "success",
            "summary": {
                "total_requirements": batch_output.total_requirements,
                "total_stories": batch_output.total_stories,
                "total_subtasks": batch_output.total_subtasks,
                "total_gaps": batch_output.total_gaps,
                "critical_gaps": batch_output.summary["critical_gaps_count"],
                "high_gaps": batch_output.summary["high_gaps_count"],
                "avg_invest_score": round(batch_output.avg_invest_score, 2),
                "success_rate": round(batch_output.summary["success_rate"], 2),
                "processing_time_seconds": round(processing_time, 3)
            },
            "requirements": []
        }
        
        # Add detailed requirement outputs
        for req_output in batch_output.requirements:
            req_data = {
                "requirement_id": req_output.requirement_id,
                "original_text": req_output.original_requirement,
                "domain": req_output.domain,
                "language": req_output.language,
                
                # Refinement
                "refinement": {
                    "title": req_output.refinement.title,
                    "user_story": req_output.refinement.user_story,
                    "acceptance_criteria": [
                        {
                            "id": ac.ac_id,
                            "given": ac.given,
                            "when": ac.when,
                            "then": ac.then,
                            "priority": ac.priority.value
                        }
                        for ac in req_output.refinement.acceptance_criteria
                    ],
                    "assumptions": req_output.refinement.assumptions,
                    "constraints": req_output.refinement.constraints,
                    "nfrs": req_output.refinement.non_functional_requirements
                },
                
                # Gaps
                "gap_report": {
                    "total_gaps": req_output.gap_report.total_gaps,
                    "requires_clarification": req_output.gap_report.requires_clarification,
                    "severity_breakdown": {
                        "critical": req_output.gap_report.critical_count,
                        "high": req_output.gap_report.high_count,
                        "medium": req_output.gap_report.medium_count,
                        "low": req_output.gap_report.low_count
                    },
                    "gaps": [
                        {
                            "id": gap.gap_id,
                            "type": gap.type.value,
                            "severity": gap.severity.value,
                            "description": gap.description,
                            "question": gap.question,
                            "suggestion": gap.suggestion,
                            "detected_by": gap.detected_by,
                            "confidence": gap.confidence
                        }
                        for gap in req_output.gap_report.gaps
                    ]
                },
                
                # Slicing
                "slicing": {
                    "total_stories": req_output.slicing.total_stories,
                    "total_subtasks": req_output.slicing.total_subtasks,
                    "slices": [
                        {
                            "id": slice_obj.slice_id,
                            "rationale": slice_obj.rationale.value,
                            "description": slice_obj.description,
                            "priority_order": slice_obj.priority_order,
                            "warnings": slice_obj.warnings,
                            "stories": [
                                {
                                    "id": story.story_id,
                                    "title": story.title,
                                    "user_story": story.user_story,
                                    "ac_refs": story.acceptance_criteria_refs,
                                    "invest_score": {
                                        "independent": story.invest_score.independent,
                                        "negotiable": story.invest_score.negotiable,
                                        "valuable": story.invest_score.valuable,
                                        "estimable": story.invest_score.estimable,
                                        "small": story.invest_score.small,
                                        "testable": story.invest_score.testable,
                                        "total": story.invest_score.total,
                                        "grade": "Excellent" if story.invest_score.total >= 25 else "Good" if story.invest_score.total >= 20 else "Fair",
                                        "warnings": story.invest_score.warnings
                                    },
                                    "estimate_hours": story.estimate_total_hours,
                                    "subtasks": [
                                        {
                                            "id": task.task_id,
                                            "title": task.title,
                                            "description": task.description,
                                            "role": task.role.value,
                                            "type": task.type.value,
                                            "priority": task.priority,
                                            "estimate_hours": task.estimate_hours,
                                            "ac_refs": task.acceptance_criteria_refs
                                        }
                                        for task in story.subtasks
                                    ]
                                }
                                for story in slice_obj.stories
                            ]
                        }
                        for slice_obj in req_output.slicing.slices
                    ]
                },
                
                # Traceability
                "traceability": {
                    "requirement_to_stories": req_output.traceability.requirement_to_stories,
                    "story_to_tasks": req_output.traceability.story_to_tasks,
                    "gaps_to_stories": req_output.traceability.gaps_to_stories
                },
                
                # Quality metrics
                "quality_metrics": {
                    "refinement_score": round(req_output.quality_metrics.refinement_score, 2),
                    "gap_coverage": round(req_output.quality_metrics.gap_coverage, 2),
                    "invest_avg_score": round(req_output.quality_metrics.invest_avg_score, 2),
                    "processing_time_seconds": round(req_output.quality_metrics.processing_time_seconds, 4)
                }
            }
            
            response["requirements"].append(req_data)
        
        logger.info(f"[{request_id}] V2 processing complete: {batch_output.total_stories} stories, {batch_output.total_subtasks} tasks, {batch_output.total_gaps} gaps")
        
        return JSONResponse(content=response)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] V2 API error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0",
        "pipeline": "Requirements Engineering with GenAI"
    }
