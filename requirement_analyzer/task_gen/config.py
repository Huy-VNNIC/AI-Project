"""
Configuration for Task Generation Pipeline
Centralized config to switch between modes easily
"""
import os
from pathlib import Path
from typing import Optional

# ============================================================================
# GENERATOR MODE
# ============================================================================
# Choose generator mode:
#   - "model": ML-based generation (trained models, no API required)
#   - "template": Rule-based templates (fast, free, deterministic)
#   - "llm": LLM-based generation (natural, costs API credits)
GENERATOR_MODE = os.getenv("TASK_GEN_MODE", "model")  # Default: model


# ============================================================================
# LLM SETTINGS (Only used if GENERATOR_MODE="llm")
# ============================================================================
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # "openai" or "anthropic"

# Model selection
LLM_MODEL = os.getenv("LLM_MODEL", None)  # Auto-select if None
# Examples:
#   OpenAI: "gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"
#   Anthropic: "claude-3-haiku-20240307", "claude-3-5-sonnet-20241022"

# API Key (or set in environment)
LLM_API_KEY = os.getenv("OPENAI_API_KEY", None)  # Or ANTHROPIC_API_KEY

# Generation parameters
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))  # 0.0-1.0, lower = more consistent
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "2"))


# ============================================================================
# MODEL PATHS
# ============================================================================
def get_model_dir() -> Path:
    """Get path to trained models directory"""
    project_root = Path(__file__).parent.parent.parent
    # Models are in requirement_analyzer/models/task_gen/models/
    return project_root / 'requirement_analyzer' / 'models' / 'task_gen' / 'models'

MODEL_DIR = get_model_dir()


# ============================================================================
# PIPELINE PARAMETERS
# ============================================================================
# Requirement detection
REQUIREMENT_THRESHOLD = float(os.getenv("REQ_THRESHOLD", "0.5"))  # 0.0-1.0

# Task limits
MAX_TASKS_DEFAULT = int(os.getenv("MAX_TASKS", "50"))

# Post-processing
ENABLE_DEDUPLICATION = os.getenv("ENABLE_DEDUP", "true").lower() == "true"
ENABLE_QUALITY_FILTER = os.getenv("ENABLE_QUALITY_FILTER", "true").lower() == "true"
DEDUPE_SIMILARITY_THRESHOLD = float(os.getenv("DEDUPE_THRESHOLD", "0.85"))

# Complex task handling
ENABLE_TASK_SPLITTING = os.getenv("ENABLE_SPLIT", "false").lower() == "true"
ENABLE_TASK_MERGING = os.getenv("ENABLE_MERGE", "false").lower() == "true"


# ============================================================================
# LOGGING
# ============================================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")  # DEBUG, INFO, WARNING, ERROR


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def get_pipeline_config() -> dict:
    """Get current pipeline configuration as dict"""
    return {
        "generator_mode": GENERATOR_MODE,
        "llm_provider": LLM_PROVIDER if GENERATOR_MODE == "llm" else None,
        "llm_model": LLM_MODEL if GENERATOR_MODE == "llm" else None,
        "requirement_threshold": REQUIREMENT_THRESHOLD,
        "max_tasks_default": MAX_TASKS_DEFAULT,
        "enable_deduplication": ENABLE_DEDUPLICATION,
        "enable_quality_filter": ENABLE_QUALITY_FILTER,
        "enable_task_splitting": ENABLE_TASK_SPLITTING,
        "enable_task_merging": ENABLE_TASK_MERGING,
        "log_level": LOG_LEVEL
    }


def print_config():
    """Print current configuration"""
    config = get_pipeline_config()
    print("=" * 60)
    print("TASK GENERATION CONFIGURATION")
    print("=" * 60)
    for key, value in config.items():
        print(f"  {key:30} = {value}")
    print("=" * 60)


# ============================================================================
# QUICK MODE SWITCHERS
# ============================================================================
def use_template_mode():
    """Quick switch to template mode"""
    global GENERATOR_MODE
    GENERATOR_MODE = "template"
    print("✓ Switched to TEMPLATE mode (fast, free, rule-based)")


def use_llm_mode(provider: str = "openai", model: Optional[str] = None):
    """Quick switch to LLM mode"""
    global GENERATOR_MODE, LLM_PROVIDER, LLM_MODEL
    GENERATOR_MODE = "llm"
    LLM_PROVIDER = provider
    if model:
        LLM_MODEL = model
    print(f"✓ Switched to LLM mode (provider={provider}, model={model or 'auto'})")
    print(f"  Make sure {provider.upper()}_API_KEY is set!")
