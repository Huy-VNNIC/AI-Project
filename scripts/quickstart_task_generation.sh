#!/bin/bash
# Quick start script for Task Generation
# Helps users choose and test modes easily

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "================================================================"
echo "              TASK GENERATION QUICK START"
echo "================================================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.8+${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python found: $(python3 --version)${NC}"
echo ""

# Check if in correct directory
if [ ! -f "requirement_analyzer/task_gen/__init__.py" ]; then
    echo -e "${RED}❌ Please run this script from project root directory${NC}"
    exit 1
fi

# Menu
echo "Choose mode to test:"
echo ""
echo "  1) Template Mode (Fast, Free, Works Offline)"
echo "  2) LLM Mode - OpenAI (Natural, Costs ~\$0.001/task)"
echo "  3) LLM Mode - Anthropic (Natural, Costs ~\$0.002/task)"
echo "  4) Compare Both Modes"
echo "  5) Check Configuration"
echo "  6) Install Dependencies"
echo ""
read -p "Enter choice [1-6]: " choice

case $choice in
  1)
    echo ""
    echo "================================================================"
    echo "Testing TEMPLATE MODE"
    echo "================================================================"
    echo ""
    
    # Check dependencies
    echo "Checking dependencies..."
    python3 -c "import spacy, nltk, sklearn" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}⚠️  Missing dependencies. Installing...${NC}"
        pip install -r requirements-task-generation.txt
        python3 -m spacy download en_core_web_sm
        python3 scripts/task_generation/test_installation.py
    fi
    
    # Set env
    export TASK_GEN_MODE=template
    
    # Run demo
    echo ""
    echo "Running template demo..."
    cd scripts/task_generation
    python3 demo.py
    
    echo ""
    echo -e "${GREEN}✓ Template demo complete!${NC}"
    echo "Output saved to: scripts/task_generation/demo_tasks.json"
    ;;
    
  2)
    echo ""
    echo "================================================================"
    echo "Testing LLM MODE - OpenAI"
    echo "================================================================"
    echo ""
    
    # Check API key
    if [ -z "$OPENAI_API_KEY" ]; then
        echo -e "${YELLOW}⚠️  OPENAI_API_KEY not set${NC}"
        echo ""
        read -p "Enter your OpenAI API key (or press Enter to skip): " api_key
        if [ -z "$api_key" ]; then
            echo -e "${RED}❌ Cannot proceed without API key${NC}"
            echo "Get your key from: https://platform.openai.com/api-keys"
            exit 1
        fi
        export OPENAI_API_KEY="$api_key"
    fi
    
    # Install openai
    echo "Checking OpenAI SDK..."
    python3 -c "import openai" 2>/dev/null || pip install openai
    
    # Set env
    export TASK_GEN_MODE=llm
    export LLM_PROVIDER=openai
    export LLM_MODEL=gpt-4o-mini
    
    # Run demo
    echo ""
    echo "Running LLM demo (this may take 30-60 seconds)..."
    cd scripts/task_generation
    python3 demo_llm.py
    
    echo ""
    echo -e "${GREEN}✓ LLM demo complete!${NC}"
    echo "Output saved to: scripts/task_generation/demo_llm_tasks.json"
    ;;
    
  3)
    echo ""
    echo "================================================================"
    echo "Testing LLM MODE - Anthropic"
    echo "================================================================"
    echo ""
    
    # Check API key
    if [ -z "$ANTHROPIC_API_KEY" ]; then
        echo -e "${YELLOW}⚠️  ANTHROPIC_API_KEY not set${NC}"
        echo ""
        read -p "Enter your Anthropic API key (or press Enter to skip): " api_key
        if [ -z "$api_key" ]; then
            echo -e "${RED}❌ Cannot proceed without API key${NC}"
            echo "Get your key from: https://console.anthropic.com/"
            exit 1
        fi
        export ANTHROPIC_API_KEY="$api_key"
    fi
    
    # Install anthropic
    echo "Checking Anthropic SDK..."
    python3 -c "import anthropic" 2>/dev/null || pip install anthropic
    
    # Set env
    export TASK_GEN_MODE=llm
    export LLM_PROVIDER=anthropic
    export LLM_MODEL=claude-3-haiku-20240307
    
    # Run demo (modify demo_llm.py to support anthropic)
    echo ""
    echo "Running LLM demo (this may take 30-60 seconds)..."
    cd scripts/task_generation
    python3 demo_llm.py
    
    echo ""
    echo -e "${GREEN}✓ LLM demo complete!${NC}"
    echo "Output saved to: scripts/task_generation/demo_llm_tasks.json"
    ;;
    
  4)
    echo ""
    echo "================================================================"
    echo "Comparing Template vs LLM Modes"
    echo "================================================================"
    echo ""
    
    # Run both
    echo "Step 1: Running template mode..."
    export TASK_GEN_MODE=template
    cd scripts/task_generation
    python3 demo.py
    
    echo ""
    echo "Step 2: Running LLM mode..."
    
    # Check API key
    if [ -z "$OPENAI_API_KEY" ]; then
        echo -e "${YELLOW}⚠️  OPENAI_API_KEY not set. Skipping LLM demo.${NC}"
    else
        export TASK_GEN_MODE=llm
        export LLM_PROVIDER=openai
        export LLM_MODEL=gpt-4o-mini
        python3 demo_llm.py
        
        echo ""
        echo "Step 3: Comparing outputs..."
        echo ""
        echo "Template output:"
        jq '.tasks[0] | {title, description, acceptance_criteria: .acceptance_criteria[:2]}' demo_tasks.json 2>/dev/null || cat demo_tasks.json | head -20
        
        echo ""
        echo "LLM output:"
        jq '.tasks[0] | {title, description, acceptance_criteria: .acceptance_criteria[:2]}' demo_llm_tasks.json 2>/dev/null || cat demo_llm_tasks.json | head -20
    fi
    
    echo ""
    echo -e "${GREEN}✓ Comparison complete!${NC}"
    ;;
    
  5)
    echo ""
    echo "================================================================"
    echo "Current Configuration"
    echo "================================================================"
    echo ""
    
    python3 -c "
from requirement_analyzer.task_gen import print_config
print_config()
"
    ;;
    
  6)
    echo ""
    echo "================================================================"
    echo "Installing Dependencies"
    echo "================================================================"
    echo ""
    
    # Base dependencies
    echo "Installing base dependencies..."
    pip install -r requirements-task-generation.txt
    
    # spaCy model
    echo ""
    echo "Downloading spaCy model..."
    python3 -m spacy download en_core_web_sm
    
    # NLTK data
    echo ""
    echo "Downloading NLTK data..."
    python3 -c "
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
"
    
    # Test installation
    echo ""
    echo "Testing installation..."
    cd scripts/task_generation
    python3 test_installation.py
    
    echo ""
    echo -e "${GREEN}✓ Installation complete!${NC}"
    ;;
    
  *)
    echo -e "${RED}Invalid choice${NC}"
    exit 1
    ;;
esac

echo ""
echo "================================================================"
echo "Next Steps:"
echo "================================================================"
echo ""
echo "1. Review outputs: cat scripts/task_generation/demo*.json"
echo "2. Read guide: less TASK_GENERATION_MODE_COMPARISON.md"
echo "3. Train models: cd scripts/task_generation && ./train_all.sh"
echo "4. Start API: python -m requirement_analyzer.api"
echo ""
echo "For help: less TASK_GENERATION_GUIDE.md"
echo ""
