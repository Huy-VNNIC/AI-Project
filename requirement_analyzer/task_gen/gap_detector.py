"""
V2 Gap Detector
===============

Detects gaps, ambiguities, and contradictions in requirements using:
- Rule-based checks (missing actor, object, constraints, etc.)
- Pattern matching for common issues
- LLM integration (future) for semantic analysis
"""
import re
from typing import List, Tuple
from requirement_analyzer.task_gen.schemas_v2 import (
    Requirement,
    RefinementOutput,
    Gap,
    GapReport,
    GapType,
    SeverityLevel
)


class GapDetector:
    """Detects gaps and issues in requirements"""
    
    # Rule patterns
    ACTOR_KEYWORDS = ['quản lý', 'nhân viên', 'khách hàng', 'người dùng', 'user', 'admin']
    OBJECT_KEYWORDS = ['phòng', 'đơn hàng', 'sản phẩm', 'bệnh án', 'khóa học']
    ERROR_KEYWORDS = ['lỗi', 'không thành công', 'thất bại', 'error', 'fail']
    PERMISSION_KEYWORDS = ['quyền', 'phân quyền', 'permission', 'role', 'authorization']
    SECURITY_KEYWORDS = ['bảo mật', 'mã hóa', 'xác thực', 'security', 'encrypt', 'auth']
    VALIDATION_KEYWORDS = ['kiểm tra', 'validate', 'hợp lệ', 'valid', 'check']
    INTEGRATION_KEYWORDS = ['api', 'tích hợp', 'integration', 'third-party', 'external']
    
    # Contradiction patterns
    CONTRADICTION_PAIRS = [
        (['luôn', 'phải', 'bắt buộc'], ['tùy chọn', 'có thể', 'không bắt buộc']),
        (['tất cả', 'mọi'], ['một số', 'vài']),
        (['công khai', 'public'], ['riêng tư', 'private']),
    ]
    
    def __init__(self):
        """Initialize gap detector"""
        self.gap_counter = 0
    
    def detect_gaps(self, requirement: Requirement, refinement: RefinementOutput) -> GapReport:
        """
        Detect gaps in a requirement
        
        Args:
            requirement: Original requirement
            refinement: Refined output
            
        Returns:
            GapReport with detected gaps
        """
        gaps = []
        self.gap_counter = 0  # Reset counter
        
        # Rule-based checks
        gaps.extend(self._check_missing_actor(requirement))
        gaps.extend(self._check_missing_object(requirement))
        gaps.extend(self._check_missing_error_handling(requirement))
        gaps.extend(self._check_missing_permissions(requirement))
        gaps.extend(self._check_missing_security(requirement))
        gaps.extend(self._check_missing_validation(requirement))
        gaps.extend(self._check_missing_integration_details(requirement))
        gaps.extend(self._check_ambiguity(requirement))
        gaps.extend(self._check_contradictions(requirement))
        
        # Check refinement quality
        gaps.extend(self._check_refinement_completeness(refinement))
        
        return GapReport(
            requirement_id=requirement.requirement_id,
            gaps=gaps
        )
    
    def _make_gap_id(self) -> str:
        """Generate gap ID"""
        self.gap_counter += 1
        return f"GAP{self.gap_counter:03d}"
    
    def _check_missing_actor(self, requirement: Requirement) -> List[Gap]:
        """Check if actor is specified"""
        text_lower = requirement.original_text.lower()
        
        # Check if any actor keyword present
        has_actor = any(kw in text_lower for kw in self.ACTOR_KEYWORDS)
        
        if not has_actor:
            return [Gap(
                gap_id=self._make_gap_id(),
                type=GapType.MISSING_ACTOR,
                severity=SeverityLevel.HIGH,
                description="Yêu cầu không chỉ rõ người dùng/vai trò thực hiện hành động",
                question="Ai là người sẽ sử dụng chức năng này? (quản lý, nhân viên, khách hàng, ...)",
                suggestion="Thêm rõ vai trò: 'Quản lý khách sạn cần...' hoặc 'Nhân viên lễ tân muốn...'",
                detected_by="rule",
                confidence=0.9
            )]
        
        return []
    
    def _check_missing_object(self, requirement: Requirement) -> List[Gap]:
        """Check if data object is specified"""
        text_lower = requirement.original_text.lower()
        
        # Check if any object keyword present
        has_object = any(kw in text_lower for kw in self.OBJECT_KEYWORDS)
        
        # Check for generic "dữ liệu" without specifics
        if 'dữ liệu' in text_lower and not has_object:
            return [Gap(
                gap_id=self._make_gap_id(),
                type=GapType.MISSING_OBJECT,
                severity=SeverityLevel.MEDIUM,
                description="Yêu cầu đề cập 'dữ liệu' nhưng không chỉ rõ loại dữ liệu nào",
                question="Dữ liệu cụ thể là gì? (phòng, đặt phòng, khách hàng, hóa đơn, ...)",
                suggestion="Thay 'dữ liệu' bằng tên cụ thể: 'dữ liệu đặt phòng', 'thông tin khách hàng'",
                detected_by="rule",
                confidence=0.85
            )]
        
        return []
    
    def _check_missing_error_handling(self, requirement: Requirement) -> List[Gap]:
        """Check if error handling is mentioned"""
        text_lower = requirement.original_text.lower()
        
        # Check if mentions actions that could fail
        has_risky_action = any(kw in text_lower for kw in [
            'tạo', 'xóa', 'cập nhật', 'lưu', 'gửi', 'xử lý',
            'create', 'delete', 'update', 'save', 'send', 'process'
        ])
        
        # Check if mentions error handling
        has_error_handling = any(kw in text_lower for kw in self.ERROR_KEYWORDS)
        
        if has_risky_action and not has_error_handling:
            return [Gap(
                gap_id=self._make_gap_id(),
                type=GapType.MISSING_ERROR_HANDLING,
                severity=SeverityLevel.HIGH,
                description="Yêu cầu không mô tả xử lý khi thao tác thất bại",
                question="Điều gì xảy ra khi thao tác thất bại? Hiển thị lỗi như thế nào? Rollback?",
                suggestion="Thêm: 'Nếu lỗi xảy ra, hệ thống hiển thị thông báo rõ ràng và rollback thay đổi'",
                detected_by="rule",
                confidence=0.8
            )]
        
        return []
    
    def _check_missing_permissions(self, requirement: Requirement) -> List[Gap]:
        """Check if permissions are specified for sensitive actions"""
        text_lower = requirement.original_text.lower()
        
        # Check for sensitive actions
        has_sensitive_action = any(kw in text_lower for kw in [
            'xóa', 'delete', 'phê duyệt', 'approve', 'từ chối', 'reject'
        ])
        
        # Check if mentions permissions
        has_permission = any(kw in text_lower for kw in self.PERMISSION_KEYWORDS)
        
        if has_sensitive_action and not has_permission:
            return [Gap(
                gap_id=self._make_gap_id(),
                type=GapType.MISSING_PERMISSION,
                severity=SeverityLevel.HIGH,
                description="Thao tác nhạy cảm không chỉ rõ phân quyền",
                question="Ai có quyền thực hiện thao tác này? Cần role nào?",
                suggestion="Thêm: 'Chỉ quản lý có quyền xóa' hoặc 'Yêu cầu role Admin'",
                detected_by="rule",
                confidence=0.9
            )]
        
        return []
    
    def _check_missing_security(self, requirement: Requirement) -> List[Gap]:
        """Check for missing security considerations"""
        text_lower = requirement.original_text.lower()
        
        # Check for sensitive data
        has_sensitive_data = any(kw in text_lower for kw in [
            'mật khẩu', 'password', 'thẻ tín dụng', 'credit card',
            'cccd', 'cmnd', 'id card', 'cá nhân', 'personal'
        ])
        
        # Check if mentions security
        has_security = any(kw in text_lower for kw in self.SECURITY_KEYWORDS)
        
        if has_sensitive_data and not has_security:
            return [Gap(
                gap_id=self._make_gap_id(),
                type=GapType.MISSING_SECURITY,
                severity=SeverityLevel.CRITICAL,
                description="Dữ liệu nhạy cảm không đề cập đến bảo mật",
                question="Làm thế nào để bảo vệ dữ liệu này? Mã hóa? Hashing? HTTPS?",
                suggestion="Thêm: 'Mật khẩu được hash với bcrypt', 'Dữ liệu truyền qua HTTPS'",
                detected_by="rule",
                confidence=1.0
            )]
        
        return []
    
    def _check_missing_validation(self, requirement: Requirement) -> List[Gap]:
        """Check for missing input validation"""
        text_lower = requirement.original_text.lower()
        
        # Check for input actions
        has_input = any(kw in text_lower for kw in [
            'nhập', 'input', 'điền', 'fill', 'tạo', 'create'
        ])
        
        # Check if mentions validation
        has_validation = any(kw in text_lower for kw in self.VALIDATION_KEYWORDS)
        
        if has_input and not has_validation:
            return [Gap(
                gap_id=self._make_gap_id(),
                type=GapType.MISSING_DATA_VALIDATION,
                severity=SeverityLevel.MEDIUM,
                description="Không mô tả validation cho dữ liệu đầu vào",
                question="Dữ liệu cần validate gì? Format? Giới hạn độ dài? Required fields?",
                suggestion="Thêm: 'Email phải đúng format', 'SĐT 10-11 số', 'Tên không trống'",
                detected_by="rule",
                confidence=0.75
            )]
        
        return []
    
    def _check_missing_integration_details(self, requirement: Requirement) -> List[Gap]:
        """Check for missing integration details"""
        text_lower = requirement.original_text.lower()
        
        # Check if mentions integration
        has_integration = any(kw in text_lower for kw in self.INTEGRATION_KEYWORDS)
        
        if has_integration:
            # Check for specific details
            has_details = any(kw in text_lower for kw in [
                'endpoint', 'format', 'json', 'xml', 'authentication',
                'timeout', 'retry', 'fallback'
            ])
            
            if not has_details:
                return [Gap(
                    gap_id=self._make_gap_id(),
                    type=GapType.MISSING_INTEGRATION,
                    severity=SeverityLevel.HIGH,
                    description="Tích hợp hệ thống ngoài thiếu chi tiết kỹ thuật",
                    question="API endpoint? Format (JSON/XML)? Authentication? Timeout? Error handling?",
                    suggestion="Thêm: 'Call API POST /endpoint với JSON body, timeout 5s, retry 3 lần'",
                    detected_by="rule",
                    confidence=0.8
                )]
        
        return []
    
    def _check_ambiguity(self, requirement: Requirement) -> List[Gap]:
        """Check for ambiguous language"""
        text_lower = requirement.original_text.lower()
        
        ambiguous_words = [
            'etc', 'vv', '...', 'tùy thuộc', 'có thể', 'nên', 'should',
            'thích hợp', 'hợp lý', 'reasonable', 'appropriate'
        ]
        
        found_ambiguous = [word for word in ambiguous_words if word in text_lower]
        
        if found_ambiguous:
            return [Gap(
                gap_id=self._make_gap_id(),
                type=GapType.AMBIGUITY,
                severity=SeverityLevel.MEDIUM,
                description=f"Yêu cầu sử dụng ngôn ngữ mơ hồ: {', '.join(found_ambiguous)}",
                question="Có thể chỉ rõ hơn không? Liệt kê cụ thể thay vì 'etc', 'vv'?",
                suggestion="Thay 'etc' bằng danh sách đầy đủ, thay 'hợp lý' bằng số cụ thể",
                detected_by="rule",
                confidence=0.7
            )]
        
        return []
    
    def _check_contradictions(self, requirement: Requirement) -> List[Gap]:
        """Check for contradictions in requirement"""
        text_lower = requirement.original_text.lower()
        
        for positive_words, negative_words in self.CONTRADICTION_PAIRS:
            has_positive = any(word in text_lower for word in positive_words)
            has_negative = any(word in text_lower for word in negative_words)
            
            if has_positive and has_negative:
                return [Gap(
                    gap_id=self._make_gap_id(),
                    type=GapType.CONTRADICTION,
                    severity=SeverityLevel.HIGH,
                    description="Yêu cầu có mâu thuẫn logic",
                    question=f"Yêu cầu vừa nói '{positive_words[0]}' vừa nói '{negative_words[0]}' - cái nào đúng?",
                    suggestion="Xác định rõ: bắt buộc hay tùy chọn? Tất cả hay một số?",
                    detected_by="rule",
                    confidence=0.85
                )]
        
        return []
    
    def _check_refinement_completeness(self, refinement: RefinementOutput) -> List[Gap]:
        """Check if refinement is complete"""
        gaps = []
        
        # Check AC count
        if len(refinement.acceptance_criteria) < 3:
            gaps.append(Gap(
                gap_id=self._make_gap_id(),
                type=GapType.AMBIGUITY,
                severity=SeverityLevel.LOW,
                description=f"Chỉ có {len(refinement.acceptance_criteria)} AC (khuyến nghị 3-8)",
                question="Có thể thêm AC cho edge cases, validation, error handling?",
                suggestion="Thêm AC cho: dữ liệu invalid, permission denied, network error",
                detected_by="rule",
                confidence=0.6
            ))
        
        # Check if has NFRs for functional requirements
        if not refinement.non_functional_requirements:
            gaps.append(Gap(
                gap_id=self._make_gap_id(),
                type=GapType.MISSING_NFR,
                severity=SeverityLevel.LOW,
                description="Không có yêu cầu phi chức năng (NFR)",
                question="Có yêu cầu về performance, security, usability không?",
                suggestion="Thêm NFR: 'Response time < 2s', 'Support 100 concurrent users'",
                detected_by="rule",
                confidence=0.5
            ))
        
        return gaps
