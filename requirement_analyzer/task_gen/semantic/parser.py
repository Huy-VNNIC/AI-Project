"""
SemanticParser
==============

Hybrid rule-bootstrap + (optional) embedding parser.  Converts raw
requirement text into a ``StoryIR``.

Architecture
------------
The parser runs through *layers*.  Each layer fills one or more IR slots
and stamps a confidence score in ``ir.confidence``.  Layers are ordered
from cheapest/most-deterministic to most-expensive:

    1. Lexicon layer (rule-based dictionary lookups)            — always on
    2. Pattern layer (regex for channels, constraints, NFRs)    — always on
    3. Behavioral signals (compound flags)                      — always on
    4. Embedding layer (pluggable, via ``embedding_backend``)   — optional

Each higher layer only fills slots that lower layers left ``None`` or
marked low-confidence (< 0.5), so adding ML never *overwrites* a
high-confidence rule decision.
"""
from __future__ import annotations

import re
from typing import Callable, Iterable, List, Optional, Tuple

from .ir import CANONICAL_INTENTS, RequirementType, StoryIR


# ── Lexicons (rule layer) ───────────────────────────────────────────────────
# Order matters inside each list — longer/more-specific phrases first.

ACTOR_LEXICON: List[Tuple[str, str]] = [
    # (keyword, canonical actor — Capitalized for direct insertion in story)
    ("quản trị viên", "Quản trị viên"),
    ("quản lý",       "Quản lý"),
    ("lễ tân",        "Lễ tân"),
    ("nhân viên",     "Nhân viên"),
    ("khách hàng",    "Khách hàng"),
    ("bệnh nhân",     "Bệnh nhân"),
    ("bác sĩ",        "Bác sĩ"),
    ("điều dưỡng",    "Điều dưỡng"),
    ("dược sĩ",       "Dược sĩ"),
    ("giáo viên",     "Giáo viên"),
    ("học sinh",      "Học sinh"),
    ("người dùng",    "Người dùng"),
    ("admin",         "Quản trị viên"),
    ("user",          "Người dùng"),
    ("customer",      "Khách hàng"),
    ("patient",       "Bệnh nhân"),
    ("doctor",        "Bác sĩ"),
    ("nurse",         "Điều dưỡng"),
]

# Some actors are *also* valid entities (a patient can be the actor or
# the object).  When we already chose them as actor, suppress the same
# canonical from the entity slot to avoid bogus "Bác sĩ kê đơn cho bác
# sĩ" stories.
_ACTOR_TO_ENTITY: dict[str, str] = {
    "Bệnh nhân":     "patient",
    "Bác sĩ":        "doctor",
    "Điều dưỡng":    "nurse",
    "Người dùng":    "user",
    "Khách hàng":    "customer",
}

