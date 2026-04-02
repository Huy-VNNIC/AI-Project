"""
Router for unified test & task generation endpoints
This router bridges both systems (requirement_analyzer and rule_based_system)
"""

from fastapi import APIRouter, HTTPException, Form
from pydantic import BaseModel
from typing import Optional
import httpx
import json

router = APIRouter(prefix="/api/unified", tags=["unified"])

# API endpoints
ANALYZER_API = "http://localhost:8000"
TESTGEN_API = "http://localhost:8001"


class UnifiedRequest(BaseModel):
    """Unified request for both systems"""
    text: str
    format: Optional[str] = "free_text"
    analyze: bool = True  # Run requirement analyzer
    generate: bool = True  # Run test generator


class UnifiedResponse(BaseModel):
    """Unified response from both systems"""
    success: bool
    analyzer_result: Optional[dict] = None
    testgen_result: Optional[dict] = None
    errors: list = []


@router.get("/health")
async def unified_health():
    """Check health of both systems"""
    health_status = {
        "analyzer": None,
        "testgen": None,
        "both_online": False
    }
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Check Analyzer
            try:
                resp = await client.get(f"{ANALYZER_API}/health")
                health_status["analyzer"] = resp.status_code == 200
            except:
                health_status["analyzer"] = False
            
            # Check Test Generator
            try:
                resp = await client.get(f"{TESTGEN_API}/health")
                health_status["testgen"] = resp.status_code == 200
            except:
                health_status["testgen"] = False
            
            health_status["both_online"] = health_status["analyzer"] and health_status["testgen"]
    except:
        health_status["both_online"] = False
    
    return health_status


@router.post("/generate", response_model=UnifiedResponse)
async def unified_generate(request: UnifiedRequest):
    """
    Generate test cases using both systems
    
    Returns results from both analyzer and test generator
    """
    errors = []
    analyzer_result = None
    testgen_result = None
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Run Requirement Analyzer
            if request.analyze:
                try:
                    data = {
                        "text": request.text,
                        "format": request.format
                    }
                    resp = await client.post(
                        f"{ANALYZER_API}/api/v3/generate",
                        data=data
                    )
                    if resp.status_code == 200:
                        analyzer_result = resp.json()
                    else:
                        errors.append(f"Analyzer error: {resp.status_code}")
                except Exception as e:
                    errors.append(f"Analyzer error: {str(e)}")
            
            # Run Test Generator
            if request.generate:
                try:
                    data = {
                        "text": request.text,
                        "format": request.format
                    }
                    resp = await client.post(
                        f"{TESTGEN_API}/generate/text",
                        json=data
                    )
                    if resp.status_code == 200:
                        testgen_result = resp.json()
                    else:
                        errors.append(f"Test Generator error: {resp.status_code}")
                except Exception as e:
                    errors.append(f"Test Generator error: {str(e)}")
    
    except Exception as e:
        errors.append(f"Unified generation error: {str(e)}")
    
    return UnifiedResponse(
        success=len(errors) == 0,
        analyzer_result=analyzer_result,
        testgen_result=testgen_result,
        errors=errors
    )


@router.post("/compare")
async def compare_results(request: UnifiedRequest):
    """
    Compare results from both systems
    Returns side-by-side analysis
    """
    # First generate from both
    unified_resp = await unified_generate(request)
    
    if not unified_resp.success:
        raise HTTPException(status_code=500, detail="Failed to generate results")
    
    # Compare test case counts, types, etc
    analyzer_tests = unified_resp.analyzer_result.get("test_cases", []) if unified_resp.analyzer_result else []
    testgen_tests = unified_resp.testgen_result.get("test_cases", []) if unified_resp.testgen_result else []
    
    return {
        "analyzer": {
            "test_count": len(analyzer_tests),
            "test_cases": analyzer_tests[:5]  # First 5 for preview
        },
        "testgen": {
            "test_count": len(testgen_tests),
            "test_cases": testgen_tests[:5]  # First 5 for preview
        },
        "comparison": {
            "total_unique_tests": len(set([t.get("id") for t in analyzer_tests + testgen_tests])),
            "coverage_overlap": "Analysis pending..."
        }
    }


@router.get("/formats")
async def get_supported_formats():
    """Get supported formats from test generator"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{TESTGEN_API}/formats")
            if resp.status_code == 200:
                return resp.json()
    except:
        pass
    
    return {
        "supported_formats": [
            {"format": "free_text", "description": "Free text requirements"},
            {"format": "user_story", "description": "User story format"},
            {"format": "use_case", "description": "Use case format"},
        ]
    }


@router.get("/status")
async def get_system_status():
    """Get detailed system status"""
    health = await unified_health()
    
    return {
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "systems": {
            "requirement_analyzer": {
                "url": ANALYZER_API,
                "port": 8000,
                "status": "online" if health["analyzer"] else "offline"
            },
            "test_generator": {
                "url": TESTGEN_API,
                "port": 8001,
                "status": "online" if health["testgen"] else "offline"
            }
        },
        "overall_status": "online" if health["both_online"] else "degraded",
        "features": {
            "unified_generation": health["both_online"],
            "analyzer_only": health["analyzer"],
            "testgen_only": health["testgen"]
        }
    }
