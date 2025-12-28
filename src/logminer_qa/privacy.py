"""
Differential privacy utilities for noisy aggregation.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Dict, Mapping, Tuple

from .config import PrivacyConfig


def laplace_noise(scale: float) -> float:
    """
    Sample from Laplace(0, scale).
    """
    uniform = random.random() - 0.5
    return -scale * math.copysign(math.log(1 - 2 * abs(uniform)), uniform)


@dataclass(slots=True)
class DifferentialPrivacyAggregator:
    config: PrivacyConfig = field(default_factory=PrivacyConfig)

    def aggregate_counts(self, counts: Mapping[str, int]) -> Dict[str, int]:
        """
        Apply Laplace noise to counts while preserving sign.
        """
        if not self.config.enable_dp:
            return dict(counts)

        epsilon = max(self.config.epsilon, 1e-3)
        sensitivity = 1.0
        scale = sensitivity / epsilon
        noisy: Dict[str, int] = {}
        for key, value in counts.items():
            noise = laplace_noise(scale)
            perturbed = max(0, int(round(value + noise)))
            noisy[key] = perturbed
        return noisy

    def aggregate_histogram(self, buckets: Mapping[str, int]) -> Dict[str, int]:
        """
        Add noise to histogram buckets.
        """
        return self.aggregate_counts(buckets)

    def privatize_ratio(self, numerator: int, denominator: int) -> float:
        """
        Applies Laplace noise to both numerator and denominator, avoiding
        divide-by-zero scenarios.
        """
        noisy_counts = self.aggregate_counts({"num": numerator, "den": denominator})
        den = noisy_counts["den"] or 1
        return noisy_counts["num"] / den

    def explain(self) -> Dict[str, Tuple[str, float]]:
        return {
            "epsilon": ("privacy budget (lower is stronger privacy)", self.config.epsilon),
            "delta": ("probability of failure guarantee", self.config.delta),
        }
