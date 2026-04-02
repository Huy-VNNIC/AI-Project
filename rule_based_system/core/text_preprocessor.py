"""
Text preprocessor module.
Bước 2: làm sạch raw text trước khi đưa vào parser.
Loại bỏ noise nhưng GIỮ NGUYÊN cấu trúc logic.
"""

import re


def preprocess(text: str) -> str:
    """
    Pipeline làm sạch text theo thứ tự:
    1. Chuẩn hoá line endings
    2. Xoá page numbers / headers thừa
    3. Xoá ký tự đặc biệt vô nghĩa
    4. Chuẩn hoá whitespace
    5. Giữ nguyên bullet points và numbering
    """
    text = _normalize_line_endings(text)
    text = _remove_page_artifacts(text)
    text = _remove_special_chars(text)
    text = _normalize_whitespace(text)
    return text.strip()


def _normalize_line_endings(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _remove_page_artifacts(text: str) -> str:
    # Xoá "Page X of Y", "- X -"
    text = re.sub(r"[Pp]age\s+\d+\s+(of\s+\d+)?", "", text)
    text = re.sub(r"^\s*-\s*\d+\s*-\s*$", "", text, flags=re.MULTILINE)
    # Xoá dòng chỉ có số (page numbers đứng riêng)
    text = re.sub(r"^\s*\d{1,3}\s*$", "", text, flags=re.MULTILINE)
    return text


def _remove_special_chars(text: str) -> str:
    # Giữ lại: chữ cái, số, dấu câu thông thường, bullet chars
    text = re.sub(r"[^\w\s\.\,\;\:\!\?\(\)\[\]\-\/\'\"\•\–\—\n]", " ", text)
    return text


def _normalize_whitespace(text: str) -> str:
    # Nhiều space liên tiếp → 1 space
    text = re.sub(r"[ \t]+", " ", text)
    # Nhiều dòng trống liên tiếp → tối đa 2 dòng
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def split_into_chunks(text: str) -> list[str]:
    """
    Tách text thành các block (section/paragraph) độc lập.
    Dùng để giúp parser nhận biết ranh giới giữa các requirement group.
    """
    # Tách theo dòng trống
    chunks = re.split(r"\n\s*\n", text)
    return [c.strip() for c in chunks if c.strip()]
