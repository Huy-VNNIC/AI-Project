"""
V2 Refinement Engine
====================

Refines raw requirements into structured User Stories with:
- Proper As a...I want...so that... format
- Given/When/Then acceptance criteria
- Extracted assumptions, constraints, NFRs

As of v3 the heavy lifting is delegated to the **Semantic Understanding
Engine** (see ``requirement_analyzer.task_gen.semantic``).  The legacy
regex-based extractors are kept as fallbacks for when the semantic
engine is disabled or its parser returns very low confidence.
"""
import os
import re
from typing import List, Optional, Tuple
from requirement_analyzer.task_gen.schemas_v2 import (
    Requirement,
    RefinementOutput,
    AcceptanceCriterion,
    SeverityLevel
)

try:
    from requirement_analyzer.task_gen.semantic import (
        ACGenerator,
        SemanticParser,
        StoryGenerator,
        StoryIR,
    )
    _SEMANTIC_AVAILABLE = True
except Exception:  # pragma: no cover - defensive: never break the pipeline
    _SEMANTIC_AVAILABLE = False


class RequirementRefiner:
    """Refines raw requirements into structured user stories"""
    
    # Vietnamese patterns
    VI_ACTOR_KEYWORDS = [
        'quản lý', 'nhân viên', 'khách hàng', 'người dùng', 'admin', 'user',
        'lễ tân', 'giám đốc', 'bác sĩ', 'bệnh nhân', 'giáo viên', 'học sinh'
    ]
    
    VI_ACTION_VERBS = [
        'cần', 'muốn', 'phải', 'được', 'cho phép', 'hỗ trợ', 'cung cấp',
        'quản lý', 'xem', 'tạo', 'sửa', 'xóa', 'tìm kiếm', 'lọc', 'báo cáo'
    ]
    
    VI_VALUE_KEYWORDS = [
        'để', 'nhằm', 'giúp', 'tăng', 'giảm', 'cải thiện', 'tối ưu', 'tiết kiệm'
    ]
    
    # NFR keywords
    NFR_KEYWORDS = {
        'performance': ['hiệu suất', 'nhanh', 'tốc độ', 'thời gian phản hồi'],
        'security': ['bảo mật', 'mã hóa', 'phân quyền', 'xác thực', 'authorization'],
        'usability': ['dễ dùng', 'thân thiện', 'trực quan', 'giao diện'],
        'reliability': ['ổn định', 'sẵn sàng', 'uptime', 'không lỗi'],
        'scalability': ['mở rộng', 'scale', 'tăng trưởng', 'nhiều người dùng']
    }
    
    def __init__(self, use_semantic_engine: Optional[bool] = None) -> None:
        """Initialize refiner.

        Args:
            use_semantic_engine: When ``True``, the new IR-based pipeline
                is used (parser → IR → story/AC generators) with the
                regex layer as a fallback for low-confidence cases.
                When ``False``, only the legacy regex pipeline runs.
                Default: read from env var ``RA_USE_SEMANTIC`` (truthy)
                or auto-enable if the semantic package imported cleanly.
        """
        if use_semantic_engine is None:
            env = os.environ.get("RA_USE_SEMANTIC", "").strip().lower()
            if env in {"0", "false", "no", "off"}:
                use_semantic_engine = False
            else:
                use_semantic_engine = _SEMANTIC_AVAILABLE
        self.use_semantic_engine = bool(use_semantic_engine and _SEMANTIC_AVAILABLE)

        if self.use_semantic_engine:
            self._parser = SemanticParser()
            self._story_gen_vi = StoryGenerator(language="vi")
            self._story_gen_en = StoryGenerator(language="en")
            self._ac_gen_vi = ACGenerator(language="vi")
            self._ac_gen_en = ACGenerator(language="en")
        else:
            self._parser = None  # type: ignore[assignment]

    def refine(self, requirement: Requirement) -> RefinementOutput:
        """Refine a requirement into a structured user story.

        Strategy:
          1. If semantic engine is enabled → parse to IR, render story +
             AC from IR.  Whenever any IR slot is too weak we fall back
             to the legacy regex extractor for that specific slot.
          2. If semantic engine is disabled → run the legacy pipeline.
        """
        if self.use_semantic_engine:
            try:
                return self._refine_via_semantic(requirement)
            except Exception:
                # Hard guarantee: never break the pipeline due to a
                # semantic-layer bug; fall back to the legacy path.
                pass
        return self._refine_legacy(requirement)

    # ── Semantic path ───────────────────────────────────────────────────────────
    def _refine_via_semantic(self, requirement: Requirement) -> RefinementOutput:
        ir: "StoryIR" = self._parser.parse(requirement.original_text)  # type: ignore[union-attr]
        language = requirement.language
        story_gen = self._story_gen_vi if language == "vi" else self._story_gen_en
        ac_gen = self._ac_gen_vi if language == "vi" else self._ac_gen_en

        # ── Story ──────────────────────────────────────────────────────
        user_story = story_gen.render(ir)

        # NFR reframing wins if the requirement is a pure NFR.
        nfr_type = self._detect_nfr_type(requirement.original_text)
        if nfr_type:
            user_story = self._reframe_nfr_user_story(
                requirement.original_text, nfr_type, language,
            )

        # ── Title ──────────────────────────────────────────────────────
        title = StoryGenerator.title_for(ir, language=language)

        # ── Acceptance Criteria ────────────────────────────────────────
        triples = ac_gen.generate(ir)
        severity_map = {
            "Critical": SeverityLevel.CRITICAL,
            "High": SeverityLevel.HIGH,
            "Medium": SeverityLevel.MEDIUM,
            "Low": SeverityLevel.LOW,
        }
        acceptance_criteria: List[AcceptanceCriterion] = [
            AcceptanceCriterion(
                ac_id=f"AC{i + 1}",
                given=t.given,
                when=t.when,
                then=t.then,
                priority=severity_map.get(t.priority, SeverityLevel.MEDIUM),
            )
            for i, t in enumerate(triples)
        ]

        # ── Assumptions / Constraints / NFRs (unchanged legacy logic) ──
        nfrs = self._extract_nfrs(requirement.original_text)
        assumptions = self._extract_assumptions(requirement.original_text, language)
        constraints = self._extract_constraints(requirement.original_text, language)

        changes_summary = self._generate_changes_summary(
            requirement.original_text,
            user_story,
            len(acceptance_criteria),
            len(assumptions),
            len(nfrs),
        )

        return RefinementOutput(
            requirement_id=requirement.requirement_id,
            title=title,
            user_story=user_story,
            acceptance_criteria=acceptance_criteria,
            assumptions=assumptions,
            constraints=constraints,
            non_functional_requirements=nfrs,
            changes_summary=changes_summary,
        )

    # ── Legacy path (regex-based, kept as safety net) ───────────────────────────────────────────────────
    def _refine_legacy(self, requirement: Requirement) -> RefinementOutput:
        """
        Refine a requirement into structured user story
        
        Args:
            requirement: Raw requirement
            
        Returns:
            RefinementOutput with user story, AC, assumptions, constraints, NFRs
        """
        # Extract actor, action, value
        actor = self._extract_actor(requirement.original_text, requirement.language)
        action = self._extract_action(requirement.original_text, requirement.language)
        value = self._extract_value(requirement.original_text, requirement.language)
        
        # Generate user story
        user_story = self._generate_user_story(actor, action, value, requirement.language)
        
        # ── NFR reframing: convert technical-spec wording to user-value wording ─
        nfr_type = self._detect_nfr_type(requirement.original_text)
        if nfr_type:
            user_story = self._reframe_nfr_user_story(requirement.original_text, nfr_type, requirement.language)
        
        # Generate title
        title = self._generate_title(action, requirement.language)
        
        # Generate acceptance criteria
        acceptance_criteria = self._generate_acceptance_criteria(
            requirement.original_text,
            actor,
            action,
            requirement.language
        )
        # Pad to a minimum of 4 AC items so every story has
        # happy-path + invalid-input + permission + system-error coverage.
        acceptance_criteria = self._ensure_min_acceptance_criteria(
            acceptance_criteria,
            actor=actor,
            language=requirement.language,
            min_ac=4,
        )

        # Extract NFRs
        nfrs = self._extract_nfrs(requirement.original_text)
        
        # Extract assumptions
        assumptions = self._extract_assumptions(requirement.original_text, requirement.language)
        
        # Extract constraints
        constraints = self._extract_constraints(requirement.original_text, requirement.language)
        
        # Changes summary
        changes_summary = self._generate_changes_summary(
            requirement.original_text,
            user_story,
            len(acceptance_criteria),
            len(assumptions),
            len(nfrs)
        )
        
        return RefinementOutput(
            requirement_id=requirement.requirement_id,
            title=title,
            user_story=user_story,
            acceptance_criteria=acceptance_criteria,
            assumptions=assumptions,
            constraints=constraints,
            non_functional_requirements=nfrs,
            changes_summary=changes_summary
        )
    
    def _extract_actor(self, text: str, language: str) -> str:
        """Extract actor from requirement"""
        text_lower = text.lower()
        
        # Check for explicit actor mentions
        for actor in self.VI_ACTOR_KEYWORDS:
            if actor in text_lower:
                return actor.capitalize()
        
        # Default actors
        if language == "vi":
            return "Người dùng"
        return "User"
    
    def _extract_action(self, text: str, language: str) -> str:
        """Extract main action from requirement.

        Returns a *clean* action phrase suitable for the
        "Là một X, tôi muốn <action>, để Y" template — i.e. without:
          - leading particles ("phải", "cần", "được", "to")
          - subject-duplication patterns ("cho phép khách hàng …",
            "hệ thống cho phép người dùng …")
          - trailing punctuation
        """
        text_lower = text.lower()
        snippet: str = ""

        # Find action verbs
        for verb in self.VI_ACTION_VERBS:
            if verb in text_lower:
                idx = text_lower.find(verb)
                snippet = text[idx:min(idx + 100, len(text))]
                snippet = re.sub(r"\s+", " ", snippet).strip()
                break

        if not snippet:
            snippet = text[:80].strip()

        return self._clean_action_text(snippet)

    # ── Action wording cleaner ─────────────────────────────────────────────
    # Patterns that introduce a redundant subject after the actor token —
    # produce duplications like "Là một Khách hàng, tôi muốn cho phép
    # khách hàng đặt phòng". These are stripped before assembly.
    _DUP_SUBJECT_PATTERNS = [
        # "cho phép <actor>" / "the system allows <actor> to"
        r"^cho phép\s+(khách hàng|người dùng|bệnh nhân|user|customer|admin|quản trị viên|nhân viên|bác sĩ|lễ tân)\b\s*",
        r"^hệ thống\s+cho phép\s+(khách hàng|người dùng|bệnh nhân|user|customer|admin|bác sĩ)\b\s*",
        r"^hệ thống\s+(cho phép|hỗ trợ|cung cấp)\b\s*",
        r"^the\s+system\s+allows\s+(the\s+)?(user|customer|patient|admin|doctor)\s+to\s+",
        r"^allow\s+(the\s+)?(user|customer|patient|admin|doctor)\s+to\s+",
        # Bare-subject prefix: "khách hàng có thể …" → "…"
        r"^(khách hàng|người dùng|bệnh nhân|bác sĩ|quản trị viên|quản lý|nhân viên|lễ tân|admin|user|customer|patient|doctor|staff)\s+(có thể|được|sẽ|cần|phải)\s+",
        # Bare noun-subject (excluding "quản lý" because it is also a verb meaning "manage")
        r"^(khách hàng|người dùng|bệnh nhân|bác sĩ|quản trị viên|lễ tân|admin|user|customer|patient|doctor|staff)\s+",
        # System-as-subject: "hệ thống gửi email …" → "gửi email …"
        r"^hệ thống\s+",
        r"^the\s+system\s+",
    ]
    _LEADING_PARTICLES = ("phải ", "cần ", "được ", "có thể ", "to ")

    def _clean_action_text(self, text: str) -> str:
        """Strip subject-duplication, leading particles, and trailing punctuation."""
        if not text:
            return text
        cleaned = text.strip()
        # Strip duplication patterns iteratively (case-insensitive)
        for _ in range(3):
            changed = False
            for pattern in self._DUP_SUBJECT_PATTERNS:
                new = re.sub(pattern, "", cleaned, flags=re.IGNORECASE).strip()
                if new != cleaned:
                    cleaned = new
                    changed = True
            if not changed:
                break
        # Strip leading particles
        low = cleaned.lower()
        for p in self._LEADING_PARTICLES:
            if low.startswith(p):
                cleaned = cleaned[len(p):].strip()
                low = cleaned.lower()
                break
        # Trim trailing punctuation
        cleaned = cleaned.rstrip(" .;,:").strip()
        # Lowercase the first letter so it reads naturally after "tôi muốn"
        if cleaned and cleaned[0].isupper() and len(cleaned) > 1 and cleaned[1].islower():
            cleaned = cleaned[0].lower() + cleaned[1:]
        return cleaned
    
    def _extract_value(self, text: str, language: str) -> str:
        """Extract value proposition from requirement"""
        text_lower = text.lower()
        
        # Find value keywords
        for keyword in self.VI_VALUE_KEYWORDS:
            if keyword in text_lower:
                idx = text_lower.find(keyword)
                snippet = text[idx:min(idx+80, len(text))]
                return snippet.strip()
        
        # Default values
        if language == "vi":
            return "để cải thiện hiệu quả công việc"
        return "to improve work efficiency"
    
    def _generate_user_story(self, actor: str, action: str, value: str, language: str) -> str:
        """Generate user story in proper format"""
        # Clean action - remove redundant Vietnamese particles
        if language == "vi":
            # Remove redundant " phải " at start of action
            action = action.strip()
            if action.lower().startswith("phải "):
                action = action[5:].strip()
            
            # Clean up the value/benefit - remove if redundant particle already exists
            value = value.strip()
            
            # Remove leading particles from value if present
            for particle in ["để", "nhằm", "giúp"]:
                if value.lower().startswith(particle + " "):
                    value = value[len(particle)+1:].strip()
                    break
            
            if not value or value == ".":
                value = "hoàn thành công việc một cách hiệu quả"
            
            return f"Là một {actor}, tôi muốn {action}, để {value}."
        else:
            # English version - ensure proper structure
            action = action.strip()
            if action.startswith("to "):
                action = action[3:].strip()
            
            value = value.strip()
            
            # Remove leading particles from value if present
            if value.lower().startswith("so that "):
                value = value[8:].strip()
            
            if not value or value == ".":
                value = "accomplish tasks more effectively"
            
            return f"As a {actor}, I want to {action}, so that {value}."

    # ── NFR detection & reframing ──────────────────────────────────────────────
    _PURE_SECURITY_KWS = {
        'ssl', 'tls', 'https', 'mã hóa', 'encrypt', 'firewall',
        'penetration', 'vulnerability', 'cybersecurity', 'data breach',
        'bảo mật dữ liệu', 'data security', 'audit log',
    }
    _PERFORMANCE_KWS = {
        'hiệu suất', 'performance', 'response time', 'thời gian phản hồi',
        'throughput', 'uptime', 'availability', 'latency', 'tốc độ tải',
        'concurrent', 'scalab', 'mở rộng', 'tải cao', 'high load',
    }
    _COMPLIANCE_KWS = {
        'gdpr', 'hipaa', 'pci', 'iso', 'tuân thủ', 'compliance', 'regulation',
        'quy định pháp luật', 'legal requirement', 'standard',
    }

    def _detect_nfr_type(self, text: str) -> str:
        """
        Returns NFR type string ('security'|'performance'|'availability'|'compliance'|'')
        Only matches *pure* NFRs — functional features with security keywords are excluded.
        """
        t = text.lower()
        # Exclude lines that are clearly functional (management/booking/CRUD actions)
        functional_overrides = [
            'quản lý', 'đặt phòng', 'đặt lịch', 'thanh toán', 'tạo mới',
            'thêm mới', 'chỉnh sửa', 'xem danh sách', 'manage', 'book',
            'reserve', 'create', 'update', 'delete', 'invoice',
        ]
        if any(kw in t for kw in functional_overrides):
            return ''  # functional requirement, no reframing
        if any(kw in t for kw in self._PURE_SECURITY_KWS):
            return 'security'
        if any(kw in t for kw in self._COMPLIANCE_KWS):
            return 'compliance'
        if any(kw in t for kw in self._PERFORMANCE_KWS):
            if 'uptime' in t or 'availability' in t or 'sẵn sàng' in t:
                return 'availability'
            return 'performance'
        return ''

    def _reframe_nfr_user_story(self, text: str, nfr_type: str, language: str) -> str:
        """
        Rewrite technical-spec NFR into user-value framing.
        e.g. "I want SSL/TLS" → "I want my data to be securely transmitted"
        """
        vi = language == 'vi'
        if nfr_type == 'security':
            return (
                "Là một khách hàng, tôi muốn thông tin cá nhân và dữ liệu giao dịch của tôi "
                "được bảo vệ an toàn, để tránh rủi ro rò rỉ hoặc truy cập trái phép."
                if vi else
                "As a customer, I want my personal and transaction data to be securely protected, "
                "so that it is safe from unauthorized access or data breaches."
            )
        if nfr_type == 'performance':
            import re
            m = re.search(r'(\d+)\s*(?:giây|second|ms|phút|minute)', text.lower())
            limit = m.group(1) + (' giây' if vi else ' seconds') if m else ('3 giây' if vi else '3 seconds')
            return (
                f"Là một người dùng, tôi muốn hệ thống phản hồi trong vòng {limit} "
                "để tôi có thể hoàn thành công việc mà không bị chờ đợi."
                if vi else
                f"As a user, I want the system to respond within {limit} "
                "so that I can complete tasks without frustrating delays."
            )
        if nfr_type == 'availability':
            return (
                "Là một người dùng, tôi muốn hệ thống luôn hoạt động ổn định và sẵn sàng, "
                "để công việc hàng ngày của tôi không bị gián đoạn."
                if vi else
                "As a user, I want the system to be continuously available, "
                "so that my daily work is never disrupted by downtime."
            )
        if nfr_type == 'compliance':
            return (
                "Là một quản trị viên, tôi muốn hệ thống tuân thủ các quy định và tiêu chuẩn "
                "bảo mật hiện hành, để tránh rủi ro pháp lý và bảo vệ quyền lợi người dùng."
                if vi else
                "As an administrator, I want the system to comply with applicable regulations and "
                "security standards, so that legal risks are minimized and user rights are protected."
            )
        return ''  # fallback — keep original

    def _generate_title(self, action: str, language: str) -> str:
        """Generate concise title"""
        # Clean action
        action = re.sub(r'\s+', ' ', action).strip()
        words = action.split()
        
        # Take first 5-7 words
        title_words = words[:7]
        title = ' '.join(title_words)
        
        # Capitalize first letter
        if title:
            title = title[0].upper() + title[1:]
        
        return title[:100]  # Max 100 chars
    
    def _generate_acceptance_criteria(
        self,
        text: str,
        actor: str,
        action: str,
        language: str
    ) -> List[AcceptanceCriterion]:
        """Generate specific Given/When/Then acceptance criteria based on requirement content"""
        criteria = []
        text_lower = text.lower()

        # ── Detect requirement sub-type ────────────────────────────────────────
        # is_pure_security: only TRUE for infra/encryption requirements (not RBAC features)
        is_pure_security = any(kw in text_lower for kw in [
            'mã hóa', 'ssl', 'tls', 'https', 'encrypt', 'firewall',
            'penetration', 'vulnerability', 'audit log', 'cybersecurity',
            'bảo mật dữ liệu', 'data security', 'data breach',
        ])
        # is_rbac_management: functional requirement about roles/permissions
        is_rbac_management = (
            not is_pure_security
            and any(kw in text_lower for kw in [
                'phân quyền', 'role', 'permission', 'access control',
                'quản lý quyền', 'phân cấp', 'role-based',
            ])
        )
        # Keep backward-compat alias used by downstream branches
        is_security = is_pure_security
        is_performance = any(kw in text_lower for kw in [
            'hiệu suất', 'performance', 'tốc độ', 'thời gian phản hồi',
            'response time', 'uptime', 'tải', 'load', 'concurrent',
        ])
        is_login = any(kw in text_lower for kw in [
            'đăng nhập', 'login', 'sign in', 'authenticate',
        ])
        is_register = any(kw in text_lower for kw in [
            'đăng ký', 'register', 'sign up', 'tạo tài khoản', 'create account',
        ])
        is_search = any(kw in text_lower for kw in [
            'tìm kiếm', 'search', 'lọc', 'filter', 'tra cứu',
        ])
        is_payment = any(kw in text_lower for kw in [
            'thanh toán', 'payment', 'pay', 'billing', 'hóa đơn', 'invoice',
        ])
        is_crud_create = any(kw in text_lower for kw in ['tạo', 'thêm', 'create', 'add', 'new'])
        is_crud_update = any(kw in text_lower for kw in ['cập nhật', 'sửa', 'update', 'edit', 'modify'])
        is_crud_delete = any(kw in text_lower for kw in ['xóa', 'delete', 'remove'])
        is_report = any(kw in text_lower for kw in ['báo cáo', 'report', 'thống kê', 'statistic'])
        is_file_upload = any(kw in text_lower for kw in ['tải lên', 'upload', 'import file'])

        # Extract numeric limits from text (e.g. "5 seconds", "100 users")
        import re
        time_match = re.search(r'(\d+)\s*(?:giây|second|ms|millisecond|phút|minute)', text_lower)
        user_match = re.search(r'(\d+)\+?\s*(?:người dùng|user|concurrent)', text_lower)
        time_limit = f"{time_match.group(1)} seconds" if time_match else "3 seconds"
        user_count = user_match.group(1) if user_match else "1000"

        # ── Branch: Security / NFR requirements ───────────────────────────────
        if is_security:
            if language == "vi":
                criteria.append(AcceptanceCriterion(ac_id="AC1",
                    given=f"Hệ thống đang xử lý dữ liệu nhạy cảm",
                    when="Dữ liệu được truyền qua mạng",
                    then="Toàn bộ dữ liệu được mã hóa bằng TLS 1.2+ và không thể đọc dưới dạng plain text",
                    priority=SeverityLevel.CRITICAL))
                criteria.append(AcceptanceCriterion(ac_id="AC2",
                    given="Người dùng không có quyền truy cập chức năng",
                    when="Gửi request đến API yêu cầu đặc quyền",
                    then="Hệ thống trả về HTTP 403 Forbidden với thông báo lỗi rõ ràng",
                    priority=SeverityLevel.HIGH))
                criteria.append(AcceptanceCriterion(ac_id="AC3",
                    given="Có sự kiện bảo mật (đăng nhập sai 5 lần)",
                    when="Hệ thống phát hiện hành vi bất thường",
                    then="Tài khoản bị khóa tạm thời 15 phút và ghi log sự kiện",
                    priority=SeverityLevel.HIGH))
            else:
                criteria.append(AcceptanceCriterion(ac_id="AC1",
                    given="System is handling sensitive data in transit",
                    when="Data is transmitted over the network",
                    then="All data is encrypted with TLS 1.2+ and unreadable as plain text",
                    priority=SeverityLevel.CRITICAL))
                criteria.append(AcceptanceCriterion(ac_id="AC2",
                    given="User lacks required permissions for the resource",
                    when="A request is sent to a privileged API endpoint",
                    then="System returns HTTP 403 Forbidden with a descriptive error message",
                    priority=SeverityLevel.HIGH))
                criteria.append(AcceptanceCriterion(ac_id="AC3",
                    given="5 consecutive failed login attempts from the same IP",
                    when="The 6th login attempt is made",
                    then="Account is locked for 15 minutes and security event is written to audit log",
                    priority=SeverityLevel.HIGH))
            return criteria

        if is_performance:
            if language == "vi":
                criteria.append(AcceptanceCriterion(ac_id="AC1",
                    given=f"Hệ thống đang chạy với {user_count} người dùng đồng thời",
                    when="Người dùng gửi request đến bất kỳ trang nào",
                    then=f"Thời gian phản hồi ≤ {time_limit} với 95% requests (P95 latency)",
                    priority=SeverityLevel.CRITICAL))
                criteria.append(AcceptanceCriterion(ac_id="AC2",
                    given="Tải hệ thống tăng đột biến gấp 3 lần bình thường",
                    when="Trong giờ cao điểm (peak hours)",
                    then="Hệ thống vẫn đáp ứng SLA: uptime ≥ 99.9%, không mất dữ liệu",
                    priority=SeverityLevel.HIGH))
                criteria.append(AcceptanceCriterion(ac_id="AC3",
                    given="Kết nối cơ sở dữ liệu bị chậm",
                    when="Response time backend > 5 giây",
                    then="Circuit breaker kích hoạt, trả về cached response hoặc thông báo lỗi thân thiện",
                    priority=SeverityLevel.MEDIUM))
            else:
                criteria.append(AcceptanceCriterion(ac_id="AC1",
                    given=f"System running with {user_count} concurrent users",
                    when="User sends a request to any page",
                    then=f"Response time ≤ {time_limit} for 95% of requests (P95 latency)",
                    priority=SeverityLevel.CRITICAL))
                criteria.append(AcceptanceCriterion(ac_id="AC2",
                    given="System load spikes to 3x normal traffic",
                    when="During peak hours",
                    then="System maintains SLA: uptime ≥ 99.9%, zero data loss",
                    priority=SeverityLevel.HIGH))
                criteria.append(AcceptanceCriterion(ac_id="AC3",
                    given="Database connection is slow",
                    when="Backend response time exceeds 5 seconds",
                    then="Circuit breaker activates, returns cached response or a user-friendly error",
                    priority=SeverityLevel.MEDIUM))
            return criteria

        # ── Branch: RBAC / Role & Permission Management ─────────────────────────
        if is_rbac_management:
            if language == "vi":
                criteria.append(AcceptanceCriterion(ac_id="AC1",
                    given="Quản trị viên đã đăng nhập và có quyền quản lý vai trò",
                    when="Tạo vai trò mới và gán quyền truy cập cho người dùng",
                    then="Người dùng được áp dụng quyền mới ngay lập tức mà không cần đăng xuất",
                    priority=SeverityLevel.HIGH))
                criteria.append(AcceptanceCriterion(ac_id="AC2",
                    given="Người dùng có vai trò 'Viewer' đang đăng nhập",
                    when="Cố gắng truy cập chức năng chỉ dành cho vai trò 'Admin'",
                    then="Hệ thống từ chối truy cập và hiển thị thông báo 'Bạn không có quyền thực hiện thao tác này'",
                    priority=SeverityLevel.HIGH))
                criteria.append(AcceptanceCriterion(ac_id="AC3",
                    given="Quản trị viên thu hồi quyền của người dùng",
                    when="Người dùng thực hiện hành động đã bị thu hồi quyền",
                    then="Hành động bị từ chối trong vòng 30 giây và session được làm mới tự động",
                    priority=SeverityLevel.MEDIUM))
            else:
                criteria.append(AcceptanceCriterion(ac_id="AC1",
                    given="Admin is logged in with role-management privileges",
                    when="Creates a new role and assigns permissions to a user",
                    then="User's new permissions take effect immediately without requiring logout",
                    priority=SeverityLevel.HIGH))
                criteria.append(AcceptanceCriterion(ac_id="AC2",
                    given="User with 'Viewer' role is logged in",
                    when="Attempts to access a feature restricted to 'Admin' role",
                    then="Access is denied and message 'You do not have permission to perform this action' is shown",
                    priority=SeverityLevel.HIGH))
                criteria.append(AcceptanceCriterion(ac_id="AC3",
                    given="Admin revokes a user's specific permission",
                    when="User attempts the now-forbidden action",
                    then="Action is rejected within 30 seconds and user session is refreshed",
                    priority=SeverityLevel.MEDIUM))
            return criteria

        # ── Branch: Login ───────────────────────────────────────────────────────
        if is_login:
            if language == "vi":
                criteria.append(AcceptanceCriterion(ac_id="AC1",
                    given="Người dùng đã có tài khoản hợp lệ",
                    when="Nhập đúng email và mật khẩu, nhấn Đăng nhập",
                    then="Hệ thống xác thực thành công, chuyển hướng đến trang chủ trong vòng 2 giây",
                    priority=SeverityLevel.HIGH))
                criteria.append(AcceptanceCriterion(ac_id="AC2",
                    given="Người dùng nhập sai mật khẩu",
                    when="Nhấn nút Đăng nhập",
                    then='Hiển thị thông báo "Email hoặc mật khẩu không đúng", không tiết lộ trường nào sai',
                    priority=SeverityLevel.HIGH))
                criteria.append(AcceptanceCriterion(ac_id="AC3",
                    given="Người dùng để trống trường email",
                    when="Nhấn nút Đăng nhập",
                    then='Hiển thị lỗi validation ngay trên trường: "Email không được để trống"',
                    priority=SeverityLevel.MEDIUM))
            else:
                criteria.append(AcceptanceCriterion(ac_id="AC1",
                    given="User has a valid account with verified email",
                    when="Enters correct email and password, clicks Login",
                    then="System authenticates and redirects to home page within 2 seconds; JWT token issued",
                    priority=SeverityLevel.HIGH))
                criteria.append(AcceptanceCriterion(ac_id="AC2",
                    given="User enters incorrect password",
                    when="Clicks Login",
                    then='System displays "Invalid email or password" without revealing which field is wrong',
                    priority=SeverityLevel.HIGH))
                criteria.append(AcceptanceCriterion(ac_id="AC3",
                    given="Email field is left empty",
                    when="User clicks Login",
                    then='Inline validation error appears: "Email is required" before form submission',
                    priority=SeverityLevel.MEDIUM))
            return criteria

        # ── Branch: Register ────────────────────────────────────────────────────
        if is_register:
            if language == "vi":
                criteria.append(AcceptanceCriterion(ac_id="AC1",
                    given="Người dùng mới điền đầy đủ thông tin hợp lệ",
                    when="Nhấn nút Đăng ký",
                    then="Tài khoản được tạo, email xác nhận gửi đến hòm thư trong vòng 30 giây",
                    priority=SeverityLevel.HIGH))
                criteria.append(AcceptanceCriterion(ac_id="AC2",
                    given="Email đã tồn tại trong hệ thống",
                    when="Nhấn nút Đăng ký",
                    then='Hiển thị thông báo lỗi: "Email đã được sử dụng", gợi ý đăng nhập hoặc đặt lại mật khẩu',
                    priority=SeverityLevel.HIGH))
                criteria.append(AcceptanceCriterion(ac_id="AC3",
                    given="Mật khẩu ít hơn 8 ký tự hoặc thiếu ký tự đặc biệt",
                    when="Người dùng nhập mật khẩu",
                    then="Hiển thị chỉ dẫn: mật khẩu tối thiểu 8 ký tự, gồm chữ hoa, chữ số và ký tự đặc biệt",
                    priority=SeverityLevel.MEDIUM))
            else:
                criteria.append(AcceptanceCriterion(ac_id="AC1",
                    given="New user fills all required fields with valid data",
                    when="Clicks Register",
                    then="Account created in DB, confirmation email sent within 30 seconds",
                    priority=SeverityLevel.HIGH))
                criteria.append(AcceptanceCriterion(ac_id="AC2",
                    given="Email already exists in the system",
                    when="User submits registration form",
                    then='Error shown: "Email already in use", with link to login or reset password',
                    priority=SeverityLevel.HIGH))
                criteria.append(AcceptanceCriterion(ac_id="AC3",
                    given="Password is fewer than 8 characters",
                    when="User types in password field",
                    then="Inline hint: min 8 chars, must include uppercase, digit, and special character",
                    priority=SeverityLevel.MEDIUM))
            return criteria

        # ── Branch: Search / Filter ─────────────────────────────────────────────
        if is_search:
            if language == "vi":
                criteria.append(AcceptanceCriterion(ac_id="AC1",
                    given="Có 50+ bản ghi trong cơ sở dữ liệu",
                    when="Người dùng nhập từ khóa hợp lệ và nhấn Tìm kiếm",
                    then="Kết quả hiển thị trong vòng 2 giây, tối đa 20 kết quả mỗi trang, phân trang rõ ràng",
                    priority=SeverityLevel.HIGH))
                criteria.append(AcceptanceCriterion(ac_id="AC2",
                    given="Từ khóa tìm kiếm không khớp với bản ghi nào",
                    when="Người dùng nhấn Tìm kiếm",
                    then='Hiển thị thông báo: "Không tìm thấy kết quả phù hợp" và gợi ý tìm kiếm khác',
                    priority=SeverityLevel.MEDIUM))
                criteria.append(AcceptanceCriterion(ac_id="AC3",
                    given="Người dùng áp dụng bộ lọc theo danh mục",
                    when="Chọn bộ lọc và nhấn Áp dụng",
                    then="Kết quả chỉ hiển thị các mục khớp tiêu chí lọc, số lượng kết quả được hiển thị",
                    priority=SeverityLevel.MEDIUM))
            else:
                criteria.append(AcceptanceCriterion(ac_id="AC1",
                    given="50+ records exist in the database",
                    when="User enters a valid keyword and clicks Search",
                    then="Results displayed within 2 seconds, max 20 items per page with pagination controls",
                    priority=SeverityLevel.HIGH))
                criteria.append(AcceptanceCriterion(ac_id="AC2",
                    given="Search keyword matches no records",
                    when="User submits search",
                    then='"No results found" message displayed with suggestions to try different keywords',
                    priority=SeverityLevel.MEDIUM))
                criteria.append(AcceptanceCriterion(ac_id="AC3",
                    given="User applies a category filter",
                    when="Filter is selected and applied",
                    then="Only items matching filter criteria are shown; result count is displayed",
                    priority=SeverityLevel.MEDIUM))
            return criteria

        # ── Branch: Payment ──────────────────────────────────────────────────────
        if is_payment:
            if language == "vi":
                criteria.append(AcceptanceCriterion(ac_id="AC1",
                    given="Người dùng đã chọn sản phẩm/dịch vụ và tiến hành thanh toán",
                    when="Nhập thông tin thẻ hợp lệ và xác nhận",
                    then="Giao dịch hoàn tất trong vòng 5 giây, hiển thị mã xác nhận và gửi email biên lai",
                    priority=SeverityLevel.CRITICAL))
                criteria.append(AcceptanceCriterion(ac_id="AC2",
                    given="Thẻ thanh toán hết hạn hoặc không đủ số dư",
                    when="Người dùng xác nhận thanh toán",
                    then="Thông báo lỗi cụ thể hiển thị, đơn hàng không bị thay đổi, không trừ tiền",
                    priority=SeverityLevel.HIGH))
                criteria.append(AcceptanceCriterion(ac_id="AC3",
                    given="Kết nối mạng bị ngắt trong quá trình thanh toán",
                    when="Giao dịch chưa hoàn tất",
                    then="Hệ thống idempotent: không trừ tiền 2 lần, giao dịch rollback an toàn",
                    priority=SeverityLevel.CRITICAL))
            else:
                criteria.append(AcceptanceCriterion(ac_id="AC1",
                    given="User has items in cart and proceeds to checkout",
                    when="Enters valid card details and confirms payment",
                    then="Transaction completes within 5 seconds, confirmation code shown and receipt emailed",
                    priority=SeverityLevel.CRITICAL))
                criteria.append(AcceptanceCriterion(ac_id="AC2",
                    given="Payment card is expired or has insufficient funds",
                    when="User confirms payment",
                    then="Specific error displayed, order unchanged, no charge made",
                    priority=SeverityLevel.HIGH))
                criteria.append(AcceptanceCriterion(ac_id="AC3",
                    given="Network drops during payment transaction",
                    when="Transaction is incomplete",
                    then="System is idempotent: no double charge, transaction safely rolled back",
                    priority=SeverityLevel.CRITICAL))
            return criteria

        # ── Branch: CRUD (create/update/delete) ──────────────────────────────────
        if is_crud_create or is_crud_update or is_crud_delete:
            entity = actor.lower() if actor.lower() not in ('người dùng', 'user') else (
                'bản ghi' if language == 'vi' else 'record'
            )
            if language == "vi":
                given_happy = f"Người dùng đã điền đầy đủ thông tin bắt buộc"
                when_happy = f"Nhấn nút {'Lưu' if not is_crud_delete else 'Xóa'}"
                then_happy = f"{'Bản ghi mới được tạo' if is_crud_create else ('Dữ liệu được cập nhật' if is_crud_update else 'Bản ghi bị xóa')} thành công, giao diện làm mới ngay lập tức"
            else:
                given_happy = f"User has filled all required fields with valid data"
                when_happy = f"User clicks {'Save' if not is_crud_delete else 'Delete'}"
                then_happy = f"{'New record created' if is_crud_create else ('Record updated' if is_crud_update else 'Record deleted')} successfully; UI refreshes to reflect the change"
            criteria.append(AcceptanceCriterion(ac_id="AC1",
                given=given_happy, when=when_happy, then=then_happy,
                priority=SeverityLevel.HIGH))

            if language == "vi":
                criteria.append(AcceptanceCriterion(ac_id="AC2",
                    given="Trường bắt buộc bị bỏ trống hoặc dữ liệu không đúng định dạng",
                    when="Nhấn nút Lưu",
                    then="Lỗi validation hiển thị ngay trên từng trường bị lỗi, form không được gửi",
                    priority=SeverityLevel.MEDIUM))
                if is_crud_delete:
                    criteria.append(AcceptanceCriterion(ac_id="AC3",
                        given="Người dùng nhấn nút Xóa",
                        when="Hộp thoại xác nhận hiển thị",
                        then='Nếu xác nhận "Có": bản ghi bị xóa vĩnh viễn; nếu "Hủy": không có thay đổi',
                        priority=SeverityLevel.HIGH))
                else:
                    criteria.append(AcceptanceCriterion(ac_id="AC3",
                        given="Dữ liệu đã lưu thành công",
                        when="Người dùng tải lại trang hoặc đăng nhập lại",
                        then="Dữ liệu vẫn được lưu đúng trong cơ sở dữ liệu, không bị mất",
                        priority=SeverityLevel.MEDIUM))
            else:
                criteria.append(AcceptanceCriterion(ac_id="AC2",
                    given="Required field is empty or data format is invalid",
                    when="User clicks Save",
                    then="Inline validation errors appear on each offending field; form not submitted",
                    priority=SeverityLevel.MEDIUM))
                if is_crud_delete:
                    criteria.append(AcceptanceCriterion(ac_id="AC3",
                        given="User clicks Delete button",
                        when="Confirmation dialog appears",
                        then='If user confirms "Yes": record permanently deleted; if "Cancel": no change',
                        priority=SeverityLevel.HIGH))
                else:
                    criteria.append(AcceptanceCriterion(ac_id="AC3",
                        given="Data was saved successfully",
                        when="User reloads the page or logs back in",
                        then="Data persists correctly in the database without loss or corruption",
                        priority=SeverityLevel.MEDIUM))
            return criteria

        # ── Branch: Report / Statistics ──────────────────────────────────────────
        if is_report:
            if language == "vi":
                criteria.append(AcceptanceCriterion(ac_id="AC1",
                    given="Có dữ liệu trong khoảng thời gian được chọn",
                    when="Người dùng chọn khoảng thời gian và nhấn Tạo báo cáo",
                    then="Báo cáo hiển thị đúng số liệu trong vòng 5 giây, có thể xuất file PDF/Excel",
                    priority=SeverityLevel.HIGH))
                criteria.append(AcceptanceCriterion(ac_id="AC2",
                    given="Không có dữ liệu trong khoảng thời gian chọn",
                    when="Nhấn Tạo báo cáo",
                    then='Thông báo "Không có dữ liệu" hiển thị, không gây lỗi hệ thống',
                    priority=SeverityLevel.MEDIUM))
            else:
                criteria.append(AcceptanceCriterion(ac_id="AC1",
                    given="Data exists within the selected date range",
                    when="User selects date range and clicks Generate Report",
                    then="Report renders with accurate figures within 5 seconds; export to PDF/Excel available",
                    priority=SeverityLevel.HIGH))
                criteria.append(AcceptanceCriterion(ac_id="AC2",
                    given="No data exists in the selected date range",
                    when="User clicks Generate Report",
                    then='"No data available" message shown; no system error thrown',
                    priority=SeverityLevel.MEDIUM))
            return criteria

        # ── Branch: File Upload ──────────────────────────────────────────────────
        if is_file_upload:
            if language == "vi":
                criteria.append(AcceptanceCriterion(ac_id="AC1",
                    given="Tệp hợp lệ (PDF/Excel, < 10 MB)",
                    when="Người dùng chọn tệp và nhấn Tải lên",
                    then="Tệp được xử lý thành công trong vòng 10 giây, dữ liệu được nhập vào hệ thống",
                    priority=SeverityLevel.HIGH))
                criteria.append(AcceptanceCriterion(ac_id="AC2",
                    given="Tệp vượt quá giới hạn kích thước (> 10 MB) hoặc sai định dạng",
                    when="Người dùng nhấn Tải lên",
                    then='Thông báo lỗi cụ thể: "Tệp vượt quá 10 MB" hoặc "Chỉ chấp nhận định dạng PDF/Excel"',
                    priority=SeverityLevel.MEDIUM))
            else:
                criteria.append(AcceptanceCriterion(ac_id="AC1",
                    given="Valid file (PDF/Excel, < 10 MB)",
                    when="User selects file and clicks Upload",
                    then="File processed within 10 seconds; data imported into the system correctly",
                    priority=SeverityLevel.HIGH))
                criteria.append(AcceptanceCriterion(ac_id="AC2",
                    given="File exceeds size limit (> 10 MB) or has wrong format",
                    when="User clicks Upload",
                    then='Specific error shown: "File exceeds 10 MB" or "Only PDF/Excel accepted"',
                    priority=SeverityLevel.MEDIUM))
            return criteria

        # ── Default fallback (generic functional requirement) ─────────────────
        if language == "vi":
            given = f"Người dùng đã đăng nhập với vai trò {actor}"
            when = f"{action[:80].strip()}"
            then = "Hệ thống xử lý thành công, hiển thị phản hồi rõ ràng trong vòng 3 giây"
        else:
            given = f"User is logged in as {actor}"
            when = f"{action[:80].strip()}"
            then = "System processes the request successfully and displays a clear response within 3 seconds"
        
        criteria.append(AcceptanceCriterion(
            ac_id="AC1", given=given, when=when, then=then,
            priority=SeverityLevel.HIGH
        ))
        
        # AC2: Validation
        if language == "vi":
            criteria.append(AcceptanceCriterion(ac_id="AC2",
                given="Dữ liệu đầu vào không hợp lệ hoặc còn thiếu trường bắt buộc",
                when="Người dùng cố gắng thực hiện hành động",
                then="Hệ thống hiển thị thông báo lỗi rõ ràng, chỉ đúng trường bị lỗi",
                priority=SeverityLevel.MEDIUM))
        else:
            criteria.append(AcceptanceCriterion(ac_id="AC2",
                given="Input data is invalid or a required field is missing",
                when="User attempts to perform the action",
                then="System shows a specific error message pointing to the offending field",
                priority=SeverityLevel.MEDIUM))
        
        # AC3: Permission check (if mentions roles/permissions)
        if any(kw in text_lower for kw in ['phân quyền', 'quyền', 'role', 'permission']):
            if language == "vi":
                criteria.append(AcceptanceCriterion(ac_id="AC3",
                    given="Người dùng không có quyền thực hiện chức năng này",
                    when="Cố gắng truy cập hoặc thực hiện hành động",
                    then="Hệ thống trả về lỗi HTTP 403 và hiển thị thông báo từ chối truy cập",
                    priority=SeverityLevel.HIGH))
            else:
                criteria.append(AcceptanceCriterion(ac_id="AC3",
                    given="User does not have permission for this feature",
                    when="Attempts to access or perform the action",
                    then="System returns HTTP 403 and shows an access-denied message",
                    priority=SeverityLevel.HIGH))
        
        return criteria
    
    # ── AC padding (ensure ≥ MIN_AC items per story) ──────────────────────
    _AC_FALLBACK_TEMPLATES_VI = [
        ("Người dùng có dữ liệu hợp lệ và đầy đủ quyền",
         "Thực hiện thao tác chính của chức năng",
         "Hệ thống xử lý thành công và phản hồi rõ ràng trong vòng 3 giây"),
        ("Dữ liệu đầu vào không hợp lệ hoặc thiếu trường bắt buộc",
         "Người dùng gửi yêu cầu",
         "Hệ thống từ chối thao tác và hiển thị thông báo lỗi cụ thể trên đúng trường bị lỗi"),
        ("Người dùng không có quyền thực hiện chức năng",
         "Cố gắng truy cập tài nguyên hoặc thao tác",
         "Hệ thống trả về HTTP 403 và ghi log sự kiện truy cập trái phép"),
        ("Lỗi hệ thống xảy ra (mất kết nối DB, dịch vụ ngoài lỗi, timeout)",
         "Người dùng thực hiện thao tác",
         "Hệ thống hiển thị thông báo lỗi thân thiện, không lộ stack trace, và cho phép thử lại"),
        ("Thao tác có thay đổi dữ liệu quan trọng",
         "Sau khi hoàn tất",
         "Hệ thống ghi audit log gồm user, thời điểm, và nội dung thay đổi"),
    ]
    _AC_FALLBACK_TEMPLATES_EN = [
        ("User has valid data and required permissions",
         "Performs the main action of the feature",
         "System processes successfully and responds within 3 seconds"),
        ("Input data is invalid or required fields are missing",
         "User submits the request",
         "System rejects the action and shows a specific error on the offending field"),
        ("User lacks the required permission for this feature",
         "Attempts to access the resource or action",
         "System returns HTTP 403 and logs the unauthorized attempt"),
        ("A system-level error occurs (DB outage, external service down, timeout)",
         "User performs the action",
         "System shows a friendly error message, hides stack traces, and offers a retry option"),
        ("Action mutates critical data",
         "On completion",
         "System writes an audit log entry with user, timestamp, and change details"),
    ]

    def _ensure_min_acceptance_criteria(
        self,
        criteria: List[AcceptanceCriterion],
        actor: str,
        language: str,
        min_ac: int = 4,
    ) -> List[AcceptanceCriterion]:
        """Pad the AC list with generic-but-useful fallbacks until ``min_ac`` is met.

        Skips templates whose Given/When/Then text would duplicate an existing AC
        (case-insensitive substring match on the ``then`` clause).
        """
        if len(criteria) >= min_ac:
            return criteria

        existing_signatures = {
            (ac.then or "").strip().lower()[:60] for ac in criteria
        }
        templates = (
            self._AC_FALLBACK_TEMPLATES_VI if language == "vi"
            else self._AC_FALLBACK_TEMPLATES_EN
        )
        next_idx = len(criteria) + 1
        for given, when, then in templates:
            if len(criteria) >= min_ac:
                break
            sig = then.strip().lower()[:60]
            if sig in existing_signatures:
                continue
            criteria.append(AcceptanceCriterion(
                ac_id=f"AC{next_idx}",
                given=given,
                when=when,
                then=then,
                priority=SeverityLevel.MEDIUM,
            ))
            existing_signatures.add(sig)
            next_idx += 1
        return criteria

    def _extract_nfrs(self, text: str) -> List[str]:
        """Extract non-functional requirements"""
        nfrs = []
        text_lower = text.lower()
        
        for nfr_type, keywords in self.NFR_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Found NFR
                    if nfr_type == 'performance':
                        nfrs.append(f"Hiệu suất: Thời gian phản hồi < 2 giây")
                    elif nfr_type == 'security':
                        nfrs.append(f"Bảo mật: Mã hóa dữ liệu nhạy cảm, xác thực người dùng")
                    elif nfr_type == 'usability':
                        nfrs.append(f"Khả năng sử dụng: Giao diện thân thiện, dễ học")
                    elif nfr_type == 'reliability':
                        nfrs.append(f"Độ tin cậy: Uptime 99.9%, xử lý lỗi gracefully")
                    elif nfr_type == 'scalability':
                        nfrs.append(f"Khả năng mở rộng: Hỗ trợ 1000+ người dùng đồng thời")
                    break
        
        # Deduplicate
        return list(set(nfrs))
    
    def _extract_assumptions(self, text: str, language: str) -> List[str]:
        """Extract implicit assumptions"""
        assumptions = []
        text_lower = text.lower()
        
        # Database assumption
        if any(kw in text_lower for kw in ['lưu', 'cập nhật', 'xóa', 'tạo', 'save', 'update']):
            if language == "vi":
                assumptions.append("Có kết nối cơ sở dữ liệu ổn định")
            else:
                assumptions.append("Stable database connection available")
        
        # Authentication assumption
        if any(kw in text_lower for kw in ['đăng nhập', 'người dùng', 'user', 'login']):
            if language == "vi":
                assumptions.append("Người dùng đã được xác thực")
            else:
                assumptions.append("User is authenticated")
        
        # Network assumption (if mentions external systems)
        if any(kw in text_lower for kw in ['api', 'tích hợp', 'integration', 'third-party']):
            if language == "vi":
                assumptions.append("Dịch vụ bên thứ ba khả dụng")
            else:
                assumptions.append("Third-party services are available")
        
        return assumptions
    
    def _extract_constraints(self, text: str, language: str) -> List[str]:
        """Extract technical/business constraints"""
        constraints = []
        text_lower = text.lower()
        
        # Technology constraints
        if 'mobile' in text_lower or 'điện thoại' in text_lower:
            constraints.append("Phải hỗ trợ iOS và Android")
        
        # Time constraints
        if any(kw in text_lower for kw in ['thời gian thực', 'real-time', 'ngay lập tức']):
            constraints.append("Cập nhật thời gian thực (latency < 500ms)")
        
        # Compliance constraints
        if any(kw in text_lower for kw in ['gdpr', 'quy định', 'compliance', 'luật']):
            constraints.append("Tuân thủ các quy định về bảo vệ dữ liệu")
        
        return constraints
    
    def _generate_changes_summary(
        self,
        original: str,
        user_story: str,
        ac_count: int,
        assumption_count: int,
        nfr_count: int
    ) -> str:
        """Generate summary of refinement changes"""
        summary_parts = []
        
        summary_parts.append(f"Chuyển đổi từ yêu cầu gốc sang User Story chuẩn")
        summary_parts.append(f"Tạo {ac_count} acceptance criteria với Given/When/Then")
        
        if assumption_count > 0:
            summary_parts.append(f"Trích xuất {assumption_count} giả định ngầm")
        
        if nfr_count > 0:
            summary_parts.append(f"Nhận diện {nfr_count} yêu cầu phi chức năng")
        
        return "; ".join(summary_parts)
