"""
AI Test Generation API v3
=========================

FastAPI endpoints for AI-powered test case generation.

Uses real AI (NLP + ML), NOT templates.
Integrates with existing V2 pipeline.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime
import json

logger = logging.getLogger("ai_test_api_v3")

try:
    from .ai_test_handler import AITestGenerationHandler
except ImportError:
    logger.warning("Could not import ai_test_handler")
    AITestGenerationHandler = None


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class GenerateTestsRequest(BaseModel):
    """Request to generate tests"""
    task_id: str = Field(..., description="Task identifier")
    description: str = Field(..., description="Task/requirement description")
    acceptance_criteria: Optional[str] = Field(None, description="Optional acceptance criteria")


class BatchGenerateTestsRequest(BaseModel):
    """Request to generate tests for multiple tasks"""
    tasks: List[Dict[str, str]] = Field(..., description="List of tasks")


class TestCaseResponse(BaseModel):
    """Single test case response"""
    test_id: str
    title: str
    test_type: str
    priority: str
    scenario_type: str
    why_generated: str
    ai_confidence: float
    steps: List[Dict[str, Any]]


class RequirementAnalysisResponse(BaseModel):
    """Requirement analysis response"""
    entities: List[Dict[str, str]]
    relationships: List[Dict[str, str]]
    conditions: List[str]
    edge_cases: List[str]
    complexity: float


class GenerateTestsResponse(BaseModel):
    """Response from test generation"""
    status: str
    task_id: str
    requirement: str
    analysis: RequirementAnalysisResponse
    scenarios: List[Dict[str, Any]]
    test_cases: List[TestCaseResponse]
    summary: Dict[str, Any]
    generated_at: str


# ============================================================================
# API ROUTER
# ============================================================================

router = APIRouter(prefix="/api/v3/ai-tests", tags=["AI Test Generation v3"])

# Initialize handler
_handler = None


def get_handler():
    """Get or create handler"""
    global _handler
    if _handler is None:
        if AITestGenerationHandler is None:
            logger.error("AI Test Handler not available")
            raise HTTPException(status_code=500, detail="AI Test Handler not initialized")
        _handler = AITestGenerationHandler()
    return _handler


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/generate", response_model=GenerateTestsResponse)
async def generate_tests(request: GenerateTestsRequest):
    """
    Generate AI-powered test cases for a task.
    
    Uses intelligent AI to:
    - Analyze requirement using NLP
    - Extract test scenarios
    - Generate specific, meaningful test cases
    
    NOT template-based. Each test is tailored to actual requirement.
    """
    
    logger.info(f"📝 Generating tests for task: {request.task_id}")
    
    try:
        handler = get_handler()
        
        result = handler.generate_tests_for_task(
            task_id=request.task_id,
            task_description=request.description,
            acceptance_criteria=request.acceptance_criteria
        )
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Generation failed"))
        
        logger.info(f"✓ Generated {result['summary']['total_test_cases']} tests for {request.task_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating tests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-batch")
async def generate_tests_batch(request: BatchGenerateTestsRequest, 
                               background_tasks: BackgroundTasks):
    """
    Generate tests for multiple tasks in batch.
    
    Can handle large numbers of tasks.
    Returns job ID for tracking.
    """
    
    logger.info(f"📦 Starting batch generation for {len(request.tasks)} tasks")
    
    try:
        handler = get_handler()
        
        # Generate tests
        results = handler.generate_tests_for_multiple_tasks(request.tasks)
        
        # Generate report
        report = handler.get_summary_report(results)
        
        logger.info(f"✓ Batch complete. Generated {report['total_test_cases_generated']} tests")
        
        return {
            "status": "success",
            "batch_size": len(request.tasks),
            "results": results,
            "summary": report
        }
        
    except Exception as e:
        logger.error(f"Error in batch generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/requirement/analyze")
async def analyze_requirement(requirement: str = Query(..., description="Requirement text")):
    """
    Analyze a requirement without generating test cases.
    
    Returns:
    - Entities found
    - Relationships
    - Conditions
    - Edge cases
    - Complexity score
    """
    
    logger.info(f"🔍 Analyzing requirement...")
    
    try:
        handler = get_handler()
        
        # Generate full analysis
        result = handler.generate_tests_for_task(
            task_id="analysis",
            task_description=requirement
        )
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Analysis failed"))
        
        # Return just analysis part
        return {
            "requirement": requirement,
            "analysis": result.get("analysis", {}),
            "complexity_score": result.get("analysis", {}).get("complexity", 0),
            "edge_cases_identified": len(result.get("analysis", {}).get("edge_cases", [])),
            "validations_found": len(result.get("analysis", {}).get("validations", []))
        }
        
    except Exception as e:
        logger.error(f"Error analyzing requirement: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-scenarios/extract")
async def extract_test_scenarios(requirement: str = Query(..., description="Requirement text")):
    """
    Extract test scenarios from requirement.
    
    Returns possible test scenarios that should be covered:
    - Happy path scenario
    - Edge case scenarios
    - Error scenarios
    - Alternative flow scenarios
    """
    
    logger.info(f"📋 Extracting test scenarios...")
    
    try:
        handler = get_handler()
        
        result = handler.generate_tests_for_task(
            task_id="scenarios",
            task_description=requirement
        )
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Extraction failed"))
        
        return {
            "requirement": requirement,
            "scenarios": result.get("scenarios", []),
            "total_scenarios": len(result.get("scenarios", [])),
            "scenario_types": self._count_scenario_types(result.get("scenarios", []))
        }
        
    except Exception as e:
        logger.error(f"Error extracting scenarios: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/pytest")
async def export_as_pytest(request: GenerateTestsRequest):
    """
    Generate tests and export as pytest code.
    
    Returns: Python test code (pytest format)
    """
    
    logger.info(f"🐍 Generating pytest code for {request.task_id}...")
    
    try:
        handler = get_handler()
        
        result = handler.generate_tests_for_task(
            task_id=request.task_id,
            task_description=request.description,
            acceptance_criteria=request.acceptance_criteria
        )
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Export failed"))
        
        # Export as pytest
        pytest_code = handler.export_tests_as_pytest(result)
        
        return {
            "status": "success",
            "task_id": request.task_id,
            "format": "pytest",
            "code": pytest_code,
            "test_count": result["summary"]["total_test_cases"]
        }
        
    except Exception as e:
        logger.error(f"Error exporting as pytest: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/gherkin")
async def export_as_gherkin(request: GenerateTestsRequest):
    """
    Generate tests and export as Gherkin/BDD scenarios.
    
    Returns: Gherkin feature file content
    """
    
    logger.info(f"🥒 Generating Gherkin scenarios for {request.task_id}...")
    
    try:
        handler = get_handler()
        
        result = handler.generate_tests_for_task(
            task_id=request.task_id,
            task_description=request.description,
            acceptance_criteria=request.acceptance_criteria
        )
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Export failed"))
        
        # Export as Gherkin
        gherkin_code = handler.export_tests_as_gherkin(result)
        
        return {
            "status": "success",
            "task_id": request.task_id,
            "format": "gherkin",
            "content": gherkin_code,
            "scenario_count": len(result.get("scenarios", []))
        }
        
    except Exception as e:
        logger.error(f"Error exporting as gherkin: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    
    try:
        handler = get_handler()
        
        return {
            "status": "healthy",
            "ai_generator": "active" if handler else "inactive",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _count_scenario_types(scenarios: List[Dict[str, Any]]) -> Dict[str, int]:
    """Count scenarios by type"""
    counts = {}
    for scenario in scenarios:
        scenario_type = scenario.get("type", "unknown")
        counts[scenario_type] = counts.get(scenario_type, 0) + 1
    return counts


# ============================================================================
# INTEGRATION FUNCTIONS
# ============================================================================

def register_ai_test_router(app):
    """Register AI test generation router with FastAPI app"""
    app.include_router(router)
    logger.info("✓ AI Test Generation v3 router registered")


__all__ = [
    "router",
    "register_ai_test_router",
    "GenerateTestsRequest",
    "GenerateTestsResponse",
]
