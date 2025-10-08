#!/bin/bash

# Script triển khai lên Hugging Face Spaces đơn giản hóa
# Thực hiện từ thư mục huggingface_deployment
set -e

# Các biến cấu hình
HUGGINGFACE_USERNAME="nhathuyvne"  # Điền username Hugging Face của bạn
SPACE_NAME="requirement-analyzer-api"  # Tên không gian trên Hugging Face
SPACE_TYPE="docker"  # Loại không gian (docker)

echo "=== Chuẩn bị triển khai lên Hugging Face ==="
echo "Người dùng: $HUGGINGFACE_USERNAME"
echo "Tên không gian: $SPACE_NAME"
echo "Loại không gian: $SPACE_TYPE"

# Kiểm tra đã đăng nhập chưa
echo "Kiểm tra trạng thái đăng nhập Hugging Face..."
if ! huggingface-cli whoami &> /dev/null; then
  echo "ERROR: Bạn chưa đăng nhập vào Hugging Face CLI. Hãy chạy 'huggingface-cli login' trước."
  exit 1
fi

# Kiểm tra nếu không gian đã tồn tại
echo "Kiểm tra không gian $HUGGINGFACE_USERNAME/$SPACE_NAME..."
huggingface-cli space info $HUGGINGFACE_USERNAME/$SPACE_NAME &> /dev/null
SPACE_EXISTS=$?

# Tạo file __init__.py để đảm bảo có thể import được
touch "$DEPLOYMENT_DIR/app/__init__.py"

if [ $SPACE_EXISTS -eq 0 ]; then
  echo "Không gian đã tồn tại, sẽ cập nhật..."
  huggingface-cli space upload . $HUGGINGFACE_USERNAME/$SPACE_NAME --path-in-space="/" --repo-type="space"
else
  echo "Tạo không gian mới: $HUGGINGFACE_USERNAME/$SPACE_NAME"
  huggingface-cli space create $HUGGINGFACE_USERNAME/$SPACE_NAME --type=$SPACE_TYPE --sdk=docker
  sleep 5  # Đợi không gian được tạo
  echo "Tải lên tệp tin..."
  huggingface-cli space upload . $HUGGINGFACE_USERNAME/$SPACE_NAME --path-in-space="/" --repo-type="space"
fi

echo "=== Triển khai hoàn tất ==="
echo "API của bạn sẽ có sẵn tại: https://$HUGGINGFACE_USERNAME-$SPACE_NAME.hf.space"
echo "Tài liệu API có sẵn tại: https://$HUGGINGFACE_USERNAME-$SPACE_NAME.hf.space/docs"
echo ""
echo "Lưu ý: Có thể mất vài phút để Docker container được xây dựng và khởi động trên Hugging Face."

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tải các thành phần phân tích và ước lượng
from app.requirement_analyzer.analyzer import RequirementAnalyzer
from app.requirement_analyzer.estimator import EffortEstimator
from app.requirement_analyzer.utils import preprocess_text_for_estimation, improve_confidence_level

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
EOL

# Tạo file requirements.txt đơn giản hơn
cat > "$DEPLOYMENT_DIR/requirements.txt" << EOL
fastapi==0.103.1
uvicorn==0.23.2
pydantic==2.3.0
python-multipart==0.0.6
nltk==3.8.1
scikit-learn==1.3.0
numpy==1.25.2
pandas==2.1.0
matplotlib==3.7.3
python-docx==1.0.1
pypdf2==3.0.1
jinja2==3.1.2
EOL

# Tạo file README.md cho Hugging Face
cat > "$DEPLOYMENT_DIR/README.md" << EOL
---
title: Software Requirement Analyzer API
emoji: 📊
colorFrom: blue
colorTo: green
sdk: python
app_port: 7860
---

# Software Requirement Analyzer API

This API provides endpoints for analyzing software requirements and estimating development effort based on requirement specifications.

## API Endpoints

