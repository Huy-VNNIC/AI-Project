"""
Use case parser module.
Parser cho Use Case document format.
Detect headers (Actor, Main Flow, Precondition...) rồi map vào schema.
"""

import re
from ..models.canonical import CanonicalRequirement


# Map section header → schema field
SECTION_MAP = {
    "actor":             "actor",
    "actors":            "actor",
    "primary actor":     "actor",
    "precondition":      "conditions",
    "preconditions":     "conditions",
    "pre-condition":     "conditions",
    "main flow":         "main_flow",
    "basic flow":        "main_flow",
    "main success":      "main_flow",
    "normal flow":       "main_flow",
    "postcondition":     "expected",
    "post-condition":    "expected",
    "success guarantee": "expected",
    "alternative flow":  "alt_flow",
    "alternate flow":    "alt_flow",
    "exception flow":    "alt_flow",
    "description":       "description",
    "goal":              "description",
}

HEADER_PATTERN = re.compile(
    r"^(?P<header>[A-Za-z][A-Za-z\s\-]{0,30})\s*:\s*(?P<value>.*)$",
    re.MULTILINE
)


def parse_use_case(text: str) -> list[CanonicalRequirement]:
    """
    Parse use case document → list CanonicalRequirement.
    Một document có thể chứa nhiều use cases.
    """
    use_case_blocks = _split_use_cases(text)
    results = []

    for block in use_case_blocks:
        req = _parse_single_use_case(block)
        if req and req.is_valid():
            results.append(req)

    return results


def _split_use_cases(text: str) -> list[str]:
    """Tách text thành các use case block riêng biệt."""
    # Split tại "Use Case X:" hoặc "UC-XXX:"
    uc_split = re.split(r"\n(?=Use Case\s*[\d\w]+\s*:|UC-\d+\s*:)", text, flags=re.IGNORECASE)
    if len(uc_split) > 1:
        return [b.strip() for b in uc_split if b.strip()]

    # Fallback: tách theo dòng trống lớn
    blocks = re.split(r"\n{3,}", text)
    return [b.strip() for b in blocks if b.strip()]


def _parse_single_use_case(block: str) -> CanonicalRequirement | None:
    """Parse 1 use case block → CanonicalRequirement."""
    sections = _extract_sections(block)

    actor      = sections.get("actor", "user").strip() or "user"
    conditions = _parse_conditions(sections.get("conditions", ""))
    expected   = sections.get("expected", "").strip()
    main_flow  = sections.get("main_flow", "")
    description= sections.get("description", "")

    action, objects = _extract_action_from_flow(main_flow or description or block)

    if not action:
        return None

    return CanonicalRequirement(
        actor=actor.lower(),
        action=action,
        objects=objects,
        conditions=conditions,
        expected=expected or f"Use case completes successfully",
        req_type=_classify(block),
        source_format="use_case",
        raw_text=block[:300],
    )


def _extract_sections(block: str) -> dict:
    """Extract các section từ block text."""
    sections = {}
    current_key = None
    current_lines = []

    for line in block.splitlines():
        line = line.strip()
        if not line:
            continue

        # Check nếu line là header
        header_match = re.match(r"^([A-Za-z][A-Za-z\s\-]{0,30})\s*:\s*(.*)$", line)
        if header_match:
            # Lưu section trước
            if current_key:
                sections[current_key] = " ".join(current_lines).strip()

            raw_header = header_match.group(1).strip().lower()
            mapped = SECTION_MAP.get(raw_header)
            if mapped:
                current_key = mapped
                current_lines = [header_match.group(2).strip()]
            else:
                current_key = None
                current_lines = []
        elif current_key:
            current_lines.append(line)

    # Lưu section cuối
    if current_key:
        sections[current_key] = " ".join(current_lines).strip()

    return sections


def _parse_conditions(text: str) -> list[str]:
    if not text:
        return []
    # Tách bởi số thứ tự "1." hoặc dấu bullet
    items = re.split(r"\d+\.\s+|\•\s+|\-\s+", text)
    return [i.strip() for i in items if i.strip()][:3]


def _extract_action_from_flow(flow_text: str) -> tuple[str, list[str]]:
    """Lấy action chính từ Main Flow text."""
    if not flow_text:
        return "", []

    # Lấy step đầu tiên (thường là action chính)
    first_line = flow_text.splitlines()[0] if flow_text.splitlines() else flow_text
    first_line = re.sub(r"^\d+\.\s+", "", first_line).strip()

    tokens = first_line.lower().split()
    if not tokens:
        return "", []

    # Tìm verb đầu tiên
    action = tokens[0]
    objects = tokens[1:4] if len(tokens) > 1 else []

    return action, objects


def _classify(text: str) -> str:
    lower = text.lower()
    if any(w in lower for w in ["password", "login", "auth", "secure", "token"]):
        return "security"
    if any(w in lower for w in ["performance", "load", "response time", "latency"]):
        return "performance"
    return "functional"
