"""
Core input processor module.
Step 1 của pipeline: nhận file bất kỳ → trả về raw text.
Hỗ trợ: PDF, DOCX, TXT, XLSX, CSV.
"""

import os
from pathlib import Path


def extract_raw_text(filepath: str) -> str:
    """
    Entry point chính. Tự detect loại file và extract text tương ứng.

    Args:
        filepath: đường dẫn đến file requirement

    Returns:
        Raw text string đã extract
    """
    path = Path(filepath)
    ext = path.suffix.lower()

    extractors = {
        ".pdf":  _extract_pdf,
        ".docx": _extract_docx,
        ".txt":  _extract_txt,
        ".xlsx": _extract_excel_as_text,
        ".csv":  _extract_csv_as_text,
    }

    extractor = extractors.get(ext)
    if not extractor:
        raise ValueError(f"Unsupported file type: {ext}. Supported: {list(extractors.keys())}")

    return extractor(filepath)


def _extract_pdf(filepath: str) -> str:
    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)
    except ImportError:
        raise ImportError("Cần cài: pip install pdfplumber")


def _extract_docx(filepath: str) -> str:
    try:
        from docx import Document
        doc = Document(filepath)
        paragraphs = []
        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text.strip())
        return "\n".join(paragraphs)
    except ImportError:
        raise ImportError("Cần cài: pip install python-docx")


def _extract_txt(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def _extract_excel_as_text(filepath: str) -> str:
    """
    Với Excel: convert sang text dạng 'column: value' để format detector nhận biết.
    Vẫn giữ filepath để ExcelParser đọc trực tiếp sau.
    """
    try:
        import pandas as pd
        df = pd.read_excel(filepath)
        lines = []
        for _, row in df.iterrows():
            parts = [f"{col}: {val}" for col, val in row.items() if str(val).strip() not in ("", "nan")]
            lines.append(" | ".join(parts))
        return "\n".join(lines)
    except ImportError:
        raise ImportError("Cần cài: pip install pandas openpyxl")


def _extract_csv_as_text(filepath: str) -> str:
    try:
        import pandas as pd
        df = pd.read_csv(filepath)
        lines = []
        for _, row in df.iterrows():
            parts = [f"{col}: {val}" for col, val in row.items() if str(val).strip() not in ("", "nan")]
            lines.append(" | ".join(parts))
        return "\n".join(lines)
    except ImportError:
        raise ImportError("Cần cài: pip install pandas")
