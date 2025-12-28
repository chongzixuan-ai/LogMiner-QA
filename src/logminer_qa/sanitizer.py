"""
Sanitization layer responsible for PII detection, token substitution,
and referential hashing before logs reach the analysis engine.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from hashlib import new as hashlib_new
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple

from .config import SanitizerConfig
from .token_store import TokenStore

LOGGER = logging.getLogger(__name__)


_DEFAULT_PATTERNS: Iterable[Tuple[str, str]] = (
    ("ACCOUNT", r"\b\d{10,18}\b"),
    ("CREDIT_CARD", r"\b(?:\d[ -]*?){13,16}\b"),
    ("EMAIL", r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
    ("IBAN", r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b"),
    ("PHONE", r"\+?\d{9,15}"),
    ("SSN", r"\b\d{3}-\d{2}-\d{4}\b"),
)


def _iter_strings(record: Any) -> Iterable[Tuple[List[str], str]]:
    """
    Yield (path, value) pairs for any string leaves inside ecord.
    """
    if isinstance(record, str):
        yield ([], record)
        return

    if isinstance(record, Mapping):
        for key, value in record.items():
            for path, sub_value in _iter_strings(value):
                yield ([str(key), *path], sub_value)
        return

    if isinstance(record, list):
        for idx, value in enumerate(record):
            for path, sub_value in _iter_strings(value):
                yield ([str(idx), *path], sub_value)


@dataclass(slots=True)
class SanitizationResult:
    sanitized: Any
    redaction_map: Dict[str, str]
    hashed_fields: Dict[str, str]


@dataclass(slots=True)
class PatternDetector:
    patterns: Iterable[Tuple[str, str]] = field(default_factory=lambda: _DEFAULT_PATTERNS)

    def find_matches(self, text: str) -> List[Tuple[str, Tuple[int, int]]]:
        matches: List[Tuple[str, Tuple[int, int]]] = []
        for label, pattern in self.patterns:
            for match in re.finditer(pattern, text):
                matches.append((label, match.span()))
        return matches


@dataclass(slots=True)
class SanitizationLayer:
    config: SanitizerConfig = field(default_factory=SanitizerConfig)
    token_store: TokenStore = field(default_factory=TokenStore)
    pattern_detector: PatternDetector = field(default_factory=PatternDetector)

    def sanitize_record(self, record: Any) -> SanitizationResult:
        """
        Sanitize a log record (dict or raw text) by redacting PII.
        """
        if isinstance(record, str):
            sanitized_text, redactions, hashed = self._sanitize_text(record)
            payload = {
                "message": sanitized_text,
                "redactions": redactions,
                "hashed_fields": hashed,
            }
            return SanitizationResult(
                sanitized=payload, redaction_map=redactions, hashed_fields=hashed
            )

        cloned = json.loads(json.dumps(record))
        redaction_map: Dict[str, str] = {}
        hashed_fields: Dict[str, str] = {}
        for path, value in _iter_strings(cloned):
            sanitized, redactions, hashed = self._sanitize_text(value)
            if sanitized != value:
                self._apply_path(cloned, path, sanitized)
            redaction_map.update(self._qualify_keys(path, redactions))
            hashed_fields.update(self._qualify_keys(path, hashed))

        sanitized_payload: Any = cloned
        if isinstance(cloned, dict):
            cloned.setdefault("redactions", {}).update(redaction_map)
            cloned.setdefault("hashed_fields", {}).update(hashed_fields)
            sanitized_payload = cloned

        return SanitizationResult(
            sanitized=sanitized_payload,
            redaction_map=redaction_map,
            hashed_fields=hashed_fields,
        )

    def _apply_path(self, root: MutableMapping[str, Any] | list, path: List[str], value: str) -> None:
        target: Any = root
        for key in path[:-1]:
            try:
                idx = int(key)
                target = target[idx]
            except ValueError:
                target = target[key]
        final_key = path[-1]
        try:
            idx = int(final_key)
            target[idx] = value
        except ValueError:
            target[final_key] = value

    def _qualify_keys(self, path: List[str], mapping: Dict[str, str]) -> Dict[str, str]:
        if not path:
            return mapping
        prefix = ".".join(path)
        return {f"{prefix}.{key}" if key else prefix: value for key, value in mapping.items()}

    def _sanitize_text(self, text: str) -> Tuple[str, Dict[str, str], Dict[str, str]]:
        redactions: Dict[str, str] = {}
        hashed_fields: Dict[str, str] = {}
        spans = self._collect_spans(text)
        if not spans:
            return text, redactions, hashed_fields

        fragments: List[str] = []
        cursor = 0
        for label, span in sorted(spans, key=lambda item: item[1][0]):
            start, end = span
            fragments.append(text[cursor:start])
            original = text[start:end]
            token = self.token_store.get_token(original)
            fragments.append(token)
            redactions[token] = label
            hashed_fields[token] = self._hash_value(original)
            cursor = end
        fragments.append(text[cursor:])
        sanitized = "".join(fragments)
        return sanitized, redactions, hashed_fields

    def _collect_spans(self, text: str) -> List[Tuple[str, Tuple[int, int]]]:
        spans = list(self.pattern_detector.find_matches(text))
        # Deduplicate overlapping spans by choosing the longest window
        deduped: List[Tuple[str, Tuple[int, int]]] = []
        for label, span in sorted(spans, key=lambda item: (item[1][0], -(item[1][1] - item[1][0]))):
            if not deduped or span[0] >= deduped[-1][1][1]:
                deduped.append((label, span))
        return deduped

    def _hash_value(self, value: str) -> str:
        hash_obj = hashlib_new(self.config.hash_algorithm)
        secret = self._resolve_secret()
        hash_obj.update(secret.encode("utf-8"))
        hash_obj.update(value.encode("utf-8"))
        return hash_obj.hexdigest()

    def _resolve_secret(self) -> str:
        import os

        secret = os.environ.get(self.config.hashing_secret_env)
        if not secret:
            LOGGER.warning(
                "Hashing secret environment variable '%s' not set. Using default.",
                self.config.hashing_secret_env,
            )
            secret = "logminer-default-secret"
        return secret

    def sanitize_json_lines(self, source: Iterable[str]) -> Iterable[str]:
        """
        Convenience generator that accepts newline-delimited JSON logs.
        """
        for line in source:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                sanitized = self.sanitize_record(line).sanitized
            else:
                sanitized = self.sanitize_record(record).sanitized
            yield json.dumps(sanitized)
