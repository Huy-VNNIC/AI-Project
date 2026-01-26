"""
Ingestion Package
Extract and process text from files
"""
from .extract_text import extract_text, extract_text_from_txt, extract_text_from_docx, extract_text_from_pdf

__all__ = [
    'extract_text',
    'extract_text_from_txt',
    'extract_text_from_docx',
    'extract_text_from_pdf',
]