INTENT_LEXICON: List[Tuple[str, str]] = [
    # Multi-word phrases first so they match before single-word verbs.
    ("đăng ký",       "register"),
    ("đăng nhập",     "login"),
    ("đăng xuất",     "logout"),
    ("xác thực",      "authenticate"),
    ("đặt lịch",      "book"),
    ("đặt phòng",     "book"),
    ("đặt vé",        "book"),
    ("đặt chỗ",       "reserve"),
    ("nhập viện",     "admit"),
    ("xuất viện",     "discharge"),
    ("phẫu thuật",    "operate"),
    ("chẩn đoán",     "diagnose"),
    ("kê đơn",        "prescribe"),
    ("kê toa",        "prescribe"),
    ("thanh toán",    "pay"),
    ("hoàn tiền",     "refund"),
    ("xuất hóa đơn",  "invoice"),
    ("lập hóa đơn",   "invoice"),
    ("tải lên",       "upload"),
    ("tải xuống",     "download"),
    ("xuất báo cáo",  "report"),
    ("xem báo cáo",   "report"),
    ("báo cáo",       "report"),
    ("xuất file",     "export"),
    ("tìm kiếm",      "search"),
    ("tra cứu",       "search"),
    ("lọc",           "filter"),
    ("phê duyệt",     "approve"),
    ("duyệt",         "approve"),
    ("phân công",     "assign"),
    ("phân quyền",    "manage_permission"),
    ("phân bổ",       "assign"),
    ("theo dõi",      "track"),
    ("giám sát",      "monitor"),
    ("kiểm tra",      "verify"),
    ("kiểm soát",     "control"),
    ("xác nhận",      "confirm"),
    ("hủy",           "cancel"),
    ("thiết lập",     "configure"),
    ("cấu hình",      "configure"),
    ("tích hợp",      "integrate"),
    ("đồng bộ hóa",   "sync"),
    ("đồng bộ",       "sync"),
    ("lưu trữ",       "archive"),
    ("khuyến mãi",    "manage"),
    ("chuyển",        "transfer"),
    ("gửi email",     "send_email"),
    ("gửi sms",       "send_sms"),
    ("thông báo",     "notify"),
    ("mã hóa",        "encrypt"),
    ("audit log",     "audit"),
    ("ghi log",       "audit"),
    ("sao lưu",       "backup"),
    ("backup",        "backup"),
    ("quản lý",       "manage"),
    ("tạo",           "create"),
    ("thêm",          "create"),
    ("sửa",           "update"),
    ("cập nhật",      "update"),
    ("xóa",           "delete"),
    ("xem",           "view"),
    ("hiển thị",      "view"),
    ("liệt kê",       "list"),
    # English aliases
    ("register",      "register"),
    ("login",         "login"),
    ("book",          "book"),
    ("pay",           "pay"),
    ("create",        "create"),
    ("update",        "update"),
    ("delete",        "delete"),
    ("search",        "search"),
    ("filter",        "filter"),
    ("manage",        "manage"),
    ("upload",        "upload"),
    ("download",      "download"),
    ("notify",        "notify"),
    ("integrate",     "integrate"),
    ("sync",          "sync"),
    ("monitor",       "monitor"),
    ("track",         "track"),
    ("verify",        "verify"),
    ("approve",       "approve"),
    ("configure",     "configure"),
    ("assign",        "assign"),
    ("cancel",        "cancel"),
    ("confirm",       "confirm"),
    ("transfer",      "transfer"),
    ("archive",       "archive"),
]

ENTITY_LEXICON: List[Tuple[str, str]] = [
    ("hồ sơ bệnh án", "medical_record"),
    ("hồ sơ",         "record"),
    ("lịch khám",     "appointment"),
    ("lịch hẹn",      "appointment"),
    ("lịch phẫu thuật", "surgery_schedule"),
    ("phòng mổ",      "operating_room"),
    ("giường bệnh",   "bed"),
    ("bệnh nhân",     "patient"),
    ("bác sĩ",        "doctor"),
    ("đơn thuốc",     "prescription"),
    ("toa thuốc",     "prescription"),
    ("thuốc",         "medication"),
    ("hóa đơn",       "invoice"),
    ("viện phí",      "hospital_bill"),
    ("phòng khách sạn", "hotel_room"),
    ("phòng",         "room"),
    ("khách sạn",     "hotel"),
    ("đơn hàng",      "order"),
    ("báo cáo",       "report"),
    ("tài khoản",     "account"),
    ("người dùng",    "user"),
    ("vai trò",       "role"),
    ("quyền",         "permission"),
    ("email",         "email"),
    # English
    ("appointment",   "appointment"),
    ("medical record", "medical_record"),
    ("invoice",       "invoice"),
    ("room",          "room"),
    ("user",          "user"),
    ("role",          "role"),
    ("report",        "report"),
]

CHANNEL_LEXICON: List[Tuple[str, str]] = [
    ("online",   "online"),
    ("trực tuyến", "online"),
    ("mobile",   "mobile"),
    ("di động",  "mobile"),
    ("điện thoại", "mobile"),
    ("kiosk",    "kiosk"),
    ("web",      "web"),
]


# ── Domain detection (specific → generic) ───────────────────────────────────
DOMAIN_RULES: List[Tuple[str, List[str]]] = [
    ("Surgery",     ["phẫu thuật", "mổ", "phòng mổ", "surgical", "surgery", "operating room"]),
    ("Inpatient",   ["giường bệnh", "nội trú", "inpatient", "ward",
                     "nhập viện", "xuất viện", "discharge"]),
    ("Clinical",    ["bác sĩ", "chẩn đoán", "diagnosis", "khám bệnh",
                     "physician", "điều dưỡng", "nurse", "triệu chứng",
                     "symptom", "clinical", "prescription"]),
    ("Pharmacy",    ["thuốc", "nhà thuốc", "pharmacy", "medication",
                     "drug", "đơn thuốc"]),
    ("Laboratory",  ["xét nghiệm", "laboratory", "lab test", "sample"]),
    ("Healthcare",  ["bệnh viện", "bệnh nhân", "y tế", "medical",
                     "hospital", "patient", "healthcare"]),
    ("Payment/Billing", ["viện phí", "thanh toán", "payment",
                         "billing", "invoice", "hóa đơn"]),
    ("Hotel",       ["khách sạn", "hotel", "phòng khách sạn", "hotel room"]),
    ("Booking/Reservation", ["đặt phòng", "đặt lịch", "booking", "reservation"]),
]


