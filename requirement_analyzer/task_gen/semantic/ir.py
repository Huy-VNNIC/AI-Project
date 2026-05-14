"""
StoryIR — Intermediate Representation
=====================================

A normalized, language-agnostic view of a single requirement.  Every
downstream module (story generator, AC engine, estimator, planner) reads
this IR instead of raw text, so business rules live in *one* place.

The IR is intentionally over-specified: optional fields default to
``None`` and parsers are free to fill only what they can extract with
high confidence.  Confidence scores per slot make it easy to escalate
to an embedding / LLM fallback when needed.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional


class RequirementType(str, Enum):
    """High-level classification of the requirement."""
    FUNCTIONAL = "Functional"
    NFR = "NFR"            # Performance / Security / Availability / Compliance
    DEVOPS = "DevOps"      # Backup, deployment, CI/CD, monitoring
    TECH = "Tech"          # Tech-stack mandates ("must use React")
    UNKNOWN = "Unknown"


# Canonical intents — short, lowercase, snake_case.  Add new intents as
# the parser learns to detect them.  The story generator and AC engine
# both key off these strings.
CANONICAL_INTENTS = {
    "register", "login", "logout", "authenticate",
    "book", "reserve", "schedule",
    "create", "read", "update", "delete", "list", "search", "filter",
    "view",
    "pay", "refund", "invoice",
    "manage", "approve", "assign", "track",
    "diagnose", "prescribe",  # clinical
    "admit", "discharge",      # inpatient
    "operate",                  # surgical
    "report", "export", "import", "upload", "download",
    "notify", "send_email", "send_sms",
    "encrypt", "audit", "backup",
    "unknown",
}


@dataclass
class StoryIR:
    """Structured meaning of a requirement.

    Slots are filled by ``SemanticParser``.  Anything the parser is unsure
    of stays ``None`` so downstream modules can decide how to fall back.
    """

    # ── Who / What / How ────────────────────────────────────────────────
    actor: Optional[str] = None              # e.g. "Bệnh nhân", "Khách hàng"
    intent: Optional[str] = None             # canonical verb, see CANONICAL_INTENTS
    entity: Optional[str] = None             # canonical noun, e.g. "appointment"
    entities: List[str] = field(default_factory=list)  # secondary nouns
    action_phrase: Optional[str] = None      # cleaned action text for fallback display
    benefit: Optional[str] = None            # the "so that …" clause

    # ── Context ─────────────────────────────────────────────────────────
    channel: Optional[str] = None            # online / mobile / kiosk
    constraints: List[str] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)

    # ── Classification ──────────────────────────────────────────────────
    domain: Optional[str] = None             # Hotel / Clinical / Pharmacy / …
    subdomain: Optional[str] = None          # finer granularity if known
    requirement_type: RequirementType = RequirementType.FUNCTIONAL

    # ── Behavioral signals (drive AC generation + estimation) ───────────
    has_external_api: bool = False
    has_payment: bool = False
    has_notification: bool = False
    has_file_io: bool = False
    is_realtime: bool = False
    is_crud_bundle: bool = False             # "manage X" → full CRUD set
    needs_permission_check: bool = False

    # ── Confidence (per-slot) ───────────────────────────────────────────
    confidence: Dict[str, float] = field(default_factory=dict)

    # ── Provenance ──────────────────────────────────────────────────────
    source_text: str = ""                    # original raw text
    parser_layers: List[str] = field(default_factory=list)
    # ^ e.g. ["rule:actor", "rule:intent", "embedding:entity"]

    # ── Convenience ─────────────────────────────────────────────────────
    def overall_confidence(self) -> float:
        if not self.confidence:
            return 0.0
        return sum(self.confidence.values()) / len(self.confidence)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["requirement_type"] = self.requirement_type.value
        return d
