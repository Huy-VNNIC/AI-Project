"""
Stage 1 — Requirement Parser
============================

Converts raw text into a :class:`ParsedRequirement` (actor / intent /
entities / constraints / edge-cases / domain / complexity).

Implementation strategy
-----------------------
* **Bilingual (VI/EN)** rule layer — covers the common verbs/actors
  found in healthcare, e-commerce, banking, hotel, education domains.
* Tries to **reuse** :class:`SemanticParser` from the requirement
  analyzer so we benefit from the lexicons that already exist there.
* Falls back to a self-contained heuristic if the semantic engine is
  not available (e.g. inside a worker that can't import scientific
  packages).

The parser produces ``confidence ∈ [0, 1]`` so downstream stages can
escalate to an LLM only on low-confidence requirements.
"""
from __future__ import annotations

import re
from typing import List, Optional

from .schemas import Complexity, ParsedRequirement

try:
    from requirement_analyzer.task_gen.semantic.parser import SemanticParser
    _SEMANTIC_AVAILABLE = True
except Exception:
    _SEMANTIC_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────
_DOMAIN_KEYWORDS = {
    "healthcare":  {"patient", "doctor", "appointment", "prescription",
                    "medical", "diagnos", "bệnh nhân", "bác sĩ", "khám",
                    "thuốc", "y tế", "viện", "hồ sơ bệnh"},
    "ecommerce":   {"cart", "checkout", "product", "order", "shipping",
                    "giỏ hàng", "đơn hàng", "sản phẩm", "khuyến mãi",
                    "thanh toán đơn"},
    "finance":     {"loan", "transfer", "transaction", "account balance",
                    "tài khoản", "chuyển khoản", "giao dịch", "vay"},
    "hotel":       {"booking", "room", "check-in", "check-out", "reserve",
                    "đặt phòng", "phòng", "khách sạn"},
    "education":   {"course", "lesson", "student", "enroll", "grade",
                    "khóa học", "học sinh", "điểm", "bài giảng"},
    "iot":         {"sensor", "device", "telemetry", "gateway",
                    "thiết bị", "cảm biến"},
}

# Heuristic actor / verb extraction (VI + EN)
_ACTOR_PATTERNS = [
    (r"\b(patient|doctor|admin|customer|user|guest|nurse|teacher|student|"
     r"manager|cashier|operator)\b", "en"),
    (r"\b(bệnh nhân|bác sĩ|quản trị|khách hàng|người dùng|khách|"
     r"y tá|giảng viên|học sinh|nhân viên|quản lý|lễ tân)\b", "vi"),
]

_VERBS_VI = {
    "đăng ký", "đăng nhập", "đăng xuất", "đặt", "hủy", "thanh toán",
    "tạo", "cập nhật", "xóa", "tìm", "tìm kiếm", "xem", "xuất",
    "in", "gửi", "nhận", "duyệt", "phê duyệt", "kiểm tra", "xác thực",
    "chẩn đoán", "kê toa", "kê đơn", "khám", "lưu", "sao lưu", "mã hóa",
    "phân quyền", "quản lý", "theo dõi", "báo cáo", "tích hợp",
}
_VERBS_EN = {
    "register", "login", "logout", "book", "reserve", "cancel", "pay",
    "create", "update", "delete", "search", "view", "export", "import",
    "send", "receive", "approve", "verify", "authenticate", "diagnose",
    "prescribe", "save", "backup", "encrypt", "manage", "track",
    "report", "integrate", "browse", "checkout", "add", "remove",
}

_PERMISSION_HINTS = {
    "must", "shall", "should", "only", "permission", "authoriz",
    "phải", "chỉ", "quyền", "được phép",
}
_SECURITY_HINTS = {
    "encrypt", "password", "auth", "token", "ssl", "https", "hash",
    "mã hóa", "mật khẩu", "xác thực", "chữ ký", "bảo mật",
}
_PERF_HINTS = {
    "second", "ms", "millisecond", "concurrent", "throughput", "latency",
    "uptime", "sla",
    "giây", "đồng thời", "tải", "thời gian phản hồi",
}