# ── NFR / DevOps / Tech detectors ───────────────────────────────────────────
NFR_HINTS = [
    "uptime", "availability", "sẵn sàng", "%",
    "response time", "thời gian phản hồi", "latency",
    "performance", "hiệu suất", "throughput",
    "ssl", "tls", "https", "encrypt", "mã hóa",
    "compliance", "gdpr", "hipaa", "iso",
]
DEVOPS_HINTS = ["backup", "sao lưu", "disaster recovery", "ci/cd",
                "deploy", "monitoring", "logging infrastructure"]
TECH_HINTS = ["react", "vue", "angular", "spring boot", "django",
              ".net", "kubernetes", "docker"]


# Compound behavior flags
EXTERNAL_API_HINTS = ["api", "webhook", "third-party", "tích hợp",
                      "gateway", "external"]
NOTIFICATION_HINTS = ["email", "sms", "thông báo", "notify",
                      "notification", "push"]
FILE_HINTS = ["upload", "download", "tải lên", "tải xuống",
              "file", "tệp", "import", "export", "pdf", "excel"]
REALTIME_HINTS = ["real-time", "realtime", "real time",
                  "websocket", "streaming", "thời gian thực"]


EmbeddingBackend = Callable[[str, Iterable[str]], Tuple[Optional[str], float]]
"""Optional plug-in that picks a label from candidates.

Signature: ``backend(text, candidate_labels) -> (best_label, score)``.
``best_label`` may be ``None`` when the backend has no opinion.
"""


