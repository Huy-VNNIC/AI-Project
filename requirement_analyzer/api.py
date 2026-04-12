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
import uvicorn
import os
import sys
import tempfile
import pandas as pd
import json
import logging
import re
import csv
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
from requirement_analyzer.task_Invest_text import InvestAnalyzer
from requirement_analyzer.task_refine_invest import InvestTaskRefiner
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

class InvestRequest(BaseModel):
    text: str
    split_mode: Optional[str] = "line"
    min_length: Optional[int] = 15


def _build_empty_invest_response() -> Dict[str, Any]:
    return {
        "status": "success",
        "summary": {
            "task_count": 0,
            "average_score": 0,
            "score_scale": 6,
            "overall_label": "No data",
            "criteria_pass_rates": {}
        },
        "results": []
    }


def _build_error_invest_response(detail: str) -> Dict[str, Any]:
    """Helper function to build consistent error response for INVEST analysis"""
    return {
        "status": "error",
        "detail": detail,
        "summary": {
            "task_count": 0,
            "average_score": 0,
            "score_scale": 6,
            "overall_label": "Error",
            "criteria_pass_rates": {},
        },
        "results": [],
    }


def _build_invest_response_from_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    criteria_keys = ["independent", "negotiable", "valuable", "estimable", "small", "testable"]
    total_score = sum(item.get("score", 0) for item in results)
    average_score = round(total_score / len(results), 4) if results else 0

    if not results:
        overall_label = "No data"
    elif average_score >= 5:
        overall_label = "Strong INVEST"
    elif average_score >= 3:
        overall_label = "Needs Refinement"
    else:
        overall_label = "Weak INVEST"

    criteria_pass_rates = {}
    for key in criteria_keys:
        passed = sum(1 for item in results if item.get("criteria", {}).get(key, {}).get("pass"))
        criteria_pass_rates[key] = {
            "passed": passed,
            "total": len(results),
            "percent": round((passed / len(results)) * 100) if results else 0
        }

    return {
        "status": "success",
        "summary": {
            "task_count": len(results),
            "average_score": average_score,
            "overall_label": overall_label,
            "criteria_pass_rates": criteria_pass_rates
        },
        "results": results
    }


def _parse_invest_tasks_from_json_payload(payload: Any) -> List[str]:
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict) and isinstance(payload.get("tasks"), list):
        items = payload["tasks"]
    else:
        raise ValueError("JSON file must be a task array or an object containing 'tasks'.")

    parsed_tasks: List[str] = []
    for item in items:
        if isinstance(item, str):
            text = item.strip()
        elif isinstance(item, dict):
            title = str(item.get("title", "")).strip()
            description = str(item.get("description", "")).strip()
            acceptance_criteria = item.get("acceptance_criteria", [])
            if isinstance(acceptance_criteria, list):
                acceptance_text = "\n".join(str(ac).strip() for ac in acceptance_criteria if str(ac).strip())
            else:
                acceptance_text = str(acceptance_criteria or "").strip()
            text = "\n".join(part for part in [title, description, acceptance_text] if part).strip()
        else:
            text = str(item).strip()

        if text:
            parsed_tasks.append(text)
    return parsed_tasks


def _compose_invest_task_text(title: str = "", description: str = "", acceptance_criteria: Optional[List[str]] = None) -> str:
    parts: List[str] = []
    if title and title.strip():
        parts.append(f"Title: {title.strip()}")
    if description and description.strip():
        parts.append(f"Description: {description.strip()}")
    cleaned_ac = [str(item).strip() for item in (acceptance_criteria or []) if str(item).strip()]
    if cleaned_ac:
        parts.append("Acceptance Criteria:")
        parts.extend(f"- {item}" for item in cleaned_ac)
    return "\n".join(parts).strip()


def _build_task_dict_from_text(text: str, index: int) -> Dict[str, Any]:
    normalized = (text or "").strip()
    single_line = re.sub(r"\s+", " ", normalized).strip()
    title = single_line[:80].rstrip(" ,.;:-") if single_line else f"Task {index}"
    return {
        "title": title or f"Task {index}",
        "description": normalized,
        "acceptance_criteria": [],
    }


