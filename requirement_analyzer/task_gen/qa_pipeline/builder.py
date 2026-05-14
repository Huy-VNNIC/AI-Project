"""
Stage 3 — Test Case Builder
===========================

Convert a :class:`Scenario` into a fully-detailed :class:`TestCase`
with concrete preconditions, steps, expected results, test data and
priority.

Steps are generated from a small library of *action templates* keyed
by category — ensuring negative tests probe the failure path,
boundary tests sweep the limits, etc.  Every step has both an action
and an expected result so the case is directly executable.
"""
from __future__ import annotations

from typing import Dict, List

from .schemas import (
    ParsedRequirement, Scenario, ScenarioCategory, TestCase, TestStep,
)


_PRIORITY_BY_CATEGORY: Dict[ScenarioCategory, str] = {
    ScenarioCategory.HAPPY_PATH:    "High",
    ScenarioCategory.NEGATIVE:      "High",
    ScenarioCategory.SECURITY:      "Critical",
    ScenarioCategory.PERMISSION:    "High",
    ScenarioCategory.BOUNDARY:      "Medium",
    ScenarioCategory.EDGE_CASE:     "Medium",
    ScenarioCategory.PERFORMANCE:   "Medium",
    ScenarioCategory.INTEGRATION:   "Medium",
    ScenarioCategory.DATA_INTEGRITY: "High",
}

_EFFORT_MIN: Dict[ScenarioCategory, int] = {
    ScenarioCategory.HAPPY_PATH:    5,
    ScenarioCategory.NEGATIVE:      6,
    ScenarioCategory.SECURITY:     12,
    ScenarioCategory.PERMISSION:    8,
    ScenarioCategory.BOUNDARY:      6,
    ScenarioCategory.EDGE_CASE:     8,
    ScenarioCategory.PERFORMANCE:  20,
    ScenarioCategory.INTEGRATION:  15,
    ScenarioCategory.DATA_INTEGRITY: 10,
}


