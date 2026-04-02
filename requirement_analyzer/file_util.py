"""
File Requirement Parser - Extract requirements from various file formats
"""

import os
from typing import List, Tuple
from pathlib import Path


class RequirementFileParser:
    """Parse requirement files (TXT, CSV, etc.)"""
    
    @staticmethod
    def parse_txt(content: str) -> List[str]:
        """Parse plain text file - split by newlines, filter empty"""
        lines = content.split('\n')
        requirements = [
            line.strip() 
            for line in lines 
            if line.strip() and not line.strip().startswith('#')
        ]
        return requirements
    
    @staticmethod
    def parse_csv(content: str, column_index: int = 0) -> List[str]:
        """Parse CSV file - extract specific column"""
        import csv
        from io import StringIO
        
        reader = csv.reader(StringIO(content))
        requirements = []
        for row_idx, row in enumerate(reader):
            # Skip header row
            if row_idx == 0:
                continue
            if len(row) > column_index:
                req = row[column_index].strip()
                if req:
                    requirements.append(req)
        return requirements
    
    @staticmethod
    def parse_markdown(content: str) -> List[str]:
        """Parse Markdown file - extract requirements from headers and lists
        
        Smart extraction that identifies actual requirements vs section headers
        """
        requirements = []
        in_code_block = False
        in_frontmatter = False
        lines = content.split('\n')
        
        # Keywords that indicate requirement lines (in Vietnamese and English)
        requirement_keywords = [
            'hệ thống phải',
            'phải',
            'must',
            'should',
            'API',
            'tích hợp',
            'hỗ trợ',
            'cho phép',
            'quản lý',
            'theo dõi',
            'cảnh báo',
            'kiểm tra',
            'xuất',
            'lưu',
            'hiển thị',
            'xử lý',
            'đánh giá',
            'encrypt',
            'implement',
            'handle',
            'allow',
            'maintain',
            'send',
            'response time',
            'backup',
        ]
        
        # Section headers to skip (common table of contents patterns)
        section_headers = [
            'introduction',
            'functional requirements',
            'non-functional requirements',
            'technical requirements',
            'constraints',
            'assumptions',
            'glossary',
            'appendix',
            'references',
            'modules',
            'module',
            'requirements',
        ]
        
        for line in lines:
            stripped = line.strip()
            
            # Skip YAML frontmatter
            if stripped.startswith('---'):
                in_frontmatter = not in_frontmatter
                continue
            if in_frontmatter:
                continue
            
            # Skip code blocks
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block or not stripped:
                continue
            
            req = None
            
            # Extract bullet points / list items (highest priority)
            if stripped.startswith('-') or stripped.startswith('*'):
                req = stripped.lstrip('-*').strip()
                if req and not req.startswith('http') and not req.startswith('[') and not req.startswith('!'):
                    pass  # req is already extracted
                else:
                    req = None
            
            # Extract numbered items BUT check if it's too short (likely section header)
            elif stripped and stripped[0].isdigit() and '.' in stripped[:4]:
                req = stripped.split('.', 1)[1].strip() if '.' in stripped else stripped.strip()
                
                # Filter out pure section headers (generic naming)
                is_section = any(header in req.lower() for header in section_headers)
                if is_section:
                    req = None
                # Also filter if too short (less than 4 words) and no requirement keywords
                elif req and len(req.split()) < 4 and not any(kw in req.lower() for kw in requirement_keywords):
                    req = None
            
            # Extract headers (##, ###, #) but ONLY if they look like actual requirements
            elif stripped.startswith('#'):
                req = stripped.lstrip('#').strip()
                # Filter: Skip section headers, keep only detailed requirements
                is_section = any(header in req.lower() for header in section_headers) or len(req.split()) <= 3
                if is_section or not any(kw in req.lower() for kw in requirement_keywords):
                    req = None
            
            # Plain text lines with requirement keywords
            elif any(kw in stripped.lower() for kw in requirement_keywords):
                req = stripped
            
            # Add requirement if it passes all filters
            if req and len(req.split()) >= 3:  # Minimum 3 words
                # Clean up markdown syntax
                req = req.replace('[', '').replace(']', '').replace('(', '')
                req = req.replace(')', '').replace('*', '').strip()
                
                # Skip if result is empty
                if req and len(req.split()) >= 3:
                    requirements.append(req)
        
        return requirements
    
    @staticmethod
    def parse_docx(content_bytes: bytes) -> List[str]:
        """Parse DOCX file - extract paragraphs"""
        try:
            from docx import Document
            from io import BytesIO
            
            doc = Document(BytesIO(content_bytes))
            requirements = [
                para.text.strip() 
                for para in doc.paragraphs 
                if para.text.strip()
            ]
            return requirements
        except ImportError:
            raise ValueError("python-docx not installed. Please install it: pip install python-docx")
        except Exception as e:
            raise ValueError(f"Error parsing DOCX file: {str(e)}")
    
    @staticmethod
    def parse_pdf(file_path: str) -> List[str]:
        """Parse PDF file - extract text"""
        try:
            import PyPDF2
            requirements = []
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text = page.extract_text()
                    lines = [
                        line.strip() 
                        for line in text.split('\n') 
                        if line.strip()
                    ]
                    requirements.extend(lines)
            return requirements
        except ImportError:
            raise ValueError("PyPDF2 not installed. Please install it: pip install PyPDF2")
    
    @classmethod
    def parse_file(cls, file_content: str, file_type: str, binary_content: bytes = None) -> List[str]:
        """
        Parse file based on type
        Args:
            file_content: File content as string (for TXT/CSV/MD)
            file_type: File extension (txt, csv, md, markdown, docx)
            binary_content: Binary content for docx files
        """
        file_type = file_type.lower()
        
        if file_type == 'txt':
            return cls.parse_txt(file_content)
        elif file_type == 'csv':
            return cls.parse_csv(file_content)
        elif file_type in ['md', 'markdown']:
            return cls.parse_markdown(file_content)
        elif file_type == 'docx' and binary_content:
            return cls.parse_docx(binary_content)
        else:
            raise ValueError(f"Unsupported file type: {file_type}. Supported: TXT, CSV, MD, DOCX")
    
    @staticmethod
    def group_requirements(requirements: List[str], group_by_feature: bool = True) -> dict:
        """
        Group requirements by feature/user story
        Returns: {"Feature 1": [...reqs], "Feature 2": [...reqs]}
        """
        grouped = {}
        current_feature = "General"
        
        for req in requirements:
            # Check if line is a feature header (starts with "Feature:" or "-")
            if req.startswith("Feature:"):
                current_feature = req.replace("Feature:", "").strip()
                grouped[current_feature] = []
            elif req.startswith("# ") or req.startswith("## "):
                current_feature = req.replace("#", "").strip()
                grouped[current_feature] = []
            else:
                # Regular requirement
                if current_feature not in grouped:
                    grouped[current_feature] = []
                grouped[current_feature].append(req)
        
        return grouped


def create_sample_requirement_file() -> str:
    """Create sample requirement file for testing"""
    sample = """Feature: User Authentication
- Users can log in with email and password
- The system validates email format before processing
- Users receive confirmation message after successful login
- The system prevents SQL injection attacks

Feature: User Profile Management
- Users can view their profile information
- Users can edit their personal details
- System validates all input fields
- Changes are persisted to database

Feature: Order Processing
- User can browse available products
- User can add items to shopping cart
- System calculates total price with tax
- User can proceed to checkout with valid payment method
"""
    return sample
