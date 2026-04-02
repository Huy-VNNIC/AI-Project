"""
FastAPI application for Task Generation API
Production-ready with logging, monitoring, and feedback collection
"""
import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from app.routers import tasks, unified, test_routes, testcase
from app.middleware.logging import LoggingMiddleware
from dotenv import load_dotenv

# Try to import V3 (Hybrid LLM) - PRIMARY
try:
    from requirement_analyzer.task_gen.api_adapter_v3 import router as v3_router
    V3_ROUTER_AVAILABLE = True
    print("✅ V3 HYBRID LLM LOADED")
except ImportError as e:
    V3_ROUTER_AVAILABLE = False
    print(f"❌ V3 Router not available: {e}")

# Try to import LLM-Free adapter - PREFERRED (no external APIs)
try:
    from requirement_analyzer.task_gen.api_adapter_llmfree import router as llmfree_router
    LLMFREE_ROUTER_AVAILABLE = True
    print("✅ LLM-FREE ADAPTER LOADED")
except ImportError as e:
    LLMFREE_ROUTER_AVAILABLE = False
    print(f"❌ LLM-Free Router not available: {e}")

# Try to import V2 test generation router - FALLBACK
try:
    from requirement_analyzer.task_gen.smart_ai_generator_v2 import AITestGenerator as GeneratorV2
    V2_ROUTER_AVAILABLE = True
except ImportError:
    V2_ROUTER_AVAILABLE = False
    GeneratorV2 = None

# Legacy routers (keep for backward compat)
try:
    from requirement_analyzer.task_gen.api_ai_test_generation_v3 import router as ai_test_router
    AI_TEST_ROUTER_AVAILABLE = True
except ImportError:
    AI_TEST_ROUTER_AVAILABLE = False

try:
    from requirement_analyzer.api_v2_test_generation import pure_ml_router
    PURE_ML_ROUTER_AVAILABLE = True
except ImportError:
    PURE_ML_ROUTER_AVAILABLE = False

try:
    from requirement_analyzer.api_v2_test_generation import router as v2_test_router
    V2_TEST_ROUTER_AVAILABLE = True
except ImportError:
    V2_TEST_ROUTER_AVAILABLE = False

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("\n" + "="*70)
    print("🚀 STARTING TASK GENERATION API")
    print("="*70)
    print(f"Model dir: {os.getenv('MODEL_DIR', 'requirement_analyzer/models/task_gen/models')}")
    print(f"Mode: {os.getenv('DEFAULT_MODE', 'model')}")
    print("\n📡 GENERATOR STATUS:")
    
    if LLMFREE_ROUTER_AVAILABLE:
        print("   ✅ LLM-Free (Smart NER) - PRIMARY")
    else:
        print("   ❌ LLM-Free (Smart NER) - NOT AVAILABLE")
    
    if V3_ROUTER_AVAILABLE:
        print("   ⚠️  V3 (Hybrid LLM) - AVAILABLE")
    else:
        print("   ❌ V3 (Hybrid LLM) - NOT AVAILABLE")
    
    if V2_ROUTER_AVAILABLE:
        print("   ⚠️  V2 (Rule-based) - AVAILABLE")
    else:
        print("   ❌ V2 (Rule-based) - NOT AVAILABLE")
    
    if AI_TEST_ROUTER_AVAILABLE:
        print("   ⚠️  Legacy AI Test Router - DEPRECATED")
    
    print("\n" + "="*70 + "\n")
    
    yield
    # Shutdown
    print("👋 Shutting down Task Generation API...")


# Create app
app = FastAPI(
    title="Task Generation API",
    description="Generate user stories and tasks from requirement documents",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging middleware
app.add_middleware(LoggingMiddleware)

# Include routers - LLM-FREE PRIMARY, V3 FALLBACK
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(unified.router, tags=["unified"])
app.include_router(test_routes.router, tags=["testing"])
app.include_router(testcase.router, tags=["testcase"])

# LLM-FREE (Primary - no external APIs)
if LLMFREE_ROUTER_AVAILABLE:
    app.include_router(llmfree_router)
    print("✅ LLM-Free Router included (Primary)")
else:
    print("❌ LLM-Free Router NOT available")

# V3 HYBRID LLM (Fallback)
if V3_ROUTER_AVAILABLE and not LLMFREE_ROUTER_AVAILABLE:
    app.include_router(v3_router)
    print("⚠️  V3 Router included (Fallback - LLM-Free not available)")
else:
    if V3_ROUTER_AVAILABLE:
        print("✅ V3 Router available but LLM-Free is primary")


@app.get("/")
async def root():
    """Home page - Unified UI with both systems"""
    unified_ui_file = PROJECT_ROOT / "templates" / "unified_ui.html"
    if unified_ui_file.exists():
        return FileResponse(unified_ui_file, media_type="text/html")
    # Fallback to old index
    index_file = PROJECT_ROOT / "templates" / "index_neumorphism.html"
    if index_file.exists():
        return FileResponse(index_file, media_type="text/html")
    raise HTTPException(status_code=404, detail="Index not found")


@app.get("/unified")
async def unified_ui():
    """Unified Test & Task Generation UI"""
    unified_ui_file = PROJECT_ROOT / "templates" / "unified_ui.html"
    if unified_ui_file.exists():
        return FileResponse(unified_ui_file, media_type="text/html")
    raise HTTPException(status_code=404, detail="Unified UI not found")


@app.get("/dashboard")
async def dashboard():
    """Dashboard - Navigation page"""
    dashboard_file = PROJECT_ROOT / "templates" / "dashboard.html"
    if dashboard_file.exists():
        return FileResponse(dashboard_file, media_type="text/html")
    raise HTTPException(status_code=404, detail="Dashboard not found")


@app.get("/task-generation")
async def task_generation():
    """Legacy task generation - Original UI"""
    test_gen_file = PROJECT_ROOT / "templates" / "task_generation.html"
    if test_gen_file.exists():
        return FileResponse(test_gen_file, media_type="text/html")
    raise HTTPException(status_code=404, detail="Task Generator not found")


@app.get("/testcase-generation")
async def testcase_generation():
    """Test case generator - Neumorphism version"""
    test_case_file = PROJECT_ROOT / "templates" / "testcase_generation_neumorphism.html"
    if test_case_file.exists():
        return FileResponse(test_case_file, media_type="text/html")
    raise HTTPException(status_code=404, detail="Test Case Generator not found")


@app.get("/test-generation/feedback-ui")
async def pure_ml_feedback_ui():
    """Serve Pure ML Feedback UI"""
    feedback_ui = PROJECT_ROOT / "templates" / "pure_ml_feedback.html"
    if feedback_ui.exists():
        return FileResponse(feedback_ui, media_type="text/html")
    raise HTTPException(status_code=404, detail="Feedback UI not found")


@app.get("/health")
async def health():
    """Detailed health check"""
    model_dir = Path(os.getenv('MODEL_DIR', 'requirement_analyzer/models/task_gen/models'))
    
    # Check models exist
    required_models = [
        'requirement_detector_model.joblib',
        'type_model.joblib',
        'priority_model.joblib',
        'domain_model.joblib'
    ]
    
    models_ok = all((model_dir / model).exists() for model in required_models)
    
    return {
        "status": "healthy" if models_ok else "degraded",
        "models_loaded": models_ok,
        "model_dir": str(model_dir),
        "mode": os.getenv('DEFAULT_MODE', 'model')
    }


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    workers = int(os.getenv("API_WORKERS", "4"))
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        workers=1 if os.getenv("ENVIRONMENT") == "development" else workers,
        reload=os.getenv("ENVIRONMENT") == "development"
    )
