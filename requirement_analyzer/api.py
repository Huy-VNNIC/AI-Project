"""
API cho service phân tích requirements và ước lượng nỗ lực
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
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

# Khởi tạo FastAPI app
app = FastAPI(
    title="Software Effort Estimation API",
    description="API để phân tích yêu cầu phần mềm và ước lượng nỗ lực phát triển",
    version="1.0.0"
)

# Cấu hình CORS
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

# Serve static files
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")

# Jinja2 templates
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

@app.get("/", response_class=HTMLResponse)
def main_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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
        return JSONResponse(content=result)
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
        
        return JSONResponse(content=result)
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
def cocomo_form_page(request: Request):
    """
    Trang form COCOMO II parameter-based estimation
    """
    return templates.TemplateResponse("cocomo_form.html", {"request": request})

@app.get("/debug", response_class=HTMLResponse)
def debug_page(request: Request):
    return templates.TemplateResponse("debug.html", {"request": request})

def start_server(host="0.0.0.0", port=8000):
    """
    Khởi động server API
    """
    uvicorn.run("requirement_analyzer.api:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    start_server()
