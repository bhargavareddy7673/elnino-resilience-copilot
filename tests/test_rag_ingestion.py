"""
Comprehensive automated test suite for the Agricultural RAG Ingestion Pipeline.

Verifies:
1. Document and Chunk schema integrity and JSON serialization.
2. TextCleaner header/footer stripping, hyphenation repair, and Telugu preservation.
3. Chunker deterministic hashing, paragraph boundary splitting, and metadata propagation.
4. DocumentIngestor end-to-end ingestion, deduplication, error handling for corrupted files.
"""

import os
import json
import tempfile
import unittest

from src.rag.document_schema import DocumentMetadata, Chunk
from src.rag.text_cleaner import TextCleaner
from src.rag.chunker import Chunker
from src.rag.ingestor import DocumentIngestor


class TestDocumentSchema(unittest.TestCase):
    def test_document_metadata_serialization(self):
        meta = DocumentMetadata(
            document_id="test_doc_01",
            crop="turmeric",
            region="Rayalaseema",
            language="en",
            organization="ICAR-IISR",
            document_title="Turmeric Production Guide",
            publication_date="2022-01",
            source_url="https://example.org/turmeric.pdf",
            file_path="data/publications/turmeric/test.pdf",
            page_count=10,
            file_hash="abc123hash",
        )
        d = meta.to_dict()
        self.assertEqual(d["document_id"], "test_doc_01")
        self.assertEqual(d["crop"], "turmeric")
        self.assertEqual(d["page_count"], 10)

        recreated = DocumentMetadata.from_dict(d)
        self.assertEqual(recreated.document_id, meta.document_id)
        self.assertEqual(recreated.source_url, meta.source_url)

    def test_chunk_serialization(self):
        chunk = Chunk(
            chunk_id="chunk_12345",
            document_id="test_doc_01",
            document_title="Turmeric Production Guide",
            organization="ICAR-IISR",
            source_url="https://example.org/turmeric.pdf",
            publication_date="2022-01",
            crop="turmeric",
            region="Rayalaseema",
            language="en",
            page_number=5,
            chunk_index=0,
            text="Irrigate turmeric every 7-10 days depending on soil moisture.",
            token_count=12,
            metadata={"word_count": 9},
        )
        json_str = chunk.to_json()
        deserialized = Chunk.from_json(json_str)
        self.assertEqual(deserialized.chunk_id, "chunk_12345")
        self.assertEqual(deserialized.page_number, 5)
        self.assertEqual(deserialized.crop, "turmeric")
        self.assertEqual(deserialized.token_count, 12)


class TestTextCleaner(unittest.TestCase):
    def setUp(self):
        self.cleaner = TextCleaner()

    def test_header_footer_removal(self):
        raw = (
            "AESA BASED IPM Package - Turmeric\n"
            "Turmeric rhizomes should be treated with Trichoderma viride.\n"
            "Directorate of Plant Protection, Quarantine & Storage\n"
            "Page 12 of 52\n"
            "Apply neem cake at 2 tonnes per hectare."
        )
        cleaned = self.cleaner.clean_page_text(raw)
        self.assertNotIn("AESA BASED IPM Package", cleaned)
        self.assertNotIn("Directorate of Plant Protection", cleaned)
        self.assertNotIn("Page 12 of 52", cleaned)
        self.assertIn("Turmeric rhizomes should be treated", cleaned)
        self.assertIn("Apply neem cake at 2 tonnes", cleaned)

    def test_line_end_hyphenation_repair(self):
        raw = "The culti-\nvation of turmeric requires well-drained fer-\ntile soil."
        cleaned = self.cleaner.clean_page_text(raw)
        self.assertIn("cultivation", cleaned)
        self.assertIn("fertile", cleaned)
        self.assertIn("well-drained", cleaned)

    def test_telugu_unicode_preservation(self):
        telugu_text = (
            "కరువు సమయంలో పంట రక్షణకు అనుసరించాల్సిన పద్ధతులు:\n"
            "1. పొలంలో నీటి సంరక్షణ చర్యలు చేపట్టాలి.\n"
            "2. వరుస నీటిపారుదల పద్ధతిని ఉపయోగించాలి."
        )
        cleaned = self.cleaner.clean_page_text(telugu_text)
        self.assertIn("కరువు సమయంలో పంట రక్షణకు", cleaned)
        self.assertIn("నీటి సంరక్షణ చర్యలు", cleaned)
        self.assertIn("వరుస నీటిపారుదల", cleaned)

    def test_scientific_dosage_preservation(self):
        raw = (
            "Spray Mancozeb 75 WP @ 2.5 g/L or Copper Oxychloride 50 WP @ 3.0 g/L "
            "against leaf spot caused by Colletotrichum capsici. NPK 19:19:19 recommended."
        )
        cleaned = self.cleaner.clean_page_text(raw)
        self.assertIn("Mancozeb 75 WP @ 2.5 g/L", cleaned)
        self.assertIn("Copper Oxychloride 50 WP @ 3.0 g/L", cleaned)
        self.assertIn("Colletotrichum capsici", cleaned)
        self.assertIn("NPK 19:19:19", cleaned)


