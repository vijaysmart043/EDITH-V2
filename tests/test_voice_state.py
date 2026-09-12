"""
Unit Tests for Voice Pipeline State Transitions and Startup Configuration.
Developed by G.Vijay Raj (vijay smart).
"""

import unittest
from startup.windows_startup import WindowsStartupManager
from voice.speech_to_text import MockSpeechToTextProvider
from voice.text_to_speech import MockTextToSpeechProvider
from voice.voice_pipeline import VoicePipeline, VoiceState
from voice.wake_word import SimulatedWakeWordProvider


class TestVoicePipeline(unittest.TestCase):

    def test_voice_pipeline_state_transitions(self):
        states_visited = []

        def _on_state_change(new_state: VoiceState):
            states_visited.append(new_state)

        wake_provider = SimulatedWakeWordProvider()
        stt_provider = MockSpeechToTextProvider("test command")
        tts_provider = MockTextToSpeechProvider()

        pipeline = VoicePipeline(
            wake_word_provider=wake_provider,
            stt_provider=stt_provider,
            tts_provider=tts_provider,
            on_state_change=_on_state_change,
        )

        self.assertEqual(pipeline.state, VoiceState.IDLE)

        # 1. Start pipeline -> LISTENING_FOR_WAKE_WORD
        pipeline.set_state(VoiceState.LISTENING_FOR_WAKE_WORD)
        self.assertEqual(pipeline.state, VoiceState.LISTENING_FOR_WAKE_WORD)

        # 2. Wake word detected -> WAKE_WORD_DETECTED
        pipeline.set_state(VoiceState.WAKE_WORD_DETECTED)
        self.assertEqual(pipeline.state, VoiceState.WAKE_WORD_DETECTED)

        # 3. Listening for command -> LISTENING_FOR_COMMAND
        pipeline.set_state(VoiceState.LISTENING_FOR_COMMAND)
        self.assertEqual(pipeline.state, VoiceState.LISTENING_FOR_COMMAND)

        # 4. Processing -> PROCESSING
        pipeline.set_state(VoiceState.PROCESSING)
        self.assertEqual(pipeline.state, VoiceState.PROCESSING)

        # 5. Responding -> RESPONDING
        pipeline.set_state(VoiceState.RESPONDING)
        self.assertEqual(pipeline.state, VoiceState.RESPONDING)

        self.assertIn(VoiceState.LISTENING_FOR_WAKE_WORD, states_visited)
        self.assertIn(VoiceState.WAKE_WORD_DETECTED, states_visited)
        self.assertIn(VoiceState.LISTENING_FOR_COMMAND, states_visited)
        self.assertIn(VoiceState.PROCESSING, states_visited)
        self.assertIn(VoiceState.RESPONDING, states_visited)

    def test_startup_manager_non_crashing(self):
        # Verify WindowsStartupManager methods run safely on any OS platform without crashing
        is_enabled = WindowsStartupManager.is_startup_enabled()
        self.assertIsInstance(is_enabled, bool)


if __name__ == "__main__":
    unittest.main()
