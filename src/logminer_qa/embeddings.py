"""
Transformer-based embedding utilities for log messages.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Iterable, List, Sequence

import numpy as np

LOGGER = logging.getLogger(__name__)

DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def _safe_import_sentence_transformers():
    try:
        from sentence_transformers import SentenceTransformer
    except Exception as exc:  # pragma: no cover - import issues
        LOGGER.warning("sentence-transformers unavailable: %s", exc)
        return None
    return SentenceTransformer


@dataclass(slots=True)
class EmbeddingService:
    """
    Lazily loads a sentence-transformers model and generates embeddings for logs.
    """

    model_name: str = DEFAULT_MODEL_NAME
    batch_size: int = 32
    device: str | None = None
    _model: object | None = field(default=None, init=False, repr=False)

    def ensure_model(self) -> bool:
        if self._model is not None:
            return True
        SentenceTransformer = _safe_import_sentence_transformers()
        if not SentenceTransformer:
            return False
        LOGGER.info("Loading transformer model %s", self.model_name)
        try:
            self._model = SentenceTransformer(self.model_name, device=self.device)
        except Exception as exc:  # pragma: no cover - runtime download issues
            hint = ""
            message = str(exc)
            if "Keras 3" in message and "tf-keras" in message:
                hint = " (install compatibility shim via 'pip install tf-keras')"
            LOGGER.warning("Failed to load transformer model %s: %s%s", self.model_name, exc, hint)
            self._model = None
            return False
        return True

    def embed_texts(self, texts: Sequence[str], show_progress: bool = True) -> np.ndarray:
        if not texts:
            return np.zeros((0, 0), dtype=np.float32)
        if not self.ensure_model():
            raise RuntimeError(
                "Sentence transformer model not available. Install 'sentence-transformers' to use embedding features."
            )
        text_list = list(texts)
        total = len(text_list)
        
        # Use progress bar for large batches
        if show_progress and total > 100:
            try:
                from tqdm import tqdm
                progress_bar = tqdm(total=total, desc="Embedding", unit="texts")
            except ImportError:
                progress_bar = None
                LOGGER.info("Processing %d texts for embedding...", total)
        else:
            progress_bar = None
        
        try:
            embeddings = self._model.encode(
                text_list,
                batch_size=self.batch_size,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=progress_bar is not None,
            )
            if progress_bar:
                progress_bar.update(total)
        finally:
            if progress_bar:
                progress_bar.close()
        
        return embeddings.astype(np.float32)

    def embed_text(self, text: str) -> np.ndarray:
        vectors = self.embed_texts([text])
        if vectors.size == 0:
            return np.zeros((0,), dtype=np.float32)
        return vectors[0]

