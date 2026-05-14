"""
Stage 2 — Scenario Generator
============================

Given a :class:`ParsedRequirement`, produce a *diverse* list of
:class:`Scenario` objects covering:

* happy path
* negative paths (one per constraint violated)
* boundary cases (driven by numeric constraints)
* security cases (when ``security`` NFR present)
* permission / role cases
* performance cases (when ``performance`` NFR present)
* integration cases (when integration verbs detected)
* edge cases (carried over from Stage 1)

Scenarios are intentionally *not* test cases yet — they describe the
*behaviour* in Given / When / Then form so a human (or the next stage)
can convert them into executable steps.
"""
from __future__ import annotations

import re
from typing import List

from .schemas import ParsedRequirement, Scenario, ScenarioCategory


_GENERIC_NEG_PHRASES = [
    "missing required field",
    "field exceeds maximum length",
    "field below minimum length",
    "invalid format",
    "duplicate submission",
]


def _humanise(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip()).rstrip(".,;: ")


class ScenarioGenerator:
    """Stage 2: ParsedRequirement → List[Scenario]."""

    def __init__(self, max_scenarios: int = 8) -> None:
        self.max_scenarios = max_scenarios

    # ── public ─────────────────────────────────────────────────────────
    def generate(self, p: ParsedRequirement) -> List[Scenario]:
        scenarios: List[Scenario] = []

        if not p.intent and not p.actor:
            return [self._catchall(p)]

        scenarios.append(self._happy_path(p))

        for ec in p.edge_cases:
            scenarios.append(self._edge_case(p, ec))

        for cs in p.constraints:
            scenarios.append(self._negative_from_constraint(p, cs))

        # Always include a generic negative + invalid-input edge so even
        # bare requirements get at least 3 diverse scenarios.
        if not any(s.category == ScenarioCategory.NEGATIVE for s in scenarios):
            scenarios.append(self._generic_negative(p))
        scenarios.append(self._invalid_input_edge(p))

        if "security" in p.nfr_tags:
            scenarios += self._security_set(p)
        if "permission" in p.nfr_tags:
            scenarios += self._permission_set(p)
        if "performance" in p.nfr_tags:
            scenarios.append(self._performance(p))

        # Boundary cases driven by numeric constraints
        scenarios += self._boundary_cases(p)

        scenarios = self._dedup(scenarios)[: self.max_scenarios]
        return scenarios

    # ── builders ───────────────────────────────────────────────────────
    @staticmethod
    def _happy_path(p: ParsedRequirement) -> Scenario:
        ent = p.entities[0] if p.entities else "the resource"
        return Scenario(
            title=f"{p.actor.title()} successfully {p.intent} {ent}",
            category=ScenarioCategory.HAPPY_PATH,
            given=f"{p.actor} is authenticated and has valid input data",
            when=f"{p.actor} performs {p.intent} on {ent}",
            then=f"the system completes the action and returns a success response",
            risk="baseline behaviour must work",
            tags=["smoke", "P1"],
        )

    @staticmethod
    def _edge_case(p: ParsedRequirement, ec: str) -> Scenario:
        ec = _humanise(ec)
        return Scenario(
            title=f"Edge case: {ec}",
            category=ScenarioCategory.EDGE_CASE,
            given=f"{p.actor} initiates {p.intent}",
            when=ec,
            then="the system handles the situation gracefully without data loss",
            risk=f"prevent regression of '{ec}'",
            tags=["edge", "P2"],
        )

    @staticmethod
    def _negative_from_constraint(p: ParsedRequirement, cs: str) -> Scenario:
        cs = _humanise(cs)
        return Scenario(
            title=f"Negative: violate constraint — {cs[:60]}",
            category=ScenarioCategory.NEGATIVE,
            given=f"{p.actor} prepares an action that violates: {cs}",
            when=f"{p.actor} submits the violating request",
            then="the system rejects the request with a precise error message",
            risk="constraint enforcement",
            tags=["negative", "P1"],
        )

    @staticmethod
    def _generic_negative(p: ParsedRequirement) -> Scenario:
        ent = p.entities[0] if p.entities else "the resource"
        return Scenario(
            title=f"Negative: invalid payload to {p.intent}",
            category=ScenarioCategory.NEGATIVE,
            given=f"{p.actor} is authenticated",
            when=f"{p.actor} submits an invalid payload to {p.intent} {ent}",
            then="the system rejects with HTTP 4xx and a descriptive message",
            risk="input validation",
            tags=["negative", "P1"],
        )

    @staticmethod
    def _invalid_input_edge(p: ParsedRequirement) -> Scenario:
        return Scenario(
            title=f"Edge case: empty / null input on {p.intent}",
            category=ScenarioCategory.EDGE_CASE,
            given=f"{p.actor} initiates {p.intent}",
            when="all required fields are empty or null",
            then="the system rejects without crashing and surfaces field-level errors",
            risk="null / empty handling",
            tags=["edge", "P2"],
        )

    @staticmethod
    def _security_set(p: ParsedRequirement) -> List[Scenario]:
        ent = p.entities[0] if p.entities else "the resource"
        return [
            Scenario(
                title=f"Reject unauthenticated access to {p.intent}",
                category=ScenarioCategory.SECURITY,
                given="no valid session token is supplied",
                when=f"the request to {p.intent} {ent} is sent",
                then="the server returns 401 Unauthorized without leaking data",
                risk="auth bypass",
                tags=["security", "P1"],
            ),
            Scenario(
                title=f"Sanitise input on {p.intent} (XSS / SQL-i payloads)",
                category=ScenarioCategory.SECURITY,
                given="a payload contains script tags and SQL meta-characters",
                when=f"the payload is sent to the {p.intent} endpoint",
                then="the server stores it sanitised and renders it escaped",
                risk="injection / XSS",
                tags=["security", "P1"],
            ),
        ]

    @staticmethod
    def _permission_set(p: ParsedRequirement) -> List[Scenario]:
        return [Scenario(
            title=f"Deny {p.intent} for users without permission",
            category=ScenarioCategory.PERMISSION,
            given="the requesting account lacks the required role",
            when=f"the account attempts to {p.intent}",
            then="the system returns 403 Forbidden and audits the attempt",
            risk="privilege escalation",
            tags=["rbac", "P1"],
        )]

    @staticmethod
    def _performance(p: ParsedRequirement) -> Scenario:
        # Try to surface any numeric threshold seen in constraints
        threshold = ""
        for c in p.constraints:
            m = re.search(r"\d+\s?(?:%|ms|s|seconds?|giây|users?|requests?)", c, re.I)
            if m:
                threshold = m.group(0)
                break
        target = threshold or "documented SLA"
        return Scenario(
            title=f"{p.intent.title()} meets performance target ({target})",
            category=ScenarioCategory.PERFORMANCE,
            given="the system is at the documented load",
            when=f"{p.intent} is invoked",
            then=f"the response completes within {target}",
            risk="SLA / scalability",
            tags=["performance", "P2"],
        )

    @staticmethod
    def _boundary_cases(p: ParsedRequirement) -> List[Scenario]:
        out: List[Scenario] = []
        for c in p.constraints:
            m = re.search(r"(\d+)\s?(%|ms|s|seconds?|giây|users?|requests?|MB|GB)",
                          c, re.I)
            if not m:
                continue
            n = int(m.group(1))
            unit = m.group(2)
            for delta, name in [(0, "at limit"), (-1, "just below limit"),
                                (1, "just above limit")]:
                val = max(0, n + delta)
                out.append(Scenario(
                    title=f"Boundary {name}: {val}{unit}",
                    category=ScenarioCategory.BOUNDARY,
                    given=f"input prepared with value {val}{unit}",
                    when=f"{p.actor} executes {p.intent}",
                    then=("the request is accepted" if delta <= 0
                          else "the request is rejected with a clear message"),
                    risk="off-by-one / boundary handling",
                    tags=["boundary", "P2"],
                ))
        return out

    @staticmethod
    def _catchall(p: ParsedRequirement) -> Scenario:
        return Scenario(
            title=f"Verify behaviour: {p.raw[:70]}",
            category=ScenarioCategory.HAPPY_PATH,
            given="system is in default state",
            when="the requirement is exercised",
            then="the documented behaviour is observed",
            risk="vague requirement — manual review required",
            tags=["P3"],
        )

    @staticmethod
    def _dedup(items: List[Scenario]) -> List[Scenario]:
        seen, out = set(), []
        for s in items:
            key = (s.category.value, s.title.lower())
            if key in seen:
                continue
            seen.add(key)
            out.append(s)
        return out
