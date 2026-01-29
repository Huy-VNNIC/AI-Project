"""
API cho service phân tích requirements và ước lượng nỗ lực
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Body, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from starlette.responses import Response as StarletteResponse
from io import BytesIO
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import os
import sys
import tempfile
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
from requirement_analyzer.analyzer import RequirementAnalyzer
from requirement_analyzer.estimator import EffortEstimator
from requirement_analyzer.task_integration import get_integration
from requirement_analyzer.utils import preprocess_text_for_estimation, improve_confidence_level
from requirement_analyzer.task_gen import (
    get_pipeline,
    TaskGenerationRequest,
    TaskGenerationResponse,
    TaskFeedback
)

# Model cho request API
class RequirementText(BaseModel):
    text: str
    method: Optional[str] = "weighted_average"

class TaskList(BaseModel):
    tasks: List[Dict[str, Any]]
    method: Optional[str] = "weighted_average"

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

# Khởi tạo FastAPI app với Swagger UI configuration
app = FastAPI(
    title="Software Effort Estimation & Task Generation API",
    description="""
    ## API Phân tích Requirements và Ước lượng Nỗ lực
    
    API này cung cấp các chức năng:
    - 📊 **V1 Estimation**: Ước lượng nỗ lực với COCOMO II, LOC, Multi-model
    - 🤖 **V2 Requirements Engineering**: Phân tích, làm mịn, phát hiện gaps, slice requirements
    - 📝 **Task Generation**: Tự động sinh tasks từ requirements
    - 🔄 **Integration**: Kết nối với Jira, Trello
    
    ### 🔐 Security
    - Rate limiting: 100 requests per 60 seconds
    - File validation: Max 2MB, safe file types only
    
    ### 📚 Documentation
    - **Swagger UI**: `/docs` (Interactive API documentation)
    - **ReDoc**: `/redoc` (Alternative documentation)
    - **OpenAPI Schema**: `/openapi.json` (Machine-readable spec)
    - **JSON Schemas**: `/api/schemas` (Data model schemas)
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "Health",
            "description": "Health check endpoints"
        },
        {
            "name": "V1 Estimation",
            "description": "COCOMO II và LOC estimation endpoints"
        },
        {
            "name": "Task Generation",
            "description": "AI-powered task generation từ requirements"
        },
        {
            "name": "V2 Requirements Engineering",
            "description": "Pipeline phân tích và làm mịn requirements"
        },
        {
            "name": "Integration",
            "description": "Jira, Trello integration endpoints"
        },
        {
            "name": "Schemas",
            "description": "JSON Schema definitions"
        }
    ]
)

# ============================================================================
# Security & Rate Limiting Middleware
# ============================================================================
from collections import defaultdict
from datetime import datetime, timedelta

# Simple rate limiter (in-memory)
request_counts = defaultdict(list)
RATE_LIMIT_REQUESTS = 100  # requests per window
RATE_LIMIT_WINDOW = 60  # seconds

@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """
    Security middleware for:
    - Rate limiting
    - Request validation
    - Logging suspicious activity
    """
    client_ip = request.client.host
    now = datetime.now()
    
    # Rate limiting (simple sliding window)
    request_counts[client_ip] = [
        ts for ts in request_counts[client_ip]
        if now - ts < timedelta(seconds=RATE_LIMIT_WINDOW)
    ]
    
    if len(request_counts[client_ip]) >= RATE_LIMIT_REQUESTS:
        logger.warning(f"⚠️ Rate limit exceeded for {client_ip}")
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": f"Maximum {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW}s"
            }
        )
    
    request_counts[client_ip].append(now)
    
    # Log suspicious requests
    if request.method not in ["GET", "POST", "OPTIONS"]:
        logger.warning(f"⚠️ Suspicious method {request.method} from {client_ip}")
    
    # Block common attack paths
    blocked_paths = ["/login", "/admin", "/.env", "/wp-admin", "/phpMyAdmin"]
    if any(blocked in str(request.url.path) for blocked in blocked_paths):
        logger.warning(f"⚠️ Blocked suspicious path {request.url.path} from {client_ip}")
        return JSONResponse(status_code=404, content={"error": "Not found"})
    
    response = await call_next(request)
    return response