def _parse_csv_tasks_from_text(decoded_text: str) -> List[Dict[str, Any]]:
    lines = [line for line in decoded_text.splitlines() if line.strip()]
    if not lines:
        return []

    reader = csv.DictReader(lines)
    if reader.fieldnames:
        normalized_fields = {field.strip().lower(): field for field in reader.fieldnames if field}
        if "title" in normalized_fields or "description" in normalized_fields:
            tasks: List[Dict[str, Any]] = []
            for index, row in enumerate(reader, start=1):
                title = str(row.get(normalized_fields.get("title", ""), "")).strip()
                description = str(row.get(normalized_fields.get("description", ""), "")).strip()
                acceptance_key = normalized_fields.get("acceptance_criteria")
                acceptance_raw = row.get(acceptance_key, "") if acceptance_key else ""
                acceptance_criteria = [
                    item.strip()
                    for item in re.split(r"\s*\|\s*", str(acceptance_raw or ""))
                    if item.strip()
                ]
                combined_text = "\n".join(part for part in [title, description] if part).strip()
                if not combined_text and not acceptance_criteria:
                    continue
                tasks.append({
                    "title": title or f"Task {index}",
                    "description": description or combined_text or title or f"Task {index}",
                    "acceptance_criteria": acceptance_criteria,
                })
            if tasks:
                return tasks

    return [
        _build_task_dict_from_text(line, index)
        for index, line in enumerate(lines, start=1)
    ]


def _parse_uploaded_tasks_to_payload(
    decoded_text: str,
    file_ext: str,
    split_mode: str,
    min_length: int,
) -> Dict[str, Any]:
    if file_ext == ".json":
        try:
            payload = json.loads(decoded_text)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail=f"Invalid JSON file: {exc.msg}") from exc

        if isinstance(payload, list):
            return {"tasks": payload}
        if isinstance(payload, dict) and isinstance(payload.get("tasks"), list):
            return payload
        raise HTTPException(
            status_code=400,
            detail="JSON file must be a task array or an object containing 'tasks'.",
        )

    if file_ext == ".csv":
        tasks = _parse_csv_tasks_from_text(decoded_text)
        return {"tasks": tasks}

    chunks = split_invest_inputs(decoded_text, split_mode)
    tasks = [
        _build_task_dict_from_text(chunk.strip(), index)
        for index, chunk in enumerate(chunks, start=1)
        if chunk and chunk.strip() and len(chunk.strip()) >= min_length
    ]
    return {"tasks": tasks}


