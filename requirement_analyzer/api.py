"""
API cho service phân tích requirements và ước lượng nỗ lực
"""

import sys
from pathlib import Path

# Check for required dependencies first
try:
    from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Body, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse, HTMLResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    from pydantic import BaseModel
    from typing import Optional, List, Dict, Any
    import uvicorn
    import os
    import tempfile
    import pandas as pd
    import json
except ImportError as e:
    print("\n" + "="*70)
    print("ERROR: Missing required dependencies!")
    print("="*70)
    print(f"\nImport error: {e}")
    print("\nTo fix this issue, please install the required dependencies:")
    print("\n  1. Make sure you have activated the virtual environment:")
    print("     source venv/bin/activate  # On Linux/Mac")
    print("     venv\\Scripts\\activate     # On Windows")
    print("\n  2. Install dependencies:")
    print("     pip install -r requirements.txt")
    print("\n  OR use the automated setup script:")
    print("     ./start_estimation_service.sh")
    print("\n" + "="*70 + "\n")
    sys.exit(1)

# Thêm thư mục gốc vào sys.path để import các module khác
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import các module cần thiết
from requirement_analyzer.analyzer import RequirementAnalyzer
from requirement_analyzer.estimator import EffortEstimator
from requirement_analyzer.task_integration import get_integration

# Model cho request API
class RequirementText(BaseModel):
    text: str
    method: Optional[str] = "weighted_average"

class TaskList(BaseModel):
    tasks: List[Dict[str, Any]]
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

@app.post("/estimate")
def estimate_effort(req: RequirementText):
    """
    Ước lượng nỗ lực từ tài liệu yêu cầu
    """
    try:
        # Phân tích và ước lượng
        result = estimator.estimate_from_requirements(req.text, req.method)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-requirements")
async def upload_requirements(file: UploadFile = File(...), method: str = Form("weighted_average")):
    """
    Tải lên tài liệu yêu cầu và ước lượng nỗ lực
    """
    try:
        # Đọc file
        content = await file.read()
        text = content.decode("utf-8")
        
        # Phân tích và ước lượng
        result = estimator.estimate_from_requirements(text, method)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/estimate-from-tasks")
def estimate_from_tasks(tasks: TaskList):
    """
    Ước lượng nỗ lực từ danh sách công việc (tasks)
    """
    try:
        # Chuyển đổi tasks thành văn bản yêu cầu
        requirements_text = "Requirements Document\n\n"
        
        for i, task in enumerate(tasks.tasks):
            title = task.get("title", f"Task {i+1}")
            description = task.get("description", "")
            priority = task.get("priority", "Medium")
            complexity = task.get("complexity", "Medium")
            
            requirements_text += f"Requirement {i+1}: {title}\n"
            requirements_text += f"Description: {description}\n"
            requirements_text += f"Priority: {priority}\n"
            requirements_text += f"Complexity: {complexity}\n\n"
        
        # Phân tích và ước lượng
        result = estimator.estimate_from_requirements(requirements_text, tasks.method)
        
        # Thêm thông tin tasks vào kết quả
        result["tasks"] = tasks.tasks
        
        return JSONResponse(content=result)
    except Exception as e:
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

def start_server(host="0.0.0.0", port=8000):
    """
    Khởi động server API
    """
    uvicorn.run("requirement_analyzer.api:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    start_server()
