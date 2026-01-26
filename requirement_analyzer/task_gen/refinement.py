"""
V2 Refinement Engine
====================

Refines raw requirements into structured User Stories with:
- Proper As a...I want...so that... format
- Given/When/Then acceptance criteria
- Extracted assumptions, constraints, NFRs
"""
import re
from typing import List, Tuple, Optional
from requirement_analyzer.task_gen.schemas_v2 import (
    Requirement,
    RefinementOutput,
    AcceptanceCriterion,
    SeverityLevel
)


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
    
    def __init__(self):
        """Initialize refiner"""
        pass
    
    def refine(self, requirement: Requirement) -> RefinementOutput:
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
        
        # Generate title
        title = self._generate_title(action, requirement.language)
        
        # Generate acceptance criteria
        acceptance_criteria = self._generate_acceptance_criteria(
            requirement.original_text,
            actor,
            action,
            requirement.language
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
        """Extract main action from requirement"""
        text_lower = text.lower()
        
        # Find action verbs
        for verb in self.VI_ACTION_VERBS:
            if verb in text_lower:
                # Extract context around verb
                idx = text_lower.find(verb)
                snippet = text[idx:min(idx+100, len(text))]
                # Clean up
                snippet = re.sub(r'\s+', ' ', snippet).strip()
                return snippet
        
        # Fallback: return first 50 chars
        return text[:50].strip()
    
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
        if language == "vi":
            return f"Là một {actor}, tôi muốn {action}, {value}."
        else:
            return f"As a {actor}, I want to {action}, so that {value}."
    
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
        """Generate Given/When/Then acceptance criteria"""
        criteria = []
        
        # AC1: Happy path
        if language == "vi":
            given = f"Đã đăng nhập với vai trò {actor}"
            when = f"Thực hiện {action}"
            then = "Hệ thống xử lý thành công và hiển thị kết quả"
        else:
            given = f"Logged in as {actor}"
            when = f"Perform {action}"
            then = "System processes successfully and displays result"
        
        criteria.append(AcceptanceCriterion(
            ac_id="AC1",
            given=given,
            when=when,
            then=then,
            priority=SeverityLevel.HIGH
        ))
        
        # AC2: Validation
        if language == "vi":
            given = "Dữ liệu đầu vào không hợp lệ"
            when = "Cố gắng thực hiện hành động"
            then = "Hệ thống hiển thị thông báo lỗi rõ ràng"
        else:
            given = "Invalid input data"
            when = "Attempt to perform action"
            then = "System displays clear error message"
        
        criteria.append(AcceptanceCriterion(
            ac_id="AC2",
            given=given,
            when=when,
            then=then,
            priority=SeverityLevel.MEDIUM
        ))
        
        # AC3: Permission check (if mentions roles/permissions)
        text_lower = text.lower()
        if any(kw in text_lower for kw in ['phân quyền', 'quyền', 'role', 'permission']):
            if language == "vi":
                given = "Người dùng không có quyền"
                when = "Cố gắng truy cập chức năng"
                then = "Hệ thống từ chối truy cập và thông báo"
            else:
                given = "User lacks permission"
                when = "Attempt to access feature"
                then = "System denies access and notifies"
            
            criteria.append(AcceptanceCriterion(
                ac_id="AC3",
                given=given,
                when=when,
                then=then,
                priority=SeverityLevel.HIGH
            ))
        
        # AC4: Data persistence (if mentions save/update)
        if any(kw in text_lower for kw in ['lưu', 'cập nhật', 'save', 'update', 'create']):
            if language == "vi":
                given = "Thay đổi dữ liệu thành công"
                when = "Tải lại trang hoặc truy cập lại"
                then = "Dữ liệu được lưu trữ và hiển thị đúng"
            else:
                given = "Data changed successfully"
                when = "Reload page or access again"
                then = "Data persists and displays correctly"
            
            criteria.append(AcceptanceCriterion(
                ac_id="AC4",
                given=given,
                when=when,
                then=then,
                priority=SeverityLevel.MEDIUM
            ))
        
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
