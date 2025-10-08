"""
Main application file for Hugging Face deployment
"""
import os
import sys
from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional

# Add app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

# Mô hình cho request API
class RequirementText(BaseModel):
    text: str
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

# Tải các thành phần phân tích và ước lượng
try:
    from app.requirement_analyzer.analyzer import RequirementAnalyzer
    from app.requirement_analyzer.estimator import EffortEstimator
    from app.requirement_analyzer.utils import preprocess_text_for_estimation, improve_confidence_level
    print("Imported modules from app.requirement_analyzer successfully")
except ImportError as e:
    print(f"Error importing from app.requirement_analyzer: {e}")
    try:
        print("Trying to import from root requirement_analyzer module")
        from requirement_analyzer import RequirementAnalyzer, EffortEstimator
        
        # Define utility functions as fallbacks
        def preprocess_text_for_estimation(text):
            return text
            
        def improve_confidence_level(confidence, factors):
            return confidence
        print("Imported modules from root requirement_analyzer")
    except ImportError as e2:
        print(f"Failed to import requirement_analyzer: {e2}")
        raise ImportError("Could not import required modules")

# Thiết lập đường dẫn đến thư mục models
models_dir = os.path.join(os.path.dirname(__file__), "app", "models")
os.environ["MODEL_DIR"] = models_dir
print(f"Models directory: {models_dir}")

# Khởi tạo các thành phần
analyzer = RequirementAnalyzer()
estimator = EffortEstimator()

# Thiết lập đường dẫn đến static và templates
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
static_dir = os.path.join(os.path.dirname(__file__), "static")

# Mount static files
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Thiết lập Jinja2 templates
if os.path.exists(templates_dir):
    templates = Jinja2Templates(directory=templates_dir)
    
    @app.get("/", response_class=HTMLResponse)
    def main_page(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})
else:
    @app.get("/", response_class=HTMLResponse)
    def main_page():
        return """
        <html>
            <head><title>Software Effort Estimation API</title></head>
            <body>
                <h1>Software Effort Estimation API</h1>
                <p>API endpoints available at:</p>
                <ul>
                    <li>/api/estimate - POST endpoint for text-based estimation</li>
                    <li>/api/upload-requirements - POST endpoint for document upload and estimation</li>
                    <li>/docs - API Documentation</li>
                </ul>
            </body>
        </html>
        """

@app.post("/api/estimate")
def estimate_effort(req: RequirementText):
    """
    Ước lượng nỗ lực từ tài liệu yêu cầu
    """
    try:
        # Tiền xử lý và làm sạch văn bản
        text = preprocess_text_for_estimation(req.text)
        
        # Phân tích và ước lượng
        result = estimator.estimate_from_requirements(text, req.method)
        
        # Cải thiện độ tin cậy
        result = improve_confidence_level(result, text)
        
        return JSONResponse(content=result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-requirements")
async def upload_requirements(file: UploadFile = File(...), method: str = Form("weighted_average")):
    """
    Tải lên tài liệu yêu cầu và ước lượng nỗ lực
    """
    try:
        # Import parser
        from app.requirement_analyzer.document_parser import DocumentParser
        
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
        
        # Parse the document
        try:
            parser = DocumentParser()
            text = parser.parse(content, filename)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error parsing document: {str(e)}")
        
        # Tiền xử lý văn bản
        text = preprocess_text_for_estimation(text)
        
        # Phân tích và ước lượng
        result = estimator.estimate_from_requirements(text, method)
        
        # Cải thiện độ tin cậy
        result = improve_confidence_level(result, text)
        
        # Thêm thông tin về document
        result["document"] = {
            "filename": filename,
            "file_type": file_ext,
            "size_bytes": len(content),
            "text_length": len(text)
        }
        
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """
    Kiểm tra trạng thái hoạt động của API
    """
    return {"status": "ok", "version": "1.0.0"}

# Tải các gói NLTK cần thiết
@app.on_event("startup")
def download_nltk_data():
    try:
        import nltk
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('wordnet')
        nltk.download('averaged_perceptron_tagger')
        try:
            nltk.download('punkt_tab')
        except:
            pass
    except Exception as e:
        print(f"Error downloading NLTK data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
