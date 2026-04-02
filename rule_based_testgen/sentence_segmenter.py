"""
Sentence Segmentation Module
Split text into atomic requirement units
Preserve conditional clauses (if/when/then)
"""

import re
from typing import List
from config import CONDITIONAL_KEYWORDS


class SentenceSegmenter:
    """Split text into requirement units"""
    
    @staticmethod
    def segment_by_delimiter(text: str) -> List[str]:
        """
        First pass: Split by clear delimiters
        - Bullet points (-, •, *, ◦)
        - Numbers (1., 2., 3.)
        - Period/Semicolon (but careful with abbreviations)
        
        Args:
            text: Preprocessed text
            
        Returns:
            List of potential requirement sentences
        """
        sentences = []
        
        # Split by bullet points
        bullet_pattern = r"^[\s]*[-•*◦]\s+"
        lines = text.split("\n")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line starts with bullet
            if re.match(bullet_pattern, line):
                # Remove bullet point
                sentence = re.sub(bullet_pattern, "", line)
                sentences.append(sentence)
            # Check if line starts with number
            elif re.match(r"^\d+[\.\)]\s+", line):
                # Remove numbering
                sentence = re.sub(r"^\d+[\.\)]\s+", "", line)
                sentences.append(sentence)
            # Regular sentence
            elif line:
                sentences.append(line)
        
        return sentences
    
    @staticmethod
    def is_conditional(sentence: str) -> bool:
        """
        Check if sentence contains conditional logic
        
        Args:
            sentence: Single sentence
            
        Returns:
            True if conditional
        """
        lower_sent = sentence.lower()
        for keyword in CONDITIONAL_KEYWORDS:
            if keyword in lower_sent:
                return True
        return False
    
    @staticmethod
    def split_conditional_clauses(sentence: str) -> List[str]:
        """
        For conditional sentences, try to split smart:
        "If user is admin, then they can delete users" →
        → Keep as one unit (it's one requirement)
        
        But: "User enters email. System validates. Email is stored." →
        → Keep as separate units
        
        Strategy: if sentence has conditional keyword + clear then/consequence,
        keep together. Otherwise split by period.
        
        Args:
            sentence: Single sentence
            
        Returns:
            List of requirement units
        """
        if not SentenceSegmenter.is_conditional(sentence):
            # Not conditional, just split by period
            parts = re.split(r"[.;]\s+", sentence)
            return [p.strip() for p in parts if p.strip()]
        else:
            # Conditional sentence - keep as unit if it's one logical requirement
            # Pattern: "IF condition THEN result" or "When X happens, Y occurs"
            # These should be kept together
            return [sentence]
    
    @staticmethod
    def clean_requirement_sentence(sent: str) -> str:
        """
        Clean individual requirement sentence
        - Remove leading/trailing whitespace
        - Add period if missing
        - Remove duplicates
        
        Args:
            sent: Single requirement sentence
            
        Returns:
            Cleaned sentence
        """
        sent = sent.strip()
        
        # Add period if missing
        if sent and not sent.endswith((".", "!", "?")):
            sent += "."
        
        return sent
    
    @staticmethod
    def segment(text: str, min_length: int = 5) -> List[str]:
        """
        Main segmentation pipeline
        
        Args:
            text: Preprocessed text
            min_length: Minimum sentence length (words)
            
        Returns:
            List of requirement sentences
        """
        requirements = []
        
        # First pass: bullet/numbering split
        sentences = SentenceSegmenter.segment_by_delimiter(text)
        
        # Second pass: handle conditionals
        for sent in sentences:
            if SentenceSegmenter.is_conditional(sent):
                # Keep conditional as single unit
                cleaned = SentenceSegmenter.clean_requirement_sentence(sent)
                if len(cleaned.split()) >= min_length:
                    requirements.append(cleaned)
            else:
                # Split non-conditional by period
                parts = SentenceSegmenter.split_conditional_clauses(sent)
                for part in parts:
                    cleaned = SentenceSegmenter.clean_requirement_sentence(part)
                    if len(cleaned.split()) >= min_length:
                        requirements.append(cleaned)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_reqs = []
        for req in requirements:
            req_lower = req.lower()
            if req_lower not in seen:
                seen.add(req_lower)
                unique_reqs.append(req)
        
        return unique_reqs


# Demo
if __name__ == "__main__":
    text = """
    - User enters email and password
    - System validates credentials
    - If email is valid and password matches, display success message
    - When user clicks logout, session is destroyed
    - Email is stored securely
    """
    
    segmenter = SentenceSegmenter()
    results = segmenter.segment(text)
    
    print("Segmented requirements:")
    for i, req in enumerate(results, 1):
        print(f"{i}. {req}")
