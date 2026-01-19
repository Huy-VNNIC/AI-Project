"""
Task Generation Module
AI-powered task generation from requirement documents
"""

from .schemas import (
    GeneratedTask,
    TaskSource,
    TaskGenerationRequest,
    TaskGenerationResponse,
    TaskFeedback
)

from .pipeline import get_pipeline, TaskGenerationPipeline
from .segmenter import get_segmenter
from .req_detector import get_detector
from .enrichers import get_enrichment_pipeline
from .generator_templates import get_generator
from .generator_llm import get_llm_generator
from .postprocess import get_postprocessor
from .config import (
    GENERATOR_MODE,
    use_template_mode,
    use_llm_mode,
    get_pipeline_config,
    print_config
)

__all__ = [
    'GeneratedTask',
    'TaskSource',
    'TaskGenerationRequest',
    'TaskGenerationResponse',
    'TaskFeedback',
    'get_pipeline',
    'TaskGenerationPipeline',
    'get_segmenter',
    'get_detector',
    'get_enrichment_pipeline',
    'get_generator',
    'get_llm_generator',
    'get_postprocessor',
    'GENERATOR_MODE',
    'use_template_mode',
    'use_llm_mode',
    'get_pipeline_config',
    'print_config'
]

__version__ = '1.0.0'
