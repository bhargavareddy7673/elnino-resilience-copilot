"""Multimodal Audio Transcription and Vernacular Speech Synthesis.

Handles:
1. Audio recording transcription via Hugging Face Whisper-tiny with anti-hallucination filtering.
2. In-memory audio array decoding via soundfile and scipy.
3. Vernacular speech synthesis via gTTS and macOS local speech fallback.
"""

import io
import os
import re
import subprocess
import tempfile
from collections import Counter
from typing import Dict, Any, Optional
import numpy as np

# Force offline mode for cached HF models to prevent network lookup timeouts
os.environ["HF_HUB_OFFLINE"] = "1"

# Ensure ffmpeg executable from imageio-ffmpeg is discovered in PATH
_FFMPEG_EXE = None
try:
    import imageio_ffmpeg
    _FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
    _ffmpeg_dir = os.path.dirname(_FFMPEG_EXE)
    _venv_bin = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../venv/bin"))
    for _p in [_venv_bin, _ffmpeg_dir]:
        if _p and _p not in os.environ.get("PATH", ""):
            os.environ["PATH"] = _p + os.pathsep + os.environ.get("PATH", "")
except Exception:
    pass

_ASR_PIPELINE = None


def decode_audio_with_ffmpeg(audio_bytes: bytes, target_sr: int = 16000) -> Optional[np.ndarray]:
    """Decode any browser audio container (WebM, OGG, WAV, MP3, M4A) directly into 16kHz mono float32.
    
    Prevents any audio frame rate, codec, or sample rate mismatch errors.
    """
    global _FFMPEG_EXE
    if not _FFMPEG_EXE:
        try:
            import imageio_ffmpeg
            _FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            _FFMPEG_EXE = "ffmpeg"

    try:
        cmd = [
            _FFMPEG_EXE,
            "-nostdin",
            "-threads", "1",
            "-i", "pipe:0",
            "-f", "f32le",
            "-acodec", "pcm_f32le",
            "-ac", "1",
            "-ar", str(target_sr),
            "pipe:1",
        ]
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, _ = proc.communicate(input=audio_bytes, timeout=10)
        if proc.returncode == 0 and len(stdout) > 0:
            arr = np.frombuffer(stdout, dtype=np.float32)
            if len(arr) > 0:
                return arr
    except Exception:
        pass
    return None


def get_asr_pipeline():
    """Lazily load and cache the Whisper-tiny ASR pipeline in offline mode."""
    global _ASR_PIPELINE
    if _ASR_PIPELINE is None:
        try:
            from transformers import pipeline
            _ASR_PIPELINE = pipeline(
                "automatic-speech-recognition",
                model="openai/whisper-tiny",
                chunk_length_s=30,
            )
        except Exception:
            _ASR_PIPELINE = None
    return _ASR_PIPELINE


def is_hallucination_or_garbage(text: str) -> bool:
    """Identify Whisper autoregressive repetition loops, silence artifacts, or non-speech garbage."""
    if not text or not text.strip():
        return True
    t = text.strip()

    # 1. Repetitive digits / dashes / symbols like '2-1-1-1-1-1-1...' or '1-2-1-2...'
    if re.search(r"(\b\d+[-–\s]?\b|\b[-–\d]\b){4,}", t):
        return True
    if re.search(r"([-\s\d]{6,})", t) and len(re.sub(r"[-\s\d]", "", t)) < 3:
        return True

    # 2. Check for Latin / Telugu letters vs foreign script hallucinations (Korean, Chinese, Cyrillic)
    valid_letters = re.findall(r"[a-zA-Z\u0c00-\u0c7f]", t)
    foreign_chars = re.findall(r"[\u4e00-\u9fff\uac00-\ud7af\u3040-\u30ff\u0600-\u06ff\u0400-\u04ff]", t)
    if len(foreign_chars) > 0 and len(foreign_chars) >= len(valid_letters):
        return True
    if len(valid_letters) < 3:
        return True

    # 3. High character repetition ratio (e.g. 1-1-1-1 or ........ or ??????)
    cleaned_chars = t.replace(" ", "")
    if len(cleaned_chars) > 8:
        char_counts = Counter(cleaned_chars)
        most_common_char, count = char_counts.most_common(1)[0]
        if count / len(cleaned_chars) > 0.35:
            return True

    # 4. Repeating n-grams / phrases (e.g. 'thank you thank you thank you')
    words = t.split()
    if len(words) >= 4:
        unique_words = set(words)
        if len(unique_words) / len(words) < 0.35:
            return True

    # 5. Whisper standard silence hallucinations and canned artifacts
    t_clean = re.sub(r"[^\w\s]", "", t.lower()).strip()
    silence_phrases = {
        "thank you", "thank you very much", "thanks for watching", "thanks for listening",
        "subtitles by the amaraorg community", "subtitles by", "please subscribe",
        "subscribe to the channel", "you", "bye", "silence", "watching", "so", "the end"
    }
    if t_clean in silence_phrases:
        return True

    return False


def is_silent_audio(audio_array: np.ndarray, rms_threshold: float = 0.005, peak_threshold: float = 0.015) -> bool:
    """Check if audio array contains essentially silence or inaudible background noise."""
    if audio_array is None or len(audio_array) == 0:
        return True
    peak = float(np.max(np.abs(audio_array)))
    if peak < peak_threshold:
        return True
    rms = float(np.sqrt(np.mean(audio_array ** 2)))
    return rms < rms_threshold


def _transcribe_with_google_api(audio_array: np.ndarray, sr: int = 16000, lang: str = "en") -> Optional[str]:
    """Transcribe audio using Google Cloud Speech API endpoint with zero extra library requirements."""
    try:
        import io
        import json
        import urllib.request
        import soundfile as sf

        lang_code = "te-IN" if lang == "te" else "en-IN"
        buf = io.BytesIO()
        sf.write(buf, audio_array, sr, format="FLAC")
        flac_bytes = buf.getvalue()

        url = f"https://www.google.com/speech-api/v2/recognize?xjerr=1&client=chromium&lang={lang_code}&maxresults=1"
        req = urllib.request.Request(
            url,
            data=flac_bytes,
            headers={"Content-Type": f"audio/x-flac; rate={sr}"},
        )
        with urllib.request.urlopen(req, timeout=4) as response:
            result_text = response.read().decode("utf-8", errors="replace")
            for line in result_text.strip().split("\n"):
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    if "result" in data and len(data["result"]) > 0:
                        alt = data["result"][0].get("alternative", [])
                        if alt and "transcript" in alt[0]:
                            tx = alt[0]["transcript"].strip()
                            if tx and not is_hallucination_or_garbage(tx):
                                return tx
                except Exception:
                    continue
    except Exception:
        pass
    return None


def _decode_audio_bytes_to_array(audio_bytes: bytes, target_sr: int = 16000) -> Optional[np.ndarray]:
    """Decode raw audio bytes into a 16kHz mono float32 NumPy array in memory with volume normalization."""
    raw_audio = None

    # 1. Primary: Use bundled FFmpeg (handles WebM from st.audio_input, OGG, WAV, MP3, M4A with zero frame rate issues)
    try:
        raw_audio = decode_audio_with_ffmpeg(audio_bytes, target_sr=target_sr)
    except Exception:
        raw_audio = None

    # 2. Secondary fallback: soundfile (handles WAV, FLAC, OGG in memory)
    if raw_audio is None:
        try:
            import soundfile as sf
            data, sr = sf.read(io.BytesIO(audio_bytes), dtype="float32")
            if len(data.shape) > 1 and data.shape[1] > 1:
                data = data.mean(axis=1)  # Mono
            if sr != target_sr:
                # Use linear interpolation to avoid ringing and shape mismatches
                num_samples = int(round(len(data) * float(target_sr) / float(sr)))
                x_old = np.linspace(0, 1, len(data))
                x_new = np.linspace(0, 1, num_samples)
                data = np.interp(x_new, x_old, data).astype(np.float32)
            raw_audio = data
        except Exception:
            pass

    # 3. Tertiary fallback: scipy.io.wavfile (standard WAV decoding)
    if raw_audio is None:
        try:
            from scipy.io import wavfile
            sr, data = wavfile.read(io.BytesIO(audio_bytes))
            if data.dtype != np.float32:
                if data.dtype == np.int16:
                    data = data.astype(np.float32) / 32768.0
                elif data.dtype == np.int32:
                    data = data.astype(np.float32) / 2147483648.0
                elif data.dtype == np.uint8:
                    data = (data.astype(np.float32) - 128.0) / 128.0
                else:
                    data = data.astype(np.float32)
            if len(data.shape) > 1 and data.shape[1] > 1:
                data = data.mean(axis=1)
            if sr != target_sr:
                num_samples = int(round(len(data) * float(target_sr) / float(sr)))
                x_old = np.linspace(0, 1, len(data))
                x_new = np.linspace(0, 1, num_samples)
                data = np.interp(x_new, x_old, data).astype(np.float32)
            raw_audio = data
        except Exception:
            pass

    # 3. Peak / RMS volume normalization to ensure quiet speech is audible and prevent silence hallucination
    if raw_audio is not None and len(raw_audio) > 0:
        max_val = np.max(np.abs(raw_audio))
        if max_val > 0.005:
            raw_audio = raw_audio / max_val * 0.90

    return raw_audio


