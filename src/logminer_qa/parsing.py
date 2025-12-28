"""
Advanced log parsing utilities leveraging regex and optional spaCy NLP.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:  # pragma: no cover
    from spacy.language import Language

LOGGER = logging.getLogger(__name__)

API_ENDPOINT_PATTERN = re.compile(
    r"\b(?:GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD)\s+(/[A-Za-z0-9_\-./]+)", re.IGNORECASE
)
STATUS_CODE_PATTERN = re.compile(r"\b(?:status:?|code:?|http/1\.[01])\s*(\d{3})", re.IGNORECASE)
AMOUNT_PATTERN = re.compile(r"\b\d+(?:[.,]\d{2})?\b")
ACCOUNT_TOKEN_PATTERN = re.compile(r"\[TOKEN_[A-Z0-9]+\]")
ERROR_TOKEN_PATTERN = re.compile(r"\b(?:ERR|ERROR|EXCEPTION|FAIL)(?:[_-]?\w+)*\b", re.IGNORECASE)


def _safe_import_spacy() -> Optional["Language"]:
    try:
        import spacy

        try:
            return spacy.load("en_core_web_sm")
        except OSError:
            LOGGER.warning("spaCy model 'en_core_web_sm' not found; using blank English model.")
            return spacy.blank("en")
    except Exception as exc:  # pragma: no cover - import failure branch
        LOGGER.warning("spaCy unavailable: %s", exc)
        return None


@dataclass(slots=True)
class ParsedRecord:
    message: str
    api_endpoints: List[str] = field(default_factory=list)
    status_codes: List[str] = field(default_factory=list)
    monetary_values: List[str] = field(default_factory=list)
    account_tokens: List[str] = field(default_factory=list)
    error_tokens: List[str] = field(default_factory=list)
    entities: List[Dict[str, str]] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "message": self.message,
            "api_endpoints": self.api_endpoints,
            "status_codes": self.status_codes,
            "monetary_values": self.monetary_values,
            "account_tokens": self.account_tokens,
            "error_tokens": self.error_tokens,
            "entities": self.entities,
            "keywords": self.keywords,
        }


class LogParser:
    """
    Enrich log records with structured insights extracted via regex and NLP.

    The parser is spaCy-aware but gracefully degrades if the model is missing.
    """

    def __init__(self, enable_nlp: bool = True) -> None:
        self.enable_nlp = enable_nlp
        self._nlp = _safe_import_spacy() if enable_nlp else None

    def parse_record(self, record: Any) -> ParsedRecord:
        message = self._extract_message(record)
        parsed = ParsedRecord(message=message)
        parsed.api_endpoints = self._unique(API_ENDPOINT_PATTERN.findall(message))
        parsed.status_codes = self._unique(STATUS_CODE_PATTERN.findall(message))
        parsed.monetary_values = self._unique(AMOUNT_PATTERN.findall(message))
        parsed.account_tokens = self._unique(ACCOUNT_TOKEN_PATTERN.findall(message))
        parsed.error_tokens = self._unique(ERROR_TOKEN_PATTERN.findall(message))
        if self._nlp:
            doc = self._nlp(message)
            parsed.entities = [
                {"text": ent.text, "label": ent.label_} for ent in doc.ents if ent.text.strip()
            ]
            parsed.keywords = self._unique(
                token.lemma_.lower()
                for token in doc
                if token.is_alpha and not token.is_stop and len(token.text) > 2
            )
        return parsed

    def _extract_message(self, record: Any) -> str:
        if isinstance(record, str):
            return record
        if isinstance(record, dict):
            for key in ("message", "msg", "log", "description", "detail"):
                value = record.get(key)
                if isinstance(value, str):
                    return value
            return str(record)
        return str(record)

    @staticmethod
    def _unique(items: Any) -> List[str]:
        seen = set()
        unique_items: List[str] = []
        for item in items:
            if not item:
                continue
            normalized = item.strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique_items.append(normalized)
        return unique_items

