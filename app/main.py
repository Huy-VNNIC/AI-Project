"""
FastAPI application for Task Generation API
Production-ready with logging, monitoring, and feedback collection
"""
import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from app.routers import tasks
from app.middleware.logging import LoggingMiddleware
from dotenv import load_dotenv

load_dotenv()


# Startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Task Generation API...")
    print(f"   Model dir: {os.getenv('MODEL_DIR', 'requirement_analyzer/models/task_gen/models')}")
    print(f"   Mode: {os.getenv('DEFAULT_MODE', 'model')}")
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

# Include routers
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])


@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "healthy",
        "service": "task-generation-api",
        "version": "1.0.0"
    }


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
