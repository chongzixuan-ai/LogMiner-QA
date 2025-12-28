"""
Datadog log search connector.
"""
from __future__ import annotations

import logging
from typing import Iterable, Iterator, MutableMapping

import requests

from .base import ConnectorConfig, LogConnector, NormalizedRecord

LOGGER = logging.getLogger(__name__)


class DatadogConnector(LogConnector):
    """
    Pulls logs via the Datadog Log Events API.

    Required options:
        - api_key: Datadog API key
        - app_key: Datadog application key
        - query:   Log query string

    Optional:
        - region: e.g. "us3" (default "us")
        - timeframe: dict like {"from": "now-15m", "to": "now"}
        - limit: integer (default 500)
    """

    DEFAULT_TIMEFRAME = {"from": "now-1h", "to": "now"}

    def fetch(self) -> Iterable[NormalizedRecord]:
        for event in self._search_events():
            content = event.get("content", {})
            if not isinstance(content, MutableMapping):
                content = {"message": str(content)}
            payload: MutableMapping[str, object] = dict(content)
            attributes = content.get("attributes", {})
            timestamp = attributes.get("timestamp") or event.get("timestamp")
            message = attributes.get("message") or content.get("message")
            yield self._normalize_common_fields(
                payload,
                event=attributes.get("service") or "datadog_event",
                message=str(message) if message else None,
                timestamp=str(timestamp) if timestamp else None,
                metadata={"tags": attributes.get("tags")},
            )

    def _search_events(self) -> Iterator[dict]:
        options = self.config.options
        api_key = options.get("api_key")
        app_key = options.get("app_key")
        query = options.get("query")
        if not all([api_key, app_key, query]):
            raise ValueError("DatadogConnector requires 'api_key', 'app_key', and 'query'.")

        region = options.get("region", "us")
        base_url = f"https://api.{region}.datadoghq.com/api/v2/logs/events/search"
        params = {
            "page[limit]": int(options.get("limit", 500)),
            "sort": "-timestamp",
        }
        headers = {
            "DD-API-KEY": api_key,
            "DD-APPLICATION-KEY": app_key,
        }
        body = {
            "filter": {
                "query": query,
                "from": options.get("timeframe", self.DEFAULT_TIMEFRAME).get("from"),
                "to": options.get("timeframe", self.DEFAULT_TIMEFRAME).get("to"),
            }
        }
        LOGGER.debug("Querying Datadog logs with query %s", query)
        response = requests.post(base_url, headers=headers, params=params, json=body, timeout=30)
        response.raise_for_status()
        data = response.json()
        for event in data.get("data", []):
            yield event

