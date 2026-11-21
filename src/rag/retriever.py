"""
Multilingual Hybrid Retrieval Engine for Agricultural Knowledge Base.

Combines:
1. BM25 keyword search with multilingual and agricultural synonym tokenization.
2. Multilingual dense vector similarity via SentenceTransformer embeddings.
3. Reciprocal Rank Fusion (RRF) for scale-invariant ranking.
4. Relevance and evidence filtering to suppress boilerplate, filter unreadable legacy fonts,
   and flag insufficient evidence for out-of-scope queries.
"""

import os
import re
import json
import math
import logging
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from src.rag.embeddings import MultilingualEmbedder

logger = logging.getLogger(__name__)


# Agricultural synonym map for query expansion across Telugu, English, and Romanized terms
CROP_SYNONYMS = {
    "turmeric": ["turmeric", "curcuma", "rhizome", "పసుపు", "pasupu", "paspu"],
    "tumeric": ["turmeric", "curcuma", "rhizome", "పసుపు", "pasupu", "paspu"],
    "pasupu": ["turmeric", "curcuma", "rhizome", "పసుపు", "pasupu", "paspu"],
    "పసుపు": ["turmeric", "curcuma", "rhizome", "పసుపు", "pasupu", "paspu"],
    "banana": ["banana", "musa", "sucker", "pseudostem", "అరటి", "arati", "ariti"],
    "arati": ["banana", "musa", "sucker", "pseudostem", "అరటి", "arati", "ariti"],
    "అరటి": ["banana", "musa", "sucker", "pseudostem", "అరటి", "arati", "ariti"],
    "paddy": ["paddy", "rice", "oryza", "వరి", "vari"],
    "rice": ["paddy", "rice", "oryza", "వరి", "vari"],
    "వరి": ["paddy", "rice", "oryza", "వరి", "vari"],
    "vari": ["paddy", "rice", "oryza", "వరి", "vari"],
    "water": ["water", "irrigation", "irrigat", "moisture", "drainage", "నీరు", "నీటి", "నీటిపారుదల", "neeru", "neeti"],
    "irigate": ["water", "irrigation", "irrigat", "moisture", "drainage", "నీరు", "నీటి", "నీటిపారుదల", "neeru", "neeti"],
    "irrigation": ["water", "irrigation", "irrigat", "moisture", "drainage", "నీరు", "నీటి", "నీటిపారుదల", "neeru", "neeti"],
    "నీరు": ["water", "irrigation", "irrigat", "moisture", "drainage", "నీరు", "నీటి", "నీటిపారుదల", "neeru", "neeti"],
    "నీటిపారుదల": ["water", "irrigation", "irrigat", "moisture", "drainage", "నీరు", "నీటి", "నీటిపారుదల", "neeru", "neeti"],
    "drought": ["drought", "dry spell", "water stress", "కరువు", "పొడి స్పెల్", "karuvu", "podi spell"],
    "కరువు": ["drought", "dry spell", "water stress", "కరువు", "పొడి స్పెల్", "karuvu", "podi spell"],
}

# Standard English stopwords to prevent noise in BM25 scoring
STOPWORDS = {
    "the", "a", "an", "is", "in", "on", "of", "for", "to", "and", "or",
    "what", "who", "how", "why", "when", "where", "which", "with", "by", "at",
    "it", "this", "that", "from", "as", "are", "was", "were", "be", "been",
    "can", "i", "do", "does", "did", "should", "would", "could", "my", "your"
}

# Regex to detect boilerplate chunks
BOILERPLATE_REGEX = re.compile(
    r"(contents\s+\w+\s+\.{5,}|published\s+by|foreword|preface|acknowledgement|editorial\s+board|cgo\s+complex|all\s+rights\s+reserved)",
    re.IGNORECASE,
)


def count_telugu_unicode(text: str) -> int:
    """Count number of Telugu Unicode characters (U+0C00 - U+0C7F)."""
    return sum(1 for ch in text if "\u0c00" <= ch <= "\u0c7f")


