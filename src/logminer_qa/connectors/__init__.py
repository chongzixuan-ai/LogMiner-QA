"""
Connector factory utilities for pulling logs from external systems.
"""
from __future__ import annotations

from .base import ConnectorConfig, LogConnector
from .datadog import DatadogConnector
from .elk import ElasticsearchConnector
from .local import JSONLinesConnector

__all__ = [
    "ConnectorConfig",
    "LogConnector",
    "DatadogConnector",
    "ElasticsearchConnector",
    "JSONLinesConnector",
]

