"""
Agricultural Knowledge Base & Retrieval-Augmented Generation (RAG) Module.

Provides modular ingestion, text cleaning, deterministic chunking,
SentenceTransformer dense embeddings, BM25 keyword search,
Reciprocal Rank Fusion (RRF) hybrid retrieval, and conversational RAG response synthesis.
"""

from src.rag.document_schema import DocumentMetadata, Chunk
from src.rag.text_cleaner import TextCleaner
from src.rag.chunker import Chunker
from src.rag.ingestor import DocumentIngestor
from src.rag.embeddings import MultilingualEmbedder
from src.rag.retriever import BM25Index, HybridRetriever, SearchResult
from src.rag.synthesizer import FarmChatbotSynthesizer, get_retriever

__all__ = [
    "DocumentMetadata",
    "Chunk",
    "TextCleaner",
    "Chunker",
    "DocumentIngestor",
    "MultilingualEmbedder",
    "BM25Index",
    "HybridRetriever",
    "SearchResult",
    "FarmChatbotSynthesizer",
    "get_retriever",
]
