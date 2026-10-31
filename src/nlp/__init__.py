"""NLP package for language detection, normalization, intent classification, and entity extraction."""
from src.nlp.language_detection import detect_language
from src.nlp.text_normalization import normalize_text
from src.nlp.entity_extractor import extract_entities
from src.nlp.intent_classifier import classify_intent, INTENT_DEFINITIONS

__all__ = [
    "detect_language",
    "normalize_text",
    "extract_entities",
    "classify_intent",
    "INTENT_DEFINITIONS",
]
