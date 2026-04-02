"""
Pipeline orchestrator module.
Kết nối toàn bộ pipeline từ đầu đến cuối.
"""

import os
import sys

# Add parent dir to path forus importing
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from .input_processor  import extract_raw_text
from .format_detector  import detect_format
from .text_preprocessor import preprocess
from .normalizer       import normalize
from .test_generator   import generate_tests
from ..models.canonical import CanonicalRequirement, TestCase

from ..parsers.free_text_parser  import parse_free_text
from ..parsers.user_story_parser import parse_user_story
from ..parsers.use_case_parser   import parse_use_case
from ..parsers.excel_parser      import parse_excel


PARSER_MAP = {
    "free_text":  parse_free_text,
    "user_story": parse_user_story,
    "use_case":   parse_use_case,
    "excel":      parse_excel,
}


def run_pipeline(
    filepath: str,
    force_format: str | None = None,
) -> dict:
    """
    Run toàn bộ pipeline cho 1 file.

    Args:
        filepath:     đường dẫn file requirement
        force_format: ép buộc format (None = auto-detect)

    Returns:
        dict với keys: requirements, test_cases, summary, format_detected
    """

    # ── Step 1: Extract raw text ──
    raw_text = extract_raw_text(filepath)

    # ── Step 2: Detect format ──
    fmt = force_format or detect_format(filepath, raw_text)

    # ── Step 3: Preprocess (với Excel thì bỏ qua, parser đọc file trực tiếp) ──
    if fmt == "excel":
        clean_text = raw_text
        parser = PARSER_MAP["excel"]
        canonical_reqs = parser(filepath)           # Excel parser nhận filepath
    else:
        clean_text = preprocess(raw_text)
        parser = PARSER_MAP[fmt]
        canonical_reqs = parser(clean_text)         # Các parser khác nhận text

    # ── Step 4: Normalize ──
    canonical_reqs = [normalize(r) for r in canonical_reqs]
    canonical_reqs = [r for r in canonical_reqs if r.is_valid()]

    # ── Step 5: Generate test cases ──
    test_cases: list[TestCase] = []
    for req in canonical_reqs:
        test_cases.extend(generate_tests(req))

    # ── Step 6: Build summary ──
    summary = _build_summary(canonical_reqs, test_cases, fmt)

    return {
        "format_detected": fmt,
        "requirements":    [_req_to_dict(r) for r in canonical_reqs],
        "test_cases":      [tc.to_dict() for tc in test_cases],
        "summary":         summary,
        "_objects": {
            "requirements": canonical_reqs,
            "test_cases":   test_cases,
        }
    }


def run_pipeline_from_text(
    text: str,
    force_format: str = "free_text",
) -> dict:
    """
    Chạy pipeline từ raw text string (dùng cho API nếu không có file).
    """
    fmt = force_format
    clean_text = preprocess(text)
    parser = PARSER_MAP.get(fmt, parse_free_text)
    canonical_reqs = parser(clean_text)
    canonical_reqs = [normalize(r) for r in canonical_reqs]
    canonical_reqs = [r for r in canonical_reqs if r.is_valid()]

    test_cases = []
    for req in canonical_reqs:
        test_cases.extend(generate_tests(req))

    return {
        "format_detected": fmt,
        "requirements":    [_req_to_dict(r) for r in canonical_reqs],
        "test_cases":      [tc.to_dict() for tc in test_cases],
        "summary":         _build_summary(canonical_reqs, test_cases, fmt),
        "_objects": {
            "requirements": canonical_reqs,
            "test_cases":   test_cases,
        }
    }


def _build_summary(reqs, test_cases, fmt) -> dict:
    by_type = {}
    by_priority = {}
    by_req_type = {}

    for tc in test_cases:
        by_type[tc.test_type]       = by_type.get(tc.test_type, 0) + 1
        by_priority[tc.priority]    = by_priority.get(tc.priority, 0) + 1

    for r in reqs:
        by_req_type[r.req_type] = by_req_type.get(r.req_type, 0) + 1

    return {
        "input_format":          fmt,
        "total_requirements":    len(reqs),
        "total_test_cases":      len(test_cases),
        "avg_tests_per_req":     round(len(test_cases) / max(len(reqs), 1), 1),
        "test_cases_by_type":    by_type,
        "test_cases_by_priority":by_priority,
        "requirements_by_type":  by_req_type,
    }


def _req_to_dict(r: CanonicalRequirement) -> dict:
    return {
        "id":           r.id,
        "actor":        r.actor,
        "action":       r.action,
        "objects":      r.objects,
        "conditions":   r.conditions,
        "expected":     r.expected,
        "req_type":     r.req_type,
        "source_format":r.source_format,
        "raw_text":     r.raw_text[:150],
    }