def transcribe_audio(
    audio_file_or_bytes,
    sample_rate: int = 16000,
    lang: str = "en",
) -> Dict[str, Any]:
    """Transcribe spoken agricultural questions from audio input into text.
    
    Args:
        audio_file_or_bytes: Streamlit UploadedFile or raw audio bytes.
        sample_rate: Audio sampling rate (default 16kHz).
        lang: Target language context ('te' for Telugu Unicode, 'en' for multilingual/English).
        
    Returns:
        Dictionary with 'success', 'text', 'language', and 'error'.
    """
    if audio_file_or_bytes is None:
        return {"success": False, "text": "", "error": "No audio data provided"}

    # Extract bytes from Streamlit UploadedFile or raw bytes
    if hasattr(audio_file_or_bytes, "read"):
        audio_bytes = audio_file_or_bytes.read()
    elif isinstance(audio_file_or_bytes, bytes):
        audio_bytes = audio_file_or_bytes
    else:
        return {"success": False, "text": "", "error": "Unsupported audio object format"}

    if not audio_bytes or len(audio_bytes) < 100:
        return {"success": False, "text": "", "error": "Audio recording is empty or too short"}

    # 1. Decode raw audio bytes to array
    raw_audio = _decode_audio_bytes_to_array(audio_bytes, target_sr=sample_rate)

    # 2. Check for silence or low-volume background noise
    if raw_audio is not None and is_silent_audio(raw_audio):
        return {
            "success": False,
            "text": "",
            "error": "I couldn't hear your voice clearly. Please tap the mic and speak your question again." if lang != "te" else "మీ మాటలు స్పష్టంగా వినిపించలేదు. దయచేసి మైక్రోఫోన్‌లో మళ్లీ మాట్లాడండి.",
        }

    # 3. Strategy A (Fastest & Most Accurate Online): Google Cloud Speech Recognition
    if raw_audio is not None and len(raw_audio) > 0:
        google_tx = _transcribe_with_google_api(raw_audio, sr=sample_rate, lang=lang)
        if google_tx and not is_hallucination_or_garbage(google_tx):
            return {
                "success": True,
                "text": google_tx,
                "error": None,
            }

    # 4. Strategy B: Local Offline Whisper ASR Pipeline
    asr = get_asr_pipeline()
    if asr is not None and raw_audio is not None and len(raw_audio) > 0:
        generate_kwargs = {
            "task": "transcribe",
            "no_repeat_ngram_size": 3,
            "repetition_penalty": 1.25,
        }
        if lang == "te":
            generate_kwargs["language"] = "te"

        try:
            result = asr(
                {"raw": raw_audio, "sampling_rate": sample_rate},
                generate_kwargs=generate_kwargs,
            )
            transcribed_text = result.get("text", "").strip()
            clean_tx = re.sub(r"^[\s\.\,\-]+$", "", transcribed_text)
            
            if clean_tx and not is_hallucination_or_garbage(clean_tx):
                return {
                    "success": True,
                    "text": clean_tx,
                    "error": None,
                }
        except Exception:
            pass

    # 5. Strategy C: Transcribe via standardized temporary WAV file or sniffer
    temp_path = None
    try:
        asr = get_asr_pipeline()
        if asr is not None:
            if raw_audio is not None and len(raw_audio) > 0:
                # Write guaranteed 16kHz PCM WAV so Whisper / PyTorch never encounters a frame rate mismatch
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    from scipy.io import wavfile
                    int_pcm = (np.clip(raw_audio, -1.0, 1.0) * 32767.0).astype(np.int16)
                    wavfile.write(tmp.name, sample_rate, int_pcm)
                    temp_path = tmp.name
            else:
                # Magic bytes container sniffer to avoid saving WebM as .wav
                suffix = ".wav"
                if audio_bytes.startswith(b"\x1a\x45\xdf\xa3"):
                    suffix = ".webm"
                elif audio_bytes.startswith(b"OggS"):
                    suffix = ".ogg"
                elif audio_bytes.startswith(b"ID3") or audio_bytes[:2] in (b"\xff\xfb", b"\xff\xf3"):
                    suffix = ".mp3"
                elif len(audio_bytes) > 8 and audio_bytes[4:8] == b"ftyp":
                    suffix = ".m4a"
                elif hasattr(audio_file_or_bytes, "name"):
                    name_lower = audio_file_or_bytes.name.lower()
                    for ext in [".webm", ".ogg", ".mp3", ".m4a", ".flac", ".wav"]:
                        if name_lower.endswith(ext):
                            suffix = ext
                            break

                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(audio_bytes)
                    temp_path = tmp.name

            generate_kwargs = {
                "task": "transcribe",
                "no_repeat_ngram_size": 3,
                "repetition_penalty": 1.25,
            }
            if lang == "te":
                generate_kwargs["language"] = "te"

            result = asr(temp_path, generate_kwargs=generate_kwargs)
            transcribed_text = result.get("text", "").strip()
            clean_tx = re.sub(r"^[\s\.\,\-]+$", "", transcribed_text)

            if clean_tx and not is_hallucination_or_garbage(clean_tx):
                return {
                    "success": True,
                    "text": clean_tx,
                    "error": None,
                }
    except Exception:
        pass
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

    return {
        "success": False,
        "text": "",
        "error": "I couldn't hear your voice clearly. Please tap the mic and speak your question again." if lang != "te" else "మీ మాటలు స్పష్టంగా వినిపించలేదు. దయచేసి మైక్రోఫోన్‌లో మళ్లీ మాట్లాడండి.",
    }


