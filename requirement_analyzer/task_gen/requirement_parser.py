"""
Requirement Parser - Extract structured information from requirements using NLP
Phase 1 of AI Test Case Generator v2
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ActorType(Enum):
    SYSTEM = "system"
    USER = "user"
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"
    EXTERNAL = "external"
    UNKNOWN = "unknown"


class ActionType(Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    SEARCH = "search"
    VALIDATE = "validate"
    SEND = "send"
    RECEIVE = "receive"
    DISPLAY = "display"
    CHECK = "check"
    MANAGE = "manage"
    TRACK = "track"
    PREVENT = "prevent"
    ALERT = "alert"
    INTEGRATE = "integrate"
    EXPORT = "export"
    IMPORT = "import"
    UNKNOWN = "unknown"


@dataclass
class Constraint:
    """Represents a constraint in requirement"""
    type: str  # "time", "range", "condition", "rule"
    value: str
    operator: Optional[str] = None  # "<=", ">=", "==", "!=", "in", "not_in"

    def __repr__(self):
        if self.operator:
            return f"{self.operator} {self.value}"
        return str(self.value)


@dataclass
class RequirementObject:
    """Structured requirement object"""
    original_text: str
    actor: str
    actor_type: ActorType
    action: str
    action_type: ActionType
    object_entity: str
    constraints: List[Constraint]
    domain: str
    priority: str = "MEDIUM"
    risk_level: str = "LOW"
    parse_confidence: float = 0.0
    raw_extraction: Dict = None

    def __repr__(self):
        return f"""
RequirementObject:
  Original: {self.original_text}
  Actor: {self.actor} ({self.actor_type.value})
  Action: {self.action} ({self.action_type.value})
  Object: {self.object_entity}
  Constraints: {self.constraints}
  Domain: {self.domain}
  Priority: {self.priority}
  Risk: {self.risk_level}
  Confidence: {self.parse_confidence:.1%}