def _build_refined_invest_file_response(refined_payload: Dict[str, Any], min_dimension: int) -> Dict[str, Any]:
    all_tasks = refined_payload.get("tasks", []) or []
    display_tasks = all_tasks
    criteria_keys = ["independent", "negotiable", "valuable", "estimable", "small", "testable"]

    results: List[Dict[str, Any]] = []
    for task in display_tasks:
        invest = task.get("invest", {})
        score_map = invest.get("score", {}) or {}
        criteria = {}
        pass_count = 0
        for key in criteria_keys:
            dim_score = int(score_map.get(key, 0) or 0)
            passed = dim_score >= min_dimension
            if passed:
                pass_count += 1
            criteria[key] = {
                "pass": passed,
                "reason": f"Score {dim_score}/5"
            }

        refinement_info = task.get("invest_refinement", {}) or {}
        status = refinement_info.get("status", "unknown")
        notes = refinement_info.get("notes") or []
        if status == "kept" and not notes:
            notes = [refinement_info.get("reason") or "Task already met INVEST, no changes required."]
        original_text = _compose_invest_task_text(
            refinement_info.get("original_title") or task.get("title") or "",
            refinement_info.get("original_description") or task.get("description") or "",
            refinement_info.get("original_acceptance_criteria") or task.get("acceptance_criteria") or [],
        )
        refined_text = _compose_invest_task_text(
            task.get("title") or "Untitled task",
            task.get("description") or "",
            task.get("acceptance_criteria") or [],
        )
        results.append({
            "title": task.get("title") or "Untitled task",
            "original": original_text,
            "refined_title": task.get("title") or "Untitled task",
            "refined": refined_text,
            "refined_description": task.get("description") or "",
            "acceptance_criteria": task.get("acceptance_criteria") or [],
            "issues": notes,
            "criteria": criteria,
            "score": pass_count,
            "invest_total": invest.get("total", 0),
            "invest_grade": invest.get("grade", "Unknown"),
            "meets_invest": invest.get("meets_invest", False),
            "recommended_action": "keep" if invest.get("meets_invest", False) else "refine",
            "refinement_status": status,
        })

    if not results:
        return {
            "status": "success",
            "mode": "refined_tasks",
            "summary": {
                "task_count": 0,
                "average_score": 0,
                "score_scale": 6,
                "overall_label": "No tasks found",
                "criteria_pass_rates": {
                    key: {"passed": 0, "total": 0, "percent": 0}
                    for key in criteria_keys
                },
            },
            "results": [],
            "refinement": {
                "before": refined_payload.get("summary_before", {}),
            "after": refined_payload.get("summary_after", {}),
            "invest_ready_total": refined_payload.get("invest_ready_total", 0),
            "refined_ready_total": refined_payload.get("refined_ready_total", 0),
            "invest_not_ready_total": refined_payload.get("invest_not_ready_total", 0),
            "displayed_total": 0,
        },
    }

    criteria_pass_rates = {}
    for key in criteria_keys:
        passed = sum(1 for item in results if item.get("criteria", {}).get(key, {}).get("pass"))
        criteria_pass_rates[key] = {
            "passed": passed,
            "total": len(results),
            "percent": round((passed / len(results)) * 100) if results else 0
        }

    avg_score = round(sum(item.get("score", 0) for item in results) / (len(results) * 6), 4) if results else 0
    ready_count = sum(1 for item in results if item.get("meets_invest"))
    overall_label = (
        "Tasks ready for INVEST"
        if ready_count == len(results)
        else "Tasks reviewed"
    )
    return {
        "status": "success",
        "mode": "refined_tasks",
        "summary": {
            "task_count": len(results),
            "average_score": avg_score,
            "score_scale": 6,
            "overall_label": overall_label,
            "criteria_pass_rates": criteria_pass_rates,
        },
        "results": results,
        "refinement": {
            "before": refined_payload.get("summary_before", {}),
            "after": refined_payload.get("summary_after", {}),
            "invest_ready_total": refined_payload.get("invest_ready_total", 0),
            "refined_ready_total": refined_payload.get("refined_ready_total", 0),
            "invest_not_ready_total": refined_payload.get("invest_not_ready_total", 0),
            "refined_total": len(results),
            "displayed_total": len(results),
        },
    }

def split_invest_inputs(text: str, split_mode: str) -> List[str]:
    """
    Split user input into logical INVEST items.
    In line mode, continuation lines are merged when they appear to belong
    to the same requirement sentence.
    
    Also handles:
    1. User story format: "As a ..., I want to action1, action2, and action3 ..."
    2. Comma-separated lists: "Build login, forgot password, social login, audit log, and admin dashboard"
    """
    raw_text = text or ""
    if split_mode == "paragraph":
        return [chunk.strip() for chunk in re.split(r"\n\s*\n+", raw_text) if chunk.strip()]

    merged_items: List[str] = []
    current = ""

    for raw_line in raw_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if not current:
            current = line
            continue

        starts_like_continuation = bool(re.match(r"^[a-zA-ZÀ-ỹ0-9]", line)) and line[:1].islower()
        previous_expects_continuation = current.endswith(",") or current.endswith(":") or current.endswith(";")

        if previous_expects_continuation or starts_like_continuation:
            current = f"{current} {line}"
        else:
            merged_items.append(current.strip())
            current = line

    if current:
        merged_items.append(current.strip())

    # Process merged items to detect and split various patterns
    final_items: List[str] = []
    for item in merged_items:
        # First try to split as user story if it matches that pattern
        user_story_result = _split_user_story(item)
        if user_story_result:
            final_items.extend(user_story_result)
        # Otherwise try comma-separated list
        elif _is_comma_separated_list(item):
            split_items = _split_comma_separated_list(item)
            final_items.extend(split_items)
        else:
            final_items.append(item)
    
    return final_items


