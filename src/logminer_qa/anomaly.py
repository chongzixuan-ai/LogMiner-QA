"""
Isolation Forest-based anomaly detection for log embeddings.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from statistics import mean
from typing import Dict, List, Optional

import numpy as np
from sklearn.ensemble import IsolationForest

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class AnomalyDetectorConfig:
    contamination: float = 0.05
    random_state: int = 42
    min_samples: int = 20
    score_normalization: bool = True


@dataclass(slots=True)
class AnomalySummary:
    scores: List[float]
    threshold: float
    top_indices: List[int]
    metadata: Dict[str, float] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, object]:
        return {
            "scores": self.scores,
            "threshold": self.threshold,
            "top_indices": self.top_indices,
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class AnomalyDetector:
    config: AnomalyDetectorConfig = field(default_factory=AnomalyDetectorConfig)
    _model: IsolationForest | None = field(default=None, init=False, repr=False)

    def score_embeddings(self, embeddings: Optional[np.ndarray]) -> AnomalySummary:
        if embeddings is None or embeddings.size == 0:
            LOGGER.info("Skipping anomaly detection: no embeddings available.")
            return AnomalySummary(scores=[], threshold=0.0, top_indices=[])

        if embeddings.ndim != 2:
            raise ValueError("Embeddings must be a 2D numpy array.")

        num_samples = embeddings.shape[0]
        if num_samples < self.config.min_samples:
            LOGGER.info(
                "Skipping anomaly detection: only %d samples, requires at least %d.",
                num_samples,
                self.config.min_samples,
            )
            return AnomalySummary(
                scores=[0.0] * num_samples,
                threshold=0.0,
                top_indices=[],
                metadata={"sample_count": float(num_samples)},
            )

        self._model = IsolationForest(
            contamination=self.config.contamination,
            random_state=self.config.random_state,
        )
        self._model.fit(embeddings)

        raw_scores = -self._model.score_samples(embeddings)
        if self.config.score_normalization:
            normalized_scores = self._normalize_scores(raw_scores)
        else:
            normalized_scores = raw_scores.tolist()

        threshold = float(np.quantile(normalized_scores, 1 - self.config.contamination))
        top_indices = np.argsort(normalized_scores)[::-1][:max(1, int(num_samples * self.config.contamination))]
        metadata = {
            "mean_score": float(mean(normalized_scores)),
            "max_score": float(max(normalized_scores)),
            "min_score": float(min(normalized_scores)),
        }

        return AnomalySummary(
            scores=normalized_scores,
            threshold=threshold,
            top_indices=top_indices.tolist(),
            metadata=metadata,
        )

    def _normalize_scores(self, scores: np.ndarray) -> List[float]:
        min_score = float(np.min(scores))
        max_score = float(np.max(scores))
        if max_score - min_score < 1e-9:
            return [0.0 for _ in scores]
        normalized = (scores - min_score) / (max_score - min_score)
        return normalized.tolist()