class TestChunker(unittest.TestCase):
    def setUp(self):
        self.sample_metadata = DocumentMetadata(
            document_id="doc_test_turmeric",
            crop="turmeric",
            region="Rayalaseema",
            language="en",
            organization="ICAR-IISR",
            document_title="Turmeric Package of Practices",
            publication_date="2021",
            source_url="https://icar.gov.in/turmeric.pdf",
            file_path="dummy.pdf",
        )

    def test_deterministic_chunk_id(self):
        chunker = Chunker(chunk_size_words=50, chunk_overlap_words=10, min_chunk_words=10)
        text = (
            "Turmeric is an important cash crop in Rayalaseema. "
            "Proper water management is critical during rhizome development stage. "
            "Farmers should avoid waterlogging as it leads to rhizome rot."
        )
        chunks1 = chunker.chunk_page(text, page_number=3, doc_metadata=self.sample_metadata)
        chunks2 = chunker.chunk_page(text, page_number=3, doc_metadata=self.sample_metadata)

        self.assertEqual(len(chunks1), 1)
        self.assertEqual(len(chunks2), 1)
        self.assertEqual(chunks1[0].chunk_id, chunks2[0].chunk_id)
        self.assertEqual(chunks1[0].page_number, 3)
        self.assertEqual(chunks1[0].crop, "turmeric")
        self.assertEqual(chunks1[0].organization, "ICAR-IISR")

    def test_paragraph_splitting_with_overlap(self):
        chunker = Chunker(chunk_size_words=20, chunk_overlap_words=5, min_chunk_words=5)
        p1 = "First paragraph discussing drip irrigation and water scheduling for turmeric crop during drought periods."
        p2 = "Second paragraph detailing nutrient management with nitrogen, phosphorus, and potassium applications."
        full_text = f"{p1}\n\n{p2}"

        chunks = chunker.chunk_page(full_text, page_number=1, doc_metadata=self.sample_metadata)
        self.assertGreaterEqual(len(chunks), 2)
        for chk in chunks:
            self.assertEqual(chk.document_id, "doc_test_turmeric")
            self.assertEqual(chk.page_number, 1)
            self.assertGreater(chk.token_count, 0)

    def test_minimum_words_filter(self):
        chunker = Chunker(chunk_size_words=50, chunk_overlap_words=10, min_chunk_words=15)
        short_text = "Too short text."
        chunks = chunker.chunk_page(short_text, page_number=1, doc_metadata=self.sample_metadata)
        self.assertEqual(len(chunks), 0)


class TestDocumentIngestor(unittest.TestCase):
    def test_error_handling_nonexistent_pdf(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ingestor = DocumentIngestor(output_dir=tmpdir)
            meta = DocumentMetadata(
                document_id="missing_doc",
                crop="banana",
                region="Rayalaseema",
                language="en",
                organization="ICAR",
                document_title="Missing",
                publication_date="2020",
                source_url="",
                file_path=os.path.join(tmpdir, "does_not_exist.pdf"),
            )
            res = ingestor.ingest_single_document(meta)
            self.assertEqual(res["status"], "failed")
            self.assertIn("File not found", res["error"])

    def test_error_handling_corrupted_pdf(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            corrupt_file = os.path.join(tmpdir, "corrupt.pdf")
            with open(corrupt_file, "wb") as f:
                f.write(b"%PDF-1.4 not a real pdf file content corrupted header")

            ingestor = DocumentIngestor(output_dir=tmpdir)
            meta = DocumentMetadata(
                document_id="corrupt_doc",
                crop="banana",
                region="Rayalaseema",
                language="en",
                organization="ICAR",
                document_title="Corrupt",
                publication_date="2020",
                source_url="",
                file_path=corrupt_file,
            )
            res = ingestor.ingest_single_document(meta)
            self.assertEqual(res["status"], "corrupted_pdf")
            self.assertIn("Failed to open PDF", res["error"])

    def test_deduplication(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            real_pdf = "data/publications/weather/imd_telugu_drought_dos_donts.pdf"
            if not os.path.exists(real_pdf):
                self.skipTest("Test PDF not yet downloaded")

            ingestor = DocumentIngestor(output_dir=tmpdir)
            meta = DocumentMetadata(
                document_id="test_drought_telugu",
                crop="weather",
                region="Andhra Pradesh",
                language="te",
                organization="IMD",
                document_title="Drought Do's and Don'ts",
                publication_date="2020",
                source_url="https://imdagrimet.gov.in",
                file_path=real_pdf,
            )

            # First run: should succeed
            res1 = ingestor.ingest_single_document(meta)
            self.assertEqual(res1["status"], "success")
            self.assertGreater(res1["chunks_created"], 0)
            self.assertEqual(res1["pages_extracted"], 3)

            # Second run: should be skipped
            res2 = ingestor.ingest_single_document(meta)
            self.assertEqual(res2["status"], "skipped_already_ingested")

            # Check chunks.jsonl has no duplicates
            chunks_path = os.path.join(tmpdir, "chunks.jsonl")
            with open(chunks_path, "r", encoding="utf-8") as f:
                lines = [l.strip() for l in f if l.strip()]
            chunk_ids = [json.loads(l)["chunk_id"] for l in lines]
            self.assertEqual(len(chunk_ids), len(set(chunk_ids)))


if __name__ == "__main__":
    unittest.main()
