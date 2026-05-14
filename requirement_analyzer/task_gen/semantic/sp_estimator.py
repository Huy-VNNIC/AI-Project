"""
Story-point estimator
=====================

Trains a regression model to predict story points from a ``StoryIR``,
using the JSONL log produced by :class:`FeedbackStore`.

Each feedback record is expected to carry the *final* SP that the team
actually committed to in ``meta["sp"]``.  Wire this in by passing
``meta={"sp": story.story_points}`` when calling ``FeedbackStore.record``.

Design choices
--------------
* **Sklearn-optional** — we use scikit-learn's ``GradientBoostingRegressor``
  when available, but fall back to a transparent rule-based estimator so
  the pipeline never hard-depends on it.
* **Feature engineering happens in pure Python** — no pandas / numpy in
  the public path, so the trained model is trivially serialisable with
  ``pickle`` and the predictor is a small POPO.
* **Confidence-weighted training** — records with ``confidence.intent < 0.5``
  contribute half-weight, so noisy labels don't dominate.

Usage
-----
::

    from requirement_analyzer.task_gen.semantic.sp_estimator import (
        train_from_feedback, load_estimator,
    )

    estimator = train_from_feedback("runs/feedback.jsonl",
                                    out_path="runs/sp_model.pkl")
    sp = estimator.predict(ir)              # → 5
"""
from __future__ import annotations

import json
import logging
import math
import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .ir import StoryIR

log = logging.getLogger(__name__)

# Fibonacci-ish SP scale used by the team.  Predictions are snapped to
# the nearest valid value.
SP_SCALE: Tuple[int, ...] = (1, 2, 3, 5, 8, 13, 21)

# Boolean IR flags expected at training/inference time.
_FLAGS = (
    "has_external_api",
    "has_payment",
    "has_notification",
    "has_file_io",
    "is_realtime",
    "is_crud_bundle",
    "needs_permission_check",
)


# ── Feature extraction ─────────────────────────────────────────────────────
@dataclass
class FeatureSpec:
    """Frozen feature vocabulary discovered at training time."""

    intents: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)
    flags: Tuple[str, ...] = _FLAGS

    @property
    def dim(self) -> int:
        return (
            len(self.intents)
            + len(self.entities)
            + len(self.domains)
            + len(self.flags)
            + 2  # entities-count, action-phrase-length
        )

    def vectorise(self, ir: StoryIR) -> List[float]:
        v = [0.0] * self.dim
        # one-hot intent
        try:
            v[self.intents.index(ir.intent or "unknown")] = 1.0
        except ValueError:
            pass
        off = len(self.intents)
        # one-hot entity
        try:
            v[off + self.entities.index(ir.entity or "")] = 1.0
        except ValueError:
            pass
        off += len(self.entities)
        # one-hot domain
        try:
            v[off + self.domains.index(ir.domain or "General")] = 1.0
        except ValueError:
            pass
        off += len(self.domains)
        # boolean flags
        for i, name in enumerate(self.flags):
            v[off + i] = 1.0 if getattr(ir, name, False) else 0.0
        off += len(self.flags)
        # auxiliary numeric features
        v[off] = float(len(ir.entities or []))
        v[off + 1] = math.log1p(len(ir.action_phrase or ir.source_text or ""))
        return v


def _ir_from_record(rec_ir: Dict[str, Any]) -> StoryIR:
    """Re-hydrate a StoryIR from a JSONL record's ``ir`` dict."""
    ir = StoryIR(source_text=rec_ir.get("source_text", ""))
    for key, value in rec_ir.items():
        if hasattr(ir, key):
            try:
                setattr(ir, key, value)
            except Exception:
                pass
    return ir


