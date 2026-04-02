"""
Normalizer module - chuẩn hoá CanonicalRequirement.
"""

import re
from dataclasses import replace
from ..models.canonical import CanonicalRequirement


# Synonym map: tất cả đều về dạng canonical
ACTION_SYNONYMS: dict[str, str] = {
    # Authentication
    "sign in":      "login",
    "log in":       "login",
    "signin":       "login",
    "authenticate": "login",
    "sign out":     "logout",
    "log out":      "logout",
    "signout":      "logout",
    "sign up":      "register",
    "create account": "register",
    "register":     "register",

    # CRUD
    "add":          "create",
    "insert":       "create",
    "make":         "create",
    "delete":       "remove",
    "remove":       "remove",
    "erase":        "remove",
    "edit":         "update",
    "modify":       "update",
    "change":       "update",
    "look up":      "search",
    "find":         "search",
    "retrieve":     "get",
    "fetch":        "get",
    "display":      "show",
    "render":       "show",
    "present":      "show",

    # Forms
    "fill in":      "enter",
    "fill out":     "enter",
    "input":        "enter",
    "type":         "enter",
    "provide":      "enter",
    "submit":       "submit",
    "send":         "submit",
    "upload":       "upload",
    "attach":       "upload",
    "download":     "download",
    "export":       "export",
    "import":       "import",

    # Navigation
    "go to":        "navigate",
    "redirect to":  "navigate",
    "open":         "navigate",
    "click":        "select",
    "choose":       "select",
    "pick":         "select",
}

ACTOR_SYNONYMS: dict[str, str] = {
    "system":       "system",
    "application":  "system",
    "app":          "system",
    "platform":     "system",
    "service":      "system",
    "server":       "system",
    "api":          "system",
    "backend":      "system",
    "database":     "system",
    "admin":        "admin",
    "administrator":"admin",
    "manager":      "admin",
    "superuser":    "admin",
    "guest":        "guest",
    "visitor":      "guest",
    "anonymous":    "guest",
    "customer":     "user",
    "client":       "user",
    "member":       "user",
    "buyer":        "user",
    "shopper":      "user",
}

SECURITY_SIGNALS = {
    "password", "passwd", "credential", "auth", "login", "token",
    "encrypt", "decrypt", "ssl", "tls", "otp", "2fa", "mfa",
    "permission", "role", "access control", "authorization",
}

PERFORMANCE_SIGNALS = {
    "response time", "latency", "throughput", "load", "concurrent",
    "millisecond", "second", "minute", "performance", "scalab",
    "capacity", "speed", "fast", "slow",
}


def normalize(req: CanonicalRequirement) -> CanonicalRequirement:
    """
    Chuẩn hoá 1 CanonicalRequirement.
    Trả về bản đã được normalize (immutable style — tạo object mới).
    """
    action     = _normalize_action(req.action)
    actor      = _normalize_actor(req.actor)
    objects    = _normalize_objects(req.objects)
    req_type   = _normalize_req_type(req)

    # Tạo object mới với các field đã chuẩn hoá
    return replace(
        req,
        action=action,
        actor=actor,
        objects=objects,
        req_type=req_type,
    )


def _normalize_action(action: str) -> str:
    if not action:
        return ""
    action = action.lower().strip()

    # Check synonym map trực tiếp
    if action in ACTION_SYNONYMS:
        return ACTION_SYNONYMS[action]

    # Check multi-word synonyms
    for syn, canonical in ACTION_SYNONYMS.items():
        if action.startswith(syn):
            return canonical

    # Lemmatize đơn giản (bỏ đuôi -ing, -ed, -s)
    action = _simple_lemmatize(action)
    return action


def _normalize_actor(actor: str) -> str:
    if not actor:
        return "user"
    actor = actor.lower().strip()
    return ACTOR_SYNONYMS.get(actor, actor)


def _normalize_objects(objects: list[str]) -> list[str]:
    """Loại bỏ stop words và deduplicate."""
    stop_words = {"the", "a", "an", "to", "of", "in", "on", "at", "for", "with"}
    cleaned = []
    seen = set()
    for obj in objects:
        obj = obj.lower().strip()
        words = [w for w in obj.split() if w not in stop_words]
        cleaned_obj = " ".join(words)
        if cleaned_obj and cleaned_obj not in seen:
            cleaned.append(cleaned_obj)
            seen.add(cleaned_obj)
    return cleaned


def _normalize_req_type(req: CanonicalRequirement) -> str:
    """Re-classify nếu req_type là default 'functional' nhưng có security/perf signals."""
    if req.req_type != "functional":
        return req.req_type

    full_text = " ".join([
        req.raw_text, req.action, req.expected, " ".join(req.objects)
    ]).lower()

    if any(sig in full_text for sig in SECURITY_SIGNALS):
        return "security"
    if any(sig in full_text for sig in PERFORMANCE_SIGNALS):
        return "performance"
    return "functional"


def _simple_lemmatize(word: str) -> str:
    """Lemmatize đơn giản không cần NLTK/spaCy."""
    if word.endswith("ing") and len(word) > 6:
        return word[:-3]
    if word.endswith("tion"):
        return word[:-4] + "e"
    if word.endswith("ed") and len(word) > 4:
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        return word[:-1]
    return word
