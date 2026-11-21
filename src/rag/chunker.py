"""
Deterministic, paragraph-aware chunking module for agricultural texts.

Splits cleaned page texts into semantic chunks while respecting:
- Paragraph and sentence boundaries.
- Configurable chunk size and overlap windows.
- Deterministic chunk ID hashing for exact reproducibility.
- Full metadata and citation preservation.
"""

import hashlib
import re
from typing import List, Dict, Any, Optional
from src.rag.document_schema import DocumentMetadata, Chunk


class Chunker:
    """Chunks agricultural text documents into citation-ready units."""

    def __init__(
        self,
        chunk_size_words: int = 250,
        chunk_overlap_words: int = 40,
        min_chunk_words: int = 20,
    ):
        """
        Initialize Chunker.

        Args:
            chunk_size_words: Target maximum words per chunk.
            chunk_overlap_words: Number of overlapping words between consecutive chunks.
            min_chunk_words: Minimum words required for a chunk (filters out negligible fragments).
        """
        if chunk_overlap_words >= chunk_size_words:
            raise ValueError("chunk_overlap_words must be strictly smaller than chunk_size_words")

        self.chunk_size_words = chunk_size_words
        self.chunk_overlap_words = chunk_overlap_words
        self.min_chunk_words = min_chunk_words

    def chunk_page(
        self,
        cleaned_text: str,
        page_number: int,
        doc_metadata: DocumentMetadata,
    ) -> List[Chunk]:
        """
        Chunk a single cleaned page into one or more Chunk objects.

        Args:
            cleaned_text: Preprocessed text of the page.
            page_number: 1-indexed page number from the source PDF.
            doc_metadata: Metadata for the parent document.

        Returns:
            List of Chunk objects with deterministic IDs and complete metadata.
        """
        if not cleaned_text or not cleaned_text.strip():
            return []

        words = cleaned_text.split()
        if len(words) < self.min_chunk_words:
            # If text is too short to split into a valid chunk
            return []

        # Split into semantic segments (paragraphs first)
        paragraphs = [p.strip() for p in cleaned_text.split("\n\n") if p.strip()]

        raw_chunks_text = self._create_sliding_windows(paragraphs, words, cleaned_text)
        chunks: List[Chunk] = []

        for idx, chunk_text in enumerate(raw_chunks_text):
            chunk_words = chunk_text.split()
            if len(chunk_words) < self.min_chunk_words:
                continue

            chunk_id = self._generate_deterministic_id(
                doc_id=doc_metadata.document_id,
                page_number=page_number,
                chunk_index=idx,
                text_sample=chunk_text[:100],
            )

            # Token count approximation (word count is standard; 1 word ~ 1.3 tokens)
            token_count = int(len(chunk_words) * 1.3)

            chunk = Chunk(
                chunk_id=chunk_id,
                document_id=doc_metadata.document_id,
                document_title=doc_metadata.document_title,
                organization=doc_metadata.organization,
                source_url=doc_metadata.source_url,
                publication_date=doc_metadata.publication_date,
                crop=doc_metadata.crop,
                region=doc_metadata.region,
                language=doc_metadata.language,
                page_number=page_number,
                chunk_index=idx,
                text=chunk_text,
                token_count=token_count,
                metadata={
                    "semantic_id": f"{doc_metadata.document_id}_p{page_number}_c{idx}",
                    "word_count": len(chunk_words),
                    "file_path": doc_metadata.file_path,
                },
            )
            chunks.append(chunk)

        return chunks

    def _create_sliding_windows(
        self,
        paragraphs: List[str],
        all_words: List[str],
        full_text: str,
    ) -> List[str]:
        """
        Group paragraphs into chunks of target size, falling back to sentence splitting
        if a single paragraph exceeds the chunk size.
        """
        if len(all_words) <= self.chunk_size_words:
            return [full_text]

        chunk_texts: List[str] = []
        current_paragraphs: List[str] = []
        current_word_count = 0

        for para in paragraphs:
            para_words = para.split()
            para_len = len(para_words)

            # If a single paragraph is larger than chunk_size, split by sentences
            if para_len > self.chunk_size_words:
                # Flush existing accumulated paragraphs first
                if current_paragraphs:
                    chunk_texts.append("\n\n".join(current_paragraphs))
                    current_paragraphs = []
                    current_word_count = 0

                sentences = self._split_sentences(para)
                sub_chunk = []
                sub_count = 0
                for sent in sentences:
                    sent_len = len(sent.split())
                    if sub_count + sent_len > self.chunk_size_words and sub_chunk:
                        chunk_texts.append(" ".join(sub_chunk))
                        # Retain overlap sentences
                        overlap_sents = []
                        overlap_count = 0
                        for s in reversed(sub_chunk):
                            s_len = len(s.split())
                            if overlap_count + s_len <= self.chunk_overlap_words:
                                overlap_sents.insert(0, s)
                                overlap_count += s_len
                            else:
                                break
                        sub_chunk = overlap_sents
                        sub_count = overlap_count

                    sub_chunk.append(sent)
                    sub_count += sent_len

                if sub_chunk:
                    chunk_texts.append(" ".join(sub_chunk))
                continue

            # Standard paragraph accumulation
            if current_word_count + para_len > self.chunk_size_words and current_paragraphs:
                chunk_texts.append("\n\n".join(current_paragraphs))
                
                # Keep last paragraph if within overlap limit
                if para_len <= self.chunk_overlap_words:
                    current_paragraphs = [current_paragraphs[-1], para] if current_paragraphs else [para]
                    current_word_count = sum(len(p.split()) for p in current_paragraphs)
                else:
                    current_paragraphs = [para]
                    current_word_count = para_len
            else:
                current_paragraphs.append(para)
                current_word_count += para_len

        if current_paragraphs:
            chunk_texts.append("\n\n".join(current_paragraphs))

        return chunk_texts

    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences supporting English, scientific terms, and Telugu punctuation.
        """
        # Split on period, exclamation, question mark, or Telugu danda followed by space or newline
        sentence_end = re.compile(r"(?<=[.!?|।॥])\s+")
        sentences = [s.strip() for s in sentence_end.split(text) if s.strip()]
        return sentences if sentences else [text]

    def _generate_deterministic_id(
        self,
        doc_id: str,
        page_number: int,
        chunk_index: int,
        text_sample: str,
    ) -> str:
        """
        Create a deterministic SHA-256 hash identifying the exact chunk content.
        """
        raw = f"{doc_id}_p{page_number}_c{chunk_index}_{text_sample}"
        hash_val = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return hash_val[:16]