def _iter_records(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def _snap_to_scale(value: float) -> int:
    return min(SP_SCALE, key=lambda s: abs(s - value))


# ── Estimators ─────────────────────────────────────────────────────────────
class _BaseEstimator:
    spec: FeatureSpec

    def predict(self, ir: StoryIR) -> int:  # pragma: no cover - interface
        raise NotImplementedError


@dataclass
class HeuristicEstimator(_BaseEstimator):
    """Transparent fallback used when no trained model is available.

    Computes a weighted score from intent/entity/flags.  The numbers were
    calibrated against the existing rule set so its behaviour matches the
    legacy SP heuristics out of the box.
    """

    spec: FeatureSpec = field(default_factory=FeatureSpec)

    _INTENT_BASE: Dict[str, int] = field(default_factory=lambda: {
        "register": 5, "login": 3, "logout": 1,
        "book": 5, "pay": 8, "refund": 5, "invoice": 5,
        "create": 3, "update": 3, "delete": 2,
        "search": 3, "filter": 2,
        "manage": 8, "approve": 5,
        "diagnose": 8, "prescribe": 5, "admit": 5, "discharge": 5,
        "operate": 8, "report": 5,
        "notify": 2, "send_email": 3, "send_sms": 3,
        "upload": 3, "download": 2, "encrypt": 5,
        "audit": 5, "backup": 3,
    })
    _FLAG_PENALTIES: Dict[str, int] = field(default_factory=lambda: {
        "has_external_api": 2,
        "has_payment": 2,
        "is_realtime": 3,
        "has_file_io": 1,
        "is_crud_bundle": 2,
        "needs_permission_check": 1,
    })

    def predict(self, ir: StoryIR) -> int:
        base = self._INTENT_BASE.get(ir.intent or "", 5)
        bonus = sum(self._FLAG_PENALTIES.get(f, 0)
                    for f in self.spec.flags
                    if getattr(ir, f, False))
        return _snap_to_scale(base + bonus)


@dataclass
class SklearnEstimator(_BaseEstimator):
    """Wraps a fitted regression model + feature spec."""

    spec: FeatureSpec
    model: Any  # sklearn estimator with ``predict``

    def predict(self, ir: StoryIR) -> int:
        x = self.spec.vectorise(ir)
        try:
            y = float(self.model.predict([x])[0])
        except Exception:
            return _snap_to_scale(5)
        return _snap_to_scale(y)


# ── Training ───────────────────────────────────────────────────────────────
def _build_dataset(
    records: Iterable[Dict[str, Any]],
    spec: Optional[FeatureSpec] = None,
) -> Tuple[FeatureSpec, List[List[float]], List[float], List[float]]:
    """Returns (spec, X, y, sample_weight)."""
    spec = spec or FeatureSpec()
    irs: List[StoryIR] = []
    ys: List[float] = []
    weights: List[float] = []

    intents: set[str] = set(spec.intents)
    entities: set[str] = set(spec.entities)
    domains: set[str] = set(spec.domains)

    for rec in records:
        meta = rec.get("meta") or {}
        sp = meta.get("sp")
        if sp is None:
            continue
        try:
            sp = float(sp)
        except (TypeError, ValueError):
            continue
        ir_dict = rec.get("ir") or {}
        ir = _ir_from_record(ir_dict)
        irs.append(ir)
        ys.append(sp)
        conf = (ir.confidence or {}).get("intent", 0.5) if hasattr(ir, "confidence") else 0.5
        weights.append(1.0 if conf >= 0.5 else 0.5)
        intents.add(ir.intent or "unknown")
        entities.add(ir.entity or "")
        domains.add(ir.domain or "General")

    spec = FeatureSpec(
        intents=sorted(intents),
        entities=sorted(entities),
        domains=sorted(domains),
    )
    X = [spec.vectorise(ir) for ir in irs]
    return spec, X, ys, weights


def train_from_feedback(
    feedback_path: str | Path,
    out_path: str | Path | None = None,
    min_records: int = 20,
) -> _BaseEstimator:
    """Train an SP regressor from a JSONL feedback log.

    Falls back to :class:`HeuristicEstimator` when the log has fewer
    than ``min_records`` labelled rows or when scikit-learn is missing.

    Returns the trained estimator.  When ``out_path`` is given the
    estimator is also pickled there.
    """
    feedback_path = Path(feedback_path)
    if not feedback_path.exists():
        log.warning("Feedback log %s not found — using heuristic.",
                    feedback_path)
        return HeuristicEstimator()

    spec, X, y, w = _build_dataset(_iter_records(feedback_path))
    log.info("SP estimator: %d labelled records found", len(y))

    if len(y) < min_records:
        log.info("Below threshold %d → using HeuristicEstimator", min_records)
        return HeuristicEstimator(spec=spec)

    try:
        from sklearn.ensemble import GradientBoostingRegressor  # type: ignore
    except ImportError:
        log.warning("scikit-learn not installed — using HeuristicEstimator")
        return HeuristicEstimator(spec=spec)

    model = GradientBoostingRegressor(
        n_estimators=200, max_depth=3, learning_rate=0.05,
        random_state=42,
    )
    model.fit(X, y, sample_weight=w)
    estimator = SklearnEstimator(spec=spec, model=model)

    if out_path:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("wb") as fh:
            pickle.dump(estimator, fh)
        log.info("Saved estimator → %s", out_path)
    return estimator


def load_estimator(path: str | Path) -> _BaseEstimator:
    """Load a previously pickled estimator; fall back on errors."""
    p = Path(path)
    if not p.exists():
        return HeuristicEstimator()
    try:
        with p.open("rb") as fh:
            obj = pickle.load(fh)
        if isinstance(obj, _BaseEstimator):
            return obj
    except Exception as exc:
        log.warning("Failed to load %s: %s", path, exc)
    return HeuristicEstimator()
