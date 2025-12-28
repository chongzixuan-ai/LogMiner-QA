"""
Elasticsearch (ELK) connector for retrieving log documents.
"""
from __future__ import annotations

import logging
from typing import Iterable, Iterator, Mapping, MutableMapping

import requests

from .base import ConnectorConfig, LogConnector, NormalizedRecord, batched

LOGGER = logging.getLogger(__name__)


class ElasticsearchConnector(LogConnector):
    """
    Pulls logs from an Elasticsearch-compatible endpoint using the search API.

    Expected options:
        - endpoint: Base URL, e.g. https://example.com:9200
        - index:    Index name or pattern
        - query:    Optional Elasticsearch query DSL dict
        - page_size: Page size (default: 500)
        - auth:     Optional dict with 'username'/'password' or 'api_key'
        - verify_ssl: bool (default True)
    """

    DEFAULT_QUERY: Mapping[str, object] = {
        "query": {"match_all": {}},
        "sort": [{"@timestamp": {"order": "desc"}}],
    }

    def fetch(self) -> Iterable[NormalizedRecord]:
        for batch in self._scroll_batches():
            for hit in batch:
                source = hit.get("_source", {})
                if not isinstance(source, MutableMapping):
                    source = {"message": str(source)}
                payload: MutableMapping[str, object] = dict(source)
                timestamp = source.get("@timestamp") or source.get("timestamp")
                message = source.get("message") or hit.get("_id")
                yield self._normalize_common_fields(
                    payload,
                    event=source.get("event", "elk_event"),
                    message=str(message) if message else None,
                    timestamp=str(timestamp) if timestamp else None,
                    metadata={"index": hit.get("_index"), "id": hit.get("_id")},
                )

    def _scroll_batches(self) -> Iterator[list[Mapping[str, object]]]:
        page_size = int(self.config.options.get("page_size", 500))
        endpoint = self.config.options.get("endpoint")
        index = self.config.options.get("index")
        if not endpoint or not index:
            raise ValueError("ElasticsearchConnector requires 'endpoint' and 'index'.")

        session = requests.Session()
        verify = self.config.options.get("verify_ssl", True)
        auth_options = self.config.options.get("auth") or {}
        if "api_key" in auth_options:
            session.headers["Authorization"] = f"ApiKey {auth_options['api_key']}"
        elif "username" in auth_options and "password" in auth_options:
            session.auth = (auth_options["username"], auth_options["password"])

        query_body = self.config.options.get("query") or self.DEFAULT_QUERY
        url = f"{endpoint.rstrip('/')}/{index}/_search"

        LOGGER.debug("Querying Elasticsearch index %s at %s", index, endpoint)
        response = session.post(
            url,
            json=query_body,
            params={"size": page_size},
            timeout=30,
            verify=verify,
        )
        response.raise_for_status()
        data = response.json()
        hits = data.get("hits", {}).get("hits", [])
        for batch in batched(hits, page_size):
            yield batch

