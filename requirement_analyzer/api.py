"""
API cho service phân tích requirements và ước lượng nỗ lực
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Body, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import Response as StarletteResponse
from io import BytesIO
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
import uvicorn
import os
import sys
import tempfile
import threading
import time
import pandas as pd
import json
import logging
from pathlib import Path

# Thiết lập logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("requirement_analyzer.api")

# Thêm thư mục gốc vào sys.path để import các module khác
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import các module cần thiết
try:
    from requirement_analyzer.analyzer import RequirementAnalyzer
except ImportError as e:
    logger.warning(f"Could not import RequirementAnalyzer (spacy compatibility): {e}")
    RequirementAnalyzer = None

from requirement_analyzer.estimator import EffortEstimator
from requirement_analyzer.task_integration import get_integration
from requirement_analyzer.utils import preprocess_text_for_estimation, improve_confidence_level
from requirement_analyzer.api_v2_handler import V2TaskGenerator

# ── Task-gen singleton (thread-safe pre-warmed instance) ──────────────────────
_task_gen_lock = threading.Lock()
_task_gen_instance: Optional[V2TaskGenerator] = None
_task_gen_ready = False
_task_gen_error: Optional[str] = None
_task_gen_startup_time: Optional[float] = None


def get_task_generator() -> V2TaskGenerator:
    """Return the module-level singleton. Raises 503 if not yet initialised."""
    if not _task_gen_ready:
        raise HTTPException(
            status_code=503,
            detail="Task generation model is still loading. Retry in a few seconds."
        )
    if _task_gen_error:
        raise HTTPException(
            status_code=503,
            detail=f"Task generation model failed to load: {_task_gen_error}"
        )
    return _task_gen_instance


def _init_task_generator():
    """Background initialisation – called once at startup."""
    global _task_gen_instance, _task_gen_ready, _task_gen_error, _task_gen_startup_time
    t0 = time.time()
    try:
        logger.info("[TaskGen] Initialising V2TaskGenerator…")
        inst = V2TaskGenerator()
        # Warm up priority classifier with a trivial inference
        try:
            from requirement_analyzer.task_gen.smart_priority import get_priority_classifier
            clf = get_priority_classifier()
            clf.predict("The system shall allow users to login securely")
            logger.info("[TaskGen] Priority classifier warmed up ✓")
        except Exception as e:
            logger.warning(f"[TaskGen] Priority warm-up skipped: {e}")
        with _task_gen_lock:
            _task_gen_instance = inst
            _task_gen_ready = True
            _task_gen_startup_time = round(time.time() - t0, 2)
        logger.info(f"[TaskGen] V2TaskGenerator ready in {_task_gen_startup_time}s ✓")
    except Exception as exc:
        with _task_gen_lock:
            _task_gen_error = str(exc)
            _task_gen_ready = False
        logger.error(f"[TaskGen] Failed to initialise V2TaskGenerator: {exc}", exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan: warm-up models before accepting requests."""
    # Run initialisation in a background thread so uvicorn loop stays responsive
    thread = threading.Thread(target=_init_task_generator, daemon=True, name="taskgen-init")
    thread.start()
    logger.info("[Startup] Task gen initialisation started in background thread")
    yield
    logger.info("[Shutdown] API shutting down")

# Model cho request API
class RequirementText(BaseModel):
    text: str
    method: Optional[str] = "weighted_average"

class TaskList(BaseModel):
    tasks: List[Dict[str, Any]]
    method: Optional[str] = "weighted_average"


class DependencyAIRequest(BaseModel):
    """Build a dependency-AI graph from a list of stories.

    Each story should expose at least: ``title`` or ``user_story``,
    optionally ``story_points`` and ``sprint``.
    """
    stories: List[Dict[str, Any]]
    language: Optional[str] = None


class WhatIfRequest(BaseModel):
    """Simulate moving one story to a different sprint."""
    stories: List[Dict[str, Any]]
    story_id: str
    new_sprint: int
    language: Optional[str] = None

