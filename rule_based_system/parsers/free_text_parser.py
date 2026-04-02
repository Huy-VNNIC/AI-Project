"""
Free text parser module.
Parser cho requirement viết dạng văn bản tự do.
Dùng spaCy dependency parsing để extract actor/action/object/condition.
"""

import re
import sys

# Lazy load spaCy để không crash nếu chưa cài
_nlp = None

def _get_nlp():
    global _nlp
    if _nlp is None:
        try:
            import spacy
            try:
                _nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("[INFO] Đang download spaCy model en_core_web_sm...")
                import subprocess
                subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"],
                               capture_output=True)
                _nlp = spacy.load("en_core_web_sm")
        except ImportError:
            raise ImportError("Cần cài: pip install spacy && python -m spacy download en_core_web_sm")
    return _nlp


from ..models.canonical import CanonicalRequirement


# Keywords nhận biết condition
CONDITION_KEYWORDS = {"if", "when", "unless", "until", "while", "provided", "given"}

# Keywords nhận biết expected result
EXPECTED_KEYWORDS = {"should", "must", "shall", "will", "can", "need to"}


def parse_free_text(text: str) -> list[CanonicalRequirement]:
    """
    Parse văn bản tự do → list CanonicalRequirement.
    Mỗi câu có nghĩa → 1 requirement.
    """
    nlp = _get_nlp()
    doc = nlp(text)
    results = []

    for sent in doc.sents:
        sent_text = sent.text.strip()
        if len(sent_text.split()) < 3:
            continue  # Bỏ qua câu quá ngắn

        req = _parse_sentence(sent, sent_text)
        if req.is_valid():
            results.append(req)

    return results


def _parse_sentence(sent, raw_text: str) -> CanonicalRequirement:
    """Parse 1 câu → CanonicalRequirement."""

    actor      = _extract_actor(sent)
    action     = _extract_action(sent)
    objects    = _extract_objects(sent)
    conditions = _extract_conditions(raw_text)
    expected   = _extract_expected(sent, raw_text)
    req_type   = _classify_req_type(raw_text)

    return CanonicalRequirement(
        actor=actor,
        action=action,
        objects=objects,
        conditions=conditions,
        expected=expected,
        req_type=req_type,
        source_format="free_text",
        raw_text=raw_text,
    )


def _extract_actor(sent) -> str:
    """Tìm subject (nsubj) của ROOT verb."""
    for token in sent:
        if token.dep_ == "nsubj" and token.head.dep_ == "ROOT":
            return token.lemma_.lower()
        if token.dep_ == "nsubjpass":
            return token.lemma_.lower()

    # Fallback: tìm token đầu tiên là NOUN hoặc PROPN
    for token in sent:
        if token.pos_ in ("NOUN", "PROPN") and not token.is_stop:
            return token.lemma_.lower()

    return "system"  # default


def _extract_action(sent) -> str:
    """Tìm ROOT verb — hành động chính của requirement."""
    for token in sent:
        if token.dep_ == "ROOT" and token.pos_ == "VERB":
            return token.lemma_.lower()

    # Fallback: tìm verb bất kỳ
    for token in sent:
        if token.pos_ == "VERB" and not token.is_stop:
            return token.lemma_.lower()

    return ""


def _extract_objects(sent) -> list[str]:
    """Tìm direct object (dobj) và prepositional object (pobj)."""
    objects = []
    for token in sent:
        if token.dep_ in ("dobj", "pobj", "attr") and not token.is_stop:
            objects.append(token.lemma_.lower())
        # Bắt compound nouns: "email address", "login page"
        if token.dep_ == "compound" and token.head.dep_ in ("dobj", "pobj"):
            compound = f"{token.lemma_.lower()} {token.head.lemma_.lower()}"
            if compound not in objects:
                objects.append(compound)
    return list(set(objects))[:5]  # Giới hạn 5 objects


def _extract_conditions(text: str) -> list[str]:
    """Tìm điều kiện IF/WHEN/UNLESS trong câu."""
    conditions = []
    lower = text.lower()

    for kw in CONDITION_KEYWORDS:
        pattern = re.compile(rf"\b{kw}\b(.+?)(?:,|\.|$)", re.IGNORECASE)
        matches = pattern.findall(text)
        for m in matches:
            clause = m.strip()
            if clause:
                conditions.append(f"{kw} {clause}")

    return conditions[:3]  # Giới hạn 3 conditions


def _extract_expected(sent, text: str) -> str:
    """Tìm expected result — thường sau 'should', 'must', 'shall'."""
    # Tìm modal verb + phần sau
    for token in sent:
        if token.lower_ in EXPECTED_KEYWORDS:
            # Lấy phần còn lại của câu sau modal
            rest = text[text.lower().find(token.lower_):]
            return rest.strip()

    # Fallback: trả về toàn câu
    return text.strip()


def _classify_req_type(text: str) -> str:
    """Phân loại requirement: functional / security / performance."""
    lower = text.lower()

    security_keywords = {"password", "auth", "login", "token", "encrypt", "permission",
                         "role", "access", "secure", "ssl", "tls", "otp", "2fa"}
    perf_keywords = {"response time", "latency", "throughput", "load", "concurrent",
                     "millisecond", "second", "performance", "scalab", "capacity"}

    if any(kw in lower for kw in security_keywords):
        return "security"
    if any(kw in lower for kw in perf_keywords):
        return "performance"
    return "functional"
