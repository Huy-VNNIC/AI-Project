"""
FeedbackStore
=============

Closed-loop learning hook.  Captures every (raw text, IR, generated story,
edited story) tuple as a JSONL training record.  Two simple online updates
make the parser smarter immediately, without retraining a model:

1. **Lexicon learning** — when a user's edited story uses a verb/noun
   not in the parser's lexicon but the original IR's intent/entity is
   present in the edit, the new surface form is added as an alias.
2. **Failure logging** — IRs with ``confidence < 0.4`` for ``intent``
   are flagged for human review and shown in the metrics summary.

The store is intentionally backend-agnostic: the default is an
append-only JSONL file under ``runs/feedback.jsonl``, but any object
exposing ``append(record: dict)`` works (e.g. SQLite, Postgres, S3).
"""
from __future__ import annotations

import json
import os
import threading
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .ir import StoryIR
from .parser import ENTITY_LEXICON, INTENT_LEXICON


_DEFAULT_PATH = Path(os.environ.get(
    "RA_FEEDBACK_PATH",
    Path(__file__).resolve().parents[3] / "runs" / "feedback.jsonl",
))


class FeedbackStore:
    """Append-only feedback log + simple online learner."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = Path(path) if path else _DEFAULT_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    # ── Capture ─────────────────────────────────────────────────────────
    def record(
        self,
        raw_text: str,
        ir: StoryIR,
        generated_story: str,
        edited_story: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        rec = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "text": raw_text,
            "ir": ir.to_dict(),
            "generated_story": generated_story,
            "edited_story": edited_story,
            "meta": meta or {},
        }
        with self._lock, self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

        # Online learning hook — only triggers when the user actually
        # edited the auto-generated story.
        if edited_story and edited_story.strip() != generated_story.strip():
            self._maybe_learn_alias(ir, edited_story)

    # ── Online learning ─────────────────────────────────────────────────
    def _maybe_learn_alias(self, ir: StoryIR, edited_story: str) -> None:
        """Cheap heuristic: if the edited story contains a phrase that
        the parser failed to recognize but maps cleanly to ``ir.intent``
        or ``ir.entity``, register it in the in-memory lexicon so future
        runs catch it.
        """
        edited = edited_story.lower()
        if ir.intent and ir.intent != "unknown":
            existing_phrases = {kw for kw, val in INTENT_LEXICON if val == ir.intent}
            for token in _candidate_tokens(edited):
                if token in existing_phrases:
                    continue
                if _looks_like_verb_phrase(token):
                    INTENT_LEXICON.append((token, ir.intent))
                    break
        if ir.entity:
            existing = {kw for kw, val in ENTITY_LEXICON if val == ir.entity}
            for token in _candidate_tokens(edited):
                if token in existing:
                    continue
                if _looks_like_noun_phrase(token):
                    ENTITY_LEXICON.append((token, ir.entity))
                    break

    # ── Metrics summary ─────────────────────────────────────────────────
    def metrics(self) -> Dict[str, Any]:
        """Compute simple aggregate metrics over the feedback log."""
        if not self.path.exists():
            return {"records": 0}
        records = list(self._iter_records())
        if not records:
            return {"records": 0}
        total = len(records)
        edited = sum(1 for r in records if r.get("edited_story"))
        intents = [r["ir"].get("intent") or "unknown" for r in records]
        unknown = sum(1 for i in intents if i == "unknown")
        avg_conf = sum(
            float(r["ir"].get("confidence", {}).get("intent", 0.0))
            for r in records
        ) / total
        return {
            "records": total,
            "edited_rate": edited / total,
            "unknown_intent_rate": unknown / total,
            "avg_intent_confidence": round(avg_conf, 3),
            "low_confidence_examples": [
                r["text"] for r in records
                if float(r["ir"].get("confidence", {}).get("intent", 0.0)) < 0.4
            ][:5],
        }

    def _iter_records(self) -> Iterable[Dict[str, Any]]:
        with self.path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue


# ── Helpers ────────────────────────────────────────────────────────────────
def _candidate_tokens(text: str) -> List[str]:
    """Return short multi-word phrases (1–3 words) that could be a new alias."""
    parts = [p.strip() for p in text.replace(",", " ").replace(".", " ").split()]
    candidates: List[str] = []
    for n in (3, 2, 1):
        for i in range(len(parts) - n + 1):
            phrase = " ".join(parts[i:i + n]).strip()
            if 2 <= len(phrase) <= 30:
                candidates.append(phrase)
    return candidates


_VERB_HINTS = {"đăng", "đặt", "tạo", "xem", "cập", "xóa", "thanh",
               "tìm", "lọc", "duyệt", "phê", "phân", "gửi"}
_NOUN_HINTS = {"hồ", "lịch", "phòng", "đơn", "thuốc", "hóa", "tài",
               "vai", "quyền", "email"}


def _looks_like_verb_phrase(token: str) -> bool:
    return any(token.startswith(h) for h in _VERB_HINTS)


def _looks_like_noun_phrase(token: str) -> bool:
    return any(token.startswith(h) for h in _NOUN_HINTS)
