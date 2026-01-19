#!/bin/bash
# Test script for production API

echo "🧪 Testing Production Infrastructure"
echo "===================================="
echo ""

# Check Python
echo "1️⃣ Checking Python..."
python3 --version || { echo "❌ Python3 not found"; exit 1; }
echo "✅ Python OK"
echo ""

# Check dependencies
echo "2️⃣ Checking dependencies..."
python3 -c "import fastapi; print(f'   FastAPI: {fastapi.__version__}')" 2>/dev/null || echo "❌ FastAPI not installed"
python3 -c "import pydantic; print(f'   Pydantic: {pydantic.__version__}')" 2>/dev/null || echo "❌ Pydantic not installed"
python3 -c "import uvicorn; print(f'   Uvicorn: {uvicorn.__version__}')" 2>/dev/null || echo "❌ Uvicorn not installed"
python3 -c "import sklearn; print(f'   Scikit-learn: {sklearn.__version__}')" 2>/dev/null || echo "❌ Scikit-learn not installed"
echo ""

# Check models
echo "3️⃣ Checking models..."
MODEL_DIR="requirement_analyzer/models/task_gen/models"
if [ -d "$MODEL_DIR" ]; then
    echo "   Model directory: ✅"
    for model in requirement_detector_model.joblib type_model.joblib priority_model.joblib domain_model.joblib; do
        if [ -f "$MODEL_DIR/$model" ]; then
            echo "   - $model: ✅"
        else
            echo "   - $model: ❌ (missing)"
        fi
    done
else
    echo "   ❌ Model directory not found: $MODEL_DIR"
fi
echo ""

# Check environment
echo "4️⃣ Checking environment..."
if [ -f ".env" ]; then
    echo "   .env: ✅"
else
    echo "   .env: ⚠️  (not found - copy from .env.example)"
fi
echo ""

# Test router import
echo "5️⃣ Testing API structure..."
python3 -c "
import sys
sys.path.append('.')
try:
    from app.routers import tasks
    print('   ✅ Router import OK')
except ImportError as e:
    print(f'   ❌ Router import failed: {e}')
except Exception as e:
    print(f'   ⚠️  Import works but initialization failed: {e}')
    print('   (This is expected if spacy/numpy version conflict exists)')
" 2>&1
echo ""

# Test middleware import
python3 -c "
import sys
sys.path.append('.')
try:
    from app.middleware.logging import LoggingMiddleware
    print('   ✅ Middleware import OK')
except ImportError as e:
    print(f'   ❌ Middleware import failed: {e}')
" 2>&1
echo ""

echo "📊 Test Summary"
echo "=============="
echo ""
echo "✅ = Ready"
echo "⚠️  = Needs configuration"
echo "❌ = Needs installation/fixing"
echo ""
echo "Next steps:"
echo "1. Fix any ❌ issues above"
echo "2. Copy .env.example to .env and configure"
echo "3. Start API: python3 -m uvicorn app.main:app --reload --port 8000"
echo "4. Visit http://localhost:8000/docs for interactive API docs"
echo ""