### POST /api/estimate
Estimate development effort based on requirement text.

### POST /api/upload-requirements
Upload a requirements document file for analysis.

### GET /health
Check API status
EOL

# Tạo file .gitattributes để Hugging Face xử lý đúng
cat > "$DEPLOYMENT_DIR/.gitattributes" << EOL
*.7z filter=lfs diff=lfs merge=lfs -text
*.arrow filter=lfs diff=lfs merge=lfs -text
*.bin filter=lfs diff=lfs merge=lfs -text
*.bz2 filter=lfs diff=lfs merge=lfs -text
*.ftz filter=lfs diff=lfs merge=lfs -text
*.gz filter=lfs diff=lfs merge=lfs -text
*.h5 filter=lfs diff=lfs merge=lfs -text
*.joblib filter=lfs diff=lfs merge=lfs -text
*.lfs.* filter=lfs diff=lfs merge=lfs -text
*.mlmodel filter=lfs diff=lfs merge=lfs -text
*.model filter=lfs diff=lfs merge=lfs -text
*.msgpack filter=lfs diff=lfs merge=lfs -text
*.npy filter=lfs diff=lfs merge=lfs -text
*.npz filter=lfs diff=lfs merge=lfs -text
*.onnx filter=lfs diff=lfs merge=lfs -text
*.ot filter=lfs diff=lfs merge=lfs -text
*.parquet filter=lfs diff=lfs merge=lfs -text
*.pb filter=lfs diff=lfs merge=lfs -text
*.pickle filter=lfs diff=lfs merge=lfs -text
*.pkl filter=lfs diff=lfs merge=lfs -text
*.pt filter=lfs diff=lfs merge=lfs -text
*.pth filter=lfs diff=lfs merge=lfs -text
*.rar filter=lfs diff=lfs merge=lfs -text
*.safetensors filter=lfs diff=lfs merge=lfs -text
saved_model/**/* filter=lfs diff=lfs merge=lfs -text
*.tar.* filter=lfs diff=lfs merge=lfs -text
*.tflite filter=lfs diff=lfs merge=lfs -text
*.tgz filter=lfs diff=lfs merge=lfs -text
*.wasm filter=lfs diff=lfs merge=lfs -text
*.xz filter=lfs diff=lfs merge=lfs -text
*.zip filter=lfs diff=lfs merge=lfs -text
*tfevents* filter=lfs diff=lfs merge=lfs -text
EOL

# Tạo script download_dependencies.py
cat > "$DEPLOYMENT_DIR/packages.py" << EOL
"""
Utility script for downloading NLTK data
"""
import nltk
import os

def download_packages():
    """
    Downloads required NLTK packages
    """
    # Set NLTK data path
    nltk_data_dir = os.path.expanduser("~/nltk_data")
    os.makedirs(nltk_data_dir, exist_ok=True)
    nltk.data.path.append(nltk_data_dir)
    
    # Download NLTK data
    packages = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']
    for package in packages:
        try:
            nltk.download(package, quiet=True)
            print(f"Downloaded {package}")
        except Exception as e:
            print(f"Error downloading {package}: {e}")
    
    # Special case for punkt_tab
    try:
        nltk.download('punkt_tab', quiet=True)
        print("Downloaded punkt_tab")
    except Exception as e:
        print(f"Error downloading punkt_tab: {e}")
    
if __name__ == "__main__":
    download_packages()
EOL

echo "=== Cấu trúc triển khai đã được tạo thành công ==="
echo "Thư mục triển khai: $DEPLOYMENT_DIR"
echo "Để triển khai lên Hugging Face Spaces:"
echo "1. Tạo một Space mới trên Hugging Face với loại 'Gradio/Spaces SDK'"
echo "2. Đẩy nội dung thư mục $DEPLOYMENT_DIR lên repository GitHub của Space"
echo "3. Hugging Face sẽ tự động triển khai ứng dụng của bạn"