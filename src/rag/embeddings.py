"""
Multilingual Dense Embedding Module for Agriculture RAG.

Provides lazy-loaded, memory-efficient embedding generation and caching
using the cached multilingual SentenceTransformer backbone (paraphrase-multilingual-MiniLM-L12-v2).
Optimized for Apple Silicon (Mac M1) with graceful offline fallback.
"""

import os
import json
import logging
from typing import List, Optional, Tuple, Union
import numpy as np

logger = logging.getLogger(__name__)


class MultilingualEmbedder:
    """
    Manages lazy-loading, embedding generation, normalization, and caching
    of multilingual text vectors (English, Telugu, and transliterated queries).
    """

    DEFAULT_LOCAL_PATH = "models/setfit_best"
    CACHE_DIR = "data/indexes"
    EMBEDDINGS_FILE = "chunk_embeddings.npy"
    CHUNK_IDS_FILE = "chunk_ids.json"

    def __init__(
        self,
        model_path: Optional[str] = None,
        cache_dir: Optional[str] = None,
        batch_size: int = 32,
        device: Optional[str] = None,
    ):
        """
        Initialize the MultilingualEmbedder.

        Args:
            model_path: Path to local model directory or Hugging Face model identifier.
            cache_dir: Directory where embedding matrices are cached.
            batch_size: Batch size for encoding chunks.
            device: 'mps', 'cpu', or None (auto-detect).
        """
        self.model_path = model_path or self.DEFAULT_LOCAL_PATH
        self.cache_dir = cache_dir or self.CACHE_DIR
        self.batch_size = batch_size
        self._device = device
        self._model = None  # Lazy loaded

        os.makedirs(self.cache_dir, exist_ok=True)

    def _resolve_device(self) -> str:
        """Resolve best available device for Mac M1 or CPU."""
        if self._device:
            return self._device
        try:
            import torch
            if torch.backends.mps.is_available():
                return "mps"
        except Exception:
            pass
        return "cpu"

    @property
    def model(self):
        """Lazy load SentenceTransformer model on first access."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            dev = self._resolve_device()
            logger.info(f"Loading multilingual SentenceTransformer from '{self.model_path}' on device '{dev}'...")
            try:
                # Load locally first without triggering network
                self._model = SentenceTransformer(self.model_path, device=dev)
            except Exception as e:
                logger.warning(f"Failed to load from {self.model_path} ({e}). Falling back to cpu...")
                self._model = SentenceTransformer(self.model_path, device="cpu")
        return self._model

    def encode(
        self,
        texts: Union[str, List[str]],
        normalize: bool = True,
        show_progress: bool = False,
    ) -> np.ndarray:
        """
        Generate normalized embeddings for one or more texts.

        Args:
            texts: Single string or list of text strings.
            normalize: If True, vectors are L2-normalized (dot product == cosine similarity).
            show_progress: Whether to show progress bar during batch encoding.

        Returns:
            np.ndarray of shape (len(texts), embedding_dim) or (embedding_dim,).
        """
        is_single = isinstance(texts, str)
        text_list = [texts] if is_single else texts

        if not text_list:
            return np.empty((0, 384), dtype=np.float32)

        # Encode with SentenceTransformer
        embeddings = self.model.encode(
            text_list,
            batch_size=self.batch_size,
            show_progress_bar=show_progress,
            normalize_embeddings=normalize,
            convert_to_numpy=True,
        )

        return embeddings[0] if is_single else embeddings

    def build_or_load_chunk_cache(
        self,
        chunks: List[dict],
        force_recompute: bool = False,
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Load cached embeddings if available; otherwise compute, normalize, and cache them.

        Args:
            chunks: List of chunk dictionaries containing 'chunk_id' and 'text'.
            force_recompute: If True, re-encodes all chunks even if cache exists.

        Returns:
            Tuple of (embeddings_matrix, list_of_chunk_ids).
        """
        cache_emb_path = os.path.join(self.cache_dir, self.EMBEDDINGS_FILE)
        cache_ids_path = os.path.join(self.cache_dir, self.CHUNK_IDS_FILE)

        current_chunk_ids = [c["chunk_id"] for c in chunks]

        # 1. Check if cache exists and matches current chunk IDs exactly
        if (
            not force_recompute
            and os.path.exists(cache_emb_path)
            and os.path.exists(cache_ids_path)
        ):
            try:
                with open(cache_ids_path, "r", encoding="utf-8") as f:
                    cached_ids = json.load(f)
                if cached_ids == current_chunk_ids:
                    embeddings = np.load(cache_emb_path)
                    if embeddings.shape[0] == len(current_chunk_ids):
                        logger.info(f"Loaded {len(current_chunk_ids)} cached embeddings from {cache_emb_path}")
                        return embeddings, cached_ids
            except Exception as e:
                logger.warning(f"Error loading cached embeddings: {e}. Recomputing...")

        # 2. Compute embeddings
        logger.info(f"Computing embeddings for {len(chunks)} agricultural chunks...")
        texts = [c["text"] for c in chunks]
        embeddings = self.encode(texts, normalize=True, show_progress=False)

        # 3. Save to cache
        np.save(cache_emb_path, embeddings)
        with open(cache_ids_path, "w", encoding="utf-8") as f:
            json.dump(current_chunk_ids, f)

        logger.info(f"Successfully cached {len(chunks)} embeddings to {cache_emb_path}")
        return embeddings, current_chunk_ids
