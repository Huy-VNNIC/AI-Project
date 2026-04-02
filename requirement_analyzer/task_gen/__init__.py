"""
Task Generation Module
AI-powered task generation from requirement documents
"""

# Legacy imports - kept for backwards compatibility
# Import these only when needed to avoid spacy compatibility issues
try:
    from .schemas import (
        GeneratedTask,
        TaskSource,
        TaskGenerationRequest,
        TaskGenerationResponse,
        TaskFeedback
    )
except ImportError as e:
    import warnings
    warnings.warn(f"Could not import legacy schemas: {e}")

# V2 Pipeline imports - these don't depend on spacy
try:
    from .schemas_v2 import (
        Requirement,
        RequirementType,
        UserStory,
        AcceptanceCriterion
    )
except ImportError:
    pass

# These imports need spacy - only import on demand
def get_pipeline():
    from .pipeline import TaskGenerationPipeline, get_pipeline as _get_pipeline
    return _get_pipeline()

def get_segmenter():
    from .segmenter import get_segmenter as _get_segmenter
    return _get_segmenter()

def get_detector():
    from .req_detector import get_detector as _get_detector
    return _get_detector()

def get_enrichment_pipeline():
    from .enrichers import get_enrichment_pipeline as _get_enrich
    return _get_enrich()

def get_generator():
    from .generator_templates import get_generator as _get_gen
    return _get_gen()

def get_llm_generator():
    from .generator_llm import get_llm_generator as _get_llm
    return _get_llm()

def get_postprocessor():
    from .postprocess import get_postprocessor as _get_post
    return _get_post()
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
