"""
Voice Processing subsystem for EDITH.
Developed by G.Vijay Raj (vijay smart).
"""

from voice.audio_manager import AudioManager
from voice.speech_to_text import MockSpeechToTextProvider, SpeechRecognitionProvider, SpeechToTextProvider
from voice.text_to_speech import MockTextToSpeechProvider, TextToSpeechProvider, WindowsSapi5TTSProvider
from voice.voice_pipeline import VoicePipeline, VoiceState
from voice.wake_word import LocalKeywordWakeWordProvider, SimulatedWakeWordProvider, WakeWordProvider

__all__ = [
    "WakeWordProvider",
    "LocalKeywordWakeWordProvider",
    "SimulatedWakeWordProvider",
    "SpeechToTextProvider",
    "SpeechRecognitionProvider",
    "MockSpeechToTextProvider",
    "TextToSpeechProvider",
    "WindowsSapi5TTSProvider",
    "MockTextToSpeechProvider",
    "AudioManager",
    "VoicePipeline",
    "VoiceState",
]
