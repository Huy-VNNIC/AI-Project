"""
V2 API - Step 5: Test Case Generation Endpoints
================================================

FastAPI endpoints for AI-powered test case generation.
Integrates with V2 task generation pipeline.

Endpoints:
- POST /api/v2/test-generation/generate-from-tasks
- POST /api/v2/test-generation/generate-from-file
- GET /api/v2/test-generation/export/{format}
- GET /api/v2/test-generation/coverage/{task_id}
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Path, Body
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional, Literal, List
import logging
import time
import hashlib
import json
from io import StringIO

from requirement_analyzer.task_gen.test_case_handler import TestCaseHandler
from requirement_analyzer.task_gen.test_case_generator import TestType

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v2/test-generation", tags=["V2 Test Generation"])

# Initialize test case handler WITH CUSTOM AI ENABLED
test_handler = TestCaseHandler(use_ai=True)
logger.info("✅ V2 Test Generation API initialized with Custom AI")

# Config
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB


@router.post("/generate-from-tasks")
async def generate_test_cases_from_tasks(
    tasks: List[dict] = Body(..., description="List of task objects"),
    user_stories: Optional[List[dict]] = Body(None, description="List of user stories"),
    acceptance_criteria: Optional[List[dict]] = Body(None, description="List of acceptance criteria"),
    include_types: Optional[List[str]] = Query(None, description="Specific test types to generate"),
    auto_export_format: Optional[str] = Query(None, description="Auto-export format (pytest, csv, junit)"),
):
    """
    Generate comprehensive test cases from tasks, user stories, and acceptance criteria
    
    Request body:
    {
        "tasks": [
            {
                "task_id": "TASK-001",
                "title": "User registration",
                "description": "Register new user",
                "priority": "High",
                "complexity": "Medium"
            }
        ],
        "user_stories": [...],
        "acceptance_criteria": [...]
    }
    
    Response:
    {
        "status": "success",
        "test_cases": [...],
        "summary": {...},
        "test_coverage": {...},
        "quality_metrics": {...}
    }
    """
    request_id = hashlib.md5(f"{time.time()}".encode()).hexdigest()[:8]
    logger.info(f"[{request_id}] Test case generation request: {len(tasks)} tasks")
    
    try:
        # Validate input
        if not tasks:
            raise HTTPException(
                status_code=422,
                detail="No tasks provided"
            )
        
        # Build API output format for handler
        api_output = {
            "tasks": tasks,
            "user_stories": user_stories or [],
            "acceptance_criteria": acceptance_criteria or []
        }
        
        # Generate test cases
        logger.info(f"[{request_id}] Generating test cases...")
        start_time = time.time()
        
        result = test_handler.generate_test_cases_from_pipeline(api_output)
        
        processing_time = time.time() - start_time
        
        # Add metadata
        result["request_id"] = request_id
        result["processing_time_seconds"] = round(processing_time, 3)
        result["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        logger.info(f"[{request_id}] Generated {result.get('total_test_cases', 0)} test cases in {processing_time:.2f}s")
        
        # Auto-export if requested
        if auto_export_format:
            result["export"] = _export_test_cases(result["test_cases"], auto_export_format)
        
        return JSONResponse(content=result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error generating test cases: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error generating test cases: {str(e)}"
        )


@router.post("/generate-from-file")
async def generate_test_cases_from_file(
    file: UploadFile = File(..., description="Requirements file"),
    include_types: Optional[List[str]] = Query(None, description="Specific test types to generate"),
):
    """
    Generate test cases from requirements file
    
    This endpoint:
    1. Parses the requirements file
    2. Runs V2 task generation pipeline
    3. Automatically generates test cases
    
    Returns complete test case suite
    """
    request_id = hashlib.md5(f"{time.time()}".encode()).hexdigest()[:8]
    logger.info(f"[{request_id}] Test generation from file: {file.filename}")
    
    try:
        # Read file
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: 2MB"
            )
        
        # Decode
        try:
            content_str = content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=422,
                detail="File must be UTF-8 encoded"
            )
        
        # For now, return placeholder
        # In production, would call V2 pipeline first, then test generation
        return JSONResponse(content={
            "request_id": request_id,
            "status": "success",
            "message": "File uploaded. Run task generation first, then test generation.",
            "file_name": file.filename,
            "file_size_bytes": len(content)
        })
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@router.post("/generate-test-cases")
async def generate_test_cases_from_requirements(
    requirements: str = Body(..., embed=True, description="Requirements text"),
    max_tests: Optional[int] = Body(50, embed=True, description="Maximum number of test cases"),
    threshold: Optional[float] = Body(0.5, embed=True, description="Confidence threshold (0-1)"),
):
    """
    Generate AI test cases from plain text requirements
    
    This is the main AI Test Case Generation endpoint.
    
    Features:
    - Parse requirements using spaCy NLP
    - Categorize into 7 test types
    - Estimate effort and automation feasibility
    - Identify security threats (OWASP)
    - Generate comprehensive test case suite
    
    Request:
    {
        "requirements": "The system shall allow users to login with email and password.\\nThe application must prevent SQL injection attacks.",
        "max_tests": 50,
        "threshold": 0.5
    }
    
    Response:
    {
        "status": "success",
        "test_cases": [...],
        "summary": {...},
        "generation_time": 12.45
    }
    """
    request_id = hashlib.md5(f"{time.time()}".encode()).hexdigest()[:8]
    logger.info(f"[{request_id}] Generate test cases from {len(requirements)} chars")
    
    try:
        if not requirements or requirements.strip() == "":
            raise HTTPException(
                status_code=422,
                detail="Requirements cannot be empty"
            )
        
        # Parse requirements into list
        req_list = [r.strip() for r in requirements.split('\n') if r.strip()]
        
        if not req_list:
            raise HTTPException(
                status_code=422,
                detail="No valid requirements found"
            )
        
        logger.info(f"[{request_id}] Processing {len(req_list)} requirements")
        
        start_time = time.time()
        
        # Generate test cases using V2 Pipeline (Production-Grade)
        from requirement_analyzer.task_gen.test_case_generator_v2 import AITestCaseGeneratorV2
        
        generator_v2 = AITestCaseGeneratorV2()
        results = generator_v2.generate(req_list, max_test_cases=max_tests, confidence_threshold=threshold)
        
        generation_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Format results
        test_cases = results.get("test_cases", [])
        summary = results["summary"].copy()
        summary["generation_time_ms"] = round(generation_time, 2)
        
        # Add effort analysis summary
        if test_cases:
            total_effort_hours = sum(tc.get("estimated_effort_hours", 0) for tc in test_cases)
            effort_details = {
                "total_effort_hours": round(total_effort_hours, 2),
                "avg_effort_hours": round(total_effort_hours / len(test_cases), 2),
                "min_effort_hours": round(min(tc.get("estimated_effort_hours", 0) for tc in test_cases), 2),
                "max_effort_hours": round(max(tc.get("estimated_effort_hours", 0) for tc in test_cases), 2),
                "effort_distribution": {
                    "quick": sum(1 for tc in test_cases if tc.get("effort", {}).get("category") == "quick"),
                    "light": sum(1 for tc in test_cases if tc.get("effort", {}).get("category") == "light"),
                    "medium": sum(1 for tc in test_cases if tc.get("effort", {}).get("category") == "medium"),
                    "heavy": sum(1 for tc in test_cases if tc.get("effort", {}).get("category") == "heavy"),
                    "very_heavy": sum(1 for tc in test_cases if tc.get("effort", {}).get("category") == "very_heavy"),
                    "epic": sum(1 for tc in test_cases if tc.get("effort", {}).get("category") == "epic"),
                }
            }
            summary["effort_analysis"] = effort_details
        
        if results.get("errors"):
            logger.warning(f"[{request_id}] Errors during generation: {results['errors']}")
        
        logger.info(f"[{request_id}] ✓ Generated {len(test_cases)} tests in {generation_time:.2f}ms using V2 Pipeline")
        
        return {
            "status": results.get("status", "success"),
            "test_cases": test_cases,
            "summary": summary,
            "generation_time": round(generation_time, 2),
            "errors": results.get("errors", [])
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error generating test cases: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@router.post("/generate-ai")
async def generate_test_cases_with_custom_ai(
    requirements: str = Body(..., embed=True, description="Requirements text"),
    max_tests: Optional[int] = Body(50, embed=True, description="Maximum test cases"),
    threshold: Optional[float] = Body(0.5, embed=True, description="Confidence threshold"),
):
    """
    🤖 CUSTOM AI TEST GENERATION
    ============================
    
    Uses the Intelligent AI system (AIIntelligentTestGenerator) that:
    - Performs deep NLP analysis with spaCy
    - Extracts entities and relationships  
    - Identifies edge cases intelligently
    - Generates specific, meaningful tests
    - Provides AI confidence scores
    
    This is SMARTER than template-based generation!
    
    Request:
    {
        "requirements": "User should be able to login with email and password",
        "max_tests": 20,
        "threshold": 0.6
    }
    
    Response includes:
    - test_cases with AI confidence
    - Requirement analysis (entities, relationships, conditions)
    - AI reasoning for each test
    - Complexity score
    """
    request_id = hashlib.md5(f"{time.time()}".encode()).hexdigest()[:8]
    logger.info(f"[{request_id}] 🤖 Custom AI Test Generation started")
    
    try:
        if not requirements or requirements.strip() == "":
            raise HTTPException(status_code=422, detail="Requirements cannot be empty")
        
        start_time = time.time()
        
        # Generate using Custom AI
        logger.info(f"[{request_id}] Using Custom AI: AIIntelligentTestGenerator")
        result = test_handler.generate_ai_test_cases_from_requirements(requirements)
        
        generation_time = (time.time() - start_time) * 1000
        
        logger.info(f"[{request_id}] ✅ Generated {result.get('summary', {}).get('total_test_cases', 0)} tests with Custom AI in {generation_time:.0f}ms")
        
        # Merge generation time
        result["generation_time"] = round(generation_time, 2)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] ❌ Custom AI generation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Custom AI Generation Error: {str(e)}"
        )


@router.post("/export/{format}")
async def export_test_cases(
    format: Literal["pytest", "csv", "junit", "json"],
    test_cases: List[dict] = Body(..., description="Test cases to export"),
):
    """
    Export test cases to various formats
    
    Supported formats:
    - pytest: Python pytest code
    - csv: CSV format for test management tools
    - junit: JUnit/TestNG XML format
    - json: Raw JSON format
    """
    request_id = hashlib.md5(f"{time.time()}".encode()).hexdigest()[:8]
    logger.info(f"[{request_id}] Exporting {len(test_cases)} test cases to {format}")
    
    try:
        if not test_cases:
            raise HTTPException(
                status_code=422,
                detail="No test cases provided"
            )
        
        exported_content = _export_test_cases(test_cases, format)
        
        # Return appropriate response based on format
        if format == "pytest":
            return {
                "status": "success",
                "format": "pytest",
                "content": exported_content,
                "language": "python",
                "file_extension": ".py"
            }
        elif format == "csv":
            return {
                "status": "success",
                "format": "csv",
                "content": exported_content,
                "file_extension": ".csv"
            }
        elif format == "junit":
            return {
                "status": "success",
                "format": "junit",
                "content": exported_content,
                "content_type": "text/xml",
                "file_extension": ".xml"
            }
        else:  # json
            return {
                "status": "success",
                "format": "json",
                "data": test_cases,
                "total_test_cases": len(test_cases)
            }
    
    except Exception as e:
        logger.error(f"[{request_id}] Export error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Export error: {str(e)}"
        )


@router.get("/coverage/{task_id}")
async def get_test_coverage(
    task_id: str = Path(..., description="Task ID to analyze"),
    test_cases: Optional[List[dict]] = Body(None, description="Test cases to analyze"),
):
    """
    Get test coverage metrics for a specific task
    
    Returns:
    - Coverage percentage
    - Number of test cases
    - Test types breakdown
    - Coverage gaps
    """
    try:
        if not test_cases:
            test_cases = []
        
        # Filter test cases for this task
        task_tests = [tc for tc in test_cases if tc.get('task_id') == task_id]
        
        # Calculate coverage
        return {
            "status": "success",
            "task_id": task_id,
            "total_test_cases": len(task_tests),
            "coverage": {
                "unit": sum(1 for tc in task_tests if tc.get('test_type') == 'Unit'),
                "integration": sum(1 for tc in task_tests if tc.get('test_type') == 'Integration'),
                "e2e": sum(1 for tc in task_tests if tc.get('test_type') == 'E2E'),
                "security": sum(1 for tc in task_tests if tc.get('test_type') == 'Security'),
                "performance": sum(1 for tc in task_tests if tc.get('test_type') == 'Performance'),
                "boundary": sum(1 for tc in task_tests if tc.get('test_type') == 'Boundary Value')
            }
        }
    
    except Exception as e:
        logger.error(f"Error calculating coverage: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0",
        "module": "Test Case Generation",
        "test_types_supported": [
            "Unit", "Integration", "E2E",
            "Boundary Value", "Decision Table",
            "Performance", "Security"
        ]
    }


# ============================================================================
# PURE ML TEST GENERATION V3 - AI LEARNING SYSTEM
# ============================================================================

# Initialize Pure ML adapter
from requirement_analyzer.pure_ml_api_adapter import PureMLAPIAdapter

pure_ml_adapter = PureMLAPIAdapter()
pure_ml_router = APIRouter(prefix="/api/v3/test-generation", tags=["V3 Pure ML Test Generation"])


@pure_ml_router.post("/generate")
async def generate_test_cases_pure_ml(
    requirements: str = Body(..., embed=True, description="Requirements text"),
    max_tests: Optional[int] = Body(10, embed=True, description="Maximum test cases"),
    confidence_threshold: Optional[float] = Body(0.5, embed=True, description="Min ML quality score"),
):
    """
    Generate test cases using Pure ML system (spaCy + Rule-based, no external API)
    
    ✨ Features:
    - Pure ML Parser (spaCy NER + rules)
    - ML-scored test scenarios
    - Learning feedback system
    - No external API required
    
    Request:
    {
        "requirements": "Patient can book appointments up to 30 days ahead.\\nPrevent unauthorized access to medical records.",
        "max_tests": 10,
        "confidence_threshold": 0.5
    }
    
    Response:
    {
        "status": "success",
        "test_cases": [...],
        "summary": {...},
        "has_learning": true
    }
    """
    request_id = hashlib.md5(f"{time.time()}".encode()).hexdigest()[:8]
    logger.info(f"[{request_id}] Pure ML generation from {len(requirements)} chars")
    
    try:
        if not requirements or requirements.strip() == "":
            raise HTTPException(status_code=422, detail="Requirements cannot be empty")
        
        start_time = time.time()
        
        # Use Pure ML adapter
        results = pure_ml_adapter.generate_test_cases(
            requirements_text=requirements,
            max_tests=max_tests,
            confidence_threshold=confidence_threshold
        )
        
        generation_time = (time.time() - start_time) * 1000
        results["summary"]["generation_time_ms"] = round(generation_time, 2)
        
        logger.info(f"[{request_id}] ✓ Generated {results['summary'].get('total_test_cases', 0)} tests in {generation_time:.2f}ms using Pure ML")
        
        return results
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Pure ML generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@pure_ml_router.post("/feedback")
async def submit_test_feedback(
    test_case_id: str = Body(..., description="Test case ID"),
    requirement_id: str = Body(..., description="Requirement ID"),
    scenario_type: str = Body(..., description="Scenario type"),
    user_feedback: str = Body(..., description="good|bad|needs_improvement"),
    test_execution_result: str = Body(..., description="pass|fail|not_executed"),
    defects_found: int = Body(0, description="Number of defects found"),
    coverage_rating: int = Body(3, description="Coverage 1-5"),
    clarity_rating: int = Body(3, description="Clarity 1-5"),
    effort_accuracy: int = Body(3, description="Effort accuracy 1-5"),
    comments: str = Body("", description="User comments"),
):
    """
    Submit feedback on generated test case
    System learns from this feedback to improve future generations
    
    💡 Learning enabled:
    - Feedback is collected and stored
    - Success rates are calculated per scenario type
    - System adjusts quality scores based on patterns
    - Recommendations generated for improvement
    """
    request_id = hashlib.md5(f"{time.time()}".encode()).hexdigest()[:8]
    logger.info(f"[{request_id}] Feedback submitted for {test_case_id}")
    
    try:
        result = pure_ml_adapter.submit_feedback(
            test_case_id=test_case_id,
            requirement_id=requirement_id,
            scenario_type=scenario_type,
            user_feedback=user_feedback,
            test_execution_result=test_execution_result,
            defects_found=defects_found,
            coverage_rating=coverage_rating,
            clarity_rating=clarity_rating,
            effort_accuracy=effort_accuracy,
            comments=comments
        )
        
        logger.info(f"[{request_id}] ✓ Feedback recorded, system learning enabled")
        return result
    
    except Exception as e:
        logger.error(f"[{request_id}] Feedback error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@pure_ml_router.get("/stats")
async def get_pure_ml_stats():
    """
    Get Pure ML system statistics
    
    Returns:
    - Generations count
    - Feedback statistics
    - Learning analysis
    - System health
    """
    try:
        result = pure_ml_adapter.get_system_stats()
        return result
    except Exception as e:
        logger.error(f"Stats error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@pure_ml_router.get("/insights")
async def get_pure_ml_insights():
    """
    Get AI learning insights
    
    Returns:
    - Success rates by scenario type
    - System strengths and weaknesses
    - Improvement recommendations
    - System health status
    """
    try:
        result = pure_ml_adapter.get_learning_insights()
        return result
    except Exception as e:
        logger.error(f"Insights error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# Helper function
def _export_test_cases(test_cases: List[dict], format: str) -> str:
    """Export test cases to specified format"""
    
    if format == "pytest":
        return test_handler.export_test_cases_to_pytest(test_cases)
    elif format == "csv":
        return test_handler.export_test_cases_to_csv(test_cases)
    elif format == "junit":
        return test_handler.export_test_cases_to_junit(test_cases)
    else:
        return json.dumps(test_cases, indent=2, ensure_ascii=False)
