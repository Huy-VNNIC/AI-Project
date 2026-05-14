"""
Stage 4 — Quality Enhancer
==========================

Polish the test cases produced by :class:`TestCaseBuilder` so they read
like work from a senior QA, not a template engine:

* removes duplicate step pairs
* trims dangling stop-words and bullet markers
* normalises sentence case (capital first letter, no trailing punct
  inside list items)
* computes a ``quality_score`` per test case based on completeness
* removes near-duplicate test cases across the whole batch
"""
from __future__ import annotations

import re
from typing import List

from .schemas import TestCase, TestStep


_BULLETS  = re.compile(r"^\s*(?:\d+[\.\)]\s+|[-*•+]\s+)+", re.UNICODE)
_TAIL_PUNCT = re.compile(r"[.,;:!?\s]+$")
_DANGLING_STOPS = {"of", "for", "with", "to", "by", "at", "in", "on",
                    "the", "a", "an", "as", "is", "be",
                    "của", "cho", "với", "đến", "vào", "trong", "bằng",
                    "khi", "để", "bởi", "do", "rằng"}


def _clean(text: str) -> str:
    if not text:
        return ""
    s = _BULLETS.sub("", text).strip()
    s = re.sub(r"\s+", " ", s)
    s = _TAIL_PUNCT.sub("", s)
    # strip dangling stop-words from the right
    for _ in range(3):
        toks = s.rsplit(" ", 1)
        if len(toks) == 2 and toks[1].lower() in _DANGLING_STOPS:
            s = toks[0]
        else:
            break
    if s and s[0].islower():
        s = s[0].upper() + s[1:]
    return s


# ─────────────────────────────────────────────────────────────────────────
class QualityEnhancer:
    """Stage 4: List[TestCase] → polished List[TestCase]."""

    def enhance(self, cases: List[TestCase]) -> List[TestCase]:
        cleaned: List[TestCase] = []
        for tc in cases:
            tc.title = _clean(tc.title)
            tc.expected_result = _clean(tc.expected_result)
            tc.preconditions = self._dedup([_clean(p) for p in tc.preconditions])
            tc.postconditions = self._dedup([_clean(p) for p in tc.postconditions])
            tc.steps = self._clean_steps(tc.steps)
            tc.quality_score = self._score(tc)
            cleaned.append(tc)

        return self._dedup_cases(cleaned)

    # ── helpers ────────────────────────────────────────────────────────
    @staticmethod
    def _dedup(seq):
        seen, out = set(), []
        for x in seq:
            if x and x.lower() not in seen:
                seen.add(x.lower())
                out.append(x)
        return out

    @staticmethod
    def _clean_steps(steps: List[TestStep]) -> List[TestStep]:
        seen = set()
        out: List[TestStep] = []
        for st in steps:
            a = _clean(st.action if hasattr(st, "action") else st["action"])
            e = _clean(st.expected if hasattr(st, "expected") else st["expected"])
            if not a:
                continue
            key = (a.lower(), e.lower())
            if key in seen:
                continue
            seen.add(key)
            out.append(TestStep(action=a, expected=e or "Outcome verified"))
        return out

    @staticmethod
    def _score(tc: TestCase) -> float:
        s = 0.0
        if tc.title:                s += 0.15
        if tc.preconditions:        s += 0.10
        if len(tc.steps) >= 2:      s += 0.25
        if all(getattr(st, 'expected', None) or st.get('expected')
               for st in tc.steps):
            s += 0.20
        if tc.expected_result:      s += 0.10
        if tc.test_data:            s += 0.10
        if tc.tags:                 s += 0.05
        if tc.requirement_ref:      s += 0.05
        return round(min(1.0, s), 3)

    @staticmethod
    def _dedup_cases(cases: List[TestCase]) -> List[TestCase]:
        seen, out = set(), []
        for tc in cases:
            key = (tc.category.value, tc.title.lower())
            if key in seen:
                continue
            seen.add(key)
            out.append(tc)
        return out
