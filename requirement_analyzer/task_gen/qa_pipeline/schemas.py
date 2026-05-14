"""Typed schemas for the QA pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional


class ScenarioCategory(str, Enum):
    HAPPY_PATH    = "happy_path"
    NEGATIVE      = "negative"
    BOUNDARY      = "boundary"
    SECURITY      = "security"
    PERMISSION    = "permission"
    PERFORMANCE   = "performance"
    INTEGRATION   = "integration"
    EDGE_CASE     = "edge_case"
    DATA_INTEGRITY = "data_integrity"


class Complexity(str, Enum):
    LOW    = "low"
    MEDIUM = "medium"
    HIGH   = "high"


@dataclass
class ParsedRequirement:
    """Stage 1 output — structured understanding of one requirement."""
    raw: str
    actor: str = ""
    intent: str = ""
    entities: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    edge_cases: List[str] = field(default_factory=list)
    domain: str = "General"
    complexity: Complexity = Complexity.MEDIUM
    nfr_tags: List[str] = field(default_factory=list)   # security/perf/...
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["complexity"] = self.complexity.value
        return d


@dataclass
class Scenario:
    """Stage 2 output — a single test idea (not yet a test case)."""
    title: str
    category: ScenarioCategory
    given: str = ""
    when: str = ""
    then: str = ""
    risk: str = ""           # short note on what's being tested
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["category"] = self.category.value
        return d


@dataclass
class TestStep:
    action: str
    expected: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TestCase:
    """Stage 3 output — fully-built executable test case."""
    test_id: str
    title: str
    category: ScenarioCategory
    priority: str = "Medium"
    preconditions: List[str] = field(default_factory=list)
    steps: List[TestStep] = field(default_factory=list)
    test_data: Dict[str, Any] = field(default_factory=dict)
    expected_result: str = ""
    postconditions: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    estimated_minutes: int = 5
    requirement_ref: str = ""
    given: str = ""
    when: str = ""
    then: str = ""
    quality_score: float = 0.0   # set by Enhancer

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["category"] = self.category.value
        d["steps"] = [s.to_dict() if hasattr(s, "to_dict") else s
                      for s in self.steps]
        return d


@dataclass
class PipelineOutput:
    parsed: List[ParsedRequirement] = field(default_factory=list)
    scenarios: List[Scenario] = field(default_factory=list)
    test_cases: List[TestCase] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "parsed":     [p.to_dict() for p in self.parsed],
            "scenarios":  [s.to_dict() for s in self.scenarios],
            "test_cases": [tc.to_dict() for tc in self.test_cases],
            "stats":      self.stats,
        }