class COCOMOParameters(BaseModel):
    # Software Size
    software_size: Optional[float] = 10.0  # KLOC
    sizing_method: Optional[str] = "source_lines_of_code"
    
    # SLDC Parameters
    sloc_a: Optional[float] = 5.0
    sloc_b: Optional[float] = 1.0
    sloc_mode: Optional[str] = "SLOC"
    
    # SCED and RCDX
    sced_percent: Optional[float] = 6.0
    rcdx_percent: Optional[float] = 15.0
    
    # Reuse Parameters
    design_modified: Optional[float] = 0.0
    code_modified: Optional[float] = 0.0
    integration_required: Optional[float] = 0.0
    assessment_assimilation: Optional[float] = 0.0
    software_understanding: Optional[float] = 0.0
    unfamiliarity: Optional[float] = 0.0
    
    # Software Scale Drivers
    precedentedness: Optional[str] = "nominal"  # very_low, low, nominal, high, very_high, extra_high
    development_flexibility: Optional[str] = "nominal"
    architecture_risk_resolution: Optional[str] = "nominal"
    team_cohesion: Optional[str] = "nominal"
    process_maturity: Optional[str] = "nominal"
    
    # Software Cost Drivers - Product
    required_software_reliability: Optional[str] = "nominal"
    database_size: Optional[str] = "nominal"
    product_complexity: Optional[str] = "nominal"
    developed_for_reusability: Optional[str] = "nominal"
    documentation_match: Optional[str] = "nominal"
    
    # Software Cost Drivers - Personnel
    analyst_capability: Optional[str] = "nominal"
    programmer_capability: Optional[str] = "nominal"
    personnel_continuity: Optional[str] = "nominal"
    application_experience: Optional[str] = "nominal"
    platform_experience: Optional[str] = "nominal"
    language_toolset_experience: Optional[str] = "nominal"
    
    # Software Cost Drivers - Platform
    time_constraint: Optional[str] = "nominal"
    storage_constraint: Optional[str] = "nominal"
    platform_volatility: Optional[str] = "nominal"
    
    # Software Cost Drivers - Project
    use_of_software_tools: Optional[str] = "nominal"
    multisite_development: Optional[str] = "nominal"
    required_development_schedule: Optional[str] = "nominal"
    
    # Labor Rate
    cost_per_person_month: Optional[float] = 5000.0
    
    # Estimation Method
    method: Optional[str] = "weighted_average"

