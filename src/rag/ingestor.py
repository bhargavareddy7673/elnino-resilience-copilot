"""
Modular document ingestion pipeline for the Agricultural RAG Knowledge Base.

Orchestrates:
- Multi-document PDF text extraction with PyMuPDF.
- Error handling for corrupted, empty, or unreadable files.
- Text cleaning and normalization.
- Deterministic chunking with page number preservation.
- Deduplication and manifest tracking.
- JSONL structured chunk storage in data/processed/.
"""

import os
import json
import logging
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

from src.rag.document_schema import DocumentMetadata, Chunk
from src.rag.text_cleaner import TextCleaner
from src.rag.chunker import Chunker

logger = logging.getLogger(__name__)


class DocumentIngestor:
    """Manages the ingestion of agricultural documents into structured chunks."""

    def __init__(
        self,
        output_dir: str = "data/processed",
        chunk_size_words: int = 250,
        chunk_overlap_words: int = 40,
        text_cleaner: Optional[TextCleaner] = None,
        chunker: Optional[Chunker] = None,
    ):
        """
        Initialize DocumentIngestor.

        Args:
            output_dir: Directory where chunks.jsonl and ingestion_manifest.json will be saved.
            chunk_size_words: Target words per chunk.
            chunk_overlap_words: Overlap words between chunks.
            text_cleaner: Optional custom TextCleaner instance.
            chunker: Optional custom Chunker instance.
        """
        if fitz is None:
            raise RuntimeError(
                "PyMuPDF (`fitz`) is not installed. Please install it with `pip install pymupdf`."
            )

        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        self.chunks_file = os.path.join(self.output_dir, "chunks.jsonl")
        self.manifest_file = os.path.join(self.output_dir, "ingestion_manifest.json")

        self.cleaner = text_cleaner or TextCleaner()
        self.chunker = chunker or Chunker(
            chunk_size_words=chunk_size_words,
            chunk_overlap_words=chunk_overlap_words,
        )

    def compute_file_hash(self, file_path: str) -> str:
        """Compute the SHA-256 hash of a file."""
        if not os.path.exists(file_path):
            return ""
        sha = hashlib.sha256()
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(65536), b""):
                sha.update(block)
        return sha.hexdigest()

    def load_ingestion_manifest(self) -> Dict[str, Any]:
        """Load the historical ingestion manifest if it exists."""
        if os.path.exists(self.manifest_file):
            try:
                with open(self.manifest_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not read existing manifest: {e}")
        return {"documents": {}, "last_updated": ""}

    def save_ingestion_manifest(self, manifest: Dict[str, Any]) -> None:
        """Save the updated ingestion manifest."""
        manifest["last_updated"] = datetime.utcnow().isoformat()
        with open(self.manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

    def load_existing_chunk_ids(self) -> set:
        """Read all existing chunk IDs from chunks.jsonl to prevent duplicates."""
        existing_ids = set()
        if os.path.exists(self.chunks_file):
            with open(self.chunks_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data = json.loads(line)
                            existing_ids.add(data.get("chunk_id"))
                        except Exception:
                            continue
        return existing_ids

    def ingest_single_document(
        self,
        doc_metadata: DocumentMetadata,
        max_pages: Optional[int] = None,
        force_reingest: bool = False,
    ) -> Dict[str, Any]:
        """
        Ingest a single PDF document.

        Args:
            doc_metadata: DocumentMetadata describing the file.
            max_pages: Optional cap on pages to process (useful for very large books or tests).
            force_reingest: If True, re-processes even if hash matches manifest.

        Returns:
            Dict containing ingestion statistics for this document.
        """
        file_path = doc_metadata.file_path
        doc_id = doc_metadata.document_id

        stats = {
            "document_id": doc_id,
            "document_title": doc_metadata.document_title,
            "file_path": file_path,
            "status": "pending",
            "pages_extracted": 0,
            "chunks_created": 0,
            "tokens_total": 0,
            "error": None,
        }

        # 1. Validate file exists
        if not os.path.exists(file_path):
            stats["status"] = "failed"
            stats["error"] = f"File not found: {file_path}"
            logger.error(stats["error"])
            return stats

        # 2. Check hash and manifest for deduplication
        current_hash = self.compute_file_hash(file_path)
        doc_metadata.file_hash = current_hash
        manifest = self.load_ingestion_manifest()

        if (
            not force_reingest
            and doc_id in manifest.get("documents", {})
            and manifest["documents"][doc_id].get("file_hash") == current_hash
        ):
            stats["status"] = "skipped_already_ingested"
            stats["chunks_created"] = manifest["documents"][doc_id].get("chunks_created", 0)
            stats["pages_extracted"] = manifest["documents"][doc_id].get("pages_extracted", 0)
            return stats

        # 3. Open PDF safely with fitz
        try:
            pdf = fitz.open(file_path)
        except Exception as e:
            stats["status"] = "corrupted_pdf"
            stats["error"] = f"Failed to open PDF {file_path}: {str(e)}"
            logger.error(stats["error"])
            return stats

        total_pdf_pages = len(pdf)
        doc_metadata.page_count = total_pdf_pages
        pages_to_process = min(total_pdf_pages, max_pages) if max_pages else total_pdf_pages

        document_chunks: List[Chunk] = []

        # 4. Extract, clean, and chunk each page
        for page_idx in range(pages_to_process):
            page_num = page_idx + 1
            try:
                page = pdf[page_idx]
                raw_text = page.get_text()
            except Exception as e:
                logger.warning(f"Error reading page {page_num} of {file_path}: {e}")
                continue

            cleaned_text = self.clean_page_text(raw_text)
            if not cleaned_text:
                continue

            page_chunks = self.chunker.chunk_page(
                cleaned_text=cleaned_text,
                page_number=page_num,
                doc_metadata=doc_metadata,
            )

            document_chunks.extend(page_chunks)
            stats["pages_extracted"] += 1

        pdf.close()

        # 5. Append new chunks to chunks.jsonl with deduplication
        existing_ids = self.load_existing_chunk_ids()
        new_chunks_count = 0
        total_tokens = 0

        with open(self.chunks_file, "a", encoding="utf-8") as f_out:
            for chk in document_chunks:
                if chk.chunk_id not in existing_ids:
                    f_out.write(chk.to_json() + "\n")
                    existing_ids.add(chk.chunk_id)
                    new_chunks_count += 1
                    total_tokens += chk.token_count

        stats["status"] = "success"
        stats["chunks_created"] = new_chunks_count
        stats["tokens_total"] = total_tokens

        # 6. Update manifest
        manifest["documents"][doc_id] = {
            "document_title": doc_metadata.document_title,
            "organization": doc_metadata.organization,
            "crop": doc_metadata.crop,
            "language": doc_metadata.language,
            "file_path": file_path,
            "file_hash": current_hash,
            "page_count": total_pdf_pages,
            "pages_extracted": stats["pages_extracted"],
            "chunks_created": new_chunks_count,
            "ingested_at": datetime.utcnow().isoformat(),
        }
        self.save_ingestion_manifest(manifest)

        return stats

    def clean_page_text(self, raw_text: str) -> str:
        """Apply text cleaner to raw page text."""
        return self.cleaner.clean_page_text(raw_text)

    def ingest_from_manifest(
        self,
        manifest_path: str = "data/publications/corpus_manifest.json",
        max_pages_per_doc: Optional[int] = None,
        force_reingest: bool = False,
    ) -> Dict[str, Any]:
        """
        Batch ingest all documents listed in a corpus manifest JSON file.

        Args:
            manifest_path: Path to the corpus manifest JSON.
            max_pages_per_doc: Optional page cap per document.
            force_reingest: If True, re-ingest all files from scratch.

        Returns:
            Dict containing aggregate ingestion statistics.
        """
        if not os.path.exists(manifest_path):
            raise FileNotFoundError(f"Corpus manifest not found at: {manifest_path}")

        with open(manifest_path, "r", encoding="utf-8") as f:
            doc_list = json.load(f)

        if force_reingest and os.path.exists(self.chunks_file):
            # Clean chunks file if forcing reingest
            os.remove(self.chunks_file)
            if os.path.exists(self.manifest_file):
                os.remove(self.manifest_file)

        summary = {
            "total_documents": len(doc_list),
            "successful_documents": 0,
            "skipped_documents": 0,
            "failed_documents": 0,
            "total_pages_extracted": 0,
            "total_chunks_created": 0,
            "total_tokens": 0,
            "crop_distribution": {},
            "language_distribution": {},
            "document_results": [],
        }

        for item in doc_list:
            doc_meta = DocumentMetadata(
                document_id=item["id"],
                crop=item["crop"],
                region=item["region"],
                language=item["language"],
                organization=item["organization"],
                document_title=item["document_title"],
                publication_date=item.get("publication_date", ""),
                source_url=item.get("source_url", ""),
                file_path=item["target_path"],
                page_count=item.get("page_count", 0),
            )

            res = self.ingest_single_document(
                doc_metadata=doc_meta,
                max_pages=max_pages_per_doc,
                force_reingest=force_reingest,
            )
            summary["document_results"].append(res)

            status = res["status"]
            if status == "success":
                summary["successful_documents"] += 1
                summary["total_pages_extracted"] += res["pages_extracted"]
                summary["total_chunks_created"] += res["chunks_created"]
                summary["total_tokens"] += res["tokens_total"]

                crop = doc_meta.crop
                summary["crop_distribution"][crop] = (
                    summary["crop_distribution"].get(crop, 0) + res["chunks_created"]
                )

                lang = doc_meta.language
                summary["language_distribution"][lang] = (
                    summary["language_distribution"].get(lang, 0) + res["chunks_created"]
                )
            elif status == "skipped_already_ingested":
                summary["skipped_documents"] += 1
            else:
                summary["failed_documents"] += 1

        return summary
