"""
Text Preprocessing Module
Clean, normalize, and prepare text for semantic analysis
"""

import re
from typing import List


class TextPreprocessor:
    """Text preprocessing and cleaning"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean raw text: remove headers, footers, page numbers
        Preserve: bullets, numbering, section structure
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove page markers (Page 1, Page 2, etc.)
        text = re.sub(r"(?:^|\n)(?:Page|p\.)\s+\d+\s*(?:\n|$)", "\n", text)
        
        # Remove multiple consecutive blank lines (normalize to max 2)
        text = re.sub(r"\n\n\n+", "\n\n", text)
        
        # Remove extra spaces but preserve structure
        lines = text.split("\n")
        cleaned_lines = []
        
        for line in lines:
            # Strip leading/trailing whitespace but preserve indentation signal
            line = line.rstrip()
            if line:  # Only keep non-empty lines
                cleaned_lines.append(line)
        
        return "\n".join(cleaned_lines)
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text for processing
        - Convert to lowercase for analysis (but keep original)
        - Remove special characters that don't affect meaning
        - Normalize spacing
        
        Args:
            text: Cleaned text
            
        Returns:
            Normalized text (lowercase)
        """
        # Lowercase for processing
        text = text.lower()
        
        # Normalize multiple spaces to single space
        text = re.sub(r" +", " ", text)
        
        # Normalize quotes
        text = text.replace(""", '"').replace(""", '"')
        text = text.replace("'", "'").replace("'", "'")
        
        return text
    
    @staticmethod
    def remove_noise(text: str) -> str:
        """
        Remove common noise patterns
        
        Args:
            text: Text to clean
            
        Returns:
            Text with noise removed
        """
        # Remove URLs
        text = re.sub(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", "", text)
        
        # Remove email addresses (but keep mention if in requirement)
        text = re.sub(r"(?<![a-zA-Z0-9])[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?![a-zA-Z0-9])", "[EMAIL]", text)
        
        # Remove file paths
        text = re.sub(r"(?:\/|\\)[\w\/\\.-]+", "[FILE_PATH]", text)
        
        # Remove excessive punctuation
        text = re.sub(r"\.{2,}", ".", text)
        text = re.sub(r"!{2,}", "!", text)
        text = re.sub(r"\?{2,}", "?", text)
        
        return text
    
    @staticmethod
    def extract_requirements_section(text: str) -> str:
        """
        Extract main requirements section (skip intro, table of contents)
        Look for common markers: "Requirements", "Specifications", "Features"
        
        Args:
            text: Full document text
            
        Returns:
            Text containing main requirements
        """
        # Find common requirement section markers
        markers = [
            r"(?i)(?:^|\n)#{1,3}\s*(?:requirements|specifications|functional\s*requirements)",
            r"(?i)^(?:requirements|specifications|features):",
        ]
        
        # Try to find requirement section
        for marker in markers:
            match = re.search(marker, text)
            if match:
                # Start from this marker and take everything after
                start = match.start()
                return text[start:]
        
        # If no marker found, return all text
        return text
    
    @staticmethod
    def process(text: str) -> str:
        """
        Main preprocessing pipeline
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned and normalized text
        """
        text = TextPreprocessor.clean_text(text)
        text = TextPreprocessor.remove_noise(text)
        text = TextPreprocessor.extract_requirements_section(text)
        text = TextPreprocessor.normalize_text(text)
        
        return text


# Demo usage
if __name__ == "__main__":
    sample_text = """
    Page 1
    
    ==== SYSTEM REQUIREMENTS ====
    
    The user should be able to:
    - Login with email and password
    - Update profile information  
    - Delete account permanently
    
    http://example.com should be accessible
    
    
    When the user logs in, the system must verify credentials.
    """
    
    processor = TextPreprocessor()
    result = processor.process(sample_text)
    print("Processed text:")
    print(result)
