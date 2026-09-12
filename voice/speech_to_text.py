"""
Speech-to-Text (STT) Provider Abstraction and Implementations for EDITH.
Allows plugging Faster-Whisper, Vosk, or SpeechRecognition interchangeably.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import io
from abc import ABC, abstractmethod
from typing import Optional

from app.logging_config import log_event


class SpeechToTextProvider(ABC):
    """Abstract Interface for Speech-to-Text Engines."""

    @abstractmethod
    def transcribe(self, audio_bytes: bytes, sample_rate: int = 16000) -> str:
        """Convert raw PCM 16-bit mono audio bytes into text."""
        pass


class SpeechRecognitionProvider(SpeechToTextProvider):
    """Production provider using SpeechRecognition package with local/offline fallback."""

    def __init__(self) -> None:
        self._recognizer = None

    def _get_recognizer(self) -> Any:
        if self._recognizer is None:
            import speech_recognition as sr
            self._recognizer = sr.Recognizer()
        return self._recognizer

    def transcribe(self, audio_bytes: bytes, sample_rate: int = 16000) -> str:
        if not audio_bytes:
            return ""

        try:
            import speech_recognition as sr
            r = self._get_recognizer()
            audio_data = sr.AudioData(audio_bytes, sample_rate=sample_rate, sample_width=2)

            # Try online Google STT first
            try:
                text = r.recognize_google(audio_data)
                log_event("STT", f"Command transcribed: {text}")
                return text.strip()
            except (sr.RequestError, sr.UnknownValueError):
                # Fallback to local sphinx if available
                try:
                    text = r.recognize_sphinx(audio_data)
                    log_event("STT", f"Command transcribed via Sphinx: {text}")
                    return text.strip()
                except Exception:
                    pass
        except Exception as e:
            log_event("STT", f"Speech recognition exception: {e}")

        return ""


class MockSpeechToTextProvider(SpeechToTextProvider):
    """Simulated provider for unit tests and synthetic commands."""

    def __init__(self, predefined_text: str = "") -> None:
        self.predefined_text = predefined_text

    def set_text(self, text: str) -> None:
        self.predefined_text = text

    def transcribe(self, audio_bytes: bytes, sample_rate: int = 16000) -> str:
        return self.predefined_text
