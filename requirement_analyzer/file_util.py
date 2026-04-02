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
    def parse_docx(file_path: str) -> List[str]:
        """Parse DOCX file - extract paragraphs"""
        try:
            from docx import Document
            doc = Document(file_path)
            requirements = [
                para.text.strip() 
                for para in doc.paragraphs 
                if para.text.strip()
            ]
            return requirements
        except ImportError:
            raise ValueError("python-docx not installed. Use TXT or CSV instead.")
    
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
            raise ValueError("PyPDF2 not installed. Use TXT or CSV instead.")
    
    @classmethod
    def parse_file(cls, file_content: str, file_type: str) -> List[str]:
        """
        Parse file based on type
        Args:
            file_content: File content as string (for TXT/CSV)
            file_type: File extension (txt, csv, docx, pdf)
        """
        file_type = file_type.lower()
        
        if file_type == 'txt':
            return cls.parse_txt(file_content)
        elif file_type == 'csv':
            return cls.parse_csv(file_content)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
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
