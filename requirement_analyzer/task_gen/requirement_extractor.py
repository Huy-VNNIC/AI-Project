"""
Requirement Extractor Interface
Abstract base for requirement extraction (pluggable for custom AI)
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from .structured_intent import StructuredIntent


class RequirementExtractor(ABC):
    """
    Abstract base class for requirement extraction
    
    Implement this with YOUR custom AI model to extract:
    - Domain
    - Entities
    - Actions
    - Constraints
    - Security concerns
    - etc.
    
    The extracto will output StructuredIntent (not raw LLM text)
    """
    
    @abstractmethod
    def extract(self, requirement_text: str) -> StructuredIntent:
        """
        Extract and parse requirement into structured format
        
        Args:
            requirement_text: Raw requirement (can be Vietnamese or English)
            
        Returns:
            StructuredIntent with all components extracted and classified
        """
        pass
    
    @abstractmethod
    def extract_batch(self, requirements: List[str]) -> List[StructuredIntent]:
        """Extract multiple requirements"""
        pass
    
    def prepare_extraction_context(self, requirement_text: str) -> dict:
        """Helper: prepare context for extraction (shared across implementations)"""
        return {
            "original_text": requirement_text,
            "text_length": len(requirement_text),
            "is_vietnamese": self._detect_vietnamese(requirement_text),
            "has_security_keywords": self._detect_security_keywords(requirement_text),
            "has_performance_keywords": self._detect_performance_keywords(requirement_text),
            "timestamp": datetime.now().isoformat(),
        }
    
    @staticmethod
    def _detect_vietnamese(text: str) -> bool:
        """Check if text contains Vietnamese characters"""
        vietnamese_chars = set("àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ")
        return any(c.lower() in vietnamese_chars for c in text)
    
    @staticmethod
    def _detect_security_keywords(text: str) -> bool:
        """Check for security-related keywords"""
        keywords = [
            "xác thực", "authenticate", "authorization", "permission",
            "security", "bảo mật", "mã hóa", "cipher", "encrypt",
            "unauthorized", "access control", "role", "password", "token",
            "audit", "log", "breach", "vulnerability", "threat"
        ]
        text_lower = text.lower()
        return any(kw in text_lower for kw in keywords)
    
    @staticmethod
    def _detect_performance_keywords(text: str) -> bool:
        """Check for performance-related keywords"""
        keywords = [
            "performance", "response time", "millisecond", "ms",
            "throughput", "concurrent", "load", "scalability",
            "optimization", "cache", "tối ưu", "hiệu suất"
        ]
        text_lower = text.lower()
        return any(kw in text_lower for kw in keywords)


class MockRequirementExtractor(RequirementExtractor):
    """
    Fallback mock extractor for testing
    Replace this with your actual AI model implementation
    """
    
    def extract(self, requirement_text: str) -> StructuredIntent:
        """Fallback extraction using rules + keywords"""
        from .structured_intent import (
            DomainType, Entity, Action, Constraint, 
            SecurityConcern
        )
        
        context = self.prepare_extraction_context(requirement_text)
        
        # Simple heuristic-based extraction (replace with your AI)
        domain = self._infer_domain(requirement_text)
        is_security = context["has_security_keywords"]
        
        intent = StructuredIntent(
            requirement_id="REQ-PLACEHOLDER",
            original_text=requirement_text,
            domain=domain,
            primary_entity=Entity(
                name="resource",
                description="Primary entity",
                attributes=[],
                relationships=[]
            ),
            primary_action=Action(
                verb="process",
                target="resource",
                description="Primary action",
                preconditions=[],
                postconditions=[]
            ),
            constraints=[],
            security_concerns=[
                SecurityConcern(
                    concern_type="authentication",
                    description="System requires user authentication",
                    severity="high",
                    test_cases_needed=["test_unauthenticated_access", "test_valid_auth"]
                )
            ] if is_security else [],
            confidence_score=0.6,
            extraction_model="mock_fallback",
            extracted_at=context["timestamp"],
        )
        
        return intent
    
    def extract_batch(self, requirements: List[str]) -> List[StructuredIntent]:
        """Extract multiple requirements"""
        return [self.extract(req) for req in requirements]
    
    @staticmethod
    def _infer_domain(text: str) -> "DomainType":
        """Simple domain inference from keywords"""
        from .structured_intent import DomainType
        
        text_lower = text.lower()
        
        if any(w in text_lower for w in ["phòng", "đặt phòng", "booking", "hotel", "khách sạn"]):
            return DomainType.HOTEL_MANAGEMENT
        elif any(w in text_lower for w in ["chuyển khoản", "thanh toán", "ngân hàng", "banking", "transfer"]):
            return DomainType.BANKING
        elif any(w in text_lower for w in ["sản phẩm", "mua hàng", "giỏ hàng", "ecommerce", "shop", "order"]):
            return DomainType.ECOMMERCE
        elif any(w in text_lower for w in ["bệnh nhân", "bác sĩ", "healthcare", "medical", "patient"]):
            return DomainType.HEALTHCARE
        else:
            return DomainType.GENERAL
