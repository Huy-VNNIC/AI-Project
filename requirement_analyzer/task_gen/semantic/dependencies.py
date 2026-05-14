"""
DependencyEngine
================

Reasons about *implicit* dependencies between stories from their IR.

A "pay" story logically requires authentication and an invoice/order;
a "discharge" story requires an "admit"; a "diagnose" story requires an
existing patient record.  Encoding these as data lets the sprint
planner order stories correctly without hand-written if-trees.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Set

from .ir import StoryIR


# Intent → set of intents that should be implemented before it.
INTENT_DEPENDENCIES: Dict[str, Set[str]] = {
    "login":      {"register"},
    "logout":     {"login"},
    "authenticate": {"register"},

    "book":       {"login"},
    "reserve":    {"login"},
    "schedule":   {"login"},

    "create":     {"login"},
    "update":     {"login", "create"},
    "delete":     {"login"},
    "view":       {"login"},
    "list":       {"login"},
    "search":     {"login"},
    "filter":     {"search"},

    "pay":        {"login", "invoice"},
    "refund":     {"pay"},
    "invoice":    {"login"},

    "manage":     {"login"},
    "approve":    {"login"},
    "assign":     {"login"},
    "track":      {"login"},

    "diagnose":   {"login"},
    "prescribe":  {"diagnose"},
    "admit":      {"login"},
    "discharge":  {"admit"},
    "operate":    {"admit"},

    "report":     {"login"},
    "export":     {"login"},
    "import":     {"login"},
    "upload":     {"login"},
    "download":   {"login"},

    "notify":     {"login"},
    "send_email": set(),
    "send_sms":   set(),

    "encrypt":    set(),
    "audit":      set(),
    "backup":     set(),
}

# Entity dependencies: entity X often presupposes entity Y exists.
ENTITY_DEPENDENCIES: Dict[str, Set[str]] = {
    "appointment":     {"patient", "doctor"},
    "prescription":    {"medical_record"},
    "medical_record":  {"patient"},
    "invoice":         {"order"},
    "hospital_bill":   {"patient"},
    "surgery_schedule":{"patient", "doctor", "operating_room"},
    "bed":             {"patient"},
}


class DependencyEngine:
    """Compute dependencies between stories represented as IRs."""

    def dependencies_for(self, ir: StoryIR) -> Set[str]:
        """Return canonical intents the given IR transitively depends on."""
        deps: Set[str] = set()
        if ir.intent:
            deps.update(INTENT_DEPENDENCIES.get(ir.intent, set()))
        if ir.entity:
            entity_deps = ENTITY_DEPENDENCIES.get(ir.entity, set())
            # Map dependent entities to "create <entity>" intents conceptually
            for ent in entity_deps:
                deps.add(f"entity:{ent}")
        return deps

    def order(self, irs: List[StoryIR]) -> List[StoryIR]:
        """Topologically sort IRs by dependency order.

        Stories whose dependencies are not present in the input set are
        treated as foundation work and surfaced first.
        """
        intents_present = {ir.intent for ir in irs if ir.intent}
        # Compute "depth" — max chain length to a foundation intent.
        memo: Dict[str, int] = {}

        def depth(intent: str, seen: Set[str]) -> int:
            if intent in memo:
                return memo[intent]
            if intent in seen:
                return 0  # cycle guard
            seen = seen | {intent}
            deps = INTENT_DEPENDENCIES.get(intent, set()) & intents_present
            d = 0 if not deps else 1 + max(depth(d, seen) for d in deps)
            memo[intent] = d
            return d

        return sorted(
            irs,
            key=lambda ir: (depth(ir.intent or "unknown", set()),
                            ir.intent or ""),
        )
