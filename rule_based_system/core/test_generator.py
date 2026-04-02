"""
Test generator module - Rule Engine.
CanonicalRequirement → list[TestCase]
"""

from ..models.canonical import CanonicalRequirement, TestCase


# Map action → common input fields để gợi ý test data
ACTION_INPUT_MAP = {
    "login":     ["email", "password"],
    "register":  ["email", "password", "confirm password", "username"],
    "search":    ["search query", "keyword", "filter"],
    "submit":    ["form fields"],
    "upload":    ["file", "file size", "file type"],
    "payment":   ["card number", "expiry date", "cvv", "amount"],
    "enter":     [],   # fallback to objects
    "create":    [],
    "update":    [],
    "delete":    [],
}

# Input field → test data suggestions
FIELD_TEST_DATA = {
    "email": {
        "valid":    "user@example.com",
        "invalid":  "not-an-email",
        "empty":    "",
        "boundary": "a@b.c",
    },
    "password": {
        "valid":    "StrongPass@123",
        "invalid":  "weak",
        "empty":    "",
        "boundary": "A1!",          # min length
    },
    "username": {
        "valid":    "john_doe",
        "invalid":  "ab",           # too short
        "empty":    "",
        "boundary": "a" * 50,       # max length
    },
    "card number": {
        "valid":    "4111111111111111",
        "invalid":  "1234",
        "empty":    "",
        "boundary": "0000000000000000",
    },
    "amount": {
        "valid":    "100.00",
        "invalid":  "-50",
        "empty":    "",
        "boundary": "0.01",
    },
    "file": {
        "valid":    "document.pdf",
        "invalid":  "malware.exe",
        "empty":    "(no file selected)",
        "boundary": "file_10mb.pdf",
    },
    "search query": {
        "valid":    "laptop",
        "invalid":  "<script>alert(1)</script>",
        "empty":    "",
        "boundary": "a" * 255,
    },
}

DEFAULT_FIELD_DATA = {
    "valid":    "valid input",
    "invalid":  "invalid input",
    "empty":    "",
    "boundary": "boundary value",
}

PRIORITY_MAP = {
    "security":    "high",
    "functional":  "medium",
    "performance": "medium",
}


def generate_tests(req: CanonicalRequirement) -> list[TestCase]:
    """
    Entry point chính.
    Sinh toàn bộ test cases từ 1 CanonicalRequirement.
    """
    tests: list[TestCase] = []

    tests.append(_positive_test(req))
    tests.extend(_negative_tests(req))
    tests.extend(_edge_tests(req))

    if req.conditions:
        tests.extend(_condition_tests(req))

    if req.req_type == "security":
        tests.extend(_security_tests(req))

    if req.req_type == "performance":
        tests.append(_performance_test(req))

    return tests


# ─────────────────────────── POSITIVE TEST ───────────────────────────

def _positive_test(req: CanonicalRequirement) -> TestCase:
    """Happy path — tất cả input hợp lệ."""
    input_fields = _get_input_fields(req)
    steps = _build_steps(req, input_fields, "valid")

    return TestCase(
        req_id=req.id,
        title=f"[Positive] {_title(req)} with valid inputs",
        precondition=_precondition(req),
        steps=steps,
        expected_result=req.expected or f"System successfully {req.action}s {_obj_str(req)}",
        test_type="positive",
        priority=PRIORITY_MAP.get(req.req_type, "medium"),
    )


# ─────────────────────────── NEGATIVE TESTS ───────────────────────────

def _negative_tests(req: CanonicalRequirement) -> list[TestCase]:
    """Sinh negative test cho mỗi input field."""
    tests = []
    input_fields = _get_input_fields(req)

    if not input_fields:
        # Không có input cụ thể → sinh 1 generic negative
        tests.append(TestCase(
            req_id=req.id,
            title=f"[Negative] {_title(req)} with invalid data",
            precondition=_precondition(req),
            steps=[f"Attempt to {req.action} {_obj_str(req)} with invalid/unauthorized data"],
            expected_result="System shows appropriate error message",
            test_type="negative",
            priority="medium",
        ))
        return tests

    for field in input_fields:
        data = FIELD_TEST_DATA.get(field, DEFAULT_FIELD_DATA)
        tests.append(TestCase(
            req_id=req.id,
            title=f"[Negative] {_title(req)} — invalid {field}",
            precondition=_precondition(req),
            steps=[
                f"Navigate to {req.action} page",
                f"Enter invalid {field}: '{data['invalid']}'",
                f"Submit/proceed",
            ],
            expected_result=f"System shows error: invalid {field}",
            test_type="negative",
            priority="high" if req.req_type == "security" else "medium",
        ))

    return tests


# ─────────────────────────── EDGE CASES ───────────────────────────

def _edge_tests(req: CanonicalRequirement) -> list[TestCase]:
    """Empty input và boundary values."""
    tests = []
    input_fields = _get_input_fields(req)

    for field in input_fields[:2]:   # giới hạn 2 fields để không spam
        data = FIELD_TEST_DATA.get(field, DEFAULT_FIELD_DATA)

        # Empty
        tests.append(TestCase(
            req_id=req.id,
            title=f"[Edge] {_title(req)} — empty {field}",
            precondition=_precondition(req),
            steps=[
                f"Navigate to {req.action} page",
                f"Leave {field} empty",
                f"Submit/proceed",
            ],
            expected_result=f"System shows required field error for {field}",
            test_type="edge",
            priority="medium",
        ))

        # Boundary
        tests.append(TestCase(
            req_id=req.id,
            title=f"[Edge] {_title(req)} — boundary {field}",
            precondition=_precondition(req),
            steps=[
                f"Navigate to {req.action} page",
                f"Enter boundary value for {field}: '{data['boundary']}'",
                f"Submit/proceed",
            ],
            expected_result=f"System handles boundary value correctly",
            test_type="edge",
            priority="low",
        ))

    return tests


