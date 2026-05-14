"""
SMART AI TEST CASE GENERATOR v2 — Rebuilt with Real NLP Intelligence
====================================================================

Architecture:
  1. NLPRequirementAnalyzer  — spaCy-based deep parsing (SVO triples, 
     constraints, conditions, domain detection)
  2. SemanticTestStrategyEngine — decides WHICH test types to generate 
     based on analysis (not a static list)
  3. IntelligentTestCaseBuilder — generates context-specific titles, 
     steps, test data, and expected results from the parsed semantics
  4. AITestGenerator — public orchestrator

Key differences from the old system:
  • spaCy dependency parsing → real Subject-Verb-Object extraction
  • Constraint extraction with actual numeric values
  • Domain detection from entity semantics, not just keyword lists
  • Test steps reference actual entities and actions from the requirement
  • Negative scenarios invert the actual conditions, not generic "invalid data"
  • Boundary tests use real numbers from the requirement
  • Security tests check the actual permission/auth requirement
  • Quality score reflects NLP parse confidence, not step count
"""

import re
import hashlib
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

import spacy
from spacy.tokens import Doc, Token

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_NLP = None  # Lazy singleton


def _get_nlp():
    global _NLP
    if _NLP is None:
        try:
            _NLP = spacy.load("en_core_web_sm")
        except OSError:
            _NLP = spacy.blank("en")
    return _NLP


class TestType(Enum):
    HAPPY_PATH = "happy_path"
    NEGATIVE = "negative"
    BOUNDARY = "boundary_value"
    SECURITY = "security"
    EDGE_CASE = "edge_case"
    PERFORMANCE = "performance"
    INTEGRATION = "integration"
    DATA_INTEGRITY = "data_integrity"