def _split_user_story(text: str) -> List[str]:
    """
    Split user story format text.
    E.g., "As a student, I want to register, view, update and delete my mentoring requests."
    -> ["As a student, I want to register my mentoring requests.",
        "As a student, I want to view my mentoring requests.",
        "As a student, I want to update my mentoring requests.",
        "As a student, I want to delete my mentoring requests."]
    """
    # Pattern: "As a [role], I want to [action1], [action2], and [action3] [suffix]"
    user_story_pattern = r'^(As\s+[^,]+,\s*I\s+want\s+to)\s+(.+?)$'
    match = re.match(user_story_pattern, text, re.IGNORECASE)
    
    if not match:
        return []
    
    prefix = match.group(1)  # "As a student, I want to"
    after_prefix = match.group(2)  # "register, view, update and delete my mentoring requests."
    
    # Extract actions and suffix
    # Find the last "and" to separate actions from suffix
    and_index = after_prefix.rfind(' and ')
    
    if and_index == -1:
        # No "and", try to find comma pattern
        comma_parts = [p.strip() for p in after_prefix.split(',')]
        if len(comma_parts) < 2:
            return []
        
        # Find where the actual tail begins (typically after last noun-like word)
        actions_part = ', '.join(comma_parts[:-1])
        suffix_part = comma_parts[-1]
    else:
        # Extract prefix before "and" and everything after "and"
        before_and = after_prefix[:and_index].strip()
        after_and = after_prefix[and_index + 5:].strip()  # Skip " and "
        
        # Split before_and by comma to get all actions
        action_list = [p.strip() for p in before_and.split(',')]
        action_list.append(after_and.split()[0].strip(',.;') if after_and.split() else after_and)
        
        # Suffix is everything after the last action
        suffix_words = after_and.split()[1:] if ' ' in after_and else []
        suffix_part = ' '.join(suffix_words) if suffix_words else after_and
    
    # Now split by comma in the actions part
    if and_index != -1:
        before_and = after_prefix[:and_index].strip()
        after_and_part = after_prefix[and_index + 5:].strip()
        
        # Extract all actions
        actions = [p.strip() for p in before_and.split(',')]
        
        # The last action and suffix are in after_and_part
        # Find where the action ends and suffix begins
        last_action_match = re.match(r'^(\S+)(?:\s+(.+))?$', after_and_part)
        if last_action_match:
            last_action = last_action_match.group(1)
            suffix_part = (last_action_match.group(2) or '').strip()
            actions.append(last_action)
        else:
            actions.append(after_and_part)
            suffix_part = ''
    else:
        comma_parts = [p.strip() for p in after_prefix.split(',')]
        actions = [p for p in comma_parts if p]
        suffix_part = ''
    
    # Clean up actions and build results
    result: List[str] = []
    for action in actions:
        if action:
            action_clean = action.strip(',.;: ')
            if suffix_part:
                full_text = f"{prefix} {action_clean} {suffix_part}".strip()
            else:
                full_text = f"{prefix} {action_clean}".strip()
            
            # Ensure sentence ends with period
            if not full_text.endswith('.'):
                full_text += '.'
            
            result.append(full_text)
    
    return result if len(result) > 1 else []


def _is_comma_separated_list(text: str) -> bool:
    """
    Detect if text is a comma-separated list of features/items.
    E.g., "Build login, forgot password, social login, audit log, and admin dashboard"
    """
    comma_count = text.count(',')
    return comma_count >= 1 and len(text) > 40


def _split_comma_separated_list(text: str) -> List[str]:
    """
    Split comma-separated list into individual items.
    Handles the pattern: "item1, item2, item3, and item4"
    """
    # Replace " and " with "," to handle the final "and" conjunction
    normalized = re.sub(r'\s+and\s+', ', ', text, flags=re.IGNORECASE)
    
    # Split by comma
    items = [item.strip() for item in normalized.split(',') if item.strip()]
    
    # Clean up items
    if items:
        cleaned_items = _clean_list_items(items)
        return cleaned_items
    
    return [text]


