"""
Format detector module.
Tự động nhận biết format của requirement document.
Không cần người dùng khai báo — hệ thống tự detect.
"""

import re
from pathlib import Path


def detect_format(filepath: str, content: str) -> str:
    """
    Nhận biết format dựa trên extension + content patterns.

    Returns:
        "excel" | "user_story" | "use_case" | "free_text"
    """
    ext = Path(filepath).suffix.lower()

    # Excel/CSV: ưu tiên extension trước
    if ext in (".xlsx", ".csv", ".xls"):
        return "excel"

    # User Story: pattern "As a/an ..., I want ..."
    user_story_patterns = [
        r"As an?\s+\w[\w\s]*,\s+I want",
        r"As an?\s+\w[\w\s]*\s+I want",
        r"I want to\s+\w",
    ]
    for pat in user_story_patterns:
        if re.search(pat, content, re.IGNORECASE):
            return "user_story"

    # Use Case: có section headers đặc trưng
    use_case_patterns = [
        r"\bUse Case\b",
        r"\bActor\s*:",
        r"\bMain Flow\s*:",
        r"\bPrecondition\s*:",
        r"\bAlternative Flow\s*:",
        r"\bPostcondition\s*:",
        r"\bBasic Flow\s*:",
    ]
    match_count = sum(1 for pat in use_case_patterns if re.search(pat, content, re.IGNORECASE))
    if match_count >= 2:
        return "use_case"

    # Mặc định: free text
    return "free_text"
