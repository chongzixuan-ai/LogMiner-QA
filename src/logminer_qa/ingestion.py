"""
High-level orchestration for log ingestion connectors.
"""
from __future__ import annotations

import json
from typing import Dict, Iterable, Iterator, List, Mapping, Sequence, Type

from .connectors import (
    ConnectorConfig,
    DatadogConnector,
    ElasticsearchConnector,
    JSONLinesConnector,
    LogConnector,
)

CONNECTOR_REGISTRY: Dict[str, Type[LogConnector]] = {
    "json-lines": JSONLinesConnector,
    "elk": ElasticsearchConnector,
    "elasticsearch": ElasticsearchConnector,
    "datadog": DatadogConnector,
}


def build_connector(name: str, options: Mapping[str, object]) -> LogConnector:
    connector_cls = CONNECTOR_REGISTRY.get(name.lower())
    if not connector_cls:
        available = ", ".join(sorted(CONNECTOR_REGISTRY))
        raise ValueError(f"Unknown connector '{name}'. Available: {available}")
    config = ConnectorConfig(name=name, options=options)
    return connector_cls(config)


def load_connectors(config: Mapping[str, Mapping[str, object]]) -> List[LogConnector]:
    return [build_connector(name, options) for name, options in config.items()]


def load_connectors_from_path(path: str) -> List[LogConnector]:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
        if not isinstance(data, Mapping):
            raise ValueError("Connector configuration file must contain a JSON object.")
        return load_connectors(data)


def aggregate_logs(connectors: Sequence[LogConnector]) -> Iterator[dict]:
    for connector in connectors:
        for record in connector.fetch():
            yield record