def _clean_list_items(items: List[str]) -> List[str]:
    """
    Clean up list items by extracting and applying common prefixes/verbs.
    E.g., "Build login, forgot password, social login" 
    -> Apply "Build" verb to all items that don't start with it
    """
    if not items:
        return items
    
    cleaned_items: List[str] = []
    
    # Extract common verb/action from first item (preserve original casing)
    first_item = items[0]
    common_verb_match = re.match(r'^([A-Za-z]+)\s+', first_item)
    common_verb_original = common_verb_match.group(1) if common_verb_match else None
    common_verb_lower = common_verb_original.lower() if common_verb_original else None
    
    for item in items:
        cleaned_item = item.strip()
        
        # If we have a common verb
        if common_verb_lower:
            # Extract the first word of this item
            first_word = cleaned_item.split()[0].lower() if cleaned_item.split() else ""
            
            # If the first word is NOT the common verb, prepend it
            if first_word != common_verb_lower:
                cleaned_item = f"{common_verb_original} {cleaned_item}"
        
        cleaned_items.append(cleaned_item)
    
    return cleaned_items

# Khởi tạo FastAPI app
app = FastAPI(
    title="Software Effort Estimation API",
    description="API để phân tích yêu cầu phần mềm và ước lượng nỗ lực phát triển",
    version="1.0.0"
)

# Khởi tạo các thành phần
analyzer = RequirementAnalyzer()
estimator = EffortEstimator()

# Jinja2 templates
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
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
    """
    Health check endpoint for task generation service
    """
    return {"status": "healthy", "service": "task-generation"}

@app.post("/api/task-generation/generate")
async def generate_tasks_from_text(requirement: RequirementText):
    """
    Generate tasks from requirement text
    """
    try:
        analyzer = RequirementAnalyzer()
        extracted_reqs = analyzer.extract_requirements(requirement.text)
        
        # Convert to tasks format
        tasks = []
        for req in extracted_reqs:
            # Map complexity level to story points estimate
            complexity_map = {
                'high': 13,
                'medium': 8,
                'low': 3,
                'very_high': 20,
                'very_low': 1
            }
            # Clean complexity level - extract base word (e.g., "medium_complexity" → "medium")
            raw_complexity = req.get("technical_complexity", "medium").lower()
            complexity_level = raw_complexity.split('_')[0]  # Get first part
            if complexity_level not in complexity_map:
                complexity_level = "medium"  # Reset to default if not found
            estimated_effort = complexity_map.get(complexity_level, 5)
            
            # Extract domain from requirement text or use default
            req_text = req.get("text", "")
            text_lower = req_text.lower()
            domain = "General"
            
            # Healthcare domain detection
            if any(kw in text_lower for kw in ["bệnh viện", "bệnh nhân", "bác sĩ", "y tế", "medical", "hospital", "patient", "physician", "doctor", "diagnosis"]):
                domain = "Healthcare/Hospital"
            elif any(kw in text_lower for kw in ["xét nghiệm", "lab", "laboratory", "test", "analyzer", "sample"]):
                domain = "Laboratory/Testing"
            elif any(kw in text_lower for kw in ["phẫu thuật", "mổ", "surgery", "surgical", "operating"]):
                domain = "Surgery"
            elif any(kw in text_lower for kw in ["thuốc", "nhà thuốc", "pharmacy", "medication", "drug"]):
                domain = "Pharmacy"
            elif any(kw in text_lower for kw in ["viện phí", "thanh toán", "payment", "billing", "invoice"]):
                domain = "Billing/Payment"
            elif any(kw in text_lower for kw in ["khách sạn", "hotel", "booking"]):
                domain = "Hotel Management"
            elif any(kw in text_lower for kw in ["đặt phòng", "reservation"]):
                domain = "Reservation System"
            
            # Generate acceptance criteria from requirement text
            acceptance_criteria = []
            if "must" in req_text.lower() or "shall" in req_text.lower() or "phải" in req_text.lower():
                acceptance_criteria.append(f"The requirement is implemented according to specifications")
                acceptance_criteria.append(f"All validation rules are enforced")
                acceptance_criteria.append(f"Error handling is in place")
            
            # Extract user role from text or use generic
            role = "User"
            if any(kw in req_text.lower() for kw in ["admin", "quản trị", "administrator"]):
                role = "Administrator"
            elif any(kw in req_text.lower() for kw in ["customer", "khách", "bệnh nhân"]):
                role = "Patient/Customer"
            elif any(kw in req_text.lower() for kw in ["staff", "nhân viên", "điều dưỡng", "nurse", "technician"]):
                role = "Healthcare Staff"
            elif any(kw in req_text.lower() for kw in ["guest", "khách", "thuê"]):
                role = "Guest"
            elif any(kw in req_text.lower() for kw in ["doctor", "bác sĩ", "physician"]):
                role = "Physician"
            
            tasks.append({
                "id": req.get("id", ""),
                "title": req_text[:100],  # First 100 chars
                "description": req_text,  # Full text as description
                "priority": req.get("priority", "medium"),
                "type": req.get("type", "general"),
                "complexity": complexity_level,
                "domain": domain,
                "story_points": estimated_effort,
                "role": role,
                "acceptance_criteria": acceptance_criteria,
                "estimated_effort": estimated_effort,
                "score": round(req.get("score", 0), 2)
            })
        
        return {
            "status": "success",
            "tasks": tasks,
            "total_tasks": len(tasks)
        }
    except Exception as e:
        logger.error(f"Error generating tasks: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/task-generation/generate-from-file")
async def generate_tasks_from_file(file: UploadFile = File(...)):
    """
    Generate tasks from uploaded file
    """
    try:
        content = await file.read()
        text_content = content.decode("utf-8")
        
        analyzer = RequirementAnalyzer()
        extracted_reqs = analyzer.extract_requirements(text_content)
        
        # Convert to tasks format
        tasks = []
        for req in extracted_reqs:
            # Map complexity level to story points estimate
            complexity_map = {
                'high': 13,
                'medium': 8,
                'low': 3,
                'very_high': 20,
                'very_low': 1
            }
            # Clean complexity level - extract base word (e.g., "medium_complexity" → "medium")
            raw_complexity = req.get("technical_complexity", "medium").lower()
            complexity_level = raw_complexity.split('_')[0]  # Get first part
            if complexity_level not in complexity_map:
                complexity_level = "medium"  # Reset to default if not found
            estimated_effort = complexity_map.get(complexity_level, 5)
            
            # Extract domain from requirement text or use default
            req_text = req.get("text", "")
            text_lower = req_text.lower()
            domain = "General"
            
            # Healthcare domain detection
            if any(kw in text_lower for kw in ["bệnh viện", "bệnh nhân", "bác sĩ", "y tế", "medical", "hospital", "patient", "physician", "doctor", "diagnosis"]):
                domain = "Healthcare/Hospital"
            elif any(kw in text_lower for kw in ["xét nghiệm", "lab", "laboratory", "test", "analyzer", "sample"]):
                domain = "Laboratory/Testing"
            elif any(kw in text_lower for kw in ["phẫu thuật", "mổ", "surgery", "surgical", "operating"]):
                domain = "Surgery"
            elif any(kw in text_lower for kw in ["thuốc", "nhà thuốc", "pharmacy", "medication", "drug"]):
                domain = "Pharmacy"
            elif any(kw in text_lower for kw in ["viện phí", "thanh toán", "payment", "billing", "invoice"]):
                domain = "Billing/Payment"
            elif any(kw in text_lower for kw in ["khách sạn", "hotel", "booking"]):
                domain = "Hotel Management"
            elif any(kw in text_lower for kw in ["đặt phòng", "reservation"]):
                domain = "Reservation System"
            
            # Generate acceptance criteria from requirement text
            acceptance_criteria = []
            if "must" in req_text.lower() or "shall" in req_text.lower() or "phải" in req_text.lower():
                acceptance_criteria.append(f"The requirement is implemented according to specifications")
                acceptance_criteria.append(f"All validation rules are enforced")
                acceptance_criteria.append(f"Error handling is in place")
            
            # Extract user role from text or use generic
            role = "User"
            if any(kw in req_text.lower() for kw in ["admin", "quản trị", "administrator"]):
                role = "Administrator"
            elif any(kw in req_text.lower() for kw in ["customer", "khách", "bệnh nhân"]):
                role = "Patient/Customer"
            elif any(kw in req_text.lower() for kw in ["staff", "nhân viên", "điều dưỡng", "nurse", "technician"]):
                role = "Healthcare Staff"
            elif any(kw in req_text.lower() for kw in ["guest", "khách", "thuê"]):
                role = "Guest"
            elif any(kw in req_text.lower() for kw in ["doctor", "bác sĩ", "physician"]):
                role = "Physician"
            
            tasks.append({
                "id": req.get("id", ""),
                "title": req_text[:100],  # First 100 chars
                "description": req_text,  # Full text as description
                "priority": req.get("priority", "medium"),
                "type": req.get("type", "general"),
                "complexity": complexity_level,
                "domain": domain,
                "story_points": estimated_effort,
                "role": role,
                "acceptance_criteria": acceptance_criteria,
                "estimated_effort": estimated_effort,
                "score": round(req.get("score", 0), 2)
            })
        
        return {
            "status": "success",
            "tasks": tasks,
            "total_tasks": len(tasks),
            "filename": file.filename
        }
    except Exception as e:
        logger.error(f"Error generating tasks from file: {str(e)}", exc_info=True)
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

@app.get("/task-generation", response_class=HTMLResponse)
async def task_generation_page(request: Request):
    """
    Trang task generation và automated effort estimation
    """
    return templates.TemplateResponse("task_generation.html", {"request": request})

@app.get("/task_Invest", response_class=HTMLResponse)
async def task_invest_page(request: Request):
    """
    Trang hien thi ket qua/task INVEST
    """
    return templates.TemplateResponse(
        "task_Invest.html",
        {
            "request": request,
            "analysis_data": None,
            "active_tab": "text",
            "form_values": {
                "text": "",
                "split_mode": "line",
                "min_length": 15,
            },
            "uploaded_file_name": "",
        },
    )


async def _process_task_invest_submission(
    *,
    text: str = "",
    split_mode: str = "line",
    min_length: int = 15,
    input_mode: str = "text",
    file: Optional[UploadFile] = None,
) -> Dict[str, Any]:
    analysis_data: Dict[str, Any]
    logger.info(f"input_mode={input_mode}, file={file.filename if file else None}, text_len={len(text)}")
    has_uploaded_file = bool(file and getattr(file, "filename", None))
    effective_input_mode = "file" if has_uploaded_file else ("file" if input_mode == "file" else "text")
    logger.info(f"effective_input_mode={effective_input_mode}")
    split_mode = (split_mode or "line").lower()
    min_length = max(1, int(min_length or 15))

    if effective_input_mode == "file":
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="Please choose a file to analyze.")

        allowed_extensions = {".txt", ".md", ".json", ".csv"}
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Please upload one of: {', '.join(sorted(allowed_extensions))}"
            )

        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        decoded_text = content.decode("utf-8-sig")
        payload = _parse_uploaded_tasks_to_payload(decoded_text, file_ext, split_mode, min_length)
        uploaded_tasks = payload.get("tasks", []) if isinstance(payload, dict) else []
        if not uploaded_tasks:
            analysis_data = _build_empty_invest_response()
        else:
            # Analyze uploaded tasks with InvestAnalyzer
            analyzer = InvestAnalyzer()
            results = []
            for task in uploaded_tasks:
                task_text = _compose_invest_task_text(
                    task.get("title", ""),
                    task.get("description", ""),
                    task.get("acceptance_criteria", [])
                )
                results.extend(analyzer.analyze_many(task_text))
            analysis_data = _build_invest_response_from_results(results)
            analysis_data["source"] = {
                "filename": file.filename,
                "file_type": file_ext,
                "task_count": len(uploaded_tasks),
            }
        return analysis_data

    analyzer = InvestAnalyzer()
    chunks = split_invest_inputs(text or "", split_mode)
    tasks = [chunk.strip() for chunk in chunks if chunk and chunk.strip() and len(chunk.strip()) >= min_length]
    if not tasks:
        return _build_empty_invest_response()

    # Analyze all tasks with InvestAnalyzer
    results = []
    for task in tasks:
        results.extend(analyzer.analyze_many(task))

    # Return results directly from InvestAnalyzer (accurate INVEST evaluation)
    return _build_invest_response_from_results(results)


