"""Embedding utilities for similarity computation."""

from __future__ import annotations

import asyncio
from typing import Iterable, Sequence

import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """Lazily load a sentence-transformer model for embeddings."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._model: SentenceTransformer | None = None
        self._lock = asyncio.Lock()

    async def ensure_model(self) -> SentenceTransformer:
        if self._model is None:
            async with self._lock:
                if self._model is None:
                    self._model = await asyncio.to_thread(SentenceTransformer, self.model_name)
        return self._model

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        model = await self.ensure_model()
        vectors = await asyncio.to_thread(model.encode, list(texts), show_progress_bar=False)
        return [vector.tolist() for vector in vectors]

    async def similarity(self, base: Sequence[float], candidates: Iterable[Sequence[float]]) -> list[float]:
        base_vec = np.array(base)
        base_norm = np.linalg.norm(base_vec) or 1.0
        scores: list[float] = []
        for candidate in candidates:
            candidate_vec = np.array(candidate)
            denom = (np.linalg.norm(candidate_vec) or 1.0) * base_norm
            scores.append(float(np.dot(base_vec, candidate_vec) / denom))
        return scores


__all__ = ["EmbeddingService"]
