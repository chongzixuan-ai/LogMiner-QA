"""
Base classes and helpers for log ingestion connectors.
"""
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Iterable, Iterator, Mapping, MutableMapping, Optional


NormalizedRecord = Dict[str, Any]


@dataclass(slots=True)
class ConnectorConfig:
    """
    Generic configuration options shared by connectors.
    """

    name: str
    options: Mapping[str, Any] = field(default_factory=dict)


class LogConnector(abc.ABC):
    """
    Abstraction for a connector that can fetch and normalize log records.

    Implementations should yield dictionaries to align with downstream
    sanitization and analysis expectations. Raw responses can be returned as
    strings when unavoidable, but connectors should make best-effort to
    structure data.
    """

    def __init__(self, config: ConnectorConfig) -> None:
        self.config = config

    @abc.abstractmethod
    def fetch(self) -> Iterable[NormalizedRecord]:
        """
        Return an iterable of normalized log records.
        """

    def _normalize_common_fields(
        self,
        payload: MutableMapping[str, Any],
        *,
        event: Optional[str] = None,
        message: Optional[str] = None,
        timestamp: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        if event:
            payload.setdefault("event", event)
        if message:
            payload.setdefault("message", message)
        if timestamp:
            payload.setdefault("timestamp", timestamp)
        elif "timestamp" not in payload:
            payload["timestamp"] = datetime.utcnow().isoformat()
        if metadata:
            payload.setdefault("metadata", {}).update(dict(metadata))
        payload.setdefault("source", self.config.name)
        return payload

    def __repr__(self) -> str:  # pragma: no cover - convenience
        return f"{self.__class__.__name__}(name={self.config.name!r})"


def batched(iterable: Iterable[Any], size: int) -> Iterator[list[Any]]:
    """
    Yield lists of up to `size` elements from an arbitrary iterable.
    """
    batch: list[Any] = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch

