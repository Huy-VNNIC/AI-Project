"""
Canonical data models dùng xuyên suốt toàn bộ pipeline.
Mọi parser đều phải xuất ra CanonicalRequirement.
Mọi output đều là TestCase.
"""

from dataclasses import dataclass, field
from typing import Literal
import uuid


@dataclass
class CanonicalRequirement:
    """
    Schema chung cho tất cả requirement, bất kể format đầu vào.
    Parser nào cũng phải map về đây trước khi đưa vào rule engine.
    """
    actor: str                          # "user", "admin", "system"
    action: str                         # động từ đã lemmatize: "login", "submit"
    objects: list[str] = field(default_factory=list)      # ["email", "password"]
    conditions: list[str] = field(default_factory=list)   # ["if token valid"]
    expected: str = ""                  # "system returns 200 OK"
    req_type: str = "functional"        # functional | security | performance
    source_format: str = "free_text"    # free_text | user_story | use_case | excel
    raw_text: str = ""                  # text gốc để debug
    id: str = field(default_factory=lambda: f"REQ_{uuid.uuid4().hex[:6].upper()}")

    def is_valid(self) -> bool:
        """Requirement hợp lệ khi ít nhất có action."""
        return bool(self.action and self.action.strip())


@dataclass
class TestCase:
    """
    Một test case hoàn chỉnh sinh ra từ 1 CanonicalRequirement.
    """
    req_id: str                         # link về requirement gốc
    title: str
    precondition: str
    steps: list[str]
    expected_result: str
    test_type: str                      # positive | negative | edge | security
    priority: str                       # high | medium | low
    id: str = field(default_factory=lambda: f"TC_{uuid.uuid4().hex[:6].upper()}")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "req_id": self.req_id,
            "title": self.title,
            "precondition": self.precondition,
            "steps": " | ".join(self.steps),
            "expected_result": self.expected_result,
            "test_type": self.test_type,
            "priority": self.priority,
        }