# ─────────────────────────── CONDITION TESTS ───────────────────────────

def _condition_tests(req: CanonicalRequirement) -> list[TestCase]:
    """Test khi condition satisfied và condition violated."""
    tests = []

    for cond in req.conditions:
        # Condition satisfied
        tests.append(TestCase(
            req_id=req.id,
            title=f"[Condition] {_title(req)} — condition met: '{cond[:50]}'",
            precondition=f"Ensure condition is met: {cond}",
            steps=[
                f"Set up: {cond}",
                f"Execute: {req.action} {_obj_str(req)}",
            ],
            expected_result=req.expected or "Action completes successfully",
            test_type="positive",
            priority="high",
        ))

        # Condition violated
        tests.append(TestCase(
            req_id=req.id,
            title=f"[Condition] {_title(req)} — condition NOT met: '{cond[:50]}'",
            precondition=f"Ensure condition is NOT met: {cond}",
            steps=[
                f"Set up without condition: {cond}",
                f"Attempt to: {req.action} {_obj_str(req)}",
            ],
            expected_result="System blocks action or shows appropriate message",
            test_type="negative",
            priority="high",
        ))

    return tests


# ─────────────────────────── SECURITY TESTS ───────────────────────────

def _security_tests(req: CanonicalRequirement) -> list[TestCase]:
    """Thêm security test cases cho security requirements."""
    tests = []

    # SQL Injection
    tests.append(TestCase(
        req_id=req.id,
        title=f"[Security] {_title(req)} — SQL injection attempt",
        precondition=_precondition(req),
        steps=[
            "Navigate to the relevant input form",
            "Enter SQL injection payload: ' OR '1'='1",
            "Submit the form",
        ],
        expected_result="System sanitizes input, shows error or rejects request. No data exposed.",
        test_type="security",
        priority="high",
    ))

    # XSS
    tests.append(TestCase(
        req_id=req.id,
        title=f"[Security] {_title(req)} — XSS attempt",
        precondition=_precondition(req),
        steps=[
            "Navigate to the relevant input form",
            "Enter XSS payload: <script>alert('xss')</script>",
            "Submit the form",
        ],
        expected_result="System escapes or rejects malicious script. No script executes.",
        test_type="security",
        priority="high",
    ))

    # Brute force (if login-related)
    if req.action in ("login", "authenticate"):
        tests.append(TestCase(
            req_id=req.id,
            title=f"[Security] {_title(req)} — brute force attempt",
            precondition="System is accessible",
            steps=[
                "Attempt login with wrong password 10+ times",
                "Check system response after repeated failures",
            ],
            expected_result="System locks account or introduces delay after N failed attempts",
            test_type="security",
            priority="high",
        ))

    return tests


# ─────────────────────────── PERFORMANCE TEST ───────────────────────────

def _performance_test(req: CanonicalRequirement) -> TestCase:
    return TestCase(
        req_id=req.id,
        title=f"[Performance] {_title(req)} — response time under load",
        precondition="System is under normal load (50 concurrent users)",
        steps=[
            f"Execute {req.action} {_obj_str(req)} with 50 concurrent requests",
            "Measure response time",
        ],
        expected_result="Response time < 3 seconds for 95th percentile",
        test_type="performance",
        priority="medium",
    )


# ─────────────────────────── HELPERS ───────────────────────────

def _get_input_fields(req: CanonicalRequirement) -> list[str]:
    """Lấy danh sách input fields từ action map hoặc objects."""
    fields = ACTION_INPUT_MAP.get(req.action, [])
    if not fields:
        # Dùng objects của requirement
        fields = req.objects[:3]
    return fields


def _build_steps(req: CanonicalRequirement, fields: list[str], data_type: str) -> list[str]:
    """Sinh steps cho test case."""
    steps = [f"Navigate to {req.action} page / feature"]
    for field in fields:
        data = FIELD_TEST_DATA.get(field, DEFAULT_FIELD_DATA)
        steps.append(f"Enter {data_type} {field}: '{data[data_type]}'")
    steps.append(f"Submit / Execute {req.action}")
    return steps


def _precondition(req: CanonicalRequirement) -> str:
    if req.conditions:
        return "; ".join(req.conditions[:2])
    actor_map = {
        "user":   "User is registered and on the login/home page",
        "admin":  "Admin is logged in with admin privileges",
        "guest":  "User is not logged in",
        "system": "System is running and accessible",
    }
    return actor_map.get(req.actor, f"{req.actor.capitalize()} has access to the system")


def _title(req: CanonicalRequirement) -> str:
    obj = _obj_str(req)
    return f"{req.actor.capitalize()} {req.action}s {obj}".strip()


def _obj_str(req: CanonicalRequirement) -> str:
    return " & ".join(req.objects[:2]) if req.objects else ""
