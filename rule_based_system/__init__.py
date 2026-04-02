"""
Rule-Based Test Case Generator System
======================================

A deterministic NLP + rule-based system for automatic test case generation.
No external AI APIs — completely self-contained.

Usage:
    from rule_based_system.core.pipeline import run_pipeline
    
    result = run_pipeline("requirements.pdf")
    print(f"Generated {result['summary']['total_test_cases']} test cases")
"""

__version__ = "1.0.0"
__author__ = "Huy VNNIC"

from .models.canonical import CanonicalRequirement, TestCase
from .core.pipeline import run_pipeline, run_pipeline_from_text
from .exports.export_handler import export_json, export_csv, export_excel, export_markdown

__all__ = [
    "CanonicalRequirement",
    "TestCase",
    "run_pipeline",
    "run_pipeline_from_text",
    "export_json",
    "export_csv",
    "export_excel",
    "export_markdown",
]