def synthesize_speech(text: str, lang: str = "en") -> Optional[bytes]:
    """Generate audio speech bytes from response text for farmer listening.
    
    Args:
        text: Response markdown text to convert to speech.
        lang: Target language ('en' or 'te').
        
    Returns:
        MP3 audio bytes or None if offline/unavailable.
    """
    if not text or not text.strip():
        return None

    try:
        from gtts import gTTS

        # Strip markdown syntax, links, and bold asterisks for clean speech synthesis
        clean_text = re.sub(r"\[.*?\]\(.*?\)", "", text)
        clean_text = re.sub(r"[*#`_>•\-]", " ", clean_text)
        clean_text = re.sub(r"\s+", " ", clean_text).strip()

        # Speak full actionable advice (up to ~450 characters) so complete sentences are heard
        if len(clean_text) > 450:
            end_period = clean_text[:450].rfind(".")
            if end_period > 150:
                clean_text = clean_text[:end_period + 1]
            else:
                clean_text = clean_text[:450] + "."

        target_lang = "te" if lang == "te" else "en"
        if target_lang == "en":
            tts = gTTS(text=clean_text, lang="en", tld="co.in", slow=False)
        else:
            tts = gTTS(text=clean_text, lang="te", slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.getvalue()
    except Exception:
        return None
