"""
StoryGenerator
==============

Renders a clean "Là một X, tôi muốn Y, để Z" sentence from a ``StoryIR``.

Key design choice: the generator is **template-free at the surface** —
it composes phrases from intent/entity vocabularies rather than copying
substrings from raw text.  When the IR is too sparse it falls back to
``ir.action_phrase`` (already cleaned by the parser).
"""
from __future__ import annotations

from typing import Dict, Optional

from .ir import StoryIR


# Canonical intent → Vietnamese / English verb phrases.
INTENT_VERB_VI: Dict[str, str] = {
    "register": "đăng ký",
    "login": "đăng nhập",
    "logout": "đăng xuất",
    "authenticate": "xác thực",
    "book": "đặt",
    "reserve": "đặt chỗ",
    "schedule": "lên lịch",
    "create": "tạo",
    "read": "xem",
    "update": "cập nhật",
    "delete": "xóa",
    "list": "xem danh sách",
    "search": "tìm kiếm",
    "filter": "lọc",
    "view": "xem",
    "pay": "thanh toán",
    "refund": "hoàn tiền",
    "invoice": "xuất hóa đơn",
    "manage": "quản lý",
    "approve": "phê duyệt",
    "assign": "phân công",
    "track": "theo dõi",
    "monitor": "giám sát",
    "verify": "kiểm tra",
    "control": "kiểm soát",
    "confirm": "xác nhận",
    "cancel": "hủy",
    "configure": "thiết lập cấu hình",
    "integrate": "tích hợp",
    "sync": "đồng bộ",
    "archive": "lưu trữ",
    "transfer": "chuyển",
    "manage_permission": "quản lý phân quyền",
    "diagnose": "chẩn đoán",
    "prescribe": "kê đơn thuốc cho",
    "admit": "tiếp nhận nhập viện cho",
    "discharge": "làm thủ tục xuất viện cho",
    "operate": "thực hiện phẫu thuật cho",
    "report": "xem báo cáo",
    "export": "xuất dữ liệu",
    "import": "nhập dữ liệu",
    "upload": "tải lên",
    "download": "tải xuống",
    "notify": "gửi thông báo",
    "send_email": "gửi email",
    "send_sms": "gửi SMS",
    "encrypt": "bảo mật bằng mã hóa",
    "audit": "ghi audit log cho",
    "backup": "sao lưu",
}

INTENT_VERB_EN: Dict[str, str] = {
    "register": "register",
    "login": "log in",
    "logout": "log out",
    "authenticate": "authenticate",
    "book": "book",
    "reserve": "reserve",
    "schedule": "schedule",
    "create": "create",
    "read": "view",
    "update": "update",
    "delete": "delete",
    "list": "view a list of",
    "search": "search for",
    "filter": "filter",
    "view": "view",
    "pay": "pay for",
    "refund": "refund",
    "invoice": "issue an invoice for",
    "manage": "manage",
    "approve": "approve",
    "assign": "assign",
    "track": "track",
    "monitor": "monitor",
    "verify": "verify",
    "control": "control",
    "confirm": "confirm",
    "cancel": "cancel",
    "configure": "configure",
    "integrate": "integrate",
    "sync": "sync",
    "archive": "archive",
    "transfer": "transfer",
    "manage_permission": "manage permissions for",
    "diagnose": "diagnose",
    "prescribe": "prescribe medication for",
    "admit": "admit",
    "discharge": "discharge",
    "operate": "perform surgery on",
    "report": "view reports on",
    "export": "export",
    "import": "import",
    "upload": "upload",
    "download": "download",
    "notify": "send notifications about",
    "send_email": "send emails about",
    "send_sms": "send SMS about",
    "encrypt": "encrypt",
    "audit": "audit",
    "backup": "back up",
}