@dataclass
class SearchResult:
    """Represents a ranked evidence chunk retrieved for a user query."""
    chunk_id: str
    document_id: str
    text: str
    crop: str
    document_title: str
    organization: str
    source_url: str
    publication_date: str
    page_number: int
    language: str
    dense_score: float = 0.0
    dense_rank: Optional[int] = None
    bm25_score: float = 0.0
    bm25_rank: Optional[int] = None
    hybrid_score: float = 0.0
    is_boilerplate: bool = False
    is_legacy_encoded: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BM25Index:
    """
    Lightweight, highly optimized BM25Okapi implementation supporting
    multilingual scripts (Telugu Unicode + Latin) and agricultural terminology.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_len: List[int] = []
        self.avgdl: float = 0.0
        self.doc_count: int = 0
        self.doc_freqs: List[Dict[str, int]] = []
        self.idf: Dict[str, float] = {}

    @staticmethod
    def tokenize(text: str, expand_synonyms: bool = False) -> List[str]:
        """
        Tokenize multilingual text, retaining Telugu Unicode and alphanumeric tokens,
        filtering stopwords and expanding agricultural synonyms.
        """
        text = text.lower()
        raw_tokens = re.findall(r"[\u0c00-\u0c7f]+|[a-z0-9]+", text)
        filtered = [t for t in raw_tokens if t not in STOPWORDS]

        if expand_synonyms:
            expanded = list(filtered)
            for token in filtered:
                if token in CROP_SYNONYMS:
                    for syn in CROP_SYNONYMS[token]:
                        for st in re.findall(r"[\u0c00-\u0c7f]+|[a-z0-9]+", syn.lower()):
                            if st not in STOPWORDS and st not in expanded:
                                expanded.append(st)
            return expanded

        return filtered

    def fit(self, corpus_texts: List[str]):
        """Build BM25 inverted index and calculate document frequencies."""
        self.doc_count = len(corpus_texts)
        self.doc_len = []
        self.doc_freqs = []
        df: Dict[str, int] = {}

        for text in corpus_texts:
            tokens = self.tokenize(text, expand_synonyms=False)
            self.doc_len.append(len(tokens))
            freqs: Dict[str, int] = {}
            for t in tokens:
                freqs[t] = freqs.get(t, 0) + 1
            self.doc_freqs.append(freqs)
            for t in freqs:
                df[t] = df.get(t, 0) + 1

        self.avgdl = sum(self.doc_len) / max(1, self.doc_count)

        # Robertson-Spärck Jones IDF with smoothing
        self.idf = {}
        for term, freq in df.items():
            self.idf[term] = math.log(1.0 + (self.doc_count - freq + 0.5) / (freq + 0.5))

    def score(self, query: str) -> np.ndarray:
        """Score all indexed documents against the query."""
        query_tokens = self.tokenize(query, expand_synonyms=True)
        scores = np.zeros(self.doc_count, dtype=np.float32)

        for term in query_tokens:
            if term not in self.idf:
                continue
            idf_val = self.idf[term]
            for doc_idx in range(self.doc_count):
                tf = self.doc_freqs[doc_idx].get(term, 0)
                if tf > 0:
                    denom = tf + self.k1 * (1.0 - self.b + self.b * (self.doc_len[doc_idx] / self.avgdl))
                    scores[doc_idx] += idf_val * (tf * (self.k1 + 1.0)) / denom

        return scores


class HybridRetriever:
    """
    Unified Multilingual Hybrid Retriever combining BM25 keyword search,
    SentenceTransformer dense vector similarity, and Reciprocal Rank Fusion.
    """

    def __init__(
        self,
        chunks_file: str = "data/processed/chunks.jsonl",
        embedder: Optional[MultilingualEmbedder] = None,
        rrf_k: int = 60,
        dense_weight: float = 1.0,
        bm25_weight: float = 1.0,
        relevance_threshold: float = 0.70,
    ):
        """
        Initialize HybridRetriever.

        Args:
            chunks_file: Path to processed chunks.jsonl.
            embedder: Optional pre-configured MultilingualEmbedder.
            rrf_k: Constant for Reciprocal Rank Fusion smoothing (standard = 60).
            dense_weight: Weight for dense retrieval ranking in RRF.
            bm25_weight: Weight for BM25 keyword ranking in RRF.
            relevance_threshold: Minimum dense similarity required for evidence.
        """
        self.chunks_file = chunks_file
        self.embedder = embedder or MultilingualEmbedder()
        self.rrf_k = rrf_k
        self.dense_weight = dense_weight
        self.bm25_weight = bm25_weight
        self.relevance_threshold = relevance_threshold

        self.chunks: List[dict] = []
        self.bm25 = BM25Index()
        self.embeddings: Optional[np.ndarray] = None
        self._is_initialized = False

    def load_index(self, force_recompute_embeddings: bool = False):
        """Load corpus chunks, initialize BM25, and load/generate dense embeddings."""
        if self._is_initialized and not force_recompute_embeddings:
            return

        if not os.path.exists(self.chunks_file):
            raise FileNotFoundError(f"Chunks file not found at {self.chunks_file}")

        logger.info(f"Loading chunks from {self.chunks_file}...")
        self.chunks = []
        with open(self.chunks_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    c = json.loads(line)
                    # Check legacy encoding
                    t_chars = count_telugu_unicode(c["text"])
                    c["is_legacy_encoded"] = (c["language"] == "te" and t_chars < 15)
                    self.chunks.append(c)

        logger.info(f"Loaded {len(self.chunks)} chunks. Building BM25 index...")
        texts = [c["text"] for c in self.chunks]
        self.bm25.fit(texts)

        logger.info("Initializing dense embeddings...")
        self.embeddings, _ = self.embedder.build_or_load_chunk_cache(
            self.chunks, force_recompute=force_recompute_embeddings
        )

        self._is_initialized = True
        logger.info("HybridRetriever successfully initialized.")

    def search_dense(
        self,
        query: str,
        top_k: int = 5,
        crop_filter: Optional[str] = None,
        suppress_legacy: bool = True,
    ) -> List[SearchResult]:
        """
        Retrieve chunks using dense semantic similarity.
        """
        self.load_index()
        query_vec = self.embedder.encode(query, normalize=True)

        similarities = np.dot(self.embeddings, query_vec)
        indices = np.argsort(similarities)[::-1]
        results = []
        rank = 1

        for idx in indices:
            chunk = self.chunks[idx]
            if suppress_legacy and chunk.get("is_legacy_encoded"):
                continue

            if crop_filter and chunk["crop"] != crop_filter and chunk["crop"] != "multicrop":
                continue

            score = float(similarities[idx])
            is_boiler = bool(BOILERPLATE_REGEX.search(chunk["text"]))

            sr = SearchResult(
                chunk_id=chunk["chunk_id"],
                document_id=chunk.get("document_id", ""),
                text=chunk["text"],
                crop=chunk["crop"],
                document_title=chunk["document_title"],
                organization=chunk["organization"],
                source_url=chunk["source_url"],
                publication_date=chunk.get("publication_date", ""),
                page_number=chunk["page_number"],
                language=chunk["language"],
                dense_score=round(score, 4),
                dense_rank=rank,
                is_boilerplate=is_boiler,
                is_legacy_encoded=chunk.get("is_legacy_encoded", False),
                metadata=chunk.get("metadata", {}),
            )
            results.append(sr)
            rank += 1
            if len(results) >= top_k:
                break

        return results

    def search_bm25(
        self,
        query: str,
        top_k: int = 5,
        crop_filter: Optional[str] = None,
        suppress_legacy: bool = True,
    ) -> List[SearchResult]:
        """
        Retrieve chunks using BM25 keyword matching.
        """
        self.load_index()
        scores = self.bm25.score(query)
        indices = np.argsort(scores)[::-1]
        results = []
        rank = 1

        for idx in indices:
            score = float(scores[idx])
            if score <= 0.0:
                break

            chunk = self.chunks[idx]
            if suppress_legacy and chunk.get("is_legacy_encoded"):
                continue

            if crop_filter and crop_filter != "all" and chunk["crop"] != crop_filter and chunk["crop"] != "multicrop":
                continue

            is_boiler = bool(BOILERPLATE_REGEX.search(chunk["text"]))

            sr = SearchResult(
                chunk_id=chunk["chunk_id"],
                document_id=chunk.get("document_id", ""),
                text=chunk["text"],
                crop=chunk["crop"],
                document_title=chunk["document_title"],
                organization=chunk["organization"],
                source_url=chunk["source_url"],
                publication_date=chunk.get("publication_date", ""),
                page_number=chunk["page_number"],
                language=chunk["language"],
                bm25_score=round(score, 4),
                bm25_rank=rank,
                is_boilerplate=is_boiler,
                is_legacy_encoded=chunk.get("is_legacy_encoded", False),
                metadata=chunk.get("metadata", {}),
            )
            results.append(sr)
            rank += 1
            if len(results) >= top_k:
                break

        return results

    def search_hybrid(
        self,
        query: str,
        top_k: int = 5,
        crop_filter: Optional[str] = None,
        candidate_pool_size: int = 30,
        suppress_boilerplate: bool = True,
        suppress_legacy: bool = True,
    ) -> Dict[str, Any]:
        """
        Perform Reciprocal Rank Fusion (RRF) hybrid retrieval with evidence filtering.
        """
        query_str = query.strip() if query else ""
        if not query_str:
            return {
                "query": query,
                "evidence_found": False,
                "results": [],
                "status": "empty_query",
                "message": "Query is empty.",
            }

        self.load_index()

        # 1. Retrieve candidates from both systems
        dense_results = self.search_dense(
            query_str, top_k=candidate_pool_size, crop_filter=crop_filter, suppress_legacy=suppress_legacy
        )
        bm25_results = self.search_bm25(
            query_str, top_k=candidate_pool_size, crop_filter=crop_filter, suppress_legacy=suppress_legacy
        )

        # 2. Combine with Reciprocal Rank Fusion
        rrf_scores: Dict[str, float] = {}
        chunk_map: Dict[str, SearchResult] = {}

        # Dense ranks
        for sr in dense_results:
            cid = sr.chunk_id
            chunk_map[cid] = sr
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (self.dense_weight / (self.rrf_k + sr.dense_rank))

        # BM25 ranks
        for sr in bm25_results:
            cid = sr.chunk_id
            if cid in chunk_map:
                chunk_map[cid].bm25_score = sr.bm25_score
                chunk_map[cid].bm25_rank = sr.bm25_rank
            else:
                chunk_map[cid] = sr
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (self.bm25_weight / (self.rrf_k + sr.bm25_rank))

        # 3. Apply boilerplate suppression
        for cid, score in list(rrf_scores.items()):
            sr = chunk_map[cid]
            if suppress_boilerplate and sr.is_boilerplate:
                rrf_scores[cid] = score * 0.35

        # 4. Sort by final RRF score
        sorted_cids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)

        final_results: List[SearchResult] = []
        for cid in sorted_cids[:top_k]:
            sr = chunk_map[cid]
            sr.hybrid_score = round(rrf_scores[cid], 5)
            final_results.append(sr)

        # 5. Check relevance threshold
        # Strong evidence criteria:
        # Either top_dense >= threshold (0.72) AND (bm25_score > 0 or top_dense >= 0.78)
        evidence_found = False
        if final_results:
            top_dense = final_results[0].dense_score
            top_bm25 = final_results[0].bm25_score
            top_hybrid = final_results[0].hybrid_score

            if (top_dense >= self.relevance_threshold and top_bm25 > 0.0) or (top_dense >= 0.78):
                evidence_found = True

        status = "success" if evidence_found else "insufficient_evidence"
        message = (
            "Evidence successfully retrieved."
            if evidence_found
            else "Insufficient supporting evidence found in agricultural publications."
        )

        return {
            "query": query,
            "evidence_found": evidence_found,
            "status": status,
            "message": message,
            "results": final_results if evidence_found else [],
        }
