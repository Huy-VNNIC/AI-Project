"""
FastAPI Main Application
REST API for Rule-Based Test Case Generator
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import tempfile
import os

# Import our modules
from input_processor import InputProcessor
from text_preprocessor import TextPreprocessor
from sentence_segmenter import SentenceSegmenter
from semantic_extractor import SemanticExtractor
from normalizer import Normalizer
from requirement_structurer import RequirementStructurer
from test_generator import TestGenerator
from export_handler import ExportHandler


# ============================================================================
# Pydantic Models
# ============================================================================

class GenerateTestsRequest(BaseModel):
    """Request to generate test cases"""
    requirements_text: str
    export_format: str = "json"  # json, excel, csv, markdown
    max_tests_per_requirement: int = 10


class TestCaseResponse(BaseModel):
    """Response with generated test cases"""
    status: str
    total_requirements: int
    total_test_cases: int
    test_cases: list
    export_url: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str


# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="Rule-Based Test Case Generator",
    description="Generate test cases from requirements using NLP + rule-based engine",
    version="1.0.0"
)


# ============================================================================
# Initialization
# ============================================================================

# Initialize all components lazily
_extractor = None
_normalizer = None
_structurer = None
_generator = None


def get_extractor() -> SemanticExtractor:
    """Get semantic extractor instance"""
    global _extractor
    if _extractor is None:
        _extractor = SemanticExtractor()
    return _extractor


def get_normalizer() -> Normalizer:
    """Get normalizer instance"""
    global _normalizer
    if _normalizer is None:
        _normalizer = Normalizer()
    return _normalizer


def get_structurer() -> RequirementStructurer:
    """Get structurer instance"""
    global _structurer
    if _structurer is None:
        _structurer = RequirementStructurer()
    return _structurer


def get_generator() -> TestGenerator:
    """Get test generator instance"""
    global _generator
    if _generator is None:
        _generator = TestGenerator()
    return _generator


# ============================================================================
# API Routes
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="Rule-Based Test Case Generator is running"
    )


@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "name": "Rule-Based Test Case Generator",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "generate_from_text": "/api/generate",
            "generate_from_file": "/api/generate-file",
            "docs": "/docs"
        }
    }


@app.post("/api/generate")
async def generate_from_text(request: GenerateTestsRequest) -> JSONResponse:
    """
    Generate test cases from requirement text
    
    Args:
        request: Request with requirements text
        
    Returns:
        Generated test cases
    """
    try:
        # Step 1: Preprocess
        print("📝 Preprocessing text...")
        preprocessor = TextPreprocessor()
        cleaned_text = preprocessor.process(request.requirements_text)
        
        # Step 2: Segment sentences
        print("✂️ Segmenting sentences...")
        segmenter = SentenceSegmenter()
        requirement_sentences = segmenter.segment(cleaned_text)
        
        if not requirement_sentences:
            raise ValueError("No requirements found in input text")
        
        # Step 3: Extract semantic information
        print("🧠 Extracting semantic information...")
        extractor = get_extractor()
        extracted_reqs = []
        
        for sent in requirement_sentences:
            try:
                extracted = extractor.extract(sent)
                extracted_reqs.append(extracted)
            except Exception as e:
                print(f"⚠️ Error extracting {sent}: {e}")
                continue
        
        if not extracted_reqs:
            raise ValueError("Could not extract semantic information from requirements")
        
        # Step 4: Normalize
        print("🔄 Normalizing...")
        normalizer = get_normalizer()
        normalized_reqs = [normalizer.normalize(req) for req in extracted_reqs]
        
        # Step 5: Structure
        print("🔧 Structuring requirements...")
        structurer = get_structurer()
        structured_reqs = structurer.structure_batch(normalized_reqs)
        
        # Step 6: Generate tests
        print("🧪 Generating test cases...")
        generator = get_generator()
        test_cases = generator.generate_batch(structured_reqs)
        
        # Limit test cases
        if len(test_cases) > request.max_tests_per_requirement * len(structured_reqs):
            test_cases = test_cases[:request.max_tests_per_requirement * len(structured_reqs)]
        
        # Step 7: Export
        print(f"📤 Exporting in {request.export_format} format...")
        
        if request.export_format == "json":
            test_data = [tc.to_dict() for tc in test_cases]
            return JSONResponse(content={
                "status": "success",
                "total_requirements": len(structured_reqs),
                "total_test_cases": len(test_cases),
                "test_cases": test_data
            })
        
        elif request.export_format == "excel":
            excel_bytes = ExportHandler.to_excel_bytes(test_cases)
            return StreamingResponse(
                iter([excel_bytes]),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": "attachment; filename=test_cases.xlsx"}
            )
        
        elif request.export_format == "csv":
            # Convert to CSV string
            import io
            csv_buffer = io.StringIO()
            ExportHandler.to_csv(test_cases, csv_buffer)
            
            return StreamingResponse(
                iter([csv_buffer.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=test_cases.csv"}
            )
        
        elif request.export_format == "markdown":
            md_content = ExportHandler.to_markdown(test_cases)
            return StreamingResponse(
                iter([md_content]),
                media_type="text/markdown",
                headers={"Content-Disposition": "attachment; filename=test_cases.md"}
            )
        
        else:
            raise ValueError(f"Unsupported export format: {request.export_format}")
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")


@app.post("/api/generate-file")
async def generate_from_file(
    file: UploadFile = File(...),
    export_format: str = Query("json", description="Export format: json, excel, csv, markdown")
):
    """
    Generate test cases from uploaded file (PDF, DOCX, TXT)
    
    Args:
        file: Uploaded file
        export_format: Export format
        
    Returns:
        Generated test cases
    """
    try:
        # Read file
        print(f"📂 Reading file: {file.filename}")
        file_content = await file.read()
        
        # Extract text
        file_ext = file.filename.split(".")[-1].lower()
        processor = InputProcessor()
        requirements_text = processor.extract_from_bytes(file_content, file_ext)
        
        # Delegate to text endpoint
        request = GenerateTestsRequest(
            requirements_text=requirements_text,
            export_format=export_format
        )
        
        return await generate_from_text(request)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")


@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    return {
        "status": "ready",
        "components": {
            "input_processor": "✓",
            "text_preprocessor": "✓",
            "sentence_segmenter": "✓",
            "semantic_extractor": "✓",
            "normalizer": "✓",
            "requirement_structurer": "✓",
            "test_generator": "✓",
            "export_handler": "✓",
        },
        "supported_formats": ["json", "excel", "csv", "markdown"],
        "supported_input_formats": ["pdf", "docx", "txt"],
    }


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("\n" + "="*70)
    print("🚀 Rule-Based Test Case Generator Started")
    print("="*70)
    print("\n📡 Initializing components...")
    
    try:
        get_extractor()
        print("✓ Semantic Extractor loaded")
    except Exception as e:
        print(f"⚠️ Semantic Extractor: {e}")
    
    get_normalizer()
    print("✓ Normalizer ready")
    
    get_structurer()
    print("✓ Requirement Structurer ready")
    
    get_generator()
    print("✓ Test Generator ready")
    
    print("\n📚 API Documentation: http://localhost:8000/docs")
    print("="*70 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("\n👋 Shutting down Rule-Based Test Case Generator\n")


# ============================================================================
# Run
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