# ─────────────────────────────────────────────────────────────────────────
class RequirementParser:
    """Stage 1: requirement → ParsedRequirement."""

    def __init__(self, use_semantic: bool = True) -> None:
        self._sem: Optional[SemanticParser] = None
        if use_semantic and _SEMANTIC_AVAILABLE:
            try:
                self._sem = SemanticParser()
            except Exception:
                self._sem = None

    # ── public ─────────────────────────────────────────────────────────
    def parse(self, text: str) -> ParsedRequirement:
        text = (text or "").strip()
        if not text:
            return ParsedRequirement(raw="")

        out = ParsedRequirement(raw=text)
        out.domain = self._detect_domain(text)
        out.actor  = self._extract_actor(text)
        out.intent = self._extract_intent(text)
        out.entities = self._extract_entities(text, out.actor, out.intent)
        out.constraints = self._extract_constraints(text)
        out.nfr_tags = self._extract_nfr_tags(text)
        out.edge_cases = self._infer_edge_cases(out)
        out.complexity = self._estimate_complexity(text, out)
        out.confidence = self._score_confidence(out)

        # If semantic engine is available, override slots when more confident
        if self._sem is not None:
            try:
                ir = self._sem.parse(text)
                if ir.actor and not out.actor:
                    out.actor = ir.actor
                if ir.intent and not out.intent:
                    out.intent = ir.intent
                if ir.entity and ir.entity not in out.entities:
                    out.entities.insert(0, ir.entity)
                if ir.domain and ir.domain != "General":
                    out.domain = ir.domain.lower()
            except Exception:
                pass
        return out

    # ── helpers ────────────────────────────────────────────────────────
    @staticmethod
    def _detect_domain(text: str) -> str:
        low = text.lower()
        best, hits = "general", 0
        for dom, kws in _DOMAIN_KEYWORDS.items():
            n = sum(1 for kw in kws if kw in low)
            if n > hits:
                best, hits = dom, n
        return best

    @staticmethod
    def _extract_actor(text: str) -> str:
        low = text.lower()
        for pat, _ in _ACTOR_PATTERNS:
            m = re.search(pat, low)
            if m:
                return m.group(1).strip()
        # Fallback: look for "the X must / shall"
        m = re.search(r"\b(the|a|an)\s+([a-z]{3,15})\s+(must|shall|should|can)\b",
                      low)
        if m:
            return m.group(2)
        return "user"

    @staticmethod
    def _extract_intent(text: str) -> str:
        low = text.lower()
        # Try VI multi-word verbs first (longer match wins)
        for v in sorted(_VERBS_VI, key=len, reverse=True):
            if v in low:
                return v
        for v in sorted(_VERBS_EN, key=len, reverse=True):
            if re.search(rf"\b{re.escape(v)}\b", low):
                return v
        # Fallback: first verb-looking token after the actor
        m = re.search(r"(?:must|shall|should|can|được)\s+([a-zA-ZÀ-ỹ]+)", low)
        return m.group(1) if m else ""

    @staticmethod
    def _extract_entities(text: str, actor: str, intent: str) -> List[str]:
        # Extract noun-ish tokens that aren't the actor/intent.
        # Conservative: take 1-3 word phrases right after the verb.
        ents: List[str] = []
        low = text.lower()
        if intent and intent in low:
            tail = low.split(intent, 1)[1]
            # First content phrase up to 4 words
            tail = re.sub(r"^[\s\W]+", "", tail)
            phrase = " ".join(tail.split()[:4])
            phrase = re.sub(r"[.,;:!?].*$", "", phrase)
            if phrase and phrase != actor:
                ents.append(phrase.strip())
        # Add capitalised proper nouns from raw text
        for m in re.finditer(r"\b([A-Z][a-zA-Z]{2,})\b", text):
            tok = m.group(1).lower()
            if tok not in ents and tok != actor:
                ents.append(tok)
        return ents[:5]

    @staticmethod
    def _extract_constraints(text: str) -> List[str]:
        constraints: List[str] = []
        # "must / shall / should" clauses
        for m in re.finditer(
            r"(?:must|shall|should|phải|cần|chỉ được)\s+([^.;]+)", text, re.I
        ):
            cl = m.group(1).strip().rstrip(",")
            if 5 < len(cl) < 120:
                constraints.append(cl)
        # numeric thresholds (e.g. "in < 2 seconds", "100 concurrent users")
        for m in re.finditer(
            r"(\d+\s?(?:%|s|ms|seconds?|giây|users?|requests?|MB|GB))", text, re.I
        ):
            constraints.append(f"limit: {m.group(1)}")
        return constraints[:8]

    @staticmethod
    def _extract_nfr_tags(text: str) -> List[str]:
        low = text.lower()
        tags = []
        if any(h in low for h in _SECURITY_HINTS):    tags.append("security")
        if any(h in low for h in _PERF_HINTS):        tags.append("performance")
        if any(h in low for h in _PERMISSION_HINTS):  tags.append("permission")
        if "log" in low or "audit" in low:            tags.append("audit")
        return tags

    @staticmethod
    def _infer_edge_cases(p: ParsedRequirement) -> List[str]:
        ec: List[str] = []
        if p.intent in {"book", "reserve", "đặt"}:
            ec += ["selected slot is already taken",
                   "selected resource becomes unavailable mid-booking"]
        if p.intent in {"pay", "thanh toán", "checkout"}:
            ec += ["payment gateway times out",
                   "card declined / insufficient funds",
                   "double-submit results in duplicate charge"]
        if p.intent in {"login", "đăng nhập", "authenticate"}:
            ec += ["wrong password 5× in a row → account locked",
                   "session expires mid-action"]
        if p.intent in {"register", "đăng ký"}:
            ec += ["email already registered",
                   "weak password rejected"]
        if p.intent in {"upload", "import"}:
            ec += ["malformed file rejected",
                   "file exceeds size limit"]
        if "search" in (p.intent or "") or "tìm" in (p.intent or ""):
            ec += ["empty query handled gracefully",
                   "Unicode / special-character query"]
        if not ec:
            ec.append("missing required field is rejected with clear message")
        return ec[:6]

    @staticmethod
    def _estimate_complexity(text: str, p: ParsedRequirement) -> Complexity:
        score = 0
        score += min(len(text.split()) // 12, 3)
        score += len(p.constraints)
        score += len(p.nfr_tags) * 2
        score += len(p.entities) // 2
        if score <= 2:
            return Complexity.LOW
        if score <= 5:
            return Complexity.MEDIUM
        return Complexity.HIGH

    @staticmethod
    def _score_confidence(p: ParsedRequirement) -> float:
        s = 0.0
        if p.actor:    s += 0.25
        if p.intent:   s += 0.30
        if p.entities: s += 0.20
        if p.domain != "general": s += 0.15
        if p.constraints or p.nfr_tags: s += 0.10
        return round(min(1.0, s), 3)