# Khởi tạo FastAPI app
app = FastAPI(
    title="Software Effort Estimation API",
    description="API để phân tích yêu cầu phần mềm và ước lượng nỗ lực phát triển",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khởi tạo các thành phần
analyzer = RequirementAnalyzer()
estimator = EffortEstimator()

# Jinja2 templates
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

# Import and register V2 test case generation router
try:
    from requirement_analyzer.api_v2_test_generation import router as test_gen_router
    app.include_router(test_gen_router, tags=["Test Case Generation"])
    logger.info("✓ V2 Test Case Generation router registered")
except Exception as e:
    logger.warning(f"Could not register test case generation router: {e}")

# Import and register Pure ML test generation router
try:
    from requirement_analyzer.api_v2_test_generation import pure_ml_router
    app.include_router(pure_ml_router, tags=["Pure ML Test Generation"])
    logger.info("✓ Pure ML Test Generation router registered")
except Exception as e:
    logger.warning(f"Could not register Pure ML router: {e}")

# Import and register Test Case UI router
try:
    from requirement_analyzer.routers_testcase import router as testcase_ui_router
    app.include_router(testcase_ui_router, tags=["Test Case UI"])
    logger.info("✓ Test Case UI router registered")
except Exception as e:
    logger.warning(f"Could not register Test Case UI router: {e}")

# Register QA Studio v3 (4-stage pipeline)
try:
    from requirement_analyzer.routers_qa_studio import router as qa_studio_router
    app.include_router(qa_studio_router, tags=["QA Pipeline v3"])
    logger.info("✓ QA Studio v3 router registered")
except Exception as e:
    logger.warning(f"Could not register QA Studio v3 router: {e}")

# Import and register Test Routes (multiple test pages)
try:
    from app.routers import test_routes
    app.include_router(test_routes.router, tags=["testing"])
    logger.info("✓ Test Routes router registered (/test/...)")
except Exception as e:
    logger.warning(f"Could not register Test Routes router: {e}")

# Import and register Test Case Router (advanced test case generation)
try:
    from app.routers import testcase
    app.include_router(testcase.router, tags=["testcase"])
    logger.info("✓ Test Case Router registered (/testcase/...)")
except Exception as e:
    logger.warning(f"Could not register Test Case Router: {e}")

@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/testcase-generation")
async def testcase_generation():
    """Serve AI Test Case Generation UI"""
    testcase_file = Path(__file__).parent.parent / "templates" / "testcase_generation_neumorphism.html"
    if testcase_file.exists():
        return FileResponse(testcase_file, media_type="text/html")
    # Fallback to old version if new one doesn't exist
    testcase_file_old = Path(__file__).parent / "templates" / "testcase_generation.html"
    if testcase_file_old.exists():
        return FileResponse(testcase_file_old, media_type="text/html")
    raise HTTPException(status_code=404, detail="Test Case Generator not found")


@app.get("/analysis-dashboard")
async def analysis_dashboard():
    """Serve modern Analysis Results Dashboard (Linear/Notion-style)."""
    dash_file = Path(__file__).parent.parent / "templates" / "analysis_dashboard.html"
    if dash_file.exists():
        return FileResponse(dash_file, media_type="text/html")
    raise HTTPException(status_code=404, detail="Analysis Dashboard not found")

@app.get("/favicon.ico")
async def favicon():
    """Serve favicon to prevent 404 errors"""
    favicon_path = Path(__file__).parent / "static" / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(favicon_path)
    # Return empty response if favicon doesn't exist
    return JSONResponse(content={}, status_code=204)

@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring
    """
    return {"status": "healthy", "service": "ai-estimation-api"}

@app.post("/estimate")
def estimate_effort_simple(req: RequirementText):
    """
    Endpoint đơn giản để ước lượng effort từ văn bản requirements
    """
    try:
        # Sử dụng method được chỉ định hoặc mặc định
        method = req.method if req.method else "weighted_average"
        
        # Tạo advanced_params với method
        advanced_params = {"method": method}
        
        # Ước lượng effort
        result = estimator.integrated_estimate(req.text, advanced_params=advanced_params)
        response = JSONResponse(content=result)
        # Add CORS headers manually for API endpoints
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
    except Exception as e:
        logger.error(f"Error in estimate_effort_simple: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
def analyze_requirements(req: RequirementText):
    """
    Phân tích tài liệu yêu cầu và trả về kết quả phân tích
    """
    try:
        # Phân tích văn bản
        analysis = analyzer.analyze_requirements_document(req.text)
        return JSONResponse(content=analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    """
    Ước lượng nỗ lực từ tài liệu yêu cầu
    """
    try:
        # Tiền xử lý và làm sạch văn bản
        text = preprocess_text_for_estimation(req.text)
        
        # Phân tích và ước lượng
        result = estimator.estimate_from_requirements(text, req.method)
        
        # Cải thiện độ tin cậy dựa trên chất lượng và độ dài của yêu cầu
        result = improve_confidence_level(result, text)
        
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error estimating effort: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-requirements")
async def upload_requirements(file: UploadFile = File(...), method: str = Form("weighted_average")):
    """
    Tải lên tài liệu yêu cầu và ước lượng nỗ lực
    
    Supported formats:
    - .txt, .md: Plain text files
    - .pdf: PDF documents
    - .doc, .docx: Microsoft Word documents
    """
    try:
        # Import parser here to avoid circular imports
        from requirement_analyzer.document_parser import DocumentParser
        
        # Kiểm tra định dạng file
        filename = file.filename
        allowed_extensions = ['.txt', '.doc', '.docx', '.pdf', '.md']
        
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file format. Please upload one of: {', '.join(allowed_extensions)}"
            )
            
        # Đọc file
        content = await file.read()
        
        # Parse the document based on file type
        try:
            parser = DocumentParser()
            text = parser.parse(content, filename)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error parsing document: {str(e)}")
        
        # Check if any text was extracted
        if not text or text.strip() == "":
            raise HTTPException(status_code=400, detail="No text content found in the document")
        
        # Tiền xử lý văn bản để cải thiện chất lượng
        text = preprocess_text_for_estimation(text)
        
        # Phân tích và ước lượng
        result = estimator.estimate_from_requirements(text, method)
        
        # Cải thiện độ tin cậy dựa trên chất lượng và độ dài của yêu cầu
        result = improve_confidence_level(result, text)
        
        # Add document info to result
        result["document"] = {
            "filename": filename,
            "file_type": file_ext,
            "size_bytes": len(content),
            "text_length": len(text)
        }
        
        response = JSONResponse(content=result)
        # Add CORS headers
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/estimate-from-tasks")
def estimate_from_tasks(tasks: TaskList):
    """
    Ước lượng nỗ lực từ danh sách công việc (tasks)
    """
    try:
        # Chuyển đổi tasks thành văn bản yêu cầu
        requirements_text = "Requirements Document\n\n"
        
        # Thêm thông tin tổng quan về project
        requirements_text += "Project Overview:\n"
        requirements_text += "This project consists of " + str(len(tasks.tasks)) + " requirements/tasks.\n\n"
        
        total_complexity = 0
        for i, task in enumerate(tasks.tasks):
            title = task.get("title", f"Task {i+1}")
            description = task.get("description", "")
            priority = task.get("priority", "Medium")
            complexity = task.get("complexity", "Medium")
            
            # Convert complexity to numeric value for estimation
            complexity_value = {"Low": 1, "Medium": 2, "High": 3}.get(complexity, 2)
            total_complexity += complexity_value
            
            requirements_text += f"Requirement {i+1}: {title}\n"
            requirements_text += f"Description: {description}\n"
            requirements_text += f"Priority: {priority}\n"
            requirements_text += f"Complexity: {complexity}\n\n"
        
        # Add estimated code size based on tasks and complexity
        avg_complexity = total_complexity / len(tasks.tasks) if tasks.tasks else 2
        estimated_loc = int(len(tasks.tasks) * 500 * avg_complexity)
        requirements_text += f"\nExpected Size:\nEstimated code size: {estimated_loc} lines of code\n"
        
        # Tiền xử lý và làm sạch văn bản
        processed_text = preprocess_text_for_estimation(requirements_text)
        
        # Phân tích và ước lượng
        result = estimator.estimate_from_requirements(processed_text, tasks.method)
        
        # Cải thiện độ tin cậy dựa trên chất lượng và số lượng tasks
        result = improve_confidence_level(result, processed_text)
        
        # Thêm thông tin tasks vào kết quả
        result["tasks"] = tasks.tasks
        
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error estimating from tasks: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Task Generation API Endpoints
@app.get("/api/task-generation/status")
async def task_generation_status():
    """Health check for task generation service (shows warm-up status)"""
    return {
        "status": "ready" if _task_gen_ready else ("error" if _task_gen_error else "loading"),
        "service": "task-generation",
        "mode": "model",
        "model_ready": _task_gen_ready,
        "startup_time_s": _task_gen_startup_time,
        "error": _task_gen_error,
    }

@app.get("/api/task-generation/health")
async def task_generation_health():
    """
    Readiness probe for task generation service.
    Returns 200 when the model is fully loaded, 503 while loading.
    """
    if not _task_gen_ready:
        raise HTTPException(
            status_code=503,
            detail=f"Model loading{'... (error: ' + _task_gen_error + ')' if _task_gen_error else '...'}"
        )
    return {
        "status": "healthy",
        "model_ready": True,
        "startup_time_s": _task_gen_startup_time,
        "priority_classes": 4,
        "fibonacci": [1, 2, 3, 5, 8, 13, 21],
        "supported_formats": [".txt", ".md", ".pdf", ".docx", ".rst"],
    }

@app.post("/api/task-generation/generate")
async def generate_tasks_from_text(requirement: RequirementText):
    """
    Generate tasks from requirement text using V2 Pipeline
    
    Features:
    - Proper Agile User Story format (As a... I want... So that...)
    - Task decomposition into multiple subtasks
    - Specific Given/When/Then acceptance criteria
    - Functional vs Non-functional requirement distinction
    - INVEST scoring for story quality
    """
    try:
        # Use pre-warmed singleton (raises 503 if still loading)
        generator = get_task_generator()

        # Parse optional sprint_weeks from request body
        sprint_weeks = None
        if hasattr(requirement, 'sprint_weeks'):
            sprint_weeks = requirement.sprint_weeks

        # Process through V2 pipeline (language auto-detected)
        result = generator.generate_from_text(
            text=requirement.text,
            language=None,       # auto-detect
            sprint_weeks=sprint_weeks,
        )

        return result
    except Exception as e:
        logger.error(f"Error generating tasks with V2 pipeline: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/task-generation/generate-from-file")
async def generate_tasks_from_file(file: UploadFile = File(...)):
    """
    Generate tasks from uploaded requirement file using V2 Pipeline.
    Supports: .txt, .md, .pdf, .docx (text extraction)
    """
    ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx", ".doc", ".rst"}
    MAX_FILE_SIZE_MB = 5

    # Validate file type
    filename = file.filename or "upload.txt"
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    try:
        content = await file.read()

        # Enforce size limit
        if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail=f"File too large (max {MAX_FILE_SIZE_MB} MB)"
            )

        # Extract text based on format
        text_content = _extract_text_from_upload(content, ext, filename)

        if not text_content or len(text_content.strip()) < 20:
            raise HTTPException(
                status_code=422,
                detail="Could not extract usable text from the file. Please check the file content."
            )

        generator = get_task_generator()
        result = generator.generate_from_text(text=text_content, language=None)
        result["filename"] = filename
        result["file_size_bytes"] = len(content)
        result["extracted_chars"] = len(text_content)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating tasks from file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ── Dependency AI endpoints ──────────────────────────────────────────────
@app.post("/api/task-generation/dependency-ai")
async def dependency_ai_analyze(payload: DependencyAIRequest):
    """Run :class:`DependencyAI` over an externally-supplied story list.

    Returns the full graph (nodes, edges, critical path, bottlenecks,
    risk scores, validation issues, recommendations).  Useful when the
    UI already has stories cached and just wants the analytics.
    """
    try:
        generator = get_task_generator()
        result = generator._compute_dependency_ai(payload.stories)
        return result
    except Exception as e:
        logger.error(f"DependencyAI analyze failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/task-generation/dependency-ai/what-if")
async def dependency_ai_what_if(payload: WhatIfRequest):
    """Simulate moving ``story_id`` to ``new_sprint``.

    Returns the resolved/introduced violations and net delta without
    mutating the persisted plan.
    """
    try:
        from requirement_analyzer.task_gen.semantic import (
            SemanticParser, DependencyAI, StoryNode,
        )
        from requirement_analyzer.task_gen.semantic.embedding import auto_backend
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Semantic engine not available: {e}",
        )

    parser = SemanticParser()
    nodes = []
    for idx, s in enumerate(payload.stories):
        text = ((s.get("title") or "") + ". "
                + (s.get("user_story") or "")).strip(". ").strip()
        if not text:
            continue
        try:
            ir = parser.parse(text)
        except Exception:
            continue
        nodes.append(StoryNode(
            story_id=str(s.get("id") or s.get("task_id") or f"S{idx + 1}"),
            ir=ir,
            sprint=s.get("sprint"),
            story_points=int(s.get("story_points") or 0) or None,
            title=s.get("title") or s.get("user_story", "")[:80],
        ))

    if not nodes:
        raise HTTPException(status_code=422, detail="No parseable stories")

    try:
        embed = auto_backend()
    except Exception:
        embed = None
    ai = DependencyAI(embedding_backend=embed).build(nodes)

    if payload.story_id not in ai.nodes:
        raise HTTPException(
            status_code=404,
            detail=f"story_id '{payload.story_id}' not found",
        )

    return ai.what_if(payload.story_id, payload.new_sprint)


def _extract_text_from_upload(content: bytes, ext: str, filename: str) -> str:
    """Extract plain text from uploaded file content."""
    if ext in (".txt", ".md", ".rst"):
        # Try UTF-8 first, fall back to latin-1
        for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
            try:
                return content.decode(enc)
            except (UnicodeDecodeError, LookupError):
                continue
        return content.decode("latin-1", errors="replace")

    if ext == ".pdf":
        try:
            import io
            import pdfplumber
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                pages = [page.extract_text() or "" for page in pdf.pages]
            return "\n".join(pages)
        except ImportError:
            pass
        # Fallback: try PyPDF2
        try:
            import io
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError:
            raise HTTPException(
                status_code=422,
                detail="PDF parsing requires 'pdfplumber' or 'PyPDF2'. Install with: pip install pdfplumber"
            )

    if ext in (".docx", ".doc"):
        try:
            import io
            import docx
            doc = docx.Document(io.BytesIO(content))
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except ImportError:
            raise HTTPException(
                status_code=422,
                detail="DOCX parsing requires 'python-docx'. Install with: pip install python-docx"
            )

    # Generic fallback
    return content.decode("utf-8", errors="replace")


@app.get("/api/task-generation/history")
async def get_task_history(limit: int = 20):
    """
    Get list of recent task generation sessions.
    Returns session summaries (no task payload).
    """
    try:
        from requirement_analyzer.task_gen.task_history import list_history
        return {"sessions": list_history(limit=limit)}
    except Exception as e:
        logger.error(f"Error getting task history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/task-generation/history/{session_id}")
async def get_task_history_session(session_id: str):
    """
    Get a specific task generation session by session_id.
    """
    try:
        from requirement_analyzer.task_gen.task_history import get_history_session
        record = get_history_session(session_id)
        if record is None:
            raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
        return record
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting history session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/task-generation/history/{session_id}")
async def delete_task_history_session(session_id: str):
    """
    Delete a task generation history session.
    """
    try:
        from requirement_analyzer.task_gen.task_history import delete_history_session
        deleted = delete_history_session(session_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
        return {"status": "deleted", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/task-generation/reliability-report")
async def get_reliability_report():
    """
    Return the AI model reliability validation report.
    Covers: dataset transparency, model comparison (7 models), Cohen's Kappa.
    """
    from pathlib import Path
    import json
    report_path = Path(__file__).parent / "models" / "task_gen" / "models" / "reliability_report.json"
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Reliability report not found. Run validate_reliability.py first.")
    return json.loads(report_path.read_text())


@app.post("/trello-import")
def import_from_trello(data: Dict[str, Any] = Body(...)):
    """
    Import và ước lượng nỗ lực từ dữ liệu Trello
    """
    try:
        api_key = data.get("api_key")
        token = data.get("token")
        board_id = data.get("board_id")
        method = data.get("method", "weighted_average")
        
        if not all([api_key, token, board_id]):
            raise HTTPException(status_code=400, detail="Missing required credentials for Trello")
        
        # Khởi tạo tích hợp Trello
        try:
            trello = get_integration('trello', api_key=api_key, token=token)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error initializing Trello: {str(e)}")
        
        # Lấy thẻ từ Trello
        try:
            cards = trello.get_cards(board_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching cards: {str(e)}")
        
        # Chuyển đổi thẻ thành danh sách công việc
        tasks = trello.cards_to_tasks(cards)
        
        # Chuyển đổi tasks thành tài liệu yêu cầu
        requirements_text = trello.convert_to_requirements_doc(tasks)
        
        # Ước lượng nỗ lực
        result = estimator.estimate_from_requirements(requirements_text, method)
        
        # Thêm thông tin tasks vào kết quả
        result["tasks"] = tasks
        result["source"] = "trello"
        
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/jira-import")
def import_from_jira(data: Dict[str, Any] = Body(...)):
    """
    Import và ước lượng nỗ lực từ dữ liệu Jira
    """
    try:
        base_url = data.get("base_url")
        username = data.get("username")
        api_token = data.get("api_token")
        project_key = data.get("project_key")
        method = data.get("method", "weighted_average")
        
        if not all([base_url, username, api_token, project_key]):
            raise HTTPException(status_code=400, detail="Missing required credentials for Jira")
        
        # Khởi tạo tích hợp Jira
        try:
            jira = get_integration('jira', base_url=base_url, username=username, api_token=api_token)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error initializing Jira: {str(e)}")
        
        # Lấy issues từ Jira
        try:
            issues = jira.get_issues(project_key)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching issues: {str(e)}")
        
        # Chuyển đổi issues thành danh sách công việc
        tasks = jira.issues_to_tasks(issues)
        
        # Chuyển đổi tasks thành tài liệu yêu cầu
        requirements_text = jira.convert_to_requirements_doc(tasks)
        
        # Ước lượng nỗ lực
        result = estimator.estimate_from_requirements(requirements_text, method)
        
        # Thêm thông tin tasks vào kết quả
        result["tasks"] = tasks
        result["source"] = "jira"
        
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/estimate-cocomo")
def estimate_with_cocomo_parameters(params: COCOMOParameters):
    """
    Ước lượng nỗ lực sử dụng các tham số COCOMO II chi tiết
    """
    try:
        # Convert Pydantic model to dictionary
        cocomo_dict = params.dict()
        
        # Convert string ratings to numeric values
        rating_to_numeric = {
            "very_low": 0.75,
            "low": 0.88,
            "nominal": 1.00,
            "high": 1.15,
            "very_high": 1.30,
            "extra_high": 1.50
        }
        
        # Process scale drivers
        scale_factors = {
            'PREC': rating_to_numeric.get(cocomo_dict['precedentedness'], 1.0),
            'FLEX': rating_to_numeric.get(cocomo_dict['development_flexibility'], 1.0),
            'RESL': rating_to_numeric.get(cocomo_dict['architecture_risk_resolution'], 1.0),
            'TEAM': rating_to_numeric.get(cocomo_dict['team_cohesion'], 1.0),
            'PMAT': rating_to_numeric.get(cocomo_dict['process_maturity'], 1.0)
        }
        
        # Process effort multipliers (cost drivers)
        effort_multipliers = {
            'RELY': rating_to_numeric.get(cocomo_dict['required_software_reliability'], 1.0),
            'DATA': rating_to_numeric.get(cocomo_dict['database_size'], 1.0),
            'CPLX': rating_to_numeric.get(cocomo_dict['product_complexity'], 1.0),
            'RUSE': rating_to_numeric.get(cocomo_dict['developed_for_reusability'], 1.0),
            'DOCU': rating_to_numeric.get(cocomo_dict['documentation_match'], 1.0),
            'ACAP': rating_to_numeric.get(cocomo_dict['analyst_capability'], 1.0),
            'PCAP': rating_to_numeric.get(cocomo_dict['programmer_capability'], 1.0),
            'PCON': rating_to_numeric.get(cocomo_dict['personnel_continuity'], 1.0),
            'APEX': rating_to_numeric.get(cocomo_dict['application_experience'], 1.0),
            'PLEX': rating_to_numeric.get(cocomo_dict['platform_experience'], 1.0),
            'LTEX': rating_to_numeric.get(cocomo_dict['language_toolset_experience'], 1.0),
            'TIME': rating_to_numeric.get(cocomo_dict['time_constraint'], 1.0),
            'STOR': rating_to_numeric.get(cocomo_dict['storage_constraint'], 1.0),
            'PVOL': rating_to_numeric.get(cocomo_dict['platform_volatility'], 1.0),
            'TOOL': rating_to_numeric.get(cocomo_dict['use_of_software_tools'], 1.0),
            'SITE': rating_to_numeric.get(cocomo_dict['multisite_development'], 1.0),
            'SCED': rating_to_numeric.get(cocomo_dict['required_development_schedule'], 1.0)
        }
        
        # Calculate COCOMO-specific values first
        effort_adjustment_factor = 1.0
        for multiplier in effort_multipliers.values():
            effort_adjustment_factor *= multiplier
            
        scale_factor = 1.0
        for factor in scale_factors.values():
            scale_factor *= (factor - 1.0) * 0.1 + 1.0
        
        # Create comprehensive project data with realistic scaling
        project_data = {
            # Basic parameters - use reasonable scaling
            'size': min(cocomo_dict['software_size'], 1000),  # Cap at 1000 KLOC for realistic estimates
            'complexity': effort_multipliers['CPLX'],
            
            # COCOMO specific parameters
            'cocomo': {
                'size': cocomo_dict['software_size'],
                'eaf': effort_adjustment_factor,
                'scale_factor': scale_factor,
                **scale_factors,
                **effort_multipliers
            },
            
            # Function Points parameters (realistic estimates from COCOMO size)
            'function_points': {
                'external_inputs': max(3, min(50, int(cocomo_dict['software_size'] * 0.8))),
                'external_outputs': max(2, min(40, int(cocomo_dict['software_size'] * 0.6))),
                'external_inquiries': max(2, min(30, int(cocomo_dict['software_size'] * 0.4))),
                'internal_files': max(1, min(20, int(cocomo_dict['software_size'] * 0.3))),
                'external_files': max(1, min(15, int(cocomo_dict['software_size'] * 0.2))),
                'complexity_multiplier': min(1.5, effort_multipliers['CPLX'])  # Cap complexity
            },
            
            # Use Case Points parameters (realistic estimates)
            'use_case_points': {
                'simple_actors': max(1, min(10, int(cocomo_dict['software_size'] * 0.5))),
                'average_actors': max(1, min(8, int(cocomo_dict['software_size'] * 0.3))),
                'complex_actors': max(0, min(5, int(cocomo_dict['software_size'] * 0.1))),
                'simple_uc': max(2, min(20, int(cocomo_dict['software_size'] * 0.8))),
                'average_uc': max(2, min(15, int(cocomo_dict['software_size'] * 0.5))),
                'complex_uc': max(1, min(10, int(cocomo_dict['software_size'] * 0.2))),
                'complexity_factor': min(1.5, effort_multipliers['CPLX'])
            },
            
            # LOC parameters - with realistic bounds
            'loc_linear': {
                'kloc': min(cocomo_dict['software_size'], 500),  # Cap for realistic LOC estimates
                'complexity': min(1.5, effort_multipliers['CPLX']),
                'developers': max(2, min(10, int(cocomo_dict['software_size'] / 10))),
                'experience': (effort_multipliers['ACAP'] + effort_multipliers['PCAP']) / 2,
                'tech_score': (effort_multipliers['TOOL'] + effort_multipliers['PLEX']) / 2
            },
            
            'loc_random_forest': {
                'kloc': min(cocomo_dict['software_size'], 500),
                'complexity': min(1.5, effort_multipliers['CPLX']),
                'developers': max(2, min(10, int(cocomo_dict['software_size'] / 10))),
                'experience': (effort_multipliers['ACAP'] + effort_multipliers['PCAP']) / 2,
                'tech_score': (effort_multipliers['TOOL'] + effort_multipliers['PLEX']) / 2
            },
            
            # ML features - normalized and bounded
            'ml_features': {
                'size': min(cocomo_dict['software_size'], 200),  # Cap size for ML models
                'complexity': min(1.5, effort_multipliers['CPLX']),
                'team_experience': min(1.3, (effort_multipliers['ACAP'] + effort_multipliers['PCAP'] + 
                                  effort_multipliers['APEX'] + effort_multipliers['PLEX']) / 4),
                'process_maturity': min(1.2, scale_factors['PMAT']),
                'development_flexibility': min(1.2, scale_factors['FLEX']),
                'required_reliability': min(1.4, effort_multipliers['RELY']),
                'time_constraint': min(1.3, effort_multipliers['TIME']),
                'storage_constraint': min(1.3, effort_multipliers['STOR']),
                'platform_volatility': min(1.3, effort_multipliers['PVOL']),
                'analyst_capability': min(1.3, effort_multipliers['ACAP']),
                'programmer_capability': min(1.3, effort_multipliers['PCAP']),
                'application_experience': min(1.3, effort_multipliers['APEX']),
                'platform_experience': min(1.3, effort_multipliers['PLEX']),
                'language_experience': min(1.3, effort_multipliers['LTEX']),
                'use_of_tools': min(1.3, effort_multipliers['TOOL']),
                'multisite_development': min(1.2, effort_multipliers['SITE']),
                'required_schedule': min(1.3, effort_multipliers['SCED'])
            },
            
            # Additional features for ML models - realistic ranges
            'features': {
                'complexity': min(1.5, effort_multipliers['CPLX']),
                'developers': max(2, min(12, int(cocomo_dict['software_size'] / 8))),
                'functional_reqs': max(5, min(100, int(cocomo_dict['software_size'] * 2))),
                'non_functional_reqs': max(3, min(50, int(cocomo_dict['software_size'] * 1))),
                'num_requirements': max(8, min(150, int(cocomo_dict['software_size'] * 3)))
            }
        }
        
        # Create advanced_params with method
        advanced_params = {"method": cocomo_dict['method']}
        
        # Use the estimator's integrated estimation
        result = estimator.integrated_estimate(project_data, advanced_params=advanced_params)
        
        # Add detailed COCOMO results
        cocomo_effort = project_data['cocomo']['size'] * scale_factor * effort_adjustment_factor
        cocomo_schedule = (cocomo_effort ** 0.33) * scale_factor
        cocomo_team_size = cocomo_effort / cocomo_schedule if cocomo_schedule > 0 else 1
        
        # Extract integrated estimate from result
        integrated_estimate = result.get('integrated_estimate', result.get('final_estimate', 0))
        if integrated_estimate == 0:
            # Fallback to any available estimate
            if 'model_estimates' in result:
                # Filter out extreme values for more realistic estimates
                estimates = []
                for v in result['model_estimates'].values():
                    if isinstance(v, (int, float)) and 0.1 <= v <= 10000:  # Reasonable range
                        estimates.append(v)
                
                if estimates:
                    # Use median instead of mean to avoid extreme outliers
                    estimates.sort()
                    n = len(estimates)
                    if n % 2 == 0:
                        integrated_estimate = (estimates[n//2-1] + estimates[n//2]) / 2
                    else:
                        integrated_estimate = estimates[n//2]
                else:
                    # If no reasonable estimates, use COCOMO as fallback
                    integrated_estimate = cocomo_effort
        
        # Cost calculation
        total_cost = integrated_estimate * cocomo_dict['cost_per_person_month']
        
        # Phase distribution (typical COCOMO II phases)
        phases = {
            'inception': {'effort_percent': 5, 'schedule_percent': 12.5},
            'elaboration': {'effort_percent': 20, 'schedule_percent': 37.5},
            'construction': {'effort_percent': 65, 'schedule_percent': 37.5},
            'transition': {'effort_percent': 10, 'schedule_percent': 12.5}
        }
        
        phase_results = {}
        total_effort = integrated_estimate
        total_schedule = result.get('duration', cocomo_schedule)
        
        for phase, percentages in phases.items():
            phase_effort = total_effort * (percentages['effort_percent'] / 100)
            phase_schedule = total_schedule * (percentages['schedule_percent'] / 100)
            phase_staff = phase_effort / phase_schedule if phase_schedule > 0 else 0
            phase_cost = phase_effort * cocomo_dict['cost_per_person_month']
            
            phase_results[phase] = {
                'effort': round(phase_effort, 2),
                'schedule': round(phase_schedule, 2),
                'staff': round(phase_staff, 1),
                'cost': round(phase_cost, 0)
            }
        
        # Enhanced result with COCOMO-specific information
        enhanced_result = {
            **result,
            'estimation': {
                'integrated_estimate': round(integrated_estimate, 2),
                'duration': round(total_schedule, 2),
                'team_size': round(integrated_estimate / total_schedule if total_schedule > 0 else 1, 1),
                'confidence_level': result.get('confidence_level', 75),
                'model_estimates': result.get('model_estimates', {})
            },
            'cocomo_details': {
                'software_size': cocomo_dict['software_size'],
                'effort_adjustment_factor': round(effort_adjustment_factor, 3),
                'scale_factor': round(scale_factor, 3),
                'cocomo_effort': round(cocomo_effort, 2),
                'cocomo_schedule': round(cocomo_schedule, 2),
                'cocomo_team_size': round(cocomo_team_size, 1),
                'total_cost': round(total_cost, 0),
                'cost_per_person_month': cocomo_dict['cost_per_person_month']
            },
            'phase_distribution': phase_results,
            'scale_drivers': {
                'precedentedness': {
                    'rating': cocomo_dict['precedentedness'],
                    'value': scale_factors['PREC']
                },
                'development_flexibility': {
                    'rating': cocomo_dict['development_flexibility'],
                    'value': scale_factors['FLEX']
                },
                'architecture_risk_resolution': {
                    'rating': cocomo_dict['architecture_risk_resolution'],
                    'value': scale_factors['RESL']
                },
                'team_cohesion': {
                    'rating': cocomo_dict['team_cohesion'],
                    'value': scale_factors['TEAM']
                },
                'process_maturity': {
                    'rating': cocomo_dict['process_maturity'],
                    'value': scale_factors['PMAT']
                }
            },
            'effort_multipliers': {
                'product_factors': {
                    'required_reliability': effort_multipliers['RELY'],
                    'database_size': effort_multipliers['DATA'],
                    'product_complexity': effort_multipliers['CPLX'],
                    'reusability': effort_multipliers['RUSE'],
                    'documentation': effort_multipliers['DOCU']
                },
                'personnel_factors': {
                    'analyst_capability': effort_multipliers['ACAP'],
                    'programmer_capability': effort_multipliers['PCAP'],
                    'personnel_continuity': effort_multipliers['PCON'],
                    'application_experience': effort_multipliers['APEX'],
                    'platform_experience': effort_multipliers['PLEX'],
                    'language_experience': effort_multipliers['LTEX']
                },
                'platform_factors': {
                    'time_constraint': effort_multipliers['TIME'],
                    'storage_constraint': effort_multipliers['STOR'],
                    'platform_volatility': effort_multipliers['PVOL']
                },
                'project_factors': {
                    'use_of_tools': effort_multipliers['TOOL'],
                    'multisite_development': effort_multipliers['SITE'],
                    'required_schedule': effort_multipliers['SCED']
                }
            },
            'input_parameters': cocomo_dict
        }
        
        return JSONResponse(content=enhanced_result)
        
    except Exception as e:
        logger.error(f"Error in COCOMO estimation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cocomo", response_class=HTMLResponse)
async def cocomo_form_page(request: Request):
    """
    Trang form COCOMO II parameter-based estimation
    """
    return templates.TemplateResponse("cocomo_form.html", {"request": request})

@app.get("/task-generation", response_class=HTMLResponse)
async def task_generation_page(request: Request):
    """
    Trang task generation và automated effort estimation
    """
    return templates.TemplateResponse("task_generation.html", {"request": request})

@app.get("/test-generator-simple", response_class=HTMLResponse)
async def test_generator_simple():
    """
    Trang đơn giản để generate test cases (không phụ thuộc vào template phức tạp)
    """
    template_path = Path(__file__).parent / "templates" / "test_generator_simple.html"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    return HTMLResponse(content="<h1>Template not found</h1>", status_code=404)

@app.get("/debug", response_class=HTMLResponse)
async def debug_page(request: Request):
    return templates.TemplateResponse("debug.html", {"request": request})

# Mount static files last to avoid route conflicts
# Use html=True to properly serve static files
try:
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir), html=False), name="static")
        logger.info(f"Mounted static files from {static_dir}")
    else:
        logger.warning(f"Static directory not found: {static_dir}")
except Exception as e:
    logger.error(f"Error mounting static files: {e}")

def start_server(host="0.0.0.0", port=8000):
    """
    Khởi động server API
    """
    uvicorn.run("requirement_analyzer.api:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    start_server()