class SemanticParser:
    """Hybrid rule + (optional) embedding parser.

    Examples
    --------
    >>> parser = SemanticParser()
    >>> ir = parser.parse("Bệnh nhân có thể đặt lịch khám với bác sĩ online")
    >>> ir.actor, ir.intent, ir.entity, ir.channel, ir.domain
    ('Bệnh nhân', 'book', 'appointment', 'online', 'Clinical')
    """

    def __init__(
        self,
        embedding_backend: Optional[EmbeddingBackend] = None,
        embedding_threshold: float = 0.55,
    ) -> None:
        self._embedding_backend = embedding_backend
        self._embedding_threshold = embedding_threshold

    # ── Public entry ────────────────────────────────────────────────────
    def parse(self, text: str) -> StoryIR:
        ir = StoryIR(source_text=text)
        text_lower = text.lower()

        # Layer 1 — lexicon
        self._fill_actor(ir, text_lower)
        self._fill_intent(ir, text_lower)
        self._fill_entity(ir, text_lower)
        self._fill_channel(ir, text_lower)
        self._fill_domain(ir, text_lower)
        self._fill_type(ir, text_lower)
        self._fill_behavioral_flags(ir, text_lower)

        # Layer 2 — derived clean action phrase (used by story generator
        # only when the IR is too sparse to render a clean template)
        ir.action_phrase = self._derive_action_phrase(text)

        # Layer 3 — embedding fallback for slots still empty / uncertain
        if self._embedding_backend is not None:
            self._embedding_fallback(ir)

        return ir

    # ── Lexicon helpers ─────────────────────────────────────────────────
    def _fill_actor(self, ir: StoryIR, text_lower: str) -> None:
        # Pick the actor whose keyword appears earliest in the text —
        # subject position is a strong signal ("Bác sĩ kê đơn cho bệnh
        # nhân" → actor is *Bác sĩ*, not *Bệnh nhân*).
        best_pos: int = -1
        best_canonical: Optional[str] = None
        for keyword, canonical in ACTOR_LEXICON:
            pos = text_lower.find(keyword)
            if pos == -1:
                continue
            if best_pos == -1 or pos < best_pos:
                best_pos = pos
                best_canonical = canonical
        if best_canonical is not None:
            ir.actor = best_canonical
            ir.confidence["actor"] = 0.9
            ir.parser_layers.append("rule:actor")
            return
        # default
        ir.actor = "Người dùng"
        ir.confidence["actor"] = 0.3

    def _fill_intent(self, ir: StoryIR, text_lower: str) -> None:
        # Same earliest-position strategy. When two phrases tie, longer
        # (more specific) one wins — e.g. "đăng nhập" beats "đăng".
        best_pos: int = -1
        best_len: int = 0
        best_canonical: Optional[str] = None
        for keyword, canonical in INTENT_LEXICON:
            pos = text_lower.find(keyword)
            if pos == -1:
                continue
            if (
                best_pos == -1
                or pos < best_pos
                or (pos == best_pos and len(keyword) > best_len)
            ):
                best_pos = pos
                best_len = len(keyword)
                best_canonical = canonical
        if best_canonical is not None:
            ir.intent = best_canonical
            ir.confidence["intent"] = 0.9
            ir.parser_layers.append("rule:intent")
            return
        ir.intent = "unknown"
        ir.confidence["intent"] = 0.0

    def _fill_entity(self, ir: StoryIR, text_lower: str) -> None:
        # Earliest-position wins for the *primary* entity. Secondary
        # entities are kept in ``ir.entities`` in their order of appearance.
        # Drop any entity whose canonical matches the chosen actor — e.g.
        # "Bác sĩ kê đơn thuốc cho bệnh nhân" should resolve to entity
        # ``prescription``, not ``doctor`` (the subject) or ``patient``
        # (the indirect object that *is* the actor in another reading).
        hits: List[Tuple[int, int, str]] = []  # (pos, -length, canonical)
        for keyword, canonical in ENTITY_LEXICON:
            pos = text_lower.find(keyword)
            if pos != -1:
                hits.append((pos, -len(keyword), canonical))
        if not hits:
            return
        hits.sort()  # earliest position, then longer keyword wins on ties
        actor_canonical = _ACTOR_TO_ENTITY.get(ir.actor or "")
        seen: List[str] = []
        for _, _, canonical in hits:
            if canonical == actor_canonical:
                continue
            if canonical not in seen:
                seen.append(canonical)
        if not seen:
            return
        ir.entity = seen[0]
        ir.entities = seen
        ir.confidence["entity"] = 0.85
        ir.parser_layers.append("rule:entity")

    def _fill_channel(self, ir: StoryIR, text_lower: str) -> None:
        for keyword, canonical in CHANNEL_LEXICON:
            if keyword in text_lower:
                ir.channel = canonical
                ir.confidence["channel"] = 0.8
                ir.parser_layers.append("rule:channel")
                return

    def _fill_domain(self, ir: StoryIR, text_lower: str) -> None:
        for domain, hints in DOMAIN_RULES:
            if any(h in text_lower for h in hints):
                ir.domain = domain
                ir.confidence["domain"] = 0.85
                ir.parser_layers.append("rule:domain")
                return
        ir.domain = "General"
        ir.confidence["domain"] = 0.3

    def _fill_type(self, ir: StoryIR, text_lower: str) -> None:
        # Functional features that *mention* security keywords (e.g. "phân
        # quyền người dùng") must not be reclassified as NFR.
        functional_overrides = ["quản lý", "đặt", "thanh toán", "tạo",
                                "cập nhật", "xóa", "đăng ký", "đăng nhập",
                                "manage", "book", "create", "update",
                                "delete", "register", "login"]
        is_functional = any(k in text_lower for k in functional_overrides)

        if any(h in text_lower for h in TECH_HINTS):
            ir.requirement_type = RequirementType.TECH
        elif any(h in text_lower for h in DEVOPS_HINTS):
            ir.requirement_type = RequirementType.DEVOPS
        elif (not is_functional) and any(h in text_lower for h in NFR_HINTS):
            ir.requirement_type = RequirementType.NFR
        else:
            ir.requirement_type = RequirementType.FUNCTIONAL
        ir.confidence["requirement_type"] = 0.8

    def _fill_behavioral_flags(self, ir: StoryIR, text_lower: str) -> None:
        ir.has_external_api = any(h in text_lower for h in EXTERNAL_API_HINTS)
        ir.has_notification = any(h in text_lower for h in NOTIFICATION_HINTS)
        ir.has_file_io      = any(h in text_lower for h in FILE_HINTS)
        ir.is_realtime      = any(h in text_lower for h in REALTIME_HINTS)
        ir.has_payment      = ir.intent in {"pay", "refund", "invoice"} or \
            any(k in text_lower for k in ["thanh toán", "payment", "billing"])
        ir.needs_permission_check = any(k in text_lower for k in [
            "phân quyền", "vai trò", "role", "permission", "rbac",
            "access control", "quản trị viên", "admin",
        ])
        # "Quản lý X" → full CRUD bundle (heavier than single-action)
        ir.is_crud_bundle = (
            ir.intent == "manage"
            or ("quản lý" in text_lower
                and any(k in text_lower for k in ["danh sách", "thông tin"]))
        )

    # ── Action-phrase cleaner ───────────────────────────────────────────
    # List/bullet markers ("1. ", "1) ", "- ", "* ", "•", "+ ") that
    # appear at the very start of a requirement bullet.
    _LEADING_BULLET = re.compile(
        r"^\s*(?:\d+[\.\)]\s+|[-*•+]\s+)+", re.UNICODE
    )
    _DUP_SUBJECT_PATTERNS = [
        r"^cho phép\s+(khách hàng|người dùng|bệnh nhân|user|customer|admin|quản trị viên|nhân viên|bác sĩ|lễ tân)\b\s*",
        r"^hệ thống\s+cho phép\s+(khách hàng|người dùng|bệnh nhân|user|customer|admin|bác sĩ)\b\s*",
        r"^hệ thống\s+(cho phép|hỗ trợ|cung cấp)\b\s*",
        r"^the\s+system\s+allows\s+(the\s+)?(user|customer|patient|admin|doctor)\s+to\s+",
        r"^allow\s+(the\s+)?(user|customer|patient|admin|doctor)\s+to\s+",
        r"^(khách hàng|người dùng|bệnh nhân|bác sĩ|quản trị viên|nhân viên|lễ tân|admin|user|customer|patient|doctor|staff)\s+(có thể|được|sẽ|cần|phải)\s+",
        r"^(khách hàng|người dùng|bệnh nhân|bác sĩ|quản trị viên|lễ tân|admin|user|customer|patient|doctor|staff)\s+",
        r"^hệ thống\s+",
        r"^the\s+system\s+",
    ]
    _LEADING_PARTICLES = ("phải ", "cần ", "được ", "có thể ", "to ")

    def _derive_action_phrase(self, text: str) -> str:
        cleaned = re.sub(r"\s+", " ", text).strip()
        # Strip list markers like "1. ", "- ", "• " first
        cleaned = self._LEADING_BULLET.sub("", cleaned).strip()
        for _ in range(3):
            changed = False
            for pat in self._DUP_SUBJECT_PATTERNS:
                new = re.sub(pat, "", cleaned, flags=re.IGNORECASE).strip()
                if new != cleaned:
                    cleaned = new
                    changed = True
            if not changed:
                break
        low = cleaned.lower()
        for p in self._LEADING_PARTICLES:
            if low.startswith(p):
                cleaned = cleaned[len(p):].strip()
                break
        cleaned = cleaned.rstrip(" .;,:").strip()
        if cleaned and cleaned[0].isupper() and len(cleaned) > 1 and cleaned[1].islower():
            cleaned = cleaned[0].lower() + cleaned[1:]
        return cleaned

    # ── Embedding fallback layer ────────────────────────────────────────
    def _embedding_fallback(self, ir: StoryIR) -> None:
        """Fill empty / low-confidence slots using the plug-in backend."""
        if self._embedding_backend is None:
            return

        if ir.confidence.get("intent", 0.0) < 0.5:
            label, score = self._embedding_backend(
                ir.source_text,
                sorted(CANONICAL_INTENTS - {"unknown"}),
            )
            if label and score >= self._embedding_threshold:
                ir.intent = label
                ir.confidence["intent"] = score
                ir.parser_layers.append(f"embedding:intent={score:.2f}")

        if ir.confidence.get("entity", 0.0) < 0.5:
            entity_candidates = sorted({c for _, c in ENTITY_LEXICON})
            label, score = self._embedding_backend(
                ir.source_text, entity_candidates,
            )
            if label and score >= self._embedding_threshold:
                ir.entity = label
                ir.confidence["entity"] = score
                ir.parser_layers.append(f"embedding:entity={score:.2f}")