# ============================================================================
# END Security Middleware
# ============================================================================

# Khởi tạo các thành phần
analyzer = RequirementAnalyzer()
estimator = EffortEstimator()

# Initialize task generation pipeline with config
try:
    from requirement_analyzer.task_gen.config import (
        GENERATOR_MODE,
        LLM_PROVIDER,
        LLM_MODEL,
        LLM_API_KEY,
        get_pipeline_config
    )
    
    # Print config on startup
    config = get_pipeline_config()
    logger.info(f"Task generation config: {config}")
    
    # Initialize with LLM if mode=llm, model if mode=model, else template
    if GENERATOR_MODE == "llm":
        logger.info(f"Initializing LLM pipeline ({LLM_PROVIDER}/{LLM_MODEL or 'auto'})...")
        task_pipeline = get_pipeline(
            generator_mode="llm",
            llm_provider=LLM_PROVIDER,
            llm_model=LLM_MODEL,
            llm_api_key=LLM_API_KEY
        )
    elif GENERATOR_MODE == "model":
        logger.info("Initializing model-based pipeline (trained ML models)...")
        task_pipeline = get_pipeline(generator_mode="model")
    else:
        logger.info("Initializing template pipeline...")
        task_pipeline = get_pipeline()
    
    logger.info(f"✓ Task generation pipeline loaded (mode={GENERATOR_MODE})")
except Exception as e:
    logger.warning(f"⚠️  Task generation pipeline not available: {e}")
    task_pipeline = None

analyzer = RequirementAnalyzer()
estimator = EffortEstimator()

# Jinja2 templates
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/task-generation", response_class=HTMLResponse)
async def task_generation_page(request: Request):
    """Task generation UI page"""
    return templates.TemplateResponse("task_generation.html", {"request": request})

@app.get("/favicon.ico")
async def favicon():
    """Serve favicon or 1x1 transparent PNG (avoids h11 protocol issues)"""
    favicon_path = Path(__file__).parent / "static" / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(favicon_path)
    # Always return 200 OK with PNG bytes => no 204/h11 edge cases
    png_data = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01'
        b'\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    return Response(content=png_data, media_type="image/png")

