"""
FastAPI Adapter - Smart AI Test Generator (v2 and v3 support)
Provides REST API endpoints for both v2 (rule-based) and v3 (hybrid LLM) generators
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os

# Import generators
from .smart_ai_generator_v2 import AITestGenerator as AITestGeneratorV2
from .smart_ai_generator_v3 import AITestGeneratorV3

router = APIRouter(prefix="/api/v1/tests", tags=["Test Generation"])

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class GenerateRequest(BaseModel):
    """Request to generate test cases"""
    requirements: List[str] = Field(
        ...,
        description="Requirements to generate test cases for",
        min_items=1,
        max_items=50
    )
    version: str = Field(
        default="v3",
        description="Generator version: 'v2' (rule-based) or 'v3' (hybrid LLM)",
        pattern="^(v2|v3)$"
    )
    max_tests_per_requirement: int = Field(
        default=5,
        ge=1,
        le=20.
    )
    enable_llm: Optional[bool] = Field(
        default=None,
        description="Force LLM off (v3 only)"
    )


class GenerationResponse(BaseModel):
    """Response with generated test cases"""
    status: str
    test_cases: List[Dict[str, Any]]
    summary: Dict[str, Any]
    generated_at: str


# ============================================================================
# GENERATORS (Singleton instances)
# ============================================================================

_generator_v2 = None
_generator_v3 = None


def get_generator_v2():
    """Lazy load v2 generator"""
    global _generator_v2
    if _generator_v2 is None:
        _generator_v2 = AITestGeneratorV2()
    return _generator_v2


def get_generator_v3(use_llm: bool = True):
    """Lazy load v3 generator"""
    global _generator_v3
    if _generator_v3 is None:
        _generator_v3 = AITestGeneratorV3(use_llm=use_llm)
    return _generator_v3


# ============================================================================
# ROUTES
# ============================================================================

@router.post("/generate", response_model=GenerationResponse)
async def generate_tests(request: GenerateRequest):
    """
    Generate test cases from requirements using v2 or v3 generator
    
    Choose generator:
    - **v2**: Rule-based, pattern matching, fast, reliable
    - **v3**: Hybrid LLM, semantic understanding, workflow-aware
    
    Example request:
    ```json
    {
      "requirements": [
        "Doctor must prescribe medication after checking allergies",
        "System must prevent duplicate appointments"
      ],
      "version": "v3",
      "max_tests_per_requirement": 5
    }
    ```
    """
    
    try:
        if request.version == "v2":
            # Generate with v2
            generator = get_generator_v2()
            result = generator.generate(request.requirements)
        
        else:  # v3
            # Determine LLM usage
            use_llm = request.enable_llm
            if use_llm is None:
                # Default to enabled if ANTHROPIC_API_KEY is set
                use_llm = bool(os.getenv("ANTHROPIC_API_KEY"))
            
            generator = get_generator_v3(use_llm=use_llm)
            result = generator.generate(
                request.requirements,
                max_tests_per_req=request.max_tests_per_requirement
            )
        
        return GenerationResponse(
            status=result.get("status", "success"),
            test_cases=result.get("test_cases", []),
            summary=result.get("summary", {}),
            generated_at=result.get("generated_at", "")
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {str(e)}"
        )


@router.post("/compare")
async def compare_versions(request: GenerateRequest):
    """
    Compare v2 and v3 generators on the same requirements
    Shows output differences and improvement metrics
    """
    
    try:
        result_v2 = None
        result_v3 = None
        
        # Generate with v2
        try:
            gen_v2 = get_generator_v2()
            result_v2 = gen_v2.generate(request.requirements)
        except Exception as e:
            result_v2 = {"error": str(e)}
        
        # Generate with v3
        try:
            use_llm = bool(os.getenv("ANTHROPIC_API_KEY"))
            gen_v3 = get_generator_v3(use_llm=use_llm)
            result_v3 = gen_v3.generate(
                request.requirements,
                max_tests_per_req=request.max_tests_per_requirement
            )
        except Exception as e:
            result_v3 = {"error": str(e)}
        
        # Analyze comparison
        comparison = {
            "v2": {
                "summary": result_v2.get("summary") if result_v2 else None,
                "sample_tests": result_v2.get("test_cases", [])[:2] if result_v2 else None
            },
            "v3": {
                "summary": result_v3.get("summary") if result_v3 else None,
                "sample_tests": result_v3.get("test_cases", [])[:2] if result_v3 else None
            },
            "improvements": {
                "quality_gain": None,
                "test_types_variety": None,
                "dependencies_tracked": False
            }
        }
        
        # Calculate improvements
        if result_v2 and result_v3:
            v2_quality = result_v2.get("summary", {}).get("avg_quality", 0)
            v3_quality = result_v3.get("summary", {}).get("avg_quality", 0)
            
            if v2_quality > 0:
                comparison["improvements"]["quality_gain"] = (
                    (v3_quality - v2_quality) / v2_quality
                )
            
            v2_types = len(result_v2.get("summary", {}).get("test_types_generated", []))
            v3_types = len(result_v3.get("summary", {}).get("test_types_generated", []))
            comparison["improvements"]["test_types_variety"] = v3_types - v2_types
            
            v3_test_count = len(result_v3.get("test_cases", []))
            deps_count = sum(
                1 for tc in result_v3.get("test_cases", [])
                if tc.get("dependencies")
            )
            comparison["improvements"]["dependencies_tracked"] = deps_count > 0
        
        return {
            "status": "success",
            "comparison": comparison
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Comparison failed: {str(e)}"
        )


@router.get("/info")
async def get_info():
    """Get information about available generators"""
    return {
        "api": "Smart AI Test Generator",
        "version": "3.0.0",
        "generators": {
            "v2": {
                "name": "Rule-Based Engine",
                "description": "Pattern-based test generation using regex and rules",
                "characteristics": [
                    "Fast (~100ms per requirement)",
                    "No external dependencies",
                    "Pattern matching (no semantic understanding)",
                    "Hardcoded test type loop"
                ]
            },
            "v3": {
                "name": "Hybrid LLM",
                "description": "Semantic understanding with LLM + rule-based engine",
                "characteristics": [
                    "Semantic parsing (Claude API)",
                    "Workflow dependency tracking",
                    "Confidence-aware scoring",
                    "Intelligent test type inference",
                    "Context-aware quality metrics"
                ]
            }
        },
        "endpoints": {
            "generate": "POST /api/v1/tests/generate - Generate test cases",
            "compare": "POST /api/v1/tests/compare - Compare v2 vs v3",
            "info": "GET /api/v1/tests/info - This endpoint"
        },
        "llm_config": {
            "api_key_set": bool(os.getenv("ANTHROPIC_API_KEY")),
            "llm_enabled": bool(os.getenv("ANTHROPIC_API_KEY")),
            "fallback_mode": not bool(os.getenv("ANTHROPIC_API_KEY"))
        }
    }


@router.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "version": "3.0.0"
    }


# ============================================================================
# Exports
# ============================================================================

__all__ = ["router"]
