"""
Requirement Pre-filtering and Validation
Lọc bỏ notes, meeting notes, headings trước khi đưa vào detector
"""
import re
from typing import List


# Pattern để detect notes/meeting/document descriptions
NOTE_PATTERNS = [
    r"\bwe discussed\b",
    r"\blast meeting\b",
    r"\bthis document describes\b",
    r"\bnote:\b",
    r"\bmockups?\b",
    r"\barchitecture\b",
    r"\bgiới thiệu\b",
    r"\bmục tiêu\b",
    r"\bphạm vi\b",
    r"\bbackground\b",
    r"\bintroduction\b",
    r"\bmeeting minutes\b",
]

# Pattern để detect requirement signals (English + Vietnamese)
REQ_SIGNAL_EN = re.compile(
    r"\b(must|shall|should|required to|needs to|need to|has to|be able to|is required to|are required to)\b",
    re.IGNORECASE
)

REQ_SIGNAL_VI = re.compile(
    r"\b(phải|cần|bắt buộc|được phép|nên|yêu cầu)\b",
    re.IGNORECASE
)

# Pattern để bỏ headings
DROP_HEADINGS = re.compile(
    r"^\s*(#{1,6}\s+|giới thiệu|mục tiêu|phạm vi|ràng buộc|lịch trình|rủi ro|phụ lục|introduction|background|scope|constraints)\b",
    re.IGNORECASE
)


def is_note_like(text: str) -> bool:
    """
    Check if text looks like a note/meeting/description (not a requirement)
    
    Returns:
        True if text looks like non-requirement content
    """
    text_lower = text.strip().lower()
    
    # Check against note patterns
    for pattern in NOTE_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    
    return False


def is_requirement_like(text: str) -> bool:
    """
    Check if text has requirement signals (modal verbs)
    
    Returns:
        True if text contains requirement keywords
    """
    return bool(REQ_SIGNAL_EN.search(text) or REQ_SIGNAL_VI.search(text))


def is_valid_requirement_candidate(text: str) -> bool:
    """
    Validate if text is a valid requirement candidate
    
    Criteria:
    - Not too short (< 10 chars)
    - Not too long (> 500 chars)
    - Not a heading
    - If looks like note, must have requirement signal
    
    Returns:
        True if text should be kept for requirement detection
    """
    text_stripped = text.strip()
    
    # Length check
    if len(text_stripped) < 10 or len(text_stripped) > 500:
        return False
    
    # Heading check
    if DROP_HEADINGS.search(text_stripped):
        return False
    
    # If looks like note, must have requirement signal
    if is_note_like(text_stripped):
        if not is_requirement_like(text_stripped):
            return False
    
    return True


def prefilter_sentences(sentences: List[str]) -> List[str]:
    """
    Pre-filter sentences before requirement detection
    
    Removes:
    - Empty/too short sentences
    - Notes/meeting minutes without requirement signals
    - Headings/section titles
    
    Args:
        sentences: List of raw sentences
        
    Returns:
        Filtered list of requirement candidates
    """
    filtered = []
    
    for sent in sentences:
        if is_valid_requirement_candidate(sent):
            filtered.append(sent.strip())
    
    return filtered


def normalize_line(line: str) -> str:
    """
    Normalize a line by removing numbering, bullets, etc.
    
    Examples:
        "1. Users must login" → "Users must login"
        "- The system shall..." → "The system shall..."
    """
    # Remove numbering: "1." "2)" "a." etc.
    line = re.sub(r"^\s*[\d\w]+[\.\)]\s*", "", line)
    
    # Remove bullets: "-" "•" "*"
    line = re.sub(r"^\s*[-•*]\s*", "", line)
    
    return line.strip()


def extract_requirements_from_text(raw_text: str) -> List[str]:
    """
    Extract requirement candidates from raw document text
    
    Steps:
    1. Split by lines
    2. Normalize (remove bullets, numbering)
    3. Filter (drop headings, notes)
    4. Keep only lines with requirement signals
    5. Deduplicate
    
    Args:
        raw_text: Raw document text (from file or textarea)
        
    Returns:
        List of requirement candidate strings
    """
    candidates = []
    seen = set()
    
    for raw_line in raw_text.splitlines():
        # Normalize
        line = normalize_line(raw_line)
        
        if not line:
            continue
        
        # Validate
        if not is_valid_requirement_candidate(line):
            continue
        
        # Deduplicate (case-insensitive)
        line_key = line.lower()
        if line_key in seen:
            continue
        
        seen.add(line_key)
        candidates.append(line)
    
    return candidates
