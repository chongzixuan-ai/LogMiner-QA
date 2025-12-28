"""
Persistent token store for referential integrity.

The token store keeps a stable mapping between original values and their
sanitized tokens, so recurring identifiers continue to correlate across
log lines without exposing raw PII.
"""
from __future__ import annotations

import json
import threading
from dataclasses import dataclass, field
from hashlib import blake2b
from pathlib import Path
from typing import Dict


def _default_encoder(value: str) -> str:
    digest = blake2b(value.encode("utf-8"), digest_size=12)
    return digest.hexdigest().upper()


@dataclass(slots=True)
class TokenStore:
    store_path: Path | None = None
    token_prefix: str = "[TOKEN_"
    token_suffix: str = "]"
    encoder = staticmethod(_default_encoder)
    persist_batch_size: int = 100  # Batch writes for performance
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)
    _mapping: Dict[str, str] = field(default_factory=dict, init=False)
    _dirty_count: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        if self.store_path:
            self.store_path.parent.mkdir(parents=True, exist_ok=True)
            if self.store_path.exists():
                with self.store_path.open("r", encoding="utf-8") as handle:
                    data = json.load(handle)
                    if isinstance(data, dict):
                        self._mapping = data

    def _make_token(self, value: str) -> str:
        encoded = self.encoder(value)
        return f"{self.token_prefix}{encoded}{self.token_suffix}"

    def get_token(self, value: str) -> str:
        with self._lock:
            token = self._mapping.get(value)
            if token is None:
                token = self._make_token(value)
                self._mapping[value] = token
                self._dirty_count += 1
                # Batch persistence: only write every N new tokens
                if self._dirty_count >= self.persist_batch_size:
                    self._persist()
                    self._dirty_count = 0
            return token

    def flush(self) -> None:
        """Force immediate persistence of all pending changes."""
        with self._lock:
            if self._dirty_count > 0:
                self._persist()
                self._dirty_count = 0

    def _persist(self) -> None:
        if not self.store_path:
            return
        with self.store_path.open("w", encoding="utf-8") as handle:
            json.dump(self._mapping, handle, indent=2, sort_keys=True)
