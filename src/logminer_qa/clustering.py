"""
Clustering utilities for grouping similar log events.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Tuple

from sklearn.cluster import MiniBatchKMeans
from sklearn.feature_extraction.text import TfidfVectorizer

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class ClusterSummary:
    labels: List[int]
    top_terms: Dict[str, List[str]] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, object]:
        buckets: Dict[str, List[int]] = {}
        for idx, label in enumerate(self.labels):
            buckets.setdefault(str(label), []).append(idx)
        return {
            "clusters": buckets,
            "top_terms": self.top_terms,
        }


@dataclass(slots=True)
class EventClusterer:
    """
    Performs lightweight clustering on sanitized log messages.
    """

    num_clusters: int = 5
    min_messages: int = 10
    max_features: int = 5000
    random_state: int = 42

    vectorizer: TfidfVectorizer = field(init=False)

    def __post_init__(self) -> None:
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=self.max_features,
            min_df=1,
        )

    def cluster_messages(self, messages: Iterable[str]) -> ClusterSummary:
        corpus = [message or "" for message in messages]
        if len(corpus) < self.min_messages:
            LOGGER.info(
                "Skipping clustering: received %d messages, needs at least %d.",
                len(corpus),
                self.min_messages,
            )
            return ClusterSummary(labels=[-1] * len(corpus))

        matrix = self.vectorizer.fit_transform(corpus)
        clusters = min(self.num_clusters, len(corpus))
        model = MiniBatchKMeans(
            n_clusters=clusters,
            random_state=self.random_state,
            batch_size=max(100, len(corpus)),
            n_init="auto",
        )
        labels = model.fit_predict(matrix)
        top_terms = self._extract_top_terms(model)
        return ClusterSummary(labels=list(labels), top_terms=top_terms)

    def _extract_top_terms(self, model: MiniBatchKMeans, top_n: int = 5) -> Dict[str, List[str]]:
        terms = self.vectorizer.get_feature_names_out()
        top_terms: Dict[str, List[str]] = {}
        for idx, center in enumerate(model.cluster_centers_):
            top_indices = center.argsort()[::-1][:top_n]
            top_terms[str(idx)] = [terms[index] for index in top_indices]
        return top_terms

