"""
Local filesystem connector for newline-delimited JSON logs.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Iterator

from .base import ConnectorConfig, LogConnector, NormalizedRecord


class JSONLinesConnector(LogConnector):
    """
    Simple connector reading newline-delimited JSON logs from disk.
    """

    def __init__(self, config: ConnectorConfig) -> None:
        super().__init__(config)
        path_value = config.options.get("path")
        if not path_value:
            raise ValueError("JSONLinesConnector requires a 'path' option.")
        self.path = Path(path_value).expanduser().resolve()
        if not self.path.exists():
            raise FileNotFoundError(f"Log source {self.path} does not exist.")

    def fetch(self) -> Iterable[NormalizedRecord]:
        return self._read_file()

    def _read_file(self) -> Iterator[NormalizedRecord]:
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    record = {"message": line}
                if not isinstance(record, dict):
                    record = {"message": str(record)}
                yield self._normalize_common_fields(record, metadata={"path": str(self.path)})