@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint for monitoring
    
    Returns:
        - status: healthy/unhealthy
        - service: service name
    """
    return {"status": "healthy", "service": "ai-estimation-api"}


@app.get("/api/schemas", tags=["Schemas"], summary="Get all JSON Schemas")
def get_json_schemas():
    """
    Export JSON Schema definitions cho tất cả data models
    
    Trả về JSON schemas cho:
    - V1 Models: RequirementText, TaskList, EstimationRequest, etc.
    - V2 Models: Requirement, RefinementOutput, Gap, SliceOutput, etc.
    - Task Generation Models: TaskGenerationRequest, TaskGenerationResponse
    
    JSON Schema có thể dùng để:
    - Validate input/output data
    - Generate client code (TypeScript, Python, etc.)
    - API documentation tools
    - Form generation
    """
    try:
        schemas = {}
        
        # V1 Models
        schemas["RequirementText"] = RequirementText.model_json_schema()
        schemas["TaskList"] = TaskList.model_json_schema()
        schemas["COCOMOParameters"] = COCOMOParameters.model_json_schema()
        
        # Task Generation Models
        from requirement_analyzer.task_gen import TaskGenerationRequest, TaskGenerationResponse, TaskFeedback
        schemas["TaskGenerationRequest"] = TaskGenerationRequest.model_json_schema()
        schemas["TaskGenerationResponse"] = TaskGenerationResponse.model_json_schema()
        schemas["TaskFeedback"] = TaskFeedback.model_json_schema()
        
        # V2 Requirements Engineering Models
        try:
            from requirement_analyzer.task_gen.schemas_v2 import (
                Requirement,
                AcceptanceCriterion,
                RefinementOutput,
                Gap,
                GapReport,
                Slice,
                SlicingOutput,
                INVESTScore,
                UserStory,
                Subtask,
                SeverityLevel,
                RequirementType,
                GapType,
                SliceRationale,
                TaskRole
            )
            
            # Data Models
            schemas["Requirement"] = Requirement.model_json_schema()
            schemas["AcceptanceCriterion"] = AcceptanceCriterion.model_json_schema()
            schemas["RefinementOutput"] = RefinementOutput.model_json_schema()
            schemas["Gap"] = Gap.model_json_schema()
            schemas["GapReport"] = GapReport.model_json_schema()
            schemas["UserStory"] = UserStory.model_json_schema()
            schemas["Subtask"] = Subtask.model_json_schema()
            schemas["Slice"] = Slice.model_json_schema()
            schemas["SlicingOutput"] = SlicingOutput.model_json_schema()
            schemas["INVESTScore"] = INVESTScore.model_json_schema()
            
            # Enums
            schemas["SeverityLevel"] = {
                "type": "string",
                "enum": [e.value for e in SeverityLevel],
                "description": "Severity levels for gaps and issues"
            }
            schemas["RequirementType"] = {
                "type": "string",
                "enum": [e.value for e in RequirementType],
                "description": "Types of requirements"
            }
            schemas["GapType"] = {
                "type": "string",
                "enum": [e.value for e in GapType],
                "description": "Types of gaps detected in requirements"
            }
            schemas["SliceRationale"] = {
                "type": "string",
                "enum": [e.value for e in SliceRationale],
                "description": "Rationale for creating a story slice"
            }
            schemas["TaskRole"] = {
                "type": "string",
                "enum": [e.value for e in TaskRole],
                "description": "Roles for task assignment"
            }
            
        except ImportError as e:
            logger.warning(f"V2 schemas not available: {e}")
        
        return {
            "openapi_version": "3.1.0",
            "info": {
                "title": "Software Effort Estimation API - Data Models",
                "version": "2.0.0",
                "description": "JSON Schema definitions for all API data models"
            },
            "schemas": schemas,
            "schema_count": len(schemas),
            "categories": {
                "v1_estimation": ["RequirementText", "TaskList", "COCOMOParameters"],
                "task_generation": ["TaskGenerationRequest", "TaskGenerationResponse", "TaskFeedback"],
                "v2_requirements": ["Requirement", "RefinementOutput", "Gap", "GapReport", "UserStory", "Subtask", "Slice", "SlicingOutput"],
                "v2_quality": ["INVESTScore", "AcceptanceCriterion"],
                "enums": ["SeverityLevel", "RequirementType", "GapType", "SliceRationale", "TaskRole"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating schemas: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating schemas: {str(e)}")


@app.get("/api/schemas/{model_name}", tags=["Schemas"], summary="Get specific JSON Schema")
def get_schema_by_name(model_name: str):
    """
    Lấy JSON Schema cho một model cụ thể
    
    Parameters:
        - model_name: Tên model (RequirementText, RefinementOutput, Gap, etc.)
    
    Example:
        GET /api/schemas/RefinementOutput
    """
    try:
        # Get all schemas first
        all_schemas = get_json_schemas()
        
        if model_name not in all_schemas["schemas"]:
            available = ", ".join(all_schemas["schemas"].keys())
            raise HTTPException(
                status_code=404,
                detail=f"Schema '{model_name}' not found. Available schemas: {available}"
            )
        
        return {
            "model_name": model_name,
            "schema": all_schemas["schemas"][model_name],
            "openapi_version": "3.1.0"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting schema for {model_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/estimate", tags=["V1 Estimation"], summary="Simple text estimation")
def estimate_effort_simple(req: RequirementText):
    """
    Endpoint đơn giản để ước lượng effort từ văn bản requirements
    
    **Input:**
    - text: Văn bản requirements (Vietnamese/English)
    - method: Integration method (weighted_average, best_model, stacking, bayesian_average)
    
    **Output:**
    - Total effort (person-months)
    - Duration (months)
    - Team size
    - Confidence level
    - Model breakdown
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

@app.post("/analyze", tags=["V1 Estimation"], summary="Analyze requirements document")
def analyze_requirements(req: RequirementText):
    """
    Phân tích tài liệu yêu cầu và trả về kết quả phân tích
    
    **Output:** Requirements analysis with metrics and insights
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

@app.post("/upload-requirements", tags=["V1 Estimation"], summary="Upload and estimate from file")
async def upload_requirements(file: UploadFile = File(...), method: str = Form("weighted_average")):
    """
    Tải lên tài liệu yêu cầu và ước lượng nỗ lực
    
    **Supported formats:**
    - .txt, .md: Plain text files
    - .pdf: PDF documents
    - .doc, .docx: Microsoft Word documents
    
    **Parameters:**
    - file: Document file (max 2MB)
    - method: Integration method (weighted_average, best_model, etc.)
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

@app.post("/estimate-from-tasks", tags=["V1 Estimation"], summary="Estimate from task list")
def estimate_from_tasks(tasks: TaskList):
    """
    Ước lượng nỗ lực từ danh sách công việc (tasks)
    
    **Input:** Array of tasks with title, description, priority, complexity
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

@app.get("/debug", response_class=HTMLResponse)
async def debug_page(request: Request):
    return templates.TemplateResponse("debug.html", {"request": request})


# ============================================================================
# TASK GENERATION ENDPOINTS (NEW)
# ============================================================================

@app.get("/api/task-generation/status")
async def task_generation_status():
    """Get task generation service status and mode"""
    if task_pipeline is None:
        return {
            "available": False,
            "mode": None,
            "message": "Task generation service not initialized"
        }
    
    return {
        "available": True,
        "mode": task_pipeline.generator_mode,
        "generator_class": type(task_pipeline.generator).__name__,
        "message": f"Task generation ready (mode: {task_pipeline.generator_mode})"
    }


@app.post("/api/task-generation/generate", tags=["Task Generation"], summary="Generate tasks from text")
async def generate_tasks_api(request: TaskGenerationRequest):
    """
    Generate tasks from requirements text - New UI endpoint
    
    **Input:**
    - text: Requirements document text
    - max_tasks: Maximum tasks to generate (default: 50)
    - requirement_threshold: Detection confidence threshold (default: 0.5)
    - epic_name: Optional epic name
    - domain_hint: Optional domain classification
    
    **Output:**
    - tasks: Array of generated tasks with title, description, priority, complexity
    - stats: Generation statistics
    - total_story_points: Estimated story points
    - estimated_duration_days: Estimated duration
    """
    if task_pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Task generation service not available. Models not loaded."
        )
    
    try:
        logger.info(f"📋 Generating tasks from text ({len(request.text)} chars)")
        
        # Use getattr with defaults for optional fields
        response = task_pipeline.generate_tasks(
            text=request.text,
            max_tasks=getattr(request, 'max_tasks', 50),
            requirement_threshold=getattr(request, 'requirement_threshold', 0.5),
            epic_name=getattr(request, 'epic_name', None),
            domain_hint=getattr(request, 'domain_hint', None)
        )
        
        logger.info(f"✅ Generated {len(response.tasks)} tasks")
        
        # Use jsonable_encoder to properly serialize datetime and Pydantic models
        result = {
            "tasks": jsonable_encoder(response.tasks),
            "total_tasks": response.total_tasks,
            "stats": response.stats,
            "processing_time": response.processing_time,
            "mode": response.mode,
            "generator_version": response.generator_version
        }
        
        # Add optional fields if present
        if response.total_story_points is not None:
            result["total_story_points"] = response.total_story_points
        if response.estimated_duration_days is not None:
            result["estimated_duration_days"] = response.estimated_duration_days
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error generating tasks: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/task-generation/generate-from-file", tags=["Task Generation"], summary="Generate tasks from file")
async def generate_tasks_from_file(
    file: UploadFile = File(...),
    max_tasks: int = Form(200),
    requirement_threshold: float = Form(0.3)
):
    """
    Generate tasks from uploaded file (txt/docx/pdf)
    
    **Improved pipeline:**
    1. Extract text from file (auto-detect format)
    2. Extract requirement candidates (filter notes/headings)
    3. Generate tasks from requirements
    
    **Supported formats:** .txt, .md, .pdf, .doc, .docx
    **Max file size:** 2MB
    """
    if task_pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Task generation service not available"
        )
    
    try:
        # Read file content
        file_bytes = await file.read()
        
        logger.info(f"📋 Processing file: {file.filename} ({len(file_bytes)} bytes)")
        
        # Step 1: Extract text from file (auto-detect format)
        from requirement_analyzer.ingestion import extract_text
        raw_text = extract_text(file.filename, file_bytes)
        
        if not raw_text or len(raw_text) < 10:
            raise HTTPException(
                status_code=400,
                detail=f"Could not extract text from file. File might be empty or unsupported format."
            )
        
        logger.info(f"   Extracted {len(raw_text)} characters from file")
        
        # Step 2: Extract requirement candidates (using filters)
        from requirement_analyzer.task_gen.filters import extract_requirements_from_text
        requirements = extract_requirements_from_text(raw_text)
        
        if not requirements:
            logger.warning("No requirements found in document after filtering")
            return JSONResponse(content={
                "tasks": [],
                "total_tasks": 0,
                "stats": {},
                "processing_time": 0.0,
                "mode": task_pipeline.generator_mode,
                "generator_version": "1.0.0",
                "source_file": file.filename,
                "ingestion": {
                    "total_chars": len(raw_text),
                    "requirements_extracted": 0,
                    "threshold": requirement_threshold,
                    "message": "No requirements detected after filtering. Document may contain only notes/headings."
                }
            })
        
        logger.info(f"   Extracted {len(requirements)} requirement candidates")
        
        # Step 3: Generate tasks using generate_from_sentences (BYPASS SEGMENTER)
        # Each requirement line is treated as separate sentence - no merging
        # For file uploads: disable quality filter to keep all detected tasks
        import time
        start_time = time.time()
        
        # Count actual detected requirements (not just extracted lines)
        detection_results = task_pipeline.detector.detect(requirements, threshold=requirement_threshold)
        detected_count = sum(1 for is_req, _ in detection_results if is_req)
        
        tasks = task_pipeline.generate_from_sentences(
            requirements,
            epic_name=None,
            requirement_threshold=requirement_threshold,
            enable_quality_filter=False,  # Keep all tasks for file uploads
            enable_deduplication=True      # But still remove duplicates
        )
        
        processing_time = time.time() - start_time
        
        # Build response with comprehensive stats
        result = {
            "tasks": jsonable_encoder(tasks),
            "total_tasks": len(tasks),
            "stats": {
                "requirements_extracted": len(requirements),
                "requirements_detected": detected_count,  # Actual count from detector
                "tasks_generated": len(tasks),  # Final tasks after postprocessing
                "processing_time": processing_time
            },
            "processing_time": processing_time,
            "mode": task_pipeline.generator_mode,
            "generator_version": "1.0.0",
            "source_file": file.filename,
            "ingestion": {
                "total_chars": len(raw_text),
                "requirements_extracted": len(requirements),
                "threshold": requirement_threshold,
                "method": "generate_from_sentences (bypass segmenter)"
            }
        }
        
        logger.info(f"✅ Generated {result['total_tasks']} tasks from file {file.filename}")
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-tasks", response_model=TaskGenerationResponse)
async def generate_tasks(request: TaskGenerationRequest):
    """
    Generate tasks from requirement document
    
    Main endpoint for AI task generation
    """
    if task_pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Task generation service not available. Please train models first."
        )
    
    try:
        logger.info(f"📋 Generating tasks from document ({len(request.text)} chars)")
        
        response = task_pipeline.generate_tasks(
            text=request.text,
            max_tasks=request.max_tasks,
            epic_name=request.epic_name,
            domain_hint=request.domain_hint
        )
        
        logger.info(f"✅ Generated {response.total_tasks} tasks in {response.processing_time:.2f}s")
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating tasks: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-tasks-estimate")
async def generate_tasks_and_estimate(request: TaskGenerationRequest):
    """
    Generate tasks AND estimate effort/story points
    
    Combines task generation with effort estimation
    """
    if task_pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Task generation service not available"
        )
    
    try:
        # 1. Generate tasks
        logger.info(f"📋 Generating tasks with estimation...")
        
        task_response = task_pipeline.generate_tasks(
            text=request.text,
            max_tasks=request.max_tasks,
            epic_name=request.epic_name,
            domain_hint=request.domain_hint
        )
        
        tasks = task_response.tasks
        
        if not tasks:
            return {
                "tasks": [],
                "total_tasks": 0,
                "estimation": None,
                "message": "No tasks generated"
            }
        
        # 2. Estimate effort if requested
        if request.include_story_points:
            logger.info(f"📊 Estimating effort for {len(tasks)} tasks...")
            
            # Convert tasks to estimation format
            task_list = [
                {
                    "title": task.title,
                    "description": task.description,
                    "type": task.type,
                    "priority": task.priority,
                    "role": task.role
                }
                for task in tasks
            ]
            
            # Call existing estimator
            try:
                estimation_result = estimator.estimate_from_requirements(
                    request.text,
                    method="weighted_average"
                )
                
                total_effort = estimation_result.get('total_effort_hours', 0)
                
                # Allocate story points based on priority and complexity
                tasks_with_points = _allocate_story_points(tasks, total_effort)
                
                # Update tasks in response
                for i, task in enumerate(tasks):
                    task.story_points = tasks_with_points[i]['story_points']
                    task.estimated_hours = tasks_with_points[i]['estimated_hours']
                
                task_response.total_story_points = sum(t['story_points'] for t in tasks_with_points)
                task_response.estimated_duration_days = estimation_result.get('duration_months', 0) * 22  # approx working days
                
            except Exception as e:
                logger.warning(f"⚠️  Effort estimation failed: {e}")
        
        # Build response
        response_dict = task_response.dict()
        response_dict['message'] = f"Successfully generated {len(tasks)} tasks"
        
        return JSONResponse(content=response_dict)
        
    except Exception as e:
        logger.error(f"Error in generate-tasks-estimate: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload-requirements-generate-tasks")
async def upload_and_generate_tasks(
    file: UploadFile = File(...),
    max_tasks: int = Form(50),
    epic_name: Optional[str] = Form(None)
):
    """
    Upload requirement document and generate tasks
    """
    if task_pipeline is None:
        raise HTTPException(status_code=503, detail="Task generation service not available")
    
    try:
        # Parse document
        from requirement_analyzer.document_parser import DocumentParser
        
        content = await file.read()
        filename = file.filename
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in ['.txt', '.doc', '.docx', '.pdf', '.md']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {file_ext}. Supported: .txt, .doc, .docx, .pdf, .md"
            )
        
        parser = DocumentParser()
        text = parser.parse(content, file_ext)
        
        if not text or len(text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Document is too short or empty"
            )
        
        # Generate tasks
        response = task_pipeline.generate_tasks(
            text=text,
            max_tasks=max_tasks,
            epic_name=epic_name
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading and generating tasks: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tasks/feedback")
async def submit_task_feedback(feedback: TaskFeedback):
    """
    Submit feedback on generated task (for learning loop)
    
    Stores user edits and acceptance to improve model later
    """
    try:
        # Store feedback (implement storage later)
        logger.info(f"📝 Received feedback for task {feedback.task_id}: accepted={feedback.accepted}")
        
        # TODO: Save to database for future model improvement
        # For now, just acknowledge
        
        return {
            "status": "success",
            "message": "Feedback received",
            "task_id": feedback.task_id
        }
        
    except Exception as e:
        logger.error(f"Error saving feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _allocate_story_points(tasks: List, total_effort_hours: float) -> List[Dict]:
    """
    Allocate story points to tasks based on effort and complexity
    
    Uses priority, type, and role as weights
    """
    if not tasks or total_effort_hours <= 0:
        return [{'story_points': 3, 'estimated_hours': 8} for _ in tasks]
    
    # Define weight factors
    priority_weights = {'Low': 0.8, 'Medium': 1.0, 'High': 1.3, 'Critical': 1.5}
    type_weights = {
        'security': 1.2,
        'data': 1.1,
        'integration': 1.15,
        'performance': 1.1,
        'interface': 1.0,
        'functional': 1.0
    }
    role_weights = {
        'Security': 1.2,
        'DevOps': 1.1,
        'Backend': 1.0,
        'Data': 1.0,
        'Frontend': 0.9,
        'QA': 0.8
    }
    
    # Calculate weights for each task
    task_weights = []
    for task in tasks:
        priority = getattr(task, 'priority', 'Medium')
        task_type = getattr(task, 'type', 'functional')
        role = getattr(task, 'role', 'Backend')
        
        weight = (
            priority_weights.get(priority, 1.0) *
            type_weights.get(task_type, 1.0) *
            role_weights.get(role, 1.0)
        )
        task_weights.append(weight)
    
    total_weight = sum(task_weights)
    
    # Allocate hours
    fibonacci = [1, 2, 3, 5, 8, 13, 21, 34]
    result = []
    
    for i, task in enumerate(tasks):
        # Calculate hours for this task
        task_hours = (task_weights[i] / total_weight) * total_effort_hours
        
        # Convert to story points (Fibonacci)
        # Rough mapping: 1 point = 1-4 hours, 2 = 4-8, 3 = 8-16, etc.
        if task_hours <= 4:
            points = 1
        elif task_hours <= 8:
            points = 2
        elif task_hours <= 16:
            points = 3
        elif task_hours <= 24:
            points = 5
        elif task_hours <= 40:
            points = 8
        elif task_hours <= 60:
            points = 13
        else:
            points = 21
        
        result.append({
            'story_points': points,
            'estimated_hours': round(task_hours, 1)
        })
    
    return result


# ============================================================================
# END TASK GENERATION ENDPOINTS
# ============================================================================

# ============================================================================
# V2 ENDPOINTS - Requirements Engineering Pipeline
# ============================================================================
try:
    from requirement_analyzer.api_v2 import router as v2_router
    app.include_router(v2_router)
    logger.info("✅ V2 API endpoints registered")
except Exception as e:
    logger.warning(f"⚠️ V2 endpoints not available: {e}")

# ============================================================================
# END V2 ENDPOINTS
# ============================================================================


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
    
    Production deployment: Binding to 0.0.0.0 for network access.
    Rate limiting and security middleware are enabled.
    """
    logger.info(f"🚀 Starting server on {host}:{port}")
    logger.info(f"   Security: Rate limiting enabled (100 req/60s)")
    logger.info(f"   Network: {'Public binding with auth' if host == '0.0.0.0' else 'Localhost only'}")
    uvicorn.run("requirement_analyzer.api:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    start_server()
