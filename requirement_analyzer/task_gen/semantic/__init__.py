"""
Semantic Understanding Engine
=============================

Pluggable layer that converts raw requirement text into a structured
*Intermediate Representation* (``StoryIR``) and uses that IR for every
downstream generation step:

    text  →  Parser  →  StoryIR  →  StoryGen / ACGen / DepGraph / Planner

The whole engine is rule-based at the bootstrap level (fast, deterministic,
no model dependency), but every component is designed so that the rule
layer can be transparently *augmented* — not replaced — by an embedding
or LLM model later.  See ``parser.SemanticParser`` for the plug-in seam.

Public API:
    from requirement_analyzer.task_gen.semantic import (
        StoryIR, SemanticParser, StoryGenerator,
        ACGenerator, DependencyEngine, FeedbackStore,
    )
"""
from .ir import StoryIR, RequirementType
from .parser import SemanticParser
from .generator import StoryGenerator
from .ac_engine import ACGenerator
from .dependencies import DependencyEngine
from .dependency_ai import DependencyAI, StoryNode, Edge
from .feedback import FeedbackStore
from .embedding import (
    SentenceTransformerBackend,
    KeywordOverlapBackend,
    auto_backend,
)
from .sp_estimator import (
    HeuristicEstimator,
    SklearnEstimator,
    train_from_feedback,
    load_estimator,
)
from . import graph_viz

__all__ = [
    "StoryIR",
    "RequirementType",
    "SemanticParser",
    "StoryGenerator",
    "ACGenerator",
    "DependencyEngine",
    "DependencyAI",
    "StoryNode",
    "Edge",
    "FeedbackStore",
    "SentenceTransformerBackend",
    "KeywordOverlapBackend",
    "auto_backend",
    "HeuristicEstimator",
    "SklearnEstimator",
    "train_from_feedback",
    "load_estimator",
    "graph_viz",
]
