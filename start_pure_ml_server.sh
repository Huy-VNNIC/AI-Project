#!/bin/bash
# Pure ML API - Start Server Script

echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║            🚀 Pure ML Test Generation API - Starting Server                    ║"
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Available Endpoints:"
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🖥️  WEB UI:"
echo "   🌐 http://localhost:8000/test-generation/feedback-ui"
echo "      → Interactive feedback system with test generation"
echo ""
echo "📡 API ENDPOINTS:"
echo "   POST http://localhost:8000/api/v3/test-generation/generate"
echo "        Generate test cases from requirements"
echo ""
echo "   POST http://localhost:8000/api/v3/test-generation/feedback"
echo "        Submit feedback (AI learns from this)"
echo ""
echo "   GET  http://localhost:8000/api/v3/test-generation/stats"
echo "        Get system statistics and health"
echo ""
echo "   GET  http://localhost:8000/api/v3/test-generation/insights"
echo "        Get AI learning insights"
echo ""
echo "📚 DOCUMENTATION:"
echo "   GET  http://localhost:8000/docs (Swagger UI)"
echo "   GET  http://localhost:8000/redoc (ReDoc)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔧 System Information:"
echo "   Directory: $(pwd)"
echo "   Python: $(python3 --version)"
echo "   venv: $([ -d .venv ] && echo "✅ Active" || echo "⚠️ Not found")"
echo ""
echo "⏳ Starting server on http://0.0.0.0:8000"
echo "   Press Ctrl+C to stop"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if venv exists and activate
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✅ Virtual environment activated"
    echo ""
fi

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
