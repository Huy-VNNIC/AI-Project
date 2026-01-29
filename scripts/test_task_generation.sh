#!/bin/bash
# Test Task Generation Configuration

echo "================================================"
echo "Task Generation Configuration Test"
echo "================================================"

cd /home/dtu/AI-Project/AI-Project

# Activate virtual environment
source /home/dtu/AI-Project/.venv/bin/activate

# Test 1: Check model files exist
echo ""
echo "1. Checking model files..."
MODEL_DIR="requirement_analyzer/models/task_gen/models"
if [ -d "$MODEL_DIR" ]; then
    echo "✓ Model directory exists: $MODEL_DIR"
    echo "  Files found:"
    ls -lh "$MODEL_DIR"/*.joblib 2>/dev/null | wc -l
    ls "$MODEL_DIR"/*.joblib 2>/dev/null | head -3
else
    echo "✗ Model directory not found: $MODEL_DIR"
fi

# Test 2: Check config
echo ""
echo "2. Checking configuration..."
python3 << 'EOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path('/home/dtu/AI-Project/AI-Project')))

try:
    from requirement_analyzer.task_gen.config import GENERATOR_MODE, MODEL_DIR
    print(f"  Generator mode: {GENERATOR_MODE}")
    print(f"  Model directory: {MODEL_DIR}")
    print(f"  Model dir exists: {MODEL_DIR.exists()}")
    
    if MODEL_DIR.exists():
        files = list(MODEL_DIR.glob('*.joblib'))
        print(f"  Found {len(files)} .joblib files")
    else:
        print(f"  ✗ Model directory does not exist!")
except Exception as e:
    print(f"  ✗ Error: {e}")
EOF

# Test 3: Test pipeline initialization
echo ""
echo "3. Testing pipeline initialization..."
python3 << 'EOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path('/home/dtu/AI-Project/AI-Project')))

try:
    from requirement_analyzer.task_gen import get_pipeline
    
    print("  Initializing pipeline with mode='model'...")
    pipeline = get_pipeline(generator_mode='model')
    
    print(f"  ✓ Pipeline initialized")
    print(f"  Generator mode: {pipeline.generator_mode}")
    print(f"  Generator class: {type(pipeline.generator).__name__}")
    
    # Test generation
    print("\n  Testing task generation...")
    result = pipeline.generate_tasks(
        text="The system must allow users to login with email and password.",
        max_tasks=1
    )
    
    print(f"  ✓ Generated {len(result.tasks)} task(s)")
    if result.tasks:
        print(f"  Task title: {result.tasks[0].title}")
        
except Exception as e:
    import traceback
    print(f"  ✗ Error: {e}")
    traceback.print_exc()
EOF

echo ""
echo "================================================"
echo "Test Complete"
echo "================================================"
