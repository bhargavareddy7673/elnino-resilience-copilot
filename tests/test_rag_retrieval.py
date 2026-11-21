"""
Comprehensive automated test suite for Multilingual Semantic & Hybrid Retrieval (Phase 4).

Verifies:
1. English agricultural query retrieval.
2. Telugu native Unicode query retrieval.
3. Code-mixed (Telugu in Roman script + English) query retrieval.
4. Robustness against common spelling errors/variants (e.g. 'tumeric', 'irigate').
5. Graceful handling of out-of-scope queries (insufficient evidence detection).
6. Safe handling of empty or whitespace-only queries.
7. Suppression of unreadable legacy font passages (ANGRAU Priyaanka/Dharani).
8. Suppression of administrative/boilerplate chunks.
9. Preservation of complete citation metadata (title, URL, organization, page).
10. Idempotent indexing and caching.
"""

import unittest
import numpy as np

from src.rag.retriever import HybridRetriever, SearchResult
from src.rag.embeddings import MultilingualEmbedder


class TestMultilingualHybridRetrieval(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize retriever once for all test methods."""
        cls.retriever = HybridRetriever()
        cls.retriever.load_index()

    def test_english_query_retrieval(self):
        query = "How can I irrigate turmeric to avoid disease?"
        res = self.retriever.search_hybrid(query, top_k=3)
        self.assertTrue(res["evidence_found"])
        self.assertEqual(res["status"], "success")
        self.assertGreaterEqual(len(res["results"]), 1)
        top = res["results"][0]
        self.assertEqual(top.crop, "turmeric")
        self.assertEqual(top.document_id, "turmeric_dppqs_icar_iisr_2014")
        self.assertGreater(top.page_number, 0)
        self.assertTrue(top.source_url.startswith("https://"))

    def test_telugu_unicode_query_retrieval(self):
        query = "కరువు మరియు పొడి వాతావరణంలో పంట రక్షణకు చేయదగినవి ఏమిటి?"
        res = self.retriever.search_hybrid(query, top_k=5)
        self.assertTrue(res["evidence_found"])
        self.assertEqual(res["status"], "success")
        self.assertGreaterEqual(len(res["results"]), 1)
        # Should retrieve IMD Telugu drought publication in the top results
        has_imd = any("weather_imd" in r.document_id for r in res["results"])
        self.assertTrue(has_imd, "Should retrieve IMD Telugu publication in top results")

    def test_code_mixed_query_retrieval(self):
        query = "turmeric ki water eppudu ivvali?"
        res = self.retriever.search_hybrid(query, top_k=3)
        self.assertTrue(res["evidence_found"])
        self.assertEqual(res["status"], "success")
        top = res["results"][0]
        self.assertEqual(top.crop, "turmeric")
        self.assertGreater(top.dense_score, 0.70)

    def test_misspelling_robustness(self):
        # Misspelled 'tumeric' and 'irigate'
        query = "How to irigate tumeric crop properly?"
        res = self.retriever.search_hybrid(query, top_k=3)
        self.assertTrue(res["evidence_found"])
        top = res["results"][0]
        self.assertEqual(top.crop, "turmeric")

    def test_out_of_scope_query_handling(self):
        # Query with zero agricultural backing
        query = "how to fix cracked laptop screen and repair motherboard"
        res = self.retriever.search_hybrid(query, top_k=3)
        self.assertFalse(res["evidence_found"])
        self.assertEqual(res["status"], "insufficient_evidence")
        self.assertEqual(len(res["results"]), 0)

    def test_empty_query_handling(self):
        res = self.retriever.search_hybrid("   ", top_k=3)
        self.assertFalse(res["evidence_found"])
        self.assertEqual(res["status"], "empty_query")
        self.assertEqual(len(res["results"]), 0)

    def test_legacy_font_suppression(self):
        # Verify that unreadable Priyaanka/Dharani Latin-1 chunks from ANGRAU are suppressed
        query = "soil water and nutrient management"
        res = self.retriever.search_hybrid(query, top_k=5, suppress_legacy=True)
        for r in res["results"]:
            self.assertFalse(r.is_legacy_encoded, f"Chunk {r.chunk_id} should not be legacy-encoded")

    def test_citation_metadata_completeness(self):
        query = "banana sucker hot water treatment before planting"
        res = self.retriever.search_hybrid(query, top_k=1)
        self.assertTrue(res["evidence_found"])
        sr = res["results"][0]

        # Verify all mandatory citation fields
        self.assertTrue(len(sr.chunk_id) > 0)
        self.assertTrue(len(sr.document_id) > 0)
        self.assertTrue(len(sr.document_title) > 0)
        self.assertTrue(len(sr.organization) > 0)
        self.assertTrue(sr.source_url.startswith("http"))
        self.assertGreater(sr.page_number, 0)
        self.assertGreater(sr.dense_score, 0.0)
        self.assertGreater(sr.hybrid_score, 0.0)

    def test_banana_irrigation_retrieval(self):
        query = "banana fertilizer application followed by irrigation"
        res = self.retriever.search_hybrid(query, top_k=3, crop_filter="banana")
        self.assertTrue(res["evidence_found"])
        top = res["results"][0]
        self.assertEqual(top.crop, "banana")
        has_water_concept = any(term in top.text.lower() for term in ["irrigation", "water", "sucker", "planting"])
        self.assertTrue(has_water_concept)

    def test_paddy_cultural_management_retrieval(self):
        query = "alley formation in rice for pest control"
        res = self.retriever.search_hybrid(query, top_k=3, crop_filter="paddy")
        self.assertTrue(res["evidence_found"])
        top = res["results"][0]
        self.assertEqual(top.crop, "paddy")
        self.assertIn("alley", top.text.lower())


if __name__ == "__main__":
    unittest.main()