# Priority enum for clarity
class Priority(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


# ---------------------------------------------------------------------------
# Domain knowledge base for smart generation
# ---------------------------------------------------------------------------

DOMAIN_KEYWORDS: Dict[str, List[str]] = {
    "healthcare": [
        "patient", "doctor", "appointment", "medical", "prescription",
        "diagnosis", "allergy", "insurance", "hospital", "clinic",
        "bệnh nhân", "bác sĩ", "lịch khám", "thuốc", "chẩn đoán",
        "hồ sơ bệnh án", "xét nghiệm", "bảo hiểm",
    ],
    "banking": [
        "account", "transfer", "balance", "transaction", "bank",
        "payment", "deposit", "withdraw", "loan", "interest",
        "tài khoản", "chuyển khoản", "số dư", "giao dịch", "ngân hàng",
    ],
    "ecommerce": [
        "product", "cart", "order", "checkout", "shipping",
        "catalog", "inventory", "price", "discount", "coupon",
        "sản phẩm", "giỏ hàng", "đơn hàng", "thanh toán", "vận chuyển",
    ],
    "authentication": [
        "login", "log in", "logout", "register", "registration", "sign up",
        "signup", "sign in", "signin", "password", "credential",
        "authentication", "authorization", "oauth", "token", "session",
        "mfa", "2fa", "verification",
        "đăng nhập", "đăng ký", "đăng xuất", "mật khẩu", "xác thực", "tài khoản người dùng",
    ],
    "communication": [
        "email", "notification", "sms", "message", "alert",
        "thông báo", "tin nhắn", "cảnh báo",
    ],
}

SECURITY_SIGNALS = [
    "prevent", "unauthorized", "secure", "protect", "encrypt",
    "authenticate", "authorize", "permission", "role", "access control",
    "injection", "xss", "csrf", "sql", "sanitize", "validate",
    "ngăn", "trái phép", "bảo mật", "bảo vệ", "mã hóa", "phân quyền",
]

PERFORMANCE_SIGNALS = [
    "fast", "performance", "response time", "latency", "throughput",
    "load", "concurrent", "scalable", "millisecond", "second",
    "real-time", "within", "under",
    "nhanh", "hiệu suất", "thời gian phản hồi", "tải",
]

INTEGRATION_SIGNALS = [
    "integrate", "api", "gateway", "third-party", "external",
    "webhook", "connect", "interface", "service",
    "tích hợp", "kết nối", "dịch vụ bên ngoài",
]

# ---------------------------------------------------------------------------
# Vietnamese language detection + lightweight Vietnamese requirement parser
# ---------------------------------------------------------------------------

# Characters that only appear in Vietnamese (or other scripts the system doesn't
# target) — used as a fast language detector.
_VI_DIACRITICS = re.compile(
    r'[ăâđêôơưĂÂĐÊÔƠƯ'
    r'àáảãạằắẳẵặầấẩẫậèéẻẽẹềếểễệìíỉĩịòóỏõọồốổỗộờớởỡợùúủũụừứửữựỳýỷỹỵ'
    r'ÀÁẢÃẠẰẮẲẴẶẦẤẨẪẬÈÉẺẼẸỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌỒỐỔỖỘỜỚỞỠỢÙÚỦŨỤỪỨỬỮỰỲÝỶỸỴ]'
)

# Vietnamese modal/auxiliary words separating subject from verb-phrase
_VI_MODALS = ("phải", "nên", "cần", "được", "có thể", "phải có")

# Common Vietnamese subject phrases (longest first for greedy match)
_VI_SUBJECTS = (
    "hệ thống", "ứng dụng", "người dùng", "khách hàng",
    "quản trị viên", "admin", "nhân viên", "bác sĩ", "bệnh nhân",
)

# Common multi-word Vietnamese verb phrases (longest first)
_VI_MULTIWORD_VERBS = (
    "cho phép", "hỗ trợ", "theo dõi", "ghi nhận", "tích hợp",
    "tra cứu", "thanh toán", "đăng nhập", "đăng ký", "đăng xuất",
    "kích hoạt", "xác thực", "kiểm tra", "phát hiện", "cảnh báo",
    "mã hóa", "quản lý", "phân tích", "cung cấp", "tạo lệnh",
    "ghi log", "sao lưu", "tính toán", "đánh giá", "hiển thị",
    "phân quyền", "ngăn chặn", "gửi thông báo", "tự động",
    "ghi nhận", "phát hành", "khóa/mở khóa",
)


def _detect_language(text: str) -> str:
    """Return 'vi' if Vietnamese diacritics dominate, else 'en'."""
    if not text:
        return "en"
    return "vi" if _VI_DIACRITICS.search(text) else "en"


def _vi_extract_svo(text: str) -> Tuple[str, str, str]:
    """Lightweight rule-based extraction of (subject, verb_phrase, object) for
    Vietnamese requirements. spaCy's English model does not parse Vietnamese
    correctly, so we use simple string heuristics instead.
    """
    t = text.strip().rstrip(".!?")
    low = t.lower()

    # 1) Subject — match the longest known subject prefix
    subject = "hệ thống"
    sub_end = 0
    for s in _VI_SUBJECTS:
        if low.startswith(s):
            subject = t[:len(s)]
            sub_end = len(s)
            break

    rest = t[sub_end:].lstrip()
    rest_low = rest.lower()

    # 2) Strip leading modal ("phải", "nên", "cần", "được"…)
    for m in _VI_MODALS:
        if rest_low.startswith(m + " "):
            rest = rest[len(m):].lstrip()
            rest_low = rest.lower()
            break

    # 3) Verb phrase — match longest known multi-word verb, else first word
    verb_phrase = ""
    obj = rest
    matched = False
    for v in _VI_MULTIWORD_VERBS:
        if rest_low.startswith(v + " ") or rest_low == v:
            verb_phrase = rest[:len(v)]
            obj = rest[len(v):].lstrip()
            matched = True
            break
    if not matched:
        parts = rest.split(maxsplit=1)
        verb_phrase = parts[0] if parts else "xử lý"
        obj = parts[1] if len(parts) > 1 else ""

    obj = obj.strip().rstrip(".,;:")
    if not obj:
        obj = "chức năng yêu cầu"
    return subject, verb_phrase, obj

# Action verb → human-readable gerund for titles
ACTION_GERUND = {
    "allow": "allowing",
    "create": "creating",
    "add": "adding",
    "register": "registering",
    "login": "logging in",
    "send": "sending",
    "verify": "verifying",
    "validate": "validating",
    "prevent": "preventing",
    "support": "supporting",
    "display": "displaying",
    "track": "tracking",
    "integrate": "integrating",
    "calculate": "calculating",
    "process": "processing",
    "delete": "deleting",
    "update": "updating",
    "manage": "managing",
    "store": "storing",
    "search": "searching",
    "filter": "filtering",
    "export": "exporting",
    "import": "importing",
    "schedule": "scheduling",
    "book": "booking",
    "cancel": "cancelling",
    "approve": "approving",
    "reject": "rejecting",
    "notify": "notifying",
    "browse": "browsing",
    "view": "viewing",
    "reset": "resetting",
    "encrypt": "encrypting",
    "upload": "uploading",
    "download": "downloading",
    "authenticate": "authenticating",
    "authorize": "authorizing",
    "return": "returning",
    "retrieve": "retrieving",
    "generate": "generating",
    "remove": "removing",
    "save": "saving",
    "load": "loading",
    "check": "checking",
    "enable": "enabling",
    "disable": "disabling",
    "transfer": "transferring",
    "receive": "receiving",
    "submit": "submitting",
    "assign": "assigning",
    "allocate": "allocating",
    "enforce": "enforcing",
    "restrict": "restricting",
    "log": "logging",
    "monitor": "monitoring",
    "detect": "detecting",
    "handle": "handling",
    "provide": "providing",
    "require": "requiring",
    "ensure": "ensuring",
    "maintain": "maintaining",
    "configure": "configuring",
    "set": "setting",
    "get": "getting",
    "apply": "applying",
    "include": "including",
    "exclude": "excluding",
    "connect": "connecting",
    "disconnect": "disconnecting",
    "sync": "syncing",
    "publish": "publishing",
    "subscribe": "subscribing",
}


# ============================================================================
# PART 1: NLP REQUIREMENT ANALYZER
# ============================================================================

@dataclass
class ParsedRequirement:
    """Structured output from NLP analysis of a single requirement."""
    original: str
    # Core SVO
    subject: str          # Who/What acts (e.g. "system", "user", "application")
    main_verb: str        # Primary action verb lemma
    verb_phrase: str       # Full verb phrase (e.g. "send confirmation emails")
    direct_object: str    # What is acted upon
    indirect_objects: List[str] = field(default_factory=list)
    # Modifiers & constraints
    conditions: List[str] = field(default_factory=list)      # "if …", "when …"
    numeric_constraints: List[Dict[str, Any]] = field(default_factory=list)
    quality_attributes: List[str] = field(default_factory=list)  # NFR keywords found
    # Semantic
    domain: str = "general"
    is_security: bool = False
    is_performance: bool = False
    is_integration: bool = False
    entities: List[str] = field(default_factory=list)        # All noun chunks
    prepositions: Dict[str, str] = field(default_factory=dict)  # prep→pobj
    # Confidence
    parse_confidence: float = 0.5
    # Detected natural language: 'en' or 'vi'. Used to pick localized templates
    # when building test case titles, descriptions, steps, and expected results.
    language: str = "en"


class NLPRequirementAnalyzer:
    """Analyze a requirement sentence using spaCy dependency parsing."""

    def __init__(self):
        self.nlp = _get_nlp()

    # ------------------------------------------------------------------
    def analyze(self, text: str) -> ParsedRequirement:
        """Full NLP analysis pipeline."""
        # Step 0 — language detection. spaCy's en_core_web_sm cannot parse
        # Vietnamese, so for Vietnamese requirements we run a tailored rule-based
        # extractor and skip the English dependency parse entirely.
        language = _detect_language(text)
        if language == "vi":
            return self._analyze_vi(text)

        doc = self.nlp(text)

        subject = self._extract_subject(doc)
        main_verb, verb_phrase = self._extract_verb_phrase(doc)
        direct_object = self._extract_direct_object(doc, main_verb)
        indirect_objects = self._extract_indirect_objects(doc, main_verb)
        prepositions = self._extract_prepositions(doc, main_verb)
        conditions = self._extract_conditions(text)
        numeric_constraints = self._extract_numeric_constraints(text)
        entities = [chunk.text for chunk in doc.noun_chunks]
        domain = self._detect_domain(text)
        is_security = self._check_signals(text, SECURITY_SIGNALS)
        is_performance = self._check_signals(text, PERFORMANCE_SIGNALS)
        is_integration = self._check_signals(text, INTEGRATION_SIGNALS)
        quality_attrs = self._extract_quality_attributes(text)
        confidence = self._calc_confidence(subject, main_verb, direct_object, entities)

        return ParsedRequirement(
            original=text.strip(),
            subject=subject,
            main_verb=main_verb,
            verb_phrase=verb_phrase,
            direct_object=direct_object,
            indirect_objects=indirect_objects,
            conditions=conditions,
            numeric_constraints=numeric_constraints,
            quality_attributes=quality_attrs,
            domain=domain,
            is_security=is_security,
            is_performance=is_performance,
            is_integration=is_integration,
            entities=entities,
            prepositions=prepositions,
            parse_confidence=confidence,
            language="en",
        )

    # ------------------------------------------------------------------
    def _analyze_vi(self, text: str) -> ParsedRequirement:
        """Rule-based parser for Vietnamese requirements.

        spaCy's English model produces nonsense POS tags for Vietnamese (which is
        why the previous output contained mojibake titles like
        ``Verify khoảning tiết kiệm succeeds...``). This method extracts SVO via
        keyword rules and reuses the same structural fields as the English path.
        """
        subject, verb_phrase, direct_object = _vi_extract_svo(text)

        # First token of verb_phrase acts as the "main verb lemma" for routing.
        main_verb = verb_phrase.split()[0].lower() if verb_phrase else "xử lý"

        conditions = self._extract_vi_conditions(text)
        numeric_constraints = self._extract_numeric_constraints(text)
        domain = self._detect_domain(text)
        is_security = self._check_signals(text, SECURITY_SIGNALS)
        is_performance = self._check_signals(text, PERFORMANCE_SIGNALS)
        is_integration = self._check_signals(text, INTEGRATION_SIGNALS)
        quality_attrs = self._extract_quality_attributes(text)

        # Confidence: based on how cleanly the requirement matched expected
        # Vietnamese patterns. Slightly lower ceiling than English path because
        # we don't have full dependency parsing here.
        score = 0.45
        if subject and subject.lower() != "hệ thống":
            score += 0.10
        if verb_phrase:
            score += 0.20
        if direct_object and direct_object != "chức năng yêu cầu":
            score += 0.15
        if numeric_constraints:
            score += 0.05
        confidence = min(round(score, 2), 0.95)

        # Coarse "entities" list — split direct_object on whitespace as a proxy
        # for noun chunks so downstream code that inspects entity count works.
        entities = [w for w in direct_object.split() if len(w) > 1] if direct_object else []

        return ParsedRequirement(
            original=text.strip(),
            subject=subject,
            main_verb=main_verb,
            verb_phrase=verb_phrase,
            direct_object=direct_object,
            indirect_objects=[],
            conditions=conditions,
            numeric_constraints=numeric_constraints,
            quality_attributes=quality_attrs,
            domain=domain,
            is_security=is_security,
            is_performance=is_performance,
            is_integration=is_integration,
            entities=entities,
            prepositions={},
            parse_confidence=confidence,
            language="vi",
        )

    @staticmethod
    def _extract_vi_conditions(text: str) -> List[str]:
        """Extract conditional clauses from Vietnamese text."""
        pattern = r'(?:nếu|khi|trừ khi|miễn là|trước khi|sau khi)\s+([^.!?,;]+)'
        matches = re.findall(pattern, text, re.IGNORECASE)
        return [m.strip() for m in matches if len(m.strip()) > 3]

    # ---------- helpers --------------------------------------------------

    def _extract_subject(self, doc: Doc) -> str:
        for token in doc:
            if token.dep_ in ("nsubj", "nsubjpass") and token.head.pos_ == "VERB":
                # Include compound tokens (e.g. "The system")
                subtree = " ".join(
                    t.text for t in token.subtree
                    if t.dep_ in ("compound", "det", "amod", "nsubj", "nsubjpass")
                    or t == token
                )
                return subtree.strip() or token.text
        # Fallback: first noun chunk
        for chunk in doc.noun_chunks:
            return chunk.text
        return "system"

    # Verbs that delegate meaning to their complement (ccomp/xcomp)
    _AUXILIARY_VERBS = {"allow", "enable", "let", "support", "require", "permit", "ensure", "provide"}

    def _extract_verb_phrase(self, doc: Doc) -> Tuple[str, str]:
        """Return (lemma, full verb phrase including object).
        
        If the ROOT verb is an auxiliary-like verb (allow, enable, support…),
        drill into its ccomp/xcomp child for the *meaningful* verb.
        """
        root = None
        for token in doc:
            if token.dep_ == "ROOT" and token.pos_ == "VERB":
                root = token
                break
        if root is None:
            for token in doc:
                if token.pos_ == "VERB":
                    root = token
                    break
        if root is None:
            return ("process", "process the requirement")

        # If root is auxiliary-like, prefer the inner verb
        effective_verb = root
        if root.lemma_ in self._AUXILIARY_VERBS:
            for child in root.children:
                if child.dep_ in ("ccomp", "xcomp", "advcl") and child.pos_ == "VERB":
                    effective_verb = child
                    break

        # Build full phrase from effective verb subtree
        phrase_tokens = []
        for t in effective_verb.subtree:
            if t.dep_ in ("nsubj", "nsubjpass"):
                continue
            if t.dep_ == "det" and t.head.dep_ in ("nsubj", "nsubjpass"):
                continue
            if t.dep_ in ("aux", "auxpass"):
                continue
            phrase_tokens.append(t.text)

        verb_phrase = " ".join(phrase_tokens).strip()
        return (effective_verb.lemma_, verb_phrase or effective_verb.lemma_)

    def _extract_direct_object(self, doc: Doc, verb_lemma: str) -> str:
        """Extract the direct object of the effective verb."""
        # Find ALL verbs matching the lemma (may be the inner verb after auxiliary resolution)
        for token in doc:
            if token.pos_ == "VERB" and token.lemma_ == verb_lemma:
                for child in token.children:
                    if child.dep_ in ("dobj", "attr"):
                        return " ".join(t.text for t in child.subtree).strip()
                # Check ccomp/xcomp children for their objects
                for child in token.children:
                    if child.dep_ in ("ccomp", "xcomp"):
                        for grandchild in child.children:
                            if grandchild.dep_ in ("dobj", "attr"):
                                return " ".join(t.text for t in grandchild.subtree).strip()
                        return " ".join(t.text for t in child.subtree
                                        if t.dep_ not in ("nsubj", "aux")).strip()
                # Check prep objects (e.g. "browse products by category")
                for child in token.children:
                    if child.dep_ == "prep":
                        for pobj in child.children:
                            if pobj.dep_ == "pobj":
                                return " ".join(t.text for t in pobj.subtree).strip()
        # Fallback: largest noun chunk that's not the subject
        chunks = list(doc.noun_chunks)
        if len(chunks) >= 2:
            return chunks[1].text
        return "the operation"

    def _extract_indirect_objects(self, doc: Doc, verb_lemma: str) -> List[str]:
        results = []
        for token in doc:
            if token.dep_ == "pobj":
                results.append(token.text)
        return results

    def _extract_prepositions(self, doc: Doc, verb_lemma: str) -> Dict[str, str]:
        preps = {}
        for token in doc:
            if token.dep_ == "prep":
                pobj = [c for c in token.children if c.dep_ == "pobj"]
                if pobj:
                    full_pobj = " ".join(t.text for t in pobj[0].subtree).strip()
                    preps[token.text] = full_pobj
        return preps

    def _extract_conditions(self, text: str) -> List[str]:
        pattern = r'(?:if|when|unless|provided that|only when|before|after|once)\s+([^.!?,;]+)'
        matches = re.findall(pattern, text, re.IGNORECASE)
        return [m.strip() for m in matches if len(m.strip()) > 3]

    def _extract_numeric_constraints(self, text: str) -> List[Dict[str, Any]]:
        """Extract numeric values with their context."""
        constraints = []
        # Pattern: number + unit (English and Vietnamese)
        pattern = r'(\d+)\s*(days?|hours?|minutes?|seconds?|milliseconds?|months?|years?|weeks?|attempts?|characters?|items?|records?|users?|times?|pages?|results?|files?|MB|GB|KB|bytes?|requests?|connections?|ngày|giờ|phút|giây|tháng|năm|lần|ký tự|bản ghi|người dùng|%)'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            value = int(match.group(1))
            unit = match.group(2).lower()
            # Get surrounding context (10 chars before)
            start = max(0, match.start() - 30)
            context = text[start:match.end()].strip()
            constraints.append({
                "value": value,
                "unit": unit,
                "context": context,
            })
        return constraints

    def _detect_domain(self, text: str) -> str:
        text_lower = text.lower()
        scores: Dict[str, float] = {}
        for domain, keywords in DOMAIN_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[domain] = float(score)
        if not scores:
            return "general"
        # Tie-breaking: authentication > communication ("email" appears in both)
        # Weight authentication keywords higher when register/login/password present
        if "authentication" in scores and "communication" in scores:
            auth_strong = any(kw in text_lower for kw in ["login", "register", "registration", "password", "authentication", "oauth", "token", "sign up", "signup", "sign in", "credential", "đăng nhập", "đăng ký", "mật khẩu"])
            if auth_strong:
                scores["authentication"] += 2.0
        return max(scores, key=scores.get)

    @staticmethod
    def _check_signals(text: str, signals: List[str]) -> bool:
        text_lower = text.lower()
        return any(sig in text_lower for sig in signals)

    def _extract_quality_attributes(self, text: str) -> List[str]:
        attrs = []
        text_lower = text.lower()
        if self._check_signals(text, SECURITY_SIGNALS):
            attrs.append("security")
        if self._check_signals(text, PERFORMANCE_SIGNALS):
            attrs.append("performance")
        if any(kw in text_lower for kw in ["reliable", "availability", "uptime", "failover"]):
            attrs.append("reliability")
        if any(kw in text_lower for kw in ["usabl", "user-friendly", "intuitive", "accessible"]):
            attrs.append("usability")
        return attrs

    def _calc_confidence(self, subject: str, verb: str, obj: str,
                         entities: List[str]) -> float:
        """Confidence based on how much we actually extracted."""
        score = 0.3  # baseline
        if subject and subject != "system":
            score += 0.15
        if verb and verb != "process":
            score += 0.2
        if obj and obj != "the operation":
            score += 0.2
        if len(entities) >= 2:
            score += 0.1
        if len(entities) >= 4:
            score += 0.05
        return min(round(score, 2), 1.0)


# ============================================================================
# PART 2: SEMANTIC TEST STRATEGY ENGINE
# ============================================================================

@dataclass
class TestScenarioPlan:
    """A planned test scenario with rationale."""
    test_type: TestType
    rationale: str          # WHY this test type is needed
    focus: str              # WHAT specifically to test
    risk_level: str         # "high" / "medium" / "low"
    priority: Priority


class SemanticTestStrategyEngine:
    """Decide which test types to generate based on semantic analysis."""

    def plan_tests(self, req: ParsedRequirement) -> List[TestScenarioPlan]:
        plans: List[TestScenarioPlan] = []

        # 1. Always: Happy path
        plans.append(TestScenarioPlan(
            test_type=TestType.HAPPY_PATH,
            rationale=f"Verify core functionality: {req.verb_phrase[:60]}",
            focus=f"{req.subject} can {req.main_verb} {req.direct_object}",
            risk_level="high",
            priority=Priority.CRITICAL,
        ))

        # 2. Negative test — invert the action
        plans.append(TestScenarioPlan(
            test_type=TestType.NEGATIVE,
            rationale=f"Ensure graceful failure when {req.main_verb} receives invalid input",
            focus=f"Invalid/missing data for {req.direct_object}",
            risk_level="high",
            priority=Priority.HIGH,
        ))

        # 3. Boundary if numeric constraints found
        if req.numeric_constraints:
            for nc in req.numeric_constraints:
                plans.append(TestScenarioPlan(
                    test_type=TestType.BOUNDARY,
                    rationale=f"Boundary: {nc['context']}",
                    focus=f"Test at value={nc['value']} {nc['unit']}, value={nc['value']-1}, value={nc['value']+1}",
                    risk_level="medium",
                    priority=Priority.HIGH,
                ))
            # Only add one boundary plan if multiple constraints (to avoid explosion)
            if len(req.numeric_constraints) > 1:
                plans = [p for p in plans if p.test_type != TestType.BOUNDARY]
                nc = req.numeric_constraints[0]
                plans.append(TestScenarioPlan(
                    test_type=TestType.BOUNDARY,
                    rationale=f"Boundary analysis for {len(req.numeric_constraints)} constraints (primary: {nc['value']} {nc['unit']})",
                    focus=f"Test at/around {nc['value']} {nc['unit']}",
                    risk_level="medium",
                    priority=Priority.HIGH,
                ))

        # 4. Security if signals detected
        if req.is_security:
            plans.append(TestScenarioPlan(
                test_type=TestType.SECURITY,
                rationale=f"Security requirement detected: {req.original[:60]}",
                focus=f"Unauthorized access to {req.direct_object}",
                risk_level="high",
                priority=Priority.CRITICAL,
            ))

        # 5. Performance if signals detected
        if req.is_performance:
            plans.append(TestScenarioPlan(
                test_type=TestType.PERFORMANCE,
                rationale=f"Performance requirement detected",
                focus=f"Response time / throughput for {req.main_verb} operation",
                risk_level="medium",
                priority=Priority.HIGH,
            ))

        # 6. Integration if external systems mentioned
        if req.is_integration:
            plans.append(TestScenarioPlan(
                test_type=TestType.INTEGRATION,
                rationale=f"External integration detected in: {req.verb_phrase[:50]}",
                focus=f"Integration with {req.prepositions.get('with', req.direct_object)}",
                risk_level="high",
                priority=Priority.HIGH,
            ))

        # 7. Data integrity for create/update/delete actions (English + Vietnamese verbs)
        _data_mod_verbs_en = ("create", "add", "store", "update", "delete", "register", "save")
        _data_mod_verbs_vi = ("tạo", "thêm", "lưu", "cập nhật", "xóa", "đăng ký", "ghi", "sao lưu")
        if req.main_verb in _data_mod_verbs_en or req.main_verb in _data_mod_verbs_vi:
            plans.append(TestScenarioPlan(
                test_type=TestType.DATA_INTEGRITY,
                rationale=f"Data modification operation ({req.main_verb}) requires integrity check",
                focus=f"Verify {req.direct_object} persisted/updated correctly",
                risk_level="medium",
                priority=Priority.HIGH,
            ))

        # 8. Edge case for conditional requirements
        if req.conditions:
            plans.append(TestScenarioPlan(
                test_type=TestType.EDGE_CASE,
                rationale=f"Conditional logic found: '{req.conditions[0][:50]}'",
                focus=f"Condition boundary and negation",
                risk_level="medium",
                priority=Priority.MEDIUM,
            ))

        return plans


# ============================================================================
# PART 3: INTELLIGENT TEST CASE BUILDER
# ============================================================================

class IntelligentTestCaseBuilder:
    """Build test cases that are specific to the analyzed requirement."""

    def __init__(self):
        self._global_counter: Dict[str, int] = {}

    def _next_id(self, domain: str, type_code: str) -> str:
        key = f"{domain[:3].upper()}-{type_code}"
        self._global_counter[key] = self._global_counter.get(key, 0) + 1
        return f"TC-{key}-{self._global_counter[key]:03d}"

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------
    def build(self, req: ParsedRequirement, plan: TestScenarioPlan,
              req_index: int) -> Dict[str, Any]:
        type_code = {
            TestType.HAPPY_PATH:     "HP",
            TestType.NEGATIVE:       "NEG",
            TestType.BOUNDARY:       "BVA",
            TestType.SECURITY:       "SEC",
            TestType.PERFORMANCE:    "PERF",
            TestType.INTEGRATION:    "INT",
            TestType.DATA_INTEGRITY: "DATA",
            TestType.EDGE_CASE:      "EDGE",
        }.get(plan.test_type, "GEN")

        test_id = self._next_id(req.domain, type_code)
        req_id = f"REQ-{req.domain[:3].upper()}-{req_index:03d}"

        # Dispatch to type-specific builder
        builder_fn = {
            TestType.HAPPY_PATH:     self._build_happy_path,
            TestType.NEGATIVE:       self._build_negative,
            TestType.BOUNDARY:       self._build_boundary,
            TestType.SECURITY:       self._build_security,
            TestType.PERFORMANCE:    self._build_performance,
            TestType.INTEGRATION:    self._build_integration,
            TestType.DATA_INTEGRITY: self._build_data_integrity,
            TestType.EDGE_CASE:      self._build_edge_case,
        }.get(plan.test_type, self._build_happy_path)

        title, description, preconditions, steps, expected, test_data = builder_fn(req, plan)

        # Localize all user-facing strings to Vietnamese when the requirement is
        # written in Vietnamese. This avoids the previous bug where English
        # templates concatenated Vietnamese fragments to produce garbled output
        # such as ``Verify khoảning tiết kiệm succeeds...``.
        if req.language == "vi":
            title, description, preconditions, steps, expected = self._localize_vi(
                req, plan, title, description, preconditions, steps, expected, test_data
            )

        effort = self._calc_effort(steps, plan.test_type, req)
        quality = self._calc_quality(req, plan, steps)

        return {
            "test_id": test_id,
            "id": test_id,
            "requirement_id": req_id,
            "title": title,
            "description": description,
            "scenario_type": plan.test_type.value,
            "test_type": plan.test_type.value,
            "type": plan.test_type.value,
            "priority": plan.priority.value,
            "risk_level": plan.risk_level,
            "preconditions": preconditions,
            "test_data": test_data,
            "steps": steps,
            "expected_result": expected,
            "postconditions": self._postconditions(plan.test_type),
            "requirement_trace": req.original,
            "domain": req.domain,
            "why_generated": plan.rationale,
            "ai_confidence": quality,
            "ml_quality_score": quality,
            "quality_score": quality,
            "confidence": {"overall_score": quality},
            "estimated_effort_hours": effort,
            "estimated_effort_minutes": round(effort * 60),
            "effort_hours": effort,
            "created_at": datetime.now().isoformat(),
        }

    # ------------------------------------------------------------------
    # Type-specific builders — each returns (title, desc, preconditions, steps, expected, test_data)
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Vietnamese localization (post-processing layer)
    # ------------------------------------------------------------------
    def _localize_vi(self, req: "ParsedRequirement", plan: "TestScenarioPlan",
                     title: str, description: str, preconditions: List[str],
                     steps: List[Dict[str, Any]], expected: str,
                     test_data: Dict[str, Any]):
        """Replace English template strings with Vietnamese equivalents,
        preserving structural data (test_data, ordering, step count).
        """
        subj = req.subject or "Hệ thống"
        verb = req.verb_phrase or req.main_verb or "xử lý"
        obj = req.direct_object or "đối tượng"
        ttype = plan.test_type

        # ---------- Title + description + expected_result ----------
        if ttype == TestType.HAPPY_PATH:
            title = f"Kiểm thử thành công: {verb} {obj} trong điều kiện bình thường"
            description = f"Xác nhận rằng {subj} có thể {verb} {obj} một cách thành công."
            expected = f"{subj} {verb} {obj} thành công; hệ thống xác nhận thao tác và dữ liệu nhất quán."
        elif ttype == TestType.NEGATIVE:
            title = f"Kiểm thử âm: {verb} {obj} thất bại đúng cách với dữ liệu không hợp lệ"
            description = f"Đảm bảo hệ thống từ chối {verb} khi dữ liệu cho {obj} thiếu, sai định dạng hoặc vi phạm ràng buộc."
            expected = f"Hệ thống ngăn thao tác {verb} với dữ liệu không hợp lệ; hiển thị thông báo lỗi rõ ràng; không lưu dữ liệu một phần."
        elif ttype == TestType.BOUNDARY:
            nc = req.numeric_constraints[0] if req.numeric_constraints else {"value": 100, "unit": "đơn vị"}
            val, unit = nc.get("value", 100), nc.get("unit", "đơn vị")
            title = f"Giá trị biên: Kiểm thử {verb} tại giới hạn {val} {unit}"
            description = f"Xác minh hành vi của hệ thống tại biên {val} {unit}: dưới biên, đúng biên và trên biên."
            expected = f"Hệ thống áp dụng đúng giới hạn {val} {unit}; chấp nhận ≤ {val}, từ chối > {val} kèm thông báo lỗi rõ ràng."
        elif ttype == TestType.SECURITY:
            title = f"Bảo mật: Xác minh truy cập trái phép tới {obj} bị chặn"
            description = f"Đảm bảo chỉ người dùng được phép mới có thể {verb} {obj}; kiểm tra khả năng chống các mối đe dọa bảo mật phổ biến."
            expected = f"Mọi nỗ lực truy cập trái phép tới {obj} đều bị từ chối; hệ thống trả về mã trạng thái phù hợp; không rò rỉ dữ liệu; các sự kiện bảo mật được ghi log."
        elif ttype == TestType.PERFORMANCE:
            time_constraint = next((nc for nc in req.numeric_constraints
                                    if any(u in nc.get("unit", "") for u in ("second", "millisecond", "giây"))), None)
            time_str = f"{time_constraint['value']} {time_constraint['unit']}" if time_constraint else "3 giây"
            title = f"Hiệu năng: Xác minh {verb} {obj} hoàn tất trong {time_str}"
            description = f"Đo thời gian phản hồi của thao tác {verb} dưới tải bình thường và tải đỉnh."
            expected = f"Thao tác {verb} {obj} hoàn tất trong {time_str} ở điều kiện bình thường; hệ thống ổn định khi chịu tải cao."
        elif ttype == TestType.INTEGRATION:
            ext_system = req.prepositions.get("with", obj)
            title = f"Tích hợp: Xác minh {verb} với hệ thống bên ngoài {ext_system}"
            description = f"Xác nhận rằng {subj} tích hợp đúng với {ext_system}, bao gồm trường hợp thành công, thất bại và timeout."
            expected = f"Tích hợp với {ext_system} hoạt động đúng cho trường hợp thành công; hệ thống xử lý timeout/lỗi/không khả dụng một cách an toàn, không mất dữ liệu."
        elif ttype == TestType.DATA_INTEGRITY:
            title = f"Toàn vẹn dữ liệu: Xác minh {obj} được lưu đúng sau khi {verb}"
            description = f"Đảm bảo dữ liệu {obj} được lưu chính xác, có thể truy xuất và nhất quán sau thao tác {verb}."
            expected = f"Dữ liệu {obj} được lưu trữ đúng; truy xuất qua API/UI khớp; mốc thời gian chính xác; toàn vẹn tham chiếu được duy trì."
        elif ttype == TestType.EDGE_CASE:
            cond = req.conditions[0] if req.conditions else f"trạng thái bất thường khi {verb}"
            title = f"Trường hợp biên: {verb} {obj} với điều kiện '{cond[:50]}'"
            description = f"Kiểm thử hành vi hệ thống khi điều kiện '{cond}' nằm ở biên hoặc bị phủ định."
            expected = f"Hệ thống xử lý đúng cả hai trạng thái của điều kiện; không hỏng dữ liệu khi chuyển trạng thái; hành vi khớp đặc tả."

        # ---------- Preconditions (translate domain-aware defaults) ----------
        domain = req.domain
        vi_preconds = ["Hệ thống đang chạy và truy cập được"]
        if domain == "healthcare":
            vi_preconds += ["Hồ sơ bệnh nhân thử nghiệm tồn tại trong hệ thống",
                            "Người dùng có thông tin xác thực bác sĩ hợp lệ"]
        elif domain == "banking":
            vi_preconds += ["Tài khoản thử nghiệm tồn tại với số dư đã biết",
                            "Người dùng có quyền giao dịch ngân hàng"]
        elif domain == "ecommerce":
            vi_preconds += ["Danh mục sản phẩm đã có dữ liệu thử nghiệm",
                            "Người dùng đã đăng ký tài khoản"]
        elif domain == "authentication":
            vi_preconds += ["Tài khoản người dùng tồn tại với thông tin đăng nhập đã biết",
                            "Dịch vụ xác thực đang hoạt động"]
        else:
            vi_preconds.append("Người dùng đã được xác thực và có quyền phù hợp")
        if ttype == TestType.SECURITY:
            vi_preconds.append("Các tính năng bảo mật của hệ thống đang được bật")
        if ttype == TestType.DATA_INTEGRITY:
            vi_preconds.append("Cơ sở dữ liệu đang ở trạng thái sạch đã biết")
        if ttype != TestType.NEGATIVE:
            vi_preconds.append("Dữ liệu kiểm thử đã được chuẩn bị và xác thực")
        preconditions = vi_preconds

        # ---------- Steps (translate by scenario type) ----------
        steps = self._build_vi_steps(req, plan)

        return title, description, preconditions, steps, expected

    def _build_vi_steps(self, req: "ParsedRequirement", plan: "TestScenarioPlan") -> List[Dict[str, Any]]:
        """Generate Vietnamese test steps tailored to the scenario type."""
        subj = req.subject or "Hệ thống"
        verb = req.verb_phrase or req.main_verb or "xử lý"
        obj = req.direct_object or "đối tượng"
        actor = "người dùng được ủy quyền" if subj.lower() in ("hệ thống", "ứng dụng") else subj
        ttype = plan.test_type

        def s(order, action, expected):
            return {"order": order, "action": action, "expected_result": expected}

        if ttype == TestType.HAPPY_PATH:
            return [
                s(1, f"Đăng nhập với vai trò {actor} bằng thông tin hợp lệ",
                  "Người dùng được xác thực và hiển thị màn hình chính"),
                s(2, f"Điều hướng đến chức năng {verb} {obj}",
                  f"Trang/biểu mẫu cho {obj} được hiển thị đúng"),
                s(3, f"Nhập đầy đủ dữ liệu hợp lệ cho {obj}",
                  "Tất cả các trường chấp nhận dữ liệu mà không báo lỗi"),
                s(4, f"Thực hiện thao tác '{verb}' và gửi yêu cầu",
                  f"Hệ thống xử lý yêu cầu {verb} thành công"),
                s(5, f"Kiểm tra trạng thái {obj} sau thao tác",
                  f"{obj} được tạo/cập nhật đúng trong hệ thống"),
            ]
        if ttype == TestType.NEGATIVE:
            return [
                s(1, f"Đăng nhập với vai trò {actor} bằng thông tin hợp lệ",
                  "Người dùng được xác thực"),
                s(2, f"Điều hướng đến chức năng {verb} {obj}",
                  "Trang được hiển thị"),
                s(3, f"Bỏ trống các trường bắt buộc của {obj}",
                  "Hệ thống đánh dấu các trường bắt buộc"),
                s(4, f"Gửi biểu mẫu {verb} với các trường bắt buộc bị trống",
                  "Hệ thống từ chối với thông báo lỗi cụ thể"),
                s(5, f"Nhập dữ liệu không hợp lệ cho {obj}",
                  "Hệ thống hiển thị lỗi xác thực inline cho từng trường sai"),
                s(6, f"Kiểm tra rằng {obj} KHÔNG bị tạo/sửa",
                  f"Không có thay đổi nào với {obj} trong cơ sở dữ liệu"),
            ]
        if ttype == TestType.BOUNDARY:
            nc = req.numeric_constraints[0] if req.numeric_constraints else {"value": 100, "unit": "đơn vị"}
            val, unit = nc.get("value", 100), nc.get("unit", "đơn vị")
            return [
                s(1, f"Đăng nhập với vai trò {actor}", "Người dùng được xác thực"),
                s(2, f"Thực hiện {verb} với giá trị = {val - 1} {unit} (dưới biên)",
                  f"Hệ thống chấp nhận: {val - 1} nằm trong giới hạn"),
                s(3, f"Thực hiện {verb} với giá trị = {val} {unit} (đúng biên)",
                  f"Hệ thống chấp nhận: {val} nằm đúng tại biên"),
                s(4, f"Thực hiện {verb} với giá trị = {val + 1} {unit} (vượt biên)",
                  f"Hệ thống từ chối: {val + 1} vượt giới hạn {val} {unit}"),
                s(5, f"Thực hiện {verb} với giá trị = 0 {unit} (biên dưới)",
                  "Hệ thống xử lý giá trị 0/tối thiểu đúng cách"),
                s(6, "Kiểm tra thông báo lỗi đặc thù cho vi phạm biên",
                  f"Thông báo lỗi nhắc rõ giới hạn {val} {unit}"),
            ]
        if ttype == TestType.SECURITY:
            return [
                s(1, f"Thử {verb} {obj} mà không xác thực",
                  "Hệ thống trả về 401 Unauthorized; không lộ dữ liệu"),
                s(2, f"Thử {verb} {obj} với token phiên đã hết hạn",
                  "Hệ thống trả về 401; chuyển hướng tới trang đăng nhập"),
                s(3, f"Thử {verb} {obj} với người dùng không đủ quyền",
                  "Hệ thống trả về 403 Forbidden; thao tác bị từ chối"),
                s(4, f"Gửi payload SQL injection vào trường nhập của {obj}",
                  "Hệ thống làm sạch input; không có lỗi SQL hoặc rò rỉ dữ liệu"),
                s(5, f"Gửi payload XSS vào trường của {obj}",
                  "Hệ thống escape output; script không được thực thi"),
                s(6, "Kiểm tra log audit ghi nhận mọi truy cập trái phép",
                  "Sự kiện bảo mật được ghi với timestamp, IP, user info"),
            ]
        if ttype == TestType.PERFORMANCE:
            time_constraint = next((nc for nc in req.numeric_constraints
                                    if any(u in nc.get("unit", "") for u in ("second", "millisecond", "giây"))), None)
            time_str = f"{time_constraint['value']} {time_constraint['unit']}" if time_constraint else "3 giây"
            return [
                s(1, f"Thực hiện {verb} {obj} với 1 người dùng đơn",
                  f"Thời gian phản hồi < {time_str}"),
                s(2, f"Thực hiện {verb} dưới tải bình thường (50 yêu cầu đồng thời)",
                  f"95th percentile < {time_str}"),
                s(3, f"Thực hiện {verb} dưới tải đỉnh (200 yêu cầu đồng thời)",
                  f"99th percentile < 2× {time_str}; không lỗi"),
                s(4, "Theo dõi CPU, bộ nhớ, connection pool trong quá trình kiểm thử tải",
                  "Tài nguyên sử dụng < 80%"),
                s(5, "Kiểm tra không có rò rỉ bộ nhớ hoặc cạn connection pool sau tải kéo dài",
                  "Hệ thống trở lại mức nền sau khi tải giảm"),
            ]
        if ttype == TestType.INTEGRATION:
            ext_system = req.prepositions.get("with", obj)
            return [
                s(1, f"Gửi yêu cầu {verb} hợp lệ tới {ext_system}",
                  f"{ext_system} xử lý yêu cầu; nhận được phản hồi thành công"),
                s(2, f"Kiểm tra dữ liệu nhất quán giữa {subj} và {ext_system}",
                  "Dữ liệu khớp ở cả hai phía"),
                s(3, f"Mô phỏng timeout từ {ext_system} (trễ 30s)",
                  "Hệ thống xử lý timeout, hiển thị thông báo thân thiện, retry nếu phù hợp"),
                s(4, f"Mô phỏng {ext_system} trả về lỗi 500",
                  "Hệ thống ghi log lỗi; không hỏng dữ liệu; thông báo cho người dùng"),
                s(5, f"Mô phỏng {ext_system} không khả dụng",
                  "Hệ thống suy giảm chức năng có kiểm soát hoặc xếp hàng yêu cầu"),
            ]
        if ttype == TestType.DATA_INTEGRITY:
            return [
                s(1, f"Thực hiện {verb} {obj} với dữ liệu hợp lệ",
                  "Thao tác hoàn tất thành công"),
                s(2, f"Truy vấn cơ sở dữ liệu để xác minh bản ghi {obj} tồn tại",
                  "Bản ghi có đầy đủ trường khớp với dữ liệu đã gửi"),
                s(3, f"Truy xuất {obj} qua UI/API",
                  "Dữ liệu hiển thị khớp chính xác với dữ liệu đã gửi"),
                s(4, "Kiểm tra mốc thời gian (created_at, updated_at) đúng",
                  "Mốc thời gian phản ánh đúng thời điểm thao tác"),
                s(5, f"Thực hiện {verb} với dữ liệu khác để kiểm tra việc cập nhật/trùng lặp",
                  "Hệ thống xử lý đúng (cập nhật hoặc ngăn trùng phù hợp)"),
                s(6, "Kiểm tra toàn vẹn tham chiếu với các thực thể liên quan",
                  "Mọi khóa ngoại hợp lệ; không có bản ghi mồ côi"),
            ]
        if ttype == TestType.EDGE_CASE:
            cond = req.conditions[0] if req.conditions else f"trạng thái bất thường khi {verb}"
            return [
                s(1, f"Thiết lập điều kiện: '{cond}'",
                  "Hệ thống ở đúng trạng thái điều kiện chỉ định"),
                s(2, f"Thực hiện {verb} {obj} khi điều kiện đúng",
                  "Hệ thống đi theo nhánh có điều kiện tương ứng"),
                s(3, f"Phủ định điều kiện ('{cond}' = false)",
                  "Trạng thái hệ thống chuyển sang điều kiện ngược lại"),
                s(4, f"Thực hiện {verb} {obj} khi điều kiện bị phủ định",
                  "Hệ thống đi theo nhánh mặc định"),
                s(5, "Bật/tắt điều kiện liên tục (mô phỏng race condition)",
                  "Hệ thống xử lý đúng các thay đổi trạng thái đồng thời mà không hỏng dữ liệu"),
            ]
        # Fallback: keep generic skeleton in Vietnamese
        return [
            s(1, f"Chuẩn bị môi trường để {verb} {obj}", "Môi trường sẵn sàng"),
            s(2, f"Thực hiện {verb} {obj}", "Thao tác hoàn tất"),
            s(3, f"Xác minh kết quả của {verb} {obj}", "Kết quả đúng kỳ vọng"),
        ]

    # ------------------------------------------------------------------
    # Type-specific builders (English) — each returns
    # (title, desc, preconditions, steps, expected, test_data)
    # ------------------------------------------------------------------
    def _build_happy_path(self, req: ParsedRequirement, plan: TestScenarioPlan):
        gerund = ACTION_GERUND.get(req.main_verb, f"{req.main_verb}ing")
        title = f"Verify {gerund} {req.direct_object} succeeds under normal conditions"
        desc = (f"Confirm that {req.subject} can successfully {req.main_verb} "
                f"{req.direct_object}" +
                (f" with {list(req.prepositions.values())[0]}" if req.prepositions else ""))

        preconditions = self._smart_preconditions(req, is_valid=True)
        test_data = self._smart_test_data(req, valid=True)

        steps = [
            self._step(1, f"Log in as {self._actor(req)} with valid credentials",
                        "User is authenticated and dashboard is displayed"),
            self._step(2, f"Navigate to {req.direct_object} management area",
                        f"{req.direct_object.capitalize()} page/form is displayed correctly"),
            self._step(3, f"Provide valid data: {self._summarize_data(test_data)}",
                        "All fields accept the input without validation errors"),
            self._step(4, f"Execute '{req.main_verb}' action and submit",
                        f"System processes the {req.main_verb} request successfully"),
            self._step(5, f"Verify {req.direct_object} state after operation",
                        f"{req.direct_object.capitalize()} is correctly created/updated in the system"),
        ]

        # Add condition-specific verification
        if req.conditions:
            steps.append(self._step(6, f"Confirm condition is met: '{req.conditions[0]}'",
                                    "System behavior matches the stated condition"))

        expected = (f"{req.subject.capitalize()} successfully {req.main_verb}s "
                    f"{req.direct_object}; system confirms the operation and data is consistent")

        return title, desc, preconditions, steps, expected, test_data

    def _build_negative(self, req: ParsedRequirement, plan: TestScenarioPlan):
        gerund = ACTION_GERUND.get(req.main_verb, f"{req.main_verb}ing")
        title = f"Verify {gerund} {req.direct_object} fails gracefully with invalid input"
        desc = (f"Ensure system rejects {req.main_verb} when required data for "
                f"{req.direct_object} is missing, malformed, or violates constraints")

        preconditions = self._smart_preconditions(req, is_valid=True)
        invalid_data = self._smart_test_data(req, valid=False)

        steps = [
            self._step(1, f"Log in as {self._actor(req)} with valid credentials",
                        "User is authenticated"),
            self._step(2, f"Navigate to {req.direct_object} management area",
                        "Page is displayed"),
            self._step(3, f"Leave required fields empty for {req.direct_object}",
                        "System highlights required fields visually"),
            self._step(4, f"Submit the {req.main_verb} form with empty required fields",
                        "System rejects submission with specific error messages"),
            self._step(5, f"Enter invalid data: {self._summarize_data(invalid_data)}",
                        "System shows inline validation errors for each invalid field"),
            self._step(6, f"Verify {req.direct_object} was NOT created/modified",
                        f"No changes to {req.direct_object} in the database"),
        ]

        expected = (f"System prevents {req.main_verb} with invalid data; "
                    f"shows specific, user-friendly error messages; "
                    f"no partial data is saved")

        return title, desc, preconditions, steps, expected, invalid_data

    def _build_boundary(self, req: ParsedRequirement, plan: TestScenarioPlan):
        nc = req.numeric_constraints[0] if req.numeric_constraints else {"value": 100, "unit": "items", "context": "limit"}
        val = nc["value"]
        unit = nc["unit"]

        title = f"Boundary: Test {req.main_verb} at limit of {val} {unit}"
        desc = (f"Verify system behavior at boundary value {val} {unit}: "
                f"at limit, below limit, and above limit")

        preconditions = self._smart_preconditions(req, is_valid=True)
        preconditions.append(f"System constraint: maximum {val} {unit}")

        test_data = {
            "below_boundary": f"{val - 1} {unit}",
            "at_boundary": f"{val} {unit}",
            "above_boundary": f"{val + 1} {unit}",
        }

        steps = [
            self._step(1, f"Log in as {self._actor(req)}",
                        "User is authenticated"),
            self._step(2, f"Execute {req.main_verb} with value = {val - 1} {unit} (below limit)",
                        f"System accepts: {val - 1} is within allowed range"),
            self._step(3, f"Execute {req.main_verb} with value = {val} {unit} (at limit)",
                        f"System accepts: {val} is exactly at the boundary"),
            self._step(4, f"Execute {req.main_verb} with value = {val + 1} {unit} (above limit)",
                        f"System rejects: {val + 1} exceeds the maximum of {val} {unit}"),
            self._step(5, f"Execute {req.main_verb} with value = 0 {unit} (minimum boundary)",
                        "System handles zero/minimum value correctly"),
            self._step(6, "Verify error messages are specific to the boundary violation",
                        f"Error message references the {val} {unit} limit clearly"),
        ]

        expected = (f"System correctly enforces the {val} {unit} boundary; "
                    f"accepts values ≤ {val}, rejects values > {val} with clear error messages")

        return title, desc, preconditions, steps, expected, test_data

    def _build_security(self, req: ParsedRequirement, plan: TestScenarioPlan):
        title = f"Security: Verify unauthorized access to {req.direct_object} is blocked"
        desc = (f"Ensure only authorized users can {req.main_verb} {req.direct_object}; "
                f"verify protection against common security threats")

        preconditions = [
            "System is running with security features enabled",
            f"{req.direct_object.capitalize()} with sensitive data exists",
            "Test accounts with different permission levels available",
        ]

        test_data = {
            "unauthorized_user": "user_without_permissions",
            "expired_session": "token_expired_30min_ago",
            "injection_payload": "' OR 1=1 --",
            "xss_payload": "<script>alert('xss')</script>",
        }

        steps = [
            self._step(1, f"Attempt to {req.main_verb} {req.direct_object} without authentication",
                        "System returns 401 Unauthorized; no data is exposed"),
            self._step(2, f"Attempt to {req.main_verb} {req.direct_object} with expired session token",
                        "System returns 401; redirects to login page"),
            self._step(3, f"Attempt to {req.main_verb} {req.direct_object} as user without required role/permission",
                        "System returns 403 Forbidden; operation is denied"),
            self._step(4, f"Submit SQL injection payload in {req.direct_object} input fields",
                        "System sanitizes input; no SQL error or data leak"),
            self._step(5, f"Submit XSS payload in {req.direct_object} fields",
                        "System escapes output; script does not execute"),
            self._step(6, "Verify audit log records all unauthorized attempts",
                        "Security events are logged with timestamp, IP, and user info"),
        ]

        expected = (f"All unauthorized attempts to {req.main_verb} {req.direct_object} are blocked; "
                    f"system returns appropriate HTTP status codes; no data is leaked; "
                    f"injection attacks are neutralized; security events are logged")

        return title, desc, preconditions, steps, expected, test_data

    def _build_performance(self, req: ParsedRequirement, plan: TestScenarioPlan):
        # Try to extract specific timing requirements
        time_constraint = None
        for nc in req.numeric_constraints:
            if any(u in nc["unit"] for u in ["second", "millisecond", "giây"]):
                time_constraint = nc
                break

        time_str = f"{time_constraint['value']} {time_constraint['unit']}" if time_constraint else "3 seconds"

        title = f"Performance: Verify {req.main_verb} {req.direct_object} completes within {time_str}"
        desc = f"Measure response time of {req.main_verb} operation under normal and peak load"

        preconditions = [
            "System is deployed in test environment matching production specs",
            "Database is seeded with realistic data volume",
            "Performance monitoring tools are active",
        ]

        test_data = {
            "single_user_load": "1 concurrent request",
            "normal_load": "50 concurrent requests",
            "peak_load": "200 concurrent requests",
            "response_threshold": time_str,
        }

        steps = [
            self._step(1, f"Execute {req.main_verb} {req.direct_object} with single user",
                        f"Response time < {time_str}"),
            self._step(2, f"Execute {req.main_verb} under normal load (50 concurrent users)",
                        f"95th percentile response time < {time_str}"),
            self._step(3, f"Execute {req.main_verb} under peak load (200 concurrent users)",
                        f"99th percentile response time < 2× {time_str}; no errors"),
            self._step(4, "Monitor CPU, memory, and database connection pool during load test",
                        "Resource usage stays within acceptable thresholds (< 80%)"),
            self._step(5, "Verify no memory leaks or connection pool exhaustion after sustained load",
                        "System recovers to baseline resource usage after load subsides"),
        ]

        expected = (f"{req.main_verb.capitalize()} operation completes within {time_str} under normal conditions; "
                    f"system maintains stability under peak load with no data loss")

        return title, desc, preconditions, steps, expected, test_data

    def _build_integration(self, req: ParsedRequirement, plan: TestScenarioPlan):
        ext_system = req.prepositions.get("with", req.direct_object)
        title = f"Integration: Verify {req.main_verb} with external {ext_system}"
        desc = (f"Confirm that {req.subject} correctly integrates with {ext_system} "
                f"including success, failure, and timeout scenarios")

        preconditions = [
            f"External {ext_system} is available in test environment",
            "API credentials/keys are configured correctly",
            "Network connectivity between systems is established",
        ]

        test_data = {
            "valid_request": f"Standard {req.main_verb} payload",
            "timeout_scenario": "External service response delayed 30s",
            "error_response": "External service returns 500 error",
        }

        steps = [
            self._step(1, f"Send valid {req.main_verb} request to {ext_system}",
                        f"External {ext_system} processes request; response received successfully"),
            self._step(2, f"Verify data consistency between {req.subject} and {ext_system}",
                        "Data matches on both sides; no data loss during transfer"),
            self._step(3, f"Simulate {ext_system} timeout (30s delay)",
                        "System handles timeout gracefully; shows user-friendly message; retries if applicable"),
            self._step(4, f"Simulate {ext_system} returning error (500)",
                        "System logs error; no data corruption; user is informed"),
            self._step(5, f"Simulate {ext_system} being completely unavailable",
                        "System degrades gracefully; core functionality still works or queues the request"),
        ]

        expected = (f"Integration with {ext_system} works correctly for success case; "
                    f"system handles timeout, error, and unavailability gracefully without data loss")

        return title, desc, preconditions, steps, expected, test_data

    def _build_data_integrity(self, req: ParsedRequirement, plan: TestScenarioPlan):
        title = f"Data Integrity: Verify {req.direct_object} persistence after {req.main_verb}"
        desc = (f"Ensure {req.direct_object} data is correctly saved, retrievable, "
                f"and consistent after {req.main_verb} operation")

        preconditions = self._smart_preconditions(req, is_valid=True)
        preconditions.append("Database is in a known clean state")

        test_data = self._smart_test_data(req, valid=True)

        steps = [
            self._step(1, f"Execute {req.main_verb} {req.direct_object} with valid data",
                        "Operation completes successfully"),
            self._step(2, f"Query the database to verify {req.direct_object} record exists",
                        "Record found with all fields matching submitted data"),
            self._step(3, f"Retrieve {req.direct_object} via the application UI/API",
                        "Displayed data matches the original submitted data exactly"),
            self._step(4, f"Verify timestamps (created_at, updated_at) are set correctly",
                        "Timestamps reflect the actual operation time"),
            self._step(5, f"Execute {req.main_verb} again with different data to verify update/duplication handling",
                        "System handles correctly (updates existing or prevents duplicate as appropriate)"),
            self._step(6, "Verify referential integrity with related entities",
                        "All foreign key relationships are valid; no orphaned records"),
        ]

        expected = (f"{req.direct_object.capitalize()} data is persisted correctly; "
                    f"retrievable via API and UI; timestamps accurate; "
                    f"referential integrity maintained")

        return title, desc, preconditions, steps, expected, test_data

    def _build_edge_case(self, req: ParsedRequirement, plan: TestScenarioPlan):
        condition_text = req.conditions[0] if req.conditions else f"unusual state during {req.main_verb}"
        title = f"Edge Case: {req.main_verb} {req.direct_object} under condition '{condition_text[:50]}'"
        desc = (f"Test system behavior when the condition '{condition_text}' "
                f"is at its boundary or negated")

        preconditions = self._smart_preconditions(req, is_valid=True)
        if req.conditions:
            preconditions.append(f"Condition setup: '{req.conditions[0]}'")

        test_data = self._smart_test_data(req, valid=True)
        test_data["condition_active"] = True
        test_data["condition_negated"] = False

        steps = [
            self._step(1, f"Setup the condition: '{condition_text}'",
                        "System is in the specified conditional state"),
            self._step(2, f"Execute {req.main_verb} {req.direct_object} while condition holds",
                        f"System follows the conditional flow correctly"),
            self._step(3, f"Negate the condition (make '{condition_text}' false)",
                        "System state changed to opposite condition"),
            self._step(4, f"Execute {req.main_verb} {req.direct_object} with negated condition",
                        "System follows the default/alternative flow"),
            self._step(5, f"Toggle condition rapidly (simulate race condition)",
                        "System handles concurrent state changes without data corruption"),
        ]

        expected = (f"System correctly handles both states of the condition; "
                    f"no data corruption during state transitions; "
                    f"behavior matches requirement specification")

        return title, desc, preconditions, steps, expected, test_data

    # ------------------------------------------------------------------
    # Helpers for smart data generation
    # ------------------------------------------------------------------

    @staticmethod
    def _step(order: int, action: str, expected: str) -> Dict[str, Any]:
        return {"order": order, "action": action, "expected_result": expected}

    @staticmethod
    def _actor(req: ParsedRequirement) -> str:
        subj = req.subject.lower()
        if subj in ("system", "application", "platform", "the system", "the application"):
            return "authorized user"
        return subj

    @staticmethod
    def _smart_preconditions(req: ParsedRequirement, is_valid: bool) -> List[str]:
        preconds = ["System is accessible and running"]

        # Domain-specific
        domain = req.domain
        if domain == "healthcare":
            preconds.append("Test patient record exists in the system")
            preconds.append("User has valid medical practitioner credentials")
        elif domain == "banking":
            preconds.append("Test account exists with known balance")
            preconds.append("User has banking permissions")
        elif domain == "ecommerce":
            preconds.append("Product catalog is populated with test data")
            preconds.append("User has a registered account")
        elif domain == "authentication":
            preconds.append("User account exists with known credentials")
            preconds.append("Authentication service is operational")
        else:
            preconds.append("User is authenticated with appropriate permissions")

        if is_valid:
            preconds.append("Test data is prepared and validated")
        return preconds

    @staticmethod
    def _smart_test_data(req: ParsedRequirement, valid: bool) -> Dict[str, Any]:
        """Generate test data based on the requirement's entities and domain."""
        data: Dict[str, Any] = {}
        entities = [e.lower() for e in req.entities]
        obj = req.direct_object.lower()
        full_text = req.original.lower()

        # Build data from entities and objects mentioned
        # Order matters: more specific patterns first
        if any(kw in obj or kw in full_text for kw in ["notification", "alert", "sms", "message queue"]):
            if valid:
                data["recipient"] = "admin@company.com"
                data["alert_type"] = "critical_error"
                data["message"] = "System alert: CPU usage above 95%"
                data["channel"] = "email"
            else:
                data["recipient"] = ""
                data["alert_type"] = ""
                data["message"] = ""
                data["channel"] = "INVALID_CHANNEL"

        elif any(kw in obj or kw in full_text for kw in ["image", "photo", "picture", "avatar", "upload file", "attachment"]):
            if valid:
                data["file_name"] = "profile_photo.png"
                data["file_type"] = "image/png"
                data["file_size_mb"] = 2.5
                data["resolution"] = "800x600"
            else:
                data["file_name"] = "malware.exe"
                data["file_type"] = "application/exe"
                data["file_size_mb"] = 50  # Exceeds limit
                data["resolution"] = "0x0"

        elif any(kw in obj or kw in full_text for kw in ["export", "report", "csv", "pdf", "download"]):
            if valid:
                data["export_format"] = "CSV"
                data["date_from"] = "2025-01-01"
                data["date_to"] = "2025-12-31"
                data["record_count"] = 150
            else:
                data["export_format"] = "INVALID"
                data["date_from"] = "2030-01-01"  # Future date
                data["date_to"] = "2020-01-01"    # Before start date
                data["record_count"] = 0

        elif any(kw in obj or kw in full_text for kw in ["authenticate", "login", "password", "credential", "registration", "sign up", "sign in"]):
            if valid:
                data["email"] = "testuser@example.com"
                data["password"] = "SecureP@ss123"
                data["username"] = "test_user_01"
            else:
                data["email"] = "invalid-email-format"
                data["password"] = "123"  # Too short
                data["username"] = ""     # Empty

        elif any(kw in obj for kw in ["price", "total", "cart", "checkout"]) or any(kw in full_text for kw in ["shopping cart", "discount code", "tax rate"]):
            if valid:
                data["product_id"] = "PROD-001"
                data["quantity"] = 2
                data["unit_price"] = 29.99
                data["discount_code"] = "SAVE10"
                data["expected_total"] = 53.98
            else:
                data["product_id"] = "NONEXISTENT"
                data["quantity"] = -1
                data["unit_price"] = "not_a_number"
                data["discount_code"] = "EXPIRED_CODE"

        elif any(kw in obj or kw in full_text for kw in ["paginate", "page size", "page number", "result", "search", "sort"]):
            if valid:
                data["page_number"] = 1
                data["page_size"] = 20
                data["sort_by"] = "created_date"
                data["sort_order"] = "DESC"
            else:
                data["page_number"] = -1
                data["page_size"] = 0
                data["sort_by"] = "nonexistent_column"
                data["sort_order"] = "INVALID"

        elif any(kw in obj or kw in full_text for kw in ["product", "order", "item", "catalog", "inventory"]):
            if valid:
                data["product_id"] = "PROD-001"
                data["quantity"] = 2
                data["price"] = 29.99
            else:
                data["product_id"] = "NONEXISTENT"
                data["quantity"] = -1
                data["price"] = "not_a_number"

        elif any(kw in obj or kw in full_text for kw in ["appointment", "schedule", "booking"]):
            if valid:
                data["date"] = "2026-05-15"
                data["time_slot"] = "09:00-09:30"
                data["patient_id"] = "PAT-001"
            else:
                data["date"] = "2020-01-01"  # Past date
                data["time_slot"] = "25:00"   # Invalid time
                data["patient_id"] = ""

        elif any(kw in obj or kw in full_text for kw in ["payment", "transaction", "transfer", "history"]):
            if valid:
                data["amount"] = 150.00
                data["currency"] = "VND"
                data["account_from"] = "ACC-001"
                data["account_to"] = "ACC-002"
            else:
                data["amount"] = -50.00
                data["currency"] = "INVALID"
                data["account_from"] = "NONEXISTENT"

        elif any(kw in obj for kw in ["record", "data"]):
            if valid:
                data["record_id"] = "REC-001"
                data["format"] = "json"
            else:
                data["record_id"] = ""
                data["format"] = "exe"  # Invalid format

        elif any(kw in obj for kw in ["password", "credential", "token"]):
            if valid:
                data["current_password"] = "OldP@ss123"
                data["new_password"] = "NewSecure@456"
                data["confirm_password"] = "NewSecure@456"
            else:
                data["current_password"] = "wrong_password"
                data["new_password"] = "12"
                data["confirm_password"] = "mismatch"

        else:
            # Generic but still meaningful
            if valid:
                data["input_field"] = f"valid_{req.main_verb}_data"
                data["status"] = "active"
            else:
                data["input_field"] = ""
                data["status"] = None

        # Add constraint-derived data
        for nc in req.numeric_constraints:
            key = f"constraint_{nc['unit'].replace(' ', '_')}"
            if valid:
                data[key] = nc["value"]
            else:
                data[key] = nc["value"] + 100  # Exceeds limit

        return data

    @staticmethod
    def _summarize_data(data: Dict[str, Any]) -> str:
        """One-line summary of test data for use in step descriptions."""
        if not data:
            return "standard test data"
        items = [f"{k}={v}" for k, v in list(data.items())[:3]]
        suffix = f" (+{len(data)-3} more)" if len(data) > 3 else ""
        return ", ".join(items) + suffix

    @staticmethod
    def _postconditions(test_type: TestType) -> List[str]:
        base = ["System remains in a stable state"]
        if test_type in (TestType.HAPPY_PATH, TestType.DATA_INTEGRITY):
            base.append("Created/modified data is verifiable in the database")
        elif test_type == TestType.NEGATIVE:
            base.append("No partial or corrupt data was saved")
        elif test_type == TestType.SECURITY:
            base.append("Security event was logged for audit")
        return base

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    @staticmethod
    def _calc_effort(steps: List[Dict], test_type: TestType,
                     req: ParsedRequirement) -> float:
        base = len(steps) * 0.15  # 9 min per step
        # Type complexity
        type_bonus = {
            TestType.SECURITY: 0.5,
            TestType.PERFORMANCE: 0.7,
            TestType.INTEGRATION: 0.6,
            TestType.BOUNDARY: 0.3,
            TestType.DATA_INTEGRITY: 0.3,
            TestType.EDGE_CASE: 0.4,
            TestType.NEGATIVE: 0.2,
            TestType.HAPPY_PATH: 0.1,
        }
        base += type_bonus.get(test_type, 0.2)
        # Domain complexity
        domain_bonus = {"healthcare": 0.3, "banking": 0.3, "ecommerce": 0.1}
        base += domain_bonus.get(req.domain, 0.1)
        # Constraint complexity
        if req.numeric_constraints:
            base += 0.2
        return round(base, 1)

    @staticmethod
    def _calc_quality(req: ParsedRequirement, plan: TestScenarioPlan,
                      steps: List[Dict]) -> float:
        """Quality based on how well we understood the requirement."""
        q = req.parse_confidence * 0.4  # NLP confidence matters most
        # Steps specificity bonus
        q += min(len(steps) * 0.06, 0.25)
        # Rationale quality
        if plan.rationale and len(plan.rationale) > 20:
            q += 0.1
        # Domain match bonus
        if req.domain != "general":
            q += 0.1
        # Constraint-aware bonus
        if req.numeric_constraints and plan.test_type == TestType.BOUNDARY:
            q += 0.15
        return round(min(q, 0.98), 2)


# ============================================================================
# PART 4: PUBLIC API (AITestGenerator)
# ============================================================================

class AITestGenerator:
    """Main public API — drop-in replacement for the old AITestGenerator."""

    def __init__(self):
        self.analyzer = NLPRequirementAnalyzer()
        self.strategy = SemanticTestStrategyEngine()
        self.builder = IntelligentTestCaseBuilder()

    def generate(self, requirements: List[str], max_tests: int = 10) -> Dict[str, Any]:
        all_test_cases: List[Dict[str, Any]] = []
        errors: List[str] = []
        seen_hashes: Set[str] = set()

        for req_idx, req_text in enumerate(requirements, 1):
            req_text = req_text.strip()
            if not req_text:
                continue
            try:
                parsed = self.analyzer.analyze(req_text)
                plans = self.strategy.plan_tests(parsed)

                for plan in plans:
                    if len(all_test_cases) >= max_tests * len(requirements):
                        break
                    tc = self.builder.build(parsed, plan, req_idx)

                    # Dedup by title hash
                    h = hashlib.md5(tc["title"].encode()).hexdigest()
                    if h in seen_hashes:
                        continue
                    seen_hashes.add(h)

                    all_test_cases.append(tc)

            except Exception as e:
                errors.append(f"Error processing '{req_text[:60]}': {str(e)}")

        # Summary
        summary = self._build_summary(all_test_cases)

        return {
            "test_cases": all_test_cases,
            "summary": summary,
            "errors": errors,
        }

    # Keep backward-compatible methods
    def submit_feedback(self, **kwargs) -> bool:
        """Placeholder for feedback — store for future use."""
        return True

    def get_system_stats(self) -> Dict[str, Any]:
        return {
            "generation": {"total": 0},
            "feedback": {"total": 0},
            "learning": {
                "total_feedback_entries": 0,
                "scenario_success_rates": {},
                "strengths": ["Deep NLP analysis", "Context-specific test generation"],
                "weaknesses": [],
                "recommendations": ["Collect more user feedback to improve quality scoring"],
            },
            "system_health": {
                "status": "healthy",
                "score": 0.85,
                "version": "2.1-nlp",
            },
        }

    @staticmethod
    def _build_summary(test_cases: List[Dict]) -> Dict[str, Any]:
        if not test_cases:
            return {
                "total_test_cases": 0,
                "avg_quality_score": 0,
                "avg_effort_hours": 0,
                "total_effort_hours": 0,
                "test_type_distribution": {},
                "domain_distribution": {},
                "priority_distribution": {},
            }

        type_dist: Dict[str, int] = {}
        domain_dist: Dict[str, int] = {}
        priority_dist: Dict[str, int] = {}
        total_quality = 0.0
        total_effort = 0.0

        for tc in test_cases:
            tt = tc.get("test_type", "unknown")
            type_dist[tt] = type_dist.get(tt, 0) + 1
            d = tc.get("domain", "general")
            domain_dist[d] = domain_dist.get(d, 0) + 1
            p = tc.get("priority", "Medium")
            priority_dist[p] = priority_dist.get(p, 0) + 1
            total_quality += tc.get("ml_quality_score", 0)
            total_effort += tc.get("effort_hours", 0)

        n = len(test_cases)
        return {
            "total_test_cases": n,
            "avg_quality_score": round(total_quality / n, 3),
            "avg_effort_hours": round(total_effort / n, 2),
            "total_effort_hours": round(total_effort, 2),
            "test_type_distribution": type_dist,
            "domain_distribution": domain_dist,
            "priority_distribution": priority_dist,
        }