@app.post("/task_Invest", response_class=HTMLResponse)
async def task_invest_page_submit(
    request: Request,
    text: str = Form(""),
    split_mode: str = Form("line"),
    min_length: int = Form(15),
    input_mode: str = Form("text"),
    file: Optional[UploadFile] = File(None),
):
    """
    Process INVEST analysis directly on the /task_Invest page.
    Supports both text input and uploaded files.
    """
    analysis_data: Dict[str, Any]
    has_uploaded_file = bool(file and getattr(file, "filename", None))
    effective_input_mode = "file" if has_uploaded_file else ("file" if input_mode == "file" else "text")
    active_tab = effective_input_mode
    uploaded_file_name = file.filename if file and file.filename else ""

    try:
        split_mode = (split_mode or "line").lower()
        min_length = max(1, int(min_length or 15))
        analysis_data = await _process_task_invest_submission(
            text=text,
            split_mode=split_mode,
            min_length=min_length,
            input_mode=input_mode,
            file=file,
        )
    except HTTPException as exc:
        analysis_data = _build_error_invest_response(exc.detail)
    except UnicodeDecodeError:
        analysis_data = _build_error_invest_response("File must be UTF-8 encoded.")
    except Exception as exc:
        logger.error(f"Error processing /task_Invest form: {exc}", exc_info=True)
        analysis_data = _build_error_invest_response(str(exc))

    return templates.TemplateResponse(
        "task_Invest.html",
        {
            "request": request,
            "analysis_data": analysis_data,
            "active_tab": active_tab,
            "form_values": {
                "text": text or "",
                "split_mode": split_mode,
                "min_length": min_length,
            },
            "uploaded_file_name": uploaded_file_name,
        },
    )


@app.post("/api/task-invest/analyze-form")
async def analyze_invest_form(
    text: str = Form(""),
    split_mode: str = Form("line"),
    min_length: int = Form(15),
    input_mode: str = Form("text"),
    file: Optional[UploadFile] = File(None),
):
    try:
        analysis_data = await _process_task_invest_submission(
            text=text,
            split_mode=split_mode,
            min_length=min_length,
            input_mode=input_mode,
            file=file,
        )
        analysis_data["active_tab"] = "file" if (file and getattr(file, "filename", None)) else ("file" if input_mode == "file" else "text")
        return analysis_data
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded.")
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error processing /api/task-invest/analyze-form: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/task-invest/analyze")
async def analyze_invest_tasks(payload: InvestRequest):
    """
    Analyze tasks/user stories with INVEST criteria
    """
    try:
        split_mode = (payload.split_mode or "line").lower()
        min_length = max(1, payload.min_length or 15)
        analyzer = InvestAnalyzer()

        chunks = split_invest_inputs(payload.text or "", split_mode)
        tasks = [chunk.strip() for chunk in chunks if chunk and chunk.strip() and len(chunk.strip()) >= min_length]
        if not tasks:
            return _build_empty_invest_response()

        results = []
        for task in tasks:
            results.extend(analyzer.analyze_many(task))
        return _build_invest_response_from_results(results)
    except Exception as e:
        logger.error(f"Error analyzing INVEST tasks: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))



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
    uvicorn.run("requirement_analyzer.api:app", host=host, port=port, reload=False)

if __name__ == "__main__":
    start_server(port=8000)
