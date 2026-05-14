"""
QA Pipeline v3 — Production-Grade Test Case Generation
======================================================

Implements the 4-stage architecture requested by senior QA spec:

    Requirement → Parser → Scenario → Builder → Enhancer → Export

Each stage is a pluggable module.  The pipeline runs **offline** by
default (no LLM key required) using:

* spaCy + rule layer  for the Parser stage
* combinatorial rules for the Scenario stage (positive / negative /
  boundary / security / permission / performance / integration)
* template-light Builder (steps generated from action-flow + entities)
* Enhancer (deduplication, dangling-stop-word removal, length normaliser)

A future ``LLMBackend`` can be plugged into any single stage without
disturbing the others — every stage takes typed inputs and returns
typed dataclasses.

Public entry point::

    from requirement_analyzer.task_gen.qa_pipeline import QAPipeline
    out = QAPipeline().run("Patient books appointment with doctor")
"""
from .schemas import (
    ParsedRequirement, Scenario, TestStep, TestCase, PipelineOutput,
)
from .parser import RequirementParser
from .scenarios import ScenarioGenerator
from .builder import TestCaseBuilder
from .enhancer import QualityEnhancer
from .pipeline import QAPipeline

__all__ = [
    "QAPipeline",
    "RequirementParser",
    "ScenarioGenerator",
    "TestCaseBuilder",
    "QualityEnhancer",
    "ParsedRequirement",
    "Scenario",
    "TestStep",
    "TestCase",
    "PipelineOutput",
]
