"""
Text-to-Speech (TTS) Voice Synthesis Providers for EDITH.
Integrates Windows SAPI5, pyttsx3, and EdgeTTS with clean provider interchangeability.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import os
import threading
from abc import ABC, abstractmethod
from typing import Optional

from app.config import config
from app.logging_config import log_event


class TextToSpeechProvider(ABC):
    """Abstract Interface for Voice Synthesis Engines."""

    @abstractmethod
    def speak(self, text: str, block: bool = False) -> None:
        """Speak the given text utterance."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Interrupt any currently playing speech."""
        pass


class WindowsSapi5TTSProvider(TextToSpeechProvider):
    """Native Windows SAPI5 / pyttsx3 offline speech synthesizer."""

    def __init__(self, rate: int = 185, volume: float = 0.95) -> None:
        self.rate = rate
        self.volume = volume
        self._lock = threading.Lock()
        self._engine = None

    def _init_engine(self) -> None:
        if self._engine is None:
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.setProperty("rate", self.rate)
                engine.setProperty("volume", self.volume)
                self._engine = engine
            except Exception as e:
                log_event("TTS", f"Could not initialize pyttsx3 engine: {e}")

    def speak(self, text: str, block: bool = False) -> None:
        if not text or not text.strip():
            return

        def _worker() -> None:
            with self._lock:
                # Windows COM Dispatch fallback if pyttsx3 loop gets stuck
                if os.name == "nt":
                    try:
                        import win32com.client
                        speaker = win32com.client.Dispatch("SAPI.SpVoice")
                        speaker.Rate = int((self.rate - 200) / 10)
                        speaker.Speak(text)
                        return
                    except Exception:
                        pass

                self._init_engine()
                if self._engine:
                    try:
                        self._engine.say(text)
                        self._engine.runAndWait()
                    except Exception as e:
                        log_event("TTS", f"Error during TTS synthesis: {e}")

        if block:
            _worker()
        else:
            threading.Thread(target=_worker, daemon=True, name="TTS-Thread").start()

    def stop(self) -> None:
        if self._engine:
            try:
                self._engine.stop()
            except Exception:
                pass


class MockTextToSpeechProvider(TextToSpeechProvider):
    """Simulated TTS provider for headless testing."""

    def __init__(self) -> None:
        self.last_spoken = ""
        self.history = []

    def speak(self, text: str, block: bool = False) -> None:
        self.last_spoken = text
        self.history.append(text)
        log_event("TTS", f"[Simulated Speech]: {text}")

    def stop(self) -> None:
        pass