"""


class RequirementParser:
    """Parse requirements into structured objects using pattern matching + NLP"""

    def __init__(self):
        self.domain_keywords = {
            "healthcare": ["patient", "doctor", "appointment", "prescription", "allergy", "insurance", "medical", "hospital", "diagnosis", "exam"],
            "banking": ["account", "transaction", "balance", "transfer", "login", "card", "payment", "deposit"],
            "e-commerce": ["product", "order", "cart", "checkout", "delivery", "payment", "customer"],
        }

        self.action_patterns = {
            ActionType.CREATE: ["tạo", "tạo mới", "tạo", "khởi tạo", "sinh", "tạo ra"],
            ActionType.READ: ["đọc", "xem", "hiển thị", "hiển", "chiếu", "truy cập", "truy"],
            ActionType.UPDATE: ["cập nhật", "chỉnh sửa", "sửa", "thay đổi", "cập"],
            ActionType.DELETE: ["xóa", "xóa", "loại bỏ", "xóa"],
            ActionType.VALIDATE: ["xác thực", "kiểm tra", "kiểm", "xác", "xác nhận"],
            ActionType.SEND: ["gửi", "gửi", "gửi đi", "thông báo"],
            ActionType.SEARCH: ["tìm", "tìm kiếm", "tìm", "lọc"],
            ActionType.ALERT: ["cảnh báo", "cảnh", "nhắc nhở", "nhắc", "thông báo"],
            ActionType.TRACK: ["theo dõi", "theo", "giám sát"],
            ActionType.MANAGE: ["quản lý", "quản", "điều quản"],
            ActionType.CHECK: ["kiểm tra", "kiểm", "checked"],
            ActionType.DISPLAY: ["hiển thị", "hiển", "chiếu"],
            ActionType.PREVENT: ["ngăn chặn", "ngăn", "cấm", "không cho phép"],
            ActionType.INTEGRATE: ["tích hợp", "tích", "kết nối"],
        }

        # Constraint patterns
        self.constraint_patterns = [
            (r"(\d+)\s*(ngày|day|days|d)", "time_days"),
            (r"(\d+)\s*(giờ|hour|hours|h)", "time_hours"),
            (r"(\d+)%", "percentage"),
            (r"([≤<>≥])\s*(\d+)", "comparison"),
            (r"từ\s*(\d+)\s*đến\s*(\d+)", "range"),
            (r"trước\s*(\d+)\s*(ngày|giờ)", "before_constraint"),
            (r"sau\s*(\d+)\s*(ngày|giờ)", "after_constraint"),
        ]

    def parse(self, requirement: str) -> RequirementObject:
        """
        Main parsing function
        Input: raw requirement text
        Output: structured RequirementObject
        """
        requirement = requirement.strip()

        # Extract domain
        domain = self._extract_domain(requirement)

        # Extract actor
        actor, actor_type = self._extract_actor(requirement)

        # Extract action
        action, action_type = self._extract_action(requirement)

        # Extract object
        obj = self._extract_object(requirement, action)

        # Extract constraints
        constraints = self._extract_constraints(requirement)

        # Determine priority and risk
        priority = self._determine_priority(requirement, domain)
        risk_level = self._determine_risk(requirement, domain)

        # Calculate confidence
        confidence = self._calculate_confidence(
            requirement, actor_type, action_type, constraints, domain
        )

        return RequirementObject(
            original_text=requirement,
            actor=actor,
            actor_type=actor_type,
            action=action,
            action_type=action_type,
            object_entity=obj,
            constraints=constraints,
            domain=domain,
            priority=priority,
            risk_level=risk_level,
            parse_confidence=confidence,
        )

    def _extract_domain(self, text: str) -> str:
        """Extract domain from text"""
        text_lower = text.lower()
        for domain, keywords in self.domain_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return domain
        return "general"

    def _extract_actor(self, text: str) -> Tuple[str, ActorType]:
        """Extract actor (who performs action)"""
        text_lower = text.lower()

        # Pattern matching for Vietnamese
        patterns = {
            ActorType.PATIENT: ["bệnh nhân", "người dùng", "khách hàng", "user"],
            ActorType.DOCTOR: ["bác sĩ", "y bác sĩ", "bs", "doctor"],
            ActorType.ADMIN: ["quản trị viên", "admin", "người quản lý"],
            ActorType.SYSTEM: ["hệ thống", "system", "app"],
            ActorType.USER: ["người dùng", "user", "người"],
        }

        for actor_type, keywords in patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return keyword, actor_type

        # Default: assume system if not specified
        return "System", ActorType.SYSTEM

    def _extract_action(self, text: str) -> Tuple[str, ActionType]:
        """Extract action verb"""
        text_lower = text.lower()

        for action_type, patterns in self.action_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return pattern, action_type

        return "perform", ActionType.UNKNOWN

    def _extract_object(self, text: str, action: str) -> str:
        """Extract object of action"""
        # Extract noun after action verb
        words = text.split()

        # Find keyword position
        action_lower = action.lower()
        for i, word in enumerate(words):
            if action_lower in word.lower():
                # Get next few words as object
                if i + 1 < len(words):
                    obj_words = []
                    for j in range(i + 1, min(i + 4, len(words))):
                        if words[j] not in ["với", "và", "hoặc", "để", "sao cho"]:
                            obj_words.append(words[j])
                        else:
                            break
                    if obj_words:
                        return " ".join(obj_words)

        # Fallback: extract entities
        entities = re.findall(r"(?:tài khoản|lịch hẹn|bệnh nhân|đơn thuốc|dữ liệu|file)\s+(\w+)", text)
        if entities:
            return entities[0]

        return "data"

    def _extract_constraints(self, text: str) -> List[Constraint]:
        """Extract constraints and conditions"""
        constraints = []

        for pattern, constraint_type in self.constraint_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                constraint = Constraint(
                    type=constraint_type,
                    value=match.group(0),
                    operator=self._extract_operator(text, match.start()),
                )
                constraints.append(constraint)

        return constraints

    def _extract_operator(self, text: str, pos: int) -> Optional[str]:
        """Extract operator near position"""
        before = text[max(0, pos - 10) : pos]
        if "≤" in before or "<=" in before:
            return "<="
        if "≥" in before or ">=" in before:
            return ">="
        if "<" in before:
            return "<"
        if ">" in before:
            return ">"
        if "=" in before:
            return "=="
        return None

    def _determine_priority(self, text: str, domain: str) -> str:
        """Determine requirement priority"""
        text_lower = text.lower()

        if "phải" in text_lower or "must" in text_lower:
            return "HIGH"
        if "nên" in text_lower or "should" in text_lower:
            return "MEDIUM"
        if "có thể" in text_lower or "could" in text_lower:
            return "LOW"

        return "MEDIUM"

    def _determine_risk(self, text: str, domain: str) -> str:
        """Determine risk level based on keywords"""
        text_lower = text.lower()

        high_risk_keywords = [
            "dị ứng",
            "tương tác thuốc",
            "bảo mật",
            "xác thực",
            "tiền",
            "thanh toán",
            "allergy",
            "interaction",
            "security",
            "payment",
        ]

        for keyword in high_risk_keywords:
            if keyword in text_lower:
                return "HIGH"

        if domain == "healthcare":
            return "MEDIUM"

        return "LOW"

    def _calculate_confidence(
        self, text: str, actor_type: ActorType, action_type: ActionType, constraints: List, domain: str
    ) -> float:
        """
        Calculate parse confidence
        Based on: clarity, specificity, constraints, domain knowledge
        """
        confidence = 0.5

        # Actor clarity
        if actor_type != ActorType.UNKNOWN:
            confidence += 0.15
        else:
            confidence -= 0.1

        # Action clarity
        if action_type != ActionType.UNKNOWN:
            confidence += 0.15
        else:
            confidence -= 0.1

        # Constraint specificity
        if len(constraints) > 0:
            confidence += 0.15
        if len(constraints) >= 2:
            confidence += 0.05

        # Domain specificity
        if domain != "general":
            confidence += 0.15

        # Text clarity (length && structure)
        if len(text.split()) > 5:
            confidence += 0.05
        if len(constraints) > 0 and len(text.split()) > 8:
            confidence += 0.05

        # Cap at 1.0
        return min(max(confidence, 0.0), 1.0)


# Test
if __name__ == "__main__":
    parser = RequirementParser()

    test_requirements = [
        "Hệ thống phải cho phép đặt lịch khám trước 30 ngày",
        "Hệ thống phải cảnh báo dị ứng thuốc khi tiếp nhận",
        "Bác sĩ phải có thể xem kết quả xét nghiệm online",
        "Hệ thống phải quản lý hồ sơ bệnh nhân với thông tin đầy đủ",
    ]

    for req in test_requirements:
        parsed = parser.parse(req)
        print(parsed)
        print("-" * 80)
