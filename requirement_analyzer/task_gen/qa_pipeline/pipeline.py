"""
QA Pipeline orchestrator.

Wires the four stages together and exposes a single :class:`QAPipeline`
entry point.  The pipeline accepts either a single requirement string
or a list of requirements (one per line) and returns a fully
populated :class:`PipelineOutput`.
"""
from __future__ import annotations

import re
import time
from typing import Iterable, List

from .builder import TestCaseBuilder
from .enhancer import QualityEnhancer
from .parser import RequirementParser
from .scenarios import ScenarioGenerator
from .schemas import (
    ParsedRequirement, PipelineOutput, Scenario, TestCase,
)


_BULLET = re.compile(r"^\s*(?:\d+[\.\)]\s+|[-*•+]\s+)+", re.UNICODE)


def _split_requirements(text: str) -> List[str]:
    """Split a text blob into one requirement per non-empty line."""
    out: List[str] = []
    for ln in (text or "").splitlines():
        ln = _BULLET.sub("", ln).strip()
        if not ln:
            continue
        if len(ln.split()) < 3:
            continue
        # Skip headings
        if ln.startswith("#") or ln.endswith(":"):
            continue
        out.append(ln)
    return out


# ─────────────────────────────────────────────────────────────────────────
class QAPipeline:
    """Orchestrates the four stages.  All components are pluggable."""

    def __init__(
        self,
        parser: RequirementParser | None = None,
        scenario_gen: ScenarioGenerator | None = None,
        builder: TestCaseBuilder | None = None,
        enhancer: QualityEnhancer | None = None,
        max_scenarios_per_req: int = 8,
    ) -> None:
        self.parser = parser or RequirementParser()
        self.scenario_gen = scenario_gen or ScenarioGenerator(
            max_scenarios=max_scenarios_per_req
        )
        self.builder = builder or TestCaseBuilder()
        self.enhancer = enhancer or QualityEnhancer()

    # ── public API ─────────────────────────────────────────────────────
    def run(self, text: str) -> PipelineOutput:
        return self.run_many(_split_requirements(text))

    def run_many(self, requirements: Iterable[str]) -> PipelineOutput:
        t0 = time.perf_counter()
        parsed_all: List[ParsedRequirement] = []
        scenarios_all: List[Scenario] = []
        cases_all: List[TestCase] = []
        scenario_to_req: List[int] = []  # index back to parsed_all
        case_counter = 0

        for req_idx, raw in enumerate(requirements, 1):
            parsed = self.parser.parse(raw)
            parsed_all.append(parsed)

            scenarios = self.scenario_gen.generate(parsed)
            req_ref = f"REQ-{req_idx:03d}"
            for sc in scenarios:
                scenarios_all.append(sc)
                scenario_to_req.append(req_idx - 1)
                case_counter += 1
                tc = self.builder.build(
                    sc, parsed,
                    test_id=f"TC-{req_idx:03d}-{case_counter:04d}",
                    requirement_ref=req_ref,
                )
                cases_all.append(tc)

        cases_all = self.enhancer.enhance(cases_all)

        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        out = PipelineOutput(
            parsed=parsed_all,
            scenarios=scenarios_all,
            test_cases=cases_all,
            stats=self._stats(parsed_all, scenarios_all, cases_all, elapsed_ms),
        )
        return out

    # ── stats ──────────────────────────────────────────────────────────
    @staticmethod
    def _stats(parsed, scenarios, cases, elapsed_ms):
        from collections import Counter
        cat = Counter(s.category.value for s in scenarios)
        prio = Counter(c.priority for c in cases)
        avg_q = (sum(c.quality_score for c in cases) / len(cases)) if cases else 0
        avg_conf = (sum(p.confidence for p in parsed) / len(parsed)) if parsed else 0
        return {
            "requirements":       len(parsed),
            "scenarios":          len(scenarios),
            "test_cases":         len(cases),
            "avg_parser_confidence": round(avg_conf, 3),
            "avg_quality_score":  round(avg_q, 3),
            "by_category":        dict(cat),
            "by_priority":        dict(prio),
            "elapsed_ms":         elapsed_ms,
        }