# Canonical entity → user-facing phrase.
ENTITY_PHRASE_VI: Dict[str, str] = {
    "appointment":      "lịch khám",
    "surgery_schedule": "lịch phẫu thuật",
    "operating_room":   "phòng mổ",
    "medical_record":   "hồ sơ bệnh án",
    "record":           "hồ sơ",
    "prescription":     "đơn thuốc",
    "medication":       "thuốc",
    "invoice":          "hóa đơn",
    "hospital_bill":    "viện phí",
    "hotel_room":       "phòng khách sạn",
    "room":             "phòng",
    "hotel":            "khách sạn",
    "order":            "đơn hàng",
    "report":           "báo cáo",
    "account":          "tài khoản",
    "user":             "người dùng",
    "role":             "vai trò",
    "permission":       "quyền truy cập",
    "email":            "email",
    "patient":          "bệnh nhân",
    "doctor":           "bác sĩ",
    "bed":              "giường bệnh",
}

ENTITY_PHRASE_EN: Dict[str, str] = {
    "appointment":      "an appointment",
    "surgery_schedule": "the surgery schedule",
    "operating_room":   "the operating room",
    "medical_record":   "the medical record",
    "record":           "the record",
    "prescription":     "a prescription",
    "medication":       "medication",
    "invoice":          "the invoice",
    "hospital_bill":    "the hospital bill",
    "hotel_room":       "a hotel room",
    "room":             "a room",
    "hotel":            "the hotel",
    "order":            "an order",
    "report":           "the report",
    "account":          "an account",
    "user":             "users",
    "role":             "roles",
    "permission":       "permissions",
    "email":            "emails",
    "patient":          "the patient",
    "doctor":           "the doctor",
    "bed":              "the bed",
}


# Default benefit per intent — gives the "so that …" clause real meaning.
BENEFIT_VI: Dict[str, str] = {
    "register":   "có thể sử dụng các dịch vụ của hệ thống",
    "login":      "truy cập an toàn vào tài khoản của mình",
    "book":       "tiết kiệm thời gian và chủ động về lịch",
    "reserve":    "đảm bảo có chỗ khi cần",
    "pay":        "hoàn tất giao dịch nhanh chóng và an toàn",
    "refund":     "lấy lại số tiền đã thanh toán khi cần",
    "create":     "ghi nhận thông tin đầy đủ vào hệ thống",
    "update":     "giữ thông tin luôn chính xác và kịp thời",
    "delete":     "loại bỏ dữ liệu không còn cần thiết",
    "search":     "nhanh chóng tìm thấy thông tin cần thiết",
    "filter":     "thu hẹp kết quả theo tiêu chí phù hợp",
    "view":       "nắm được thông tin một cách rõ ràng",
    "manage":     "kiểm soát và vận hành hiệu quả",
    "approve":    "đảm bảo đúng quy trình phê duyệt",
    "diagnose":   "đưa ra phương án điều trị chính xác",
    "prescribe":  "đảm bảo bệnh nhân nhận đúng thuốc",
    "admit":      "tiếp nhận bệnh nhân vào điều trị nội trú",
    "discharge":  "hoàn tất quy trình xuất viện đúng quy định",
    "operate":    "đảm bảo ca phẫu thuật được thực hiện đúng kế hoạch",
    "report":     "có dữ liệu phục vụ ra quyết định",
    "notify":     "thông tin được truyền đến đúng người, đúng lúc",
    "send_email": "thông tin được gửi đến khách hàng kịp thời",
    "send_sms":   "thông tin được gửi đến khách hàng kịp thời",
    "upload":     "đưa dữ liệu vào hệ thống một cách thuận tiện",
    "download":   "lưu dữ liệu về máy khi cần",
    "encrypt":    "bảo vệ dữ liệu nhạy cảm khỏi truy cập trái phép",
    "audit":      "có thể truy vết mọi thay đổi quan trọng",
    "backup":     "khôi phục dữ liệu khi xảy ra sự cố",
}

