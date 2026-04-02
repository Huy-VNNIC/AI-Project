"""
FastAPI application - REST API layer.

Endpoints:
  POST /generate         → upload file → trả về test cases JSON
  POST /generate/text    → raw text input → trả về test cases JSON
  POST /export/excel     → upload file → trả về file Excel
  GET  /health           → health check
  GET  /formats          → list supported formats
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add rule_based_system to path for imports
rule_based_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, rule_based_dir)

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Import from core modules
from core.pipeline import run_pipeline, run_pipeline_from_text
from exports.export_handler import export_json, export_excel


app = FastAPI(
    title="Rule-Based Test Case Generator",
    description="Tự động sinh test case từ requirement document (PDF, DOCX, TXT, Excel, User Story, Use Case)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────── MODELS ───────────────────────────

class TextRequest(BaseModel):
    text: str
    format: Optional[str] = "free_text"   # free_text | user_story | use_case

class GenerateResponse(BaseModel):
    success: bool
    format_detected: str
    summary: dict
    requirements: list
    test_cases: list


# ─────────────────────────── ENDPOINTS ───────────────────────────

@app.get("/")
def root():
    return {
        "message": "Rule-Based Test Case Generator API",
        "version": "1.0.0",
        "docs": "/docs",
        "supported_formats": ["free_text", "user_story", "use_case", "excel"],
        "supported_file_types": [".pdf", ".docx", ".txt", ".xlsx", ".csv"],
    }


@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/formats")
def list_formats():
    return {
        "supported_formats": [
            {"format": "free_text",   "description": "Văn bản tự do (PDF, DOCX, TXT)"},
            {"format": "user_story",  "description": "User Story: As a... I want... so that..."},
            {"format": "use_case",    "description": "Use Case document với Actor, Main Flow, Precondition"},
            {"format": "excel",       "description": "Bảng Excel/CSV với columns: requirement, actor, action..."},
        ],
        "supported_file_types": [".pdf", ".docx", ".txt", ".xlsx", ".csv"],
    }


@app.post("/generate", response_model=GenerateResponse)
async def generate_from_file(
    file: UploadFile = File(..., description="Requirement document"),
    force_format: Optional[str] = Form(None, description="Ép format: free_text|user_story|use_case|excel"),
):
    """
    Upload file requirement → tự động detect format → sinh test cases.
    """
    # Validate extension
    allowed = {".pdf", ".docx", ".txt", ".xlsx", ".csv", ".xls"}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"File type '{ext}' not supported. Allowed: {allowed}")

    # Lưu file tạm
    tmp_dir = tempfile.mkdtemp()
    tmp_path = os.path.join(tmp_dir, file.filename)

    try:
        content = await file.read()
        with open(tmp_path, "wb") as f:
            f.write(content)

        # Chạy pipeline
        result = run_pipeline(tmp_path, force_format=force_format)

        return {
            "success":         True,
            "format_detected": result["format_detected"],
            "summary":         result["summary"],
            "requirements":    result["requirements"],
            "test_cases":      result["test_cases"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


@app.post("/generate/text")
async def generate_from_text(request: TextRequest):
    """
    Gửi text thẳng (không cần file) → sinh test cases.
    Hữu ích để test nhanh hoặc tích hợp với hệ thống khác.
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text is empty")

    if len(request.text) > 50_000:
        raise HTTPException(status_code=400, detail="Text too long (max 50,000 chars)")

    try:
        result = run_pipeline_from_text(request.text, force_format=request.format)
        return {
            "success":         True,
            "format_detected": result["format_detected"],
            "summary":         result["summary"],
            "requirements":    result["requirements"],
            "test_cases":      result["test_cases"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


@app.post("/export/excel")
async def export_to_excel(
    file: UploadFile = File(...),
    force_format: Optional[str] = Form(None),
):
    """
    Upload file → sinh test cases → trả về file Excel để download.
    """
    allowed = {".pdf", ".docx", ".txt", ".xlsx", ".csv"}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"File type '{ext}' not supported")

    tmp_dir = tempfile.mkdtemp()
    tmp_input = os.path.join(tmp_dir, file.filename)
    tmp_output = os.path.join(tmp_dir, "test_cases.xlsx")

    try:
        content = await file.read()
        with open(tmp_input, "wb") as f:
            f.write(content)

        result = run_pipeline(tmp_input, force_format=force_format)
        test_cases = result["_objects"]["test_cases"]

        output_path = export_excel(test_cases, tmp_output)

        return FileResponse(
            path=output_path,
            filename=f"test_cases_{Path(file.filename).stem}.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    except Exception as e:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────── ENTRYPOINT ───────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
