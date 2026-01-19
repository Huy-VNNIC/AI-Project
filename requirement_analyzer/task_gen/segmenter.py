"""
Segmenter: Tách document thành sections và sentences
"""
import re
from typing import List, Tuple, Optional
from dataclasses import dataclass
import spacy
from pathlib import Path


@dataclass
class Sentence:
    """Một câu với metadata"""
    text: str
    section: Optional[str] = None
    offset_start: int = 0
    offset_end: int = 0
    line_number: int = 0
    tokens: List[str] = None
    
    def __post_init__(self):
        if self.tokens is None:
            self.tokens = self.text.split()


@dataclass
class Section:
    """Một section trong document"""
    title: str
    content: str
    level: int  # heading level
    offset_start: int
    offset_end: int
    sentences: List[Sentence] = None
    
    def __post_init__(self):
        if self.sentences is None:
            self.sentences = []


class DocumentSegmenter:
    """
    Tách document thành sections và sentences
    Giữ offset để trace ngược lại
    """
    
    def __init__(self):
        # Load spaCy for sentence splitting
        try:
            self.nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])
            self.nlp.add_pipe("sentencizer")
        except OSError:
            print("⚠️  spaCy model not found, using fallback sentence splitter")
            self.nlp = None
        
        # Heading patterns (markdown and numbered)
        self.heading_patterns = [
            # Markdown headings
            (r'^(#{1,6})\s+(.+)$', 'markdown'),
            # Numbered headings: 1., 1.1, 1.1.1
            (r'^(\d+(?:\.\d+)*\.?)\s+(.+)$', 'numbered'),
            # ALL CAPS headings
            (r'^([A-Z\s]{5,})$', 'caps'),
            # Underlined headings (next line is ===== or -----)
            (r'^(.+)\n([=\-]{3,})$', 'underlined'),
        ]
    
    def segment(self, text: str) -> Tuple[List[Section], List[Sentence]]:
        """
        Segment document into sections and sentences
        Returns: (sections, all_sentences)
        """
        # Normalize text
        text = self._normalize_text(text)
        
        # Extract sections
        sections = self._extract_sections(text)
        
        # Extract sentences from each section
        all_sentences = []
        for section in sections:
            sentences = self._extract_sentences(
                section.content,
                section.title,
                section.offset_start
            )
            section.sentences = sentences
            all_sentences.extend(sentences)
        
        # If no sections found, treat whole doc as one section
        if not sections:
            default_section = Section(
                title="Document",
                content=text,
                level=0,
                offset_start=0,
                offset_end=len(text)
            )
            sentences = self._extract_sentences(text, "Document", 0)
            default_section.sentences = sentences
            sections = [default_section]
            all_sentences = sentences
        
        return sections, all_sentences
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text"""
        # Fix multiple spaces
        text = re.sub(r'[ \t]+', ' ', text)
        # Fix multiple newlines (but keep paragraph breaks)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
    
    def _extract_sections(self, text: str) -> List[Section]:
        """Extract sections from document"""
        sections = []
        lines = text.split('\n')
        
        current_section = None
        current_content = []
        current_offset = 0
        
        for line_idx, line in enumerate(lines):
            line = line.strip()
            
            # Check if line is a heading
            heading_info = self._is_heading(line)
            
            if heading_info:
                # Save previous section
                if current_section:
                    content = '\n'.join(current_content).strip()
                    current_section.content = content
                    current_section.offset_end = current_offset
                    if content:  # only add non-empty sections
                        sections.append(current_section)
                
                # Start new section
                title, level = heading_info
                current_section = Section(
                    title=title,
                    content='',
                    level=level,
                    offset_start=current_offset,
                    offset_end=0
                )
                current_content = []
            else:
                # Add to current section
                if line:
                    current_content.append(line)
            
            current_offset += len(line) + 1  # +1 for newline
        
        # Save last section
        if current_section:
            content = '\n'.join(current_content).strip()
            current_section.content = content
            current_section.offset_end = current_offset
            if content:
                sections.append(current_section)
        
        return sections
    
    def _is_heading(self, line: str) -> Optional[Tuple[str, int]]:
        """Check if line is a heading. Returns (title, level) or None"""
        if not line or len(line) < 2:
            return None
        
        # Markdown headings
        match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if match:
            hashes, title = match.groups()
            return (title.strip(), len(hashes))
        
        # Numbered headings: 1., 1.1., 1.1.1.
        match = re.match(r'^(\d+(?:\.\d+)*\.?)\s+(.+)$', line)
        if match:
            number, title = match.groups()
            level = len(number.split('.'))
            return (title.strip(), level)
        
        # ALL CAPS (at least 5 chars, mostly uppercase)
        if len(line) >= 5 and line.isupper() and line.replace(' ', '').isalpha():
            return (line.strip(), 1)
        
        return None
    
    def _extract_sentences(
        self,
        text: str,
        section_title: str,
        section_offset: int
    ) -> List[Sentence]:
        """Extract sentences from text"""
        sentences = []
        
        if self.nlp:
            # Use spaCy sentencizer
            doc = self.nlp(text)
            offset = section_offset
            
            for sent in doc.sents:
                sent_text = sent.text.strip()
                if len(sent_text) < 5:  # skip very short sentences
                    continue
                
                sentence = Sentence(
                    text=sent_text,
                    section=section_title,
                    offset_start=offset,
                    offset_end=offset + len(sent_text),
                    tokens=[token.text for token in sent]
                )
                sentences.append(sentence)
                offset += len(sent.text)
        else:
            # Fallback: simple sentence splitting
            simple_sents = self._simple_sentence_split(text)
            offset = section_offset
            
            for sent_text in simple_sents:
                if len(sent_text) < 5:
                    continue
                
                sentence = Sentence(
                    text=sent_text,
                    section=section_title,
                    offset_start=offset,
                    offset_end=offset + len(sent_text),
                    tokens=sent_text.split()
                )
                sentences.append(sentence)
                offset += len(sent_text) + 1
        
        return sentences
    
    def _simple_sentence_split(self, text: str) -> List[str]:
        """Simple rule-based sentence splitting (fallback)"""
        # Split on sentence-ending punctuation followed by space and capital
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def get_sentence_context(
        self,
        sentence: Sentence,
        all_sentences: List[Sentence],
        context_before: int = 1,
        context_after: int = 1
    ) -> str:
        """Get surrounding context for a sentence"""
        try:
            idx = all_sentences.index(sentence)
            start_idx = max(0, idx - context_before)
            end_idx = min(len(all_sentences), idx + context_after + 1)
            
            context_sentences = all_sentences[start_idx:end_idx]
            return ' '.join(s.text for s in context_sentences)
        except ValueError:
            return sentence.text


# Singleton instance
_segmenter = None

def get_segmenter() -> DocumentSegmenter:
    """Get singleton segmenter instance"""
    global _segmenter
    if _segmenter is None:
        _segmenter = DocumentSegmenter()
    return _segmenter