# ─────────────────────────────────────────────────────────────────────────
class TestCaseBuilder:
    """Stage 3: Scenario + ParsedRequirement → TestCase."""

    def build(
        self,
        scenario: Scenario,
        parsed: ParsedRequirement,
        test_id: str,
        requirement_ref: str = "",
    ) -> TestCase:
        steps = self._steps_for(scenario, parsed)
        tc = TestCase(
            test_id=test_id,
            title=scenario.title,
            category=scenario.category,
            priority=_PRIORITY_BY_CATEGORY.get(scenario.category, "Medium"),
            preconditions=self._preconditions(scenario, parsed),
            steps=steps,
            test_data=self._test_data(scenario, parsed),
            expected_result=scenario.then or "behaviour observed",
            postconditions=self._postconditions(scenario, parsed),
            tags=list(scenario.tags) + [parsed.domain],
            estimated_minutes=_EFFORT_MIN.get(scenario.category, 5),
            requirement_ref=requirement_ref,
            given=scenario.given,
            when=scenario.when,
            then=scenario.then,
        )
        return tc

    # ── helpers ────────────────────────────────────────────────────────
    @staticmethod
    def _preconditions(s: Scenario, p: ParsedRequirement) -> List[str]:
        pre: List[str] = []
        if s.category == ScenarioCategory.SECURITY:
            pre.append("Test environment isolated from production")
        if s.category == ScenarioCategory.PERMISSION:
            pre.append("A user account WITHOUT the required role is available")
        if s.category in (ScenarioCategory.HAPPY_PATH,
                           ScenarioCategory.NEGATIVE,
                           ScenarioCategory.BOUNDARY):
            pre.append(f"{p.actor.title()} has an authenticated session")
            if p.entities:
                pre.append(f"{p.entities[0].title()} fixture exists in the database")
        if s.category == ScenarioCategory.PERFORMANCE:
            pre.append("Load generation tool is configured to documented SLA")
        if s.category == ScenarioCategory.INTEGRATION:
            pre.append("All downstream services are reachable")
        if not pre:
            pre.append("System is in its default reset state")
        return pre

    @staticmethod
    def _postconditions(s: Scenario, p: ParsedRequirement) -> List[str]:
        if s.category == ScenarioCategory.HAPPY_PATH:
            return [f"{p.entities[0] if p.entities else 'record'} is persisted",
                    "Audit log contains the action"]
        if s.category in (ScenarioCategory.NEGATIVE,
                           ScenarioCategory.SECURITY,
                           ScenarioCategory.PERMISSION):
            return ["No partial data is written",
                    "Failure is logged with correlation id"]
        return ["System returns to a consistent state"]

    @staticmethod
    def _test_data(s: Scenario, p: ParsedRequirement) -> Dict[str, str]:
        ent = p.entities[0] if p.entities else "resource"
        if s.category == ScenarioCategory.HAPPY_PATH:
            return {"input": f"valid {ent} payload"}
        if s.category == ScenarioCategory.NEGATIVE:
            return {"input": f"payload missing required field for {ent}"}
        if s.category == ScenarioCategory.SECURITY:
            return {"payload": "<script>alert(1)</script>"
                    if "xss" in s.title.lower() else "no Authorization header"}
        if s.category == ScenarioCategory.BOUNDARY:
            return {"value": s.title.split(":", 1)[-1].strip()}
        if s.category == ScenarioCategory.PERFORMANCE:
            return {"profile": "k6 ramp-up to documented load"}
        return {}

    @staticmethod
    def _steps_for(s: Scenario, p: ParsedRequirement) -> List[TestStep]:
        ent = p.entities[0] if p.entities else "the resource"
        intent = p.intent or "perform action"
        steps: List[TestStep] = []

        if s.category == ScenarioCategory.HAPPY_PATH:
            steps = [
                TestStep(action=f"Authenticate as {p.actor}",
                         expected="Session is established"),
                TestStep(action=f"Submit a valid request to {intent} {ent}",
                         expected="Request is accepted (HTTP 2xx)"),
                TestStep(action="Verify the persisted record",
                         expected="Record matches the submitted payload"),
            ]
        elif s.category == ScenarioCategory.NEGATIVE:
            steps = [
                TestStep(action=f"Authenticate as {p.actor}",
                         expected="Session is established"),
                TestStep(action="Submit an invalid request",
                         expected="HTTP 4xx with a clear error message"),
                TestStep(action="Verify no record was written",
                         expected="Database state is unchanged"),
            ]
        elif s.category == ScenarioCategory.SECURITY:
            if "unauthenticated" in s.title.lower():
                steps = [
                    TestStep(action="Send the request without an Authorization header",
                             expected="HTTP 401 returned, body free of stack traces"),
                    TestStep(action="Inspect server logs",
                             expected="Auth failure logged with timestamp + correlation id"),
                ]
            else:
                steps = [
                    TestStep(action="Send a malicious payload",
                             expected="Server stores it sanitised"),
                    TestStep(action=f"Render the persisted {ent}",
                             expected="Output is HTML-escaped — no script execution"),
                ]
        elif s.category == ScenarioCategory.PERMISSION:
            steps = [
                TestStep(action=f"Authenticate as a user without the required role",
                         expected="Session is established but role is missing"),
                TestStep(action=f"Attempt to {intent} {ent}",
                         expected="HTTP 403 returned"),
                TestStep(action="Inspect audit log",
                         expected="Forbidden attempt is recorded"),
            ]
        elif s.category == ScenarioCategory.BOUNDARY:
            steps = [
                TestStep(action=s.given,
                         expected="Input prepared"),
                TestStep(action=s.when,
                         expected=s.then),
            ]
        elif s.category == ScenarioCategory.PERFORMANCE:
            steps = [
                TestStep(action="Warm up the system for 1 minute",
                         expected="Caches primed, baseline established"),
                TestStep(action=f"Drive load against the {intent} endpoint",
                         expected=s.then),
                TestStep(action="Collect p95 / p99 latency and error rate",
                         expected="Metrics within SLA"),
            ]
        elif s.category == ScenarioCategory.EDGE_CASE:
            steps = [
                TestStep(action=f"Reproduce condition: {s.when}",
                         expected="Condition is in place"),
                TestStep(action=f"Exercise {intent}",
                         expected=s.then),
            ]
        else:
            steps = [TestStep(action=s.when or s.title,
                              expected=s.then or "documented behaviour observed")]

        return steps
