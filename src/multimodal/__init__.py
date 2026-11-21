"""Multimodal AI Module for El Niño Resilience Co-Pilot.

Provides:
1. Speech-to-Text (Whisper Multilingual ASR) & Spoken Audio Synthesis (gTTS).
2. Agricultural Computer Vision (Leaf Pathology & Diagnostic RAG Linkage).
"""

from src.multimodal.audio_transcriber import transcribe_audio, synthesize_speech
from src.multimodal.crop_vision import diagnose_crop_image, DiagnosticResult

__all__ = [
    "transcribe_audio",
    "synthesize_speech",
    "diagnose_crop_image",
    "DiagnosticResult",
]
