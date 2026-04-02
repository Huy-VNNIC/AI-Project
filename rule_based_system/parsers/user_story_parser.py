"""
User story parser module.
Parser cho User Story format: As a [actor], I want [action] so that [expected]
"""

import re
from ..models.canonical import CanonicalRequirement


# Pattern chính — bắt đủ các biến thể phổ biến
USER_STORY_PATTERNS = [
    # Chuẩn: As a X, I want Y so that Z
    re.compile(
        r"As an?\s+(?P<actor>[^,]+),\s+"
        r"I want(?:\s+to)?\s+(?P<action>.+?)"
        r"(?:\s+so that\s+(?P<expected>.+?))?[\.\n]",
        re.IGNORECASE | re.DOTALL
    ),
    # Không có "so that"
    re.compile(
        r"As an?\s+(?P<actor>[^,\n]+),?\s+"
        r"I(?:'d like to| want to| need to)\s+(?P<action>[^\n\.]+)",
        re.IGNORECASE
    ),
    # "I want" đứng đầu (informal)
    re.compile(
        r"I want(?:\s+to)?\s+(?P<action>[^\n\.]+)",
        re.IGNORECASE
    ),
]


def parse_user_story(text: str) -> list[CanonicalRequirement]:
    """
    Parse text chứa User Stories → list CanonicalRequirement.
    Một file có thể chứa nhiều user stories.
    """
    results = []
    seen_spans = set()  # tránh parse trùng

    for pattern in USER_STORY_PATTERNS:
        for match in pattern.finditer(text):
            span = match.span()
            # Bỏ qua nếu đã parse vùng này
            if any(abs(span[0] - s) < 10 for s in seen_spans):
                continue
            seen_spans.add(span[0])

            actor    = (match.groupdict().get("actor") or "user").strip()
            action   = (match.groupdict().get("action") or "").strip()
            expected = (match.groupdict().get("expected") or "").strip()

            # Tách action thành verb + objects
            action_verb, action_objects = _split_action(action)

            req = CanonicalRequirement(
                actor=_normalize_actor(actor),
                action=action_verb,
                objects=action_objects,
                conditions=[],
                expected=expected or f"System fulfils: {action}",
                req_type=_classify(action + " " + expected),
                source_format="user_story",
                raw_text=match.group(0).strip(),
            )

            if req.is_valid():
                results.append(req)

    return results


def _split_action(action_text: str) -> tuple[str, list[str]]:
    """
    Tách "view product details" → ("view", ["product detail"])
    Tách "enter email and password" → ("enter", ["email", "password"])
    """
    tokens = action_text.lower().split()
    if not tokens:
        return "", []

    verb = tokens[0]
    rest = tokens[1:]

    # Tách objects bởi "and", "or", ","
    objects_text = " ".join(rest)
    objects = re.split(r"\s+and\s+|\s+or\s+|,\s*", objects_text)
    objects = [o.strip() for o in objects if o.strip()]

    return verb, objects


def _normalize_actor(actor: str) -> str:
    """Chuẩn hoá tên actor."""
    lower = actor.lower().strip()
    system_aliases = {"system", "application", "app", "platform", "service", "api"}
    if lower in system_aliases:
        return "system"
    return lower


def _classify(text: str) -> str:
    lower = text.lower()
    if any(w in lower for w in ["password", "login", "auth", "secure", "token", "permission"]):
        return "security"
    if any(w in lower for w in ["fast", "quick", "load", "performance", "response time"]):
        return "performance"
    return "functional"
