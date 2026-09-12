"""
Audio Device and Microphone Capture Manager for EDITH.
Enumerates input devices, captures streaming PCM audio frames, and calculates RMS amplitude.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import threading
from typing import Any, Callable, Dict, List, Optional

try:
    import numpy as np
except ImportError:
    np = None

from app.logging_config import log_event


class AudioManager:
    """Manages audio capture and microphone stream lifecycle."""

    def __init__(self, sample_rate: int = 16000, chunk_size: int = 1024) -> None:
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self._is_recording = False
        self._stream = None
        self._audio_callback: Optional[Callable[[Any], None]] = None
        self._current_rms: float = 0.0

    @staticmethod
    def list_input_devices() -> List[Dict[str, Any]]:
        """List all available audio input microphones on Windows."""
        devices: List[Dict[str, Any]] = []
        try:
            import sounddevice as sd
            devs = sd.query_devices()
            for idx, d in enumerate(devs):
                if d.get("max_input_channels", 0) > 0:
                    devices.append({
                        "id": idx,
                        "name": d.get("name", f"Microphone {idx}"),
                        "channels": d.get("max_input_channels"),
                        "default": idx == sd.default.device[0],
                    })
        except Exception as e:
            log_event("AUDIO", f"Could not query audio devices: {e}")
            devices.append({"id": 0, "name": "Default System Microphone", "channels": 1, "default": True})
        return devices

    def start_stream(
        self,
        device_index: Optional[int] = None,
        callback: Optional[Callable[[np.ndarray], None]] = None,
    ) -> bool:
        """Begin non-blocking audio capture stream."""
        if self._is_recording:
            return True

        self._audio_callback = callback
        self._is_recording = True

        try:
            import sounddevice as sd

            def _sd_callback(indata: np.ndarray, frames: int, time_info: Any, status: Any) -> None:
                if status:
                    log_event("AUDIO", f"Stream status: {status}")
                if not self._is_recording:
                    return

                # Calculate RMS
                data_flat = indata[:, 0]
                rms = float(np.sqrt(np.mean(data_flat.astype(np.float32) ** 2)))
                self._current_rms = rms

                if self._audio_callback:
                    # Convert to 16-bit integer PCM array
                    pcm16 = (data_flat * 32767).astype(np.int16)
                    self._audio_callback(pcm16)

            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                blocksize=self.chunk_size,
                device=device_index,
                channels=1,
                dtype="float32",
                callback=_sd_callback,
            )
            self._stream.start()
            log_event("AUDIO", f"Microphone stream started at {self.sample_rate}Hz.")
            return True
        except Exception as e:
            log_event("AUDIO", f"Failed starting audio capture stream: {e}")
            self._is_recording = False
            return False

    def stop_stream(self) -> None:
        """Safely halt the audio stream."""
        self._is_recording = False
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None
        log_event("AUDIO", "Microphone stream stopped.")

    @property
    def current_rms(self) -> float:
        return self._current_rms

    @property
    def is_recording(self) -> bool:
        return self._is_recording
