"""
Embedding backends
==================

Pluggable label-classification backends compatible with
``SemanticParser(embedding_backend=…)``.

Signature contract
------------------
A backend is any callable with::

    backend(text: str, candidates: Iterable[str]) -> tuple[str | None, float]

returning ``(best_label, similarity_score_in_[0,1])`` or ``(None, 0.0)``
when it has no opinion.

Two backends ship here:

* ``SentenceTransformerBackend`` — real semantic similarity using
  ``sentence-transformers`` (lazy import; fails *gracefully*).
* ``KeywordOverlapBackend`` — zero-dependency Jaccard fallback so the
  pipeline keeps working in CI / minimal environments.
"""
from __future__ import annotations

import logging
import re
from typing import Iterable, List, Optional, Tuple

log = logging.getLogger(__name__)


# ── Pretty labels (used as fake "definitions" the encoder embeds) ──────────
# Mapping a canonical key to a richer phrase improves embedding-similarity
# accuracy because the encoder sees natural language instead of a slug.
LABEL_DESCRIPTIONS = {
    # intents
    "register":   "đăng ký tài khoản, sign up new account",
    "login":      "đăng nhập, log in, authenticate user",
    "logout":     "đăng xuất, log out",
    "book":       "đặt lịch, đặt phòng, đặt vé, make a reservation",
    "pay":        "thanh toán, payment, checkout",
    "refund":     "hoàn tiền, refund, reverse payment",
    "invoice":    "lập hóa đơn, generate invoice",
    "create":     "tạo mới, create record",
    "update":     "cập nhật, edit, modify",
    "delete":     "xóa, remove",
    "search":     "tìm kiếm, search, query",
    "filter":     "lọc, filter results",
    "manage":     "quản lý CRUD danh sách",
    "approve":    "phê duyệt, approve, sign off",
    "diagnose":   "chẩn đoán bệnh, diagnose patient",
    "prescribe":  "kê đơn thuốc, prescribe medication",
    "admit":      "tiếp nhận nội trú, admit patient",
    "discharge":  "xuất viện, discharge patient",
    "operate":    "thực hiện phẫu thuật, perform surgery",
    "report":     "báo cáo, generate report",
    "notify":     "thông báo, notify user",
    "send_email": "gửi email, send email",
    "send_sms":   "gửi tin nhắn, send sms",
    "upload":     "tải lên, upload file",
    "download":   "tải xuống, download file",
    "encrypt":    "mã hóa dữ liệu, encrypt data",
    "audit":      "ghi nhật ký kiểm toán, audit log",
    "backup":     "sao lưu dữ liệu, backup data",
}


# ────────────────────────────────────────────────────────────────────────────
class SentenceTransformerBackend:
    """Wrap a sentence-transformers model as an embedding backend.

    Uses cosine similarity between the requirement sentence and each
    candidate label (rendered through ``LABEL_DESCRIPTIONS`` when known).
    The model is loaded lazily and cached on the instance.

    Parameters
    ----------
    model_name:
        HuggingFace model id. ``paraphrase-multilingual-MiniLM-L12-v2`` is
        the default because the corpus is mixed Vietnamese + English.
    device:
        ``"cpu"`` | ``"cuda"``.  ``None`` → auto.
    """

    def __init__(
        self,
        model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
        device: Optional[str] = None,
    ) -> None:
        self.model_name = model_name
        self.device = device
        self._model = None
        self._cand_cache: dict[Tuple[str, ...], "object"] = {}

    # Lazy heavy import — only when actually called
    def _ensure_model(self) -> bool:
        if self._model is not None:
            return True
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
        except ImportError:
            log.warning(
                "sentence-transformers not installed; "
                "SentenceTransformerBackend disabled. "
                "Install with: pip install sentence-transformers"
            )
            return False
        try:
            self._model = SentenceTransformer(self.model_name, device=self.device)
        except Exception as exc:  # network / disk / cuda issues
            log.warning("Failed to load %s: %s", self.model_name, exc)
            return False
        return True

    def _describe(self, label: str) -> str:
        return LABEL_DESCRIPTIONS.get(label, label.replace("_", " "))

    def __call__(
        self, text: str, candidates: Iterable[str]
    ) -> Tuple[Optional[str], float]:
        cand_list: List[str] = [c for c in candidates if c]
        if not cand_list or not text.strip():
            return None, 0.0
        if not self._ensure_model():
            return None, 0.0

        # Cache candidate embeddings — they don't change between calls
        key = tuple(cand_list)
        cand_emb = self._cand_cache.get(key)
        if cand_emb is None:
            cand_emb = self._model.encode(  # type: ignore[union-attr]
                [self._describe(c) for c in cand_list],
                convert_to_tensor=True,
                normalize_embeddings=True,
            )
            self._cand_cache[key] = cand_emb

        text_emb = self._model.encode(  # type: ignore[union-attr]
            text, convert_to_tensor=True, normalize_embeddings=True
        )

        # Cosine similarity (vectors are normalised → dot product)
        from sentence_transformers import util  # type: ignore
        sims = util.cos_sim(text_emb, cand_emb)[0]
        best_idx = int(sims.argmax())
        best_score = float(sims[best_idx])
        return cand_list[best_idx], best_score


# ────────────────────────────────────────────────────────────────────────────
class KeywordOverlapBackend:
    """Zero-dependency Jaccard fallback.

    Useful for CI, unit tests, or environments without `sentence-transformers`.
    Score = |intersection| / |union| over case-folded word tokens.
    """

    _TOKEN = re.compile(r"[\w\u00C0-\u1EF9]+", re.UNICODE)

    def _tokens(self, s: str) -> set[str]:
        return {t.lower() for t in self._TOKEN.findall(s)}

    def __call__(
        self, text: str, candidates: Iterable[str]
    ) -> Tuple[Optional[str], float]:
        text_toks = self._tokens(text)
        if not text_toks:
            return None, 0.0
        best_label: Optional[str] = None
        best_score = 0.0
        for c in candidates:
            desc = LABEL_DESCRIPTIONS.get(c, c.replace("_", " "))
            cand_toks = self._tokens(desc)
            if not cand_toks:
                continue
            inter = len(text_toks & cand_toks)
            if inter == 0:
                continue
            union = len(text_toks | cand_toks)
            score = inter / union
            if score > best_score:
                best_score = score
                best_label = c
        return best_label, best_score


# ────────────────────────────────────────────────────────────────────────────
def auto_backend() -> "object":
    """Return the best available backend without raising.

    Tries `SentenceTransformerBackend` first; falls back to keyword overlap.
    Useful for one-line wiring::

        from .embedding import auto_backend
        parser = SemanticParser(embedding_backend=auto_backend())
    """
    st = SentenceTransformerBackend()
    if st._ensure_model():
        log.info("auto_backend: using SentenceTransformerBackend (%s)",
                 st.model_name)
        return st
    log.info("auto_backend: falling back to KeywordOverlapBackend")
    return KeywordOverlapBackend()
