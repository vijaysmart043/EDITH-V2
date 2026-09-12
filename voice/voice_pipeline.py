"""
Voice Processing Pipeline and State Machine for EDITH.
Coordinates Wake Word detection, Command Listening, Speech-to-Text transcription,
and Text-to-Speech playback with strict state transitions.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import io
import threading
import time
from enum import Enum
from typing import Any, Callable, List, Optional

try:
    import numpy as np
except ImportError:
    np = None

from app.config import config
from app.logging_config import log_event
from voice.audio_manager import AudioManager
from voice.speech_to_text import MockSpeechToTextProvider, SpeechRecognitionProvider, SpeechToTextProvider
from voice.text_to_speech import MockTextToSpeechProvider, TextToSpeechProvider, WindowsSapi5TTSProvider
from voice.wake_word import LocalKeywordWakeWordProvider, WakeWordProvider


class VoiceState(str, Enum):
    IDLE = "IDLE"
    LISTENING_FOR_WAKE_WORD = "LISTENING_FOR_WAKE_WORD"
    WAKE_WORD_DETECTED = "WAKE_WORD_DETECTED"
    LISTENING_FOR_COMMAND = "LISTENING_FOR_COMMAND"
    PROCESSING = "PROCESSING"
    EXECUTING = "EXECUTING"
    RESPONDING = "RESPONDING"
    ERROR = "ERROR"


class VoicePipeline:
    """Manages audio capture loop, wake word triggers, speech-to-text, and state notifications."""

    def __init__(
        self,
        wake_word_provider: Optional[WakeWordProvider] = None,
        stt_provider: Optional[SpeechToTextProvider] = None,
        tts_provider: Optional[TextToSpeechProvider] = None,
        on_state_change: Optional[Callable[[VoiceState], None]] = None,
        on_command_detected: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.state: VoiceState = VoiceState.IDLE
        self.wake_word_provider = wake_word_provider or LocalKeywordWakeWordProvider(
            sensitivity=config.voice.wake_word_sensitivity
        )
        self.stt_provider = stt_provider or SpeechRecognitionProvider()
        self.tts_provider = tts_provider or WindowsSapi5TTSProvider(
            rate=config.voice.voice_rate,
            volume=config.voice.voice_volume,
        )
        self.audio_manager = AudioManager()

        self.on_state_change = on_state_change
        self.on_command_detected = on_command_detected

        self._running = False
        self._command_audio_buffer: List[Any] = []
        self._command_start_time: float = 0.0
        self._listening_timeout_sec: float = float(config.voice.conversation_timeout_sec)
        self._lock = threading.Lock()

    def set_state(self, new_state: VoiceState) -> None:
        """Update state and notify observers/UI."""
        with self._lock:
            old_state = self.state
            self.state = new_state

        if old_state != new_state:
            log_event("VOICE_PIPELINE", f"State transition: {old_state} -> {new_state}")
            if self.on_state_change:
                self.on_state_change(new_state)

    def start(self) -> bool:
        """Start wake word listening in background."""
        if self._running:
            return True

        self._running = True
        self.wake_word_provider.start()
        self.set_state(VoiceState.LISTENING_FOR_WAKE_WORD)

        # Start audio stream
        ok = self.audio_manager.start_stream(
            device_index=config.voice.microphone_index,
            callback=self._process_incoming_audio,
        )
        if not ok:
            self.set_state(VoiceState.ERROR)
            return False

        return True

    def stop(self) -> None:
        """Halt voice pipeline and release microphone."""
        self._running = False
        self.audio_manager.stop_stream()
        self.wake_word_provider.stop()
        self.set_state(VoiceState.IDLE)

    def _process_incoming_audio(self, pcm_frame: np.ndarray) -> None:
        """Callback invoked by AudioManager for every audio frame."""
        if not self._running:
            return

        current = self.state

        # State 1: Listening for Wake Word ("Hey EDITH")
        if current == VoiceState.LISTENING_FOR_WAKE_WORD:
            detected = self.wake_word_provider.process_audio(pcm_frame)
            if detected:
                log_event("WAKE_WORD", f"Wake word detected: '{config.voice.wake_word}'")
                self.set_state(VoiceState.WAKE_WORD_DETECTED)
                # Play brief acknowledgment chime or voice 'Yes?'
                self.tts_provider.speak("Yes?", block=False)
                # Transition to listening for command
                self._command_audio_buffer.clear()
                self._command_start_time = time.time()
                self.set_state(VoiceState.LISTENING_FOR_COMMAND)

        # State 2: Listening for Command
        elif current == VoiceState.LISTENING_FOR_COMMAND:
            self._command_audio_buffer.append(pcm_frame)
            elapsed = time.time() - self._command_start_time

            # In typical assistant flow, collect ~3.5 to 5 seconds of utterance or silence detection
            if elapsed >= 3.5:
                self.set_state(VoiceState.PROCESSING)
                threading.Thread(target=self._transcribe_and_dispatch, daemon=True).start()

    def trigger_manual_command(self, command_text: str) -> None:
        """Allow UI text box or push-to-talk button to dispatch command directly."""
        self.set_state(VoiceState.PROCESSING)
        if self.on_command_detected:
            self.on_command_detected(command_text)

    def _transcribe_and_dispatch(self) -> None:
        """Worker thread to run STT transcription without blocking audio capture."""
        try:
            if not self._command_audio_buffer:
                self.set_state(VoiceState.LISTENING_FOR_WAKE_WORD)
                return

            # Flatten audio frames
            if np is not None and len(self._command_audio_buffer) > 0 and isinstance(self._command_audio_buffer[0], np.ndarray):
                full_audio = np.concatenate(self._command_audio_buffer)
                audio_bytes = full_audio.tobytes()
            else:
                audio_bytes = b"".join(b if isinstance(b, bytes) else bytes(b) for b in self._command_audio_buffer)

            text = self.stt_provider.transcribe(audio_bytes, sample_rate=self.audio_manager.sample_rate)
            if text and text.strip():
                log_event("STT", f"Command transcribed: {text}")
                if self.on_command_detected:
                    self.on_command_detected(text)
            else:
                log_event("STT", "No speech recognized.")
                self.set_state(VoiceState.LISTENING_FOR_WAKE_WORD)
        except Exception as e:
            log_event("VOICE_PIPELINE", f"Error transcribing command: {e}")
            self.set_state(VoiceState.ERROR)
            time.sleep(1.0)
            self.set_state(VoiceState.LISTENING_FOR_WAKE_WORD)

    def speak_response(self, text: str, return_to_wake_word: bool = True) -> None:
        """Speak response using TTS and transition states cleanly."""
        self.set_state(VoiceState.RESPONDING)
        self.tts_provider.speak(text, block=True)
        if return_to_wake_word and self._running:
            self.set_state(VoiceState.LISTENING_FOR_WAKE_WORD)
