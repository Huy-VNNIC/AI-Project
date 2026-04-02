"""
API Adapter for LLM-Free AI Pipeline
Direct integration of structured intent extraction + domain-specific test generation
"""
import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import asdict

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from requirement_analyzer.task_gen.test_generation_pipeline import TestGenerationPipeline
from requirement_analyzer.task_gen.requirement_extractor import MockRequirementExtractor
from requirement_analyzer.task_gen.structured_intent import DomainType


class LLMFreeAPIAdapter:
    """Adapter between FastAPI and LLM-Free Pipeline"""
    
    def __init__(self, custom_extractor=None):
        """
        Initialize adapter with optional custom AI model
        
        Args:
            custom_extractor: Optional custom RequirementExtractor instance with user's AI model
        """
        extractor = custom_extractor or MockRequirementExtractor()
        self.pipeline = TestGenerationPipeline(extractor=extractor)
        self.generated_count = 0
        self.last_quality = 0.8
        
    def generate_tests(
        self,
        requirements_text: str,
        max_tests: int = 50,
        quality_threshold: float = 0.5,
        auto_deduplicate: bool = True,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Generate tests from requirements text
        
        Args:
            requirements_text: User's requirement document (Vietnamese or English)
            max_tests: Maximum test cases to return
            quality_threshold: Minimum confidence score (0-1)
            auto_deduplicate: Enable automatic deduplication
            verbose: Enable detailed logging
            
        Returns:
            API response with test cases and metadata
        """
        start_time = time.time()
        
        try:
            # Split requirements into lines (one requirement per line)
            requirements = [
                line.strip() 
                for line in requirements_text.split('\n') 
                if line.strip() and not line.strip().startswith('#')
            ]
            
            if not requirements:
                return {
                    'status': 'error',
                    'message': 'No requirements found in input',
                    'test_cases': [],
                    'summary': {
                        'requirements_processed': 0,
                        'test_cases_generated': 0,
                        'unique_tests_final': 0,
                        'quality_score': 0.0
                    },
                    'generated_at': datetime.now().isoformat()
                }
            
            # Process through pipeline
            result = self.pipeline.process_requirements(
                requirements=requirements,
                auto_deduplicate=auto_deduplicate,
                verbose=verbose
            )
            
            # Filter by quality threshold
            filtered_tests = [
                test for test in result['test_cases']
                if test.get('ml_quality_score', 0.5) >= quality_threshold
            ]
            
            # Limit to max_tests
            final_tests = filtered_tests[:max_tests]
            
            # Calculate statistics
            latency_ms = int((time.time() - start_time) * 1000)
            avg_confidence = (
                sum(t.get('ml_quality_score', 0.5) for t in final_tests) / len(final_tests)
                if final_tests else 0.5
            )
            avg_effort = (
                sum(t.get('effort_hours', 0.0) for t in final_tests) / len(final_tests)
                if final_tests else 0.0
            )
            
            # Count test types
            test_types = {}
            domain_types = {}
            for test in final_tests:
                test_type = test.get('test_type', 'functional')
                test_types[test_type] = test_types.get(test_type, 0) + 1
                
                domain = test.get('domain', 'general')
                domain_types[domain] = domain_types.get(domain, 0) + 1
            
            self.generated_count += len(final_tests)
            self.last_quality = avg_confidence
            
            return {
                'status': 'success',
                'test_cases': final_tests,
                'summary': {
                    'requirements_processed': len(requirements),
                    'test_cases_generated': result['summary']['test_cases_generated'],
                    'test_cases_deduplicated': result['summary'].get('test_cases_deduplicated', 0),
                    'unique_tests_final': len(final_tests),
                    'latency_ms': latency_ms,
                    'avg_confidence': round(avg_confidence, 2),
                    'avg_effort_hours': round(avg_effort, 2),
                    'quality_score': round(avg_confidence, 2),
                    'test_type_distribution': test_types,
                    'domain_distribution': domain_types,
                    'quality_gates': {
                        'passed': len([t for t in final_tests if t.get('ml_quality_score', 0.5) >= 0.7]),
                        'marginal': len([t for t in final_tests if 0.5 <= t.get('ml_quality_score', 0.5) < 0.7]),
                        'failed': len([t for t in final_tests if t.get('ml_quality_score', 0.5) < 0.5])
                    }
                },
                'generated_at': datetime.now().isoformat(),
                'system': 'llm-free-ai',
                'mode': 'smart-ner'
            }
            
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            return {
                'status': 'error',
                'message': str(e),
                'test_cases': [],
                'summary': {
                    'requirements_processed': 0,
                    'test_cases_generated': 0,
                    'unique_tests_final': 0,
                    'latency_ms': latency_ms,
                    'quality_score': 0.0
                },
                'generated_at': datetime.now().isoformat(),
                'system': 'llm-free-ai'
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            'total_tests_generated': self.generated_count,
            'avg_quality': round(self.last_quality, 2),
            'system': 'llm-free-ai',
            'mode': 'smart-ner-vietnamese-optimized'
        }


# Singleton instance
_adapter = None


def get_llmfree_adapter(custom_extractor=None) -> LLMFreeAPIAdapter:
    """Get or create LLM-Free adapter instance"""
    global _adapter
    if _adapter is None:
        _adapter = LLMFreeAPIAdapter(custom_extractor=custom_extractor)
    return _adapter


# ============================================================================
# FASTAPI ROUTER - For API exposure
# ============================================================================
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


class GenerateTestsRequest(BaseModel):
    """Request body for test generation endpoint"""
    requirements: str = Field(
        ...,
        description="Requirement text (Vietnamese or English, one per line)"
    )
    max_tests: int = Field(
        default=50,
        ge=1,
        le=200,
        description="Maximum test cases to generate"
    )
    quality_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum confidence score (0-1)"
    )
    auto_deduplicate: bool = Field(
        default=True,
        description="Enable automatic deduplication"
    )


class GenerateTestsResponse(BaseModel):
    """Response body for test generation endpoint"""
    status: str
    test_cases: List[Dict[str, Any]]
    summary: Dict[str, Any]
    generated_at: str
    system: str = "llm-free-ai"


# Create router with correct prefix
router = APIRouter(
    prefix="/api/v3/test-generation",
    tags=["Test Generation v3 - LLM-Free"]
)


@router.post("/generate", response_model=GenerateTestsResponse)
async def generate_tests_endpoint(request: GenerateTestsRequest):
    """
    Generate test cases from requirements using LLM-Free AI Pipeline
    
    Features:
    - No external APIs or LLM calls
    - Domain-aware test generation (hotel, banking, healthcare, e-commerce)
    - Automatic deduplication (semantic similarity)
    - Vietnamese language support
    - Real metrics (not hardcoded)
    
    Example request:
    ```json
    {
      "requirements": "Hệ thống phải cho phép đặt phòng mới\\nHệ thống phải kiểm tra tính khả dụng của phòng"
    }
    ```
    """
    try:
        adapter = get_llmfree_adapter()
        result = adapter.generate_tests(
            requirements_text=request.requirements,
            max_tests=request.max_tests,
            quality_threshold=request.quality_threshold,
            auto_deduplicate=request.auto_deduplicate
        )
        
        if result['status'] == 'error':
            raise HTTPException(
                status_code=400,
                detail=result.get('message', 'Test generation failed')
            )
        
        return result
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Test generation error: {str(e)}"
        )


@router.get("/stats")
async def get_stats():
    """Get test generation statistics"""
    adapter = get_llmfree_adapter()
    return adapter.get_stats()


# For testing
if __name__ == '__main__':
    adapter = LLMFreeAPIAdapter()
    
    # Test with Vietnamese requirements
    test_reqs = """
Hệ thống phải cho phép đặt phòng mới với các thông tin: loại phòng, ngày check-in, ngày check-out, thông tin khách hàng
Hệ thống phải kiểm tra tính khả dụng của phòng theo loại và ngày
Hệ thống phải hỗ trợ xác nhận, hủy, và chỉnh sửa đơn đặt phòng
"""
    
    result = adapter.generate_tests(test_reqs, max_tests=10)
    print(f"✅ Generated {result['summary']['unique_tests_final']} tests")
    print(f"   Quality: {result['summary']['avg_confidence']}")
    print(f"   Domains: {result['summary']['domain_distribution']}")
