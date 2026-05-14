"""
ACGenerator
===========

Intent-driven Acceptance Criteria generator.

For each canonical intent we know *what behaviors must be verified* —
not as fixed text, but as a list of **scenario types** (happy, invalid,
permission, external_failure, idempotency, …).  Each scenario is then
rendered into a Given/When/Then triple, parameterized by the IR slots
(actor, entity, channel, …).

Compared to a flat template lookup, this approach yields AC that varies
naturally across stories — a "pay" story gets an idempotency AC, a
"login" story gets a brute-force lockout AC, a "manage" story gets full
CRUD coverage — without any hand-written if/else trees in the caller.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from .ir import StoryIR


# Each scenario is a tuple (kind, render_vi, render_en).
ScenarioRenderer = Callable[[StoryIR], "ACTriple"]


@dataclass
class ACTriple:
    given: str
    when: str
    then: str
    priority: str = "Medium"      # Critical / High / Medium / Low
    kind: str = "generic"


# ── Scenario library ──────────────────────────────────────────────────────
# All renderers receive the IR and produce an ``ACTriple``. They never
# read raw text — only IR slots — which keeps generation deterministic.

def _entity_vi(ir: StoryIR) -> str:
    from .generator import ENTITY_PHRASE_VI
    return ENTITY_PHRASE_VI.get(ir.entity or "", "thông tin")


def _entity_en(ir: StoryIR) -> str:
    from .generator import ENTITY_PHRASE_EN
    return ENTITY_PHRASE_EN.get(ir.entity or "", "the resource")


def _verb_vi(ir: StoryIR) -> str:
    from .generator import INTENT_VERB_VI
    return INTENT_VERB_VI.get(ir.intent or "", "thực hiện thao tác")


def _verb_en(ir: StoryIR) -> str:
    from .generator import INTENT_VERB_EN
    return INTENT_VERB_EN.get(ir.intent or "", "perform the action")


# Each entry: scenario kind → (vi_renderer, en_renderer, priority)
SCENARIO_LIBRARY: Dict[str, tuple] = {
    "happy": (
        lambda ir: ACTriple(
            f"{ir.actor or 'Người dùng'} đã đăng nhập với dữ liệu hợp lệ",
            f"Thực hiện {_verb_vi(ir)} {_entity_vi(ir)}".strip(),
            "Hệ thống xử lý thành công và phản hồi rõ ràng trong vòng 3 giây",
            "High", "happy",
        ),
        lambda ir: ACTriple(
            f"{ir.actor or 'User'} is logged in with valid data",
            f"Performs {_verb_en(ir)} {_entity_en(ir)}".strip(),
            "System processes successfully and responds within 3 seconds",
            "High", "happy",
        ),
    ),
    "invalid_input": (
        lambda ir: ACTriple(
            "Dữ liệu đầu vào không hợp lệ hoặc thiếu trường bắt buộc",
            "Người dùng gửi yêu cầu",
            "Hệ thống từ chối thao tác và hiển thị thông báo lỗi cụ thể trên đúng trường bị lỗi",
            "Medium", "invalid_input",
        ),
        lambda ir: ACTriple(
            "Input is invalid or required fields are missing",
            "User submits the request",
            "System rejects the action and shows a specific error on the offending field",
            "Medium", "invalid_input",
        ),
    ),
    "permission": (
        lambda ir: ACTriple(
            "Người dùng không có quyền thực hiện chức năng",
            "Cố gắng truy cập hoặc thao tác trên tài nguyên",
            "Hệ thống trả về HTTP 403 và ghi log sự kiện truy cập trái phép",
            "High", "permission",
        ),
        lambda ir: ACTriple(
            "User lacks the required permission",
            "Attempts to access or operate on the resource",
            "System returns HTTP 403 and logs the unauthorized attempt",
            "High", "permission",
        ),
    ),
    "system_error": (
        lambda ir: ACTriple(
            "Lỗi hệ thống xảy ra (mất kết nối DB, dịch vụ ngoài lỗi, timeout)",
            "Người dùng thực hiện thao tác",
            "Hệ thống hiển thị thông báo lỗi thân thiện, không lộ stack trace, cho phép thử lại",
            "Medium", "system_error",
        ),
        lambda ir: ACTriple(
            "A system-level error occurs (DB outage, external service down, timeout)",
            "User performs the action",
            "System shows a friendly error, hides stack traces, and offers a retry option",
            "Medium", "system_error",
        ),
    ),
    "audit_log": (
        lambda ir: ACTriple(
            "Thao tác làm thay đổi dữ liệu quan trọng",
            "Sau khi hoàn tất thao tác",
            "Hệ thống ghi audit log gồm user, thời điểm và nội dung thay đổi",
            "Medium", "audit_log",
        ),
        lambda ir: ACTriple(
            "Action mutates critical data",
            "On completion",
            "System writes an audit log entry with user, timestamp and change details",
            "Medium", "audit_log",
        ),
    ),
    # Domain-specific scenarios -----------------------------------------------
    "login_lockout": (
        lambda ir: ACTriple(
            "Người dùng nhập sai mật khẩu 5 lần liên tiếp",
            "Lần thử thứ 6",
            "Tài khoản bị khóa tạm thời 15 phút và sự kiện được ghi vào audit log",
            "High", "login_lockout",
        ),
        lambda ir: ACTriple(
            "5 consecutive failed login attempts from the same account",
            "On the 6th attempt",
            "Account is locked for 15 minutes and the event is written to the audit log",
            "High", "login_lockout",
        ),
    ),
    "register_duplicate": (
        lambda ir: ACTriple(
            "Email đã tồn tại trong hệ thống",
            "Người dùng nhấn Đăng ký",
            'Hệ thống hiển thị "Email đã được sử dụng" kèm gợi ý đăng nhập hoặc đặt lại mật khẩu',
            "High", "register_duplicate",
        ),
        lambda ir: ACTriple(
            "Email already exists in the system",
            "User clicks Register",
            'System displays "Email already in use" with links to login or reset password',
            "High", "register_duplicate",
        ),
    ),
    "payment_idempotency": (
        lambda ir: ACTriple(
            "Mạng bị ngắt giữa chừng giao dịch thanh toán",
            "Giao dịch chưa hoàn tất",
            "Hệ thống đảm bảo idempotent: không trừ tiền hai lần, giao dịch rollback an toàn",
            "Critical", "payment_idempotency",
        ),
        lambda ir: ACTriple(
            "Network drops mid-transaction during payment",
            "Transaction is incomplete",
            "System is idempotent: no double charge, transaction safely rolled back",
            "Critical", "payment_idempotency",
        ),
    ),
    "payment_decline": (
        lambda ir: ACTriple(
            "Thẻ hết hạn hoặc không đủ số dư",
            "Người dùng xác nhận thanh toán",
            "Thông báo lỗi cụ thể, đơn hàng giữ nguyên, không trừ tiền",
            "High", "payment_decline",
        ),
        lambda ir: ACTriple(
            "Card is expired or has insufficient funds",
            "User confirms payment",
            "Specific error displayed, order unchanged, no charge made",
            "High", "payment_decline",
        ),
    ),
    "search_pagination": (
        lambda ir: ACTriple(
            f"Có 50+ {_entity_vi(ir)} trong cơ sở dữ liệu",
            "Người dùng nhập từ khóa và nhấn Tìm kiếm",
            "Kết quả hiển thị trong vòng 2 giây, tối đa 20 kết quả mỗi trang, có phân trang",
            "High", "search_pagination",
        ),
        lambda ir: ACTriple(
            f"50+ {_entity_en(ir)} exist in the database",
            "User enters a keyword and clicks Search",
            "Results within 2 seconds, max 20 per page, with pagination controls",
            "High", "search_pagination",
        ),
    ),
    "delete_confirm": (
        lambda ir: ACTriple(
            f"Người dùng nhấn nút Xóa trên một {_entity_vi(ir)}",
            "Hộp thoại xác nhận hiển thị",
            'Nếu xác nhận "Có": bản ghi bị xóa vĩnh viễn; nếu "Hủy": không có thay đổi',
            "High", "delete_confirm",
        ),
        lambda ir: ACTriple(
            f"User clicks Delete on a {_entity_en(ir)}",
            "Confirmation dialog appears",
            'If user confirms "Yes": record is permanently deleted; if "Cancel": no change',
            "High", "delete_confirm",
        ),
    ),
    "external_api_failure": (
        lambda ir: ACTriple(
            "Dịch vụ bên thứ ba (gateway/API) không phản hồi",
            "Hệ thống gọi tới dịch vụ ngoài",
            "Hệ thống áp dụng circuit breaker, trả về cached response hoặc lỗi thân thiện và retry với backoff",
            "High", "external_api_failure",
        ),
        lambda ir: ACTriple(
            "Third-party service (gateway/API) is unresponsive",
            "System invokes the external dependency",
            "Circuit breaker activates, returns cached response or friendly error, and retries with backoff",
            "High", "external_api_failure",
        ),
    ),
    "notification_delivery": (
        lambda ir: ACTriple(
            "Sự kiện kích hoạt thông báo đã xảy ra",
            "Hệ thống tạo và gửi thông báo",
            "Thông báo được gửi tới đúng người nhận trong vòng 30 giây; thất bại được ghi log và retry tối đa 3 lần",
            "Medium", "notification_delivery",
        ),
        lambda ir: ACTriple(
            "A notification-triggering event has occurred",
            "System creates and sends the notification",
            "Notification is delivered to the correct recipient within 30 seconds; failures are logged and retried up to 3 times",
            "Medium", "notification_delivery",
        ),
    ),
    "file_validation": (
        lambda ir: ACTriple(
            "Tệp vượt quá 10 MB hoặc sai định dạng cho phép",
            "Người dùng nhấn Tải lên",
            "Hệ thống từ chối tệp và hiển thị thông báo cụ thể về kích thước/định dạng",
            "Medium", "file_validation",
        ),
        lambda ir: ACTriple(
            "File exceeds 10 MB or has an unsupported format",
            "User clicks Upload",
            "System rejects the file and shows a specific size/format error",
            "Medium", "file_validation",
        ),
    ),
    "report_empty_data": (
        lambda ir: ACTriple(
            "Không có dữ liệu trong khoảng thời gian được chọn",
            "Người dùng nhấn Tạo báo cáo",
            'Hệ thống hiển thị "Không có dữ liệu" mà không phát sinh lỗi',
            "Medium", "report_empty_data",
        ),
        lambda ir: ACTriple(
            "No data exists in the selected date range",
            "User clicks Generate Report",
            '"No data available" message is displayed; no system error thrown',
            "Medium", "report_empty_data",
        ),
    ),
    "clinical_safety": (
        lambda ir: ACTriple(
            "Bệnh nhân có dị ứng / tương tác thuốc đã ghi nhận trong hồ sơ",
            "Bác sĩ kê đơn thuốc xung đột",
            "Hệ thống cảnh báo ngay lập tức và yêu cầu xác nhận chủ động trước khi lưu",
            "Critical", "clinical_safety",
        ),
        lambda ir: ACTriple(
            "Patient has recorded allergies / drug interactions",
            "Doctor prescribes a conflicting medication",
            "System raises an immediate alert and requires explicit confirmation before saving",
            "Critical", "clinical_safety",
        ),
    ),
}


# Map intent → list of scenario kinds (in order of importance).
INTENT_SCENARIOS: Dict[str, List[str]] = {
    "register": ["happy", "register_duplicate", "invalid_input", "system_error"],
    "login":    ["happy", "invalid_input", "login_lockout", "system_error"],
    "logout":   ["happy", "system_error"],
    "authenticate": ["happy", "login_lockout", "permission", "system_error"],
    "book":     ["happy", "invalid_input", "permission", "external_api_failure", "audit_log"],
    "reserve":  ["happy", "invalid_input", "system_error"],
    "schedule": ["happy", "invalid_input", "system_error"],

    "create":   ["happy", "invalid_input", "permission", "audit_log"],
    "update":   ["happy", "invalid_input", "permission", "audit_log"],
    "delete":   ["delete_confirm", "permission", "audit_log", "system_error"],
    "view":     ["happy", "permission", "system_error"],
    "list":     ["happy", "permission", "system_error"],
    "search":   ["search_pagination", "happy", "system_error"],
    "filter":   ["happy", "search_pagination", "system_error"],

    "pay":       ["happy", "payment_decline", "payment_idempotency",
                  "external_api_failure", "audit_log"],
    "refund":    ["happy", "permission", "payment_idempotency", "audit_log"],
    "invoice":   ["happy", "invalid_input", "audit_log"],

    "manage":    ["happy", "invalid_input", "permission", "delete_confirm", "audit_log"],
    "approve":   ["happy", "permission", "audit_log", "system_error"],
    "assign":    ["happy", "permission", "audit_log"],
    "track":     ["happy", "permission", "system_error"],

    "diagnose":  ["happy", "clinical_safety", "permission", "audit_log"],
    "prescribe": ["happy", "clinical_safety", "permission", "audit_log"],
    "admit":     ["happy", "invalid_input", "permission", "audit_log"],
    "discharge": ["happy", "permission", "audit_log"],
    "operate":   ["happy", "permission", "audit_log", "clinical_safety"],

    "report":    ["happy", "report_empty_data", "permission"],
    "export":    ["happy", "permission", "system_error"],
    "import":    ["happy", "file_validation", "system_error"],
    "upload":    ["happy", "file_validation", "system_error"],
    "download":  ["happy", "permission", "system_error"],

    "notify":    ["notification_delivery", "system_error"],
    "send_email": ["notification_delivery", "system_error"],
    "send_sms":  ["notification_delivery", "system_error"],

    "encrypt":   ["happy", "permission", "audit_log"],
    "audit":     ["happy", "permission"],
    "backup":    ["happy", "system_error", "audit_log"],

    # default
    "unknown":   ["happy", "invalid_input", "permission", "system_error"],
}


class ACGenerator:
    """Generate Given/When/Then acceptance criteria from a ``StoryIR``."""

    def __init__(self, language: str = "vi", min_ac: int = 4, max_ac: int = 7) -> None:
        self.language = language
        self.min_ac = min_ac
        self.max_ac = max_ac

    def generate(self, ir: StoryIR) -> List[ACTriple]:
        scenarios = self._select_scenarios(ir)
        out: List[ACTriple] = []
        for kind in scenarios:
            triple = self._render(kind, ir)
            if triple is None:
                continue
            out.append(triple)
            if len(out) >= self.max_ac:
                break
        # Pad with the default-fallback chain if still under min_ac.
        if len(out) < self.min_ac:
            for kind in ("happy", "invalid_input", "permission",
                         "system_error", "audit_log"):
                if any(t.kind == kind for t in out):
                    continue
                triple = self._render(kind, ir)
                if triple:
                    out.append(triple)
                if len(out) >= self.min_ac:
                    break
        return out[: self.max_ac]

    # ── Internal ────────────────────────────────────────────────────────
    def _select_scenarios(self, ir: StoryIR) -> List[str]:
        scenarios = list(INTENT_SCENARIOS.get(ir.intent or "unknown",
                                              INTENT_SCENARIOS["unknown"]))

        # Behavioral signals can add scenarios that the intent table missed.
        if ir.has_payment and "payment_idempotency" not in scenarios:
            scenarios.append("payment_idempotency")
        if ir.has_external_api and "external_api_failure" not in scenarios:
            scenarios.append("external_api_failure")
        if ir.has_notification and "notification_delivery" not in scenarios:
            scenarios.append("notification_delivery")
        if ir.has_file_io and "file_validation" not in scenarios:
            scenarios.append("file_validation")
        if ir.needs_permission_check and "permission" not in scenarios:
            scenarios.insert(1, "permission")
        if ir.is_crud_bundle:
            for k in ("delete_confirm", "audit_log"):
                if k not in scenarios:
                    scenarios.append(k)

        # Deduplicate while preserving order.
        seen = set()
        deduped: List[str] = []
        for k in scenarios:
            if k not in seen:
                seen.add(k)
                deduped.append(k)
        return deduped

    def _render(self, kind: str, ir: StoryIR) -> Optional[ACTriple]:
        entry = SCENARIO_LIBRARY.get(kind)
        if entry is None:
            return None
        vi_render, en_render = entry[0], entry[1]
        return vi_render(ir) if self.language == "vi" else en_render(ir)