BENEFIT_EN: Dict[str, str] = {
    "register":   "I can start using the system",
    "login":      "I can securely access my account",
    "book":       "I can save time and stay in control of my schedule",
    "pay":        "the transaction is completed quickly and safely",
    "create":     "the information is recorded properly",
    "update":     "the information stays accurate",
    "delete":     "obsolete data is removed",
    "search":     "I can quickly find what I need",
    "filter":     "I can narrow results to relevant items",
    "manage":     "operations stay under control",
    "diagnose":   "I can determine the right treatment plan",
    "report":     "I have data to make informed decisions",
}


class StoryGenerator:
    """Render user-story sentences from a ``StoryIR``."""

    # Intents whose verb already implies the entity — don't append the
    # entity phrase, otherwise we get "đăng nhập người dùng" or
    # "đăng ký tài khoản tài khoản".
    _INTENT_DROPS_ENTITY = {
        "login", "logout", "register", "authenticate",
        "send_email", "send_sms", "notify", "backup",
        "manage_permission",
    }

    def __init__(self, language: str = "vi") -> None:
        self.language = language

    def render(self, ir: StoryIR) -> str:
        if self.language == "vi":
            return self._render_vi(ir)
        return self._render_en(ir)

    # ── Vietnamese ──────────────────────────────────────────────────────
    def _render_vi(self, ir: StoryIR) -> str:
        actor = ir.actor or "Người dùng"
        verb = INTENT_VERB_VI.get(ir.intent or "", None)
        entity = ENTITY_PHRASE_VI.get(ir.entity or "", "")
        channel = ir.channel
        benefit = ir.benefit or BENEFIT_VI.get(ir.intent or "", "hoàn thành công việc một cách hiệu quả")

        if verb:
            phrase = verb
            if entity and ir.intent not in self._INTENT_DROPS_ENTITY \
                    and entity.lower() not in verb.lower():
                phrase = f"{verb} {entity}".strip()
            else:
                # Verb may end in a dangling Vietnamese preposition
                # ("kê đơn thuốc cho") when no entity is appended.
                for tail in (" cho", " với", " đến", " vào"):
                    if phrase.endswith(tail):
                        phrase = phrase[: -len(tail)]
                        break
            if channel == "online":
                phrase = f"{phrase} trực tuyến"
            elif channel == "mobile":
                phrase = f"{phrase} trên thiết bị di động"
        else:
            # IR is too sparse → use the cleaned action phrase
            phrase = ir.action_phrase or ir.source_text.strip().rstrip(".")

        return f"Là một {actor}, tôi muốn {phrase}, để {benefit}."

    # ── English ─────────────────────────────────────────────────────────
    def _render_en(self, ir: StoryIR) -> str:
        actor = ir.actor or "User"
        verb = INTENT_VERB_EN.get(ir.intent or "", None)
        entity = ENTITY_PHRASE_EN.get(ir.entity or "", "")
        channel = ir.channel
        benefit = ir.benefit or BENEFIT_EN.get(ir.intent or "", "I can do my job effectively")

        if verb:
            phrase = verb
            if entity and ir.intent not in self._INTENT_DROPS_ENTITY \
                    and entity.lower() not in verb.lower():
                phrase = f"{verb} {entity}".strip()
            else:
                for tail in (" for", " on", " to", " with", " about"):
                    if phrase.endswith(tail):
                        phrase = phrase[: -len(tail)]
                        break
            if channel == "online":
                phrase = f"{phrase} online"
            elif channel == "mobile":
                phrase = f"{phrase} on mobile"
        else:
            phrase = ir.action_phrase or ir.source_text.strip().rstrip(".")

        return f"As a {actor}, I want to {phrase}, so that {benefit}."

    # Words that should never end a title (Vietnamese prepositions,
    # conjunctions, articles).  When the truncation cut leaves one of
    # these dangling, strip it.
    _DANGLING_TAIL_WORDS = {
        # vi
        "của", "cho", "với", "và", "hoặc", "khi", "để", "theo", "tại",
        "vào", "trong", "bằng", "bao", "gồm", "qua", "trên", "dưới",
        "hay", "như", "do", "bởi", "rằng", "là", "được", "phải", "cần",
        "có", "không", "thì", "mà", "nếu",
        # en
        "of", "for", "with", "and", "or", "when", "to", "by", "at",
        "in", "on", "the", "a", "an", "as", "is", "be", "via",
    }
    _MAX_TITLE_LEN = 80

    @staticmethod
    def _clean_fallback_title(text: str) -> str:
        import re as _re
        # Strip bullet/list markers
        text = _re.sub(r"^\s*(?:\d+[\.\)]\s+|[-*•+]\s+)+", "", text).strip()
        # First clause only (drop sub-sentences)
        for sep in (". ", "; ", " - ", " – "):
            if sep in text:
                text = text.split(sep, 1)[0]
                break
        # Truncate on a word boundary (don't slice mid-word)
        if len(text) > StoryGenerator._MAX_TITLE_LEN:
            cut = text[: StoryGenerator._MAX_TITLE_LEN]
            sp = cut.rfind(" ")
            if sp >= 40:
                cut = cut[:sp]
            text = cut
        text = text.rstrip(" .,;:")
        # Strip dangling stop-words from the right
        for _ in range(4):
            parts = text.rsplit(" ", 1)
            if len(parts) < 2:
                break
            if parts[1].lower() in StoryGenerator._DANGLING_TAIL_WORDS:
                text = parts[0].rstrip(" .,;:")
            else:
                break
        return text

    # ── Helpers used by other modules ───────────────────────────────────
    @staticmethod
    def title_for(ir: StoryIR, language: str = "vi") -> str:
        """Generate a short title for the story.

        Behaviour:
        * Use ``intent verb + entity`` when both are known.
        * Skip the entity for intents that already imply it (e.g. ``login``
          shouldn't render as "Đăng nhập người dùng", ``send_email`` not as
          "Gửi email email").
        * On unknown / empty intent, fall back to the cleaned action
          phrase rather than literally inserting the word "unknown".
        """
        verb_map = INTENT_VERB_VI if language == "vi" else INTENT_VERB_EN
        ent_map = ENTITY_PHRASE_VI if language == "vi" else ENTITY_PHRASE_EN

        intent = ir.intent or ""
        verb = verb_map.get(intent, "")

        # Unknown / unmapped intent → don't synthesise a fake verb
        if not verb or intent in {"unknown", ""}:
            fallback = (ir.action_phrase or ir.source_text or "").strip()
            fallback = StoryGenerator._clean_fallback_title(fallback)
            if fallback:
                return fallback[:1].upper() + fallback[1:]
            return "Yêu cầu" if language == "vi" else "Requirement"

        # Some intents already incorporate the entity into the verb
        # phrase (login/send_email/…) — keep title clean.
        entity = ""
        if intent not in StoryGenerator._INTENT_DROPS_ENTITY:
            entity = ent_map.get(ir.entity or "", "")
            # Avoid repeating an entity word that's already inside the verb
            # phrase, e.g. verb="xem báo cáo" + entity="báo cáo" → drop.
            if entity and entity.lower() in verb.lower():
                entity = ""

        title = f"{verb} {entity}".strip()
        # Strip dangling preposition when no entity was appended
        if not entity:
            for tail in (" cho", " với", " đến", " vào",
                          " for", " on", " to", " with", " about"):
                if title.endswith(tail):
                    title = title[: -len(tail)]
                    break
        # Title is too short (e.g. just a single verb "Xem") → enrich
        # with the cleaned action phrase so the user gets a meaningful
        # name instead of a 1-word stub.
        if len(title) < 6:
            enriched = StoryGenerator._clean_fallback_title(
                ir.action_phrase or ir.source_text or ""
            )
            if enriched and len(enriched) > len(title):
                return enriched[:1].upper() + enriched[1:]
        return title[:1].upper() + title[1:] if title else title
